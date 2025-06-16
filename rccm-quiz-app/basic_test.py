#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re

def test_basic_subjects():
    """基礎科目(4-1) 10問完全手作業テスト"""
    
    base_url = 'http://localhost:5003'
    session = requests.Session()

    print('🔧 基礎科目(4-1) 10問テスト開始...')

    # Access basic subjects department
    response = session.get(f'{base_url}/department_study/basic')
    if response.status_code != 200:
        print(f'❌ 基礎科目アクセス失敗: {response.status_code}')
        return False

    print('✅ 基礎科目開始成功')

    # Complete 10 questions
    for i in range(1, 11):
        print(f'[{time.strftime("%H:%M:%S")}] 🎯 基礎科目: 問題{i}/10')
        
        # Get exam page
        response = session.get(f'{base_url}/exam')
        if 'セッション情報が異常です' in response.text:
            print(f'❌ 問題{i}: セッション異常エラー')
            return False
        
        # Extract question ID 
        qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
        if qid_match:
            qid = qid_match.group(1)
            print(f'    QID: {qid}')
        else:
            print(f'    QID: 不明')
            qid = '1'
        
        # Submit answer
        answer_data = {'qid': qid, 'answer': 'A', 'elapsed': str(i * 0.5)}
        response = session.post(f'{base_url}/exam', data=answer_data)
        
        if response.status_code != 200:
            print(f'❌ 問題{i}: 解答送信失敗 - {response.status_code}')
            return False
        
        # Check for session errors
        if 'セッション情報が異常です' in response.text:
            print(f'❌ 問題{i}: セッション異常エラー')
            return False
            
        print(f'    ✅ 問題{i}: 解答完了')
        
        # Navigate to next question (except for last question)
        if i < 10:
            time.sleep(0.1)

    print('🎉 基礎科目(4-1) 10問テスト完全成功！')
    return True

if __name__ == '__main__':
    success = test_basic_subjects()
    if not success:
        exit(1)
    print('✅ 基礎科目テスト完了')