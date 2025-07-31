#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the fixed result display issue
"""

import sys
import os

# Add app directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

def test_fixed_result_display():
    """Test that result page now displays even with empty history"""
    
    print("Testing fixed result display functionality...")
    
    try:
        from app import app
        print("Flask app imported successfully")
    except Exception as e:
        print(f"Flask app import error: {e}")
        return
    
    with app.test_client() as client:
        
        print("\n1. Testing /result with empty session...")
        response = client.get('/result')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if '問題結果' in content:
                print("SUCCESS: Result page now displays with empty session")
                if 'debug_message' in content:
                    print("SUCCESS: Debug information is shown to help diagnosis")
                return True
            else:
                print("WARNING: Result page displayed but content may be incomplete")
        elif response.status_code == 302:
            print(f"Still redirecting to: {response.location}")
        else:
            print(f"Unexpected response: {response.status_code}")
        
        return False

if __name__ == '__main__':
    success = test_fixed_result_display()
    if success:
        print("\n✓ FIX VERIFIED: Result page now displays properly")
        print("Users will see a result page with debug information instead of being redirected")
    else:
        print("\n× Fix needs further investigation")