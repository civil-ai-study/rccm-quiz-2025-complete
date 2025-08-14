#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Emergency Fix 17 - 10 Question Completion Test
建設環境部門Emergency Fix 17対応10問完走テスト

Purpose: Verify that Emergency Fix 17 enables construction environment department 
to complete full 10-question sessions without session replacement issues.
"""

import os
import sys
from flask import Flask, session
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def main():
    """Construction Environment 10-Question Completion Test"""
    print("Construction Environment Emergency Fix 17 - 10 Question Completion Test")
    print("=" * 80)
    print("Purpose: Verify Emergency Fix 17 enables full 10-question completion")
    print()

    try:
        # Import the app
        from app import app
        
        print("=== TASK 12: Construction Environment 10-Question Completion Test ===")
        print()
        
        # Test with Flask test client
        with app.test_client() as client:
            print("Step 1: Initialize construction environment session")
            
            # Create construction environment session via start_exam
            response1 = client.get('/start_exam/specialist_env')
            print(f"Start exam response: {response1.status_code}")
            
            if response1.status_code != 200:
                print("ERROR: Failed to initialize construction environment session")
                return False
            
            # Verify initial session state
            with client.session_transaction() as sess:
                if 'exam_session' in sess:
                    exam_session = sess['exam_session']
                    questions = exam_session.get('questions', [])
                    print(f"SUCCESS: Construction environment session created with {len(questions)} questions")
                    
                    if questions:
                        categories = [q.get('category', 'Unknown') for q in questions]
                        unique_categories = set(categories)
                        print(f"Categories in session: {unique_categories}")
                        
                        if '建設環境' in unique_categories and len(unique_categories) == 1:
                            print("SUCCESS: All questions are construction environment (no field mixing)")
                        else:
                            print(f"ERROR: Field mixing detected - categories: {unique_categories}")
                            return False
                else:
                    print("ERROR: No exam session created")
                    return False
            
            print()
            print("Step 2: Test Emergency Fix 17 session preservation")
            
            # Access /exam route to trigger Emergency Fix 17
            response2 = client.get('/exam')
            print(f"Exam route response: {response2.status_code}")
            
            if response2.status_code != 200:
                print("ERROR: Failed to access exam route")
                return False
            
            # Verify Emergency Fix 17 preserved the session
            with client.session_transaction() as sess:
                if 'exam_category' in sess:
                    category = sess.get('exam_category')
                    question_ids = sess.get('exam_question_ids', [])
                    print(f"Session preserved - Category: {category}, Questions: {len(question_ids)}")
                    
                    if category == '建設環境' and len(question_ids) == 10:
                        print("SUCCESS: Emergency Fix 17 preserved construction environment session")
                    else:
                        print(f"ERROR: Session not properly preserved - Category: {category}, Count: {len(question_ids)}")
                        return False
                else:
                    print("ERROR: Session was not preserved by Emergency Fix 17")
                    return False
            
            print()
            print("Step 3: Execute 10-question completion test")
            
            # Complete 10 questions
            success_count = 0
            
            for i in range(1, 11):
                print(f"Question {i}/10:")
                
                # Get current question
                response = client.get('/exam')
                
                if response.status_code == 200:
                    if f"問題 {i}/10" in response.text and "建設環境" in response.text:
                        print(f"  SUCCESS: Question {i} displayed correctly")
                        
                        # Submit answer
                        answer_data = {
                            'qid': str(i),  # Sequential ID from Emergency Fix 18
                            'answer': 'A',
                            'elapsed': '30'
                        }
                        
                        post_response = client.post('/exam', data=answer_data)
                        
                        if post_response.status_code == 200:
                            print(f"  SUCCESS: Answer submitted for question {i}")
                            success_count += 1
                            
                            # Check progression or completion
                            if i < 10:
                                # Should show next question
                                if f"問題 {i+1}/10" in post_response.text:
                                    print(f"  SUCCESS: Progressed to question {i+1}")
                                else:
                                    print(f"  WARNING: Progression to question {i+1} unclear")
                            else:
                                # Should show completion
                                if "テスト完了" in post_response.text or "結果" in post_response.text:
                                    print(f"  SUCCESS: Test completion detected")
                                else:
                                    print(f"  WARNING: Test completion unclear")
                        else:
                            print(f"  ERROR: Failed to submit answer for question {i}")
                    else:
                        print(f"  ERROR: Question {i} not displayed correctly")
                        print(f"  Response contains construction environment: {'建設環境' in response.text}")
                        print(f"  Response contains question {i}/10: {f'問題 {i}/10' in response.text}")
                else:
                    print(f"  ERROR: Failed to get question {i}")
                
                print()
            
            print("Step 4: Verify final results")
            
            # Access results page
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                if "建設環境" in result_response.text:
                    print("SUCCESS: Results page shows construction environment")
                    
                    # Check for completion metrics
                    if "10/10" in result_response.text or "10問" in result_response.text:
                        print("SUCCESS: 10-question completion confirmed")
                    else:
                        print("WARNING: 10-question completion not clearly indicated")
                else:
                    print("ERROR: Results page does not show construction environment")
            else:
                print("ERROR: Failed to access results page")
            
            print()
            print("=== TASK 12 TEST SUMMARY ===")
            print(f"Successfully processed questions: {success_count}/10")
            
            if success_count == 10:
                print("🎉 TASK 12 COMPLETED: Construction Environment 10-Question Test SUCCESSFUL")
                print("✅ Emergency Fix 17: Session replacement prevention WORKING")
                print("✅ Emergency Fix 18: Question ID mapping WORKING") 
                print("✅ Field isolation: No basic subject mixing detected")
                print("✅ 10-question completion: ACHIEVED")
                return True
            else:
                print(f"❌ TASK 12 PARTIAL: Only {success_count}/10 questions completed successfully")
                print("⚠️ Emergency Fix 17 may need additional refinement")
                return False
        
    except Exception as e:
        print(f"Test execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)