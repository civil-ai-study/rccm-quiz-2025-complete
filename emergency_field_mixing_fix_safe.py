#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY FIX: Field Mixing Problem Resolution (ASCII Safe)
Purpose: Fix LIGHTWEIGHT_DEPARTMENT_MAPPING causing field mixing identified in Task 9
Problem: app.py line 2585 English ID conversion system causing incorrect category filtering
Solution: Replace English ID conversion with direct Japanese category usage
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_current_field_mixing_problem():
    """Demonstrate current field mixing problem"""
    print("=== EMERGENCY: Field Mixing Problem Demonstration ===")
    print("Purpose: Prove LIGHTWEIGHT_DEPARTMENT_MAPPING system causes field mixing")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("[River Department Specialist Test]")
            
            # Test river department specialist exam
            response = client.get('/exam?type=specialist&department=river')
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                
                # Check for field mixing
                if '基礎科目（共通）' in response_text:
                    print("ERROR: Field mixing confirmed - Basic subject questions in River department")
                    print("CAUSE: LIGHTWEIGHT_DEPARTMENT_MAPPING conversion system malfunction")
                    return True
                elif '河川、砂防及び海岸・海洋' in response_text:
                    print("OK: River department questions properly displayed")
                    return False
                else:
                    print("WARNING: Unknown state")
                    return True
            else:
                print(f"ERROR: HTTP error {response.status_code}")
                return True
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return True

def apply_emergency_fix():
    """Apply emergency fix to resolve field mixing"""
    print()
    print("=== EMERGENCY FIX APPLICATION ===")
    print("Fix: Replace LIGHTWEIGHT_DEPARTMENT_MAPPING with direct Japanese category usage")
    print()
    
    try:
        # Create backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'rccm-quiz-app/app.py.backup_emergency_field_mixing_{timestamp}'
        
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup created: {backup_file}")
        
        # Apply fix
        lines = original_content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Fix line 2585: Eliminate English ID to Japanese category conversion
            if 'target_category = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)' in line:
                lines[i] = '                            # EMERGENCY FIX: Eliminate English ID conversion, use direct Japanese categories'
                lines.insert(i+1, '                            # Direct mapping: river -> 河川、砂防及び海岸・海洋')
                lines.insert(i+2, '                            if department == "river":')
                lines.insert(i+3, '                                target_category = "河川、砂防及び海岸・海洋"')
                lines.insert(i+4, '                            elif department == "road":')
                lines.insert(i+5, '                                target_category = "道路"')
                lines.insert(i+6, '                            elif department == "urban":')
                lines.insert(i+7, '                                target_category = "都市計画及び地方計画"')
                lines.insert(i+8, '                            elif department == "tunnel":')
                lines.insert(i+9, '                                target_category = "トンネル"')
                lines.insert(i+10, '                            elif department == "garden":')
                lines.insert(i+11, '                                target_category = "造園"')
                lines.insert(i+12, '                            elif department == "env":')
                lines.insert(i+13, '                                target_category = "建設環境"')
                lines.insert(i+14, '                            elif department == "steel":')
                lines.insert(i+15, '                                target_category = "鋼構造及びコンクリート"')
                lines.insert(i+16, '                            elif department == "soil":')
                lines.insert(i+17, '                                target_category = "土質及び基礎"')
                lines.insert(i+18, '                            elif department == "construction":')
                lines.insert(i+19, '                                target_category = "施工計画、施工設備及び積算"')
                lines.insert(i+20, '                            elif department == "water":')
                lines.insert(i+21, '                                target_category = "上水道及び工業用水道"')
                lines.insert(i+22, '                            elif department == "forest":')
                lines.insert(i+23, '                                target_category = "森林土木"')
                lines.insert(i+24, '                            elif department == "agri":')
                lines.insert(i+25, '                                target_category = "農業土木"')
                lines.insert(i+26, '                            else:')
                lines.insert(i+27, '                                target_category = department  # Fallback')
                modified = True
                break
        
        if modified:
            fixed_content = '\n'.join(lines)
            with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print("Emergency fix applied: English ID conversion system replaced with direct Japanese category mapping")
            return True
        else:
            print("ERROR: Target line not found for modification")
            return False
            
    except Exception as e:
        print(f"ERROR: Fix application failed - {str(e)}")
        return False

def test_after_fix():
    """Test functionality after fix"""
    print()
    print("=== POST-FIX FUNCTIONALITY TEST ===")
    print("Purpose: Verify field mixing problem resolution")
    print()
    
    try:
        # Need to reload module after file modification
        import importlib
        import sys
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        
        with app.test_client() as client:
            print("[Post-Fix River Department Test]")
            
            # Test river department specialist exam
            response = client.get('/exam?type=specialist&department=river')
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                
                # Check fix effectiveness
                if '河川、砂防及び海岸・海洋' in response_text:
                    print("SUCCESS: River department specialist questions properly displayed")
                    return True
                elif '基礎科目（共通）' in response_text:
                    print("FAILURE: Field mixing problem still persists")
                    return False
                else:
                    print("WARNING: Unclear fix result")
                    return False
                
            else:
                print(f"ERROR: HTTP error {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Post-fix test failed - {str(e)}")
        return False

def run_emergency_field_mixing_fix():
    """Execute emergency field mixing fix"""
    print("EMERGENCY RESPONSE: Field Mixing Problem Fix (LIGHTWEIGHT_DEPARTMENT_MAPPING Issue)")
    print("=" * 80)
    print("Discovery: Task 9 River Department 10-question test identified field mixing")
    print("Problem: app.py line 2585 English ID to Japanese category conversion system")
    print("Solution: Eliminate English ID conversion, implement direct Japanese category usage")
    print()
    
    # Step 1: Demonstrate problem
    problem_exists = test_current_field_mixing_problem()
    
    if problem_exists:
        print()
        print("Field mixing problem confirmed - Executing emergency fix")
        
        # Step 2: Apply emergency fix
        fix_success = apply_emergency_fix()
        
        if fix_success:
            # Step 3: Test after fix
            fix_verified = test_after_fix()
            
            print()
            print("=" * 80)
            print("=== EMERGENCY FIX RESULT SUMMARY ===")
            print("=" * 80)
            
            if fix_verified:
                print("SUCCESS: Emergency fix completed")
                print("SUCCESS: Field mixing problem resolved")
                print("SUCCESS: River department specialist questions properly displayed")
                print()
                print(">>> Next Action: Re-execute Task 9 River Department 10-question completion test")
            else:
                print("FAILURE: Emergency fix failed or insufficient")
                print(">>> Next Action: More fundamental fix required")
        else:
            print("FAILURE: Emergency fix application failed")
            print(">>> Next Action: Manual fix required")
    else:
        print()
        print("Field mixing problem already resolved")
        print(">>> Next Action: Proceed to other department tests")

if __name__ == "__main__":
    run_emergency_field_mixing_fix()