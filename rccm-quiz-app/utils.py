"""
RCCM学習アプリ - ユーティリティ関数
エラーハンドリング強化版
"""

import pandas as pd
import os
import logging
from typing import List, Dict, Optional

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

class DataLoadError(Exception):
    """データ読み込み専用エラー"""
    pass

class DataValidationError(Exception):
    """データ検証専用エラー"""
    pass

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
    
    # エンコーディング別読み込み試行
    encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig', 'iso-2022-jp']
    df = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            logger.debug(f"エンコーディング試行: {encoding}")
            df = pd.read_csv(csv_path, encoding=encoding)
            used_encoding = encoding
            logger.info(f"読み込み成功: {encoding} エンコーディング")
            break
        except UnicodeDecodeError as e:
            logger.debug(f"エンコーディングエラー {encoding}: {e}")
            continue
        except pd.errors.EmptyDataError:
            logger.error("CSVファイルにデータがありません")
            raise DataLoadError("CSVファイルにデータがありません")
        except pd.errors.ParserError as e:
            logger.error(f"CSV解析エラー: {e}")
            raise DataLoadError(f"CSVファイルの形式が正しくありません: {e}")
    
    if df is None:
        logger.error("すべてのエンコーディングで読み込みに失敗")
        raise DataLoadError("CSVファイルのエンコーディングを特定できません")
    
    if df.empty:
        logger.error("CSVファイルにデータがありません")
        raise DataLoadError("CSVファイルにデータがありません")
    
    logger.info(f"データ読み込み完了: {len(df)}行, エンコーディング: {used_encoding}")
    
    # データ構造検証
    required_columns = [
        'id', 'category', 'question', 'option_a', 'option_b', 
        'option_c', 'option_d', 'correct_answer'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        error_msg = f"必須列が不足: {missing_columns}"
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    # データ内容検証
    valid_questions = []
    validation_errors = []
    
    for index, row in df.iterrows():
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

def validate_question_data(row: pd.Series, index: int) -> Optional[Dict]:
    """
    個別問題データの検証
    """
    # ID検証
    if pd.isna(row.get('id')) or row.get('id') == '':
        raise DataValidationError("IDが空です")
    
    try:
        question_id = int(float(row['id']))
    except (ValueError, TypeError):
        raise DataValidationError(f"IDが数値ではありません: {row.get('id')}")
    
    # 必須フィールド検証
    if not row.get('question') or pd.isna(row.get('question')):
        raise DataValidationError("問題文が空です")
    
    if not row.get('correct_answer') or pd.isna(row.get('correct_answer')):
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
        if not option_text or pd.isna(option_text):
            raise DataValidationError(f"選択肢{option_key}が空です")
    
    # 正解選択肢に対応するオプションが存在するか確認
    correct_option = options.get(correct_answer);
    if not correct_option or pd.isna(correct_option):
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
            'question': '普通ポルトランドセメントの凝結時間に関する記述で最も適切なものはどれか。サービスワーカー導入',
            'option_a': '始発凝結時間は45分以上',
            'option_b': '終結凝結時間は8時間以内',
            'option_c': '始発凝結時間は60分以内',
            'option_d': '終結凝結時間は12時間以内',
            'correct_answer': 'C',
            'explanation': 'JIS R 5210では普通ポルトランドセメントの始発凝結時間は60分以内、終結凝結時間は10時間以内と規定されています。これは現場での打設計画や品質管理において重要な基準値です。サービスワーカー導入テスト用',
            'reference': 'JIS R 5210（ポルトランドセメント）',
            'difficulty': '基本',
            'keywords': 'セメント,凝結時間,品質管理',
            'practical_tip': '現場では気温や湿度によって凝結時間が変化するため、季節に応じた施工計画の調整が必要です。'
        }
        # 他のサンプルデータ...
    ] 