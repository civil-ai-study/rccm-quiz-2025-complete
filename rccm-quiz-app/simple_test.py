#!/usr/bin/env python3
"""
Simple debug test for review functionality
"""

import requests

BASE_URL = "http://localhost:5003"

def main():
    print("🔍 Simple review functionality debug test")
    
    session = requests.Session()
    
    # Step 1: Create test data
    print("\n1. Creating review test data...")
    response = session.get(f"{BASE_URL}/debug/create_review_data")
    print(f"Status: {response.status_code}")
    if "復習テストデータ作成完了" in response.text:
        print("✅ Test data created")
    else:
        print("❌ Test data creation failed")
        return
    
    # Step 2: Check review list
    print("\n2. Checking review list...")
    response = session.get(f"{BASE_URL}/review")
    print(f"Status: {response.status_code}")
    if "復習開始" in response.text:
        print("✅ Review start button found in list")
    else:
        print("❌ Review start button not found")
    
    # Step 3: Try review start with detailed logging
    print("\n3. Testing review start with detailed tracking...")
    response = session.get(f"{BASE_URL}/exam/review", allow_redirects=False)
    print(f"Initial response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"Redirect location: {location}")
        
        # Follow the redirect manually
        print("\n4. Following redirect manually...")
        redirect_response = session.get(f"{BASE_URL}{location}")
        print(f"Redirect response status: {redirect_response.status_code}")
        
        if "エラーが発生しました" in redirect_response.text:
            print("❌ ERROR PAGE DETECTED")
            # Extract error message
            import re
            error_match = re.search(r'<p class="mb-0"><strong>(.*?)</strong></p>', redirect_response.text)
            if error_match:
                print(f"Error message: {error_match.group(1)}")
        elif "問題" in redirect_response.text and "選択肢" in redirect_response.text:
            print("✅ QUESTION PAGE DETECTED")
            # Extract question counter
            counter_match = re.search(r'>(\d+)/(\d+)<', redirect_response.text)
            if counter_match:
                current, total = counter_match.groups()
                print(f"Question counter: {current}/{total}")
        else:
            print("❓ UNKNOWN PAGE TYPE")
            print(f"Content preview: {redirect_response.text[:200]}")
    
    elif response.status_code == 200:
        print("Direct 200 response (no redirect)")
        if "エラーが発生しました" in response.text:
            print("❌ ERROR PAGE")
        elif "問題" in response.text:
            print("✅ QUESTION PAGE")
        else:
            print("❓ UNKNOWN PAGE")
    
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

if __name__ == "__main__":
    main()