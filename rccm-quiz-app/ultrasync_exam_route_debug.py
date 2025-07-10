#!/usr/bin/env python3
# 🛡️ ULTRASYNC /examルートの詳細調査

import requests
import json
from datetime import datetime
import re

def debug_exam_route():
    """副作用ゼロで/examルートの問題を調査"""
    
    print('🛡️ ULTRASYNC /examルート詳細調査開始')
    print('=' * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ステップ1: 基礎科目試験開始でセッション作成
        print('ステップ1: 基礎科目試験開始でセッション作成')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        response = session.post(start_url, data=data, allow_redirects=False, timeout=15)
        print(f'  start_exam応答: {response.status_code}')
        
        # ステップ2: /examルートに直接アクセス
        print('ステップ2: /examルートに直接アクセス')
        exam_response = session.get(f'{base_url}/exam', timeout=15)
        print(f'  /exam応答: {response.status_code}')
        print(f'  /exam URL: {exam_response.url}')
        
        # ステップ3: /examの応答内容詳細分析
        print('ステップ3: /examの応答内容詳細分析')
        if exam_response.status_code == 200:
            content = exam_response.text
            
            # タイトル確認
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                title = title_match.group(1)
                print(f'  ページタイトル: {title}')
                
                if 'エラー' in title:
                    print('  ❌ エラーページが表示されている')
                    
                    # エラーメッセージの抽出
                    error_patterns = [
                        r'<div[^>]*class="error[^"]*"[^>]*>(.*?)</div>',
                        r'<p[^>]*class="error[^"]*"[^>]*>(.*?)</p>',
                        r'<span[^>]*class="error[^"]*"[^>]*>(.*?)</span>',
                        r'エラー[^<]*：([^<]+)',
                        r'Error[^<]*:([^<]+)'
                    ]
                    
                    for pattern in error_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                        if matches:
                            for match in matches:
                                error_msg = re.sub(r'<[^>]+>', '', match).strip()
                                if error_msg:
                                    print(f'  エラーメッセージ: {error_msg}')
                else:
                    print('  ✅ 正常なページが表示されている')
            
            # フォーム要素の確認
            form_count = content.count('<form')
            input_count = content.count('<input')
            print(f'  フォーム数: {form_count}')
            print(f'  入力要素数: {input_count}')
            
            # 重要要素の確認
            elements = [
                ('csrf_token', 'CSRFトークン'),
                ('name="qid"', '問題ID'),
                ('name="answer"', '回答フィールド'),
                ('問題', '問題テキスト'),
                ('選択肢', '選択肢'),
                ('A)', '選択肢A'),
                ('B)', '選択肢B'),
                ('C)', '選択肢C'),
                ('D)', '選択肢D')
            ]
            
            for element, description in elements:
                if element in content:
                    print(f'  ✅ {description}: 存在')
                else:
                    print(f'  ❌ {description}: 不存在')
        
        # ステップ4: セッション状態の確認
        print('ステップ4: セッション状態の確認')
        debug_response = session.get(f'{base_url}/debug/session', timeout=15)
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f'  セッション状態: {debug_data}')
            
            # 重要なセッション値の確認
            exam_question_ids = debug_data.get('exam_question_ids', [])
            exam_current = debug_data.get('exam_current', 0)
            print(f'  問題ID数: {len(exam_question_ids)}')
            print(f'  現在位置: {exam_current}')
            
            if exam_question_ids:
                print(f'  問題ID例: {exam_question_ids[:3]}...')
            else:
                print('  ❌ 問題IDが空 - これがエラーの原因かもしれません')
        
        # ステップ5: 基礎科目データの確認
        print('ステップ5: 基礎科目データの確認')
        debug_info_response = session.get(f'{base_url}/debug/session_info', timeout=15)
        if debug_info_response.status_code == 200:
            debug_info_data = debug_info_response.json()
            debug_info = debug_info_data.get('debug_info', {})
            
            data_source = debug_info.get('data_source', '')
            questions_count = debug_info.get('questions_count', 0)
            exam_type = debug_info.get('exam_type', '')
            
            print(f'  データソース: {data_source}')
            print(f'  問題数: {questions_count}')
            print(f'  試験タイプ: {exam_type}')
            
            if data_source == 'basic' and questions_count > 0:
                print('  ✅ 基礎科目データは正常に読み込まれている')
            else:
                print('  ❌ 基礎科目データの読み込みに問題がある')
        
        # ステップ6: パラメータ付きアクセスのテスト
        print('ステップ6: パラメータ付きアクセスのテスト')
        
        # 基礎科目のパラメータ付きアクセス
        param_url = f'{base_url}/exam?question_type=basic'
        param_response = session.get(param_url, timeout=15)
        print(f'  パラメータ付きアクセス: {param_response.status_code}')
        
        if param_response.status_code == 200:
            param_content = param_response.text
            param_title_match = re.search(r'<title>(.*?)</title>', param_content)
            if param_title_match:
                param_title = param_title_match.group(1)
                print(f'  パラメータ付きページタイトル: {param_title}')
                
                if 'エラー' not in param_title:
                    print('  ✅ パラメータ付きアクセスは成功')
                else:
                    print('  ❌ パラメータ付きアクセスでもエラー')
        
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC /examルート詳細調査完了')
        
    except Exception as e:
        print(f'調査中にエラー: {e}')
        return None

if __name__ == '__main__':
    debug_exam_route()