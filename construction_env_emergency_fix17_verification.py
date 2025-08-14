#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Emergency Fix 17 Verification
建設環境部門緊急対応-17検証
Purpose: Analyze why Emergency Fix 17 still allows session replacement
"""

import os
import sys
from flask import Flask, session
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def main():
    """Construction Environment Emergency Fix 17 Verification Test"""
    print("Construction Environment Emergency Fix 17 Verification Test")
    print("=" * 80)
    print("Purpose: Analyze why Emergency Fix 17 still allows session replacement")
    print()

    try:
        # Import the app to test the actual implementation
        from app import app, emergency_load_all_questions
        
        print("=== 1. Testing Emergency Fix 17 Logic ===")
        
        # Test the emergency data loading
        all_questions = emergency_load_all_questions()
        print(f"Total questions loaded: {len(all_questions)}")
        
        # Filter construction environment questions
        env_questions = [q for q in all_questions if q.get('category') == '建設環境']
        print(f"Construction environment questions available: {len(env_questions)}")
        
        # Test with Flask test client to simulate the actual flow
        with app.test_client() as client:
            print("\n=== 2. Testing Session Flow ===")
            
            # Step 1: Create construction environment session via start_exam
            response1 = client.get('/start_exam/specialist_env')
            print(f"Step 1 - Start exam response: {response1.status_code}")
            
            if response1.status_code == 200:
                # Check session after start_exam
                with client.session_transaction() as sess:
                    print(f"After start_exam - Session keys: {list(sess.keys())}")
                    if 'questions' in sess:
                        questions = sess['questions']
                        print(f"Questions in session: {len(questions)}")
                        if questions:
                            categories = [q.get('category', 'Unknown') for q in questions]
                            print(f"Question categories: {set(categories)}")
            
            # Step 2: Access /exam route (this is where replacement occurs)
            response2 = client.get('/exam')
            print(f"Step 2 - Exam route response: {response2.status_code}")
            
            if response2.status_code == 200:
                # Check session after /exam
                with client.session_transaction() as sess:
                    print(f"After /exam - Session keys: {list(sess.keys())}")
                    if 'exam_question_ids' in sess:
                        question_ids = sess['exam_question_ids']
                        print(f"Exam question IDs: {len(question_ids) if question_ids else 0}")
                        
                        if 'exam_category' in sess:
                            category = sess.get('exam_category')
                            print(f"Exam category: {category}")
                        
                        # Check if the questions are still construction environment
                        if question_ids:
                            # Find the actual questions by ID
                            actual_questions = [q for q in all_questions if q['id'] in question_ids]
                            if actual_questions:
                                actual_categories = [q.get('category', 'Unknown') for q in actual_questions]
                                print(f"Actual question categories after /exam: {set(actual_categories)}")
        
        print("\n=== 3. Analyzing Root Cause ===")
        print("Checking the exam() function implementation...")
        
        # Read the relevant part of app.py to see Emergency Fix 17 implementation
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find Emergency Fix 17 implementation
        if 'EMERGENCY FIX 17' in content:
            print("✅ Emergency Fix 17 found in code")
            
            # Check if the logic is in the right place
            lines = content.split('\n')
            fix17_lines = [i for i, line in enumerate(lines) if 'EMERGENCY FIX 17' in line]
            
            for line_num in fix17_lines:
                print(f"Emergency Fix 17 at line {line_num + 1}: {lines[line_num].strip()}")
            
            # Check if the fix is before the new session creation logic
            new_session_lines = [i for i, line in enumerate(lines) if '新規セッションを開始' in line]
            if new_session_lines and fix17_lines:
                fix_line = min(fix17_lines)
                new_session_line = min(new_session_lines)
                print(f"Fix at line {fix_line + 1}, New session logic at line {new_session_line + 1}")
                
                if fix_line < new_session_line:
                    print("✅ Emergency Fix 17 is positioned before new session logic")
                else:
                    print("❌ Emergency Fix 17 may be positioned after new session logic")
        else:
            print("❌ Emergency Fix 17 not found in code")
        
        print("\n=== 4. Detailed Session Detection Analysis ===")
        
        # Test the actual conditions used in Emergency Fix 17
        with app.test_client() as client:
            # Create a construction environment session
            response1 = client.get('/start_exam/specialist_env')
            
            if response1.status_code == 200:
                with client.session_transaction() as sess:
                    print("Session detection test:")
                    
                    # Test the conditions from Emergency Fix 17
                    has_emergency_session = 'questions' in sess and sess.get('questions')
                    has_standard_session = 'exam_question_ids' in sess and sess.get('exam_question_ids')
                    
                    print(f"has_emergency_session: {has_emergency_session}")
                    print(f"has_standard_session: {has_standard_session}")
                    
                    if has_emergency_session:
                        emergency_questions = sess.get('questions', [])
                        if emergency_questions and len(emergency_questions) > 0:
                            first_question = emergency_questions[0]
                            category = first_question.get('category')
                            print(f"First question category: {category}")
                            print(f"Is construction environment: {category == '建設環境'}")
                            
                # Now access /exam route to trigger Emergency Fix 17
                print("\nTrigger Emergency Fix 17 by accessing /exam:")
                response2 = client.get('/exam')
                print(f"Response status: {response2.status_code}")
                
                with client.session_transaction() as sess:
                    print("After /exam session state:")
                    print(f"Session keys: {list(sess.keys())}")
                    
                    if 'exam_category' in sess:
                        print(f"Final exam_category: {sess.get('exam_category')}")
                    
                    if 'exam_question_ids' in sess:
                        question_ids = sess['exam_question_ids']
                        print(f"Final question count: {len(question_ids) if question_ids else 0}")
        
        print("\n=== 5. Conclusion ===")
        print("The session replacement issue may be due to:")
        print("1. Emergency Fix 17 logic not executing properly")
        print("2. Conditions not matching the actual session state")
        print("3. New session creation logic overriding the fix")
        print("4. Session detection logic failing")
        print("5. The fix may be too late in the exam() function flow")
        
    except Exception as e:
        print(f"Verification failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()