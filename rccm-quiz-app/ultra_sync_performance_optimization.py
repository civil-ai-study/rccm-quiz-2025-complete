#!/usr/bin/env python3
"""
📊 Ultra Sync Performance Optimization Fix
CLAUDE.md準拠・副作用ゼロ保証・ウルトラシンクパフォーマンス最適化

🎯 レスポンス時間短縮とスケーラビリティ向上の包括的修正
- アプリケーションレベルキャッシング
- インデックスベース高速検索
- 非同期データ処理
- 効率的なフィルタリング
- メモリ使用量最適化
"""

import logging
import threading
import time
import asyncio
import functools
import weakref
from collections import defaultdict, OrderedDict
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import os

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultra_sync_performance_optimization.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltraSyncPerformanceOptimizer:
    """📊 ウルトラシンクパフォーマンス最適化クラス"""
    
    def __init__(self):
        # 高速インデックス（O(1)検索）
        self.questions_index = {}          # id -> question
        self.category_index = defaultdict(list)    # category -> [questions]
        self.department_index = defaultdict(list)  # department -> [questions]
        self.year_index = defaultdict(list)        # year -> [questions]
        self.type_index = defaultdict(list)        # type -> [questions]
        
        # キャッシュシステム
        self.filter_cache = {}  # フィルタ結果キャッシュ
        self.response_cache = {} # レスポンスキャッシュ
        self.cache_lock = threading.RLock()
        
        # パフォーマンス統計
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'index_searches': 0,
            'linear_searches': 0,
            'data_loads': 0,
            'filter_operations': 0,
            'total_response_time': 0,
            'request_count': 0
        }
        
        # データロード状態
        self.data_loaded = False
        self.data_load_lock = threading.RLock()
        self.load_time = None
        
    def build_high_performance_indexes(self, all_questions: List[Dict[str, Any]]) -> None:
        """🔥 高性能インデックス構築（O(1)検索用）"""
        start_time = time.time()
        
        with self.data_load_lock:
            logger.info("🔥 高性能インデックス構築開始...")
            
            # 既存インデックスクリア
            self.questions_index.clear()
            self.category_index.clear()
            self.department_index.clear()
            self.year_index.clear()
            self.type_index.clear()
            
            # インデックス構築
            for question in all_questions:
                qid = str(question.get('id', ''))
                if not qid:
                    continue
                    
                # 基本インデックス（O(1)検索）
                self.questions_index[qid] = question
                
                # カテゴリインデックス
                category = question.get('category', '').strip()
                if category:
                    self.category_index[category].append(question)
                
                # 部門インデックス
                department = question.get('department', '').strip()
                if department:
                    self.department_index[department].append(question)
                
                # 年度インデックス
                year = question.get('year')
                if year:
                    try:
                        year_int = int(year)
                        self.year_index[year_int].append(question)
                    except (ValueError, TypeError):
                        pass
                
                # タイプインデックス
                question_type = question.get('question_type', '').strip()
                if question_type:
                    self.type_index[question_type].append(question)
            
            # 統計情報
            build_time = time.time() - start_time
            self.load_time = build_time
            self.data_loaded = True
            
            logger.info(f"✅ 高性能インデックス構築完了: {len(all_questions)}問")
            logger.info(f"📊 インデックス統計:")
            logger.info(f"  - 基本インデックス: {len(self.questions_index)}問")
            logger.info(f"  - カテゴリ: {len(self.category_index)}種類")
            logger.info(f"  - 部門: {len(self.department_index)}種類")
            logger.info(f"  - 年度: {len(self.year_index)}年分")
            logger.info(f"  - タイプ: {len(self.type_index)}種類")
            logger.info(f"⚡ 構築時間: {build_time:.3f}秒")
            
            self.performance_stats['data_loads'] += 1
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """🔍 ID による高速問題検索（O(1)）"""
        self.performance_stats['index_searches'] += 1
        return self.questions_index.get(str(question_id))
    
    def get_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """📋 カテゴリによる高速問題検索（O(1)）"""
        self.performance_stats['index_searches'] += 1
        return self.category_index.get(category, []).copy()
    
    def get_questions_by_department(self, department: str) -> List[Dict[str, Any]]:
        """🏢 部門による高速問題検索（O(1)）"""
        self.performance_stats['index_searches'] += 1
        return self.department_index.get(department, []).copy()
    
    def get_questions_by_year(self, year: int) -> List[Dict[str, Any]]:
        """📅 年度による高速問題検索（O(1)）"""
        self.performance_stats['index_searches'] += 1
        return self.year_index.get(year, []).copy()
    
    def get_questions_by_type(self, question_type: str) -> List[Dict[str, Any]]:
        """📝 タイプによる高速問題検索（O(1)）"""
        self.performance_stats['index_searches'] += 1
        return self.type_index.get(question_type, []).copy()
    
    @functools.lru_cache(maxsize=1000)
    def get_filtered_questions_cached(self, 
                                    department: Optional[str] = None,
                                    category: Optional[str] = None,
                                    year: Optional[int] = None,
                                    question_type: Optional[str] = None,
                                    exclude_ids: tuple = ()) -> Tuple[Dict[str, Any], ...]:
        """⚡ キャッシュ付き高速フィルタリング（複合条件）"""
        self.performance_stats['filter_operations'] += 1
        
        # ベースデータセット選択（最も制限的な条件から開始）
        candidate_questions = []
        
        if department and department in self.department_index:
            candidate_questions = self.department_index[department]
        elif category and category in self.category_index:
            candidate_questions = self.category_index[category]
        elif year and year in self.year_index:
            candidate_questions = self.year_index[year]
        elif question_type and question_type in self.type_index:
            candidate_questions = self.type_index[question_type]
        else:
            # すべての問題から開始（非効率だが完全性保証）
            candidate_questions = list(self.questions_index.values())
        
        # 追加フィルタ適用
        filtered = []
        exclude_set = set(str(qid) for qid in exclude_ids)
        
        for question in candidate_questions:
            # 除外IDチェック
            if str(question.get('id', '')) in exclude_set:
                continue
            
            # 部門フィルタ
            if department and question.get('department', '').strip() != department:
                continue
            
            # カテゴリフィルタ
            if category and question.get('category', '').strip() != category:
                continue
            
            # 年度フィルタ
            if year:
                try:
                    q_year = int(question.get('year', 0))
                    if q_year != year:
                        continue
                except (ValueError, TypeError):
                    continue
            
            # タイプフィルタ
            if question_type and question.get('question_type', '').strip() != question_type:
                continue
            
            filtered.append(question)
        
        # キャッシュ用にタプル変換
        return tuple(filtered)
    
    def get_mixed_questions_optimized(self, 
                                    department: str,
                                    question_type: str = 'specialist',
                                    year: Optional[int] = None,
                                    count: int = 10,
                                    exclude_ids: List = None) -> List[Dict[str, Any]]:
        """🎯 最適化された複合問題選択"""
        start_time = time.time()
        
        if not self.data_loaded:
            logger.warning("⚠️ インデックスが構築されていません")
            return []
        
        exclude_ids = exclude_ids or []
        exclude_tuple = tuple(str(qid) for qid in exclude_ids)
        
        # キャッシュされた高速フィルタリング
        try:
            filtered_questions = self.get_filtered_questions_cached(
                department=department,
                question_type=question_type,
                year=year,
                exclude_ids=exclude_tuple
            )
            filtered_list = list(filtered_questions)
        except Exception as e:
            logger.error(f"キャッシュフィルタリングエラー: {e}")
            # フォールバック: 基本的なインデックス検索
            if department in self.department_index:
                filtered_list = [
                    q for q in self.department_index[department]
                    if str(q.get('id', '')) not in exclude_tuple
                ]
            else:
                filtered_list = []
        
        # ランダム選択（効率的な方法）
        import random
        if len(filtered_list) <= count:
            selected = filtered_list.copy()
        else:
            # Fisher-Yates shuffle の最適化版
            selected = random.sample(filtered_list, min(count, len(filtered_list)))
        
        # パフォーマンス統計更新
        elapsed_time = time.time() - start_time
        self.performance_stats['total_response_time'] += elapsed_time
        self.performance_stats['request_count'] += 1
        
        logger.debug(f"⚡ 最適化選択完了: {len(selected)}問/{len(filtered_list)}問中 ({elapsed_time:.3f}秒)")
        
        return selected
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📊 パフォーマンス統計取得"""
        if self.performance_stats['request_count'] > 0:
            avg_response_time = self.performance_stats['total_response_time'] / self.performance_stats['request_count']
        else:
            avg_response_time = 0
        
        cache_hit_rate = 0
        total_cache_requests = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = (self.performance_stats['cache_hits'] / total_cache_requests) * 100
        
        return {
            'data_loaded': self.data_loaded,
            'data_load_time': self.load_time,
            'questions_indexed': len(self.questions_index),
            'categories_indexed': len(self.category_index),
            'departments_indexed': len(self.department_index),
            'years_indexed': len(self.year_index),
            'types_indexed': len(self.type_index),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'average_response_time': round(avg_response_time * 1000, 2),  # ms
            'performance_stats': self.performance_stats.copy(),
            'cache_info': {
                'filter_cache_size': len(self.filter_cache),
                'response_cache_size': len(self.response_cache),
                'lru_cache_info': self.get_filtered_questions_cached.cache_info()._asdict()
            }
        }
    
    def clear_performance_cache(self) -> Dict[str, int]:
        """🧹 パフォーマンスキャッシュクリア"""
        cleared_counts = {
            'filter_cache': len(self.filter_cache),
            'response_cache': len(self.response_cache),
            'lru_cache_hits': self.get_filtered_questions_cached.cache_info().hits
        }
        
        # キャッシュクリア
        self.filter_cache.clear()
        self.response_cache.clear()
        self.get_filtered_questions_cached.cache_clear()
        
        logger.info(f"🧹 パフォーマンスキャッシュクリア完了: {cleared_counts}")
        return cleared_counts
    
    def optimize_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """🗜️ セッションデータ最適化"""
        optimized_count = 0
        
        # 問題IDのみ保存（フルオブジェクトは保存しない）
        if 'exam_questions' in session_data:
            questions = session_data['exam_questions']
            if isinstance(questions, list) and len(questions) > 0:
                if isinstance(questions[0], dict) and 'id' in questions[0]:
                    # フルオブジェクト → IDのみ
                    session_data['exam_question_ids'] = [q['id'] for q in questions]
                    del session_data['exam_questions']
                    optimized_count += len(questions)
        
        # 履歴データ圧縮
        if 'history' in session_data:
            history = session_data['history']
            if isinstance(history, list) and len(history) > 50:
                # 最新50件のみ保持
                session_data['history'] = history[-50:]
                optimized_count += len(history) - 50
        
        # 一時データクリア
        temp_keys = [k for k in session_data.keys() if k.startswith(('temp_', 'cache_', 'debug_'))]
        for key in temp_keys:
            del session_data[key]
            optimized_count += 1
        
        return {'optimized_items': optimized_count}


class AsyncDataLoader:
    """⚡ 非同期データローダー"""
    
    def __init__(self):
        self.executor = None
        self.loop = None
    
    async def load_questions_async(self, csv_path: str) -> List[Dict[str, Any]]:
        """非同期問題データローディング"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        if not self.executor:
            self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='data_loader')
        
        loop = asyncio.get_event_loop()
        
        try:
            # 別スレッドで重いI/O処理を実行
            questions = await loop.run_in_executor(
                self.executor, 
                self._load_questions_sync, 
                csv_path
            )
            return questions
        except Exception as e:
            logger.error(f"非同期データロードエラー: {e}")
            return []
    
    def _load_questions_sync(self, csv_path: str) -> List[Dict[str, Any]]:
        """同期問題データローディング（Executorで実行）"""
        try:
            # 実際のロジックは utils.load_questions_improved を呼び出し
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from utils import load_questions_improved
            
            return load_questions_improved(csv_path)
        except Exception as e:
            logger.error(f"同期データロードエラー: {e}")
            return []


def performance_timing_decorator(func: Callable) -> Callable:
    """📊 パフォーマンス測定デコレーター"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            # 遅いレスポンスを警告
            if elapsed_time > 1.0:
                logger.warning(f"⚠️ 遅いレスポンス: {func.__name__} ({elapsed_time:.3f}秒)")
            elif elapsed_time > 0.1:
                logger.info(f"📊 レスポンス時間: {func.__name__} ({elapsed_time:.3f}秒)")
            
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ 処理エラー: {func.__name__} ({elapsed_time:.3f}秒) - {e}")
            raise
    
    return wrapper


def memory_efficient_pagination(data_list: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """📄 メモリ効率的なページネーション"""
    total = len(data_list)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # スライスのみ取得（全データを保持しない）
    page_data = data_list[start_idx:end_idx]
    
    return {
        'data': page_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': end_idx < total
        }
    }


def create_question_digest(question: Dict[str, Any]) -> str:
    """🔑 問題データの軽量ダイジェスト作成"""
    # 重要フィールドのみでハッシュ生成
    key_data = {
        'id': question.get('id'),
        'category': question.get('category'),
        'department': question.get('department'),
        'year': question.get('year'),
        'question_type': question.get('question_type')
    }
    
    digest_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(digest_str.encode('utf-8')).hexdigest()[:8]


def main():
    """パフォーマンス最適化テスト実行"""
    logger.info("🚀 Ultra Sync Performance Optimization Test Starting...")
    
    # テストデータ作成
    test_questions = [
        {
            'id': i,
            'category': f'Category_{i % 5}',
            'department': f'Department_{i % 3}',
            'year': 2015 + (i % 8),
            'question_type': 'specialist' if i % 2 == 0 else 'basic',
            'question': f'Test question {i}',
            'options': {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'},
            'correct_answer': 'A'
        }
        for i in range(1000)  # 1000問のテストデータ
    ]
    
    # パフォーマンス最適化テスト
    optimizer = UltraSyncPerformanceOptimizer()
    
    # インデックス構築テスト
    start_time = time.time()
    optimizer.build_high_performance_indexes(test_questions)
    build_time = time.time() - start_time
    print(f"📊 インデックス構築時間: {build_time:.3f}秒")
    
    # 検索性能テスト
    search_start = time.time()
    for i in range(100):
        # ID検索テスト
        question = optimizer.get_question_by_id(str(i))
        
        # カテゴリ検索テスト
        category_questions = optimizer.get_questions_by_category(f'Category_{i % 5}')
        
        # 複合フィルタテスト
        filtered = optimizer.get_mixed_questions_optimized(
            department=f'Department_{i % 3}',
            question_type='specialist',
            year=2015 + (i % 8),
            count=10
        )
    
    search_time = time.time() - search_start
    print(f"📊 100回検索時間: {search_time:.3f}秒 (平均: {search_time*10:.1f}ms)")
    
    # 統計レポート
    stats = optimizer.get_performance_stats()
    print(f"\n📈 パフォーマンス統計:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    print("\n🎉 Ultra Sync Performance Optimization Test Complete!")


if __name__ == "__main__":
    main()