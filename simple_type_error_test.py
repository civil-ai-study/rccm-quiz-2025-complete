#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple TypeError Fix Verification Test
"""

import requests
import time
import sys

def test_type_error_fix():
    """Test the specific TypeError fix"""
    base_url = "http://localhost:5005"
    
    print("Testing TypeError fix...")
    
    try:
        # Test homepage
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code != 200:
            print(f"Homepage failed: {response.status_code}")
            return False
        print("Homepage OK")
        
        # Test with session
        session = requests.Session()
        
        # Set user
        user_data = {
            'user_name': 'TEST_USER',
            'exam_type': '河川・砂防',
            'exam_year': '2018'
        }
        
        response = session.post(f"{base_url}/set_user", data=user_data, timeout=10)
        if response.status_code not in [200, 302]:
            print(f"Set user failed: {response.status_code}")
            return False
        print("Set user OK")
        
        # Start exam (this is where TypeError occurred)
        start_data = {'num_questions': '10'}
        response = session.post(f"{base_url}/start_exam", data=start_data, timeout=15)
        
        if response.status_code == 500:
            print("500 Error - TypeError still exists")
            print(response.text[:300])
            return False
        elif response.status_code in [200, 302]:
            print("Start exam successful - TypeError fixed!")
            return True
        else:
            print(f"Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("Starting TypeError fix verification...")
    time.sleep(2)  # Wait for server
    
    success = test_type_error_fix()
    
    if success:
        print("SUCCESS: TypeError fix verified!")
        sys.exit(0)
    else:
        print("FAILED: TypeError still exists")
        sys.exit(1)