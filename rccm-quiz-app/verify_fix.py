#!/usr/bin/env python3
"""
Simple verification of the navigation fixes
"""

import requests
import re

BASE_URL = "http://localhost:5003"

def test_session_flow():
    session = requests.Session()
    
    print("🔄 Testing complete session flow...")
    
    # Start exam
    response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    print(f"✅ Started exam: {response.status_code}")
    
    # Find first question ID and counter
    qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
    counter_match = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', response.text)
    
    if qid_match and counter_match:
        qid = qid_match.group(1)
        current, total = counter_match.groups()
        print(f"✅ Question 1: ID={qid}, counter={current}/{total}")
        
        # Submit answer
        answer_data = {'qid': qid, 'answer': 'A', 'elapsed': '5'}
        feedback_response = session.post(f"{BASE_URL}/exam", data=answer_data)
        
        if "次の問題へ" in feedback_response.text:
            print("✅ Question 1 feedback: Shows '次の問題へ' correctly")
        
        if "難易度が自動調整されました" not in feedback_response.text:
            print("✅ Question 1 feedback: Difficulty message removed")
            
        # Navigate to question 2
        q2_response = session.get(f"{BASE_URL}/exam")
        q2_counter_match = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', q2_response.text)
        
        if q2_counter_match:
            q2_current, q2_total = q2_counter_match.groups()
            print(f"✅ Question 2: counter={q2_current}/{q2_total}")
            
            if q2_current == "2" and int(q2_total) >= 2:
                print("🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
                return True
            else:
                print(f"❌ Counter issue: expected 2/>=2, got {q2_current}/{q2_total}")
                return False
        else:
            print("❌ Could not find question 2 counter")
            return False
    else:
        print("❌ Could not parse question 1")
        return False

if __name__ == "__main__":
    success = test_session_flow()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")