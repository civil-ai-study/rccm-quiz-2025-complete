#!/usr/bin/env python3
"""
造園2016年エラー詳細分析スクリプト

RCCMアプリの造園2016年で発生するHTTP 500エラーの根本原因を特定します。
- 造園2016年のデータ存在確認
- get_mixed_questions関数の実行ログ
- 有効年度での誤判定箇所の特定
"""

import sys
import os
import logging
import json
import csv
from datetime import datetime

# アプリのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'zoen_2016_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_csv_data():
    """CSVデータを読み込みます"""
    logger.info("=== CSVデータ読み込み開始 ===")
    
    csv_file = os.path.join('rccm-quiz-app', 'data', '4-2_2016.csv')
    if not os.path.exists(csv_file):
        logger.error(f"❌ 2016年データファイルが存在しません: {csv_file}")
        return []
    
    questions = []
    zoen_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, 1):
                if len(row) >= 3:
                    category = row[1].strip() if len(row) > 1 else ''
                    year = row[2].strip() if len(row) > 2 else ''
                    
                    if category == '造園':
                        zoen_count += 1
                        questions.append({
                            'id': row[0] if row else f'auto_{row_num}',
                            'category': category,
                            'year': year,
                            'question': row[3] if len(row) > 3 else '',
                            'question_type': 'specialist',
                            'row_num': row_num
                        })
                        
                        if zoen_count <= 3:  # 最初の3問をログ出力
                            logger.info(f"造園問題 {zoen_count}: ID={row[0]}, 年度={year}, 問題={row[3][:50] if len(row) > 3 else 'なし'}...")
                            
    except Exception as e:
        logger.error(f"❌ CSVファイル読み込みエラー: {e}")
        return []
    
    logger.info(f"✅ 2016年造園問題数: {zoen_count}問")
    return questions

def test_department_mapping():
    """部門マッピングをテストします"""
    logger.info("=== 部門マッピングテスト開始 ===")
    
    from app import DEPARTMENT_TO_CATEGORY_MAPPING, normalize_department_name, get_department_category
    
    test_departments = ['造園', 'landscape']
    
    for dept in test_departments:
        logger.info(f"部門名: {dept}")
        normalized = normalize_department_name(dept)
        logger.info(f"  正規化後: {normalized}")
        
        category = get_department_category(normalized) if normalized else None
        logger.info(f"  カテゴリ: {category}")
        
        mapping_result = DEPARTMENT_TO_CATEGORY_MAPPING.get(dept)
        logger.info(f"  マッピング結果: {mapping_result}")
        logger.info("---")

def test_get_mixed_questions():
    """get_mixed_questions関数をテストします"""
    logger.info("=== get_mixed_questions関数テスト開始 ===")
    
    try:
        from app import get_mixed_questions, load_all_questions
        
        # 全問題を読み込み
        logger.info("全問題読み込み中...")
        all_questions = load_all_questions()
        logger.info(f"全問題数: {len(all_questions)}問")
        
        # 造園2016年の問題をフィルタ
        zoen_2016_questions = [
            q for q in all_questions 
            if q.get('category') == '造園' and str(q.get('year')) == '2016'
        ]
        logger.info(f"造園2016年問題数: {len(zoen_2016_questions)}問")
        
        if not zoen_2016_questions:
            logger.error("❌ 造園2016年の問題が見つかりません")
            return
        
        # get_mixed_questionsをテスト
        mock_session = {'history': [], 'srs_data': {}}
        
        logger.info("造園2016年でget_mixed_questionsを実行...")
        try:
            selected_questions = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='造園',
                session_size=10,
                department='造園',
                question_type='specialist',
                year=2016
            )
            
            if selected_questions:
                logger.info(f"✅ get_mixed_questions成功: {len(selected_questions)}問選択")
                for i, q in enumerate(selected_questions[:3], 1):
                    logger.info(f"  問題{i}: ID={q.get('id')}, カテゴリ={q.get('category')}, 年度={q.get('year')}")
            else:
                logger.error("❌ get_mixed_questionsが空の結果を返しました")
                
        except Exception as e:
            logger.error(f"❌ get_mixed_questions実行エラー: {e}")
            logger.exception("詳細なエラー情報:")
            
    except ImportError as e:
        logger.error(f"❌ app.pyのインポートエラー: {e}")

def test_valid_years():
    """有効年度の設定を確認します"""
    logger.info("=== 有効年度設定確認 ===")
    
    try:
        from app import VALID_YEARS
        logger.info(f"VALID_YEARS: {VALID_YEARS}")
        
        test_years = [2015, 2016, 2017, 2018, 2019]
        for year in test_years:
            is_valid = year in VALID_YEARS
            logger.info(f"年度 {year}: {'有効' if is_valid else '無効'}")
            
    except ImportError as e:
        logger.error(f"❌ VALID_YEARSのインポートエラー: {e}")

def analyze_error_handling():
    """エラーハンドリングロジックを分析します"""
    logger.info("=== エラーハンドリング分析 ===")
    
    try:
        from app import get_mixed_questions, load_all_questions, VALID_YEARS
        
        all_questions = load_all_questions()
        mock_session = {'history': [], 'srs_data': {}}
        
        # 各種条件でテスト
        test_cases = [
            {'dept': '造園', 'year': 2016, 'description': '造園2016年（正常ケース）'},
            {'dept': '造園', 'year': 2020, 'description': '造園2020年（無効年度）'},
            {'dept': '無効部門', 'year': 2016, 'description': '無効部門2016年'},
            {'dept': '道路', 'year': 2016, 'description': '道路2016年（比較用）'}
        ]
        
        for case in test_cases:
            logger.info(f"--- テストケース: {case['description']} ---")
            
            try:
                result = get_mixed_questions(
                    user_session=mock_session,
                    all_questions=all_questions,
                    requested_category=case['dept'],
                    session_size=10,
                    department=case['dept'],
                    question_type='specialist',
                    year=case['year']
                )
                
                if result:
                    logger.info(f"✅ 成功: {len(result)}問選択")
                else:
                    logger.warning(f"⚠️ 結果が空: 年度{case['year']}が{'有効' if case['year'] in VALID_YEARS else '無効'}")
                    
            except Exception as e:
                logger.error(f"❌ エラー発生: {e}")
                
    except Exception as e:
        logger.error(f"❌ エラーハンドリング分析失敗: {e}")

def main():
    """メイン実行関数"""
    logger.info("🔍 造園2016年エラー詳細分析を開始します")
    logger.info("="*60)
    
    try:
        # 1. CSVデータ確認
        load_csv_data()
        
        # 2. 部門マッピング確認
        test_department_mapping()
        
        # 3. 有効年度確認
        test_valid_years()
        
        # 4. get_mixed_questions関数テスト
        test_get_mixed_questions()
        
        # 5. エラーハンドリング分析
        analyze_error_handling()
        
        logger.info("="*60)
        logger.info("🔍 造園2016年エラー分析完了")
        
    except Exception as e:
        logger.error(f"❌ 分析実行中にエラーが発生しました: {e}")
        logger.exception("詳細なエラー情報:")

if __name__ == '__main__':
    main()