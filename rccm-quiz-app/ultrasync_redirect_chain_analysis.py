#!/usr/bin/env python3
# 🛡️ ULTRASYNC リダイレクトチェーン詳細分析

import requests
import json
from datetime import datetime

def analyze_redirect_chain():
    """リダイレクトチェーンの詳細分析"""
    
    print('🛡️ ULTRASYNC リダイレクトチェーン分析開始')
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
        
        # ステップ2: 基礎科目試験開始（リダイレクト追跡）
        print('ステップ2: 基礎科目試験開始（リダイレクト追跡）')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        
        # allow_redirects=Falseでリダイレクトを手動制御
        response = session.post(start_url, data=data, allow_redirects=False, timeout=30)
        print(f'  POST /start_exam/基礎科目: {response.status_code}')
        
        redirect_count = 0
        current_url = start_url
        
        while response.status_code in [301, 302, 303, 307, 308] and redirect_count < 10:
            redirect_count += 1
            location = response.headers.get('Location', '')
            print(f'  リダイレクト{redirect_count}: {response.status_code} → {location}')
            
            # 相対URLの場合は絶対URLに変換
            if location.startswith('/'):
                location = base_url + location
            
            current_url = location
            response = session.get(location, allow_redirects=False, timeout=30)
        
        # 最終的なレスポンス
        print(f'  最終応答: {response.status_code}')
        print(f'  最終URL: {current_url}')
        print(f'  総リダイレクト数: {redirect_count}')
        
        # ステップ3: 最終的なページ内容の分析
        if response.status_code == 200:
            print('ステップ3: 最終ページ内容の分析')
            
            # 最終ページで追加のリダイレクト指示を確認
            if redirect_count > 0:
                final_response = session.get(current_url, allow_redirects=True, timeout=30)
                print(f'  最終自動リダイレクト後: {final_response.status_code}')
                print(f'  最終到達URL: {final_response.url}')
                
                content = final_response.text
            else:
                content = response.text
            
            # フォーム要素の確認
            form_count = content.count('<form')
            print(f'  フォーム要素数: {form_count}')
            
            # 特定のキーワードの確認
            keywords = [
                ('exam_simulator', 'exam_simulatorキーワード'),
                ('exam_question', 'exam_questionキーワード'),
                ('/exam', '/examパス'),
                ('csrf_token', 'CSRFトークン'),
                ('name="qid"', '問題ID'),
                ('name="answer"', '回答フィールド')
            ]
            
            for keyword, description in keywords:
                if keyword in content:
                    print(f'  ✅ {description}: 存在')
                else:
                    print(f'  ❌ {description}: 不存在')
        
        # ステップ4: 直接的なルート確認
        print('ステップ4: 直接的なルート確認')
        
        routes_to_check = [
            '/exam_question',
            '/exam',
            '/exam_simulator'
        ]
        
        for route in routes_to_check:
            try:
                route_response = session.get(f'{base_url}{route}', allow_redirects=False, timeout=15)
                print(f'  {route}: {route_response.status_code}')
                
                if route_response.status_code in [301, 302, 303, 307, 308]:
                    location = route_response.headers.get('Location', '')
                    print(f'    → リダイレクト先: {location}')
                    
            except Exception as e:
                print(f'  {route}: エラー - {e}')
        
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC リダイレクトチェーン分析完了')
        
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == '__main__':
    analyze_redirect_chain()