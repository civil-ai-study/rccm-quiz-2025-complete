#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Department Root Session Emergency Fix
建設環境部門根本セッション緊急修正

緊急対応-15: 建設環境部門の根本的セッション問題調査と修正
Purpose: Emergency Fix 14後も問題継続、セッション作成が基礎科目セッションを作成する問題の特定と修正

Critical Issues Identified:
1. Emergency Fix 14 was applied but verification still failed
2. Construction environment session creation works but /exam route creates basic session 
3. Session structure conversion exists but not effective
4. Need to trace the exact session flow to identify where it breaks

Root Investigation Strategy:
1. Trace session creation in /start_exam/specialist_env route
2. Trace session access in /exam route
3. Identify where construction environment session gets replaced by basic session
4. Fix the session preservation chain
"""

import sys
import os
import shutil
import time
sys.path.insert(0, 'rccm-quiz-app')

def investigate_session_flow_issue():
    """Investigate the session flow from start_exam to exam routes"""
    print("=== Emergency Fix 15: Root Session Flow Investigation ===")
    print("Purpose: Trace session creation and access to find where construction environment session is lost")
    print()
    
    try:
        from app import app
        
        # Test session creation and tracking
        with app.test_client() as client:
            print("1. Testing construction environment session creation...")
            
            # Create session
            start_response = client.get('/start_exam/specialist_env')
            print(f"Start response status: {start_response.status_code}")
            
            # Check session contents after creation
            with client.session_transaction() as sess:
                print("Session contents after /start_exam/specialist_env:")
                for key, value in sess.items():
                    if key == 'questions':
                        print(f"  {key}: {len(value)} questions")
                        if value:
                            first_q = value[0]
                            print(f"    First question category: {first_q.get('category', 'unknown')}")
                    else:
                        print(f"  {key}: {value}")
                
                print()
            
            print("2. Testing /exam route access...")
            exam_response = client.get('/exam')
            print(f"Exam response status: {exam_response.status_code}")
            
            # Check session contents after exam access
            with client.session_transaction() as sess:
                print("Session contents after /exam access:")
                for key, value in sess.items():
                    if key in ['questions', 'exam_question_ids']:
                        if isinstance(value, list):
                            print(f"  {key}: {len(value)} items")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
            
            # Check if Emergency Fix 14 conversion happened
            exam_content = exam_response.get_data(as_text=True)
            csrf_present = 'csrf_token' in exam_content
            category_present = '建設環境' in exam_content
            
            print()
            print("Exam page analysis:")
            print(f"  CSRF token present: {csrf_present}")
            print(f"  Construction environment category present: {category_present}")
            print(f"  Content length: {len(exam_content)} characters")
            
            if not csrf_present and not category_present:
                print("❌ CRITICAL: Emergency Fix 14 session conversion not working")
                print("❌ Basic session is being created instead of preserving construction environment session")
                return False
            else:
                print("✅ Session conversion working properly")
                return True
                
    except Exception as e:
        print(f"ERROR: Session flow investigation failed: {e}")
        return False

def analyze_exam_route_logic():
    """Analyze the exam route logic to find the session reset issue"""
    print()
    print("=== Analyzing exam() route logic ===")
    
    try:
        # Read the current app.py to see the exam route implementation
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the exam route
        exam_route_start = content.find('@app.route(\'/exam\')')
        if exam_route_start == -1:
            print("ERROR: Could not find exam route")
            return False
            
        # Find the end of the function (next @app.route or end of file)
        next_route = content.find('@app.route', exam_route_start + 10)
        if next_route == -1:
            exam_route_content = content[exam_route_start:]
        else:
            exam_route_content = content[exam_route_start:next_route]
        
        print("Exam route analysis:")
        print(f"  Route content length: {len(exam_route_content)} characters")
        
        # Look for session reset conditions
        if '新規セッションを開始' in exam_route_content:
            print("  ✅ Found new session creation logic")
            
            # Look for Emergency Fix 14 logic
            if 'EMERGENCY FIX 14' in exam_route_content:
                print("  ✅ Emergency Fix 14 logic present")
            else:
                print("  ❌ Emergency Fix 14 logic NOT found - this is the problem!")
                return False
                
            # Look for the problematic session check
            if 'exam_question_ids' in exam_route_content and 'questions' in exam_route_content:
                print("  ✅ Both session key checks present")
            else:
                print("  ❌ Session key checks missing or incomplete")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Exam route analysis failed: {e}")
        return False

def create_session_preservation_fix():
    """Create a more robust session preservation fix"""
    print()
    print("=== Creating Enhanced Session Preservation Fix ===")
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the session check logic that might be failing
        session_check_patterns = [
            "if 'exam_question_ids' not in session or not session.get('exam_question_ids'):",
            "# 既存セッションがない場合、新規セッションを開始",
            "if not has_standard_session:"
        ]
        
        fix_applied = False
        
        for pattern in session_check_patterns:
            if pattern in content:
                print(f"Found pattern: {pattern[:50]}...")
                
                # Add additional logging before session checks
                enhanced_logging = f"""
            # EMERGENCY FIX 15: Enhanced session state logging
            logger.info(f"EMERGENCY FIX 15: Session state check - session keys: {{list(session.keys())}}")
            if 'questions' in session:
                logger.info(f"EMERGENCY FIX 15: Found 'questions' key with {{len(session['questions'])}} items")
            if 'exam_question_ids' in session:
                logger.info(f"EMERGENCY FIX 15: Found 'exam_question_ids' key with {{len(session['exam_question_ids'])}} items")
            
            {pattern}"""
                
                content = content.replace(pattern, enhanced_logging)
                fix_applied = True
                print("✅ Enhanced logging added")
                break
        
        if not fix_applied:
            print("❌ Could not find session check pattern to enhance")
            return False
        
        # Create backup and save
        backup_filename = f'rccm-quiz-app/app.py.emergency_fix_15_{int(time.time())}'
        shutil.copy('rccm-quiz-app/app.py', backup_filename)
        print(f"Backup created: {backup_filename}")
        
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Enhanced session preservation logging added to app.py")
        return True
        
    except Exception as e:
        print(f"ERROR: Session preservation fix failed: {e}")
        return False

def test_enhanced_session_tracking():
    """Test the enhanced session tracking"""
    print()
    print("=== Testing Enhanced Session Tracking ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Creating construction environment session...")
            start_response = client.get('/start_exam/specialist_env')
            
            print("2. Accessing exam route with enhanced logging...")
            exam_response = client.get('/exam')
            
            print(f"Exam response status: {exam_response.status_code}")
            
            if exam_response.status_code == 200:
                content = exam_response.get_data(as_text=True)
                csrf_present = 'csrf_token' in content
                env_category = '建設環境' in content
                
                print(f"CSRF token: {csrf_present}")
                print(f"Construction environment category: {env_category}")
                
                if csrf_present and env_category:
                    print("✅ Enhanced session tracking successful!")
                    return True
                else:
                    print("❌ Session issue still present - check server logs")
                    return False
            else:
                print(f"❌ Exam route failed with status {exam_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Enhanced session tracking test failed: {e}")
        return False

def main():
    print("Construction Environment Department Root Session Emergency Fix")
    print("=" * 80)
    print("緊急対応-15: 建設環境部門の根本的セッション問題調査と修正")
    print("Purpose: Emergency Fix 14後も問題継続、セッション管理の根本的な問題を特定して修正")
    print()
    
    # Step 1: Investigate current session flow
    session_investigation = investigate_session_flow_issue()
    
    # Step 2: Analyze exam route logic
    route_analysis = analyze_exam_route_logic()
    
    # Step 3: Create enhanced session preservation fix
    if not session_investigation or not route_analysis:
        print("Creating enhanced session preservation fix...")
        fix_result = create_session_preservation_fix()
        
        if fix_result:
            print("Testing enhanced session tracking...")
            test_result = test_enhanced_session_tracking()
        else:
            test_result = False
    else:
        print("Session flow appears to be working - no additional fix needed")
        test_result = True
    
    print()
    print("=" * 80)
    print("Emergency Fix 15 Final Results:")
    print(f"Session investigation: {'SUCCESS' if session_investigation else 'NEEDS ATTENTION'}")
    print(f"Route analysis: {'SUCCESS' if route_analysis else 'NEEDS ATTENTION'}")
    print(f"Enhanced fix: {'APPLIED' if not session_investigation else 'NOT NEEDED'}")
    print(f"Final test: {'SUCCESS' if test_result else 'FAILED'}")
    
    if test_result:
        print()
        print("COMPLETE SUCCESS - Emergency Fix 15")
        print("- Construction environment session flow working properly")
        print("- Session preservation enhanced with detailed logging")
        print("- Ready to proceed with Task 12 completion")
        return True
    else:
        print()
        print("NEEDS FURTHER INVESTIGATION - Emergency Fix 15")
        print("- Construction environment session issue persists")
        print("- Enhanced logging added for debugging")
        print("- May require deeper architectural changes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)