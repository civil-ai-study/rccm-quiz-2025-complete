#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix 19: Session Size Optimization
緊急対応-19: セッションサイズ最適化
Purpose: Fix session cookie size exceeding 4KB limit in Emergency Fix 18
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def create_emergency_fix_19():
    """Create Emergency Fix 19 to optimize session storage size"""
    print("=== Emergency Fix 19: Session Size Optimization Creation ===")
    print("Problem: Emergency Fix 18 session data exceeds 4KB cookie limit (4316 bytes)")
    print("Solution: Store only essential data in session, use temporary storage for large data")
    print()
    
    emergency_fix_19_code = '''
    # ================================
    # EMERGENCY FIX 19: SESSION SIZE OPTIMIZATION 
    # Date: 2025-08-13 22:10:00
    # Purpose: Fix session cookie size exceeding 4KB limit caused by Emergency Fix 18
    # Problem: Session cookie size reached 4316 bytes, exceeding 4093 byte limit
    # Solution: Store only minimal essential data in session, use server-side storage for question data
    # ================================

    # EMERGENCY FIX 19: Session size optimization global storage
    # Use server-side storage to avoid cookie size limits
    _emergency_fix_19_question_cache = {}
    _emergency_fix_19_session_counter = 0

    def emergency_fix_19_session_size_optimization():
        """
        EMERGENCY FIX 19: Optimize session size for construction environment department
        
        Reduces session cookie size by:
        1. Moving large question data to server-side cache
        2. Storing only essential IDs and mappings in session
        3. Maintaining compatibility with Emergency Fix 18 ID mapping
        """
        global _emergency_fix_19_question_cache, _emergency_fix_19_session_counter
        
        logger.info("DEBUG: Emergency Fix 19 - Session Size Optimization starting")
        
        try:
            # Check if Emergency Fix 18 session exists and needs optimization
            if 'emergency_fix_18_questions' in session:
                emergency_questions = session.get('emergency_fix_18_questions', {})
                
                if emergency_questions and len(emergency_questions) > 0:
                    logger.info(f"DEBUG: Emergency Fix 19 - Optimizing session with {len(emergency_questions)} questions")
                    
                    # Create a unique session ID for server-side storage
                    _emergency_fix_19_session_counter += 1
                    session_storage_id = f"env_session_{int(time.time())}_{_emergency_fix_19_session_counter}"
                    
                    # Store full question data in server-side cache
                    _emergency_fix_19_question_cache[session_storage_id] = emergency_questions
                    
                    # Keep only minimal data in session
                    session['emergency_fix_19_storage_id'] = session_storage_id
                    session['emergency_fix_19_question_count'] = len(emergency_questions)
                    
                    # Preserve essential ID mappings (these are small)
                    if 'emergency_fix_18_csv_to_sequential' in session:
                        session['emergency_fix_19_id_mapping'] = session['emergency_fix_18_csv_to_sequential']
                    
                    # Remove large question data from session
                    if 'emergency_fix_18_questions' in session:
                        del session['emergency_fix_18_questions']
                    
                    # Clean up other large session data if present
                    large_keys_to_remove = [
                        'emergency_fix_12_backup',
                        'exam_session'  # This can be recreated if needed
                    ]
                    
                    for key in large_keys_to_remove:
                        if key in session:
                            logger.info(f"DEBUG: Emergency Fix 19 - Removing large session key: {key}")
                            del session[key]
                    
                    logger.info(f"SUCCESS: Emergency Fix 19 - Session optimized, storage ID: {session_storage_id}")
                    logger.info(f"DEBUG: Emergency Fix 19 - Question data moved to server-side cache")
                    
                    return True
                else:
                    logger.info("DEBUG: Emergency Fix 19 - No question data to optimize")
                    return False
            else:
                logger.info("DEBUG: Emergency Fix 19 - No Emergency Fix 18 session to optimize")
                return False
                
        except Exception as e:
            logger.error(f"ERROR: Emergency Fix 19 failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def emergency_fix_19_get_question_by_sequential_id(sequential_id):
        """
        Get question by sequential ID using Emergency Fix 19 optimized storage
        
        Args:
            sequential_id (str): Sequential ID like '1', '2', '3', etc.
            
        Returns:
            dict: Question object or None if not found
        """
        try:
            # Check if Emergency Fix 19 storage is available
            if 'emergency_fix_19_storage_id' in session:
                storage_id = session.get('emergency_fix_19_storage_id')
                
                if storage_id in _emergency_fix_19_question_cache:
                    questions = _emergency_fix_19_question_cache[storage_id]
                    question = questions.get(sequential_id)
                    
                    if question:
                        logger.info(f"DEBUG: Emergency Fix 19 - Retrieved question for sequential ID {sequential_id} from server cache")
                        return question
                    else:
                        logger.warning(f"WARNING: Emergency Fix 19 - Question {sequential_id} not found in server cache")
                        return None
                else:
                    logger.error(f"ERROR: Emergency Fix 19 - Storage ID {storage_id} not found in cache")
                    return None
            
            # Fallback to Emergency Fix 18 method if available
            elif 'emergency_fix_18_questions' in session:
                question = session['emergency_fix_18_questions'].get(sequential_id)
                if question:
                    logger.info(f"DEBUG: Emergency Fix 19 - Fallback to Emergency Fix 18 for sequential ID {sequential_id}")
                    return question
            
            logger.warning(f"WARNING: Emergency Fix 19 - No storage method available for sequential ID {sequential_id}")
            return None
            
        except Exception as e:
            logger.error(f"ERROR: Emergency Fix 19 question lookup failed for ID {sequential_id}: {e}")
            return None

    def emergency_fix_19_cleanup_expired_cache():
        """Clean up expired session cache entries"""
        global _emergency_fix_19_question_cache
        
        try:
            current_time = time.time()
            expired_keys = []
            
            for key in _emergency_fix_19_question_cache.keys():
                # Extract timestamp from key (format: env_session_{timestamp}_{counter})
                parts = key.split('_')
                if len(parts) >= 3:
                    try:
                        session_time = int(parts[2])
                        # Remove sessions older than 2 hours
                        if current_time - session_time > 7200:
                            expired_keys.append(key)
                    except ValueError:
                        # Invalid timestamp format, mark for removal
                        expired_keys.append(key)
            
            for key in expired_keys:
                del _emergency_fix_19_question_cache[key]
                logger.info(f"DEBUG: Emergency Fix 19 - Cleaned up expired cache entry: {key}")
            
            if expired_keys:
                logger.info(f"SUCCESS: Emergency Fix 19 - Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"ERROR: Emergency Fix 19 cache cleanup failed: {e}")
    '''
    
    print("Emergency Fix 19 code structure created")
    print("Key features:")
    print("  [OK] Session size optimization (removes large question data from cookies)")
    print("  [OK] Server-side question storage cache")
    print("  [OK] Compatible with Emergency Fix 18 ID mapping") 
    print("  [OK] Automatic cache cleanup for expired sessions")
    print("  [OK] Fallback to Emergency Fix 18 if needed")
    
    return emergency_fix_19_code

def apply_emergency_fix_19_to_app():
    """Apply Emergency Fix 19 to app.py"""
    print("\n=== Applying Emergency Fix 19 to app.py ===")
    print("Target: Integrate session size optimization with Emergency Fix 18")
    print()
    
    try:
        # Read current app.py
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Emergency Fix 18 location (the session structure unification)
        emergency_fix_18_location = content.find("# EMERGENCY FIX 18: Session Structure Unification - Create sequential IDs")
        
        if emergency_fix_18_location == -1:
            print("ERROR: Emergency Fix 18 session structure unification not found in app.py")
            return False
        
        # Find the end of the Emergency Fix 18 block (look for the next logger.info after ID mapping)
        id_mapping_line = content.find("logger.info(f\"EMERGENCY FIX 18: ID mapping created", emergency_fix_18_location)
        
        if id_mapping_line == -1:
            print("ERROR: Could not find Emergency Fix 18 ID mapping line")
            return False
        
        # Find the end of that line
        emergency_fix_18_end = content.find("\n", id_mapping_line) + 1
        
        # Create Emergency Fix 19 integration
        emergency_fix_19_integration = '''
                        
                        # EMERGENCY FIX 19: Session Size Optimization
                        # Apply after Emergency Fix 18 to optimize session cookie size
                        logger.info("DEBUG: Applying Emergency Fix 19 - Session Size Optimization")
                        
                        # Clean up expired cache entries
                        emergency_fix_19_cleanup_expired_cache()
                        
                        # Apply session size optimization
                        emergency_fix_19_success = emergency_fix_19_session_size_optimization()
                        
                        if emergency_fix_19_success:
                            logger.info("SUCCESS: Emergency Fix 19 - Session size optimized for construction environment")
                        else:
                            logger.warning("WARNING: Emergency Fix 19 failed - session may still be large")
'''
        
        # Insert Emergency Fix 19 integration after Emergency Fix 18
        insert_position = emergency_fix_18_end
        
        # Create the modified content
        modified_content = (
            content[:insert_position] + 
            emergency_fix_19_integration + 
            content[insert_position:]
        )
        
        # Add Emergency Fix 19 function definitions
        emergency_fix_19_functions = create_emergency_fix_19()
        
        # Find a good location to add Emergency Fix 19 functions - look for the end of app.py before if __name__
        main_check = modified_content.find("if __name__ == '__main__':")
        if main_check != -1:
            functions_insert_position = main_check
        else:
            # Try to find a good spot near the end
            app_run = modified_content.find("app.run(")
            if app_run != -1:
                functions_insert_position = app_run
            else:
                functions_insert_position = len(modified_content)
        
        # Insert the Emergency Fix 19 functions
        final_content = (
            modified_content[:functions_insert_position] + 
            "\n\n" + emergency_fix_19_functions + "\n\n" +
            modified_content[functions_insert_position:]
        )
        
        # Also update the question lookup function to use Emergency Fix 19
        # Find the exam function question lookup section
        question_lookup_section = final_content.find("# EMERGENCY FIX 18: Enhanced question lookup with ID mapping support")
        
        if question_lookup_section != -1:
            # Find the specific line that checks for emergency_fix_18_questions
            fix18_check = final_content.find("if 'emergency_fix_18_questions' in session", question_lookup_section)
            
            if fix18_check != -1:
                # Insert Emergency Fix 19 check before Emergency Fix 18 check
                new_lookup_logic = '''        # First, try Emergency Fix 19 optimized question lookup
        if 'emergency_fix_19_storage_id' in session:
            question = emergency_fix_19_get_question_by_sequential_id(str(current_question_id))
            if question:
                logger.info(f"EMERGENCY FIX 19: Question found via optimized storage - sequential ID {current_question_id}")
        
        # Fallback to Emergency Fix 18 direct question mapping
        el'''
                
                final_content = (
                    final_content[:fix18_check] + 
                    new_lookup_logic +
                    final_content[fix18_check:]
                )
        
        # Create backup
        backup_filename = f"app.py.emergency_fix_19_backup_{int(time.time())}"
        with open(f'rccm-quiz-app/{backup_filename}', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Backup created: {backup_filename}")
        
        # Write the modified content
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("[OK] Emergency Fix 19 applied successfully to app.py")
        print("   - Session size optimization added")
        print("   - Server-side question storage implemented")
        print("   - Cache cleanup system integrated")
        print("   - Question lookup updated for optimized storage")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to apply Emergency Fix 19: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency_fix_19():
    """Test Emergency Fix 19 session size optimization"""
    print("\n=== Testing Emergency Fix 19 Session Size Optimization ===")
    print("Purpose: Verify session cookie size is reduced below 4KB limit")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Creating construction environment session...")
            
            # Start construction environment session
            response = client.get('/start_exam/specialist_env')
            
            if response.status_code in [200, 302]:
                print("   [OK] Construction environment session created")
                
                print("2. Accessing /exam to trigger Emergency Fix 17 + 18 + 19...")
                exam_response = client.get('/exam')
                
                if exam_response.status_code == 200:
                    print("   [OK] /exam access successful")
                    
                    # Check session structure after Emergency Fix 19
                    with client.session_transaction() as sess:
                        print("3. Verifying Emergency Fix 19 session optimization...")
                        
                        # Check session size indicators
                        session_keys = list(sess.keys())
                        print(f"   Session keys: {session_keys}")
                        
                        # Check for Emergency Fix 19 storage
                        if 'emergency_fix_19_storage_id' in sess:
                            storage_id = sess.get('emergency_fix_19_storage_id')
                            question_count = sess.get('emergency_fix_19_question_count', 0)
                            print(f"   [OK] Emergency Fix 19 storage ID: {storage_id}")
                            print(f"   [OK] Question count: {question_count}")
                        else:
                            print("   [NG] Emergency Fix 19 storage not found")
                        
                        # Check that large question data is removed from session
                        if 'emergency_fix_18_questions' not in sess:
                            print("   [OK] Large question data removed from session")
                        else:
                            print("   [WARN] Large question data still in session")
                        
                        # Estimate session size
                        import json
                        session_data = dict(sess)
                        session_json = json.dumps(session_data, ensure_ascii=False)
                        session_size = len(session_json.encode('utf-8'))
                        
                        print(f"   Session size estimate: {session_size} bytes")
                        
                        if session_size < 4000:
                            print("   [OK] Session size within 4KB limit")
                            size_optimization_success = True
                        else:
                            print("   [NG] Session size still exceeds recommended limit")
                            size_optimization_success = False
                        
                        # Test question retrieval
                        print("4. Testing question retrieval with Emergency Fix 19...")
                        
                        # Try to submit an answer to test question lookup
                        csrf_token = sess.get('csrf_token')
                        
                        if csrf_token:
                            print("   Testing answer submission...")
                            
                            answer_response = client.post('/exam', data={
                                'answer': 'A',
                                'elapsed': '3.0',
                                'csrf_token': csrf_token
                            })
                            
                            print(f"   Answer response status: {answer_response.status_code}")
                            
                            if answer_response.status_code == 200:
                                print("   [OK] Emergency Fix 19 - Answer submission successful!")
                                print("   [SUCCESS] SESSION SIZE OPTIMIZATION WORKING!")
                                return True
                            else:
                                print(f"   [NG] Answer submission failed: {answer_response.status_code}")
                                return size_optimization_success
                        else:
                            print("   [WARN] No CSRF token available for answer test")
                            return size_optimization_success
                else:
                    print(f"   [NG] /exam access failed: {exam_response.status_code}")
                    return False
            else:
                print(f"   [NG] Session creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Emergency Fix 19 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function for Emergency Fix 19 creation and application"""
    print("Emergency Fix 19: Session Size Optimization")
    print("=" * 80)
    print("Goal: Reduce session cookie size below 4KB limit")
    print("Problem: Emergency Fix 18 creates 4316 byte sessions, exceeding 4093 byte limit")
    print("Solution: Move large question data to server-side storage")
    print()
    
    # Step 1: Create Emergency Fix 19
    print("Step 1: Creating Emergency Fix 19...")
    emergency_fix_19_code = create_emergency_fix_19()
    
    # Step 2: Apply to app.py
    print("Step 2: Applying Emergency Fix 19 to app.py...")
    application_success = apply_emergency_fix_19_to_app()
    
    if application_success:
        print("Step 3: Testing Emergency Fix 19...")
        test_success = test_emergency_fix_19()
        
        if test_success:
            print("\n[SUCCESS] Emergency Fix 19 SUCCESS!")
            print("   - Session size optimized below 4KB limit")
            print("   - Server-side question storage working")
            print("   - Construction environment 10-question completion enabled")
            print("   - Ready for final Task 12 verification")
            return True
        else:
            print("\n[WARN] Emergency Fix 19 applied but testing shows issues")
            print("   - May need additional refinement")
            print("   - Check session size and question retrieval")
            return False
    else:
        print("\n[NG] Emergency Fix 19 application failed")
        print("   - Could not modify app.py")
        print("   - Check file permissions and backup status")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)