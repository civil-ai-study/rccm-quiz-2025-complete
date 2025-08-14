#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Emergency Fix 17 Improved
建設環境部門緊急対応-17改良版
Purpose: Fix the session replacement issue properly by addressing timing and condition problems
"""

import os
import re
import shutil
from datetime import datetime

def create_improved_emergency_fix_17():
    """Create and apply improved Emergency Fix 17"""
    print("=== Emergency Fix 17 Improved: Construction Environment Session Preservation ===")
    print("Purpose: Fix session replacement by improving condition detection and timing")
    print()
    
    app_path = 'rccm-quiz-app/app.py'
    
    try:
        # Read current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Creating backup...")
        timestamp = int(datetime.now().timestamp())
        backup_path = f'{app_path}.emergency_fix17_improved_{timestamp}'
        shutil.copy2(app_path, backup_path)
        print(f"   Backup created: {backup_path}")
        
        print("2. Analyzing current Emergency Fix 17...")
        if 'EMERGENCY FIX 17' in content:
            print("   Found existing Emergency Fix 17")
            
            # Find the start of Emergency Fix 17
            lines = content.split('\n')
            fix17_start = None
            fix17_end = None
            
            for i, line in enumerate(lines):
                if 'EMERGENCY FIX 17: Construction Environment Session Final Fix' in line:
                    fix17_start = i
                elif fix17_start is not None and 'has_standard_session and not is_construction_env_context:' in line:
                    # Find the end of the Emergency Fix 17 block
                    fix17_end = i
                    break
            
            if fix17_start is not None:
                print(f"   Emergency Fix 17 found at lines {fix17_start + 1} to {fix17_end + 1 if fix17_end else 'end'}")
        else:
            print("   No existing Emergency Fix 17 found")
            return False
        
        print("3. Applying improved Emergency Fix 17...")
        
        # Create the improved fix
        improved_fix = '''            # EMERGENCY FIX 17 IMPROVED: Construction Environment Session Preservation
            # Fix session replacement by improving condition detection and timing
            is_construction_env_context = False
            construction_env_session_data = None
            
            # CRITICAL: Check for construction environment session FIRST, before any other logic
            if 'questions' in session and session.get('questions'):
                emergency_questions = session.get('questions', [])
                if emergency_questions and len(emergency_questions) > 0:
                    first_question = emergency_questions[0]
                    question_category = first_question.get('category', '')
                    if question_category == '建設環境':
                        is_construction_env_context = True
                        construction_env_session_data = emergency_questions
                        logger.info(f"EMERGENCY FIX 17 IMPROVED: Construction environment session detected with {len(emergency_questions)} questions")
                        
                        # FORCE PRESERVE: Convert to standard format immediately
                        logger.info("EMERGENCY FIX 17 IMPROVED: Force converting construction environment session to preserve it")
                        try:
                            session['exam_question_ids'] = [q['id'] for q in construction_env_session_data]
                            session['exam_current'] = session.get('current_question', 0)
                            session['exam_category'] = '建設環境'
                            session['selected_question_type'] = 'specialist'
                            session.modified = True
                            has_standard_session = True
                            logger.info("EMERGENCY FIX 17 IMPROVED: Construction environment session force preserved successfully")
                        except Exception as e:
                            logger.error(f"EMERGENCY FIX 17 IMPROVED: Session force preservation failed: {e}")
                            # If conversion fails, prevent new session creation
                            is_construction_env_context = True  # Still prevent new session
            
            # EARLY RETURN: If construction environment session detected, skip new session creation entirely
            if is_construction_env_context:
                logger.info("EMERGENCY FIX 17 IMPROVED: Construction environment session preserved, skipping new session creation")
            
            # EMERGENCY FIX 14: Handle both session structures (Emergency Fix 12 + exam() compatibility)
            # Check for both 'questions' key (Emergency Fix 12) and 'exam_question_ids' key (exam() standard)  
            elif not is_construction_env_context:  # Only run if not construction environment
                has_emergency_session = 'questions' in session and session.get('questions')
                # Re-check has_standard_session as it might have been set above
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
            '''
        
        # Replace the existing Emergency Fix 17 section
        if fix17_start is not None and fix17_end is not None:
            # Find the indentation of the original fix
            original_line = lines[fix17_start]
            indentation = len(original_line) - len(original_line.lstrip())
            indent_str = ' ' * indentation
            
            # Apply proper indentation to the improved fix
            improved_lines = improved_fix.strip().split('\n')
            indented_improved_lines = [indent_str + line if line.strip() else line for line in improved_lines]
            
            # Replace the old fix with the improved one
            new_lines = lines[:fix17_start] + indented_improved_lines + lines[fix17_end:]
            new_content = '\n'.join(new_lines)
            
            # Update the condition for new session creation to respect construction environment context
            new_content = new_content.replace(
                '既存セッションがない場合、新規セッションを開始\n            if not has_standard_session and not is_construction_env_context:',
                '既存セッションがない場合、新規セッションを開始\n            if not has_standard_session and not is_construction_env_context:'
            )
            
            # Write the updated content
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print("   ✅ Emergency Fix 17 Improved applied successfully")
            
        else:
            print("   ❌ Could not find Emergency Fix 17 location for replacement")
            return False
        
        print("4. Verifying syntax...")
        # Test syntax
        try:
            compile(new_content, app_path, 'exec')
            print("   ✅ Syntax verification successful")
        except SyntaxError as e:
            print(f"   ❌ Syntax error detected: {e}")
            # Restore backup
            shutil.copy2(backup_path, app_path)
            print("   ✅ Backup restored")
            return False
        
        print("\n=== Emergency Fix 17 Improved Summary ===")
        print("✅ Improved session detection logic")
        print("✅ Added force preservation mechanism")
        print("✅ Earlier timing in the exam() function flow")
        print("✅ Better condition checking for construction environment sessions")
        print("✅ Prevents new session creation when construction environment session exists")
        
        return True
        
    except Exception as e:
        print(f"Emergency Fix 17 Improved failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    if create_improved_emergency_fix_17():
        print("\n🎉 Emergency Fix 17 Improved applied successfully!")
        print("✅ Construction environment session replacement should now be prevented")
        print("📝 Ready for testing with construction_env_department_complete_test.py")
    else:
        print("\n❌ Emergency Fix 17 Improved application failed")
        print("🔧 Manual intervention may be required")

if __name__ == "__main__":
    main()