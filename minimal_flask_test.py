#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Flask test to isolate the department validation issue
"""

import os
import sys

# Add the app directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

from flask import Flask, render_template_string

# Import the config
from config import RCCMConfig

# Create minimal Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

print(f"Flask app created. Testing departments...")

# Test the failing departments directly
@app.route('/test/<department_id>')
def test_department(department_id):
    try:
        # Exact same logic as in the production app
        print(f"=== Testing department: {department_id} ===")
        
        # Step 1: Check if department exists in config
        print(f"1. Checking existence in RCCMConfig.DEPARTMENTS...")
        print(f"   Available departments: {list(RCCMConfig.DEPARTMENTS.keys())}")
        
        exists = department_id in RCCMConfig.DEPARTMENTS
        print(f"   Department '{department_id}' exists: {exists}")
        
        if not exists:
            print(f"   ERROR: Department not found!")
            return f"ERROR: Department '{department_id}' not found in RCCMConfig.DEPARTMENTS"
        
        # Step 2: Get department info
        dept_info = RCCMConfig.DEPARTMENTS[department_id]
        dept_name = dept_info.get('name', 'UNNAMED')
        print(f"2. Department info retrieved: {dept_name}")
        
        return f"SUCCESS: Department '{department_id}' found with name '{dept_name}'"
        
    except Exception as e:
        print(f"EXCEPTION in test_department: {e}")
        import traceback
        traceback.print_exc()
        return f"EXCEPTION: {str(e)}"

if __name__ == '__main__':
    # Test the failing departments
    test_departments = ['urban', 'garden', 'env', 'steel', 'soil']
    
    with app.test_client() as client:
        print("\n=== Testing departments with Flask test client ===")
        
        for dept_id in test_departments:
            print(f"\n--- Testing: {dept_id} ---")
            
            try:
                response = client.get(f'/test/{dept_id}')
                print(f"HTTP Status: {response.status_code}")
                print(f"Response: {response.data.decode('utf-8')}")
                
            except Exception as e:
                print(f"Test client error: {e}")
                import traceback
                traceback.print_exc()