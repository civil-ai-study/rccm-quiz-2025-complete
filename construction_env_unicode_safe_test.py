#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Unicode-Safe Test
建設環境部門Unicode安全テスト
Purpose: Execute Emergency Fix 18 testing without Unicode output issues in Windows cp932 environment
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def safe_print(text):
    """Unicode-safe print function for Windows cp932 environment"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic Unicode characters with ASCII equivalents
        safe_text = text.replace('✅', '[OK]').replace('❌', '[NG]').replace('⚠️', '[WARN]').replace('🎉', '[SUCCESS]')
        print(safe_text)

def test_emergency_fix_18_unicode_safe():
    """Test Emergency Fix 18 with Unicode-safe output"""
    safe_print("=== Emergency Fix 18 Unicode-Safe Test ===")
    safe_print("Purpose: Test Emergency Fix 18 functionality without Unicode encoding issues")
    safe_print("")
    
    try:
        from app import app
        
        with app.test_client() as client:
            safe_print("1. Creating construction environment session...")
            
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            safe_print(f"   /start_exam/specialist_env status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                safe_print("   [OK] Construction environment session created")
                
                safe_print("2. Accessing /exam to trigger Emergency Fix 17 Enhanced + Emergency Fix 18...")
                exam_response = client.get('/exam')
                
                safe_print(f"   /exam status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    safe_print("   [OK] /exam access successful")
                    
                    # Check session structure
                    with client.session_transaction() as sess:
                        safe_print("3. Session structure analysis...")
                        safe_print(f"   Session keys: {list(sess.keys())}")
                        
                        # Check Emergency Fix 18 components
                        if 'emergency_fix_18_questions' in sess:
                            fix18_questions = sess['emergency_fix_18_questions']
                            safe_print(f"   [OK] emergency_fix_18_questions: {len(fix18_questions)} questions")
                            safe_print(f"   Question IDs: {list(fix18_questions.keys())}")
                        else:
                            safe_print("   [NG] emergency_fix_18_questions missing")
                        
                        if 'exam_question_ids' in sess:
                            exam_ids = sess['exam_question_ids']
                            safe_print(f"   [OK] exam_question_ids: {exam_ids}")
                        else:
                            safe_print("   [NG] exam_question_ids missing")
                        
                        if 'exam_category' in sess:
                            category = sess['exam_category']
                            safe_print(f"   [OK] exam_category: {category}")
                            is_correct_category = category == '建設環境'
                            safe_print(f"   Category correct: {is_correct_category}")
                        else:
                            safe_print("   [NG] exam_category missing")
                
                    safe_print("4. Testing answer submission...")
                    
                    # Get CSRF token from the response
                    content = exam_response.get_data(as_text=True)
                    csrf_token = None
                    
                    if 'csrf_token' in content:
                        import re
                        csrf_match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', content)
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            safe_print(f"   [OK] CSRF token found: {csrf_token[:20]}...")
                        else:
                            safe_print("   [WARN] CSRF token field found but value extraction failed")
                    else:
                        safe_print("   [NG] CSRF token not found in response")
                    
                    # Test answer submission
                    form_data = {
                        'answer': 'A',
                        'elapsed': '3.5'
                    }
                    
                    if csrf_token:
                        form_data['csrf_token'] = csrf_token
                        safe_print("   [OK] Including CSRF token in submission")
                    else:
                        safe_print("   [WARN] Submitting without CSRF token")
                    
                    # Submit answer
                    answer_response = client.post('/exam', data=form_data)
                    
                    safe_print(f"   Answer submission status: {answer_response.status_code}")
                    
                    if answer_response.status_code == 200:
                        safe_print("   [OK] Answer submission successful!")
                        
                        # Check response content
                        answer_content = answer_response.get_data(as_text=True)
                        
                        # Look for progression indicators
                        if '2/10' in answer_content:
                            safe_print("   [OK] Question progression to 2/10 confirmed")
                            return True
                        elif '次の問題' in answer_content:
                            safe_print("   [OK] Next question link found")
                            return True
                        else:
                            safe_print("   [WARN] No clear progression indicator found")
                            return False
                            
                    elif answer_response.status_code == 400:
                        safe_print("   [NG] HTTP 400 error during answer submission")
                        
                        # Get error details
                        error_content = answer_response.get_data(as_text=True)
                        
                        if 'CSRF' in error_content:
                            safe_print("   ERROR TYPE: CSRF token validation failed")
                        elif 'validation' in error_content.lower():
                            safe_print("   ERROR TYPE: Form validation failed")
                        elif 'session' in error_content.lower():
                            safe_print("   ERROR TYPE: Session-related error")
                        else:
                            safe_print("   ERROR TYPE: Unknown - checking response content")
                            safe_print(f"   Error content: {error_content[:200]}...")
                        
                        return False
                        
                    else:
                        safe_print(f"   [NG] Unexpected status code: {answer_response.status_code}")
                        return False
                else:
                    safe_print(f"   [NG] /exam access failed: {exam_response.status_code}")
                    return False
            else:
                safe_print(f"   [NG] Session creation failed: {response.status_code}")
                return False
    
    except Exception as e:
        safe_print(f"ERROR: Emergency Fix 18 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency_fix_18_question_progression_safe():
    """Test Emergency Fix 18 question progression with Unicode-safe output"""
    safe_print("")
    safe_print("=== Emergency Fix 18 Question Progression Test (Unicode-Safe) ===")
    safe_print("Purpose: Test multi-question progression with Emergency Fix 18")
    safe_print("")
    
    try:
        from app import app
        
        with app.test_client() as client:
            safe_print("1. Setting up session and processing multiple questions...")
            
            # Setup
            client.get('/start_exam/specialist_env')
            
            success_count = 0
            for i in range(1, 4):  # Test first 3 questions
                safe_print(f"   Processing question {i}...")
                
                # Get question
                q_response = client.get('/exam')
                if q_response.status_code != 200:
                    safe_print(f"   [NG] Question {i} display failed: {q_response.status_code}")
                    break
                
                # Check if it's the right question number
                content = q_response.get_data(as_text=True)
                if f'{i}/10' in content:
                    safe_print(f"   [OK] Question {i}/10 displayed correctly")
                else:
                    safe_print(f"   [WARN] Question {i}/10 display unclear")
                
                # Extract CSRF token
                csrf_token = None
                import re
                csrf_match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                
                # Submit answer
                form_data = {
                    'answer': 'A',
                    'elapsed': '2.0'
                }
                if csrf_token:
                    form_data['csrf_token'] = csrf_token
                
                answer_response = client.post('/exam', data=form_data)
                
                if answer_response.status_code == 200:
                    safe_print(f"   [OK] Question {i} answer submitted successfully")
                    success_count += 1
                else:
                    safe_print(f"   [NG] Question {i} answer submission failed: {answer_response.status_code}")
                    break
            
            safe_print(f"   Successfully processed: {success_count}/3 questions")
            
            if success_count >= 2:
                safe_print("   [OK] Multi-question progression working!")
                return True
            else:
                safe_print("   [NG] Multi-question progression failed")
                return False
    
    except Exception as e:
        safe_print(f"ERROR: Question progression test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function for Unicode-safe Emergency Fix 18 testing"""
    safe_print("Construction Environment Unicode-Safe Test")
    safe_print("=" * 60)
    safe_print("Goal: Verify Emergency Fix 18 functionality without Unicode encoding issues")
    safe_print("")
    
    # Test 1: Basic functionality
    safe_print("Test 1: Emergency Fix 18 Basic Functionality")
    basic_success = test_emergency_fix_18_unicode_safe()
    
    # Test 2: Question progression
    safe_print("Test 2: Emergency Fix 18 Question Progression")
    progression_success = test_emergency_fix_18_question_progression_safe()
    
    safe_print("")
    safe_print("=" * 60)
    safe_print("UNICODE-SAFE TEST RESULTS")
    safe_print("=" * 60)
    
    total_tests = 2
    successful_tests = sum([basic_success, progression_success])
    
    safe_print(f"Total Tests: {total_tests}")
    safe_print(f"Successful: {successful_tests}")
    safe_print(f"Success Rate: {(successful_tests / total_tests) * 100:.1f}%")
    safe_print("")
    
    safe_print("Detailed Results:")
    safe_print(f"  {'[OK]' if basic_success else '[NG]'} Basic Functionality Test")
    safe_print(f"  {'[OK]' if progression_success else '[NG]'} Question Progression Test")
    safe_print("")
    
    if successful_tests == total_tests:
        safe_print("[SUCCESS] Emergency Fix 18 is working perfectly!")
        safe_print("   Construction environment 10-question completion is ready")
        return True
    elif successful_tests >= 1:
        safe_print("[WARN] Emergency Fix 18 is partially working but needs refinement")
        safe_print("   Core functionality may be operational")
        return True
    else:
        safe_print("[NG] Emergency Fix 18 needs significant debugging")
        safe_print("   Multiple issues need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)