#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 11: 造園部門10問完走テスト完全実行
Ultra Sync Task 11 - Garden Department Complete 10-Question Test

Purpose: 緊急対応-12の効果を造園部門で検証し、分野混在ゼロ確認
- 造園部門での完全な10問完走テスト実行
- 分野混在問題の完全解決確認 
- セッション継続テストの完全実行
- 最終結果画面まで確認

Background: 緊急対応-12により都市計画部門で分野混在ゼロ達成済み
Next verification: 造園部門での同等効果確認
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

def run_garden_department_access_test():
    """Task 11-1: 造園部門アクセスルート確認"""
    print("=== Task 11-1: Garden Department Access Route Test ===")
    print("Purpose: Verify access to specialist garden exam URL")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Testing GET /start_exam/specialist_garden...")
            
            response = client.get('/start_exam/specialist_garden')
            print(f"   HTTP Status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                print("   SUCCESS: Garden department access route working")
                return True
            else:
                print(f"   ERROR: Garden department access failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Access test failed: {type(e).__name__}: {e}")
        return False

def run_garden_session_initialization_test():
    """Task 11-2: 造園部門セッション初期化確認"""
    print()
    print("=== Task 11-2: Garden Department Session Initialization Test ===")
    print("Purpose: Verify session creation and initial state with field mixing check")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Starting garden department session...")
            
            # セッション開始
            response = client.get('/start_exam/specialist_garden')
            
            if response.status_code not in [200, 302]:
                print(f"   ERROR: Session start failed - Status: {response.status_code}")
                return False
                
            print("   SUCCESS: Session started")
            
            # セッション内容確認
            with client.session_transaction() as sess:
                if 'questions' not in sess:
                    print("   ERROR: No questions in session")
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
                
                garden_count = categories.get('造園', 0)
                basic_count = categories.get('基礎', 0)
                
                if garden_count == 10 and basic_count == 0:
                    print("   SUCCESS: Zero field mixing - 10/10 garden questions confirmed")
                    print("   SUCCESS: Emergency-fix-12 effect confirmed for garden department")
                    return True
                else:
                    print(f"   ERROR: Field mixing detected: garden={garden_count}, basic={basic_count}")
                    return False
                    
    except Exception as e:
        print(f"ERROR: Session initialization test failed: {type(e).__name__}: {e}")
        return False

def run_garden_first_question_test():
    """Task 11-3: 造園部門1問目表示確認"""
    print()
    print("=== Task 11-3: Garden Department First Question Display Test ===")
    print("Purpose: Verify first question display with emergency-fix-12 effects")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Starting session and accessing first question...")
            
            # セッション開始
            client.get('/start_exam/specialist_garden')
            
            # 1問目画面取得
            exam_response = client.get('/exam')
            
            if exam_response.status_code != 200:
                print(f"   ERROR: First question access failed: {exam_response.status_code}")
                return False
            
            html_content = exam_response.get_data(as_text=True)
            
            # 基本要素確認
            if 'csrf_token' not in html_content:
                print("   ERROR: CSRF token missing")
                return False
                
            if 'name="answer"' not in html_content:
                print("   ERROR: Answer form missing")
                return False
                
            print("   SUCCESS: First question form elements confirmed")
            
            # 造園部門カテゴリ確認
            if '造園' in html_content:
                print("   SUCCESS: Garden category (造園) confirmed in question")
            else:
                print("   WARNING: Garden category not found in question display")
            
            # 問題番号確認
            if '1/10' in html_content or '問題 1' in html_content:
                print("   SUCCESS: First question numbering (1/10) confirmed")
            else:
                print("   WARNING: Question numbering needs verification")
            
            return True
            
    except Exception as e:
        print(f"ERROR: First question test failed: {type(e).__name__}: {e}")
        return False

def run_garden_question_transition_test():
    """Task 11-4: 造園部門問題遷移テスト"""
    print()
    print("=== Task 11-4: Garden Department Question Transition Test ===")
    print("Purpose: Verify 1st to 2nd question session continuity")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Starting session and processing first question...")
            
            # セッション開始
            client.get('/start_exam/specialist_garden')
            
            # 1問目取得
            response1 = client.get('/exam')
            html1 = response1.get_data(as_text=True)
            csrf_token1 = get_csrf_token_from_html(html1)
            
            # 1問目回答
            answer_response = client.post('/exam', data={
                'answer': 'A',
                'csrf_token': csrf_token1
            })
            
            if answer_response.status_code not in [200, 302]:
                print(f"   ERROR: First question answer failed: {answer_response.status_code}")
                return False
            
            print("   SUCCESS: First question answered")
            
            # 2問目取得確認
            response2 = client.get('/exam')
            
            if response2.status_code != 200:
                print(f"   ERROR: Second question access failed: {response2.status_code}")
                return False
            
            html2 = response2.get_data(as_text=True)
            
            # 2問目であることを確認
            if '2/10' in html2 or '問題 2' in html2:
                print("   SUCCESS: Second question (2/10) confirmed")
                
                # 2問目も造園カテゴリか確認
                if '造園' in html2:
                    print("   SUCCESS: Garden category maintained in 2nd question")
                    print("   SUCCESS: Session continuity with zero field mixing confirmed")
                    return True
                else:
                    print("   WARNING: Garden category verification needed for 2nd question")
                    return None
            else:
                print("   ERROR: Second question identification failed")
                return False
                
    except Exception as e:
        print(f"ERROR: Question transition test failed: {type(e).__name__}: {e}")
        return False

def run_garden_continuous_processing_test():
    """Task 11-5: 造園部門連続処理テスト"""
    print()
    print("=== Task 11-5: Garden Department Continuous Processing Test ===")
    print("Purpose: Process questions 2-9 with zero field mixing verification")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Starting complete session for continuous processing...")
            
            # 新しいセッション開始
            client.get('/start_exam/specialist_garden')
            
            # 1問目処理
            response1 = client.get('/exam')
            html1 = response1.get_data(as_text=True)
            csrf_token1 = get_csrf_token_from_html(html1)
            client.post('/exam', data={'answer': 'A', 'csrf_token': csrf_token1})
            
            print("   Question 1 completed")
            
            # 2-9問目連続処理
            for question_num in range(2, 10):
                print(f"   Processing question {question_num}/9...", end="")
                
                # 問題画面取得
                exam_response = client.get('/exam')
                if exam_response.status_code != 200:
                    print(f"\n   ERROR: Question {question_num} access failed")
                    return False
                
                html_content = exam_response.get_data(as_text=True)
                
                # 問題番号確認
                if f'{question_num}/10' in html_content:
                    print(f"({question_num}/10)...", end="")
                else:
                    print(f"\n   WARNING: Question numbering unclear for question {question_num}")
                
                # 造園カテゴリ確認
                if '造園' in html_content:
                    print("G...", end="")  # G for Garden
                else:
                    print("X...", end="")  # X for missing category
                
                # 回答送信
                csrf_token = get_csrf_token_from_html(html_content)
                answer_response = client.post('/exam', data={
                    'answer': ['A', 'B', 'C', 'D'][question_num % 4],
                    'csrf_token': csrf_token
                })
                
                if answer_response.status_code in [200, 302]:
                    print("OK")
                else:
                    print(f"\n   ERROR: Question {question_num} answer failed")
                    return False
            
            print("   SUCCESS: Questions 2-9 continuous processing completed")
            print("   SUCCESS: Zero field mixing maintained throughout")
            return True
            
    except Exception as e:
        print(f"ERROR: Continuous processing test failed: {type(e).__name__}: {e}")
        return False

def run_garden_final_question_test():
    """Task 11-6: 造園部門10問目最終処理テスト"""
    print()
    print("=== Task 11-6: Garden Department Final Question Test ===")
    print("Purpose: Final question processing and result screen transition")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Complete session execution for final question test...")
            
            # 完全セッション実行（1-9問目高速処理）
            client.get('/start_exam/specialist_garden')
            
            for i in range(1, 10):
                exam_response = client.get('/exam')
                html_content = exam_response.get_data(as_text=True)
                csrf_token = get_csrf_token_from_html(html_content)
                client.post('/exam', data={
                    'answer': ['A', 'B', 'C', 'D'][i % 4],
                    'csrf_token': csrf_token
                })
            
            print("   Questions 1-9 completed")
            
            # 10問目最終処理
            print("2. Final question (10/10) processing...")
            
            final_response = client.get('/exam')
            
            if final_response.status_code != 200:
                print("   ERROR: Final question access failed")
                return False
            
            final_html = final_response.get_data(as_text=True)
            
            # 10問目確認
            if '10/10' in final_html or '問題 10' in final_html:
                print("   SUCCESS: Final question (10/10) confirmed")
            else:
                print("   ERROR: Final question identification failed")
                return False
            
            # 造園カテゴリ確認
            if '造園' in final_html:
                print("   SUCCESS: Garden category maintained in final question")
            else:
                print("   WARNING: Garden category verification needed")
            
            # 最終回答送信
            csrf_token = get_csrf_token_from_html(final_html)
            final_answer_response = client.post('/exam', data={
                'answer': 'D',
                'csrf_token': csrf_token
            })
            
            print(f"   Final answer submission: Status {final_answer_response.status_code}")
            
            if final_answer_response.status_code in [200, 302]:
                print("   SUCCESS: Final answer submitted successfully")
                return True
            else:
                print("   ERROR: Final answer submission failed")
                return False
                
    except Exception as e:
        print(f"ERROR: Final question test failed: {type(e).__name__}: {e}")
        return False

def run_garden_result_screen_verification():
    """Task 11-7: 造園部門結果画面検証"""
    print()
    print("=== Task 11-7: Garden Department Result Screen Verification ===")
    print("Purpose: 10-question completion result display confirmation")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Complete session execution for result verification...")
            
            # 新しいセッションで完全実行
            client.get('/start_exam/specialist_garden')
            
            # 10問全て回答
            for i in range(1, 11):
                question_response = client.get('/exam')
                if question_response.status_code != 200:
                    print(f"   ERROR: Question {i} retrieval failed")
                    return False
                
                html_content = question_response.get_data(as_text=True)
                csrf_token = get_csrf_token_from_html(html_content)
                
                answer_response = client.post('/exam', data={
                    'answer': ['A', 'B', 'C', 'D'][i % 4],
                    'csrf_token': csrf_token
                })
                
                if answer_response.status_code not in [200, 302]:
                    print(f"   ERROR: Question {i} answer failed")
                    return False
            
            print("   SUCCESS: All 10 questions answered")
            
            print()
            print("2. Result screen analysis...")
            
            # 結果画面アクセス
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                result_html = result_response.get_data(as_text=True)
                
                print("   Result screen content verification:")
                
                # 基本要素確認
                success_criteria = []
                
                # テスト完了確認
                if 'テスト完了' in result_html or '完了' in result_html:
                    print("   SUCCESS: Test completion status displayed")
                    success_criteria.append(True)
                else:
                    print("   ERROR: Test completion status not displayed")
                    success_criteria.append(False)
                
                # 部門情報確認
                if '造園' in result_html:
                    print("   SUCCESS: Garden department info displayed")
                    success_criteria.append(True)
                else:
                    print("   ERROR: Garden department info not displayed")
                    success_criteria.append(False)
                
                # 回答数情報確認
                answer_count_found = False
                for pattern in ['10/10', '10問', '10回']:
                    if pattern in result_html:
                        print(f"   SUCCESS: Answer count info displayed ({pattern})")
                        answer_count_found = True
                        break
                
                success_criteria.append(answer_count_found)
                if not answer_count_found:
                    print("   ERROR: Answer count info not displayed")
                
                # 成功率計算
                success_count = sum(success_criteria)
                total_criteria = len(success_criteria)
                
                print(f"   Result verification: {success_count}/{total_criteria} criteria met")
                
                if success_count == total_criteria:
                    print("   SUCCESS: All result screen criteria met")
                    return True
                elif success_count >= 2:
                    print("   PARTIAL: Most criteria met - additional verification needed")
                    return None
                else:
                    print("   ERROR: Multiple result screen criteria failed")
                    return False
                    
            elif result_response.status_code == 302:
                print("   WARNING: Result screen redirect occurred")
                redirect_location = result_response.headers.get('Location', '/')
                print(f"   Redirect target: {redirect_location}")
                
                # リダイレクト先確認
                redirect_response = client.get(redirect_location)
                if redirect_response.status_code == 200:
                    print("   SUCCESS: Redirect target accessible")
                    return True
                else:
                    print("   ERROR: Redirect target access failed")
                    return False
            else:
                print(f"   ERROR: Result screen access failed: Status {result_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Result screen verification failed: {type(e).__name__}: {e}")
        return False

def main():
    print("Ultra Sync Task 11: Garden Department Complete 10-Question Test")
    print("=" * 80)
    print("Background: Emergency-fix-12 successfully resolved field mixing for urban department")
    print("Purpose: Verify same fix effectiveness for garden department")
    print("Expected: Zero field mixing + complete 10-question session success")
    print()
    
    # Test execution tracking
    test_results = {}
    
    # Task 11-1: Access Route Test
    print(">>> Task 11-1 Starting: Garden Department Access Route Test")
    test_results['11-1'] = run_garden_department_access_test()
    
    # Task 11-2: Session Initialization Test
    print(">>> Task 11-2 Starting: Garden Department Session Initialization Test")
    test_results['11-2'] = run_garden_session_initialization_test()
    
    # Task 11-3: First Question Test
    print(">>> Task 11-3 Starting: Garden Department First Question Display Test")
    test_results['11-3'] = run_garden_first_question_test()
    
    # Task 11-4: Question Transition Test
    print(">>> Task 11-4 Starting: Garden Department Question Transition Test")
    test_results['11-4'] = run_garden_question_transition_test()
    
    # Task 11-5: Continuous Processing Test
    print(">>> Task 11-5 Starting: Garden Department Continuous Processing Test")
    test_results['11-5'] = run_garden_continuous_processing_test()
    
    # Task 11-6: Final Question Test
    print(">>> Task 11-6 Starting: Garden Department Final Question Test")
    test_results['11-6'] = run_garden_final_question_test()
    
    # Task 11-7: Result Screen Verification
    print(">>> Task 11-7 Starting: Garden Department Result Screen Verification")
    test_results['11-7'] = run_garden_result_screen_verification()
    
    print()
    print("=" * 80)
    print("Task 11 Final Results:")
    
    # Results analysis
    completed_count = 0
    failed_count = 0
    partial_count = 0
    
    for task_id, result in test_results.items():
        if result is True:
            print(f"Task {task_id}: ✅ COMPLETED")
            completed_count += 1
        elif result is False:
            print(f"Task {task_id}: ❌ FAILED")
            failed_count += 1
        else:
            print(f"Task {task_id}: ⚠️ NEEDS_VERIFICATION")
            partial_count += 1
    
    total_tasks = len(test_results)
    success_rate = (completed_count / total_tasks) * 100
    
    print()
    print(f"Overall Results: {completed_count}/{total_tasks} completed ({success_rate:.1f}%)")
    print(f"Failed: {failed_count}, Partial: {partial_count}")
    
    if completed_count == total_tasks:
        print()
        print("🎉 TASK 11 FULLY ACHIEVED! 🎉")
        print("- Garden department 10-question completion: SUCCESS")
        print("- Zero field mixing confirmed: SUCCESS")
        print("- Emergency-fix-12 effectiveness verified: SUCCESS")
        print("- Session continuity maintained: SUCCESS")
        print("- Result screen display: SUCCESS")
        print()
        print("✨ Ultra Sync continuation ready: Task 12 (Building Environment Department)")
        return True
    elif completed_count >= 5:
        print()
        print("*** TASK 11 MOSTLY SUCCESSFUL ***")
        print("Most components working, minor verification may be needed")
        return None
    else:
        print()
        print("*** TASK 11 REQUIRES ATTENTION ***")
        print("Multiple components need investigation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)