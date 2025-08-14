#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Question ID Diagnosis
建設環境部門問題ID診断
Purpose: 問題データID不一致の根本原因を特定し、Emergency Fix 12とexam関数の不整合を解析
"""

import os
import sys
import time

# Add the rccm-quiz-app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def analyze_emergency_get_questions_id_generation():
    """emergency_get_questions関数の問題ID生成ロジック分析"""
    print("=== Emergency Get Questions ID Generation Analysis ===")
    print("Purpose: Analyze how emergency_get_questions generates question IDs")
    print()
    
    try:
        from utils import emergency_get_questions
        
        print("1. Testing emergency_get_questions for construction environment...")
        
        # Call emergency_get_questions to get construction environment questions
        construction_env_questions = emergency_get_questions(
            department='env', 
            question_type='specialist', 
            count=10
        )
        
        print(f"   Questions returned: {len(construction_env_questions)}")
        
        if construction_env_questions:
            print("\n2. Analyzing question structure and IDs...")
            
            for i, question in enumerate(construction_env_questions[:3]):  # Show first 3 questions
                print(f"   Question {i+1}:")
                print(f"     ID: {question.get('id', 'NO_ID')}")
                print(f"     Category: {question.get('category', 'NO_CATEGORY')}")
                print(f"     Type: {question.get('question_type', 'NO_TYPE')}")
                print(f"     Year: {question.get('year', 'NO_YEAR')}")
                print(f"     All keys: {list(question.keys())}")
                print()
            
            # Extract all IDs
            all_ids = [q.get('id', 'NO_ID') for q in construction_env_questions]
            print(f"   All question IDs: {all_ids}")
            
            # Check ID types
            id_types = set(type(id_val).__name__ for id_val in all_ids)
            print(f"   ID data types: {id_types}")
            
            return construction_env_questions
        else:
            print("   ERROR: No construction environment questions returned")
            return []
            
    except Exception as e:
        print(f"ERROR: emergency_get_questions analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_exam_function_expected_ids():
    """exam関数が期待する問題ID形式の分析"""
    print("\n=== Exam Function Expected ID Format Analysis ===")
    print("Purpose: Understand what ID format the /exam function expects")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. Creating a basic session to see exam function ID expectations...")
            
            # Start a basic session to see how IDs are normally structured
            response = client.get('/start_exam/basic')
            
            if response.status_code in [200, 302]:
                print("   Basic session created successfully")
                
                # Check the session structure
                with client.session_transaction() as sess:
                    print("\n2. Analyzing basic session structure...")
                    print(f"   Session keys: {list(sess.keys())}")
                    
                    if 'exam_question_ids' in sess:
                        exam_ids = sess['exam_question_ids']
                        print(f"   exam_question_ids: {exam_ids}")
                        print(f"   exam_question_ids type: {type(exam_ids)}")
                        print(f"   ID count: {len(exam_ids) if exam_ids else 0}")
                        
                        if exam_ids:
                            first_id = exam_ids[0]
                            print(f"   First ID: {first_id} (type: {type(first_id)})")
                            
                            # Check if these are sequential or CSV-based IDs
                            if all(str(id_val).isdigit() for id_val in exam_ids):
                                print("   ID pattern: All numeric")
                                if exam_ids == [str(i) for i in range(1, len(exam_ids) + 1)]:
                                    print("   ID type: Sequential (1, 2, 3, ...)")
                                else:
                                    print("   ID type: Non-sequential numeric")
                            else:
                                print("   ID pattern: Mixed or non-numeric")
                            
                            return exam_ids
                    else:
                        print("   No exam_question_ids found in basic session")
                        return []
            else:
                print(f"   ERROR: Basic session creation failed: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"ERROR: exam function analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_id_mismatch_root_cause(emergency_questions, exam_expected_ids):
    """ID不一致の根本原因分析"""
    print("\n=== ID Mismatch Root Cause Analysis ===")
    print("Purpose: Identify the exact cause of ID mismatch between Emergency Fix 12 and exam function")
    print()
    
    if not emergency_questions:
        print("ERROR: No emergency questions to analyze")
        return False
    
    if not exam_expected_ids:
        print("ERROR: No exam expected IDs to analyze")
        return False
    
    # Extract IDs from emergency questions
    emergency_ids = [q.get('id', 'NO_ID') for q in emergency_questions]
    
    print(f"1. Emergency Fix 12 IDs: {emergency_ids}")
    print(f"2. Exam function expected IDs: {exam_expected_ids}")
    print()
    
    # Analyze the mismatch
    print("3. ID Mismatch Analysis:")
    
    # Check if emergency IDs exist in exam expected IDs
    emergency_ids_str = [str(id_val) for id_val in emergency_ids]
    exam_ids_str = [str(id_val) for id_val in exam_expected_ids]
    
    matches = set(emergency_ids_str) & set(exam_ids_str)
    emergency_only = set(emergency_ids_str) - set(exam_ids_str)
    exam_only = set(exam_ids_str) - set(emergency_ids_str)
    
    print(f"   Matching IDs: {matches}")
    print(f"   Emergency-only IDs: {emergency_only}")
    print(f"   Exam-only IDs: {exam_only}")
    print()
    
    # Determine the root cause
    print("4. Root Cause Analysis:")
    
    if not matches:
        print("   CRITICAL: No ID overlap between Emergency Fix 12 and exam function")
        print("   Root Cause: Completely different ID systems")
        
        # Check ID patterns
        if all(id_val.isdigit() and int(id_val) > 100 for id_val in emergency_ids_str):
            print("   Emergency IDs pattern: CSV file IDs (high numbers like 184, 207)")
        
        if exam_ids_str == [str(i) for i in range(1, len(exam_ids_str) + 1)]:
            print("   Exam IDs pattern: Sequential session IDs (1, 2, 3, ...)")
            
        print("\n   SOLUTION NEEDED: Convert Emergency Fix 12 to use sequential IDs")
        print("   or modify exam function to handle CSV IDs")
        
        return True  # Found the root cause
    else:
        print("   Some IDs match - partial compatibility")
        return False

def main():
    """Main diagnostic function"""
    print("Construction Environment Question ID Diagnosis")
    print("=" * 70)
    print("Task: Diagnose question data ID mismatch between Emergency Fix 12 and exam function")
    print("Goal: Identify why ID 184 is not in available_ids ['1','2','3','4','5']")
    print()
    
    # Step 1: Analyze emergency_get_questions ID generation
    emergency_questions = analyze_emergency_get_questions_id_generation()
    
    # Step 2: Analyze exam function expected ID format
    exam_expected_ids = analyze_exam_function_expected_ids()
    
    # Step 3: Analyze the root cause of mismatch
    root_cause_found = analyze_id_mismatch_root_cause(emergency_questions, exam_expected_ids)
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC RESULTS SUMMARY")
    print("=" * 70)
    
    if root_cause_found:
        print("✅ Root cause identified: ID system incompatibility")
        print("📋 Next steps:")
        print("   1. Modify Emergency Fix 12 to generate sequential IDs")
        print("   2. Or modify exam function to handle CSV IDs") 
        print("   3. Ensure session structure compatibility")
        print("   4. Test with construction environment 10-question completion")
    else:
        print("⚠️ Root cause analysis incomplete - need further investigation")
    
    return root_cause_found

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)