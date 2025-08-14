#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Loading Diagnosis - Emergency Fix for "No Data" Problem
Purpose: Diagnose and fix the data loading issue causing field mixing
Problem: "無データ" in logs indicates files are not being loaded properly
Solution: Diagnose and fix file validation and loading process
"""

import sys
import os
import csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def diagnose_data_files():
    """Diagnose data file accessibility and content"""
    print("=== DATA LOADING DIAGNOSIS ===")
    print("Purpose: Diagnose data loading failure causing field mixing")
    print()
    
    data_dir = os.path.join('rccm-quiz-app', 'data')
    print(f"Data directory: {data_dir}")
    print(f"Directory exists: {os.path.exists(data_dir)}")
    print()
    
    # Check critical files
    critical_files = ['4-1.csv', '4-2_2019.csv']
    
    for filename in critical_files:
        filepath = os.path.join(data_dir, filename)
        print(f"=== {filename} ===")
        print(f"  Exists: {os.path.exists(filepath)}")
        
        if os.path.exists(filepath):
            print(f"  Size: {os.path.getsize(filepath)} bytes")
            
            # Try to read file content
            try:
                with open(filepath, 'r', encoding='shift_jis') as f:
                    lines = f.readlines()
                    print(f"  Lines: {len(lines)}")
                    print(f"  Header: {lines[0].strip() if lines else 'No header'}")
                    
                    # Analyze categories for specialist files
                    if '4-2' in filename:
                        categories = set()
                        if len(lines) > 1:
                            reader = csv.DictReader(lines, delimiter=',')
                            for row in reader:
                                if 'category' in row:
                                    categories.add(row['category'])
                        print(f"  Categories: {sorted(categories)}")
                        print(f"  Category count: {len(categories)}")
                        
                        # Check for specific categories
                        river_questions = sum(1 for line in lines if '河川' in line or '砂防' in line or '海岸' in line)
                        road_questions = sum(1 for line in lines if '道路' in line)
                        print(f"  River-related questions: {river_questions}")
                        print(f"  Road-related questions: {road_questions}")
                        
            except Exception as e:
                print(f"  Read error: {str(e)}")
        print()

def test_validation_function():
    """Test the file validation function causing issues"""
    print("=== FILE VALIDATION FUNCTION TEST ===")
    print()
    
    try:
        from utils import validate_file_path
        
        test_paths = [
            'rccm-quiz-app/data/4-1.csv',
            'rccm-quiz-app/data/4-2_2019.csv',
            os.path.join('rccm-quiz-app', 'data', '4-1.csv'),
        ]
        
        for path in test_paths:
            print(f"Testing path: {path}")
            try:
                validated = validate_file_path(path)
                print(f"  Validated: {validated}")
                print(f"  Exists after validation: {os.path.exists(validated)}")
            except Exception as e:
                print(f"  Validation error: {str(e)}")
            print()
            
    except Exception as e:
        print(f"Import error: {str(e)}")

def test_load_questions_function():
    """Test the load_questions_improved function"""
    print("=== LOAD_QUESTIONS FUNCTION TEST ===")
    print()
    
    try:
        from utils import load_questions_improved
        
        test_file = os.path.join('rccm-quiz-app', 'data', '4-2_2019.csv')
        print(f"Testing file: {test_file}")
        print(f"File exists: {os.path.exists(test_file)}")
        
        if os.path.exists(test_file):
            try:
                questions = load_questions_improved(test_file)
                print(f"Questions loaded: {len(questions)}")
                
                if questions:
                    sample = questions[0]
                    print(f"Sample question keys: {list(sample.keys())}")
                    print(f"Sample category: {sample.get('category', 'No category')}")
                    
                    # Count by category
                    categories = {}
                    for q in questions:
                        cat = q.get('category', 'Unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    print(f"Category distribution: {categories}")
                    
            except Exception as e:
                print(f"Load error: {str(e)}")
        
    except Exception as e:
        print(f"Import error: {str(e)}")

def test_complete_data_loading():
    """Test the complete data loading process"""
    print("=== COMPLETE DATA LOADING TEST ===")
    print()
    
    try:
        from utils import load_all_questions
        
        print("Testing load_all_questions function...")
        try:
            all_questions = load_all_questions()
            print(f"Total questions loaded: {len(all_questions)}")
            
            if all_questions:
                # Analyze by question type
                types = {}
                for q in all_questions:
                    qtype = q.get('question_type', 'Unknown')
                    types[qtype] = types.get(qtype, 0) + 1
                
                print(f"Question types: {types}")
                
                # Analyze specialist categories
                specialist_categories = {}
                for q in all_questions:
                    if q.get('question_type') == 'specialist':
                        cat = q.get('category', 'Unknown')
                        specialist_categories[cat] = specialist_categories.get(cat, 0) + 1
                
                print(f"Specialist categories: {specialist_categories}")
                
                # Check for river questions specifically
                river_count = sum(1 for q in all_questions if '河川' in q.get('category', ''))
                print(f"River questions found: {river_count}")
                
            else:
                print("NO QUESTIONS LOADED - This is the root cause!")
                
        except Exception as e:
            print(f"Load all questions error: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Import error: {str(e)}")

def create_emergency_data_fix():
    """Create emergency fix for data loading"""
    print("=== EMERGENCY DATA LOADING FIX ===")
    print()
    
    # Create a simplified data loading function that bypasses validation issues
    fix_code = '''
def emergency_load_all_questions():
    """Emergency simplified data loading function"""
    import os
    import csv
    
    data_dir = os.path.join('rccm-quiz-app', 'data')
    all_questions = []
    
    # Load 4-1 basic questions
    basic_file = os.path.join(data_dir, '4-1.csv')
    if os.path.exists(basic_file):
        try:
            with open(basic_file, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['question_type'] = 'basic'
                    row['category'] = '共通'
                    all_questions.append(row)
            print(f"Basic questions loaded: {sum(1 for q in all_questions if q.get('question_type') == 'basic')}")
        except Exception as e:
            print(f"Basic file error: {e}")
    
    # Load 4-2 specialist questions
    specialist_file = os.path.join(data_dir, '4-2_2019.csv')
    if os.path.exists(specialist_file):
        try:
            with open(specialist_file, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['question_type'] = 'specialist'
                    # Keep original category
                    all_questions.append(row)
            print(f"Specialist questions loaded: {sum(1 for q in all_questions if q.get('question_type') == 'specialist')}")
        except Exception as e:
            print(f"Specialist file error: {e}")
    
    return all_questions
'''
    
    # Write emergency fix to a test file
    with open('emergency_data_loader.py', 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("Emergency fix code written to emergency_data_loader.py")
    
    # Test the emergency fix
    print("Testing emergency fix...")
    exec(fix_code)
    
    try:
        questions = emergency_load_all_questions()
        print(f"Emergency loader result: {len(questions)} questions")
        
        if questions:
            categories = {}
            for q in questions:
                cat = q.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            print(f"Categories found: {categories}")
            
            river_count = sum(1 for q in questions if '河川' in q.get('category', ''))
            print(f"River questions: {river_count}")
            
        return len(questions) > 0
        
    except Exception as e:
        print(f"Emergency fix error: {str(e)}")
        return False

def run_complete_diagnosis():
    """Run complete data loading diagnosis"""
    print("DATA LOADING DIAGNOSIS - Emergency Fix for Field Mixing Problem")
    print("=" * 70)
    print("Background: Task 9 identified field mixing - root cause may be data loading failure")
    print("Symptom: '無データ' in logs indicates files not being loaded")
    print("Goal: Diagnose and fix data loading to enable proper field filtering")
    print()
    
    # Step 1: Check data files
    diagnose_data_files()
    
    # Step 2: Test validation
    test_validation_function()
    
    # Step 3: Test question loading
    test_load_questions_function()
    
    # Step 4: Test complete loading
    test_complete_data_loading()
    
    # Step 5: Create emergency fix
    fix_success = create_emergency_data_fix()
    
    print("=" * 70)
    print("=== DIAGNOSIS SUMMARY ===")
    if fix_success:
        print("SUCCESS: Emergency data loader created and tested")
        print("RESULT: Data loading issue diagnosed and temporary fix available")
        print("NEXT: Apply emergency fix to resolve field mixing problem")
    else:
        print("FAILURE: Unable to resolve data loading issue")
        print("NEXT: Manual intervention required")

if __name__ == "__main__":
    run_complete_diagnosis()