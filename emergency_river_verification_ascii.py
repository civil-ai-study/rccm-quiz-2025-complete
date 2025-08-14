#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY RIVER VERIFICATION (ASCII SAFE)
Purpose: Verify emergency data loading fix resolved field mixing - Ultra Sync Task 9 completion test
Context: After emergency data loading patch applied to app.py
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def verify_emergency_data_integration():
    """Verify emergency data fix integration - ASCII safe output"""
    print("=== EMERGENCY RIVER VERIFICATION TEST ===")
    print("Purpose: Verify field mixing fix with ASCII-safe output")
    print()
    
    try:
        # Import Flask test client
        from app import app
        
        print("SUCCESS: Main app imported successfully")
        
        # Test using Flask test client
        with app.test_client() as client:
            print()
            print("Test 1: Homepage verification")
            response = client.get('/')
            if response.status_code == 200:
                print("SUCCESS: Homepage loads")
            else:
                print(f"ERROR: Homepage failed status {response.status_code}")
                return False
            
            print()
            print("Test 2: River department specialist exam")
            response = client.get('/exam?type=specialist&department=river')
            
            if response.status_code == 200:
                print("SUCCESS: River exam starts")
                response_text = response.get_data(as_text=True)
                
                # Check for emergency data fix activation (ASCII safe)
                if 'Emergency data fix success' in response_text:
                    print("SUCCESS: Emergency data fix active")
                    emergency_active = True
                else:
                    print("INFO: Emergency data fix may not be active")
                    emergency_active = False
                
                # Check for proper question form
                if '<form' in response_text and 'name="answer"' in response_text:
                    print("SUCCESS: Question form rendered")
                    
                    # Test answer submission
                    print()
                    print("Test 3: Answer submission")
                    csrf_token = ""
                    if 'csrf_token' in response_text:
                        start = response_text.find('value="') + 7
                        end = response_text.find('"', start)
                        csrf_token = response_text[start:end] if start > 6 and end > start else ""
                    
                    post_data = {
                        'answer': 'A',
                        'csrf_token': csrf_token
                    }
                    
                    post_response = client.post('/exam', data=post_data, follow_redirects=True)
                    
                    if post_response.status_code == 200:
                        print("SUCCESS: Answer submission successful")
                        
                        # Check question progression
                        post_text = post_response.get_data(as_text=True)
                        if '2/10' in post_text:
                            print("SUCCESS: Question progression working")
                            
                            # Field mixing verification - key test
                            print()
                            print("Test 4: Field mixing verification")
                            
                            # Test multiple questions to verify category consistency
                            field_mixing_test_results = []
                            
                            for question_num in range(2, 6):  # Test questions 2-5
                                # Get current question
                                current_response = client.get('/exam')
                                if current_response.status_code == 200:
                                    current_text = current_response.get_data(as_text=True)
                                    
                                    # Check if this is a river question or basic question
                                    # Look for category indicators (ASCII safe)
                                    is_river_related = any(word in current_text.lower() for word in [
                                        'river', 'flood', 'dam', 'waterway', 'drainage'
                                    ])
                                    
                                    is_basic_question = any(word in current_text.lower() for word in [
                                        'basic', 'fundamental', 'general'
                                    ])
                                    
                                    if is_river_related:
                                        field_mixing_test_results.append(f"Q{question_num}: River-related")
                                    elif is_basic_question:
                                        field_mixing_test_results.append(f"Q{question_num}: Basic subject")
                                    else:
                                        field_mixing_test_results.append(f"Q{question_num}: Category unclear")
                                    
                                    # Submit answer to continue
                                    csrf_token = ""
                                    if 'csrf_token' in current_text:
                                        start = current_text.find('value="') + 7
                                        end = current_text.find('"', start)
                                        csrf_token = current_text[start:end] if start > 6 and end > start else ""
                                    
                                    client.post('/exam', data={'answer': 'B', 'csrf_token': csrf_token})
                                
                            # Analyze field mixing results
                            print("Field mixing test results:")
                            for result in field_mixing_test_results:
                                print(f"  {result}")
                            
                            river_questions = sum(1 for r in field_mixing_test_results if 'River-related' in r)
                            basic_questions = sum(1 for r in field_mixing_test_results if 'Basic subject' in r)
                            
                            print(f"Summary: {river_questions} river, {basic_questions} basic")
                            
                            # Determine if field mixing is resolved
                            if basic_questions == 0 and river_questions > 0:
                                print("SUCCESS: Field mixing RESOLVED - No basic questions in river department")
                                return True
                            elif basic_questions > 0:
                                print("FAILED: Field mixing PERSISTS - Basic questions still appearing")
                                return False
                            else:
                                print("UNCLEAR: Cannot determine question types definitively")
                                return False
                                
                        else:
                            print("ERROR: Question progression failed")
                            return False
                    else:
                        print(f"ERROR: Answer submission failed {post_response.status_code}")
                        return False
                        
                else:
                    print("ERROR: Question form not found")
                    return False
                    
            else:
                print(f"ERROR: River exam failed status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        return False

def run_emergency_river_verification():
    """Execute emergency river verification test"""
    print("EMERGENCY RIVER VERIFICATION (ASCII SAFE)")
    print("=" * 60)
    print("Testing emergency data loading fix for field mixing resolution")
    print()
    
    success = verify_emergency_data_integration()
    
    print()
    print("=" * 60)
    if success:
        print("SUCCESS: Emergency river verification completed successfully")
        print("Result: Field mixing appears to be resolved")
        print()
        print(">>> Next Action: Mark Task 9 complete and proceed with other departments")
        return True
    else:
        print("FAILED: Emergency river verification failed")
        print("Issue: Field mixing may still be present")
        print()
        print(">>> Action Required: Review emergency fix or investigate further")
        return False

if __name__ == "__main__":
    run_emergency_river_verification()