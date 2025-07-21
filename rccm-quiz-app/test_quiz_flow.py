#!/usr/bin/env python3
"""
4-2専門科目選択フローのテスト
「4-2の選択問題を行って専門科目を選択して一問目を開いた問題が出てません」エラーの調査
"""

import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_specialist_question_flow():
    """専門科目問題フローをテスト"""
    
    with app.test_client() as client:
        # セッションを開始
        with client.session_transaction() as sess:
            sess['selected_department'] = '河川・砂防'
            sess['selected_question_type'] = 'specialist'
            sess['selected_year'] = 2019
        
        logger.info("=== 4-2専門科目選択フローテスト開始 ===")
        
        # 1. 部門選択
        logger.info("1. 部門選択 (/departments/river_sabo)")
        resp = client.get('/departments/river_sabo')
        logger.info(f"部門選択レスポンス: {resp.status_code}")
        
        # 2. 問題種別選択
        logger.info("2. 問題種別選択 (/departments/river_sabo/types)")
        resp = client.get('/departments/river_sabo/types')
        logger.info(f"問題種別選択レスポンス: {resp.status_code}")
        
        # 3. 試験開始（専門科目）
        logger.info("3. 試験開始 (/exam?question_type=specialist&department=河川・砂防&year=2019)")
        resp = client.get('/exam?question_type=specialist&department=河川・砂防&year=2019')
        logger.info(f"試験開始レスポンス: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"試験開始失敗: {resp.get_data(as_text=True)[:500]}")
            return False
        
        # 4. 一問目の表示確認
        logger.info("4. 一問目表示確認 (/quiz_question)")
        resp = client.get('/quiz_question')
        logger.info(f"一問目表示レスポンス: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"一問目表示失敗: {resp.get_data(as_text=True)[:500]}")
            return False
        
        logger.info("=== テスト完了 ===")
        return True

def test_csv_data_loading():
    """CSVデータの読み込みテスト"""
    logger.info("=== CSVデータ読み込みテスト ===")
    
    from utils import load_specialist_questions_only
    
    try:
        # 河川・砂防部門のデータを読み込み
        questions = load_specialist_questions_only('河川、砂防及び海岸・海洋', 2019)
        logger.info(f"河川・砂防 2019年度問題数: {len(questions)}問")
        
        if questions:
            first_q = questions[0]
            logger.info(f"最初の問題ID: {first_q.get('id')}")
            logger.info(f"カテゴリ: {first_q.get('category')}")
            logger.info(f"問題種別: {first_q.get('question_type')}")
            logger.info(f"年度: {first_q.get('year')}")
            
        return len(questions) > 0
        
    except Exception as e:
        logger.error(f"CSVデータ読み込みエラー: {e}")
        return False

def test_session_management():
    """セッション管理のテスト"""
    logger.info("=== セッション管理テスト ===")
    
    with app.test_client() as client:
        # セッションに問題IDを設定
        with client.session_transaction() as sess:
            sess['quiz_question_ids'] = [30, 31, 32]  # 河川・砂防の問題ID
            sess['quiz_current'] = 0
            sess['quiz_category'] = '河川・砂防'
        
        # quiz_questionルートをテスト
        resp = client.get('/quiz_question')
        logger.info(f"quiz_questionレスポンス: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"quiz_questionエラー: {resp.get_data(as_text=True)[:500]}")
            return False
        
        return True

if __name__ == "__main__":
    print("4-2専門科目問題フローの調査開始")
    
    # CSVデータ読み込みテスト
    csv_ok = test_csv_data_loading()
    print(f"CSVデータ読み込み: {'OK' if csv_ok else 'NG'}")
    
    # セッション管理テスト
    session_ok = test_session_management()
    print(f"セッション管理: {'OK' if session_ok else 'NG'}")
    
    # 専門科目フローテスト
    flow_ok = test_specialist_question_flow()
    print(f"専門科目フロー: {'OK' if flow_ok else 'NG'}")
    
    if not (csv_ok and session_ok and flow_ok):
        print("\n=== 問題が検出されました ===")
        if not csv_ok:
            print("- CSVデータの読み込みに問題があります")
        if not session_ok:
            print("- セッション管理に問題があります")
        if not flow_ok:
            print("- 専門科目フローに問題があります")
    else:
        print("\n=== 全てのテストが成功しました ===")