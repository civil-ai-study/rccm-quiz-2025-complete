#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Urban Department Field Mixing Analysis (ASCII Safe)
Ultra Sync Task 10: Focused analysis on urban department field mixing issue
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def analyze_urban_department_field_mixing():
    """Analyze why urban department shows basic subject questions"""
    print("=== URBAN DEPARTMENT FIELD MIXING ANALYSIS ===")
    print("Purpose: Determine why emergency data fix didn't resolve urban field mixing")
    print()
    
    try:
        from app import app
        
        print("1. Emergency Data Loading System Test:")
        from utils import emergency_load_all_questions, emergency_get_questions
        
        all_questions = emergency_load_all_questions()
        print(f"   Total questions loaded: {len(all_questions)}")
        
        # Check categories available
        categories = {}
        for q in all_questions:
            cat = q.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("   Categories available:")
        for cat, count in sorted(categories.items()):
            print(f"     {cat}: {count} questions")
        
        print()
        print("2. Urban Planning Category Analysis:")
        urban_category = '都市計画及び地方計画'
        urban_count = categories.get(urban_category, 0)
        print(f"   Expected category '{urban_category}': {urban_count} questions")
        
        # Test emergency function filtering
        urban_questions_emergency = emergency_get_questions(
            department_category=urban_category,
            question_type='specialist',
            count=10
        )
        print(f"   Emergency function returned: {len(urban_questions_emergency)} questions")
        
        if len(urban_questions_emergency) > 0:
            print("   Sample questions from emergency function:")
            for i, q in enumerate(urban_questions_emergency[:3], 1):
                print(f"     {i}. ID:{q['id']} Category:{q['category']} Type:{q.get('question_type', 'N/A')}")
        
        print()
        print("3. Application Session Analysis:")
        with app.test_client() as client:
            # Start urban planning session
            response = client.get('/start_exam/specialist_urban')
            print(f"   Session start response: {response.status_code}")
            
            # Check session contents
            with client.session_transaction() as sess:
                if 'questions' in sess:
                    session_questions = sess['questions']
                    print(f"   Questions in session: {len(session_questions)}")
                    
                    # Analyze session question categories
                    session_categories = {}
                    for q in session_questions:
                        cat = q.get('category', 'unknown')
                        session_categories[cat] = session_categories.get(cat, 0) + 1
                    
                    print("   Session question categories:")
                    for cat, count in sorted(session_categories.items()):
                        print(f"     {cat}: {count} questions")
                    
                    # Check for field mixing
                    basic_count = session_categories.get('基礎', 0)
                    urban_count = session_categories.get(urban_category, 0)
                    
                    print()
                    print("4. Field Mixing Analysis:")
                    print(f"   Basic subject questions in session: {basic_count}")
                    print(f"   Urban planning questions in session: {urban_count}")
                    
                    if basic_count > 0 and urban_count == 0:
                        print("   CRITICAL: Field mixing detected - basic subjects only")
                        print("   ROOT CAUSE: Application is not using emergency filtered data")
                        return False
                    elif urban_count > 0 and basic_count == 0:
                        print("   SUCCESS: Urban planning questions only - field mixing resolved")
                        return True
                    else:
                        print(f"   MIXED RESULT: Both categories present (basic:{basic_count}, urban:{urban_count})")
                        return None
                else:
                    print("   ERROR: No questions found in session")
                    return False
                    
    except Exception as e:
        print(f"   ERROR: Analysis failed - {e}")
        return False

def test_department_parameter_mapping():
    """Test how department parameter is mapped in the application"""
    print()
    print("5. Department Parameter Mapping Analysis:")
    
    try:
        from app import app
        
        # Check LIGHTWEIGHT_DEPARTMENT_MAPPING
        from app import LIGHTWEIGHT_DEPARTMENT_MAPPING
        print("   LIGHTWEIGHT_DEPARTMENT_MAPPING contents:")
        for dept_id, dept_name in LIGHTWEIGHT_DEPARTMENT_MAPPING.items():
            print(f"     '{dept_id}' -> '{dept_name}'")
        
        print()
        urban_mapping = LIGHTWEIGHT_DEPARTMENT_MAPPING.get('urban', 'NOT_FOUND')
        print(f"   'urban' maps to: '{urban_mapping}'")
        
        # Test the mapping chain
        print()
        print("6. URL Parameter Chain Analysis:")
        
        with app.test_client() as client:
            # Trace the parameter flow
            print("   Testing URL: /start_exam/specialist_urban")
            
            # This should trigger the exam_start function with exam_type='specialist_urban'
            response = client.get('/start_exam/specialist_urban')
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'No location header')
                print(f"   Redirect location: {location}")
            
        return True
        
    except Exception as e:
        print(f"   ERROR: Parameter mapping analysis failed - {e}")
        return False

def main():
    print("URBAN DEPARTMENT FIELD MIXING ANALYSIS")
    print("=" * 60)
    print("Ultra Sync Task 10 - Detailed Investigation")
    print("Purpose: Understand why urban department shows basic questions")
    print()
    
    # Test 1: Field mixing analysis
    field_mixing_result = analyze_urban_department_field_mixing()
    
    # Test 2: Parameter mapping
    mapping_result = test_department_parameter_mapping()
    
    print()
    print("=" * 60)
    print("ANALYSIS RESULTS:")
    print(f"Field mixing analysis: {'SUCCESS' if field_mixing_result else 'FAILED' if field_mixing_result is False else 'INCONCLUSIVE'}")
    print(f"Parameter mapping analysis: {'SUCCESS' if mapping_result else 'FAILED'}")
    
    print()
    print("CONCLUSION:")
    if field_mixing_result is False:
        print("CRITICAL FINDING: Emergency data loading fix incomplete")
        print("- Emergency functions work correctly in isolation")
        print("- Application session still uses unfiltered/basic questions")
        print("- Field mixing problem persists at application level")
        print()
        print("NEXT STEPS:")
        print("1. Identify where session questions are populated")
        print("2. Ensure application uses emergency_get_questions consistently")
        print("3. Fix department parameter passing to emergency functions")
    elif field_mixing_result is True:
        print("SUCCESS: Field mixing resolved for urban department")
        print("- Urban planning questions properly filtered")
        print("- Emergency data loading fix working at application level")
    else:
        print("INCONCLUSIVE: Mixed results - further investigation needed")
        
    return field_mixing_result

if __name__ == "__main__":
    main()