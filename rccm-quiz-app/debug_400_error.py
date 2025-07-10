#!/usr/bin/env python3
# 400エラー詳細調査

import requests
import json
from datetime import datetime

def debug_400_error():
    """400エラーの詳細調査"""
    
    print('🔍 400エラー詳細調査開始')
    print('=' * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # 1. ホームページアクセス
        print('1. ホームページアクセス')
        response = session.get(base_url, timeout=30)
        print(f'  応答: {response.status_code}')
        
        # 2. 基礎科目試験開始
        print('2. 基礎科目試験開始')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        response = session.post(start_url, data=data, allow_redirects=True, timeout=30)
        print(f'  応答: {response.status_code}')
        print(f'  URL: {response.url}')
        
        if response.status_code == 200:
            # 3. 実際の問題画面の詳細分析
            print('3. 問題画面の詳細分析')
            content = response.text
            
            # フォーム要素の確認
            if '<form' in content:
                print('  ✅ フォーム要素存在')
                
                # CSRF トークンの確認
                if 'csrf_token' in content or 'csrf-token' in content:
                    print('  ✅ CSRFトークン存在')
                else:
                    print('  ⚠️ CSRFトークンなし')
                
                # セッション要素の確認
                if 'session' in content.lower():
                    print('  ✅ セッション要素存在')
                
                # 入力フィールドの確認
                if 'name="answer"' in content:
                    print('  ✅ 回答フィールド存在')
                elif 'name=' in content:
                    print('  ⚠️ 他のフィールド存在')
                    import re
                    fields = re.findall(r'name="([^"]*)"', content)
                    print(f'    フィールド一覧: {fields[:5]}')
            
            # 4. 正しいフォームデータでのテスト送信
            print('4. 正しいフォームデータでのテスト送信')
            
            # CSRFトークンの抽出
            csrf_token = None
            import re
            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f'  CSRFトークン取得: {csrf_token[:20]}...')
            
            # 適切なデータで送信テスト
            test_data = {}
            if csrf_token:
                test_data['csrf_token'] = csrf_token
            
            # 問題番号やセッション情報の確認
            question_id_match = re.search(r'question[_-]?id["\s]*[:=]["\s]*([^"\s,}]+)', content)
            if question_id_match:
                question_id = question_id_match.group(1)
                test_data['question_id'] = question_id
                print(f'  問題ID取得: {question_id}')
            
            # 選択肢の形式確認
            if 'type="radio"' in content:
                print('  ✅ ラジオボタン形式')
                test_data['answer'] = 'A'
            elif 'value="A"' in content:
                print('  ✅ 選択肢A-D存在')
                test_data['answer'] = 'A'
            
            print(f'  送信データ: {test_data}')
            
            # テスト送信
            test_response = session.post(f'{base_url}/exam', data=test_data, allow_redirects=False, timeout=30)
            print(f'  テスト送信応答: {test_response.status_code}')
            
            if test_response.status_code == 400:
                print('  400エラー詳細:')
                print(f'    応答ヘッダー: {dict(test_response.headers)}')
                print(f'    応答内容: {test_response.text[:300]}...')
            
        else:
            print(f'  試験開始失敗: {response.status_code}')
            print(f'  内容: {response.text[:300]}...')
        
    except Exception as e:
        print(f'エラー: {e}')

if __name__ == '__main__':
    debug_400_error()