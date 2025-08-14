#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix 17 Manual Test
緊急対応-17手動テスト
Purpose: Manually test Emergency Fix 17 debug logging to understand execution flow
"""

import os
import sys
import time
from flask import Flask, session

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_emergency_fix_17_debug():
    """Test Emergency Fix 17 debug logging with manual session setup"""
    print("=== Emergency Fix 17 Manual Debug Test ===")
    print("Purpose: Manually test Emergency Fix 17 with construction environment session")
    print()
    
    try:
        # Import the app
        from app import app
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                print("1. Setting up construction environment session manually...")
                
                # Manually create a construction environment session similar to Emergency Fix 12
                construction_env_questions = [
                    {
                        'id': '190',
                        'category': '建設環境',
                        'year': '2019',
                        'question': 'Test construction environment question',
                        'option_a': 'Option A',
                        'option_b': 'Option B', 
                        'option_c': 'Option C',
                        'option_d': 'Option D',
                        'correct_answer': 'A',
                        'question_type': 'specialist'
                    }
                ]
                
                # Set up the emergency session structure that Emergency Fix 12 creates
                sess['questions'] = construction_env_questions
                sess['current_question'] = 0
                sess['exam_id'] = 'manual_test_session'
                sess['exam_type'] = 'specialist_env'
                
                print(f"   Session keys set: {list(sess.keys())}")
                print(f"   Questions count: {len(sess['questions'])}")
                print(f"   First question category: {sess['questions'][0]['category']}")
                print(f"   Should trigger Emergency Fix 17: {sess['questions'][0]['category'] == '建設環境'}")
                
            print("\n2. Accessing /exam route to trigger Emergency Fix 17...")
            response = client.get('/exam')
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response length: {len(response.get_data()) if response else 0} bytes")
            
            # Check session state after Emergency Fix 17 processing
            with client.session_transaction() as sess:
                print(f"\n3. Session state after /exam access:")
                print(f"   Session keys: {list(sess.keys())}")
                
                if 'exam_question_ids' in sess:
                    print(f"   exam_question_ids count: {len(sess.get('exam_question_ids', []))}")
                
                if 'exam_category' in sess:
                    print(f"   exam_category: '{sess.get('exam_category')}'")
                    category_correct = sess.get('exam_category') == '建設環境'
                    print(f"   Construction environment category preserved: {category_correct}")
                
                if 'questions' in sess:
                    print(f"   Original 'questions' key still exists: True")
                    print(f"   Original questions count: {len(sess.get('questions', []))}")
                else:
                    print(f"   Original 'questions' key still exists: False")
                
            print("\n=== Manual Test Results ===")
            if response and response.status_code == 200:
                print("✅ /exam route accessible")
                
                with client.session_transaction() as sess:
                    if sess.get('exam_category') == '建設環境':
                        print("✅ Emergency Fix 17 successfully preserved construction environment category")
                        print("✅ Manual test indicates Emergency Fix 17 is working correctly")
                    else:
                        print("❌ Emergency Fix 17 failed to preserve construction environment category")
                        print(f"❌ Expected '建設環境', got: '{sess.get('exam_category', 'NO_CATEGORY')}'")
            else:
                print("❌ /exam route failed or not accessible")
                
        print("\n4. Manual test completed")
                
    except Exception as e:
        print(f"Manual test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("Emergency Fix 17 Manual Debug Test")
    print("=" * 50)
    test_emergency_fix_17_debug()

if __name__ == "__main__":
    main()