#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask runtime debug test for department configuration issues
"""

import os
import sys

# Add the app directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

print(f"Looking for app in: {app_dir}")

try:
    # Import config first
    from config import RCCMConfig
    print(f"Config imported successfully")
    print(f"RCCMConfig.DEPARTMENTS keys: {list(RCCMConfig.DEPARTMENTS.keys())}")
    
    # Test the specific failing departments
    test_departments = ['urban', 'garden', 'env']
    
    print("\n=== Testing Department Checks ===")
    for dept_id in test_departments:
        exists_before = dept_id in RCCMConfig.DEPARTMENTS
        print(f"{dept_id} exists BEFORE Flask app: {exists_before}")
    
    # Now import the Flask app
    print("\n=== Importing Flask App ===")
    from app import app
    
    # Import RCCMConfig again to see if it changed
    from config import RCCMConfig as RCCMConfig2
    
    print(f"RCCMConfig after app import - keys: {list(RCCMConfig2.DEPARTMENTS.keys())}")
    
    # Test the departments again
    print("\n=== Testing Department Checks AFTER Flask Import ===")
    for dept_id in test_departments:
        exists_after = dept_id in RCCMConfig2.DEPARTMENTS
        print(f"{dept_id} exists AFTER Flask app: {exists_after}")
        
    # Check if they are the same object
    print(f"\nRCCMConfig objects same? {RCCMConfig is RCCMConfig2}")
    print(f"RCCMConfig.DEPARTMENTS same? {RCCMConfig.DEPARTMENTS is RCCMConfig2.DEPARTMENTS}")
    
    # Test within Flask app context
    print("\n=== Testing within Flask App Context ===")
    with app.app_context():
        # Import again within context
        from config import RCCMConfig as RCCMConfig3
        print(f"RCCMConfig in app context - keys: {list(RCCMConfig3.DEPARTMENTS.keys())}")
        
        for dept_id in test_departments:
            exists_context = dept_id in RCCMConfig3.DEPARTMENTS
            print(f"{dept_id} exists IN APP CONTEXT: {exists_context}")

except ImportError as e:
    print(f"Import Error: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"Unexpected Error: {e}")
    import traceback
    traceback.print_exc()