#!/usr/bin/env python3
"""
Test get_mixed_questions function directly to identify the issue
"""

import os
import sys
import csv
import json

# Add the app directory to path
sys.path.append(r'C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app')

def test_department_mapping():
    """Test the department mapping and question selection"""
    print("=== Test get_mixed_questions function ===")
    
    data_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\data"
    
    # Test 1: Check what categories exist in 2016 file
    print("\n1. Check 2016 CSV file categories:")
    csv_file = os.path.join(data_dir, "4-2_2016.csv")
    
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            categories = set()
            for row in reader:
                category = row.get('category', '').strip()
                if category:
                    categories.add(category)
        
        print("  Available categories:")
        for i, cat in enumerate(sorted(categories), 1):
            print(f"    {i}. '{cat}'")
    
    # Test 2: Try to load questions using the utils function
    print("\n2. Test load_specialist_questions_only function:")
    
    try:
        # Import the function from utils
        from utils import load_specialist_questions_only
        
        # Find the actual landscape category name from CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            landscape_category = None
            for row in reader:
                category = row.get('category', '').strip()
                if '園' in category:
                    landscape_category = category
                    break
        
        if landscape_category:
            print(f"  Testing with category: '{landscape_category}'")
            
            questions = load_specialist_questions_only(landscape_category, 2016, data_dir)
            print(f"  Result: {len(questions)} questions loaded")
            
            if questions:
                print("  Sample question:")
                sample = questions[0]
                for key in ['id', 'category', 'year', 'question_type']:
                    print(f"    {key}: {sample.get(key, 'N/A')}")
            
        else:
            print("  Error: Landscape category not found")
            
    except ImportError as e:
        print(f"  Error importing utils: {e}")
    except Exception as e:
        print(f"  Error testing load function: {e}")
    
    # Test 3: Check DEPARTMENT_TO_CATEGORY_MAPPING
    print("\n3. Test department mapping:")
    
    try:
        # Import necessary functions from app
        from app import DEPARTMENT_TO_CATEGORY_MAPPING, normalize_department_name, get_department_category
        
        # Test different landscape department variations
        test_departments = ['landscape', '造園', 'zouen', 'garden']
        
        print("  Testing department name variations:")
        for dept in test_departments:
            print(f"    Input: '{dept}'")
            try:
                normalized = normalize_department_name(dept)
                print(f"      Normalized: '{normalized}'")
                category = get_department_category(normalized) if normalized else None
                print(f"      Category: '{category}'")
            except Exception as e:
                print(f"      Error: {e}")
        
        print(f"\n  Available mappings in DEPARTMENT_TO_CATEGORY_MAPPING:")
        try:
            for key, value in DEPARTMENT_TO_CATEGORY_MAPPING.items():
                print(f"    '{key}' -> '{value}'")
        except Exception as e:
            print(f"    Error displaying mappings: {e}")
            
    except ImportError as e:
        print(f"  Error importing from app: {e}")
    except Exception as e:
        print(f"  Error testing mappings: {e}")
    
    # Test 4: Simulate get_mixed_questions call
    print("\n4. Test get_mixed_questions simulation:")
    
    try:
        from app import get_mixed_questions
        
        # Create a mock session
        mock_session = {'history': []}
        
        # Load all questions first
        all_questions = []
        csv_files = ['4-2_2016.csv']
        
        for csv_file_name in csv_files:
            filepath = os.path.join(data_dir, csv_file_name)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        question = dict(row)
                        question['question_type'] = 'specialist'
                        all_questions.append(question)
        
        print(f"  Loaded {len(all_questions)} total questions")
        
        # Test with landscape department
        print(f"  Testing get_mixed_questions with landscape department...")
        
        # Find the actual landscape department name
        landscape_dept = None
        for q in all_questions:
            if '園' in q.get('category', ''):
                landscape_dept = q.get('category')
                break
        
        if landscape_dept:
            print(f"  Using department: '{landscape_dept}'")
            
            # Test direct call with the actual category name
            result = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='全体',
                session_size=5,
                department=landscape_dept,  # Use the actual category name
                question_type='specialist',
                year=2016
            )
            
            print(f"  Result: {len(result)} questions selected")
            
            if result:
                print("  Sample selected question:")
                sample = result[0]
                for key in ['id', 'category', 'year', 'question_type']:
                    print(f"    {key}: {sample.get(key, 'N/A')}")
            else:
                print("  No questions selected!")
        
    except Exception as e:
        print(f"  Error testing get_mixed_questions: {e}")

if __name__ == "__main__":
    test_department_mapping()