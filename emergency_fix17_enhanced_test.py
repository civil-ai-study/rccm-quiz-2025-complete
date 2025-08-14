#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix 17 Enhanced Test
緊急対応-17強化版テスト
Purpose: Test Emergency Fix 17 Enhanced with exam_session structure support
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_emergency_fix_17_enhanced():
    """Test Emergency Fix 17 Enhanced with exam_session structure"""
    print("=== Emergency Fix 17 Enhanced Test ===")
    print("Purpose: Test Emergency Fix 17 with exam_session structure from /start_exam")
    print()
    
    try:
        # Import the app
        from app import app
        
        with app.test_client() as client:
            print("1. Simulating /start_exam/specialist_env flow...")
            
            # First, access /start_exam/specialist_env to create exam_session structure
            response = client.get('/start_exam/specialist_env')
            print(f"   /start_exam/specialist_env response: {response.status_code}")
            
            # Check the session structure created by /start_exam/specialist_env
            with client.session_transaction() as sess:
                print(f"   Session keys after /start_exam: {list(sess.keys())}")
                
                if 'exam_session' in sess:
                    exam_session = sess['exam_session']
                    print(f"   exam_session keys: {list(exam_session.keys())}")
                    
                    if 'questions' in exam_session:
                        questions = exam_session['questions']
                        print(f"   Questions in exam_session: {len(questions)}")
                        if questions and len(questions) > 0:
                            category = questions[0].get('category', 'NO_CATEGORY')
                            print(f"   First question category: '{category}'")
                            print(f"   Should trigger Emergency Fix 17 Enhanced: {category == '建設環境'}")
                    else:
                        print("   No 'questions' key in exam_session")
                else:
                    print("   No 'exam_session' key in session")
            
            print("\n2. Accessing /exam to trigger Emergency Fix 17 Enhanced...")
            exam_response = client.get('/exam')
            print(f"   /exam response: {exam_response.status_code}")
            
            # Check session state after Emergency Fix 17 Enhanced processing
            with client.session_transaction() as sess:
                print(f"\n3. Session state after Emergency Fix 17 Enhanced:")
                print(f"   Session keys: {list(sess.keys())}")
                
                if 'exam_question_ids' in sess:
                    print(f"   exam_question_ids count: {len(sess.get('exam_question_ids', []))}")
                
                if 'exam_category' in sess:
                    category = sess.get('exam_category')
                    print(f"   exam_category: '{category}'")
                    success = category == '建設環境'
                    print(f"   Construction environment preserved: {success}")
                    
                    if success:
                        print("SUCCESS: Emergency Fix 17 Enhanced working with exam_session structure")
                        return True
                    else:
                        print("FAILED: Category not preserved correctly")
                        return False
                else:
                    print("FAILED: No exam_category set")
                    return False
                
    except Exception as e:
        print(f"Enhanced test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Emergency Fix 17 Enhanced Test")
    print("=" * 50)
    success = test_emergency_fix_17_enhanced()
    
    if success:
        print("\nTest Result: PASSED")
        print("Emergency Fix 17 Enhanced is working correctly with exam_session structure")
    else:
        print("\nTest Result: FAILED") 
        print("Emergency Fix 17 Enhanced needs further investigation")

if __name__ == "__main__":
    main()