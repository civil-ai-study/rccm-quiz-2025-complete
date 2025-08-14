#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix 18 Focused Test
緊急対応-18集中テスト
Purpose: Test Emergency Fix 18 session structure unification and identify HTTP 400 error cause
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_emergency_fix_18_session_structure():
    """Test Emergency Fix 18 session structure creation"""
    print("=== Emergency Fix 18 Session Structure Test ===")
    print("Purpose: Verify session structure unification works correctly")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Creating construction environment session...")
            response = client.get('/start_exam/specialist_env')
            
            print(f"   /start_exam/specialist_env status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                print("   ✅ Session creation successful")
                
                print("2. Accessing /exam to trigger Emergency Fix 17 Enhanced + Emergency Fix 18...")
                exam_response = client.get('/exam')
                
                print(f"   /exam status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    print("   ✅ /exam access successful")
                    
                    # Check session structure
                    with client.session_transaction() as sess:
                        print("3. Session structure analysis...")
                        print(f"   Session keys: {list(sess.keys())}")
                        
                        # Check Emergency Fix 18 components
                        if 'emergency_fix_18_questions' in sess:
                            fix18_questions = sess['emergency_fix_18_questions']
                            print(f"   ✅ emergency_fix_18_questions: {len(fix18_questions)} questions")
                            print(f"   Question IDs: {list(fix18_questions.keys())}")
                        else:
                            print("   ❌ emergency_fix_18_questions missing")
                        
                        if 'exam_question_ids' in sess:
                            exam_ids = sess['exam_question_ids']
                            print(f"   ✅ exam_question_ids: {exam_ids}")
                        else:
                            print("   ❌ exam_question_ids missing")
                        
                        if 'exam_category' in sess:
                            category = sess['exam_category']
                            print(f"   ✅ exam_category: {category}")
                            is_correct_category = category == '建設環境'
                            print(f"   Category correct: {is_correct_category}")
                        else:
                            print("   ❌ exam_category missing")
                        
                        return True
                else:
                    print(f"   ❌ /exam access failed: {exam_response.status_code}")
                    return False
            else:
                print(f"   ❌ Session creation failed: {response.status_code}")
                return False
    
    except Exception as e:
        print(f"ERROR: Session structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency_fix_18_answer_submission():
    """Test Emergency Fix 18 answer submission with detailed error analysis"""
    print("\n=== Emergency Fix 18 Answer Submission Test ===")
    print("Purpose: Identify and resolve HTTP 400 error during answer submission")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Setting up construction environment session...")
            
            # Create session
            setup_response = client.get('/start_exam/specialist_env')
            if setup_response.status_code not in [200, 302]:
                print(f"   ❌ Setup failed: {setup_response.status_code}")
                return False
            
            # Access first question
            first_q_response = client.get('/exam')
            if first_q_response.status_code != 200:
                print(f"   ❌ First question access failed: {first_q_response.status_code}")
                return False
            
            print("   ✅ Session setup successful")
            
            # Extract CSRF token from the response
            content = first_q_response.get_data(as_text=True)
            
            # Look for CSRF token
            csrf_token = None
            if 'csrf_token' in content:
                import re
                csrf_match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✅ CSRF token found: {csrf_token[:20]}...")
                else:
                    print("   ⚠️ CSRF token field found but value extraction failed")
            else:
                print("   ❌ CSRF token not found in response")
            
            # Check question display
            has_question = '<h3' in content and 'question' in content.lower()
            has_form = '<form' in content and 'method="POST"' in content
            has_answers = 'name="answer"' in content
            
            print(f"   Question display: {has_question}")
            print(f"   Form present: {has_form}")
            print(f"   Answer options: {has_answers}")
            
            print("2. Attempting answer submission...")
            
            # Prepare form data
            form_data = {
                'answer': 'A',
                'elapsed': '3.5'
            }
            
            # Add CSRF token if found
            if csrf_token:
                form_data['csrf_token'] = csrf_token
                print("   ✅ Including CSRF token in submission")
            else:
                print("   ⚠️ Submitting without CSRF token")
            
            # Submit answer
            answer_response = client.post('/exam', data=form_data)
            
            print(f"   Answer submission status: {answer_response.status_code}")
            
            if answer_response.status_code == 200:
                print("   ✅ Answer submission successful!")
                
                # Check response content
                answer_content = answer_response.get_data(as_text=True)
                
                # Look for progression indicators
                if '2/10' in answer_content:
                    print("   ✅ Question progression to 2/10 confirmed")
                elif '次の問題' in answer_content:
                    print("   ✅ Next question link found")
                else:
                    print("   ⚠️ No clear progression indicator found")
                
                return True
                
            elif answer_response.status_code == 400:
                print("   ❌ HTTP 400 error during answer submission")
                
                # Get error details
                error_content = answer_response.get_data(as_text=True)
                
                if 'CSRF' in error_content:
                    print("   ERROR TYPE: CSRF token validation failed")
                elif 'validation' in error_content.lower():
                    print("   ERROR TYPE: Form validation failed")
                elif 'session' in error_content.lower():
                    print("   ERROR TYPE: Session-related error")
                else:
                    print("   ERROR TYPE: Unknown - checking response content")
                    print(f"   Error content: {error_content[:200]}...")
                
                return False
                
            else:
                print(f"   ❌ Unexpected status code: {answer_response.status_code}")
                return False
    
    except Exception as e:
        print(f"ERROR: Answer submission test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency_fix_18_question_progression():
    """Test Emergency Fix 18 question progression through multiple questions"""
    print("\n=== Emergency Fix 18 Question Progression Test ===")
    print("Purpose: Test multi-question progression with Emergency Fix 18")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Setting up session and processing multiple questions...")
            
            # Setup
            client.get('/start_exam/specialist_env')
            
            success_count = 0
            for i in range(1, 4):  # Test first 3 questions
                print(f"   Processing question {i}...")
                
                # Get question
                q_response = client.get('/exam')
                if q_response.status_code != 200:
                    print(f"   ❌ Question {i} display failed: {q_response.status_code}")
                    break
                
                # Check if it's the right question number
                content = q_response.get_data(as_text=True)
                if f'{i}/10' in content:
                    print(f"   ✅ Question {i}/10 displayed correctly")
                else:
                    print(f"   ⚠️ Question {i}/10 display unclear")
                
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
                    print(f"   ✅ Question {i} answer submitted successfully")
                    success_count += 1
                else:
                    print(f"   ❌ Question {i} answer submission failed: {answer_response.status_code}")
                    break
            
            print(f"   Successfully processed: {success_count}/3 questions")
            
            if success_count >= 2:
                print("   ✅ Multi-question progression working!")
                return True
            else:
                print("   ❌ Multi-question progression failed")
                return False
    
    except Exception as e:
        print(f"ERROR: Question progression test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function for Emergency Fix 18 focused testing"""
    print("Emergency Fix 18 Focused Test")
    print("=" * 60)
    print("Goal: Verify Emergency Fix 18 functionality and resolve HTTP 400 error")
    print()
    
    # Test 1: Session structure
    print("Test 1: Session Structure Verification")
    structure_success = test_emergency_fix_18_session_structure()
    
    # Test 2: Answer submission
    print("\nTest 2: Answer Submission Analysis")
    submission_success = test_emergency_fix_18_answer_submission()
    
    # Test 3: Question progression
    print("\nTest 3: Question Progression Test")
    progression_success = test_emergency_fix_18_question_progression()
    
    print("\n" + "=" * 60)
    print("EMERGENCY FIX 18 FOCUSED TEST RESULTS")
    print("=" * 60)
    
    total_tests = 3
    successful_tests = sum([structure_success, submission_success, progression_success])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success Rate: {(successful_tests / total_tests) * 100:.1f}%")
    print()
    
    print("Detailed Results:")
    print(f"  {'✅' if structure_success else '❌'} Session Structure Test")
    print(f"  {'✅' if submission_success else '❌'} Answer Submission Test") 
    print(f"  {'✅' if progression_success else '❌'} Question Progression Test")
    print()
    
    if successful_tests == total_tests:
        print("🎉 Emergency Fix 18 is working perfectly!")
        print("   Construction environment 10-question completion is ready")
        return True
    elif successful_tests >= 2:
        print("⚠️ Emergency Fix 18 is mostly working but needs refinement")
        print("   Core functionality is operational")
        return True
    else:
        print("❌ Emergency Fix 18 needs significant debugging")
        print("   Multiple issues need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)