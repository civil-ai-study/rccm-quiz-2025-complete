#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RIVER TEST PURE ASCII
Purpose: Test river department with pure ASCII output only
Context: Ultra Sync Task 9 completion verification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_river_department_pure_ascii():
    """Test river department - pure ASCII output"""
    print("=== RIVER DEPARTMENT TEST (PURE ASCII) ===")
    print("Purpose: Verify field mixing fix")
    print()
    
    try:
        from app import app
        print("App imported successfully")
        
        with app.test_client() as client:
            print("Test 1: Homepage")
            response = client.get('/')
            if response.status_code == 200:
                print("Homepage OK")
            else:
                print("Homepage FAILED")
                return False
            
            print()
            print("Test 2: River department exam")
            response = client.get('/exam?type=specialist&department=river')
            
            if response.status_code == 200:
                print("River exam starts OK")
                response_text = response.get_data(as_text=True)
                
                # Check for emergency data fix
                if 'Emergency data fix success' in response_text:
                    print("Emergency data fix: ACTIVE")
                else:
                    print("Emergency data fix: NOT DETECTED")
                
                # Check form
                if '<form' in response_text and 'name="answer"' in response_text:
                    print("Question form: OK")
                    
                    # Submit answer
                    print()
                    print("Test 3: Answer submission")
                    csrf_token = ""
                    if 'csrf_token' in response_text:
                        start = response_text.find('value="') + 7
                        end = response_text.find('"', start)
                        csrf_token = response_text[start:end] if start > 6 and end > start else ""
                    
                    post_data = {'answer': 'A', 'csrf_token': csrf_token}
                    post_response = client.post('/exam', data=post_data, follow_redirects=True)
                    
                    if post_response.status_code == 200:
                        print("Answer submission: OK")
                        post_text = post_response.get_data(as_text=True)
                        
                        if '2/10' in post_text:
                            print("Question progression: OK")
                            
                            # Field mixing check
                            print()
                            print("Test 4: Field mixing check")
                            
                            # Check for basic vs river content indicators
                            basic_indicators = ['basic', 'fundamental', 'general']
                            river_indicators = ['river', 'flood', 'dam', 'waterway']
                            
                            basic_count = sum(1 for word in basic_indicators if word in post_text.lower())
                            river_count = sum(1 for word in river_indicators if word in post_text.lower())
                            
                            print(f"Basic indicators found: {basic_count}")
                            print(f"River indicators found: {river_count}")
                            
                            # Simple field mixing assessment
                            if river_count > 0 and basic_count == 0:
                                print("Field mixing status: RESOLVED")
                                return True
                            elif basic_count > river_count:
                                print("Field mixing status: PROBLEM PERSISTS")
                                return False
                            else:
                                print("Field mixing status: UNCLEAR")
                                return False
                        else:
                            print("Question progression: FAILED")
                            return False
                    else:
                        print("Answer submission: FAILED")
                        return False
                else:
                    print("Question form: NOT FOUND")
                    return False
            else:
                print("River exam: FAILED")
                return False
                
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    print("RIVER TEST PURE ASCII")
    print("=" * 50)
    
    success = test_river_department_pure_ascii()
    
    print()
    print("=" * 50)
    if success:
        print("RESULT: SUCCESS")
        print("Field mixing appears to be resolved")
    else:
        print("RESULT: FAILED")
        print("Field mixing issue persists")
    
    return success

if __name__ == "__main__":
    main()