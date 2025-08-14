#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Urban Department Session Creation Debug Test
Debugging why the session is not being created properly after emergency fix
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def debug_urban_session_creation():
    """Debug the urban department session creation process step by step"""
    print("=== Urban Department Session Creation Debug ===")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Testing GET /start_exam/specialist_urban...")
            
            # Step 1: Make the GET request with session tracking
            with client.session_transaction() as sess:
                print(f"   Session before request: {list(sess.keys())}")
            
            response = client.get('/start_exam/specialist_urban')
            print(f"   HTTP Status: {response.status_code}")
            
            # Step 2: Check session after request
            with client.session_transaction() as sess:
                print(f"   Session after request: {list(sess.keys())}")
                print(f"   Session contents:")
                for key, value in sess.items():
                    if key == 'questions' and isinstance(value, list):
                        print(f"     {key}: {len(value)} questions")
                        if len(value) > 0:
                            sample_q = value[0]
                            print(f"       Sample question category: {sample_q.get('category', 'unknown')}")
                    else:
                        print(f"     {key}: {type(value).__name__} - {str(value)[:100]}...")
            
            # Step 3: If we have a redirect, follow it
            if response.status_code == 302:
                print()
                print("2. Following redirect...")
                location = response.headers.get('Location', '/')
                print(f"   Redirect location: {location}")
                
                follow_response = client.get(location)
                print(f"   Follow-up HTTP Status: {follow_response.status_code}")
                
                # Check session again after following redirect
                with client.session_transaction() as sess:
                    print(f"   Session after redirect: {list(sess.keys())}")
                    if 'questions' in sess:
                        questions = sess['questions']
                        print(f"   Questions in session: {len(questions)}")
                        
                        if len(questions) > 0:
                            # Analyze question categories
                            categories = {}
                            for q in questions:
                                cat = q.get('category', 'unknown')
                                categories[cat] = categories.get(cat, 0) + 1
                            
                            print("   Question categories in session:")
                            for cat, count in categories.items():
                                print(f"     {cat}: {count} questions")
                            
                            # Check for urban planning questions specifically
                            urban_category = '都市計画及び地方計画'
                            urban_count = categories.get(urban_category, 0)
                            basic_count = categories.get('基礎', 0)
                            
                            if urban_count > 0 and basic_count == 0:
                                print("   ✅ SUCCESS: Urban planning questions only!")
                                return True
                            elif basic_count > 0 and urban_count == 0:
                                print("   ❌ PROBLEM: Only basic subject questions")
                                return False
                            else:
                                print(f"   ⚠️ MIXED: urban={urban_count}, basic={basic_count}")
                                return None
                        else:
                            print("   ❌ PROBLEM: No questions in session")
                            return False
                    else:
                        print("   ❌ PROBLEM: No 'questions' key in session")
                        return False
            else:
                print("   No redirect - checking direct response")
                return response.status_code == 200
                
    except Exception as e:
        print(f"ERROR during debug: {type(e).__name__}: {e}")
        return False

def test_emergency_functions_directly():
    """Test emergency functions directly to ensure they work"""
    print()
    print("=== Direct Emergency Function Test ===")
    
    try:
        from utils import emergency_get_questions
        
        print("Testing emergency_get_questions for urban department...")
        
        # Test with correct parameters
        urban_questions = emergency_get_questions(
            department='urban',
            question_type='specialist', 
            count=10
        )
        
        print(f"Emergency function returned: {len(urban_questions)} questions")
        
        if len(urban_questions) > 0:
            print("Sample question analysis:")
            for i, q in enumerate(urban_questions[:3], 1):
                print(f"  {i}. ID:{q.get('id')} Category:{q.get('category')} Type:{q.get('question_type')}")
            
            # Check all categories
            categories = set(q.get('category') for q in urban_questions)
            print(f"All categories in result: {categories}")
            
            # Check for field mixing
            expected_category = '都市計画及び地方計画'
            field_mixing = any(q.get('category') != expected_category for q in urban_questions)
            
            if not field_mixing:
                print("✅ Emergency function works correctly - zero field mixing")
                return True
            else:
                print("❌ Field mixing detected in emergency function")
                return False
        else:
            print("❌ Emergency function returned no questions")
            return False
            
    except Exception as e:
        print(f"ERROR testing emergency function: {type(e).__name__}: {e}")
        return False

def main():
    print("Urban Department Session Creation Debug Test")
    print("=" * 60)
    print()
    
    # Test 1: Direct emergency function test
    emergency_test_result = test_emergency_functions_directly()
    
    # Test 2: Session creation debug
    session_test_result = debug_urban_session_creation()
    
    print()
    print("=" * 60)
    print("DEBUG TEST RESULTS:")
    print(f"Emergency function test: {'PASS' if emergency_test_result else 'FAIL'}")
    print(f"Session creation test: {'PASS' if session_test_result else 'FAIL' if session_test_result is False else 'INCONCLUSIVE'}")
    
    if emergency_test_result and not session_test_result:
        print()
        print("DIAGNOSIS: Emergency functions work but session creation fails")
        print("LIKELY CAUSE: Session creation code path not using emergency functions properly")
        print("NEXT STEP: Need to investigate session creation route implementation")
    elif not emergency_test_result:
        print()
        print("DIAGNOSIS: Emergency functions are not working properly")
        print("LIKELY CAUSE: Parameter mismatch or function implementation issue")
    elif emergency_test_result and session_test_result:
        print()
        print("✅ DIAGNOSIS: Both emergency functions and session creation working!")
        print("The emergency fix has been successful")
    
    return emergency_test_result and session_test_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)