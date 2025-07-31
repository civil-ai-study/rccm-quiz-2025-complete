#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門の完全テスト実行（絶対に嘘をつかない）
Task 2: Road Department Complete Testing
"""

import time
from app import app

def test_road_department():
    print("=== 道路部門の完全テスト実行（絶対に嘘をつかない） ===")
    
    # Step 1: Server status check
    print("\n1. サーバー状況確認:")
    start_time = time.time()
    
    with app.test_client() as client:
        try:
            response = client.get('/')
            response_time = time.time() - start_time
            print(f"   Homepage status: {response.status_code}")
            print(f"   Response time: {response_time:.3f}s")
            
            if response.status_code != 200:
                print(f"   ❌ ERROR: Homepage failed with status {response.status_code}")
                return False
            else:
                print("   ✅ SUCCESS: Server is running")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            return False
    
    # Step 2: Road department page access
    print("\n2. 道路部門ページアクセス確認:")
    with app.test_client() as client:
        try:
            response = client.get('/quiz_department/道路')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"   Redirect to: {location}")
                print("   ✅ SUCCESS: Route redirect working")
            elif response.status_code == 200:
                text = response.get_data(as_text=True)
                if "エラー" in text:
                    print("   ❌ ERROR: Error page returned despite 200 status")
                    return False
                else:
                    print("   ✅ SUCCESS: Page loaded without redirect")
            else:
                print(f"   ❌ ERROR: Unexpected status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            return False
    
    # Step 3: Exam endpoint test
    print("\n3. /examエンドポイント確認:")
    with app.test_client() as client:
        try:
            # Set up session for road department
            with client.session_transaction() as sess:
                sess['quiz_question_ids'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                sess['quiz_current'] = 0
                sess['quiz_department'] = '道路'
                sess['selected_question_type'] = 'specialist'
            
            response = client.get('/exam')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                text = response.get_data(as_text=True)
                
                # Check for error content
                if "エラー" in text or "問題が発生" in text:
                    print("   ❌ TRUTH: Error page detected despite HTTP 200")
                    
                    # Extract error details safely
                    if "問題データが存在しません" in text:
                        print("   Error detail: 問題データが存在しません")
                    elif "問題データが空" in text:
                        print("   Error detail: 問題データが空")
                    else:
                        print("   Error detail: Unknown error content")
                    return False
                else:
                    print("   ✅ SUCCESS: Exam page loaded without error")
                    
                    # Verify question content
                    if "問題" in text and ("選択肢" in text or "option" in text):
                        print("   ✅ Question content found")
                    else:
                        print("   ⚠️  WARNING: No question content detected")
                        return False
            else:
                print(f"   ❌ ERROR: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            return False
    
    # Step 4: Question data verification
    print("\n4. 道路部門問題データ確認:")
    try:
        from app import get_department_questions_ultrasync
        questions = get_department_questions_ultrasync('道路', 10)
        
        if questions and len(questions) >= 10:
            print(f"   ✅ SUCCESS: {len(questions)} questions available for road department")
            
            # Check question structure
            sample_question = questions[0]
            required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            
            for field in required_fields:
                if field not in sample_question:
                    print(f"   ❌ ERROR: Missing required field '{field}' in question data")
                    return False
            
            print("   ✅ Question data structure validated")
            
        else:
            print(f"   ❌ ERROR: Insufficient questions for road department ({len(questions) if questions else 0} found, need 10)")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False
    
    # Step 5: Complete flow simulation
    print("\n5. 完全フロー確認:")
    with app.test_client() as client:
        try:
            # Start from department selection
            response1 = client.get('/quiz_department/道路')
            print(f"   Department selection: {response1.status_code}")
            
            if response1.status_code == 302:
                # Follow redirect to exam
                location = response1.headers.get('Location', '')
                if location.startswith('/'):
                    response2 = client.get(location)
                    print(f"   Exam page: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        text = response2.get_data(as_text=True)
                        if "エラー" not in text and "問題が発生" not in text:
                            print("   ✅ SUCCESS: Complete flow working")
                            return True
                        else:
                            print("   ❌ ERROR: Error in exam page")
                            return False
                    else:
                        print(f"   ❌ ERROR: Exam page returned {response2.status_code}")
                        return False
                else:
                    print(f"   ❌ ERROR: Invalid redirect location: {location}")
                    return False
            else:
                print(f"   ❌ ERROR: Department selection failed: {response1.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            return False

if __name__ == "__main__":
    success = test_road_department()
    print(f"\n=== 道路部門テスト結果 ===")
    if success:
        print("✅ SUCCESS: 道路部門は正常に動作しています")
    else:
        print("❌ FAILED: 道路部門にエラーが発見されました")