#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Department Session Structure Emergency Fix
建設環境部門セッション構造緊急修正

緊急対応-14: 建設環境部門セッション構造不整合緊急修正
Purpose: Fix session structure mismatch between start_exam route and exam route
CRITICAL: start_exam uses 'questions' key, exam() uses 'exam_question_ids' key

Root Cause Identified:
- /start_exam/specialist_env creates session with 'questions' key ✅
- /exam route expects 'exam_question_ids' key ❌
- Session structure mismatch causes exam() to create new basic session instead of using existing construction environment session

Fix Strategy:
- Add session structure conversion system in exam() function
- Convert Emergency Fix 12 session structure to exam() compatible structure
- Ensure seamless transition between start_exam and exam routes
"""

import sys
import os
import shutil
import time
sys.path.insert(0, 'rccm-quiz-app')

def create_session_structure_integration_fix():
    """Create and apply session structure integration fix"""
    print("=== Emergency Fix 14: Session Structure Integration ===")
    print("Purpose: Fix session structure mismatch between start_exam and exam routes")
    print("Critical Issue: Construction Environment session being replaced by basic session")
    print()
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the problematic section in exam() function where session check occurs
        print("1. Analyzing exam() function session check logic...")
        
        # Locate the problematic session check that causes new session creation
        problematic_session_check = """            # 既存セッションがない場合、新規セッションを開始
            if 'exam_question_ids' not in session or not session.get('exam_question_ids'):"""
        
        if problematic_session_check in content:
            print("-> Found problematic session check logic")
            
            # Create the emergency fix replacement that handles both session structures
            emergency_session_fix = """            # EMERGENCY FIX 14: Handle both session structures (Emergency Fix 12 + exam() compatibility)
            # Check for both 'questions' key (Emergency Fix 12) and 'exam_question_ids' key (exam() standard)
            has_emergency_session = 'questions' in session and session.get('questions')
            has_standard_session = 'exam_question_ids' in session and session.get('exam_question_ids')
            
            # If Emergency Fix 12 session exists but standard session doesn't, convert structure
            if has_emergency_session and not has_standard_session:
                logger.info("EMERGENCY FIX 14: Converting Emergency Fix 12 session structure to exam() compatible structure")
                try:
                    emergency_questions = session.get('questions', [])
                    if emergency_questions:
                        # Convert Emergency Fix session structure to standard exam structure
                        session['exam_question_ids'] = [q['id'] for q in emergency_questions]
                        session['exam_current'] = session.get('current_question', 0)
                        
                        # Set category based on first question
                        first_question = emergency_questions[0]
                        session['exam_category'] = first_question.get('category', '不明')
                        session['selected_question_type'] = first_question.get('question_type', 'specialist')
                        
                        session.modified = True
                        logger.info(f"EMERGENCY FIX 14: Session structure converted successfully - {len(emergency_questions)} questions, category: {session['exam_category']}")
                        
                        # Now we have standard session structure, continue with normal flow
                        has_standard_session = True
                    else:
                        logger.warning("EMERGENCY FIX 14: Emergency session questions empty")
                except Exception as e:
                    logger.error(f"EMERGENCY FIX 14: Session structure conversion failed: {e}")
            
            # 既存セッションがない場合、新規セッションを開始
            if not has_standard_session:"""
            
            # Apply the fix
            content = content.replace(problematic_session_check, emergency_session_fix)
            fix_applied = True
            print("-> Applied Emergency Fix 14: Session structure integration")
        else:
            print("-> Problematic session check not found - may already be fixed")
            fix_applied = False
        
        if not fix_applied:
            print("-> No fixes needed - session structure may already be integrated")
            return True
        
        print()
        print("2. Creating backup and applying Emergency Fix 14...")
        
        # Create backup
        backup_filename = f'rccm-quiz-app/app.py.emergency_session_structure_fix_{int(time.time())}'
        shutil.copy('rccm-quiz-app/app.py', backup_filename)
        print(f"-> Backup created: {backup_filename}")
        
        # Apply the fix
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("-> Emergency Fix 14 applied to app.py")
        
        print()
        print("3. Verification test...")
        
        # Test the fix
        try:
            from app import app
            print("-> App imports successfully after Emergency Fix 14")
            
            # Test construction environment session creation and exam access
            with app.test_client() as client:
                # Step 1: Create construction environment session
                start_response = client.get('/start_exam/specialist_env')
                if start_response.status_code in [200, 302]:
                    print("-> Construction environment session creation successful")
                    
                    # Step 2: Test exam page access (should use converted session structure)
                    exam_response = client.get('/exam')
                    if exam_response.status_code == 200:
                        content = exam_response.get_data(as_text=True)
                        
                        # Check for construction environment content
                        if '建設環境' in content and 'csrf_token' in content:
                            print("-> Exam page displays construction environment content with CSRF token")
                            print("SUCCESS: Emergency Fix 14 - Session structure integration working")
                        else:
                            print("-> Exam page content validation failed")
                            return False
                    else:
                        print(f"-> Exam page access failed: {exam_response.status_code}")
                        return False
                else:
                    print(f"-> Session creation failed: {start_response.status_code}")
                    return False
                    
            print()
            print("=== Emergency Fix 14 Results ===")
            print("SUCCESS: Session structure integration implemented")
            print("SUCCESS: Emergency Fix 12 'questions' key compatibility added")
            print("SUCCESS: Standard exam() 'exam_question_ids' key support maintained")
            print("SUCCESS: Construction environment session preservation confirmed")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Verification failed: {e}")
            # Restore backup if verification fails
            shutil.copy(backup_filename, 'rccm-quiz-app/app.py')
            print("-> Backup restored due to verification failure")
            return False
            
    except Exception as e:
        print(f"ERROR: Emergency Fix 14 failed: {e}")
        return False

def test_construction_environment_after_session_fix():
    """Test construction environment department after applying session structure fix"""
    print()
    print("=== Emergency Fix 14 Effectiveness Test ===")
    
    try:
        from app import app
        with app.test_client() as client:
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            if response.status_code in [200, 302]:
                print("Session creation successful")
                
                # Test exam page access
                exam_response = client.get('/exam')
                print(f"Exam page status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    content = exam_response.get_data(as_text=True)
                    
                    # Check essential elements
                    csrf_check = 'csrf_token' in content
                    form_check = '<form' in content and 'method="POST"' in content
                    category_check = '建設環境' in content
                    question_check = '<h3' in content
                    answer_check = 'name="answer"' in content
                    
                    print("Essential elements check:")
                    print(f"  CSRF token: {'✅' if csrf_check else '❌'}")
                    print(f"  Form elements: {'✅' if form_check else '❌'}")
                    print(f"  Category display (建設環境): {'✅' if category_check else '❌'}")
                    print(f"  Question elements: {'✅' if question_check else '❌'}")
                    print(f"  Answer options: {'✅' if answer_check else '❌'}")
                    
                    if all([csrf_check, form_check, category_check, question_check, answer_check]):
                        print("SUCCESS: Emergency Fix 14 - Construction environment session structure working properly")
                        return True
                    else:
                        print("FAILED: Some essential elements missing")
                        return False
                else:
                    print("FAILED: Exam page access failed")
                    return False
            else:
                print(f"ERROR: Session creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Effectiveness test failed: {e}")
        return False

def main():
    print("Construction Environment Department Session Structure Emergency Fix")
    print("=" * 80)
    print("緊急対応-14: 建設環境部門セッション構造不整合緊急修正")
    print("Purpose: Fix session structure mismatch between start_exam and exam routes")
    print("Critical Issue: Construction environment session being replaced by basic session")
    print()
    
    # Apply Emergency Fix 14
    fix_result = create_session_structure_integration_fix()
    
    if fix_result:
        print()
        print("Testing Emergency Fix 14 effectiveness...")
        test_result = test_construction_environment_after_session_fix()
        
        print()
        print("=" * 80)
        print("Emergency Fix 14 Final Results:")
        print(f"Emergency Fix 14 application: {'SUCCESS' if fix_result else 'FAILED'}")
        print(f"Construction environment session fix: {'SUCCESS' if test_result else 'FAILED' if test_result is False else 'INCONCLUSIVE'}")
        
        if fix_result and test_result:
            print()
            print("COMPLETE SUCCESS - Emergency Fix 14 Applied")
            print("- Session structure mismatch problem resolved")
            print("- Construction environment department now works properly")
            print("- Emergency Fix 12 and exam() route integration successful")
            print("- Ready to proceed with Task 12 completion")
            return True
        elif fix_result:
            print()
            print("PARTIAL SUCCESS - Fix Applied But Issues May Remain")
            print("- Emergency Fix 14 applied successfully")
            print("- Construction environment may still require additional investigation")
            return False
        else:
            print()
            print("FAILED - Emergency Fix 14 Could Not Be Applied")
            print("- Session structure integration failed")
            print("- Manual intervention required")
            return False
    else:
        print("Emergency Fix 14 application failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)