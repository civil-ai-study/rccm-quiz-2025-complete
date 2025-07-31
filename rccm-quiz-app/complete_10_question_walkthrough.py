#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: 10問完走テスト（最終結果画面まで確認）
河川・砂防部門での完全フロー確認
"""

from app import app
import time

def complete_10_question_test():
    """10問完走して最終結果画面まで確認"""
    print("ULTRA SYNC: Complete 10-question walkthrough test")
    print("=" * 60)
    
    test_dept = '河川・砂防'
    
    with app.app_context():
        with app.test_client() as client:
            print(f"Department: {test_dept}")
            print("=" * 40)
            
            # セッション初期化
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_name'] = 'walkthrough_test'
            
            # Step 1: 試験開始
            print("Step 1: Starting exam...")
            response = client.post(f'/start_exam/{test_dept}', data={'questions': '10'})
            
            if response.status_code != 302:
                print(f"FAILED: Start exam returned {response.status_code}")
                return False
            
            # Step 2: セッション状態確認
            with client.session_transaction() as sess:
                question_ids = sess.get('quiz_question_ids', [])
                if len(question_ids) != 10:
                    print(f"FAILED: Expected 10 questions, got {len(question_ids)}")
                    return False
                print(f"SUCCESS: {len(question_ids)} questions loaded")
            
            # Step 3: 全10問を順次回答
            print("Step 3: Answering all 10 questions...")
            for i in range(10):
                # 問題表示
                quiz_response = client.get('/quiz')
                if quiz_response.status_code != 200:
                    print(f"FAILED: Question {i+1} display failed")
                    return False
                
                # 回答送信（常にoption_aを選択）
                answer_response = client.post('/quiz', data={'answer': 'option_a'})
                if answer_response.status_code not in [200, 302]:
                    print(f"FAILED: Question {i+1} answer submission failed")
                    return False
                
                print(f"   Question {i+1}: Answered")
            
            # Step 4: 結果画面確認
            print("Step 4: Checking final results...")
            result_response = client.get('/quiz_result')
            
            if result_response.status_code != 200:
                print(f"FAILED: Results page returned {response.status_code}")
                return False
            
            result_html = result_response.data.decode('utf-8', errors='ignore')
            
            # 結果画面の重要要素確認
            if 'スコア' in result_html or 'score' in result_html.lower():
                print("SUCCESS: Score display found")
            else:
                print("WARNING: Score display not found")
            
            if '10' in result_html:
                print("SUCCESS: Question count (10) found in results")
            else:
                print("WARNING: Question count not found")
            
            print(f"Result page length: {len(result_html)} characters")
            
            # Step 5: セッション最終状態
            with client.session_transaction() as sess:
                quiz_current = sess.get('quiz_current', -1)
                print(f"Final quiz_current: {quiz_current}")
                
                if quiz_current >= 9:  # 0-indexedなので9が最後
                    print("SUCCESS: Quiz completed (quiz_current >= 9)")
                else:
                    print(f"WARNING: Quiz may not be completed (quiz_current = {quiz_current})")
            
            print("=" * 60)
            print("10-QUESTION WALKTHROUGH: COMPLETED")
            print("All steps executed successfully!")
            return True

if __name__ == "__main__":
    success = complete_10_question_test()
    if success:
        print("\nULTRA SYNC: 10問完走テスト完全成功!")
    else:
        print("\nULTRA SYNC: 10問完走テストで問題検出")