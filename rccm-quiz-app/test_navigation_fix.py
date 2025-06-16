#!/usr/bin/env python3
"""
Test the navigation bug fixes
"""

import requests
import re
import time

BASE_URL = "http://localhost:5003"

def test_navigation_fix():
    """Test the fixed navigation logic"""
    print("🔍 Testing navigation bug fixes...")
    
    session = requests.Session()
    
    # Step 1: Start a 河川砂防 exam
    print("📚 Starting 河川砂防 specialist exam...")
    response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    
    if response.status_code != 200:
        print(f"❌ Failed to start exam: {response.status_code}")
        return False
    
    # Extract question ID from form
    qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
    if not qid_match:
        print("❌ Could not find question ID")
        return False
    
    qid = qid_match.group(1)
    print(f"✅ Question 1 loaded (ID: {qid})")
    
    # Check question counter in the page
    counter_match = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', response.text)
    if counter_match:
        current, total = counter_match.groups()
        print(f"✅ Question counter: {current}/{total}")
        if current != "1":
            print(f"⚠️ Expected question 1, got {current}")
    
    # Step 2: Submit answer for question 1
    print("📝 Submitting answer for question 1...")
    answer_data = {
        'qid': qid,
        'answer': 'A',
        'elapsed': '5'
    }
    
    submit_response = session.post(f"{BASE_URL}/exam", data=answer_data)
    if submit_response.status_code != 200:
        print(f"❌ Answer submission failed: {submit_response.status_code}")
        return False
    
    # Check the feedback page for correct navigation
    feedback_content = submit_response.text
    print("✅ Answer submitted, checking feedback page...")
    
    # Look for question counter in feedback
    feedback_counter_match = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', feedback_content)
    if feedback_counter_match:
        fb_current, fb_total = feedback_counter_match.groups()
        print(f"✅ Feedback counter: {fb_current}/{fb_total}")
        if fb_current != "1":
            print(f"⚠️ Expected feedback for question 1, got {fb_current}")
    
    # Check for navigation button
    if "次の問題へ" in feedback_content:
        print("✅ '次の問題へ' button found - navigation fix successful!")
    elif "結果を見る" in feedback_content:
        print("❌ '結果を見る' button found - navigation still broken!")
        return False
    else:
        print("❌ No navigation button found")
        return False
    
    # Check that difficulty message is removed
    if "難易度が自動調整されました" in feedback_content:
        print("❌ Difficulty adjustment message still present")
        return False
    else:
        print("✅ Difficulty adjustment message removed")
    
    # Step 3: Navigate to question 2
    print("➡️ Navigating to question 2...")
    next_url_match = re.search(r'href="(/exam[^"]*)"[^>]*>.*?次の問題へ', feedback_content, re.DOTALL)
    if not next_url_match:
        print("❌ Could not find next question URL")
        return False
    
    next_url = next_url_match.group(1)
    print(f"✅ Found next URL: {next_url}")
    
    response2 = session.get(f"{BASE_URL}{next_url}")
    if response2.status_code != 200:
        print(f"❌ Failed to navigate to question 2: {response2.status_code}")
        return False
    
    # Check question 2 counter
    counter_match2 = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', response2.text)
    if counter_match2:
        current2, total2 = counter_match2.groups()
        print(f"✅ Question 2 counter: {current2}/{total2}")
        if current2 != "2":
            print(f"❌ Expected question 2, got {current2}")
            return False
        if int(total2) < 2:
            print(f"❌ Total questions should be >= 2, got {total2}")
            return False
    else:
        print("❌ Could not find question counter on question 2")
        return False
    
    # Step 4: Submit answer for question 2 and verify it doesn't say "result"
    qid2_match = re.search(r'name="qid" value="([^"]+)"', response2.text)
    if not qid2_match:
        print("❌ Could not find question 2 ID")
        return False
    
    qid2 = qid2_match.group(1)
    print(f"✅ Question 2 loaded (ID: {qid2})")
    
    print("📝 Submitting answer for question 2...")
    answer_data2 = {
        'qid': qid2,
        'answer': 'B',
        'elapsed': '4'
    }
    
    submit_response2 = session.post(f"{BASE_URL}/exam", data=answer_data2)
    if submit_response2.status_code != 200:
        print(f"❌ Answer 2 submission failed: {submit_response2.status_code}")
        return False
    
    feedback_content2 = submit_response2.text
    
    # Check the critical issue: question 2 should NOT show "結果を見る"
    if "結果を見る" in feedback_content2 and "次の問題へ" not in feedback_content2:
        print("❌ CRITICAL BUG STILL EXISTS: Question 2 shows '結果を見る' instead of '次の問題へ'!")
        return False
    elif "次の問題へ" in feedback_content2:
        print("✅ CRITICAL BUG FIXED: Question 2 correctly shows '次の問題へ'!")
    
    # Check question counter in feedback for question 2
    feedback_counter_match2 = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', feedback_content2)
    if feedback_counter_match2:
        fb_current2, fb_total2 = feedback_counter_match2.groups()
        print(f"✅ Question 2 feedback counter: {fb_current2}/{fb_total2}")
        if fb_current2 == "10" and fb_total2 == "10":
            print("❌ COUNTER BUG STILL EXISTS: Shows 10/10 instead of 2/X!")
            return False
        elif fb_current2 == "2":
            print("✅ COUNTER BUG FIXED: Correctly shows question 2!")
    
    return True

def main():
    print("=" * 60)
    print("NAVIGATION BUG FIX TEST")
    print("=" * 60)
    
    # Wait a moment for the server to be ready
    time.sleep(2)
    
    try:
        success = test_navigation_fix()
        print("\n" + "=" * 60)
        if success:
            print("🎉 ALL NAVIGATION FIXES SUCCESSFUL!")
            print("✅ Bug fixed: Question 2 navigation")
            print("✅ Bug fixed: Difficulty message removed") 
            print("✅ Bug fixed: Question counter")
        else:
            print("🚨 SOME FIXES FAILED!")
            print("❌ Navigation issues still exist")
        print("=" * 60)
        return success
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)