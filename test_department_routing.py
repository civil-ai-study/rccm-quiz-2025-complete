#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test department routing logic directly
"""

import os
import sys

# Add the app directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

print(f"Testing department routing logic...")

try:
    # Import the necessary functions from app
    from config import RCCMConfig
    
    # Try to import the resolve_department_alias function
    # But first let's create a minimal version to test
    LEGACY_DEPARTMENT_ALIASES = {
        'civil_planning': 'river',
        'river_sabo': 'river',
        'construction_environment': 'env',
        'construction_management': 'construction',
        'water_supply_sewerage': 'water',
        'forest_civil': 'forest',
        'agricultural_civil': 'agri',
        'common': 'basic'
    }
    
    def resolve_department_alias(department):
        """Test version of resolve_department_alias"""
        if department in LEGACY_DEPARTMENT_ALIASES:
            resolved = LEGACY_DEPARTMENT_ALIASES[department]
            print(f"Department alias resolved: {department} -> {resolved}")
            return resolved
        
        # Additional individual aliases
        department_aliases = {
            'shinrin': 'forestry',  # 森林土木のエイリアス
        }
        
        if department in department_aliases:
            print(f"Individual alias resolved: {department} -> {department_aliases[department]}")
            return department_aliases[department]

        return department
    
    # Test the departments that are failing
    test_departments = ['urban', 'garden', 'env', 'steel', 'soil', 'construction', 'water', 'forest', 'agri']
    
    print("\n=== Testing Department Resolution and Validation ===")
    for dept_id in test_departments:
        print(f"\n--- Testing: {dept_id} ---")
        
        # Step 1: Resolve alias
        resolved_dept = resolve_department_alias(dept_id)
        print(f"1. Alias resolution: {dept_id} -> {resolved_dept}")
        
        # Step 2: Check existence in RCCMConfig
        exists_in_config = resolved_dept in RCCMConfig.DEPARTMENTS
        print(f"2. Exists in RCCMConfig.DEPARTMENTS: {exists_in_config}")
        
        if exists_in_config:
            dept_info = RCCMConfig.DEPARTMENTS[resolved_dept]
            print(f"3. Department info found: {dept_info.get('name', 'UNNAMED')}")
        else:
            print(f"3. ERROR: Department not found in config!")
            print(f"   Available departments: {list(RCCMConfig.DEPARTMENTS.keys())}")
            
    print("\n=== Testing Complete DEPARTMENTS List ===")
    print(f"Total departments in config: {len(RCCMConfig.DEPARTMENTS)}")
    for dept_id in sorted(RCCMConfig.DEPARTMENTS.keys()):
        print(f"  - {dept_id}: {RCCMConfig.DEPARTMENTS[dept_id].get('name', 'UNNAMED')}")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()