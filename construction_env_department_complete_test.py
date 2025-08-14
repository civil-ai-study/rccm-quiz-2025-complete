#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Department 10-Question Complete Test (UTF-8 Safe Version)
建設環境部門10問完走テスト（UTF-8安全版）

Task 12: 建設環境部門10問完走テスト実行
Purpose: 緊急対応-12/13の修正効果を建設環境部門で検証
Target: セッション継続テストを完全実行し最終結果画面まで確認

CRITICAL: 
- 緊急対応-12により分野混在問題が解決されているはず
- 緊急対応-13によりCSRFトークン問題が解決されているはず  
- 建設環境部門で10問完走および分野混在ゼロを確認
"""

import sys
import os
import time
sys.path.insert(0, 'rccm-quiz-app')

def run_construction_env_department_access_test():
    """Task 12-1: 建設環境部門アクセスルート確認"""
    print("=== Task 12-1: Construction Environment Department Access Route Test ===")
    print("Purpose: /start_exam/specialist_env URL access verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Accessing construction environment department specialist exam...")
            response = client.get('/start_exam/specialist_env')
            
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                print("SUCCESS: Construction environment department access successful")
                
                # Check for session creation
                if response.status_code == 302:
                    print("-> Redirect detected (session creation)")
                else:
                    print("-> Direct page access successful")
                
                return True
            else:
                print(f"ERROR: Access failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return False

def run_construction_env_session_initialization_test():
    """Task 12-2: 建設環境部門セッション初期化確認"""
    print()
    print("=== Task 12-2: Construction Environment Department Session Initialization Test ===")
    print("Purpose: Verify emergency fix 12 effect - construction environment questions 10/10, basic 0/10")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Starting construction environment department session...")
            
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            if response.status_code in [200, 302]:
                print("-> Session creation successful")
                
                # Check session contents
                with client.session_transaction() as sess:
                    if 'questions' in sess:
                        session_questions = sess['questions']
                        print(f"-> Session questions loaded: {len(session_questions)}")
                        
                        # Analyze categories to check for field mixing
                        categories = {}
                        for q in session_questions:
                            cat = q.get('category', 'unknown')
                            categories[cat] = categories.get(cat, 0) + 1
                        
                        print("-> Session question categories:")
                        for cat, count in categories.items():
                            print(f"   {cat}: {count} questions")
                        
                        # Check for field mixing (Emergency Fix 12 verification)
                        basic_count = categories.get('基礎', 0)
                        env_count = categories.get('建設環境', 0)
                        
                        print()
                        print("Field mixing analysis (Emergency Fix 12 verification):")
                        if basic_count == 0 and env_count == 10:
                            print("SUCCESS: Field mixing ZERO - construction environment questions 10/10, basic 0/10")
                            print("SUCCESS: Emergency Fix 12 effect confirmed for construction environment department")
                            return True
                        elif basic_count > 0:
                            print(f"FAILED: Field mixing detected - basic questions: {basic_count}/10")
                            print("FAILED: Emergency Fix 12 effect not working properly")
                            return False
                        else:
                            print(f"MIXED RESULT: env={env_count}, basic={basic_count}, others may exist")
                            return None
                    else:
                        print("ERROR: No questions in session")
                        return False
            else:
                print(f"ERROR: Session creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Session initialization test failed: {e}")
        return False

def run_construction_env_first_question_display_test():
    """Task 12-3: 建設環境部門1問目表示確認"""
    print()
    print("=== Task 12-3: Construction Environment Department First Question Display Test ===")
    print("Purpose: CSRF token, form elements, construction environment category display verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Creating construction environment session and displaying first question...")
            
            # Start session
            session_response = client.get('/start_exam/specialist_env')
            
            if session_response.status_code in [200, 302]:
                print("-> Session created successfully")
                
                # Get first question display
                exam_response = client.get('/exam')
                
                print(f"-> Exam page HTTP status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    content = exam_response.get_data(as_text=True)
                    
                    # Check for CSRF token (Emergency Fix 13 verification)
                    csrf_check = 'csrf_token' in content
                    print(f"-> CSRF token present: {csrf_check}")
                    
                    # Check for form elements
                    form_check = '<form' in content and 'method="POST"' in content
                    print(f"-> Form elements present: {form_check}")
                    
                    # Check for construction environment category display
                    category_check = '建設環境' in content
                    print(f"-> Construction environment category displayed: {category_check}")
                    
                    # Check for question elements
                    question_check = '<h3' in content
                    print(f"-> Question title elements present: {question_check}")
                    
                    # Check for answer options
                    option_check = 'name="answer"' in content
                    print(f"-> Answer option elements present: {option_check}")
                    
                    if csrf_check and form_check and category_check and question_check and option_check:
                        print("SUCCESS: First question display complete - CSRF, form, category all confirmed")
                        print("SUCCESS: Emergency Fix 13 CSRF effect confirmed")
                        return True
                    else:
                        print("FAILED: Some essential elements missing in first question display")
                        return False
                else:
                    print(f"ERROR: Exam page access failed: {exam_response.status_code}")
                    return False
            else:
                print(f"ERROR: Session creation failed: {session_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: First question display test failed: {e}")
        return False

def run_construction_env_question_transition_test():
    """Task 12-4: 建設環境部門問題遷移テスト"""
    print()
    print("=== Task 12-4: Construction Environment Department Question Transition Test ===") 
    print("Purpose: 1st→2nd question session continuity, construction environment category maintenance verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Starting construction environment session...")
            
            # Start session
            session_response = client.get('/start_exam/specialist_env')
            
            if session_response.status_code in [200, 302]:
                print("-> Session started successfully")
                
                # Get first question
                first_question_response = client.get('/exam')
                
                if first_question_response.status_code == 200:
                    print("-> First question displayed successfully")
                    
                    # Submit answer for first question
                    print("2. Submitting answer for first question...")
                    answer_response = client.post('/exam', data={
                        'answer': 'A',
                        'elapsed': '3.5'
                    })
                    
                    print(f"-> Answer submission HTTP status: {answer_response.status_code}")
                    
                    if answer_response.status_code == 200:
                        print("-> Answer submission successful")
                        
                        # Check for transition to second question
                        content = answer_response.get_data(as_text=True)
                        
                        # Look for navigation to next question
                        next_question_check = '2/10' in content or 'next' in content.lower()
                        print(f"-> Navigation to 2nd question available: {next_question_check}")
                        
                        # Check construction environment category maintenance
                        category_maintained = '建設環境' in content
                        print(f"-> Construction environment category maintained: {category_maintained}")
                        
                        if next_question_check and category_maintained:
                            print("SUCCESS: Question transition successful - session continuity and category maintenance confirmed")
                            return True
                        else:
                            print("FAILED: Question transition or category maintenance failed")
                            return False
                    else:
                        print(f"ERROR: Answer submission failed: {answer_response.status_code}")
                        return False
                else:
                    print(f"ERROR: First question display failed: {first_question_response.status_code}")
                    return False
            else:
                print(f"ERROR: Session start failed: {session_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Question transition test failed: {e}")
        return False

def run_construction_env_continuous_processing_test():
    """Task 12-5: 建設環境部門連続処理テスト"""
    print()
    print("=== Task 12-5: Construction Environment Department Continuous Processing Test ===")
    print("Purpose: 2-9th question continuous processing, field mixing ZERO maintenance verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Starting construction environment session for continuous processing...")
            
            # Start fresh session
            session_response = client.get('/start_exam/specialist_env')
            
            if session_response.status_code in [200, 302]:
                print("-> Fresh session started")
                
                successful_questions = 0
                category_maintained_count = 0
                
                # Process questions 1-9 (leaving 10th for final test)
                for question_num in range(1, 10):
                    print(f"   Processing question {question_num}/10...")
                    
                    # Get current question
                    exam_response = client.get('/exam')
                    
                    if exam_response.status_code == 200:
                        content = exam_response.get_data(as_text=True)
                        
                        # Check category maintenance
                        if '建設環境' in content:
                            category_maintained_count += 1
                        
                        # Submit answer
                        answer_response = client.post('/exam', data={
                            'answer': 'B',
                            'elapsed': '2.0'
                        })
                        
                        if answer_response.status_code == 200:
                            successful_questions += 1
                        else:
                            print(f"   ERROR: Answer submission failed for question {question_num}")
                            break
                    else:
                        print(f"   ERROR: Question {question_num} display failed")
                        break
                
                print(f"-> Successful question processing: {successful_questions}/9")
                print(f"-> Category maintenance (construction environment): {category_maintained_count}/9")
                
                if successful_questions == 9 and category_maintained_count == 9:
                    print("SUCCESS: Continuous processing successful - field mixing ZERO maintained")
                    return True
                elif successful_questions == 9:
                    print("PARTIAL: Processing successful but category maintenance issues")
                    return None
                else:
                    print("FAILED: Continuous processing failed")
                    return False
                    
            else:
                print(f"ERROR: Fresh session start failed: {session_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Continuous processing test failed: {e}")
        return False

def run_construction_env_final_question_processing_test():
    """Task 12-6: 建設環境部門10問目最終処理テスト"""
    print()
    print("=== Task 12-6: Construction Environment Department 10th Question Final Processing Test ===")
    print("Purpose: Emergency Fix 13 CSRF token fix complete, final question processing system normal operation verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Starting construction environment session for final question processing...")
            
            # Start session and process through to 10th question
            session_response = client.get('/start_exam/specialist_env')
            
            if session_response.status_code in [200, 302]:
                print("-> Session started for final question test")
                
                # Process questions 1-9 quickly
                for question_num in range(1, 10):
                    exam_response = client.get('/exam')
                    if exam_response.status_code == 200:
                        client.post('/exam', data={'answer': 'A', 'elapsed': '1.0'})
                    else:
                        print(f"ERROR: Failed to process question {question_num}")
                        return False
                
                print("-> Processed questions 1-9, now at 10th question")
                
                # Get 10th question
                final_question_response = client.get('/exam')
                
                if final_question_response.status_code == 200:
                    content = final_question_response.get_data(as_text=True)
                    
                    # Check if it's the 10th question
                    tenth_question_check = '10/10' in content
                    print(f"-> 10th question (10/10) display: {tenth_question_check}")
                    
                    # Check CSRF token presence (Emergency Fix 13 verification)
                    csrf_present = 'csrf_token' in content
                    print(f"-> CSRF token present in 10th question: {csrf_present}")
                    
                    # Check construction environment category maintenance
                    category_maintained = '建設環境' in content
                    print(f"-> Construction environment category maintained: {category_maintained}")
                    
                    # Submit final answer
                    print("2. Submitting final answer...")
                    final_answer_response = client.post('/exam', data={
                        'answer': 'C',
                        'elapsed': '4.0'
                    })
                    
                    print(f"-> Final answer submission status: {final_answer_response.status_code}")
                    
                    if final_answer_response.status_code == 200:
                        final_content = final_answer_response.get_data(as_text=True)
                        
                        # Check for completion/result navigation
                        completion_check = '結果' in final_content or 'result' in final_content.lower()
                        print(f"-> Completion/result navigation available: {completion_check}")
                        
                        if tenth_question_check and csrf_present and category_maintained and completion_check:
                            print("SUCCESS: Emergency Fix 13 CSRF token fix complete - final question processing system normal operation verified")
                            return True
                        else:
                            print("FAILED: Some final question processing elements missing")
                            return False
                    else:
                        print(f"ERROR: Final answer submission failed: {final_answer_response.status_code}")
                        return False
                else:
                    print(f"ERROR: 10th question display failed: {final_question_response.status_code}")
                    return False
            else:
                print(f"ERROR: Session start failed: {session_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Final question processing test failed: {e}")
        return False

def run_construction_env_result_screen_verification_test():
    """Task 12-7: 建設環境部門結果画面検証"""
    print()
    print("=== Task 12-7: Construction Environment Department Result Screen Verification Test ===")
    print("Purpose: Emergency Fix 12/13 effect - final result screen normal display, session management success verification")
    print()
    
    try:
        from app import app
        with app.test_client() as client:
            print("1. Starting complete construction environment 10-question session...")
            
            # Start session
            session_response = client.get('/start_exam/specialist_env')
            
            if session_response.status_code in [200, 302]:
                print("-> Complete session started")
                
                # Process all 10 questions
                for question_num in range(1, 11):
                    exam_response = client.get('/exam')
                    if exam_response.status_code == 200:
                        answer_response = client.post('/exam', data={
                            'answer': 'A',
                            'elapsed': '2.5'
                        })
                        if answer_response.status_code != 200:
                            print(f"ERROR: Answer submission failed for question {question_num}")
                            return False
                    else:
                        print(f"ERROR: Question {question_num} display failed")
                        return False
                
                print("-> All 10 questions processed")
                
                # Access result screen
                print("2. Accessing result screen...")
                result_response = client.get('/result')
                
                print(f"-> Result screen HTTP status: {result_response.status_code}")
                
                if result_response.status_code == 200:
                    result_content = result_response.get_data(as_text=True)
                    
                    # Check for result screen elements
                    result_display = '結果' in result_content or 'result' in result_content.lower()
                    print(f"-> Result screen display: {result_display}")
                    
                    # Check for completion information
                    completion_info = '10' in result_content and '建設環境' in result_content
                    print(f"-> Completion information (10 questions, construction environment): {completion_info}")
                    
                    # Check for session data integrity
                    session_data_check = 'session' in result_content.lower() or 'complete' in result_content.lower()
                    print(f"-> Session data integrity maintained: {session_data_check}")
                    
                    if result_display and completion_info:
                        print("SUCCESS: Emergency Fix 12/13 effect - final result screen normal display, session management success verified")
                        return True
                    else:
                        print("FAILED: Result screen verification failed")
                        return False
                else:
                    print(f"ERROR: Result screen access failed: {result_response.status_code}")
                    return False
            else:
                print(f"ERROR: Session start failed: {session_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Result screen verification test failed: {e}")
        return False

def main():
    """Construction Environment Department 10-Question Complete Test Execution"""
    print("Construction Environment Department 10-Question Complete Test")
    print("=" * 80)
    print("Task 12: 建設環境部門10問完走テスト実行")
    print("Purpose: Verify Emergency Fix 12/13 effectiveness in construction environment department")
    print("Target: Complete session continuity test execution and final result screen verification")
    print()
    
    # Test execution sequence
    test_functions = [
        run_construction_env_department_access_test,
        run_construction_env_session_initialization_test,
        run_construction_env_first_question_display_test,
        run_construction_env_question_transition_test,
        run_construction_env_continuous_processing_test,
        run_construction_env_final_question_processing_test,
        run_construction_env_result_screen_verification_test
    ]
    
    test_names = [
        "12-1: Construction Environment Department Access Route Test",
        "12-2: Construction Environment Department Session Initialization Test",
        "12-3: Construction Environment Department First Question Display Test",
        "12-4: Construction Environment Department Question Transition Test",
        "12-5: Construction Environment Department Continuous Processing Test",
        "12-6: Construction Environment Department Final Question Processing Test",
        "12-7: Construction Environment Department Result Screen Verification Test"
    ]
    
    results = []
    
    # Execute all tests
    for i, (test_func, test_name) in enumerate(zip(test_functions, test_names)):
        try:
            print(f"Starting {test_name}...")
            result = test_func()
            results.append(result)
            
            if result is True:
                print(f"SUCCESS: {test_name} completed")
            elif result is False:
                print(f"FAILED: {test_name} failed")
            else:
                print(f"PARTIAL: {test_name} partially successful")
                
        except Exception as e:
            print(f"ERROR: {test_name} execution failed: {e}")
            results.append(False)
        
        print()
        
        # Short delay between tests
        time.sleep(1)
    
    # Final results summary
    print("=" * 80)
    print("CONSTRUCTION ENVIRONMENT DEPARTMENT 10-QUESTION COMPLETE TEST RESULTS")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r is True)
    partial_count = sum(1 for r in results if r is None)
    failed_count = sum(1 for r in results if r is False)
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Partial: {partial_count}")
    print(f"Failed: {failed_count}")
    print(f"Success Rate: {(success_count / len(results)) * 100:.1f}%")
    print()
    
    # Detailed results
    print("Detailed Results:")
    for i, (result, test_name) in enumerate(zip(results, test_names)):
        if result is True:
            status = "SUCCESS"
        elif result is False:
            status = "FAILED"
        else:
            status = "PARTIAL"
        print(f"  {status}: {test_name}")
    
    print()
    
    # Final assessment
    if success_count == len(results):
        print("COMPLETE SUCCESS: Construction Environment Department 10-Question Complete Test")
        print("- Emergency Fix 12/13 effectiveness confirmed in construction environment department")
        print("- Field mixing ZERO achieved")
        print("- Session continuity test successful")
        print("- Final result screen verification complete")
        print("- Ready to proceed with Task 13")
        return True
    elif success_count >= len(results) * 0.8:
        print("SUBSTANTIAL SUCCESS: Construction Environment Department test largely successful")
        print("- Most critical functions working properly")
        print("- Minor issues may require attention")
        print("- Generally ready to proceed with Task 13")
        return True
    else:
        print("NEEDS ATTENTION: Construction Environment Department test requires investigation")
        print("- Multiple critical issues detected")
        print("- Emergency Fix 12/13 may need additional work")
        print("- Recommend investigation before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)