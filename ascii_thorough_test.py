#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
厳重な10問完走テスト - ASCII版 (Windowsエンコーディング対応)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re
from bs4 import BeautifulSoup

def ascii_thorough_test():
    print("=== 厳重な10問完走テスト開始 ===")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. 道路部門選択ページアクセス
            print("1. 道路部門選択ページアクセス")
            dept_response = client.get('/departments/road/types')
            
            if dept_response.status_code != 200:
                return f"FAILED: 部門ページアクセス失敗 {dept_response.status_code}"
            
            print("SUCCESS: 道路部門ページアクセス成功")
            
            # 2. specialist問題開始
            print("2. specialist問題開始")
            start_response = client.get('/departments/road/start?mode=specialist')
            
            if start_response.status_code not in [200, 302]:
                return f"FAILED: 問題開始失敗 {start_response.status_code}"
            
            print("SUCCESS: specialist問題開始成功")
            
            # 3. 10問完走テスト
            print("3. 10問完走テスト実行")
            questions_data = []
            field_mixing_detected = False
            
            for i in range(1, 11):
                print(f"--- 問題 {i}/10 処理中 ---")
                
                # 現在の問題取得
                exam_response = client.get('/exam')
                
                if exam_response.status_code != 200:
                    return f"FAILED: 問題{i}取得失敗 {exam_response.status_code}"
                
                html = exam_response.data.decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                # 問題番号確認
                progress_element = soup.find('span', class_='badge bg-primary')
                if progress_element:
                    progress_text = progress_element.text.strip()
                    print(f"  問題番号: {progress_text}")
                    
                    if f"{i}/10" not in progress_text:
                        return f"FAILED: 問題{i}番号表示異常 {progress_text}"
                else:
                    return f"FAILED: 問題{i}進捗表示なし"
                
                # カテゴリ確認（最重要：分野混在チェック）
                category_match = re.search(r'カテゴリ:\s*([^<]+)', html)
                if category_match:
                    category = category_match.group(1).strip()
                    print(f"  カテゴリ: {category}")
                    
                    # 道路部門以外のカテゴリが出現したら分野混在
                    if category != "道路":
                        field_mixing_detected = True
                        return f"CRITICAL: 問題{i}で分野混在検出! 期待値='道路' 実際='{category}'"
                    
                    print(f"  SUCCESS: カテゴリ正常 - {category}")
                else:
                    return f"FAILED: 問題{i}カテゴリ情報なし"
                
                # qid取得
                qid_input = soup.find('input', {'name': 'qid'})
                if not qid_input:
                    return f"FAILED: 問題{i}qid取得失敗"
                
                qid = qid_input['value']
                print(f"  qid: {qid}")
                
                # CSRF token取得
                csrf_token = None
                csrf_input = soup.find('input', {'name': 'csrf_token'})
                if csrf_input:
                    csrf_token = csrf_input['value']
                
                questions_data.append({
                    'number': i,
                    'qid': qid,
                    'category': category
                })
                
                # 回答送信
                answer_choice = ['A', 'B', 'C', 'D'][(i - 1) % 4]
                answer_data = {
                    'qid': qid,
                    'answer': answer_choice,
                    'elapsed': str(25 + i * 3)
                }
                if csrf_token:
                    answer_data['csrf_token'] = csrf_token
                
                print(f"  回答送信: {answer_choice}")
                answer_response = client.post('/exam', data=answer_data)
                
                if answer_response.status_code != 200:
                    return f"FAILED: 問題{i}回答送信失敗 {answer_response.status_code}"
                
                print(f"  SUCCESS: 問題{i}回答完了")
            
            # 4. 結果画面確認
            print("4. 結果画面到達確認")
            result_response = client.get('/result')
            
            if result_response.status_code != 200:
                return f"FAILED: 結果画面アクセス失敗 {result_response.status_code}"
            
            result_html = result_response.data.decode('utf-8', errors='ignore')
            
            # "テスト完了"表示確認
            if "テスト完了" not in result_html:
                return f"FAILED: 結果画面にテスト完了表示なし"
            
            # 結果詳細取得
            dept_match = re.search(r'部門:\s*([^<\n]+)', result_html)
            answer_match = re.search(r'回答数:\s*([^<\n]+)', result_html)
            
            dept_info = dept_match.group(1).strip() if dept_match else "不明"
            answer_info = answer_match.group(1).strip() if answer_match else "不明"
            
            print("SUCCESS: 結果画面到達成功")
            print(f"  部門情報: {dept_info}")
            print(f"  回答情報: {answer_info}")
            
            return {
                'status': 'COMPLETE_SUCCESS',
                'department': '道路',
                'questions_completed': 10,
                'field_mixing_detected': field_mixing_detected,
                'questions_data': questions_data,
                'result_page_reached': True,
                'dept_info': dept_info,
                'answer_info': answer_info
            }

if __name__ == "__main__":
    result = ascii_thorough_test()
    
    print("=" * 60)
    if isinstance(result, dict) and result['status'] == 'COMPLETE_SUCCESS':
        print("COMPLETE SUCCESS: 道路部門10問完走テスト成功")
        print("=" * 60)
        print(f"部門: {result['department']}")
        print(f"問題完了数: {result['questions_completed']}/10")
        print(f"分野混在: {'検出なし' if not result['field_mixing_detected'] else '検出あり'}")
        print(f"結果画面到達: {'成功' if result['result_page_reached'] else '失敗'}")
        print(f"部門情報: {result['dept_info']}")
        print(f"回答情報: {result['answer_info']}")
        
        print("\n--- 各問題詳細 ---")
        for q in result['questions_data']:
            print(f"問題{q['number']:2d}: qid={q['qid']}, カテゴリ={q['category']}")
        
        print("\n結論: CLAUDE.mdの「10問完走成功・分野混在なし」が実証されました")
    else:
        print(f"TEST FAILED: {result}")
    print("=" * 60)