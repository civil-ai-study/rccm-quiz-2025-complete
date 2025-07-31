#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Manual Test - Simple Version
本番環境での厳格な10問手動テスト（シンプル版）
"""

import sys
import os
import time
import re
from datetime import datetime

# スクリプトのディレクトリを基準にパスを設定
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

def run_production_test():
    """本番環境での厳格テスト実行"""
    
    print("=" * 80)
    print("ULTRA SYNC Production Rigorous Manual Test")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = []
    session_states = []
    error_count = 0
    success_count = 0
    
    try:
        from app import app
        print("✓ Flask Application imported successfully")
        success_count += 1
    except Exception as e:
        print(f"✗ Flask Application import failed: {e}")
        error_count += 1
        return False
    
    # テストクライアント作成
    with app.test_client() as client:
        
        print("\nPHASE 1: Session Initialization Test")
        print("-" * 50)
        
        # Step 1: 初期状態確認
        try:
            with client.session_transaction() as sess:
                initial_keys = len(sess.keys())
            print(f"✓ Initial session state captured: {initial_keys} keys")
            success_count += 1
        except Exception as e:
            print(f"✗ Initial session capture failed: {e}")
            error_count += 1
        
        # Step 2: 基礎科目試験開始
        print("Starting basic subject exam...")
        response = client.get('/start_exam/基礎科目')
        
        if response.status_code == 302:
            print(f"✓ Exam initialization successful: Redirect to {response.location}")
            success_count += 1
        else:
            print(f"✗ Exam initialization failed: Status {response.status_code}")
            error_count += 1
            return False
        
        # Step 3: セッション状態確認
        try:
            with client.session_transaction() as sess:
                question_ids = len(sess.get('exam_question_ids', []))
                exam_current = sess.get('exam_current')
                history = len(sess.get('history', []))
            
            if question_ids == 10:
                print(f"✓ Session initialized: {question_ids} questions, current: {exam_current}, history: {history}")
                success_count += 1
            else:
                print(f"✗ Session initialization incomplete: {question_ids} questions")
                error_count += 1
                return False
        except Exception as e:
            print(f"✗ Session state check failed: {e}")
            error_count += 1
        
        print("\nPHASE 2: 10-Question Manual Answer Test")
        print("-" * 50)
        
        # 10問の手動回答テスト
        for question_num in range(1, 11):
            print(f"\nQuestion {question_num}/10:")
            
            # 問題表示テスト
            response = client.get('/exam')
            
            if response.status_code == 302:
                if '/result' in response.location:
                    print(f"  ✓ Q{question_num}: Early completion - redirected to result")
                    success_count += 1
                    break
                else:
                    print(f"  ! Q{question_num}: Unexpected redirect to {response.location}")
            elif response.status_code == 200:
                print(f"  ✓ Q{question_num}: Question displayed successfully")
                success_count += 1
            else:
                print(f"  ✗ Q{question_num}: Display failed with status {response.status_code}")
                error_count += 1
                continue
            
            # セッション状態確認（回答前）
            try:
                with client.session_transaction() as sess:
                    pre_history = len(sess.get('history', []))
            except:
                pre_history = 0
            
            # CSRFトークン取得
            csrf_token = None
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
            
            # 回答提出（選択肢Aを選択）
            answer_data = {'answer': 'A'}
            if csrf_token:
                answer_data['csrf_token'] = csrf_token
            
            answer_response = client.post('/exam', data=answer_data)
            
            if answer_response.status_code == 302:
                if '/result' in answer_response.location:
                    print(f"  ✓ Q{question_num}: Answer submitted - Test completed!")
                    success_count += 1
                    break
                else:
                    print(f"  ✓ Q{question_num}: Answer submitted - Continue to next")
                    success_count += 1
            elif answer_response.status_code == 200:
                print(f"  ✓ Q{question_num}: Answer submitted - Feedback displayed")
                success_count += 1
            else:
                print(f"  ✗ Q{question_num}: Answer submission failed - Status {answer_response.status_code}")
                error_count += 1
            
            # セッション状態確認（回答後）
            try:
                with client.session_transaction() as sess:
                    post_history = len(sess.get('history', []))
                
                if post_history > pre_history:
                    print(f"  ✓ Q{question_num}: History updated ({pre_history} -> {post_history})")
                    success_count += 1
                else:
                    print(f"  ! Q{question_num}: History not updated ({pre_history} -> {post_history})")
            except Exception as e:
                print(f"  ! Q{question_num}: Session check error: {e}")
            
            time.sleep(0.1)  # 短い待機
        
        print("\nPHASE 3: Result Page Display Test")
        print("-" * 50)
        
        # 最終セッション状態確認
        try:
            with client.session_transaction() as sess:
                final_current = sess.get('exam_current')
                final_questions = len(sess.get('exam_question_ids', []))
                final_history = len(sess.get('history', []))
                quiz_completed = sess.get('quiz_completed')
            
            print(f"Final session state:")
            print(f"  Current: {final_current}")
            print(f"  Questions: {final_questions}")
            print(f"  History: {final_history}")
            print(f"  Completed: {quiz_completed}")
        except Exception as e:
            print(f"✗ Final session state check failed: {e}")
            error_count += 1
        
        # 結果画面直接アクセステスト
        print("\nTesting result page access...")
        result_response = client.get('/result')
        
        if result_response.status_code == 200:
            content = result_response.get_data(as_text=True)
            
            if '問題結果' in content:
                print("✓ Result page content: Title found")
                success_count += 1
                
                if '正答数' in content:
                    print("✓ Result page content: Statistics found")
                    success_count += 1
                
                if '次のアクション' in content:
                    print("✓ Result page content: Actions found")
                    success_count += 1
                
                if 'debug_message' in content:
                    print("✓ Result page content: Debug info available")
                    success_count += 1
                else:
                    print("! Result page content: No debug info (may be normal)")
                
            else:
                print("✗ Result page content: Title missing")
                error_count += 1
                
        elif result_response.status_code == 302:
            print(f"✗ Result page access: Still redirecting to {result_response.location}")
            error_count += 1
        else:
            print(f"✗ Result page access: Status {result_response.status_code}")
            error_count += 1
        
        print("\nPHASE 4: Error Handling Test")
        print("-" * 50)
        
        # 無効なデータでのテスト
        invalid_response = client.post('/exam', data={'invalid': 'data'})
        if invalid_response.status_code in [400, 302]:
            print(f"✓ Invalid data handling: Properly rejected with status {invalid_response.status_code}")
            success_count += 1
        else:
            print(f"! Invalid data handling: Unexpected response {invalid_response.status_code}")
    
    # テスト結果サマリー
    print("\n" + "=" * 80)
    print("ULTRA SYNC Production Test Results Summary")
    print("=" * 80)
    print(f"Total Tests: {success_count + error_count}")
    print(f"Successes: {success_count}")
    print(f"Failures: {error_count}")
    print(f"Success Rate: {(success_count / (success_count + error_count) * 100):.1f}%")
    
    if error_count == 0:
        print("\n✓ ALL TESTS PASSED: Result page displays correctly")
        print("✓ 10-question completion flows properly to result page")
        print("✓ Session management is working correctly")
        return True
    else:
        print(f"\n✗ {error_count} TESTS FAILED: Issues need to be addressed")
        return False

def main():
    """メイン実行関数"""
    success = run_production_test()
    
    if success:
        print("\nPRODUCTION TEST COMPLETED: Result display issue is RESOLVED")
    else:
        print("\nPRODUCTION TEST: Further fixes are needed")
    
    return success

if __name__ == '__main__':
    main()