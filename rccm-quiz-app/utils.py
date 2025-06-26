"""
RCCM学習アプリ - ユーティリティ関数
エラーハンドリング強化版 & 高性能キャッシュシステム
"""

import csv
import os
import logging
import threading
import time
import hashlib
import functools
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable, Tuple
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rccm_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === キャッシュシステム ===

class LRUCache:
    """
    スレッドセーフなLRUキャッシュ実装
    メモリ効率とアクセス速度を両立
    """
    
    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl  # Time-To-Live (秒)
        self.cache = OrderedDict()
        self.timestamps = {}
        self.access_count = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                self.miss_count += 1
                return None
            
            # TTLチェック
            if self._is_expired(key):
                del self.cache[key]
                del self.timestamps[key]
                if key in self.access_count:
                    del self.access_count[key]
                self.miss_count += 1
                return None
            
            # LRU更新
            value = self.cache.pop(key)
            self.cache[key] = value
            self.access_count[key] = self.access_count.get(key, 0) + 1
            self.hit_count += 1
            
            return value
    
    def put(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.maxsize and self.maxsize > 0:
                # 最も古いエントリを安全に削除（改修版）
                try:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    self.timestamps.pop(oldest_key, None)  # safe removal
                    self.access_count.pop(oldest_key, None)  # safe removal
                except (StopIteration, KeyError) as e:
                    logger.warning(f"Cache cleanup error: {e}")
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.access_count[key] = 0
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.access_count.clear()
            self.hit_count = 0
            self.miss_count = 0
    
    def stats(self) -> Dict[str, Any]:
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'maxsize': self.maxsize,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                'most_accessed': sorted(
                    self.access_count.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
            }

class CacheManager:
    """
    統合キャッシュマネージャー
    複数のキャッシュインスタンスを管理
    """
    
    def __init__(self):
        # 企業環境用に拡張されたキャッシュ設定
        self.caches = {
            'questions': LRUCache(maxsize=50, ttl=7200),  # 問題データ（企業用拡張）
            'validation': LRUCache(maxsize=100, ttl=3600),  # データ検証結果
            'csv_parsing': LRUCache(maxsize=50, ttl=7200),  # CSV解析結果
            'file_metadata': LRUCache(maxsize=200, ttl=600),  # ファイルメタデータ
            'department_mapping': LRUCache(maxsize=500, ttl=14400),  # 部門マッピング
            'user_sessions': LRUCache(maxsize=1000, ttl=1800),  # ユーザーセッション
            'question_filters': LRUCache(maxsize=200, ttl=3600),  # 問題フィルター
            'aggregated_stats': LRUCache(maxsize=100, ttl=900),  # 集計統計
        }
        self.background_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='cache_bg')
        
    def get_cache(self, cache_name: str) -> LRUCache:
        return self.caches.get(cache_name)
    
    def clear_all(self) -> None:
        for cache in self.caches.values():
            cache.clear()
        logger.info("全キャッシュをクリアしました")
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.stats()
        return stats
    
    def log_stats(self) -> None:
        stats = self.get_stats()
        logger.info("=== キャッシュ統計 ===")
        for cache_name, cache_stats in stats.items():
            logger.info(f"{cache_name}: サイズ={cache_stats['size']}/{cache_stats['maxsize']}, "
                       f"ヒット率={cache_stats['hit_rate']:.2%}, "
                       f"総リクエスト={cache_stats['total_requests']}")

# グローバルキャッシュマネージャー
cache_manager = CacheManager()

def cache_result(cache_name: str, ttl: Optional[int] = None):
    """
    関数結果をキャッシュするデコレータ
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキー生成
            key_data = str(args) + str(sorted(kwargs.items()))
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            cache = cache_manager.get_cache(cache_name)
            if cache is None:
                # キャッシュが存在しない場合は直接実行
                return func(*args, **kwargs)
            
            # キャッシュから取得を試行
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"キャッシュヒット: {func.__name__}")
                return result
            
            # キャッシュミス: 関数実行
            logger.debug(f"キャッシュミス: {func.__name__}")
            result = func(*args, **kwargs)
            
            # 結果をキャッシュに保存
            cache.put(cache_key, result)
            
            return result
        return wrapper
    return decorator

def get_file_hash(filepath: str) -> str:
    """ファイルのハッシュ値を計算"""
    if not os.path.exists(filepath):
        return ""
    
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_file_modified(filepath: str, cached_hash: str) -> bool:
    """ファイルが変更されているかチェック"""
    current_hash = get_file_hash(filepath)
    return current_hash != cached_hash

class DataLoadError(Exception):
    """データ読み込み専用エラー"""
    pass

class DataValidationError(Exception):
    """データ検証専用エラー"""
    pass

@cache_result('questions', ttl=3600)
def load_questions_improved(csv_path: str) -> List[Dict]:
    """
    改善版問題データ読み込み
    具体的なエラーハンドリングと詳細ログ
    """
    logger.info(f"問題データ読み込み開始: {csv_path}")
    
    # ファイル存在確認
    if not os.path.exists(csv_path):
        logger.error(f"CSVファイルが見つかりません: {csv_path}")
        raise FileNotFoundError(f"問題ファイルが見つかりません: {csv_path}")
    
    # ファイルサイズ確認
    file_size = os.path.getsize(csv_path)
    if file_size == 0:
        logger.error(f"CSVファイルが空です: {csv_path}")
        raise DataLoadError("問題ファイルが空です")
    
    logger.info(f"ファイルサイズ: {file_size} bytes")
    
    # ファイルの変更チェック（キャッシュ無効化用）
    file_hash = get_file_hash(csv_path)
    cache_key = f"{csv_path}_{file_hash}"
    
    # CSVパース結果をキャッシュから確認
    csv_cache = cache_manager.get_cache('csv_parsing')
    cached_df = csv_cache.get(cache_key) if csv_cache else None
    
    if cached_df is not None:
        logger.debug(f"CSV解析結果をキャッシュから取得: {csv_path}")
        df, used_encoding = cached_df
    else:
        # エンコーディング別読み込み試行（CLAUDE.md準拠: Shift_JIS優先）
        encodings = ['shift_jis', 'utf-8', 'cp932', 'utf-8-sig', 'iso-2022-jp']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                logger.debug(f"エンコーディング試行: {encoding}")
                with open(csv_path, 'r', encoding=encoding, newline='') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    if not rows:
                        logger.error("CSVファイルにデータがありません")
                        raise DataLoadError("CSVファイルにデータがありません")
                    df = rows
                    used_encoding = encoding
                    logger.info(f"読み込み成功: {encoding} エンコーディング")
                    break
            except UnicodeDecodeError as e:
                logger.debug(f"エンコーディングエラー {encoding}: {e}")
                continue
            except Exception as e:
                logger.error(f"CSV解析エラー: {e}")
                continue
        
        # 解析結果をキャッシュに保存
        if df is not None and csv_cache:
            csv_cache.put(cache_key, (df, used_encoding))
    
    if df is None:
        logger.error("すべてのエンコーディングで読み込みに失敗")
        raise DataLoadError("CSVファイルのエンコーディングを特定できません")
    
    if not df:
        logger.error("CSVファイルにデータがありません")
        raise DataLoadError("CSVファイルにデータがありません")
    
    logger.info(f"データ読み込み完了: {len(df)}行, エンコーディング: {used_encoding}")
    
    # データ構造検証
    required_columns = [
        'id', 'category', 'question', 'option_a', 'option_b', 
        'option_c', 'option_d', 'correct_answer'
    ]
    
    # データフレームの最初の行からカラムを取得
    if df:
        columns = list(df[0].keys())
    else:
        columns = []
    
    missing_columns = [col for col in required_columns if col not in columns]
    if missing_columns:
        error_msg = f"必須列が不足: {missing_columns}"
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    # データ内容検証
    valid_questions = []
    validation_errors = []
    
    for index, row in enumerate(df):
        try:
            validated_question = validate_question_data(row, index)
            if validated_question:
                valid_questions.append(validated_question)
        except DataValidationError as e:
            validation_errors.append(f"行{index + 2}: {e}")
            logger.warning(f"データ検証エラー 行{index + 2}: {e}")
    
    if not valid_questions:
        error_msg = "有効な問題データがありません"
        logger.error(error_msg)
        if validation_errors:
            error_msg += f"\n検証エラー:\n" + "\n".join(validation_errors[:5])
        raise DataValidationError(error_msg)
    
    if validation_errors:
        logger.warning(f"検証エラーのある行: {len(validation_errors)}件")
        # 最初の5件のエラーをログ出力
        for error in validation_errors[:5]:
            logger.warning(error)
    
    logger.info(f"有効な問題データ: {len(valid_questions)}問")
    return valid_questions

def validate_question_data(row: Dict[str, Any], index: int) -> Optional[Dict]:
    """
    個別問題データの検証
    """
    # ID検証
    if not row.get('id') or row.get('id') == '':
        raise DataValidationError("IDが空です")
    
    try:
        question_id = int(float(row['id']))
    except (ValueError, TypeError):
        raise DataValidationError(f"IDが数値ではありません: {row.get('id')}")
    
    # 必須フィールド検証
    if not row.get('question') or row.get('question') == '':
        raise DataValidationError("問題文が空です")
    
    if not row.get('correct_answer') or row.get('correct_answer') == '':
        raise DataValidationError("正解が指定されていません")
    
    # 正解選択肢検証
    correct_answer = str(row['correct_answer']).strip().upper()
    if correct_answer not in ['A', 'B', 'C', 'D']:
        raise DataValidationError(f"正解選択肢が無効: {correct_answer}")
    
    # 選択肢存在確認
    options = {
        'A': row.get('option_a'),
        'B': row.get('option_b'),
        'C': row.get('option_c'),
        'D': row.get('option_d')
    }
    
    for option_key, option_text in options.items():
        if not option_text or option_text == '':
            raise DataValidationError(f"選択肢{option_key}が空です")
    
    # 正解選択肢に対応するオプションが存在するか確認
    correct_option = options.get(correct_answer)
    if not correct_option or correct_option == '':
        raise DataValidationError(f"正解選択肢{correct_answer}に対応するオプションがありません")
    
    # データ正規化
    question_data = {
        'id': question_id,
        'category': str(row.get('category', '')).strip(),
        'question': str(row['question']).strip(),
        'option_a': str(row['option_a']).strip(),
        'option_b': str(row['option_b']).strip(),
        'option_c': str(row['option_c']).strip(),
        'option_d': str(row['option_d']).strip(),
        'correct_answer': correct_answer,
        'explanation': str(row.get('explanation', '')).strip(),
        'reference': str(row.get('reference', '')).strip(),
        'difficulty': str(row.get('difficulty', '標準')).strip(),
        'keywords': str(row.get('keywords', '')).strip(),
        'practical_tip': str(row.get('practical_tip', '')).strip()
    }
    
    return question_data

def load_rccm_data_files(data_dir: str) -> List[Dict]:
    """
    RCCM専用：4-1基礎・4-2専門データファイルの統合読み込み
    企業環境最適化: 重複読み込み防止機能付き
    """
    global _data_already_loaded, _data_load_lock
    
    # 重複読み込み防止チェック
    with _data_load_lock:
        if _data_already_loaded:
            logger.info("🚀 企業環境最適化: データ既読み込み済み - スキップ")
            # キャッシュから既存データを返す
            if hasattr(cache_manager_instance, '_global_questions_cache'):
                return cache_manager_instance._global_questions_cache
            else:
                logger.warning("⚠️ キャッシュデータが見つかりません - 読み込み続行")
    
    logger.info(f"RCCM統合データ読み込み開始: {data_dir}")
    
    all_questions = []
    file_count = 0
    
    # 4-1基礎データファイル読み込み
    basic_file = os.path.join(data_dir, '4-1.csv')
    if os.path.exists(basic_file):
        try:
            basic_questions = load_questions_improved(basic_file)
            for q in basic_questions:
                q['question_type'] = 'basic'
                q['department'] = 'common'  # 基礎科目は共通
                q['category'] = '共通'  # カテゴリも統一
                # 基礎科目には年度情報を設定しない（年度不問）
                q['year'] = None
            all_questions.extend(basic_questions)
            file_count += 1
            logger.info(f"4-1基礎データ読み込み完了: {len(basic_questions)}問")
        except Exception as e:
            logger.warning(f"4-1基礎データ読み込みエラー: {e}")
    
    # 4-2専門データファイル読み込み（年度別）
    specialist_years = []
    for year in range(2008, 2020):  # 2008-2019年の範囲で確認
        specialist_file = os.path.join(data_dir, f'4-2_{year}.csv')
        if os.path.exists(specialist_file):
            try:
                year_questions = load_questions_improved(specialist_file)
                for q in year_questions:
                    q['question_type'] = 'specialist'
                    q['year'] = year
                    # カテゴリから部門を推定
                    q['department'] = map_category_to_department(q.get('category', ''))
                    # 専門科目であることを明確に標記
                    if not q.get('category'):
                        q['category'] = '専門科目'
                
                all_questions.extend(year_questions)
                specialist_years.append(year)
                file_count += 1
                logger.info(f"4-2専門データ{year}年読み込み完了: {len(year_questions)}問")
            except Exception as e:
                logger.warning(f"4-2専門データ{year}年読み込みエラー: {e}")
    
    # 注: 旧questions.csvファイル（レガシーデータ）は使用しません
    # RCCM試験データは4-1.csvと4-2_*.csvから読み込まれます
    
    # IDの重複チェック・調整
    all_questions = resolve_id_conflicts(all_questions)
    
    # 企業環境最適化: データロード完了フラグとキャッシュ設定
    with _data_load_lock:
        _data_already_loaded = True
        # グローバルキャッシュに保存
        cache_manager_instance._global_questions_cache = all_questions
        logger.info("🚀 企業環境最適化: データキャッシュ完了 - 次回読み込み高速化")
    
    logger.info(f"RCCM統合データ読み込み完了: {file_count}ファイル, 総計{len(all_questions)}問")
    logger.info(f"4-2専門データ対象年度: {specialist_years}")
    
    return all_questions

def map_category_to_department(category: str) -> str:
    """
    カテゴリ名から適切なRCCM部門IDにマッピング（実際のCSVデータ対応）
    """
    category_mapping = {
        # 道路
        '道路': 'road',
        
        # トンネル
        'トンネル': 'tunnel',
        
        # 河川砂防海岸（年度による表記の違いに対応）
        '河川、砂防及び海岸・海洋': 'civil_planning',
        '河川砂防海岸': 'civil_planning',
        '河川砂防': 'civil_planning',  # 2008年度
        '河川砂防海岸海洋': 'civil_planning',  # 2010年度
        '河川砂防及び海岸・海洋': 'civil_planning',  # 2012年度
        '河川、砂防及び海岸･海洋': 'civil_planning',  # 2013年度
        '河川・砂防及び海岸・海洋': 'civil_planning',  # 2014年度
        
        # 都市計画（年度による表記の違いに対応）
        '都市計画及び地方計画': 'urban_planning',
        '都市計画地方計画': 'urban_planning',
        
        # 造園
        '造園': 'landscape',
        
        # 建設環境
        '建設環境': 'construction_env',
        
        # 鋼構造コンクリート（年度による表記の違いに対応）
        '鋼構造及びコンクリート': 'steel_concrete',
        '鋼構造コンクリート': 'steel_concrete',
        
        # 土質基礎
        '土質及び基礎': 'soil_foundation',
        
        # 施工計画（年度による表記の違いに対応）
        '施工計画': 'construction_planning',
        '施工計画施工設備積算': 'construction_planning',
        
        # 上水道
        '上水道及び工業用水道': 'water_supply',
        
        # 森林土木
        '森林土木': 'forestry',
        
        # 農業土木
        '農業土木': 'agriculture',
        
        # 未分類・その他
        '未分類': 'road',  # デフォルト部門
    }
    
    for key, dept in category_mapping.items():
        if key in category:
            return dept
    
    return 'road'  # デフォルト

def resolve_id_conflicts(questions: List[Dict]) -> List[Dict]:
    """
    IDの重複を解決し、一意のIDを設定（問題種別別に範囲分け）
    基礎科目: 1-1000, 専門科目: 1001-10000
    ⚠️ 重複問題の根本原因解決と完全なID整合性保証
    """
    logger.info(f"ID重複解決開始: 入力問題数={len(questions)}問")
    
    # 入力データの検証
    if not questions:
        logger.warning("空の問題リストが渡されました")
        return []
    
    # 元のIDの重複状況を分析
    original_id_counts = {}
    for q in questions:
        original_id = str(q.get('id', 'unknown'))
        original_id_counts[original_id] = original_id_counts.get(original_id, 0) + 1
    
    duplicated_ids = [id_val for id_val, count in original_id_counts.items() if count > 1]
    if duplicated_ids:
        logger.warning(f"重複ID検出: {len(duplicated_ids)}個のIDが重複 (例: {duplicated_ids[:10]})")
    
    used_ids = set()
    resolved_questions = []
    id_mapping = {}  # 元ID → 新IDのマッピング記録
    
    # 問題種別別に分離
    basic_questions = [q for q in questions if q.get('question_type') == 'basic']
    specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
    other_questions = [q for q in questions if q.get('question_type') not in ['basic', 'specialist']]
    
    logger.info(f"問題分類: 基礎={len(basic_questions)}問, 専門={len(specialist_questions)}問, その他={len(other_questions)}問")
    
    # 基礎科目のID範囲: 1-1000
    next_basic_id = 1
    for index, q in enumerate(basic_questions):
        original_id = q.get('id')
        
        # 安全な次のIDを見つける
        while next_basic_id in used_ids or next_basic_id > 1000:
            next_basic_id += 1
            if next_basic_id > 1000:
                logger.error(f"基礎科目のID範囲(1-1000)を超過: {len(basic_questions)}問は範囲を超えています")
                raise DataValidationError(f"基礎科目の問題数({len(basic_questions)})がID範囲(1-1000)を超過")
        
        # IDを更新
        q['id'] = next_basic_id
        q['original_id'] = original_id
        q['file_source'] = '4-1.csv'  # データ来源を記録
        used_ids.add(next_basic_id)
        resolved_questions.append(q)
        id_mapping[f"basic_{original_id}"] = next_basic_id
        next_basic_id += 1
    
    # 専門科目のID範囲: 1001-10000
    next_specialist_id = 1001
    for index, q in enumerate(specialist_questions):
        original_id = q.get('id')
        year = q.get('year', 'unknown')
        
        # 安全な次のIDを見つける
        while next_specialist_id in used_ids or next_specialist_id > 10000:
            next_specialist_id += 1
            if next_specialist_id > 10000:
                logger.error(f"専門科目のID範囲(1001-10000)を超過: {len(specialist_questions)}問は範囲を超えています")
                raise DataValidationError(f"専門科目の問題数({len(specialist_questions)})がID範囲(1001-10000)を超過")
        
        # IDを更新
        q['id'] = next_specialist_id
        q['original_id'] = original_id
        q['file_source'] = f'4-2_{year}.csv'  # データ来源を記録
        used_ids.add(next_specialist_id)
        resolved_questions.append(q)
        id_mapping[f"specialist_{year}_{original_id}"] = next_specialist_id
        next_specialist_id += 1
    
    # その他の問題: 10001以降
    next_other_id = 10001
    for index, q in enumerate(other_questions):
        original_id = q.get('id')
        
        # 安全な次のIDを見つける
        while next_other_id in used_ids:
            next_other_id += 1
            # 理論上の上限チェック（100万問まで）
            if next_other_id > 1000000:
                logger.error("その他問題のID範囲を超過しました")
                raise DataValidationError("その他問題の数が上限を超過")
        
        q['id'] = next_other_id
        q['original_id'] = original_id
        q['file_source'] = 'legacy.csv'
        used_ids.add(next_other_id)
        resolved_questions.append(q)
        id_mapping[f"other_{original_id}"] = next_other_id
        next_other_id += 1
    
    # 最終検証
    final_ids = [q['id'] for q in resolved_questions]
    final_unique_ids = set(final_ids)
    
    if len(final_ids) != len(final_unique_ids):
        logger.error(f"ID重複解決失敗: {len(final_ids)}問中{len(final_unique_ids)}個のユニークID")
        raise DataValidationError("ID重複解決に失敗しました")
    
    # ID範囲チェック
    basic_ids = [q['id'] for q in resolved_questions if q.get('question_type') == 'basic']
    specialist_ids = [q['id'] for q in resolved_questions if q.get('question_type') == 'specialist']
    
    if basic_ids and (min(basic_ids) < 1 or max(basic_ids) > 1000):
        logger.error(f"基礎科目ID範囲エラー: {min(basic_ids)}-{max(basic_ids)}")
        raise DataValidationError("基礎科目のID範囲が正しくありません")
    
    if specialist_ids and (min(specialist_ids) < 1001 or max(specialist_ids) > 10000):
        logger.error(f"専門科目ID範囲エラー: {min(specialist_ids)}-{max(specialist_ids)}")
        raise DataValidationError("専門科目のID範囲が正しくありません")
    
    logger.info(f"✅ ID重複解決完了: 基礎={len(basic_questions)}問(1-{max(basic_ids) if basic_ids else 0}), "
               f"専門={len(specialist_questions)}問(1001-{max(specialist_ids) if specialist_ids else 1000}), "
               f"その他={len(other_questions)}問, 総計={len(resolved_questions)}問")
    
    # ID変更の記録をログ出力（デバッグ用）
    if duplicated_ids:
        logger.info(f"重複解決例: {list(id_mapping.items())[:5]}")
    
    return resolved_questions

def get_sample_data_improved() -> List[Dict]:
    """
    改善版サンプルデータ
    フォールバック用
    """
    logger.info("サンプルデータを使用")
    
    return [
        {
            'id': 1,
            'category': 'コンクリート',
            'department': 'road',
            'question_type': 'basic',
            'question': '普通ポルトランドセメントの凝結時間に関する記述で最も適切なものはどれか。',
            'option_a': '始発凝結時間は45分以上',
            'option_b': '終結凝結時間は8時間以内',
            'option_c': '始発凝結時間は60分以内',
            'option_d': '終結凝結時間は12時間以内',
            'correct_answer': 'C',
            'explanation': 'JIS R 5210では普通ポルトランドセメントの始発凝結時間は60分以内、終結凝結時間は10時間以内と規定されています。',
            'reference': 'JIS R 5210',
            'difficulty': '基本',
            'keywords': 'セメント,凝結時間,品質管理',
            'practical_tip': '現場では気温や湿度によって凝結時間が変化するため、季節に応じた施工計画の調整が必要です。'
        }
    ]

# === 企業環境用CSVデータアクセス最適化 ===

class EnterpriseDataManager:
    """
    企業環境でのCSVデータアクセス最適化
    大量同時アクセス・高速読み込み対応
    """
    
    def __init__(self, data_dir: str = 'data', cache_manager: CacheManager = None):
        self.data_dir = data_dir
        self.cache_manager = cache_manager or cache_manager_instance
        self.file_watcher = {}
        self.preload_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='preload')
        self.compression_enabled = True
        
    def preload_all_data(self):
        """
        アプリケーション起動時にすべてのCSVデータを事前読み込み
        企業環境での高速レスポンス確保
        """
        logger.info("CSVデータの事前読み込み開始（企業環境最適化）")
        
        try:
            csv_files = [
                '4-1.csv',  # 基礎科目
                '4-2_2008.csv', '4-2_2009.csv', '4-2_2010.csv',
                '4-2_2011.csv', '4-2_2012.csv', '4-2_2013.csv',
                '4-2_2014.csv', '4-2_2015.csv', '4-2_2016.csv',
                '4-2_2017.csv', '4-2_2018.csv', '4-2_2019.csv'
            ]
            
            # 並列読み込みで高速化
            futures = []
            for csv_file in csv_files:
                future = self.preload_executor.submit(self._preload_single_file, csv_file)
                futures.append(future)
            
            # 結果確認
            loaded_count = 0
            for future in futures:
                try:
                    if future.result():
                        loaded_count += 1
                except Exception as e:
                    logger.error(f"CSVファイル事前読み込みエラー: {e}")
            
            logger.info(f"CSVデータ事前読み込み完了: {loaded_count}/{len(csv_files)} ファイル")
            return loaded_count == len(csv_files)
            
        except Exception as e:
            logger.error(f"CSVデータ事前読み込み失敗: {e}")
            return False
    
    def _preload_single_file(self, filename: str) -> bool:
        """単一CSVファイルの事前読み込み"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if not os.path.exists(file_path):
                return False
            
            # キャッシュキー生成
            cache_key = f"csv_preload_{filename}"
            
            # ファイルサイズとタイムスタンプでキャッシュ判定
            stat = os.stat(file_path)
            metadata_key = f"{cache_key}_metadata"
            current_metadata = f"{stat.st_size}_{stat.st_mtime}"
            
            metadata_cache = self.cache_manager.get_cache('file_metadata')
            cached_metadata = metadata_cache.get(metadata_key)
            
            if cached_metadata == current_metadata:
                # メタデータが一致する場合はキャッシュ済み
                return True
            
            # ファイル読み込み
            data = load_questions_improved(file_path)
            
            # キャッシュに保存
            questions_cache = self.cache_manager.get_cache('questions')
            questions_cache.put(cache_key, data)
            metadata_cache.put(metadata_key, current_metadata)
            
            logger.debug(f"事前読み込み完了: {filename} ({len(data)}問)")
            return True
            
        except Exception as e:
            logger.error(f"ファイル事前読み込みエラー {filename}: {e}")
            return False
    
    def get_optimized_data(self, filename: str) -> List[Dict]:
        """
        最適化されたデータ取得
        キャッシュファーストアプローチ
        """
        cache_key = f"csv_preload_{filename}"
        questions_cache = self.cache_manager.get_cache('questions')
        
        # キャッシュから取得試行
        cached_data = questions_cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # キャッシュミス時はリアルタイム読み込み
        logger.info(f"キャッシュミス - リアルタイム読み込み: {filename}")
        file_path = os.path.join(self.data_dir, filename)
        data = load_questions_improved(file_path)
        
        # 結果をキャッシュに保存
        questions_cache.put(cache_key, data)
        return data
    
    def get_file_integrity_check(self) -> Dict[str, Any]:
        """
        CSVファイルの整合性チェック
        企業環境でのデータ品質保証
        """
        try:
            integrity_report = {
                'timestamp': datetime.now().isoformat(),
                'files': {},
                'total_questions': 0,
                'status': 'healthy'
            }
            
            # 各CSVファイルをチェック
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.csv') and not filename.endswith(('_backup.csv', '_fixed.csv')):
                    file_path = os.path.join(self.data_dir, filename)
                    
                    try:
                        # ファイル基本情報
                        stat = os.stat(file_path)
                        
                        # データ読み込みテスト
                        file_path_full = os.path.join(self.data_dir, filename)
                        data = load_questions_improved(file_path_full)
                        
                        integrity_report['files'][filename] = {
                            'size_bytes': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'question_count': len(data),
                            'status': 'ok'
                        }
                        integrity_report['total_questions'] += len(data)
                        
                    except Exception as e:
                        integrity_report['files'][filename] = {
                            'status': 'error',
                            'error': str(e)
                        }
                        integrity_report['status'] = 'degraded'
            
            logger.info(f"データ整合性チェック完了: {integrity_report['total_questions']}問")
            return integrity_report
            
        except Exception as e:
            logger.error(f"データ整合性チェックエラー: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }

# 企業環境最適化: 重複読み込み防止フラグ
_data_already_loaded = False
_data_load_lock = threading.Lock()

# グローバルキャッシュマネージャーインスタンス  
cache_manager_instance = CacheManager()

# グローバルインスタンス（企業環境用）
enterprise_data_manager = EnterpriseDataManager(cache_manager=cache_manager_instance) 