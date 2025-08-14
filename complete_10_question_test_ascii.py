#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
厳重な10問完走テスト - 分野混在なし確認付き (ASCII版)
道路部門で実際に10問解いて結果画面まで到達することを確認
"""
import requests
import re
from bs4 import BeautifulSoup
import time

def complete_10_question_test(department_id, department_name, base_url="http://127.0.0.1:5005"):
    """指定部門で10問完走テスト実行"""
    print(f"\n=== {department_name}部門 10問完走テスト開始 ===")
    
    session = requests.Session()
    
    try:
        # 1. 部門選択ページにアクセス
        print(f"1. 部門選択ページアクセス: {department_id}")
        dept_url = f"{base_url}/departments/{department_id}/types"
        dept_response = session.get(dept_url)
        
        if dept_response.status_code != 200:
            return f"ERROR: 部門ページアクセス失敗: {dept_response.status_code}"
        
        if "学習開始" not in dept_response.text:
            return f"ERROR: 部門ページ表示異常: 学習開始ボタンなし"
        
        print(f"SUCCESS: 部門ページアクセス成功")
        
        # 2. 問題開始（specialist問題）
        print("2. specialist問題開始")
        start_url = f"{base_url}/departments/{department_id}/start?mode=specialist"
        start_response = session.get(start_url)
        
        if start_response.status_code != 200:
            return f"ERROR: 問題開始失敗: {start_response.status_code}"
        
        print("SUCCESS: specialist問題開始成功")
        
        # 3. 10問完走テスト
        print("3. 10問完走テスト開始")
        questions_data = []
        
        for i in range(1, 11):
            print(f"--- 問題 {i}/10 処理中 ---")
            
            # 現在の問題ページを取得
            exam_url = f"{base_url}/exam"
            exam_response = session.get(exam_url)
            
            if exam_response.status_code != 200:
                return f"ERROR: 問題{i}取得失敗: {exam_response.status_code}"
            
            soup = BeautifulSoup(exam_response.text, 'html.parser')
            
            # 問題番号確認
            progress_element = soup.find('span', class_='badge bg-primary')
            if progress_element:
                progress_text = progress_element.text.strip()
                print(f"  問題番号表示: {progress_text}")
                
                if f"{i}/10" not in progress_text:
                    return f"ERROR: 問題{i}の番号表示異常: {progress_text}"
            else:
                return f"ERROR: 問題{i}の進捗表示なし"
            
            # カテゴリ確認（分野混在チェック）
            category_match = re.search(r'カテゴリ:\s*([^<]+)', exam_response.text)
            if category_match:
                category = category_match.group(1).strip()
                print(f"  カテゴリ: {category}")
                
                if category != department_name:
                    return f"CRITICAL: 問題{i}で分野混在発見: 期待値'{department_name}' 実際'{category}'"
                
                print(f"  SUCCESS: カテゴリ正常: {category}")
            else:
                return f"ERROR: 問題{i}でカテゴリ情報なし"
            
            # 問題文取得
            question_element = soup.find('h3', id='question-title')
            if question_element:
                question_text = question_element.text.strip()[:50]
                print(f"  問題文: {question_text}...")
            else:
                return f"ERROR: 問題{i}で問題文なし"
            
            # qid取得
            qid_input = soup.find('input', {'name': 'qid'})
            if not qid_input:
                return f"ERROR: 問題{i}でqid取得失敗"
            
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
                'category': category,
                'question_preview': question_text[:30]
            })
            
            # 回答送信
            answer_choice = ['A', 'B', 'C', 'D'][i % 4]  # A, B, C, Dをローテーション
            answer_data = {
                'qid': qid,
                'answer': answer_choice,
                'elapsed': str(30 + i * 5)  # 経過時間シミュレート
            }
            if csrf_token:
                answer_data['csrf_token'] = csrf_token
            
            print(f"  回答送信: {answer_choice}")
            answer_response = session.post(exam_url, data=answer_data)
            
            if answer_response.status_code != 200:
                return f"ERROR: 問題{i}回答送信失敗: {answer_response.status_code}"
            
            print(f"  SUCCESS: 問題{i}回答完了")
            time.sleep(0.5)  # レート制限回避
        
        # 4. 結果画面確認
        print("4. 結果画面確認")
        result_url = f"{base_url}/result"
        result_response = session.get(result_url)
        
        if result_response.status_code != 200:
            return f"ERROR: 結果画面アクセス失敗: {result_response.status_code}"
        
        if "テスト完了" not in result_response.text:
            return f"ERROR: 結果画面表示異常: テスト完了表示なし"
        
        # 結果詳細確認
        result_soup = BeautifulSoup(result_response.text, 'html.parser')
        dept_info_elements = result_soup.find_all(string=re.compile(r'部門:'))
        answer_info_elements = result_soup.find_all(string=re.compile(r'回答数:'))
        
        print("SUCCESS: 結果画面到達成功")
        if dept_info_elements:
            print(f"  部門情報: {dept_info_elements[0].strip()}")
        if answer_info_elements:
            print(f"  回答情報: {answer_info_elements[0].strip()}")
        
        return {
            'status': 'SUCCESS',
            'department': department_name,
            'questions_completed': 10,
            'field_mixing_detected': False,
            'questions_data': questions_data,
            'result_page_reached': True
        }
        
    except Exception as e:
        return f"ERROR: テスト実行中エラー: {str(e)}"

if __name__ == "__main__":
    print("=== 厳重な10問完走テスト - 分野混在なし確認 ===")
    print("=" * 60)
    
    # 道路部門テスト
    result = complete_10_question_test("road", "道路")
    
    if isinstance(result, dict) and result['status'] == 'SUCCESS':
        print("\n=== 道路部門10問完走テスト 完全成功！ ===")
        print(f"SUCCESS: 部門: {result['department']}")
        print(f"SUCCESS: 問題完了: {result['questions_completed']}/10")
        print(f"SUCCESS: 分野混在: {'なし' if not result['field_mixing_detected'] else 'あり'}")
        print(f"SUCCESS: 結果画面到達: {'成功' if result['result_page_reached'] else '失敗'}")
        print("\n=== 各問題データ ===")
        for q in result['questions_data']:
            print(f"  問題{q['number']}: qid={q['qid']}, カテゴリ={q['category']}")
    else:
        print(f"\nCRITICAL FAILURE: {result}")