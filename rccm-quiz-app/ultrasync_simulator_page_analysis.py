#!/usr/bin/env python3
# 🛡️ ULTRASYNC exam_simulatorページの詳細分析

import requests
import json
from datetime import datetime
import re

def analyze_exam_simulator_page():
    """exam_simulatorページの詳細分析"""
    
    print('🛡️ ULTRASYNC exam_simulatorページ分析開始')
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
        print(f'  最終URL: {response.url}')
        
        if response.status_code == 200:
            # ステップ3: ページ内容の詳細分析
            print('ステップ3: ページ内容の詳細分析')
            content = response.text
            
            # ページのタイトル確認
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                print(f'  ページタイトル: {title_match.group(1)}')
            
            # コンテンツの長さ
            print(f'  コンテンツ長: {len(content)}文字')
            
            # フォーム要素の詳細確認
            form_patterns = re.findall(r'<form[^>]*>(.*?)</form>', content, re.DOTALL)
            print(f'  フォーム数: {len(form_patterns)}')
            
            # 実際のHTMLコンテンツの最初の500文字を表示
            print('  HTMLコンテンツの最初の500文字:')
            print(f'    {content[:500]}...')
            
            # エラーメッセージの確認
            error_keywords = ['error', 'エラー', 'Error', '404', '500', '400', 'not found', '見つからない']
            for keyword in error_keywords:
                if keyword in content.lower():
                    print(f'  ⚠️ エラー関連キーワード発見: {keyword}')
            
            # JavaScript関連の確認
            script_patterns = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            print(f'  JavaScriptブロック数: {len(script_patterns)}')
            
            # 問題関連の要素確認
            question_keywords = ['question', '問題', 'quiz', 'exam', '試験']
            for keyword in question_keywords:
                if keyword in content.lower():
                    print(f'  ✅ 問題関連キーワード発見: {keyword}')
            
            # 特定の重要な要素の確認
            important_elements = [
                ('問題テキスト', r'class="question-text"'),
                ('選択肢', r'name="answer"'),
                ('送信ボタン', r'type="submit"'),
                ('CSRFトークン', r'name="csrf_token"'),
                ('問題ID', r'name="qid"'),
                ('フォーム', r'<form'),
                ('エラー表示', r'class="error"'),
                ('アラート', r'class="alert"')
            ]
            
            for element_name, pattern in important_elements:
                matches = re.findall(pattern, content)
                if matches:
                    print(f'  ✅ {element_name}発見: {len(matches)}個')
                else:
                    print(f'  ❌ {element_name}なし')
            
            # もしフォームが見つからない場合、リダイレクトの可能性を確認
            if len(form_patterns) == 0:
                print('  ❌ フォームが見つからない - 原因調査:')
                
                # メタリフレッシュの確認
                meta_refresh = re.search(r'<meta[^>]*http-equiv="refresh"[^>]*content="[^"]*url=([^"]*)"', content, re.IGNORECASE)
                if meta_refresh:
                    print(f'    メタリフレッシュによるリダイレクト: {meta_refresh.group(1)}')
                
                # JavaScriptリダイレクトの確認
                js_redirect = re.search(r'location\.href\s*=\s*["\']([^"\']*)["\']', content)
                if js_redirect:
                    print(f'    JavaScriptリダイレクト: {js_redirect.group(1)}')
                
                # 条件分岐の確認
                if 'if' in content.lower() and 'redirect' in content.lower():
                    print('    条件分岐によるリダイレクトの可能性あり')
                
                # エラーメッセージの詳細確認
                error_patterns = [
                    r'エラー[^<]*',
                    r'Error[^<]*',
                    r'問題[^<]*見つかりません',
                    r'セッション[^<]*無効',
                    r'データ[^<]*見つかりません'
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f'    エラーメッセージ: {matches[0]}')
                
            # ステップ4: exam_simulatorからexamへの直接アクセステスト
            print('ステップ4: /examへの直接アクセステスト')
            
            # クッキーを維持して直接/examにアクセス
            exam_response = session.get(f'{base_url}/exam', timeout=30)
            print(f'  /exam直接アクセス: {exam_response.status_code}')
            
            if exam_response.status_code == 200:
                exam_content = exam_response.text
                exam_forms = re.findall(r'<form[^>]*>(.*?)</form>', exam_content, re.DOTALL)
                print(f'  /examでのフォーム数: {len(exam_forms)}')
                
                # /examで問題が表示されるかチェック
                if 'name="answer"' in exam_content:
                    print('  ✅ /examで問題フォームが表示される')
                else:
                    print('  ❌ /examでも問題フォームが表示されない')
                
        else:
            print(f'  試験開始失敗: {response.status_code}')
            
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC exam_simulatorページ分析完了')
        
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == '__main__':
    analyze_exam_simulator_page()