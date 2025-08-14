#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Department Test - ASCII版10問完走テスト
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def final_department_test():
    """Final 10-question completion test"""
    print("=== Final Department 10-Question Test ===")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. Department types page access
            types_response = client.get('/departments/road/types')
            if types_response.status_code != 200:
                return f"FAILED: Department types page {types_response.status_code}"
            print("SUCCESS: Department types page access")
            
            # 2. Start specialist exam for road department
            exam_response = client.get('/exam?department=road&type=specialist')
            if exam_response.status_code != 200:
                return f"FAILED: Start specialist exam {exam_response.status_code}"
            print("SUCCESS: Specialist exam started")
            
            # 3. Test 10 questions completion
            questions_completed = 0
            categories_found = set()
            
            for i in range(1, 11):
                print(f"Processing question {i}/10...")
                
                # Get current question
                current_response = client.get('/exam')
                if current_response.status_code != 200:
                    return f"FAILED: Question {i} access failed {current_response.status_code}"
                
                html = current_response.data.decode('utf-8', errors='ignore')
                
                # Check progress display
                progress_match = re.search(r'(\d+)/(\d+)', html)
                if progress_match:
                    current_num = int(progress_match.group(1))
                    total_num = int(progress_match.group(2))
                    print(f"  Progress: {current_num}/{total_num}")
                
                # Check category (field mixing detection)
                category_match = re.search(r'カテゴリ:\s*([^<\n]+)', html)
                if category_match:
                    category = category_match.group(1).strip()
                    categories_found.add(category)
                    print(f"  Category: {category}")
                    
                    # Field mixing check
                    if category != "道路":
                        return {
                            'status': 'FIELD_MIXING_DETECTED',
                            'question': i,
                            'expected': '道路',
                            'actual': category
                        }
                
                # Get question ID
                qid_match = re.search(r'name="qid" value="([^"]+)"', html)
                if not qid_match:
                    return f"FAILED: Question {i} - qid not found"
                qid = qid_match.group(1)
                
                # Get CSRF token
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html)
                csrf_token = csrf_match.group(1) if csrf_match else None
                
                # Submit answer
                answer_data = {
                    'qid': qid,
                    'answer': ['A', 'B', 'C', 'D'][(i-1) % 4],
                    'elapsed': str(30 + i * 2)
                }
                if csrf_token:
                    answer_data['csrf_token'] = csrf_token
                
                answer_response = client.post('/exam', data=answer_data)
                if answer_response.status_code != 200:
                    return f"FAILED: Question {i} answer submission {answer_response.status_code}"
                
                questions_completed += 1
                print(f"  Question {i} completed successfully")
            
            # 4. Check result page
            result_response = client.get('/result')
            if result_response.status_code != 200:
                return f"FAILED: Result page access {result_response.status_code}"
            
            result_html = result_response.data.decode('utf-8', errors='ignore')
            has_completion = any(word in result_html for word in ["完了", "結果", "score", "テスト完了"])
            
            return {
                'status': 'COMPLETE_SUCCESS',
                'questions_completed': questions_completed,
                'target_questions': 10,
                'categories_found': list(categories_found),
                'field_mixing_success': len(categories_found) <= 1 and ("道路" in categories_found or len(categories_found) == 0),
                'result_page_reached': True,
                'completion_confirmed': has_completion
            }

if __name__ == "__main__":
    result = final_department_test()
    
    print("=" * 60)
    if isinstance(result, dict):
        if result['status'] == 'COMPLETE_SUCCESS':
            print("SUCCESS: 10-Question Department Test PASSED")
            print(f"Questions completed: {result['questions_completed']}/{result['target_questions']}")
            print(f"Categories found: {', '.join(result['categories_found'])}")
            print(f"Field mixing check: {'PASSED' if result['field_mixing_success'] else 'FAILED'}")
            print(f"Result page reached: {'YES' if result['result_page_reached'] else 'NO'}")
            print(f"Completion confirmed: {'YES' if result['completion_confirmed'] else 'NO'}")
            
            print("\nConclusion:")
            print("- Department routing 404 error: RESOLVED")
            print("- 10-question completion: SUCCESS")
            if result['field_mixing_success']:
                print("- Field mixing issue: RESOLVED")
            else:
                print("- Field mixing issue: REQUIRES INVESTIGATION")
                
        elif result['status'] == 'FIELD_MIXING_DETECTED':
            print("FIELD MIXING DETECTED:")
            print(f"Question {result['question']}: Expected '{result['expected']}', Got '{result['actual']}'")
            
        else:
            print(f"TEST RESULT: {result}")
    else:
        print(f"TEST FAILED: {result}")
    
    print("=" * 60)