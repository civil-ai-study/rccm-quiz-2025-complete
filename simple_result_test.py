#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple result page test script
"""

import sys
import os

# Add app directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

def test_result_page():
    """Test the result page functionality"""
    
    print("Testing result page functionality...")
    
    try:
        from app import app
        print("Flask app imported successfully")
    except Exception as e:
        print(f"Flask app import error: {e}")
        return
    
    # Test client
    with app.test_client() as client:
        
        print("\n1. Testing /result direct access...")
        response = client.get('/result')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"Redirect to: {response.location}")
        elif response.status_code == 200:
            print("Result page displayed successfully")
        
        print("\n2. Testing exam flow...")
        
        # Start exam
        response = client.get('/start_exam/基礎科目')
        print(f"start_exam status: {response.status_code}")
        
        # Check session state
        with client.session_transaction() as sess:
            print(f"Session keys: {list(sess.keys())}")
            print(f"exam_question_ids: {len(sess.get('exam_question_ids', []))}")
            print(f"exam_current: {sess.get('exam_current')}")
            print(f"history: {len(sess.get('history', []))}")
        
        # Simulate 10 answers
        print("\n3. Simulating 10 answers...")
        for i in range(10):
            # Get exam page
            response = client.get('/exam')
            if response.status_code == 302:
                print(f"Question {i+1}: Redirected to {response.location}")
                if '/result' in response.location:
                    print(f"SUCCESS: Redirected to result after question {i+1}")
                    break
                continue
            elif response.status_code != 200:
                print(f"Question {i+1}: HTTP error {response.status_code}")
                break
            
            # Submit answer
            response = client.post('/exam', data={'answer': 'A'})
            if response.status_code == 302:
                print(f"Question {i+1}: Answer submitted, redirect to {response.location}")
                if '/result' in response.location:
                    print(f"SUCCESS: Redirected to result after answering question {i+1}")
                    break
            else:
                print(f"Question {i+1}: Answer response status {response.status_code}")
        
        # Final session check
        with client.session_transaction() as sess:
            print(f"\nFinal session state:")
            print(f"exam_current: {sess.get('exam_current')}")
            print(f"history length: {len(sess.get('history', []))}")
            print(f"quiz_completed: {sess.get('quiz_completed')}")
        
        # Test result page again
        print("\n4. Testing /result after simulation...")
        response = client.get('/result')
        print(f"Result page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if '問題結果' in content:
                print("SUCCESS: Result page content found")
            else:
                print("WARNING: Result page content missing")
        elif response.status_code == 302:
            print(f"WARNING: Result page redirects to {response.location}")

if __name__ == '__main__':
    test_result_page()