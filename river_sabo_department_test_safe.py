#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
河川・砂防部門完全テスト（ウルトラシンク・絶対に嘘をつかない）
Unicode安全版 - 絵文字なし
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

def river_sabo_complete_test():
    """
    河川・砂防部門の完全テスト実行（絶対に嘘をつかない）
    """
    
    print("=" * 100)
    print("河川・砂防部門完全テスト（ウルトラシンク・絶対に嘘をつかない）")
    print("=" * 100)
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'department': '河川・砂防',
        'test_status': 'running',
        'detailed_results': {},
        'errors': [],
        'question_numbers_left_side': [],
        'category_consistency': None,
        'mixing_detected': False,
        'final_results_verified': False
    }
    
    base_url = 'http://127.0.0.1:5006'
    session = requests.Session()
    
    try:
        print("\nステップ1: サーバー接続確認")
        response = session.get(base_url)
        if response.status_code != 200:
            test_results['errors'].append(f"サーバー接続失敗: {response.status_code}")
            print(f"NG サーバー接続失敗: {response.status_code}")
            return test_results
        
        print("OK サーバー接続成功")
        
        print("\nステップ2: 河川・砂防部門セッション開始")
        setup_data = {
            's_type': 'specialist',
            's_dept': '河川・砂防',
            's_questions': '10'
        }
        
        setup_response = session.post(f'{base_url}/setup', data=setup_data)
        if setup_response.status_code != 200:
            test_results['errors'].append(f"セッション開始失敗: {setup_response.status_code}")
            print(f"NG セッション開始失敗: {setup_response.status_code}")
            return test_results
        
        print("OK 河川・砂防部門セッション開始成功")
        
        print("\nステップ3: 問題画面取得と詳細検証")
        exam_response = session.get(f'{base_url}/exam')
        if exam_response.status_code != 200:
            test_results['errors'].append(f"問題画面取得失敗: {exam_response.status_code}")
            print(f"NG 問題画面取得失敗: {exam_response.status_code}")
            return test_results
        
        # 問題画面の内容を詳細検証（絶対に嘘をつかない）
        exam_content = exam_response.text
        print("OK 問題画面取得成功 - 内容を詳細検証中...")
        
        # エラーページかどうかの確認
        if "処理中に問題が発生しました" in exam_content or "エラー" in exam_content:
            test_results['errors'].append("問題画面にエラーメッセージを検出")
            print("NG 問題画面にエラーメッセージを検出")
            test_results['detailed_results']['exam_page_error'] = True
            return test_results
        
        test_results['detailed_results']['exam_page_error'] = False
        
        # 左側問題番号の確認（1/10から10/10まで）
        print("\nステップ4: 左側問題番号チェック(1/10-10/10)の詳細検証")
        
        question_numbers_found = []
        categories_found = set()
        
        # 10問すべてをチェック
        for i in range(10):
            current_question_num = i + 1
            
            # 問題番号パターンを検索
            if f"{current_question_num}/10" in exam_content:
                question_numbers_found.append(f"{current_question_num}/10")
                print(f"OK 問題番号確認: {current_question_num}/10")
            else:
                test_results['errors'].append(f"問題番号{current_question_num}/10が見つからない")
                print(f"NG 問題番号{current_question_num}/10が見つからない")
            
            # 各問題の回答を進める
            if i < 9:  # 最後の問題以外
                answer_data = {
                    'answer': '1',  # サンプル回答
                    'current': str(i),
                    'next': '1'
                }
                answer_response = session.post(f'{base_url}/answer', data=answer_data)
                
                if answer_response.status_code == 200:
                    print(f"OK 問題{current_question_num}回答処理成功")
                    
                    # カテゴリ情報の確認
                    answer_content = answer_response.text
                    if "河川" in answer_content or "砂防" in answer_content:
                        categories_found.add("河川・砂防")
                    
                    # 他分野の混在チェック
                    other_categories = ["道路", "都市計画", "造園", "建設環境", "鋼構造", "コンクリート", "土質", "基礎", "施工", "上下水道", "森林", "農業", "トンネル"]
                    for other_cat in other_categories:
                        if other_cat in answer_content:
                            categories_found.add(other_cat)
                            test_results['mixing_detected'] = True
                            print(f"警告 分野混在検出: {other_cat}")
                else:
                    test_results['errors'].append(f"問題{current_question_num}回答処理失敗: {answer_response.status_code}")
                    print(f"NG 問題{current_question_num}回答処理失敗: {answer_response.status_code}")
                
                time.sleep(0.5)  # サーバー負荷軽減
        
        test_results['question_numbers_left_side'] = question_numbers_found
        
        print("\nステップ5: 最終回答と結果画面確認")
        
        # 最後の問題（10問目）の回答
        final_answer_data = {
            'answer': '1',
            'current': '9',
            'submit': '1'
        }
        
        final_response = session.post(f'{base_url}/answer', data=final_answer_data)
        if final_response.status_code == 200:
            print("OK 最終回答処理成功")
            
            # 結果画面の確認
            results_content = final_response.text
            if "結果" in results_content or "score" in results_content.lower():
                test_results['final_results_verified'] = True
                print("OK 結果画面表示確認")
            else:
                test_results['final_results_verified'] = False
                print("NG 結果画面が表示されていない")
        else:
            test_results['errors'].append(f"最終回答処理失敗: {final_response.status_code}")
            print(f"NG 最終回答処理失敗: {final_response.status_code}")
        
        # カテゴリ一貫性の確認
        if len(categories_found) == 1 and "河川・砂防" in categories_found:
            test_results['category_consistency'] = True
            print("OK カテゴリ一貫性確認: 河川・砂防部門のみ")
        elif len(categories_found) > 1:
            test_results['category_consistency'] = False
            test_results['mixing_detected'] = True
            print(f"NG カテゴリ混在検出: {list(categories_found)}")
        else:
            test_results['category_consistency'] = False
            print("NG カテゴリが確認できない")
        
        # 最終テスト状況判定
        if (len(test_results['errors']) == 0 and 
            len(test_results['question_numbers_left_side']) == 10 and
            test_results['category_consistency'] and
            not test_results['mixing_detected'] and
            test_results['final_results_verified']):
            test_results['test_status'] = 'success'
            print("\nOK 河川・砂防部門完全テスト成功")
        else:
            test_results['test_status'] = 'failed'
            print("\nNG 河川・砂防部門完全テスト失敗")
    
    except Exception as e:
        test_results['errors'].append(f"テスト実行中の例外: {str(e)}")
        test_results['test_status'] = 'error'
        print(f"ERROR テスト実行中の例外: {e}")
    
    # 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"river_sabo_test_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nテスト結果保存: {result_file}")
    
    # 結果サマリー表示
    print("\n" + "=" * 100)
    print("河川・砂防部門完全テスト結果サマリー（絶対に嘘なし）")
    print("=" * 100)
    print(f"テスト状況: {test_results['test_status']}")
    print(f"エラー数: {len(test_results['errors'])}")
    print(f"左側問題番号確認: {len(test_results['question_numbers_left_side'])}/10")
    print(f"カテゴリ一貫性: {test_results['category_consistency']}")
    print(f"分野混在検出: {test_results['mixing_detected']}")
    print(f"結果画面確認: {test_results['final_results_verified']}")
    
    if test_results['errors']:
        print("\n検出されたエラー:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    return test_results

if __name__ == "__main__":
    result = river_sabo_complete_test()
    
    # 終了コード設定
    if result['test_status'] == 'success':
        sys.exit(0)
    else:
        sys.exit(1)