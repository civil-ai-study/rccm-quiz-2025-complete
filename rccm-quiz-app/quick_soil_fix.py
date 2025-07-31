#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Quick soil foundation fix test")
    
    # 1. Test normalize function
    os.environ['TESTING'] = 'true'
    
    from app import normalize_department_name, DEPARTMENT_TO_CATEGORY_MAPPING, LEGACY_DEPARTMENT_ALIASES
    
    dept_name = '土質・基礎'
    print(f"Testing department: {dept_name}")
    
    # Check if in mapping directly
    print(f"In DEPARTMENT_TO_CATEGORY_MAPPING: {dept_name in DEPARTMENT_TO_CATEGORY_MAPPING}")
    if dept_name in DEPARTMENT_TO_CATEGORY_MAPPING:
        print(f"Maps to: {DEPARTMENT_TO_CATEGORY_MAPPING[dept_name]}")
    
    # Check normalize function
    normalized = normalize_department_name(dept_name)
    print(f"Normalized: {normalized}")
    
    if normalized:
        category = DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized)
        print(f"Category: {category}")
    else:
        print("Normalization failed!")
        
        # Check what's in the mappings
        print("Available departments:")
        for key in DEPARTMENT_TO_CATEGORY_MAPPING.keys():
            if '土質' in key or '基礎' in key:
                print(f"  {key}")
                
        print("Aliases:")
        for key, value in LEGACY_DEPARTMENT_ALIASES.items():
            if '土質' in key or '基礎' in key or '土質' in value or '基礎' in value:
                print(f"  {key} -> {value}")
    
    # Test actual function call
    from app import get_mixed_questions, load_questions
    
    print("\nTesting get_mixed_questions...")
    questions = load_questions()
    print(f"Total questions: {len(questions)}")
    
    # Create dummy user session
    user_session = {}
    
    try:
        result = get_mixed_questions(user_session, questions, 
                                   requested_category='', 
                                   session_size=10, 
                                   department='土質・基礎', 
                                   question_type='specialist',
                                   year=None)
        print(f"get_mixed_questions result: {len(result)} questions")
        if len(result) == 0:
            print("PROBLEM: get_mixed_questions returned empty list!")
        else:
            print("SUCCESS: Questions found")
    except Exception as e:
        print(f"ERROR in get_mixed_questions: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"Quick test failed: {e}")
    import traceback
    traceback.print_exc()