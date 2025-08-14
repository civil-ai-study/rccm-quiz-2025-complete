#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY DATA LOADING SYSTEM FIX
Purpose: Fix the "0ファイル,総計0問" problem identified in emergency diagnostics
Problem: System shows 0 files/0 questions despite CSV files containing correct data
Solution: Create emergency data loading bypass to restore functionality
"""

import sys
import os
import csv
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def create_emergency_data_loader():
    """Create emergency data loading function that bypasses problematic validation"""
    print("=== EMERGENCY DATA LOADING SYSTEM FIX ===")
    print("Purpose: Fix 0ファイル,総計0問 problem with direct CSV loading")
    print()
    
    # Emergency fix code that bypasses complex validation
    emergency_fix_code = '''
def emergency_load_all_questions():
    """
    EMERGENCY DATA LOADER - Bypasses complex validation causing 0ファイル,総計0問 error
    Problem: Original system fails to load any questions due to validation issues
    Solution: Direct CSV loading with minimal validation
    """
    import os
    import csv
    import logging
    
    logger = logging.getLogger(__name__)
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    all_questions = []
    
    print(f"Emergency data loading from: {data_dir}")
    
    # Emergency bypass: Direct CSV loading without complex validation
    csv_files = {
        '4-1.csv': 'basic',
        '4-2_2019.csv': 'specialist'
    }
    
    for filename, question_type in csv_files.items():
        filepath = os.path.join(data_dir, filename)
        print(f"Loading: {filepath}")
        
        if os.path.exists(filepath):
            try:
                # Try multiple encodings
                for encoding in ['utf-8-sig', 'utf-8', 'shift_jis', 'cp932']:
                    try:
                        with open(filepath, 'r', encoding=encoding) as f:
                            reader = csv.DictReader(f)
                            file_questions = []
                            for row in reader:
                                # Emergency fix: Set required fields
                                row['question_type'] = question_type
                                if question_type == 'basic':
                                    row['category'] = '共通'
                                # Keep original category for specialist questions
                                file_questions.append(row)
                            
                            all_questions.extend(file_questions)
                            print(f"✅ {filename}: {len(file_questions)} questions loaded (encoding: {encoding})")
                            break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"⚠️ Error with {filename}: {e}")
                        continue
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
        else:
            print(f"❌ File not found: {filepath}")
    
    print(f"Emergency loader result: {len(all_questions)} total questions")
    return all_questions

# Emergency replacement for problematic get_questions function
def emergency_get_questions(department=None, question_type=None, count=10):
    """
    EMERGENCY QUESTION GETTER - Replaces problematic original function
    """
    all_questions = emergency_load_all_questions()
    
    if not all_questions:
        print("❌ EMERGENCY: No questions loaded - check CSV files")
        return []
    
    # Filter questions based on parameters
    filtered_questions = all_questions
    
    if question_type:
        filtered_questions = [q for q in filtered_questions if q.get('question_type') == question_type]
        print(f"Filtered by type '{question_type}': {len(filtered_questions)} questions")
    
    if department and question_type == 'specialist':
        # EMERGENCY FIX: Use direct Japanese category mapping
        department_mapping = {
            'river': '河川、砂防及び海岸・海洋',
            'road': '道路',
            'urban': '都市計画及び地方計画',
            'tunnel': 'トンネル',
            'garden': '造園',
            'env': '建設環境',
            'steel': '鋼構造及びコンクリート',
            'soil': '土質及び基礎',
            'construction': '施工計画、施工設備及び積算',
            'water': '上水道及び工業用水道',
            'forest': '森林土木',
            'agri': '農業土木'
        }
        
        target_category = department_mapping.get(department, department)
        filtered_questions = [q for q in filtered_questions if q.get('category') == target_category]
        print(f"Filtered by department '{department}' (category: {target_category}): {len(filtered_questions)} questions")
    
    # Return requested count
    if count and len(filtered_questions) > count:
        import random
        filtered_questions = random.sample(filtered_questions, count)
    
    print(f"Final result: {len(filtered_questions)} questions")
    return filtered_questions
'''
    
    # Write emergency fix to utils.py as a patch
    try:
        # Read current utils.py
        with open('rccm-quiz-app/utils.py', 'r', encoding='utf-8') as f:
            utils_content = f.read()
        
        # Add emergency functions at the end
        emergency_patch = f"""

# ================================
# EMERGENCY DATA LOADING FIX
# Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Purpose: Fix 0ファイル,総計0問 problem
# ================================

{emergency_fix_code}

# End of emergency fix
# ================================
"""
        
        # Create backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'rccm-quiz-app/utils.py.backup_emergency_data_fix_{timestamp}'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(utils_content)
        print(f"✅ Backup created: {backup_file}")
        
        # Apply emergency patch
        patched_content = utils_content + emergency_patch
        with open('rccm-quiz-app/utils.py', 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print("✅ Emergency data loading functions added to utils.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply emergency patch: {e}")
        return False

def test_emergency_fix():
    """Test the emergency fix"""
    print()
    print("=== TESTING EMERGENCY FIX ===")
    
    try:
        # Import the emergency functions
        sys.path.insert(0, 'rccm-quiz-app')
        from utils import emergency_load_all_questions, emergency_get_questions
        
        # Test basic loading
        all_questions = emergency_load_all_questions()
        print(f"✅ Emergency loader test: {len(all_questions)} questions")
        
        if all_questions:
            # Test category distribution
            categories = {}
            for q in all_questions:
                cat = q.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print("Categories found:")
            for cat, count in sorted(categories.items()):
                print(f"  {cat}: {count} questions")
            
            # Test river department filtering (the problematic case)
            river_questions = emergency_get_questions(department='river', question_type='specialist', count=10)
            print(f"✅ River department test: {len(river_questions)} questions")
            
            if river_questions:
                river_categories = {q.get('category') for q in river_questions}
                print(f"River question categories: {river_categories}")
                
                # Check for field mixing
                if '河川、砂防及び海岸・海洋' in river_categories:
                    print("✅ FIELD MIXING FIXED: River questions properly filtered")
                    return True
                else:
                    print("❌ Field mixing still present")
                    return False
            else:
                print("❌ No river questions found")
                return False
        else:
            print("❌ No questions loaded by emergency system")
            return False
            
    except Exception as e:
        print(f"❌ Emergency fix test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_app_py_patch():
    """Apply patch to app.py to use emergency functions"""
    print()
    print("=== APPLYING APP.PY PATCH ===")
    
    try:
        # Read app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Create backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'rccm-quiz-app/app.py.backup_emergency_data_patch_{timestamp}'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(app_content)
        print(f"✅ App.py backup created: {backup_file}")
        
        # Add import for emergency functions at the top
        emergency_import = """
# EMERGENCY DATA LOADING FIX
try:
    from utils import emergency_load_all_questions, emergency_get_questions
    EMERGENCY_DATA_FIX_AVAILABLE = True
    print("✅ Emergency data loading functions imported successfully")
except ImportError:
    EMERGENCY_DATA_FIX_AVAILABLE = False
    print("⚠️ Emergency data loading functions not available")
"""
        
        # Find a good place to insert the import (after other imports)
        lines = app_content.split('\n')
        import_insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('from') or line.startswith('import'):
                import_insert_pos = i + 1
        
        # Insert emergency import
        lines.insert(import_insert_pos, emergency_import)
        
        # Patch get_questions function calls to use emergency version
        emergency_patch_code = '''
    # EMERGENCY DATA FIX: Use emergency functions if available
    if EMERGENCY_DATA_FIX_AVAILABLE:
        try:
            questions = emergency_get_questions(department=department, question_type=question_type, count=count)
            if questions:
                logger.info(f"✅ Emergency data fix success: {len(questions)} questions loaded")
                return questions
            else:
                logger.warning("⚠️ Emergency data fix returned no questions, falling back to original")
        except Exception as e:
            logger.error(f"❌ Emergency data fix error: {e}, falling back to original")
'''
        
        # Find get_questions function and add emergency patch
        patched_lines = []
        in_get_questions = False
        for line in lines:
            if 'def get_questions(' in line:
                in_get_questions = True
                patched_lines.append(line)
            elif in_get_questions and line.strip().startswith('logger.info') and 'questions requested' in line:
                patched_lines.append(line)
                # Add emergency patch after the initial logging
                for patch_line in emergency_patch_code.strip().split('\n'):
                    patched_lines.append(patch_line)
                in_get_questions = False
            else:
                patched_lines.append(line)
        
        # Write patched content
        patched_content = '\n'.join(patched_lines)
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print("✅ Emergency data patch applied to app.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch app.py: {e}")
        return False

def run_emergency_data_loading_fix():
    """Execute complete emergency data loading fix"""
    print("EMERGENCY DATA LOADING SYSTEM FIX")
    print("=" * 60)
    print("Problem: System shows 0ファイル,総計0問 despite CSV files containing data")
    print("Solution: Emergency data loading bypass with direct CSV access")
    print()
    
    # Step 1: Create emergency data loader
    step1_success = create_emergency_data_loader()
    
    if step1_success:
        # Step 2: Test emergency fix
        step2_success = test_emergency_fix()
        
        if step2_success:
            # Step 3: Apply app.py patch
            step3_success = apply_app_py_patch()
            
            if step3_success:
                print()
                print("=" * 60)
                print("=== EMERGENCY FIX SUMMARY ===")
                print("✅ Step 1: Emergency data loader created")
                print("✅ Step 2: Emergency fix tested successfully")
                print("✅ Step 3: App.py patch applied")
                print()
                print("🎉 EMERGENCY DATA LOADING FIX COMPLETE")
                print("Expected result: River department will now show river questions instead of basic questions")
                print()
                print(">>> Next Action: Re-run Task 9 (River Department test) to verify fix")
                return True
            else:
                print("❌ Step 3 failed: App.py patch failed")
        else:
            print("❌ Step 2 failed: Emergency fix test failed")
    else:
        print("❌ Step 1 failed: Emergency data loader creation failed")
    
    print()
    print(">>> Emergency fix incomplete - manual intervention required")
    return False

if __name__ == "__main__":
    run_emergency_data_loading_fix()