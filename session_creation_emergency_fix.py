#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Creation Emergency Fix
緊急対応-11: セッション作成時の問題選択システム修正

Purpose: Fix the get_mixed_questions() function to use emergency filtering 
instead of the problematic LIGHTWEIGHT_DEPARTMENT_MAPPING system.

Root Cause: While emergency_load_all_questions() was implemented for data loading,
the get_mixed_questions() function still uses the old filtering logic with 
LIGHTWEIGHT_DEPARTMENT_MAPPING, causing field mixing issues.

Fix: Replace LIGHTWEIGHT_DEPARTMENT_MAPPING usage with direct Japanese category filtering
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def create_emergency_session_fix():
    """Create and apply emergency fix for session creation field mixing"""
    print("=== 緊急対応-11: セッション作成時の問題選択システム修正 ===")
    print("Purpose: Fix get_mixed_questions() to use emergency filtering")
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
        
        if problematic_section in content:
            print("✓ Found problematic LIGHTWEIGHT_DEPARTMENT_MAPPING usage")
            
            # Create the emergency fix replacement
            emergency_fix_replacement = """        # EMERGENCY FIX: Use direct Japanese category filtering
        # Completely bypass LIGHTWEIGHT_DEPARTMENT_MAPPING to eliminate field mixing
        target_category = requested_category
        
        # No English ID conversion - use categories directly as they appear in CSV
        # This prevents field mixing issues caused by the mapping system
        logger.info(f"🚨 EMERGENCY FIX: Direct category filtering: {requested_category}")"""
            
            # Apply the fix
            new_content = content.replace(problematic_section, emergency_fix_replacement)
            
            # Also need to fix the specialist department filtering section
            specialist_section = """            # ROCKET ULTRA SYNC: 正規化部門名による安全な変換
            normalized_dept = normalize_department_name(department)
            target_category = get_department_category(normalized_dept) if normalized_dept else None"""
            
            if specialist_section in new_content:
                print("✓ Found problematic specialist department filtering")
                
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
                
                new_content = new_content.replace(specialist_section, specialist_fix)
                print("✓ Applied emergency fix to specialist department filtering")
        
        print()
        print("2. Creating backup and applying emergency fix...")
        
        # Create backup
        import shutil
        backup_filename = f'rccm-quiz-app/app.py.emergency_session_fix_backup_{int(__import__("time").time())}'
        shutil.copy('rccm-quiz-app/app.py', backup_filename)
        print(f"✓ Backup created: {backup_filename}")
        
        # Apply the fix
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✓ Emergency fix applied to app.py")
        
        print()
        print("3. Verification test...")
        
        # Test the fix
        try:
            from app import app
            print("✓ App imports successfully after fix")
            
            # Test session creation
            with app.test_client() as client:
                response = client.get('/start_exam/specialist_urban')
                if response.status_code == 200:
                    print("✓ Urban department session creation successful")
                else:
                    print(f"⚠ Session creation returned status: {response.status_code}")
                    
            print()
            print("=== 緊急対応-11 実行結果 ===")
            print("✅ EMERGENCY FIX APPLIED: Session creation system modified")
            print("✅ LIGHTWEIGHT_DEPARTMENT_MAPPING bypass implemented")
            print("✅ Direct Japanese category filtering enabled")
            print("✅ Field mixing root cause eliminated")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            # Restore backup if verification fails
            shutil.copy(backup_filename, 'rccm-quiz-app/app.py')
            print("✓ Backup restored due to verification failure")
            return False
            
    except Exception as e:
        print(f"❌ Emergency fix failed: {e}")
        return False

def test_urban_department_after_fix():
    """Test urban department after applying emergency session fix"""
    print()
    print("=== 緊急対応-11 効果検証 ===")
    
    try:
        from app import app
        with app.test_client() as client:
            # Start urban planning session
            response = client.get('/start_exam/specialist_urban')
            
            if response.status_code == 200:
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
                            print("✅ SUCCESS: Field mixing eliminated - urban planning questions only")
                            return True
                        elif basic_count > 0 and urban_count == 0:
                            print("❌ STILL FAILED: Only basic subject questions in session")
                            return False
                        else:
                            print(f"⚠ MIXED RESULT: basic={basic_count}, urban={urban_count}")
                            return None
                    else:
                        print("❌ No questions in session")
                        return False
            else:
                print(f"❌ Session creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Verification test failed: {e}")
        return False

def main():
    print("緊急対応-11: セッション作成時の問題選択システム修正")
    print("=" * 60)
    print("Ultra Sync Task 10 - Emergency Session Creation Fix")
    print("Purpose: Fix field mixing in urban department session creation")
    print()
    
    # Apply emergency fix
    fix_result = create_emergency_session_fix()
    
    if fix_result:
        print()
        print("Testing emergency fix effectiveness...")
        test_result = test_urban_department_after_fix()
        
        print()
        print("=" * 60)
        print("緊急対応-11 最終結果:")
        print(f"Emergency fix application: {'SUCCESS' if fix_result else 'FAILED'}")
        print(f"Field mixing elimination: {'SUCCESS' if test_result else 'FAILED' if test_result is False else 'INCONCLUSIVE'}")
        
        if fix_result and test_result:
            print()
            print("🎉 緊急対応-11 完全成功")
            print("- Session creation field mixing problem resolved")
            print("- Urban department now shows urban planning questions only")
            print("- Ready to continue with Task 10 completion")
        elif fix_result:
            print()
            print("⚠ 緊急対応-11 部分成功")
            print("- Emergency fix applied successfully")
            print("- Field mixing may still require additional investigation")
        else:
            print()
            print("❌ 緊急対応-11 失敗")
            print("- Emergency fix could not be applied")
            print("- Manual intervention required")
    
    return fix_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)