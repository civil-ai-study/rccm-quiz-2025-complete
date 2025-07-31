#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: Test the session reset fix
"""

from app import app

def test_session_fix():
    """Test the session reset fix"""
    print("ULTRA SYNC Test session reset fix")
    print("=" * 40)
    
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Session initialization
        with client.session_transaction() as sess:
            sess.clear()
            sess['user_name'] = 'test_fix'
            sess.modified = True
        
        print("Step 1: Department selection")
        resp1 = client.get('/quiz_department/道路')
        print(f"  Response: {resp1.status_code}")
        
        print("\nStep 2: First POST answer")
        resp2 = client.post('/exam', data={'answer': 'A'})
        print(f"  Response: {resp2.status_code}")
        
        # Check session before GET
        with client.session_transaction() as sess:
            current_before = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"\nBefore GET: exam_current={current_before}, questions={len(question_ids)}")
        
        print("\nStep 3: GET after POST (this should preserve exam_current)")
        resp3 = client.get('/exam')
        print(f"  Response: {resp3.status_code}")
        
        # Check session after GET
        with client.session_transaction() as sess:
            current_after = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"\nAfter GET: exam_current={current_after}, questions={len(question_ids)}")
            
            if current_after == current_before and current_after > 0:
                print("SUCCESS: exam_current was preserved\!")
                return True
            else:
                print(f"FAILURE: exam_current changed from {current_before} to {current_after}")
                return False

if __name__ == "__main__":
    success = test_session_fix()
    if success:
        print("\nFinal result: FIX SUCCESSFUL")
    else:
        print("\nFinal result: FIX FAILED - need further investigation")
EOF < /dev/null
