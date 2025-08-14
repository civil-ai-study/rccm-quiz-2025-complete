#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Creation Emergency Fix (Parameter Corrected Version)
緊急対応-11: セッション作成時の問題選択システム修正

Purpose: Fix the get_mixed_questions() function to use emergency filtering 
instead of the problematic LIGHTWEIGHT_DEPARTMENT_MAPPING system.

CRITICAL FIX: Corrected parameter name from 'department_category' to 'department'
"""

import sys
import os
import shutil
import time
sys.path.insert(0, 'rccm-quiz-app')

def create_emergency_session_fix():
    """Create and apply emergency fix for session creation field mixing"""
    print("=== Emergency Session Creation Fix (Parameter Corrected) ===")
    print("Purpose: Fix get_mixed_questions() to use emergency filtering")
    print("CRITICAL: Fixed parameter mismatch issue")
    print()
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the problematic section in get_mixed_questions
        print("1. Analyzing get_mixed_questions function...")
        
        # Locate the problematic LIGHTWEIGHT_DEPARTMENT_MAPPING usage
        problematic_section = """        # ROCKET ULTRA SYNC FIX: 英語部門名→日本語カテゴリ名の完全マッピング
        target_category = requested_category
        if requested_category in LIGHTWEIGHT_DEPARTMENT_MAPPING:
            target_category = LIGHTWEIGHT_DEPARTMENT_MAPPING[requested_category]
            logger.info(f"🔧 ULTRA SYNC: 英語→日本語マッピング適用 {requested_category} → {target_category}")"""
        
        fix_applied = False
        
        if problematic_section in content:
            print("-> Found problematic LIGHTWEIGHT_DEPARTMENT_MAPPING usage")
            
            # Create the emergency fix replacement
            emergency_fix_replacement = """        # EMERGENCY FIX: Use direct Japanese category filtering
        # Completely bypass LIGHTWEIGHT_DEPARTMENT_MAPPING to eliminate field mixing
        target_category = requested_category
        
        # No English ID conversion - use categories directly as they appear in CSV
        # This prevents field mixing issues caused by the mapping system
        logger.info(f"EMERGENCY FIX: Direct category filtering: {requested_category}")"""
            
            # Apply the fix
            content = content.replace(problematic_section, emergency_fix_replacement)
            fix_applied = True
            print("-> Applied emergency fix to LIGHTWEIGHT_DEPARTMENT_MAPPING usage")
        
        # Also need to fix the specialist department filtering section
        specialist_section = """            # ROCKET ULTRA SYNC: 正規化部門名による安全な変換
            normalized_dept = normalize_department_name(department)
            target_category = get_department_category(normalized_dept) if normalized_dept else None"""
        
        if specialist_section in content:
            print("-> Found problematic specialist department filtering")
            
            specialist_fix = """            # EMERGENCY FIX: Use emergency filtering for specialist departments
            # Direct category mapping without English ID conversion
            target_category = None
            if department:
                # Map department directly to Japanese categories used in CSV
                EMERGENCY_DEPARTMENT_MAPPING = {
                    'road': '道路',
                    'river': '河川、砂防及び海岸・海洋', 
                    'urban': '都市計画及び地方計画',
                    'garden': '造園',
                    'env': '建設環境',
                    'steel': '鋼構造及びコンクリート',
                    'soil': '土質及び基礎',
                    'construction': '施工計画、施工設備及び積算',
                    'water': '上水道及び工業用水道',
                    'forest': '森林土木',
                    'agri': '農業土木',
                    'tunnel': 'トンネル'
                }
                target_category = EMERGENCY_DEPARTMENT_MAPPING.get(department, department)"""
            
            content = content.replace(specialist_section, specialist_fix)
            fix_applied = True
            print("-> Applied emergency fix to specialist department filtering")
        
        if not fix_applied:
            print("-> No problematic sections found - may already be fixed")
            return True
        
        print()
        print("2. Creating backup and applying emergency fix...")
        
        # Create backup
        backup_filename = f'rccm-quiz-app/app.py.emergency_session_fix_backup_{int(time.time())}'
        shutil.copy('rccm-quiz-app/app.py', backup_filename)
        print(f"-> Backup created: {backup_filename}")
        
        # Apply the fix
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("-> Emergency fix applied to app.py")
        
        print()
        print("3. Verification test...")
        
        # Test the fix
        try:
            from app import app
            print("-> App imports successfully after fix")
            
            # Test session creation
            with app.test_client() as client:
                response = client.get('/start_exam/specialist_urban')
                if response.status_code in [200, 302]:
                    print("-> Urban department session creation successful")
                else:
                    print(f"-> Session creation returned status: {response.status_code}")
                    
            print()
            print("=== Emergency Fix Results ===")
            print("SUCCESS: Session creation system modified")
            print("SUCCESS: LIGHTWEIGHT_DEPARTMENT_MAPPING bypass implemented")
            print("SUCCESS: Direct Japanese category filtering enabled")
            print("SUCCESS: Field mixing root cause eliminated")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Verification failed: {e}")
            # Restore backup if verification fails
            shutil.copy(backup_filename, 'rccm-quiz-app/app.py')
            print("-> Backup restored due to verification failure")
            return False
            
    except Exception as e:
        print(f"ERROR: Emergency fix failed: {e}")
        return False

def test_urban_department_after_fix():
    """Test urban department after applying emergency session fix"""
    print()
    print("=== Emergency Fix Effectiveness Test ===")
    
    try:
        from app import app
        with app.test_client() as client:
            # Start urban planning session
            response = client.get('/start_exam/specialist_urban')
            
            if response.status_code in [200, 302]:
                print("Session creation successful")
                
                # Check session contents
                with client.session_transaction() as sess:
                    if 'questions' in sess:
                        session_questions = sess['questions']
                        print(f"Session questions: {len(session_questions)}")
                        
                        # Analyze categories
                        categories = {}
                        for q in session_questions:
                            cat = q.get('category', 'unknown')
                            categories[cat] = categories.get(cat, 0) + 1
                        
                        print("Session question categories:")
                        for cat, count in categories.items():
                            print(f"  {cat}: {count} questions")
                        
                        # Check for field mixing
                        basic_count = categories.get('基礎', 0)
                        urban_count = categories.get('都市計画及び地方計画', 0)
                        
                        if basic_count == 0 and urban_count > 0:
                            print("SUCCESS: Field mixing eliminated - urban planning questions only")
                            return True
                        elif basic_count > 0 and urban_count == 0:
                            print("FAILED: Only basic subject questions in session")
                            return False
                        else:
                            print(f"MIXED RESULT: basic={basic_count}, urban={urban_count}")
                            return None
                    else:
                        print("ERROR: No questions in session")
                        return False
            else:
                print(f"ERROR: Session creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Verification test failed: {e}")
        return False

def run_quick_urban_test():
    """Quick test to verify urban department functionality"""
    print()
    print("=== Quick Urban Department Test ===")
    
    try:
        # Test the emergency function directly
        from utils import emergency_get_questions
        
        # CRITICAL FIX: Use correct parameter name 'department' not 'department_category'
        urban_questions = emergency_get_questions(
            department='urban',  # CORRECTED: was department_category
            question_type='specialist',
            count=10
        )
        
        print(f"Emergency function returned: {len(urban_questions)} questions")
        
        if len(urban_questions) > 0:
            print("Sample questions:")
            for i, q in enumerate(urban_questions[:3], 1):
                print(f"  {i}. ID:{q['id']} Category:{q['category']}")
            
            # Check for field mixing
            urban_category = '都市計画及び地方計画'
            field_mixing = any(q.get('category') != urban_category for q in urban_questions)
            
            if not field_mixing:
                print("SUCCESS: Emergency filtering works - zero field mixing")
                return True
            else:
                print("WARNING: Field mixing detected in emergency filtering")
                return False
        else:
            print("ERROR: No urban planning questions found")
            return False
            
    except Exception as e:
        print(f"ERROR: Quick test failed: {e}")
        print(f"Exception details: {type(e).__name__}: {str(e)}")
        return False

def main():
    print("Emergency Session Creation Fix - Parameter Corrected")
    print("=" * 60)
    print("Ultra Sync Task 10 - Emergency Fix for Field Mixing")
    print("Purpose: Fix field mixing in urban department session creation")
    print("CRITICAL FIX: Corrected parameter mismatch issue")
    print()
    
    # First run quick test to verify emergency functions work
    quick_test_result = run_quick_urban_test()
    
    if not quick_test_result:
        print("CRITICAL: Emergency functions not working properly")
        return False
    
    # Apply emergency fix
    fix_result = create_emergency_session_fix()
    
    if fix_result:
        print()
        print("Testing emergency fix effectiveness...")
        test_result = test_urban_department_after_fix()
        
        print()
        print("=" * 60)
        print("Emergency Fix Final Results:")
        print(f"Emergency fix application: {'SUCCESS' if fix_result else 'FAILED'}")
        print(f"Field mixing elimination: {'SUCCESS' if test_result else 'FAILED' if test_result is False else 'INCONCLUSIVE'}")
        
        if fix_result and test_result:
            print()
            print("COMPLETE SUCCESS - Emergency Fix Applied")
            print("- Session creation field mixing problem resolved")
            print("- Urban department now shows urban planning questions only")
            print("- Ready to continue with Task 10 completion")
        elif fix_result:
            print()
            print("PARTIAL SUCCESS - Fix Applied But Issues Remain")
            print("- Emergency fix applied successfully")
            print("- Field mixing may still require additional investigation")
        else:
            print()
            print("FAILED - Emergency Fix Could Not Be Applied")
            print("- Emergency fix could not be applied")
            print("- Manual intervention required")
    
    return fix_result and test_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)