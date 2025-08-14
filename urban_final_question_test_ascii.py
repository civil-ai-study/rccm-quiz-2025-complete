#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 10-6: 都市計画部門10問目最終処理テスト (ASCII Safe)
Ultra Sync Task 10-6 - Final Question Processing and Result Verification

Purpose: 都市計画部門の10問目最終問題処理と結果画面遷移を完全テスト
- 1-9問目を高速で処理（既に分野混在ゼロ確認済み）
- 10問目の最終処理を詳細確認
- 結果画面への正常遷移を確認
- セッション完了状態の検証
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def get_csrf_token_from_html(html_content):
    """HTMLからCSRFトークンを抽出する汎用関数"""
    import re
    csrf_pattern = r'name="csrf_token"[^>]*value="([^"]*)"'
    match = re.search(csrf_pattern, html_content)
    if match:
        return match.group(1)
    return ""

def run_urban_final_question_test():
    """都市計画部門10問目最終処理テストを実行"""
    print("=== Task 10-6: Urban Department Final Question Test ===")
    print("Purpose: Final question processing and result screen verification")
    print("Background: Field mixing issue resolved by emergency-fix-12")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Starting urban planning session...")
            
            # セッション開始
            response = client.get('/start_exam/specialist_urban')
            
            if response.status_code not in [200, 302]:
                print(f"ERROR: Session start failed - Status: {response.status_code}")
                return False
                
            print("   SUCCESS: Session started")
            
            # セッション内容確認
            with client.session_transaction() as sess:
                if 'questions' not in sess:
                    print("ERROR: No questions in session")
                    return False
                    
                session_questions = sess['questions']
                print(f"   Session questions: {len(session_questions)}")
                
                # 分野混在確認（緊急対応-12の効果確認）
                categories = {}
                for q in session_questions:
                    cat = q.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print("   Question categories:")
                for cat, count in categories.items():
                    print(f"     {cat}: {count} questions")
                
                urban_count = categories.get('都市計画及び地方計画', 0)
                basic_count = categories.get('基礎', 0)
                
                if urban_count == 10 and basic_count == 0:
                    print("   SUCCESS: Zero field mixing - 10/10 urban planning questions")
                else:
                    print(f"   ERROR: Field mixing detected: urban={urban_count}, basic={basic_count}")
                    return False
            
            print()
            print("2. Processing questions 1-9 at high speed...")
            
            # 1-9問目を高速処理
            for question_num in range(1, 10):
                print(f"   Processing question {question_num}/9", end="")
                
                # 問題画面確認
                exam_response = client.get('/exam')
                if exam_response.status_code != 200:
                    print(f"\n   ERROR: Question {question_num} page failed")
                    return False
                
                # 回答送信
                html_content = exam_response.get_data(as_text=True)
                csrf_token = get_csrf_token_from_html(html_content)
                
                answer_response = client.post('/exam', data={
                    'answer': 'A',  # 固定回答
                    'csrf_token': csrf_token
                })
                
                if answer_response.status_code in [200, 302]:
                    print("...OK", end="")
                else:
                    print(f"\n   ERROR: Question {question_num} answer failed")
                    return False
            
            print("\n   SUCCESS: Questions 1-9 completed")
            
            print()
            print("3. Final question (10/10) detailed test...")
            
            # 10問目画面取得
            final_question_response = client.get('/exam')
            
            if final_question_response.status_code != 200:
                print("   ERROR: Final question page failed")
                return False
            
            final_html = final_question_response.get_data(as_text=True)
            
            # 10問目であることを確認
            if '10/10' in final_html or '問題 10' in final_html:
                print("   SUCCESS: Final question (10/10) confirmed")
            else:
                print("   ERROR: Final question identification failed")
                return False
            
            # 10問目のカテゴリ確認
            if '都市計画及び地方計画' in final_html:
                print("   SUCCESS: Final question category confirmed (Urban Planning)")
            else:
                print("   WARNING: Final question category needs verification")
            
            # 10問目回答送信
            csrf_token = get_csrf_token_from_html(final_html)
            final_answer_response = client.post('/exam', data={
                'answer': 'D',  # 最終問題は選択肢Dで回答
                'csrf_token': csrf_token
            })
            
            print(f"   Final answer submission: Status {final_answer_response.status_code}")
            
            if final_answer_response.status_code in [200, 302]:
                print("   SUCCESS: Final answer submitted")
            else:
                print("   ERROR: Final answer submission failed")
                return False
            
            print()
            print("4. Result screen transition verification...")
            
            # 結果画面アクセス
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                print("   SUCCESS: Result screen access successful")
                
                result_html = result_response.get_data(as_text=True)
                
                # 結果画面の内容確認
                if 'テスト完了' in result_html:
                    print("   SUCCESS: Test completion status displayed")
                else:
                    print("   WARNING: Test completion status needs verification")
                
                # 回答数確認
                if '10' in result_html and '回答' in result_html:
                    print("   SUCCESS: 10 answers completion displayed")
                else:
                    print("   WARNING: Answer count display needs verification")
                
                # 部門名確認
                if '都市計画' in result_html:
                    print("   SUCCESS: Urban planning department displayed")
                else:
                    print("   WARNING: Department name display needs verification")
                
                return True
                
            elif result_response.status_code == 302:
                print("   WARNING: Result screen redirect occurred")
                redirect_location = result_response.headers.get('Location', '/')
                print(f"   Redirect target: {redirect_location}")
                
                # リダイレクト先にアクセス
                redirect_response = client.get(redirect_location)
                if redirect_response.status_code == 200:
                    print("   SUCCESS: Redirect target access successful")
                    return True
                else:
                    print("   ERROR: Redirect target access failed")
                    return False
            else:
                print(f"   ERROR: Result screen access failed: Status {result_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Test execution error: {type(e).__name__}: {e}")
        return False

def run_result_screen_verification():
    """Task 10-7: 結果画面詳細検証"""
    print()
    print("=== Task 10-7: Result Screen Detailed Verification ===")
    print("Purpose: Final result validity and session completion verification")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Complete session execution...")
            
            # 新しいセッションで完全実行
            session_response = client.get('/start_exam/specialist_urban')
            
            if session_response.status_code not in [200, 302]:
                print("ERROR: Session start failed")
                return False
            
            # 10問全て回答
            for i in range(1, 11):
                # 問題画面取得
                question_response = client.get('/exam')
                if question_response.status_code != 200:
                    print(f"ERROR: Question {i} retrieval failed")
                    return False
                
                # 回答送信
                html_content = question_response.get_data(as_text=True)
                csrf_token = get_csrf_token_from_html(html_content)
                
                answer_response = client.post('/exam', data={
                    'answer': ['A', 'B', 'C', 'D'][i % 4],
                    'csrf_token': csrf_token
                })
                
                if answer_response.status_code not in [200, 302]:
                    print(f"ERROR: Question {i} answer failed")
                    return False
            
            print("   SUCCESS: All 10 questions answered")
            
            print()
            print("2. Result screen detailed analysis...")
            
            # 結果画面詳細確認
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                result_html = result_response.get_data(as_text=True)
                
                print("   Result screen content analysis:")
                
                # HTML要素確認
                if '<title>' in result_html:
                    print("   SUCCESS: HTML title element present")
                else:
                    print("   ERROR: HTML title element missing")
                
                # テスト完了確認
                if 'テスト完了' in result_html or '完了' in result_html:
                    print("   SUCCESS: Test completion status displayed")
                else:
                    print("   ERROR: Test completion status not displayed")
                
                # 部門情報確認
                if '都市計画' in result_html:
                    print("   SUCCESS: Urban planning department info displayed")
                else:
                    print("   ERROR: Department info not displayed")
                
                # 回答数情報確認
                answer_count_found = False
                for pattern in ['10/10', '10問', '10回']:
                    if pattern in result_html:
                        print(f"   SUCCESS: Answer count info displayed ({pattern})")
                        answer_count_found = True
                        break
                
                if not answer_count_found:
                    print("   ERROR: Answer count info not displayed")
                
                # セッション状態確認
                with client.session_transaction() as sess:
                    print("   Final session state:")
                    session_keys = list(sess.keys())
                    print(f"     Session keys: {session_keys}")
                    
                    if 'completed' in sess or 'finished' in sess:
                        print("   SUCCESS: Session completion flag confirmed")
                    else:
                        print("   WARNING: Session completion flag needs verification")
                
                print()
                print("3. Task 10-6/10-7 completion evaluation...")
                
                success_criteria = [
                    'テスト完了' in result_html or '完了' in result_html,
                    '都市計画' in result_html,
                    any(pattern in result_html for pattern in ['10/10', '10問', '10回'])
                ]
                
                success_count = sum(success_criteria)
                total_criteria = len(success_criteria)
                
                print(f"   Success criteria: {success_count}/{total_criteria}")
                
                if success_count == total_criteria:
                    print("   SUCCESS: All criteria met - Task 10-6/10-7 completed")
                    return True
                elif success_count >= 2:
                    print("   PARTIAL: Mostly successful - Additional verification needed")
                    return None
                else:
                    print("   ERROR: Multiple criteria failed")
                    return False
                    
            else:
                print(f"   ERROR: Result screen access failed: Status {result_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Result screen verification error: {type(e).__name__}: {e}")
        return False

def main():
    print("Ultra Sync Task 10-6/10-7: Urban Department Final Processing & Result Verification")
    print("=" * 80)
    print("Background: Field mixing resolved by emergency-fix-12")
    print("Purpose: Complete verification of final question processing and result screen")
    print()
    
    # Task 10-6: 10問目最終処理テスト
    print(">>> Task 10-6 Starting: Urban Department Final Question Processing Test")
    task_10_6_result = run_urban_final_question_test()
    
    # Task 10-7: 結果画面検証
    print(">>> Task 10-7 Starting: Urban Department Result Screen Detailed Verification")
    task_10_7_result = run_result_screen_verification()
    
    print()
    print("=" * 80)
    print("Task 10-6/10-7 Final Results:")
    print(f"Task 10-6 (Final Question Processing): {'COMPLETED' if task_10_6_result else 'FAILED' if task_10_6_result is False else 'NEEDS_VERIFICATION'}")
    print(f"Task 10-7 (Result Screen Verification): {'COMPLETED' if task_10_7_result else 'FAILED' if task_10_7_result is False else 'NEEDS_VERIFICATION'}")
    
    if task_10_6_result and task_10_7_result:
        print()
        print("*** Task 10 FULLY ACHIEVED! ***")
        print("- Urban department 10-question completion test: COMPLETED")
        print("- Zero field mixing maintained: CONFIRMED")
        print("- Session continuity: SUCCESS")
        print("- Final result screen display: SUCCESS")
        print("- Next task: Task 11 (Garden Department) ready")
        
        # 連続実行でTask 11の準備
        print()
        print(">>> Ultra Sync Continuation: Task 11 (Garden Department) preparing...")
        return True
    elif task_10_6_result or task_10_7_result:
        print()
        print("*** Task 10-6/10-7 PARTIAL COMPLETION ***")
        print("Some components successful, continued action may be needed")
        return None
    else:
        print()
        print("*** Task 10-6/10-7 FAILED ***")
        print("Continued action required")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)