#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASCII Safe Ultra Simple Deep Search: Data Path Verification
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
from utils import load_rccm_data_files
import glob

def ascii_data_path_verification():
    """ASCII Safe Data Path Verification"""
    print("=== ASCII Safe Data Path Verification ===")
    
    with app.app_context():
        print("1. Current Working Directory Analysis:")
        cwd = os.getcwd()
        print(f"   Current working dir: {cwd}")
        print(f"   Script location: {os.path.dirname(__file__)}")
        
        # Test different possible paths
        paths_to_test = [
            'data',
            'rccm-quiz-app/data',
            os.path.join('rccm-quiz-app', 'data'),
            os.path.join(os.path.dirname(__file__), 'rccm-quiz-app', 'data')
        ]
        
        print("\n2. Path Existence Test:")
        working_path = None
        for path in paths_to_test:
            exists = os.path.exists(path)
            print(f"   {path}: {'EXISTS' if exists else 'NOT FOUND'}")
            if exists and working_path is None:
                working_path = path
        
        print(f"\n3. Working path identified: {working_path}")
        
        if working_path:
            # CSV file count
            csv_files = glob.glob(os.path.join(working_path, '*.csv'))
            print(f"   CSV files found: {len(csv_files)}")
            
            # Test data loading
            print("\n4. Data Loading Test:")
            try:
                questions = load_rccm_data_files(working_path)
                print(f"   Questions loaded: {len(questions)}")
                
                if questions:
                    print("   SUCCESS: Data loading works!")
                    
                    # Category distribution
                    categories = {}
                    for q in questions:
                        cat = q.get('category', 'Unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    print("   Categories found:")
                    for cat, count in sorted(categories.items()):
                        print(f"     {cat}: {count}")
                else:
                    print("   FAILURE: No questions loaded")
            except Exception as e:
                print(f"   ERROR: {e}")
        
        # Test extract function separately
        print("\n5. Extract Function Test:")
        from app import extract_department_questions_from_csv
        try:
            road_questions = extract_department_questions_from_csv('道路', 10)
            print(f"   Road questions extracted: {len(road_questions)}")
            if road_questions:
                print("   Extract function works!")
            else:
                print("   Extract function returns empty")
        except Exception as e:
            print(f"   Extract function error: {e}")
        
        print("\n=== Verification Complete ===")

if __name__ == "__main__":
    ascii_data_path_verification()