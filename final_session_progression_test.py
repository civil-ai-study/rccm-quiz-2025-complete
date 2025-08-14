#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Session Progression Test with CSRF Token Support
Purpose: Test session progression with proper CSRF token handling
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def extract_csrf_token(html):
    """Extract CSRF token from HTML"""
    csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if csrf_match:
        return csrf_match.group(1)
    
    # Alternative pattern
    csrf_match = re.search(r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\'][^>]*>', html)
    if csrf_match:
        return csrf_match.group(1)
    
    return None

def final_session_progression_test():
    """Final Session Progression Test with CSRF support"""
    print("=== Final Session Progression Test with CSRF ===")
    
    with app.test_client() as client:
        # Step 1: Start road department session using correct route
        print("\n1. Road Department Session Start Test")
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
            # Show ASCII-safe portion only
            safe_content = ''.join(c for c in html[:200] if ord(c) < 128)
            print("Response content (first 200 ASCII chars):", safe_content)
            return False
        
        # Extract question ID for 1st question
        qid_match = re.search(r'name="qid"\s+value="([^"]+)"', html)
        if not qid_match:
            print("ERROR: Question ID extraction failed")
            return False
        
        qid1 = qid_match.group(1)
        print(f"SUCCESS: Question 1 ID: {qid1}")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(html)
        if csrf_token:
            print(f"SUCCESS: CSRF token extracted: {csrf_token[:20]}...")
        else:
            print("WARNING: CSRF token not found, proceeding without it")
        
        # Step 2: Submit answer for 1st question
        print("\n2. Question 1 Answer Submission Test")
        answer_data = {
            'qid': qid1,
            'answer': 'A',
            'elapsed': '30.5'
        }
        
        # Add CSRF token if available
        if csrf_token:
            answer_data['csrf_token'] = csrf_token
        
        post_response = client.post('/exam', data=answer_data)
        
        if post_response.status_code != 200:
            print(f"ERROR: Question 1 answer submission failed: status={post_response.status_code}")
            # Try to get error details
            error_html = post_response.get_data(as_text=True)
            safe_error = ''.join(c for c in error_html[:300] if ord(c) < 128)
            print("Error response:", safe_error)
            return False
        
        post_html = post_response.get_data(as_text=True)
        
        # Check for "Next Question (2/10)" button in feedback
        if '2/10' in post_html:
            print("SUCCESS: Question 1 answer processed, 2/10 progress confirmed")
        else:
            print("ERROR: Question 1 answer processing failed, 2/10 progress not found")
            safe_feedback = ''.join(c for c in post_html[:300] if ord(c) < 128)
            print("Feedback content:", safe_feedback)
            return False
        
        # Step 3: Navigate to 2nd question - use GET /exam directly
        print("\n3. Question 2 Navigation Test")
        
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
            safe_content2 = ''.join(c for c in html2[:200] if ord(c) < 128)
            print("Question 2 content:", safe_content2)
            return False
        
        # Extract question ID for 2nd question
        qid2_match = re.search(r'name="qid"\s+value="([^"]+)"', html2)
        if not qid2_match:
            print("ERROR: Question 2 ID extraction failed")
            return False
        
        qid2 = qid2_match.group(1)
        print(f"SUCCESS: Question 2 ID: {qid2}")
        
        # Extract CSRF token for 2nd question
        csrf_token2 = extract_csrf_token(html2)
        
        # Step 4: Submit answer for 2nd question
        print("\n4. Question 2 Answer Submission Test")
        answer_data2 = {
            'qid': qid2,
            'answer': 'B',
            'elapsed': '25.0'
        }
        
        if csrf_token2:
            answer_data2['csrf_token'] = csrf_token2
        
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
            safe_feedback2 = ''.join(c for c in post_html2[:300] if ord(c) < 128)
            print("Question 2 feedback content:", safe_feedback2)
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
            if any(char in html3 for char in ['road', 'doro', '道路', '路面', '車道', '歩道']):
                print("SUCCESS: Field verification - Road department questions correctly displayed")
            else:
                print("WARNING: Field verification incomplete - Road department indicators not clearly found")
            
            return True
        else:
            print("ERROR: Question 3/10 display failed")
            safe_content3 = ''.join(c for c in html3[:200] if ord(c) < 128)
            print("Question 3 content:", safe_content3)
            return False

if __name__ == "__main__":
    success = final_session_progression_test()
    if success:
        print("\nTARGET ACHIEVED: [Session Continuation System Root Fix] Task Completed")
        print("SUCCESS: exam_current increment working normally")
        print("SUCCESS: Progress display updating correctly 1/10->2/10->3/10")
        print("SUCCESS: Ready to proceed to next task (Road Department 10-Question Complete Test)")
    else:
        print("\nERROR: Session continuation system has problems")
        print("Detailed investigation and fixes required")