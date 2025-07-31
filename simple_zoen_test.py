#!/usr/bin/env python3
"""造園2016年エラー簡潔テスト"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

try:
    from app import get_mixed_questions, load_questions, VALID_YEARS, DEPARTMENT_TO_CATEGORY_MAPPING
    
    print("=== VALID_YEARS ===")
    print(f"2016 in VALID_YEARS: {2016 in VALID_YEARS}")
    
    print("\n=== DEPARTMENT_MAPPING ===")
    print(f"造園 -> {DEPARTMENT_TO_CATEGORY_MAPPING.get('造園')}")
    
    print("\n=== DATA LOADING ===")
    all_questions = load_questions()
    print(f"Total questions: {len(all_questions)}")
    
    zoen_2016 = [q for q in all_questions if q.get('category') == '造園' and str(q.get('year')) == '2016']
    print(f"造園2016 questions: {len(zoen_2016)}")
    
    if zoen_2016:
        print(f"First question: ID={zoen_2016[0].get('id')}, type={zoen_2016[0].get('question_type')}")
    
    print("\n=== GET_MIXED_QUESTIONS TEST ===")
    mock_session = {'history': [], 'srs_data': {}}
    
    try:
        result = get_mixed_questions(
            user_session=mock_session,
            all_questions=all_questions,
            requested_category='造園',
            session_size=10,
            department='造園',
            question_type='specialist',
            year=2016
        )
        
        if result:
            print(f"SUCCESS: {len(result)} questions selected")
            print(f"First result: ID={result[0].get('id')}, cat={result[0].get('category')}, year={result[0].get('year')}")
        else:
            print("EMPTY RESULT - This is the issue!")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()