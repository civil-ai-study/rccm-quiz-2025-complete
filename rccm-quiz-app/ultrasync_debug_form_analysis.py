#!/usr/bin/env python3
# 🛡️ ULTRASYNC フォームデータ解析ツール

import requests
import json
from datetime import datetime
import re

def analyze_form_data_extraction():
    """フォームデータ抽出の詳細分析"""
    
    print('🛡️ ULTRASYNC フォームデータ解析開始')
    print('=' * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ステップ1: ホームページアクセス
        print('ステップ1: ホームページアクセス')
        response = session.get(base_url, timeout=30)
        print(f'  応答: {response.status_code}')
        
        # ステップ2: 基礎科目試験開始
        print('ステップ2: 基礎科目試験開始')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        response = session.post(start_url, data=data, allow_redirects=True, timeout=30)
        print(f'  応答: {response.status_code}')
        print(f'  URL: {response.url}')
        
        if response.status_code == 200:
            # ステップ3: HTMLコンテンツの詳細分析
            print('ステップ3: HTMLコンテンツの詳細分析')
            content = response.text
            
            # 正規表現でHTMLを解析
            # フォーム要素の確認
            form_patterns = re.findall(r'<form[^>]*>(.*?)</form>', content, re.DOTALL)
            print(f'  フォーム数: {len(form_patterns)}')
            
            if form_patterns:
                form_content = form_patterns[0]  # 最初のフォーム
                
                # フォームアクションの確認
                action_match = re.search(r'action="([^"]*)"', content)
                if action_match:
                    print(f'  フォームアクション: {action_match.group(1)}')
                
                # フォームメソッドの確認
                method_match = re.search(r'method="([^"]*)"', content)
                if method_match:
                    print(f'  フォームメソッド: {method_match.group(1)}')
                
                # 入力フィールドの確認
                input_patterns = re.findall(r'<input[^>]*>', form_content)
                print(f'  入力フィールド数: {len(input_patterns)}')
                
                for i, input_field in enumerate(input_patterns):
                    name_match = re.search(r'name="([^"]*)"', input_field)
                    value_match = re.search(r'value="([^"]*)"', input_field)
                    type_match = re.search(r'type="([^"]*)"', input_field)
                    
                    name = name_match.group(1) if name_match else 'None'
                    value = value_match.group(1) if value_match else 'None'
                    input_type = type_match.group(1) if type_match else 'None'
                    
                    print(f'    フィールド{i+1}: name="{name}", value="{value}", type="{input_type}"')
                
                # CSRFトークンの確認
                csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', content)
                if csrf_match:
                    csrf_value = csrf_match.group(1)
                    print(f'  ✅ CSRFトークン存在: {csrf_value[:20]}...')
                else:
                    print('  ❌ CSRFトークンが見つからない')
                
                # 問題IDの確認
                qid_match = re.search(r'<input[^>]*name="qid"[^>]*value="([^"]*)"', content)
                if qid_match:
                    qid_value = qid_match.group(1)
                    print(f'  ✅ 問題ID存在: {qid_value}')
                else:
                    print('  ❌ 問題IDが見つからない')
                
                # 回答選択肢の確認
                answer_matches = re.findall(r'<input[^>]*name="answer"[^>]*value="([^"]*)"', content)
                print(f'  回答選択肢数: {len(answer_matches)}')
                for answer_value in answer_matches:
                    print(f'    選択肢: value="{answer_value}"')
                
                # ステップ4: 実際のフォームデータ構築
                print('ステップ4: 実際のフォームデータ構築')
                
                form_data = {}
                
                # CSRFトークンの取得
                if csrf_match:
                    form_data['csrf_token'] = csrf_match.group(1)
                
                # 問題IDの取得
                if qid_match:
                    form_data['qid'] = qid_match.group(1)
                
                # 経過時間の設定
                form_data['elapsed'] = '0'
                
                # テスト回答の設定
                form_data['answer'] = 'A'
                
                # セッション初期化フラグ
                session_match = re.search(r'<input[^>]*name="session_initialized"[^>]*value="([^"]*)"', content)
                if session_match:
                    form_data['session_initialized'] = session_match.group(1)
                
                print(f'  構築されたフォームデータ: {form_data}')
                
                # ステップ5: 実際のフォーム送信テスト
                print('ステップ5: 実際のフォーム送信テスト')
                
                test_response = session.post(f'{base_url}/exam', data=form_data, allow_redirects=False, timeout=30)
                print(f'  テスト送信応答: {test_response.status_code}')
                
                if test_response.status_code == 200:
                    print('  ✅ フォーム送信成功！')
                    print(f'  応答URL: {test_response.url}')
                    print(f'  応答内容サイズ: {len(test_response.text)}文字')
                    
                    # 成功時の応答内容の分析
                    response_content = test_response.text
                    if '次の問題' in response_content:
                        print('  ✅ 次の問題への遷移確認')
                    elif '結果' in response_content:
                        print('  ✅ 結果画面への遷移確認')
                    else:
                        print('  ⚠️ 不明な応答内容')
                        
                elif test_response.status_code == 400:
                    print('  ❌ 400エラー継続')
                    print(f'  応答内容: {test_response.text[:200]}...')
                    
                    # 400エラーの詳細分析
                    error_content = test_response.text
                    if 'CSRF' in error_content:
                        print('  原因: CSRFトークンエラー')
                    elif 'セッション' in error_content:
                        print('  原因: セッションエラー')
                    elif 'フィールド' in error_content:
                        print('  原因: フィールドエラー')
                    else:
                        print('  原因: 不明なエラー')
                        
                else:
                    print(f'  予期しない応答: {test_response.status_code}')
                
            else:
                print('  ❌ フォームが見つからない')
                
        else:
            print(f'  試験開始失敗: {response.status_code}')
            print(f'  内容: {response.text[:300]}...')
        
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC フォームデータ解析完了')
        
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == '__main__':
    analyze_form_data_extraction()