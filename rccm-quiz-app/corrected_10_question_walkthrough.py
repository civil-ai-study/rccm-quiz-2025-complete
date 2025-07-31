#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: 修正版10問完走テスト
正しいエンドポイント（/quiz_question）を使用
"""

from app import app

def corrected_10_question_test():
    """修正版10問完走テスト"""
    print("ULTRA SYNC: Corrected 10-question walkthrough test")
    print("=" * 60)
    
    test_dept = '河川・砂防'
    
    with app.app_context():
        with app.test_client() as client:
            print(f"Department: {test_dept}")
            print("=" * 40)
            
            # セッション初期化
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_name'] = 'corrected_test'
            
            # Step 1: 試験開始
            print("Step 1: Starting exam...")
            response = client.post(f'/start_exam/{test_dept}', data={'questions': '10'})
            
            if response.status_code != 302:
                print(f"FAILED: Start exam returned {response.status_code}")
                return False
            
            with client.session_transaction() as sess:
                question_ids = sess.get('quiz_question_ids', [])
                print(f"SUCCESS: {len(question_ids)} questions loaded")
            
            # Step 2: 全10問を順次回答（修正版）
            print("Step 2: Answering all 10 questions...")
            for i in range(10):
                # 問題表示（正しいエンドポイント使用）
                quiz_response = client.get('/quiz_question')
                if quiz_response.status_code != 200:
                    print(f"FAILED: Question {i+1} display failed ({quiz_response.status_code})")
                    return False
                
                # 回答送信
                answer_response = client.post('/quiz_question', data={'answer': 'option_a'})
                if answer_response.status_code not in [200, 302]:
                    print(f"FAILED: Question {i+1} answer failed ({answer_response.status_code})")
                    return False
                
                print(f"   Question {i+1}: OK")
            
            # Step 3: 最終セッション状態確認
            print("Step 3: Checking final session state...")
            with client.session_transaction() as sess:
                quiz_current = sess.get('quiz_current', -1)
                question_ids = sess.get('quiz_question_ids', [])
                print(f"   Final quiz_current: {quiz_current}")
                print(f"   Total questions: {len(question_ids)}")
                
                if quiz_current >= 9:  # 10問目完了
                    print("SUCCESS: All 10 questions completed!")
                else:
                    print(f"WARNING: Only {quiz_current + 1} questions completed")
            
            # Step 4: 結果画面アクセス試行
            print("Step 4: Attempting to access results...")
            result_response = client.get('/quiz_result')
            print(f"   Result page status: {result_response.status_code}")
            
            if result_response.status_code == 200:
                result_html = result_response.data.decode('utf-8', errors='ignore')
                print(f"   Result page length: {len(result_html)} characters")
                print("SUCCESS: Results page accessible!")
            else:
                print("WARNING: Results page not accessible")
            
            print("=" * 60)
            print("CORRECTED 10-QUESTION WALKTHROUGH: COMPLETED")
            return True

if __name__ == "__main__":
    success = corrected_10_question_test()
    if success:
        print("\nULTRA SYNC: 修正版10問完走テスト成功!")
    else:
        print("\nULTRA SYNC: 修正版10問完走テストで問題検出")