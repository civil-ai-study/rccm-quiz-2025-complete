import csv
import re

def fix_csv_file(filename):
    """Fix CSV files by finding lines with wrong field counts and attempting to fix comma issues"""
    print(f"Fixing {filename}...")
    
    # Read the file and identify problematic lines
    problematic_lines = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader, 1):
            if len(row) != 12:
                problematic_lines.append((i, row))
    
    if not problematic_lines:
        print(f"No issues found in {filename}")
        return
    
    print(f"Found {len(problematic_lines)} problematic lines")
    
    # Read the raw file content
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix each problematic line
    for line_num, row in problematic_lines:
        if line_num <= len(lines):
            original_line = lines[line_num - 1].strip()
            print(f"Line {line_num}: {len(row)} fields")
            print(f"Original: {original_line}")
            
            # Common patterns to fix:
            # 1. Numbers with commas like "1,000" -> "1000"
            # 2. Multiple consecutive commas
            # 3. Missing fields
            
            fixed_line = original_line
            # Fix numbers with commas (keeping Japanese text intact)
            fixed_line = re.sub(r'(\d+),(\d{3})', r'\1\2', fixed_line)
            
            # Try to parse the fixed line
            try:
                test_row = list(csv.reader([fixed_line]))[0]
                if len(test_row) == 12:
                    print(f"Fixed: {fixed_line}")
                    lines[line_num - 1] = fixed_line + '\n'
                else:
                    print(f"Still {len(test_row)} fields after fix")
            except:
                print("Failed to parse fixed line")
    
    # Write the fixed file back
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed {filename}")

# Fix the problematic files
files_to_fix = ['data/4-2_2010.csv', 'data/4-2_2011.csv', 'data/4-2_2013.csv', 'data/4-2_2014.csv']

for filename in files_to_fix:
    try:
        fix_csv_file(filename)
        print()
    except Exception as e:
        print(f"Error fixing {filename}: {e}")
        print()