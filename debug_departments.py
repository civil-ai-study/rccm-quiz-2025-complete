#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct debug script for department configuration issues
"""

import os
import sys

# Add the app directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)
print(f"Looking for config in: {app_dir}")

try:
    # Direct import of config to check department configuration
    from config import RCCMConfig
    
    print("=== Direct Config Import Test ===")
    print(f"RCCMConfig.DEPARTMENTS keys: {list(RCCMConfig.DEPARTMENTS.keys())}")
    print(f"Total departments: {len(RCCMConfig.DEPARTMENTS)}")
    
    # Test specific departments
    test_departments = ['urban', 'garden', 'env', 'steel', 'soil', 'construction', 'water', 'forest', 'agri']
    
    print("\n=== Department Existence Test ===")
    for dept_id in test_departments:
        exists = dept_id in RCCMConfig.DEPARTMENTS
        print(f"{dept_id}: {'EXISTS' if exists else 'MISSING'}")
        if exists:
            dept_info = RCCMConfig.DEPARTMENTS[dept_id]
            print(f"  - Name: {dept_info.get('name', 'MISSING')}")
    
    print("\n=== All Department Details ===")
    for dept_id, dept_info in RCCMConfig.DEPARTMENTS.items():
        print(f"{dept_id}: {dept_info.get('name', 'UNNAMED')}")

except ImportError as e:
    print(f"Import Error: {e}")
    # Try alternative import
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'rccm-quiz-app'))
        from config import RCCMConfig
        
        print("=== Alternative Import Successful ===")
        print(f"RCCMConfig.DEPARTMENTS keys: {list(RCCMConfig.DEPARTMENTS.keys())}")
        
    except ImportError as e2:
        print(f"Alternative Import Error: {e2}")
        
        # Try direct file reading
        config_path = os.path.join('rccm-quiz-app', 'config.py')
        if os.path.exists(config_path):
            print(f"Config file exists: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'DEPARTMENTS = {' in content:
                    print("DEPARTMENTS definition found in config.py")
                    # Count department entries
                    import re
                    dept_entries = re.findall(r"'(\w+)': \{", content)
                    print(f"Department IDs found: {dept_entries}")
                else:
                    print("DEPARTMENTS definition not found in config.py")
        else:
            print(f"Config file not found: {config_path}")

except Exception as e:
    print(f"Unexpected Error: {e}")
    import traceback
    traceback.print_exc()