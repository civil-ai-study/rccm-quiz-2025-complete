#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: Trace exam_current changes throughout the flow
"""

from app import app

def trace_exam_current():
    """Trace exam_current changes throughout the flow"""
    print("ULTRA SYNC Trace exam_current changes")
    print("=" * 50)
    
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Session initialization
        with client.session_transaction() as sess:
            sess.clear()
            sess['user_name'] = 'trace_exam'
            sess.modified = True
        
        print("Step 1: After session init")
        with client.session_transaction() as sess:
            current = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"  exam_current={current}, question_ids={len(question_ids)}")
        
        # Department selection
        print("\nStep 2: Department selection")
        resp1 = client.get('/quiz_department/道路')
        print(f"  Response: {resp1.status_code}")
        with client.session_transaction() as sess:
            current = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"  exam_current={current}, question_ids={len(question_ids)}")
        
        # First question display (GET /exam)
        print("\nStep 3: First question display (GET /exam)")
        resp2 = client.get('/exam')
        print(f"  Response: {resp2.status_code}")
        with client.session_transaction() as sess:
            current = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"  exam_current={current}, question_ids={len(question_ids)}")
        
        # First answer submission (POST /exam)
        print("\nStep 4: First answer submission (POST /exam)")
        resp3 = client.post('/exam', data={'answer': 'A'})
        print(f"  Response: {resp3.status_code}")
        if resp3.status_code == 302:
            print(f"  Redirect: {resp3.headers.get('Location', '')}")
        with client.session_transaction() as sess:
            current = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"  exam_current={current}, question_ids={len(question_ids)}")
        
        # Second question display (GET /exam after redirect)
        print("\nStep 5: Second question display (GET /exam after redirect)")
        resp4 = client.get('/exam')
        print(f"  Response: {resp4.status_code}")
        with client.session_transaction() as sess:
            current = sess.get('exam_current', 'NOT_SET')
            question_ids = sess.get('exam_question_ids', [])
            print(f"  exam_current={current}, question_ids={len(question_ids)}")
        
        print("\n*** This is where exam_current gets reset from 1 back to 0 ***")

if __name__ == "__main__":
    trace_exam_current()