#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corrected Session Progression Test
Purpose: Test session progression using the correct /exam route with department parameter
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def corrected_session_progression_test():
    """Corrected Session Progression Test using /exam route"""
    print("=== Corrected Session Progression Test ===")
    
    with app.test_client() as client:
        # Step 1: Start road department session using correct route
        print("\n1. Road Department Session Start Test")
        # The correct way based on the routing - use /exam with department parameter
        response = client.get('/exam?department=road&count=10')
        
        if response.status_code != 200:
            print(f"ERROR: Session start failed: status={response.status_code}")
            return False
        
        # Check if 1st question page
        html = response.get_data(as_text=True)
        if '1/10' in html:
            print("SUCCESS: Question 1/10 display confirmed")
        else:
            print("ERROR: Question 1/10 display failed")
            print("Response content (first 200 chars):", html[:200])
            return False
        
        # Extract question ID for 1st question
        qid_match = re.search(r'name="qid"\s+value="([^"]+)"', html)
        if not qid_match:
            print("ERROR: Question ID extraction failed")
            return False
        
        qid1 = qid_match.group(1)
        print(f"SUCCESS: Question 1 ID: {qid1}")
        
        # Step 2: Submit answer for 1st question
        print("\n2. Question 1 Answer Submission Test")
        answer_data = {
            'qid': qid1,
            'answer': 'A',
            'elapsed': '30.5'
        }
        
        post_response = client.post('/exam', data=answer_data)
        
        if post_response.status_code != 200:
            print(f"ERROR: Question 1 answer submission failed: status={post_response.status_code}")
            return False
        
        post_html = post_response.get_data(as_text=True)
        
        # Check for "Next Question (2/10)" button in feedback
        if '2/10' in post_html:
            print("SUCCESS: Question 1 answer processed, 2/10 progress confirmed")
        else:
            print("ERROR: Question 1 answer processing failed, 2/10 progress not found")
            print("Feedback content (first 300 chars):", post_html[:300])
            return False
        
        # Step 3: Navigate to 2nd question - use GET /exam directly
        print("\n3. Question 2 Navigation Test")
        
        # After POST, the next question should be available via GET /exam
        response2 = client.get('/exam')
        
        if response2.status_code != 200:
            print(f"ERROR: Question 2 access failed: status={response2.status_code}")
            return False
        
        html2 = response2.get_data(as_text=True)
        
        # Check 2nd question progress
        if '2/10' in html2:
            print("SUCCESS: Question 2/10 display confirmed")
        else:
            print("ERROR: Question 2/10 display failed")
            print("Question 2 content (first 200 chars):", html2[:200])
            return False
        
        # Extract question ID for 2nd question
        qid2_match = re.search(r'name="qid"\s+value="([^"]+)"', html2)
        if not qid2_match:
            print("ERROR: Question 2 ID extraction failed")
            return False
        
        qid2 = qid2_match.group(1)
        print(f"SUCCESS: Question 2 ID: {qid2}")
        
        # Step 4: Submit answer for 2nd question
        print("\n4. Question 2 Answer Submission Test")
        answer_data2 = {
            'qid': qid2,
            'answer': 'B',
            'elapsed': '25.0'
        }
        
        post_response2 = client.post('/exam', data=answer_data2)
        
        if post_response2.status_code != 200:
            print(f"ERROR: Question 2 answer submission failed: status={post_response2.status_code}")
            return False
        
        post_html2 = post_response2.get_data(as_text=True)
        
        # Check for 3rd question progress
        if '3/10' in post_html2:
            print("SUCCESS: Question 2 answer processed, 3/10 progress confirmed")
        else:
            print("ERROR: Question 2 answer processing failed, 3/10 progress not found")
            print("Question 2 feedback content (first 300 chars):", post_html2[:300])
            return False
        
        # Step 5: Navigate to 3rd question
        print("\n5. Question 3 Navigation Test")
        
        response3 = client.get('/exam')
        
        if response3.status_code != 200:
            print(f"ERROR: Question 3 access failed: status={response3.status_code}")
            return False
        
        html3 = response3.get_data(as_text=True)
        
        if '3/10' in html3:
            print("SUCCESS: Question 3/10 display confirmed")
            print("CELEBRATION: Session continuation system working correctly!")
            
            # Check for field mixing (should be road department)
            # Look for Japanese character for road department
            if 'road' in html3.lower() or any(char in html3 for char in ['道路', '路面', '車道', '歩道']):
                print("SUCCESS: Field verification - Road department questions correctly displayed")
            else:
                print("WARNING: Field verification incomplete - Road department indicators not clearly found")
            
            return True
        else:
            print("ERROR: Question 3/10 display failed")
            print("Question 3 content (first 200 chars):", html3[:200])
            return False

if __name__ == "__main__":
    success = corrected_session_progression_test()
    if success:
        print("\nTARGET ACHIEVED: [Session Continuation System Root Fix] Task Completed")
        print("SUCCESS: exam_current increment working normally")
        print("SUCCESS: Progress display updating correctly 1/10->2/10->3/10")
        print("SUCCESS: Ready to proceed to next task (Road Department 10-Question Complete Test)")
    else:
        print("\nERROR: Session continuation system has problems")
        print("Detailed investigation and fixes required")