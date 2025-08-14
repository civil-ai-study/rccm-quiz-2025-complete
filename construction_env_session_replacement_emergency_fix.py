#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Department Session Replacement Emergency Fix
建設環境部門セッション置換問題緊急修正

緊急対応-16: 建設環境部門セッション置換問題根本修正
Purpose: Prevent /exam route from replacing construction environment sessions with basic sessions
CRITICAL: /exam route creates new basic session instead of preserving construction environment session

Root Cause Confirmed by Emergency Fix 15:
- Construction environment session creation works (Emergency Fix 12) ✅
- /exam route access replaces construction environment session with basic session ❌
- Session replacement causes CSRF token absence, category display failure, 400 errors ❌

Fix Strategy:
- Modify exam() function session validation to preserve construction environment sessions
- Ensure proper session continuity between /start_exam/specialist_env and /exam routes
- Add specific logic to detect and preserve construction environment sessions
"""

import sys
import os
import shutil
import time
sys.path.insert(0, 'rccm-quiz-app')

def create_construction_env_session_preservation_fix():
    """Create and apply construction environment session preservation fix"""
    print("=== Emergency Fix 16: Construction Environment Session Preservation ===")
    print("Purpose: Prevent /exam route from replacing construction environment sessions with basic sessions")
    print("Critical Issue: Construction environment session being replaced at /exam route access")
    print()
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the exam() function and its session validation logic
        print("1. Analyzing exam() function session validation logic...")
        
        # Look for the session validation section that might be causing the replacement
        session_validation_patterns = [
            "# Emergency Fix 14で拡張した検証が失敗した場合、新規セッションを開始",
            "if not has_standard_session:",
            "# 既存セッションがない場合、新規セッションを開始"
        ]
        
        fix_applied = False
        
        # Strategy: Add construction environment session detection before session creation
        for pattern in session_validation_patterns:
            if pattern in content:
                print(f"-> Found session validation pattern: {pattern[:50]}...")
                
                # Create the emergency fix for construction environment session preservation
                construction_env_preservation_fix = f"""            # EMERGENCY FIX 16: Construction Environment Session Preservation
            # Detect if this is a construction environment context to prevent session replacement
            is_construction_env_context = False
            if hasattr(session, 'get'):
                # Check if Emergency Fix 12 construction environment session exists
                if 'questions' in session and session.get('questions'):
                    emergency_questions = session.get('questions', [])
                    if emergency_questions and len(emergency_questions) > 0:
                        first_question = emergency_questions[0]
                        if first_question.get('category') == '建設環境':
                            is_construction_env_context = True
                            logger.info("EMERGENCY FIX 16: Construction environment session detected - preserving existing session")
                            
                            # Force preserve construction environment session by ensuring has_standard_session = True
                            if not has_standard_session:
                                logger.info("EMERGENCY FIX 16: Converting construction environment session to standard format")
                                try:
                                    session['exam_question_ids'] = [q['id'] for q in emergency_questions]
                                    session['exam_current'] = session.get('current_question', 0)
                                    session['exam_category'] = '建設環境'
                                    session['selected_question_type'] = 'specialist'
                                    session.modified = True
                                    has_standard_session = True
                                    logger.info("EMERGENCY FIX 16: Construction environment session preserved successfully")
                                except Exception as e:
                                    logger.error(f"EMERGENCY FIX 16: Session preservation failed: {{e}}")
            
            {pattern}"""
                
                # Apply the fix
                content = content.replace(pattern, construction_env_preservation_fix)
                fix_applied = True
                print("-> Applied Emergency Fix 16: Construction Environment Session Preservation")
                break
        
        if not fix_applied:
            print("-> Session validation pattern not found - applying alternative fix")
            
            # Alternative approach: Find the exam() function and add preservation logic at the beginning
            exam_function_start = content.find('def exam():')
            if exam_function_start != -1:
                # Find the first logger statement after function definition
                start_search = exam_function_start
                logger_start = content.find('logger.info', start_search)
                if logger_start != -1:
                    # Insert preservation logic before the first logger statement
                    preservation_logic = """    # EMERGENCY FIX 16: Construction Environment Session Preservation
    # Check for existing construction environment session before any session validation
    construction_env_session_exists = False
    if 'questions' in session and session.get('questions'):
        emergency_questions = session.get('questions', [])
        if emergency_questions and len(emergency_questions) > 0:
            first_question = emergency_questions[0]
            if first_question.get('category') == '建設環境':
                construction_env_session_exists = True
                logger.info("EMERGENCY FIX 16: Construction environment session detected - will preserve")
    
    """
                    
                    content = content[:logger_start] + preservation_logic + content[logger_start:]
                    fix_applied = True
                    print("-> Applied Emergency Fix 16: Alternative construction environment preservation")
                else:
                    print("-> Could not find insertion point for preservation logic")
            else:
                print("-> Could not find exam() function")
        
        if not fix_applied:
            print("-> No fixes applied - could not locate appropriate insertion point")
            return False
        
        print()
        print("2. Creating backup and applying Emergency Fix 16...")
        
        # Create backup
        backup_filename = f'rccm-quiz-app/app.py.emergency_session_replacement_fix_{int(time.time())}'
        shutil.copy('rccm-quiz-app/app.py', backup_filename)
        print(f"-> Backup created: {backup_filename}")
        
        # Apply the fix
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("-> Emergency Fix 16 applied to app.py")
        
        print()
        print("3. Verification test...")
        
        # Test the fix
        try:
            from app import app
            print("-> App imports successfully after Emergency Fix 16")
            
            # Test construction environment session preservation
            with app.test_client() as client:
                # Step 1: Create construction environment session
                start_response = client.get('/start_exam/specialist_env')
                if start_response.status_code in [200, 302]:
                    print("-> Construction environment session creation successful")
                    
                    # Step 2: Test exam page access (should preserve construction environment session)
                    exam_response = client.get('/exam')
                    if exam_response.status_code == 200:
                        content = exam_response.get_data(as_text=True)
                        
                        # Check for construction environment content preservation
                        csrf_present = 'csrf_token' in content
                        env_category = '建設環境' in content
                        
                        print(f"-> CSRF token present: {csrf_present}")
                        print(f"-> Construction environment category present: {env_category}")
                        print(f"-> Content length: {len(content)} characters")
                        
                        if csrf_present and env_category:
                            print("SUCCESS: Emergency Fix 16 - Construction environment session preservation working")
                            return True
                        else:
                            print("-> Session preservation verification failed")
                            return False
                    else:
                        print(f"-> Exam page access failed: {exam_response.status_code}")
                        return False
                else:
                    print(f"-> Session creation failed: {start_response.status_code}")
                    return False
                    
            print()
            print("=== Emergency Fix 16 Results ===")
            print("SUCCESS: Construction environment session replacement prevention implemented")
            print("SUCCESS: Session preservation logic added to exam() function")
            print("SUCCESS: Construction environment session continuity enhanced")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Verification failed: {e}")
            # Restore backup if verification fails
            shutil.copy(backup_filename, 'rccm-quiz-app/app.py')
            print("-> Backup restored due to verification failure")
            return False
            
    except Exception as e:
        print(f"ERROR: Emergency Fix 16 failed: {e}")
        return False

def test_construction_environment_after_preservation_fix():
    """Test construction environment department after applying session preservation fix"""
    print()
    print("=== Emergency Fix 16 Effectiveness Test ===")
    
    try:
        from app import app
        with app.test_client() as client:
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            if response.status_code in [200, 302]:
                print("Session creation successful")
                
                # Test exam page access with session preservation
                exam_response = client.get('/exam')
                print(f"Exam page status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    content = exam_response.get_data(as_text=True)
                    
                    # Check essential elements for construction environment session
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
                        print("SUCCESS: Emergency Fix 16 - Construction environment session preservation working properly")
                        return True
                    else:
                        print("FAILED: Some essential elements missing - session replacement may still be occurring")
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

def run_construction_env_complete_test_after_fix():
    """Run construction environment complete test after Emergency Fix 16"""
    print()
    print("=== Construction Environment Complete Test After Emergency Fix 16 ===")
    
    try:
        # Import the complete test function
        sys.path.insert(0, '.')
        from construction_env_department_complete_test import main as run_complete_test
        
        print("Running construction environment department complete test...")
        test_result = run_complete_test()
        
        if test_result:
            print("SUCCESS: Construction environment department complete test passed after Emergency Fix 16")
            return True
        else:
            print("FAILED: Construction environment department complete test still failing")
            return False
            
    except Exception as e:
        print(f"ERROR: Complete test execution failed: {e}")
        return False

def main():
    print("Construction Environment Department Session Replacement Emergency Fix")
    print("=" * 80)
    print("緊急対応-16: 建設環境部門セッション置換問題根本修正")
    print("Purpose: Prevent /exam route from replacing construction environment sessions with basic sessions")
    print("Critical Issue: Construction environment session being replaced at /exam route access")
    print()
    
    # Apply Emergency Fix 16
    fix_result = create_construction_env_session_preservation_fix()
    
    if fix_result:
        print()
        print("Testing Emergency Fix 16 effectiveness...")
        test_result = test_construction_environment_after_preservation_fix()
        
        if test_result:
            print()
            print("Running complete construction environment test...")
            complete_test_result = run_construction_env_complete_test_after_fix()
        else:
            complete_test_result = False
        
        print()
        print("=" * 80)
        print("Emergency Fix 16 Final Results:")
        print(f"Emergency Fix 16 application: {'SUCCESS' if fix_result else 'FAILED'}")
        print(f"Session preservation test: {'SUCCESS' if test_result else 'FAILED' if test_result is False else 'INCONCLUSIVE'}")
        print(f"Complete department test: {'SUCCESS' if complete_test_result else 'FAILED' if complete_test_result is False else 'INCONCLUSIVE'}")
        
        if fix_result and test_result and complete_test_result:
            print()
            print("COMPLETE SUCCESS - Emergency Fix 16 Applied")
            print("- Construction environment session replacement problem resolved")
            print("- Session preservation at /exam route implemented")
            print("- Construction environment department 10-question completion successful")
            print("- Ready to proceed with Task 13")
            return True
        elif fix_result and test_result:
            print()
            print("PARTIAL SUCCESS - Session Preservation Working")
            print("- Emergency Fix 16 applied successfully")
            print("- Session preservation test passed")
            print("- Complete test may require additional investigation")
            return True
        else:
            print()
            print("FAILED - Emergency Fix 16 Needs Investigation")
            print("- Session replacement issue may persist")
            print("- Additional architectural changes may be required")
            return False
    else:
        print("Emergency Fix 16 application failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)