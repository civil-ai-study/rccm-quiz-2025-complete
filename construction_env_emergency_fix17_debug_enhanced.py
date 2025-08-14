#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Emergency Fix 17 Debug Enhanced
建設環境部門緊急対応-17デバッグ強化版
Purpose: Add comprehensive debug logging to understand why Emergency Fix 17 is not triggered
"""

import os
import re
import shutil
from datetime import datetime

def add_debug_logging_to_emergency_fix_17():
    """Add comprehensive debug logging to Emergency Fix 17 to understand execution flow"""
    print("=== Emergency Fix 17 Debug Enhanced: Adding Comprehensive Logging ===")
    print("Purpose: Understand why Emergency Fix 17 Improved is not being triggered")
    print()
    
    app_path = 'rccm-quiz-app/app.py'
    
    try:
        # Read current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Creating backup...")
        timestamp = int(datetime.now().timestamp())
        backup_path = f'{app_path}.emergency_fix17_debug_{timestamp}'
        shutil.copy2(app_path, backup_path)
        print(f"   Backup created: {backup_path}")
        
        print("2. Adding comprehensive debug logging...")
        
        # Add debug logging at the very beginning of exam() function
        debug_logging_start = '''
        # DEBUG LOGGING: Emergency Fix 17 execution tracking
        logger.info("=== DEBUG: exam() function entry ===")
        logger.info(f"DEBUG: Request method: {request.method}")
        logger.info(f"DEBUG: Request args: {request.args}")
        logger.info(f"DEBUG: Session keys at entry: {list(session.keys())}")
        
        if 'questions' in session:
            questions_count = len(session.get('questions', []))
            logger.info(f"DEBUG: Emergency session 'questions' key found with {questions_count} questions")
            if questions_count > 0:
                first_question = session['questions'][0]
                category = first_question.get('category', 'NO_CATEGORY')
                logger.info(f"DEBUG: First question category: '{category}'")
                logger.info(f"DEBUG: Is construction environment: {category == '建設環境'}")
        else:
            logger.info("DEBUG: No 'questions' key in session")
            
        if 'exam_question_ids' in session:
            exam_ids_count = len(session.get('exam_question_ids', []))
            logger.info(f"DEBUG: Standard session 'exam_question_ids' key found with {exam_ids_count} questions")
        else:
            logger.info("DEBUG: No 'exam_question_ids' key in session")'''
        
        # Find the exam function and add debug logging right at the start
        lines = content.split('\n')
        exam_function_start = None
        
        for i, line in enumerate(lines):
            if 'def exam():' in line or '@app.route(\'/exam\')' in line:
                # Find the actual function body start
                if 'def exam():' in line:
                    exam_function_start = i + 1
                    break
                elif '@app.route(\'/exam\')' in line:
                    # Look for the function definition after the route decorator
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'def exam():' in lines[j]:
                            exam_function_start = j + 1
                            break
        
        if exam_function_start is not None:
            print(f"   Found exam() function at line {exam_function_start + 1}")
            
            # Insert debug logging at the beginning of the function
            # Find the proper indentation
            function_line = lines[exam_function_start - 1]
            base_indent = len(function_line) - len(function_line.lstrip())
            body_indent = base_indent + 4
            indent_str = ' ' * body_indent
            
            # Split debug logging into individual lines with proper indentation
            debug_lines = debug_logging_start.strip().split('\n')
            indented_debug_lines = [indent_str + line.strip() if line.strip() else line for line in debug_lines]
            
            # Insert debug logging after the function definition
            new_lines = lines[:exam_function_start] + indented_debug_lines + [''] + lines[exam_function_start:]
        else:
            print("   ❌ Could not find exam() function")
            return False
        
        # Now find Emergency Fix 17 Improved and add debug logging there too
        fix17_start = None
        for i, line in enumerate(new_lines):
            if 'EMERGENCY FIX 17 IMPROVED: Construction Environment Session Preservation' in line:
                fix17_start = i
                break
        
        if fix17_start is not None:
            print(f"   Found Emergency Fix 17 Improved at line {fix17_start + 1}")
            
            # Add debug logging right before the Emergency Fix 17 Improved section
            emergency_debug_logging = '''
            # DEBUG LOGGING: Before Emergency Fix 17 Improved execution
            logger.info("=== DEBUG: About to execute Emergency Fix 17 Improved ===")
            logger.info(f"DEBUG: Session has 'questions' key: {'questions' in session}")
            if 'questions' in session:
                emergency_questions = session.get('questions', [])
                logger.info(f"DEBUG: Questions count: {len(emergency_questions)}")
                if emergency_questions and len(emergency_questions) > 0:
                    first_question = emergency_questions[0]
                    question_category = first_question.get('category', '')
                    logger.info(f"DEBUG: First question category: '{question_category}'")
                    logger.info(f"DEBUG: Category check result: {question_category == '建設環境'}")
                else:
                    logger.info("DEBUG: Emergency questions list is empty")
            else:
                logger.info("DEBUG: No 'questions' key found in session")'''
            
            # Get the indentation of the Emergency Fix line
            original_line = new_lines[fix17_start]
            indentation = len(original_line) - len(original_line.lstrip())
            indent_str = ' ' * indentation
            
            # Apply proper indentation to the debug logging
            debug_lines = emergency_debug_logging.strip().split('\n')
            indented_debug_lines = [indent_str + line.strip() if line.strip() else line for line in debug_lines]
            
            # Insert debug logging before Emergency Fix 17 Improved
            new_lines = new_lines[:fix17_start] + indented_debug_lines + [''] + new_lines[fix17_start:]
            
        else:
            print("   ❌ Could not find Emergency Fix 17 Improved section")
            return False
        
        # Add debug logging after Emergency Fix 17 processing
        post_fix17_debug = '''
            # DEBUG LOGGING: After Emergency Fix 17 Improved processing
            logger.info("=== DEBUG: Emergency Fix 17 Improved processing completed ===")
            logger.info(f"DEBUG: is_construction_env_context value: {is_construction_env_context}")
            logger.info(f"DEBUG: Session keys after Emergency Fix: {list(session.keys())}")
            if 'exam_question_ids' in session:
                logger.info(f"DEBUG: exam_question_ids count: {len(session.get('exam_question_ids', []))}")
            if 'exam_category' in session:
                logger.info(f"DEBUG: exam_category value: '{session.get('exam_category')}'")'''
        
        # Find where Emergency Fix 17 ends to add post-processing debug
        post_fix17_location = None
        for i, line in enumerate(new_lines):
            if 'EARLY RETURN: If construction environment session detected' in line:
                # Find the end of this section (after the logger.info call)
                for j in range(i+1, min(i+10, len(new_lines))):
                    if 'logger.info("EMERGENCY FIX 17 IMPROVED: Construction environment session preserved' in new_lines[j]:
                        post_fix17_location = j + 1
                        break
        
        if post_fix17_location is not None:
            print(f"   Adding post-Emergency Fix debug logging at line {post_fix17_location + 1}")
            
            # Get indentation for post-fix debug logging
            reference_line = new_lines[post_fix17_location - 1]
            indentation = len(reference_line) - len(reference_line.lstrip())
            indent_str = ' ' * indentation
            
            # Apply proper indentation
            debug_lines = post_fix17_debug.strip().split('\n')
            indented_debug_lines = [indent_str + line.strip() if line.strip() else line for line in debug_lines]
            
            # Insert post-processing debug logging
            new_lines = new_lines[:post_fix17_location] + indented_debug_lines + [''] + new_lines[post_fix17_location:]
        
        # Write the enhanced content with debug logging
        new_content = '\n'.join(new_lines)
        
        print("3. Validating syntax...")
        try:
            compile(new_content, app_path, 'exec')
            print("   ✅ Syntax validation successful")
        except SyntaxError as e:
            print(f"   ❌ Syntax error detected: {e}")
            # Restore backup
            shutil.copy2(backup_path, app_path)
            print("   ✅ Backup restored")
            return False
        
        # Write the updated content
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("\n=== Emergency Fix 17 Debug Enhanced Summary ===")
        print("✅ Added comprehensive debug logging at exam() function entry")
        print("✅ Added debug logging before Emergency Fix 17 Improved execution")
        print("✅ Added debug logging after Emergency Fix 17 Improved processing")
        print("✅ Enhanced session state tracking")
        print("✅ Added category comparison debugging")
        
        return True
        
    except Exception as e:
        print(f"Debug enhancement failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    if add_debug_logging_to_emergency_fix_17():
        print("\n🎉 Emergency Fix 17 Debug Enhanced applied successfully!")
        print("🔍 Comprehensive debug logging added to track execution flow")
        print("📝 Ready for testing to understand why Emergency Fix 17 is not triggered")
        print("\n🔧 Next steps:")
        print("1. Run construction_env_department_complete_test.py")
        print("2. Check server logs for detailed debug information")
        print("3. Analyze why Emergency Fix 17 conditions are not met")
    else:
        print("\n❌ Emergency Fix 17 Debug Enhanced application failed")
        print("🔧 Manual intervention may be required")

if __name__ == "__main__":
    main()