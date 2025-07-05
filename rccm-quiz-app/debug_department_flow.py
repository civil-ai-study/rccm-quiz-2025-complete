#!/usr/bin/env python3
"""
Debug script for investigating soil_foundation and urban_planning department flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_questions_improved
from config import RCCMConfig

# Test the department mapping
print("=== DEPARTMENT MAPPING TEST ===")
from app import DEPARTMENT_TO_CATEGORY_MAPPING, LEGACY_DEPARTMENT_ALIASES, resolve_department_alias

print(f"DEPARTMENT_TO_CATEGORY_MAPPING:")
for dept, cat in DEPARTMENT_TO_CATEGORY_MAPPING.items():
    print(f"  {dept} -> {cat}")

print(f"\nLEGACY_DEPARTMENT_ALIASES:")
for alias, dept in LEGACY_DEPARTMENT_ALIASES.items():
    print(f"  {alias} -> {dept}")

print(f"\nTest resolve_department_alias:")
test_departments = ['soil_foundation', 'urban_planning', 'soil', 'urban']
for dept in test_departments:
    resolved = resolve_department_alias(dept)
    print(f"  {dept} -> {resolved}")

# Test department existence in config
print(f"\n=== CONFIG DEPARTMENTS ===")
print(f"Available departments in RCCMConfig.DEPARTMENTS:")
for dept_id, dept_info in RCCMConfig.DEPARTMENTS.items():
    print(f"  {dept_id}: {dept_info['name']}")

# Test data loading
print(f"\n=== DATA LOADING TEST ===")
try:
    questions = load_questions_improved()
    print(f"Total questions loaded: {len(questions)}")
    
    # Check question types
    question_types = {}
    for q in questions:
        qtype = q.get('question_type', 'unknown')
        if qtype not in question_types:
            question_types[qtype] = 0
        question_types[qtype] += 1
    
    print(f"Question types:")
    for qtype, count in question_types.items():
        print(f"  {qtype}: {count}")
    
    # Check categories for specialist questions
    specialist_categories = {}
    for q in questions:
        if q.get('question_type') == 'specialist':
            cat = q.get('category', 'unknown')
            if cat not in specialist_categories:
                specialist_categories[cat] = 0
            specialist_categories[cat] += 1
    
    print(f"\nSpecialist question categories:")
    for cat, count in specialist_categories.items():
        print(f"  {cat}: {count}")
    
    # Test specific departments
    target_departments = ['土質及び基礎', '都市計画及び地方計画']
    for target_cat in target_departments:
        dept_questions = [q for q in questions if q.get('category') == target_cat and q.get('question_type') == 'specialist']
        print(f"\n{target_cat} specialist questions: {len(dept_questions)}")
        if dept_questions:
            print(f"  Sample question ID: {dept_questions[0].get('id')}")
            print(f"  Sample question year: {dept_questions[0].get('year')}")
            print(f"  Sample question type: {dept_questions[0].get('question_type')}")
    
except Exception as e:
    print(f"Error loading questions: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== DEPARTMENT FLOW TEST ===")
# Test the app logic for these departments
from app import get_department_category, normalize_department_name

test_flow = [
    ('soil_foundation', 'soil_foundation'),
    ('urban_planning', 'urban_planning'),
    ('soil', 'soil_foundation'),
    ('urban', 'urban_planning')
]

for input_dept, expected_dept in test_flow:
    print(f"\nTesting department: {input_dept}")
    
    # Step 1: Resolve alias
    resolved = resolve_department_alias(input_dept)
    print(f"  1. Alias resolution: {input_dept} -> {resolved}")
    
    # Step 2: Normalize
    normalized = normalize_department_name(resolved)
    print(f"  2. Normalization: {resolved} -> {normalized}")
    
    # Step 3: Get category
    category = get_department_category(normalized)
    print(f"  3. Category mapping: {normalized} -> {category}")
    
    # Step 4: Check if in RCCMConfig
    in_config = resolved in RCCMConfig.DEPARTMENTS
    print(f"  4. In RCCMConfig: {in_config}")
    
    if in_config:
        print(f"     Config name: {RCCMConfig.DEPARTMENTS[resolved]['name']}")