#!/usr/bin/env python3
import csv
import re
import os

def analyze_csv_for_symbols(file_path):
    """Analyze a CSV file for numbered symbols in options"""
    problems = []
    symbol_pattern = re.compile(r'[①②③④⑤⑥⑦⑧⑨⑩]')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                problem_options = []
                
                # Check each option column for symbols
                for option_col in ['option_a', 'option_b', 'option_c', 'option_d']:
                    if option_col in row and symbol_pattern.search(row[option_col]):
                        problem_options.append(option_col)
                
                # If we found symbols in any option, record this question
                if problem_options:
                    problems.append({
                        'file': os.path.basename(file_path),
                        'question_id': row.get('id', 'N/A'),
                        'question_text': row.get('question', '')[:50] + '...' if len(row.get('question', '')) > 50 else row.get('question', ''),
                        'problematic_options': problem_options,
                        'option_a': row.get('option_a', ''),
                        'option_b': row.get('option_b', ''),
                        'option_c': row.get('option_c', ''),
                        'option_d': row.get('option_d', ''),
                        'explanation': row.get('explanation', ''),
                        'full_question': row.get('question', '')
                    })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return problems

def main():
    data_dir = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data"
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    csv_files.sort()
    
    all_problems = []
    files_with_problems = []
    
    print("=== COMPREHENSIVE ANALYSIS OF NUMBERED SYMBOLS IN CSV FILES ===\n")
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        problems = analyze_csv_for_symbols(file_path)
        
        if problems:
            files_with_problems.append(csv_file)
            all_problems.extend(problems)
            print(f"📁 FILE: {csv_file}")
            print(f"   Found {len(problems)} questions with numbered symbols")
            print()
    
    print(f"=== SUMMARY ===")
    print(f"Total files checked: {len(csv_files)}")
    print(f"Files with problems: {len(files_with_problems)}")
    print(f"Total problematic questions: {len(all_problems)}")
    print()
    
    print("Files containing numbered symbols:")
    for file in files_with_problems:
        print(f"  - {file}")
    print()
    
    print("=== DETAILED ANALYSIS OF PROBLEMATIC QUESTIONS ===\n")
    
    for i, problem in enumerate(all_problems, 1):
        print(f"🔍 PROBLEM {i}:")
        print(f"   File: {problem['file']}")
        print(f"   Question ID: {problem['question_id']}")
        print(f"   Question: {problem['question_text']}")
        print(f"   Problematic Options: {', '.join(problem['problematic_options'])}")
        print()
        
        # Show the actual option content
        for opt in ['option_a', 'option_b', 'option_c', 'option_d']:
            if opt in problem['problematic_options']:
                print(f"   {opt.upper()}: {problem[opt]}")
        print()
        
        # Check if explanation might contain actual option texts
        explanation = problem['explanation']
        if any(symbol in explanation for symbol in ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']):
            print(f"   EXPLANATION (may contain actual option texts): {explanation}")
            print()
        
        print("   " + "="*60)
        print()

if __name__ == "__main__":
    main()