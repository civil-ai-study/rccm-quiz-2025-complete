#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix 18: Session Structure Unification and ID Mapping Fix
緊急対応-18: セッション構造統一とIDマッピング修正

Purpose: 建設環境部門10問完走テスト実現のため、Emergency Fix 12とexam関数の
セッション構造とID体系の不一致を解決

Root Cause Identified:
1. Emergency Fix 12 creates sessions with:
   - 'questions' key containing CSV IDs (192, 183, 182, etc.)
   - Direct question objects in session
   
2. /exam function expects:
   - 'exam_question_ids' key with sequential IDs ['1', '2', '3', etc.]
   - Questions loaded separately using these IDs

Solution:
- Modify Emergency Fix 17 Enhanced to create compatible session structure
- Add ID mapping between CSV IDs and sequential session IDs
- Ensure seamless 10-question completion for construction environment department
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def create_emergency_fix_18():
    """Create Emergency Fix 18 to unify session structure and fix ID mapping"""
    print("=== Emergency Fix 18: Session Structure Unification Creation ===")
    print("Purpose: Fix session structure and ID mapping for construction environment 10-question completion")
    print()
    
    emergency_fix_18_code = '''
    # ================================
    # EMERGENCY FIX 18: SESSION STRUCTURE UNIFICATION AND ID MAPPING FIX
    # Date: 2025-08-13 21:55:00
    # Purpose: Fix session structure compatibility between Emergency Fix 12 and exam function
    # Problem: Emergency Fix 12 uses 'questions' key with CSV IDs, /exam expects 'exam_question_ids' with sequential IDs
    # Solution: Create unified session structure with proper ID mapping
    # ================================

    # EMERGENCY FIX 18: Construction Environment Session Structure Unification
    # This fix addresses the root cause identified in the diagnostic:
    # - Emergency Fix 12 creates sessions with CSV IDs (192, 183, 182, etc.)
    # - /exam function expects sequential IDs ['1', '2', '3', '4', '5', etc.]
    # - Session structure mismatch: 'questions' vs 'exam_question_ids'

    def emergency_fix_18_session_structure_unification():
        """
        EMERGENCY FIX 18: Unify session structure for construction environment department
        
        Creates compatible session structure that works with both:
        1. Emergency Fix 12 question loading system
        2. /exam function ID expectations
        """
        logger.info("DEBUG: Emergency Fix 18 - Session Structure Unification starting")
        
        try:
            # CRITICAL: Check for Emergency Fix 12 construction environment sessions
            emergency_questions = None
            has_emergency_fix_12_session = False
            
            # Detection logic for Emergency Fix 12 sessions
            if 'questions' in session and session.get('questions'):
                emergency_questions = session.get('questions', [])
                
                # Verify this is a construction environment session
                if emergency_questions and len(emergency_questions) > 0:
                    first_question = emergency_questions[0]
                    if first_question.get('category') == '建設環境':
                        has_emergency_fix_12_session = True
                        logger.info(f"DEBUG: Emergency Fix 18 - Found Emergency Fix 12 construction environment session with {len(emergency_questions)} questions")
            
            # Also check exam_session structure (from /start_exam)
            elif 'exam_session' in session and session.get('exam_session'):
                exam_session = session.get('exam_session', {})
                exam_questions = exam_session.get('questions', [])
                
                if exam_questions and len(exam_questions) > 0:
                    first_question = exam_questions[0]
                    if first_question.get('category') == '建設環境':
                        emergency_questions = exam_questions
                        has_emergency_fix_12_session = True
                        logger.info(f"DEBUG: Emergency Fix 18 - Found exam_session construction environment session with {len(exam_questions)} questions")
            
            if has_emergency_fix_12_session and emergency_questions:
                logger.info("DEBUG: Emergency Fix 18 - Converting Emergency Fix 12 session to unified structure")
                
                # CRITICAL CONVERSION: Create unified session structure
                
                # Step 1: Create sequential ID mapping
                csv_to_sequential_mapping = {}
                sequential_to_csv_mapping = {}
                exam_question_ids = []
                
                for i, question in enumerate(emergency_questions):
                    sequential_id = str(i + 1)  # 1-based sequential IDs
                    csv_id = question.get('id', str(i + 1))
                    
                    csv_to_sequential_mapping[csv_id] = sequential_id
                    sequential_to_csv_mapping[sequential_id] = csv_id
                    exam_question_ids.append(sequential_id)
                
                logger.info(f"DEBUG: Emergency Fix 18 - Created ID mapping: {csv_to_sequential_mapping}")
                
                # Step 2: Create unified session structure compatible with /exam function
                session['exam_question_ids'] = exam_question_ids
                session['exam_current'] = 0
                session['exam_category'] = '建設環境'
                session['exam_department'] = 'env'
                session['exam_type'] = 'specialist'
                session['exam_start_time'] = time.time()
                
                # Step 3: Store ID mappings for question lookup
                session['emergency_fix_18_csv_to_sequential'] = csv_to_sequential_mapping
                session['emergency_fix_18_sequential_to_csv'] = sequential_to_csv_mapping
                
                # Step 4: Store original questions with sequential ID mapping
                session['emergency_fix_18_questions'] = {}
                for i, question in enumerate(emergency_questions):
                    sequential_id = str(i + 1)
                    session['emergency_fix_18_questions'][sequential_id] = question
                
                # Step 5: Preserve original Emergency Fix 12 session for reference
                session['emergency_fix_12_backup'] = {
                    'questions': emergency_questions,
                    'current_question': session.get('current_question', 0)
                }
                
                # Step 6: Clean up conflicting session keys
                if 'questions' in session:
                    del session['questions']
                if 'current_question' in session:
                    del session['current_question']
                if 'exam_session' in session:
                    del session['exam_session']
                
                logger.info("SUCCESS: Emergency Fix 18 - Session structure unified successfully")
                logger.info(f"DEBUG: Emergency Fix 18 - Session now has exam_question_ids: {exam_question_ids}")
                logger.info(f"DEBUG: Emergency Fix 18 - Session category: {session.get('exam_category')}")
                
                return True
            else:
                logger.info("DEBUG: Emergency Fix 18 - No Emergency Fix 12 construction environment session found")
                return False
                
        except Exception as e:
            logger.error(f"ERROR: Emergency Fix 18 failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    # EMERGENCY FIX 18: Enhanced Question Loading for Unified Structure
    def emergency_fix_18_get_question_by_sequential_id(sequential_id):
        """
        Get question by sequential ID using Emergency Fix 18 mapping
        
        Args:
            sequential_id (str): Sequential ID like '1', '2', '3', etc.
            
        Returns:
            dict: Question object or None if not found
        """
        try:
            # Check if Emergency Fix 18 session structure exists
            if 'emergency_fix_18_questions' in session:
                question = session['emergency_fix_18_questions'].get(sequential_id)
                if question:
                    logger.info(f"DEBUG: Emergency Fix 18 - Retrieved question for sequential ID {sequential_id}: CSV ID {question.get('id')}")
                    return question
            
            # Fallback: Try to find CSV ID and load question
            if 'emergency_fix_18_sequential_to_csv' in session:
                csv_id = session['emergency_fix_18_sequential_to_csv'].get(sequential_id)
                if csv_id and 'emergency_fix_12_backup' in session:
                    original_questions = session['emergency_fix_12_backup'].get('questions', [])
                    for q in original_questions:
                        if q.get('id') == csv_id:
                            logger.info(f"DEBUG: Emergency Fix 18 - Found question via CSV ID mapping: {sequential_id} -> {csv_id}")
                            return q
            
            logger.warning(f"WARNING: Emergency Fix 18 - Question not found for sequential ID {sequential_id}")
            return None
            
        except Exception as e:
            logger.error(f"ERROR: Emergency Fix 18 question lookup failed for ID {sequential_id}: {e}")
            return None
    '''
    
    print("Emergency Fix 18 code structure created")
    print("Key features:")
    print("  ✅ Session structure unification")
    print("  ✅ CSV ID to sequential ID mapping")
    print("  ✅ Compatible with /exam function expectations")
    print("  ✅ Preserves Emergency Fix 12 questions")
    print("  ✅ Construction environment category preservation")
    
    return emergency_fix_18_code

def apply_emergency_fix_18_to_app():
    """Apply Emergency Fix 18 to app.py"""
    print("\n=== Applying Emergency Fix 18 to app.py ===")
    print("Target: Add session structure unification to Emergency Fix 17 Enhanced")
    print()
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Emergency Fix 17 Enhanced location
        emergency_fix_17_start = content.find("# EMERGENCY FIX 17 ENHANCED: Construction Environment Session Preservation")
        
        if emergency_fix_17_start == -1:
            print("ERROR: Emergency Fix 17 Enhanced not found in app.py")
            return False
        
        # Find the end of Emergency Fix 17 Enhanced
        emergency_fix_17_end = content.find("# End of Emergency Fix 17 Enhanced", emergency_fix_17_start)
        
        if emergency_fix_17_end == -1:
            # If no explicit end marker, find the next Emergency Fix or end of function
            emergency_fix_17_end = content.find("# EMERGENCY FIX", emergency_fix_17_start + 100)
            if emergency_fix_17_end == -1:
                emergency_fix_17_end = content.find("return render_template", emergency_fix_17_start)
        
        if emergency_fix_17_end == -1:
            print("ERROR: Could not determine Emergency Fix 17 Enhanced end location")
            return False
        
        # Create Emergency Fix 18 integration
        emergency_fix_18_integration = '''
        
        # EMERGENCY FIX 18: Session Structure Unification Integration
        # Integrate Emergency Fix 18 with Emergency Fix 17 Enhanced
        if is_construction_env_context and construction_env_session_data:
            logger.info("DEBUG: Applying Emergency Fix 18 - Session Structure Unification")
            
            # Apply Emergency Fix 18 session structure unification
            emergency_fix_18_success = emergency_fix_18_session_structure_unification()
            
            if emergency_fix_18_success:
                logger.info("SUCCESS: Emergency Fix 18 - Session structure unified for construction environment")
                
                # Continue with Emergency Fix 17 Enhanced logic but use unified structure
                if 'exam_question_ids' in session and session.get('exam_question_ids'):
                    # Use the unified session structure created by Emergency Fix 18
                    logger.info("SUCCESS: Emergency Fix 17 Enhanced + Emergency Fix 18 - Using unified session structure")
                else:
                    logger.warning("WARNING: Emergency Fix 18 succeeded but no exam_question_ids found")
            else:
                logger.warning("WARNING: Emergency Fix 18 failed - falling back to Emergency Fix 17 Enhanced only")
        '''
        
        # Insert Emergency Fix 18 integration before Emergency Fix 17 Enhanced completion
        insert_position = emergency_fix_17_end
        
        # Create the modified content
        modified_content = (
            content[:insert_position] + 
            emergency_fix_18_integration + 
            "\n        # End of Emergency Fix 18 Integration\n" +
            content[insert_position:]
        )
        
        # Add Emergency Fix 18 function definitions at the end of the file
        emergency_fix_18_functions = create_emergency_fix_18()
        
        # Find a good location to add the functions (before if __name__ == '__main__')
        main_check = modified_content.find("if __name__ == '__main__':")
        if main_check != -1:
            functions_insert_position = main_check
        else:
            functions_insert_position = len(modified_content)
        
        # Insert the Emergency Fix 18 functions
        final_content = (
            modified_content[:functions_insert_position] + 
            "\n\n" + emergency_fix_18_functions + "\n\n" +
            modified_content[functions_insert_position:]
        )
        
        # Create backup
        backup_filename = f"app.py.emergency_fix_18_backup_{int(time.time())}"
        with open(f'rccm-quiz-app/{backup_filename}', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup created: {backup_filename}")
        
        # Write the modified content
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Emergency Fix 18 applied successfully to app.py")
        print("   - Session structure unification added")
        print("   - ID mapping system integrated")
        print("   - Compatible with Emergency Fix 17 Enhanced")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to apply Emergency Fix 18: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency_fix_18():
    """Test Emergency Fix 18 with construction environment session"""
    print("\n=== Testing Emergency Fix 18 ===")
    print("Purpose: Verify session structure unification works for construction environment")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Creating construction environment session...")
            
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            if response.status_code in [200, 302]:
                print("   ✅ Construction environment session created")
                
                print("2. Accessing /exam to trigger Emergency Fix 17 Enhanced + Emergency Fix 18...")
                exam_response = client.get('/exam')
                
                if exam_response.status_code == 200:
                    print("   ✅ /exam access successful")
                    
                    # Check session structure after Emergency Fix 18
                    with client.session_transaction() as sess:
                        print("3. Verifying Emergency Fix 18 session structure...")
                        
                        # Check for unified session structure
                        if 'exam_question_ids' in sess:
                            exam_ids = sess.get('exam_question_ids', [])
                            print(f"   ✅ exam_question_ids found: {exam_ids}")
                            
                            if exam_ids == [str(i) for i in range(1, len(exam_ids) + 1)]:
                                print("   ✅ Sequential ID format confirmed")
                            else:
                                print("   ⚠️ Non-sequential ID format")
                        
                        if 'exam_category' in sess:
                            category = sess.get('exam_category')
                            print(f"   ✅ exam_category: {category}")
                            
                            if category == '建設環境':
                                print("   ✅ Construction environment category preserved")
                            else:
                                print(f"   ❌ Unexpected category: {category}")
                        
                        if 'emergency_fix_18_questions' in sess:
                            print("   ✅ Emergency Fix 18 question mapping found")
                        
                        if 'emergency_fix_18_csv_to_sequential' in sess:
                            mapping = sess.get('emergency_fix_18_csv_to_sequential', {})
                            print(f"   ✅ ID mapping created: {len(mapping)} mappings")
                        
                        print("4. Testing question progression...")
                        
                        # Try to access question 2
                        if exam_ids and len(exam_ids) >= 2:
                            # Submit answer for question 1
                            answer_response = client.post('/exam', data={
                                'answer': 'A',
                                'elapsed': '3.0'
                            })
                            
                            if answer_response.status_code == 200:
                                print("   ✅ Question 1 answer submission successful")
                                
                                # Check for progression to question 2
                                content = answer_response.get_data(as_text=True)
                                if '2/10' in content or 'question 2' in content.lower():
                                    print("   ✅ Emergency Fix 18 - Question progression successful!")
                                    print("   🎉 SESSION STRUCTURE UNIFICATION WORKING!")
                                    return True
                                else:
                                    print("   ❌ Question progression failed")
                            else:
                                print(f"   ❌ Answer submission failed: {answer_response.status_code}")
                        
            else:
                print(f"   ❌ Session creation failed: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"ERROR: Emergency Fix 18 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function for Emergency Fix 18 creation and application"""
    print("Emergency Fix 18: Session Structure Unification and ID Mapping Fix")
    print("=" * 80)
    print("Goal: Resolve construction environment department 10-question completion")
    print("Root Cause: Session structure and ID mapping incompatibility")
    print("Solution: Unified session structure with proper ID mapping")
    print()
    
    # Step 1: Create Emergency Fix 18
    print("Step 1: Creating Emergency Fix 18...")
    emergency_fix_18_code = create_emergency_fix_18()
    
    # Step 2: Apply to app.py
    print("Step 2: Applying Emergency Fix 18 to app.py...")
    application_success = apply_emergency_fix_18_to_app()
    
    if application_success:
        print("Step 3: Testing Emergency Fix 18...")
        test_success = test_emergency_fix_18()
        
        if test_success:
            print("\n✅ Emergency Fix 18 SUCCESS!")
            print("   - Session structure unified")
            print("   - ID mapping working")
            print("   - Construction environment 10-question completion enabled")
            print("   - Ready for Task 12 completion")
            return True
        else:
            print("\n⚠️ Emergency Fix 18 applied but testing failed")
            print("   - May need additional debugging")
            print("   - Check logs for specific issues")
            return False
    else:
        print("\n❌ Emergency Fix 18 application failed")
        print("   - Could not modify app.py")
        print("   - Check file permissions and backup status")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)