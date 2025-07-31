#!/usr/bin/env python3
"""
RCCM Quiz App Year Investigation Script
Root cause analysis for invalid year issues (2015-2019)
"""

import os
import sys
import csv
import json
from collections import defaultdict

def main():
    print("=== RCCM Quiz App Year Investigation ===")
    
    # Data directory path
    data_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\data"
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        return
    
    print(f"Data directory: {data_dir}")
    
    # 1. Check available CSV files
    print("\n1. Available year files check:")
    csv_files = []
    for filename in os.listdir(data_dir):
        if filename.startswith('4-2_') and filename.endswith('.csv') and 'backup' not in filename:
            csv_files.append(filename)
    
    csv_files.sort()
    years_available = []
    
    for csv_file in csv_files:
        filepath = os.path.join(data_dir, csv_file)
        if os.path.exists(filepath):
            # Extract year
            year_str = csv_file.replace('4-2_', '').replace('.csv', '')
            try:
                year = int(year_str)
                years_available.append(year)
                
                # Count lines in file
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    problem_count = len(lines) - 1  # Exclude header
                    
                print(f"  OK: {csv_file}: {year} year, {problem_count} problems")
                
            except ValueError:
                print(f"  Warning: {csv_file}: Year extraction error")
    
    print(f"\nAvailable years: {sorted(years_available)}")
    print(f"Total years: {len(years_available)}")
    
    # 2. Detailed check for 2015 and 2016 data
    print("\n2. Detailed check for problematic years:")
    
    target_years = [2015, 2016, 2017, 2018, 2019]
    for year in target_years:
        csv_file = f"4-2_{year}.csv"
        filepath = os.path.join(data_dir, csv_file)
        
        if not os.path.exists(filepath):
            print(f"  Error: {year} year: File not found ({csv_file})")
            continue
            
        print(f"\n  Analysis for {year}:")
        try:
            departments = defaultdict(int)
            valid_records = 0
            error_records = 0
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        # Check required fields
                        if 'category' not in row or 'year' not in row:
                            error_records += 1
                            print(f"    Warning: Line {i}: Missing required fields - {list(row.keys())}")
                            continue
                        
                        category = row['category'].strip()
                        year_in_data = row['year'].strip()
                        
                        # Validate year data
                        if not year_in_data or year_in_data != str(year):
                            error_records += 1
                            print(f"    Warning: Line {i}: Year mismatch - Expected:{year}, Actual:'{year_in_data}'")
                            continue
                        
                        departments[category] += 1
                        valid_records += 1
                        
                    except Exception as e:
                        error_records += 1
                        print(f"    Error: Line {i}: Read error - {e}")
            
            print(f"    Valid records: {valid_records}")
            print(f"    Error records: {error_records}")
            print(f"    Problems by department:")
            
            for dept, count in sorted(departments.items()):
                print(f"      - {dept}: {count} problems")
                
        except Exception as e:
            print(f"    Error: File read error - {e}")
    
    # 3. Check year validation in app.py
    print("\n3. Check year validation in app.py:")
    
    app_py_path = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for VALID_YEARS constant
            if 'VALID_YEARS' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'VALID_YEARS' in line and ('=' in line or '[' in line):
                        print(f"  Line {i+1}: {line.strip()}")
                        # Check next few lines too
                        for j in range(1, 5):
                            if i+j < len(lines) and (']' in lines[i+j] or ',' in lines[i+j]):
                                print(f"  Line {i+j+1}: {lines[i+j].strip()}")
                                if ']' in lines[i+j]:
                                    break
            else:
                print("  Warning: VALID_YEARS constant not found")
                
        except Exception as e:
            print(f"  Error: app.py read error - {e}")
    else:
        print(f"  Error: app.py not found: {app_py_path}")
    
    # 4. Result summary
    print("\n4. Investigation result summary:")
    print("=" * 50)
    
    print(f"Available years in CSV files: {sorted(years_available)}")
    
    missing_years = []
    for year in range(2015, 2020):
        if year not in years_available:
            missing_years.append(year)
    
    if missing_years:
        print(f"Missing years: {missing_years}")
    else:
        print("OK: All years 2015-2019 are available")
    
    # Landscape department 2016 test
    print(f"\n5. Landscape department 2016 test:")
    test_year = 2016
    test_dept = "造園"
    csv_file = f"4-2_{test_year}.csv"
    filepath = os.path.join(data_dir, csv_file)
    
    if os.path.exists(filepath):
        try:
            landscape_questions = 0
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('category', '').strip() == test_dept:
                        landscape_questions += 1
            
            print(f"  {test_dept} department {test_year}: {landscape_questions} problems")
            
            if landscape_questions > 0:
                print(f"  OK: {test_dept} department {test_year} problems exist")
            else:
                print(f"  Error: {test_dept} department {test_year} problems not found")
                
                # Check available departments
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    available_depts = set()
                    for row in reader:
                        dept = row.get('category', '').strip()
                        if dept:
                            available_depts.add(dept)
                    
                    print(f"  Available departments in {test_year}: {sorted(available_depts)}")
                    
        except Exception as e:
            print(f"  Test error: {e}")
    else:
        print(f"  Error: {test_year} year file does not exist")

if __name__ == "__main__":
    main()