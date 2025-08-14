#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
シンプルな実完走テスト - 実際に10問解いて結果確認
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re
from bs4 import BeautifulSoup

def simple_complete_test():
    """シンプルな10問完走テスト"""
    print("=== シンプル10問完走テスト開始 ===")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. ホームページアクセス
            print("1. ホームページアクセス")
            home_response = client.get('/')
            if home_response.status_code != 200:
                return f"FAILED: ホームページアクセス失敗 {home_response.status_code}"
            print("SUCCESS: ホームページアクセス成功")
            
            # 2. セッション初期化（専門科目開始）
            print("2. 専門科目セッション開始")
            start_response = client.get('/start_exam/specialist')
            if start_response.status_code not in [200, 302]:
                return f"FAILED: 専門科目開始失敗 {start_response.status_code}"
            print("SUCCESS: 専門科目セッション開始成功")
            
            # 3. クイズ開始
            print("3. クイズページアクセス")
            quiz_response = client.get('/quiz')
            if quiz_response.status_code != 200:
                return f"FAILED: クイズアクセス失敗 {quiz_response.status_code}"
            print("SUCCESS: クイズページアクセス成功")
            
            # 4. 10問完走テスト
            print("4. 10問完走テスト実行")
            questions_data = []
            
            for i in range(1, 11):
                print(f"--- 問題 {i}/10 処理中 ---")
                
                # 現在の問題取得
                current_response = client.get('/quiz')
                if current_response.status_code != 200:
                    return f"FAILED: 問題{i}取得失敗 {current_response.status_code}"
                
                html = current_response.data.decode('utf-8', errors='ignore')
                
                # 問題番号確認
                progress_match = re.search(r'(\d+)/(\d+)', html)
                if progress_match:
                    current_num = int(progress_match.group(1))
                    total_num = int(progress_match.group(2))
                    print(f"  問題番号: {current_num}/{total_num}")
                    
                    if current_num != i:
                        print(f"  WARNING: 期待値{i} 実際{current_num}")
                else:
                    print("  問題番号表示なし")
                
                # カテゴリ確認
                category_match = re.search(r'カテゴリ:\s*([^<\n]+)', html)
                if category_match:
                    category = category_match.group(1).strip()
                    print(f"  カテゴリ: {category}")
                else:
                    category = "不明"
                    print("  カテゴリ情報なし")
                
                # qid取得
                qid_match = re.search(r'name="qid" value="([^"]+)"', html)
                if qid_match:
                    qid = qid_match.group(1)
                    print(f"  qid: {qid}")
                else:
                    return f"FAILED: 問題{i}でqid取得失敗"
                
                questions_data.append({
                    'number': i,
                    'qid': qid,
                    'category': category
                })
                
                # CSRF token取得
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html)
                csrf_token = csrf_match.group(1) if csrf_match else None
                
                # 回答送信
                answer_choice = ['A', 'B', 'C', 'D'][(i - 1) % 4]
                answer_data = {
                    'qid': qid,
                    'answer': answer_choice,
                    'elapsed': str(30 + i * 2)
                }
                if csrf_token:
                    answer_data['csrf_token'] = csrf_token
                
                print(f"  回答送信: {answer_choice}")
                answer_response = client.post('/quiz', data=answer_data)
                
                if answer_response.status_code != 200:
                    return f"FAILED: 問題{i}回答送信失敗 {answer_response.status_code}"
                
                print(f"  SUCCESS: 問題{i}回答完了")
            
            # 5. 結果画面確認
            print("5. 結果画面確認")
            result_response = client.get('/result')
            
            if result_response.status_code != 200:
                return f"FAILED: 結果画面アクセス失敗 {result_response.status_code}"
            
            result_html = result_response.data.decode('utf-8', errors='ignore')
            
            # 結果確認
            has_completion = "完了" in result_html or "結果" in result_html or "score" in result_html.lower()
            
            print("SUCCESS: 結果画面到達成功")
            
            return {
                'status': 'COMPLETE_SUCCESS',
                'questions_completed': 10,
                'questions_data': questions_data,
                'result_page_reached': True,
                'completion_confirmed': has_completion
            }

if __name__ == "__main__":
    result = simple_complete_test()
    
    print("=" * 60)
    if isinstance(result, dict) and result['status'] == 'COMPLETE_SUCCESS':
        print("🎉 COMPLETE SUCCESS: 10問完走テスト成功")
        print("=" * 60)
        print(f"問題完了数: {result['questions_completed']}/10")
        print(f"結果画面到達: {'成功' if result['result_page_reached'] else '失敗'}")
        print(f"完了確認: {'成功' if result['completion_confirmed'] else '失敗'}")
        
        print("\n--- 各問題詳細（分野混在チェック） ---")
        categories = set()
        for q in result['questions_data']:
            categories.add(q['category'])
            print(f"問題{q['number']:2d}: qid={q['qid']}, カテゴリ={q['category']}")
        
        print(f"\n--- 分野混在チェック結果 ---")
        print(f"出現カテゴリ数: {len(categories)}")
        print(f"カテゴリ一覧: {', '.join(categories)}")
        
        if len(categories) == 1:
            print("✅ 分野混在なし - 単一カテゴリのみ出題")
        else:
            print("❌ 分野混在あり - 複数カテゴリが混在")
        
        print("\n🏆 結論: 実際に10問完走し、分野混在状況を確認しました")
    else:
        print(f"❌ TEST FAILED: {result}")
    print("=" * 60)