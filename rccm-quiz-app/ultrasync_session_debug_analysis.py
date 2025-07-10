#!/usr/bin/env python3
# 🛡️ ULTRASYNC セッション状態詳細調査ツール

import requests
import json
from datetime import datetime
import re

def analyze_session_state():
    """セッション状態の詳細調査（副作用ゼロ）"""
    
    print('🛡️ ULTRASYNC セッション状態詳細調査開始')
    print('=' * 60)
    
    # セッション保持のためのセッションオブジェクト
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ステップ1: ホームページアクセス（セッション初期化）
        print('ステップ1: ホームページアクセス（セッション初期化）')
        response = session.get(base_url, timeout=15)
        print(f'  応答: {response.status_code}')
        
        # セッションクッキーの確認
        cookies = session.cookies
        print(f'  セッションクッキー数: {len(cookies)}')
        for cookie in cookies:
            print(f'    {cookie.name}: {cookie.value[:50]}...')
        
        # ステップ2: 基礎科目試験開始（セッション作成）
        print('ステップ2: 基礎科目試験開始（セッション作成）')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        
        # POSTリクエストでセッション作成
        response = session.post(start_url, data=data, allow_redirects=False, timeout=15)
        print(f'  POST応答: {response.status_code}')
        
        # リダイレクト先の確認
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '')
            print(f'  リダイレクト先: {location}')
        
        # ステップ3: exam_questionに直接アクセスしてセッション状態を確認
        print('ステップ3: exam_questionへの直接アクセス（セッション状態確認）')
        
        # 直接exam_questionにアクセス
        exam_question_response = session.get(f'{base_url}/exam_question', allow_redirects=False, timeout=15)
        print(f'  exam_question応答: {exam_question_response.status_code}')
        
        if exam_question_response.status_code in [301, 302, 303, 307, 308]:
            redirect_location = exam_question_response.headers.get('Location', '')
            print(f'  exam_questionリダイレクト先: {redirect_location}')
            
            # リダイレクト先の分析
            if 'exam_simulator' in redirect_location:
                print('  ❌ 問題: exam_simulatorにリダイレクトされている')
            elif 'exam' in redirect_location and 'simulator' not in redirect_location:
                print('  ✅ 正常: examにリダイレクトされている')
            else:
                print(f'  ⚠️ 不明なリダイレクト先: {redirect_location}')
        elif exam_question_response.status_code == 200:
            print('  ✅ exam_questionが直接表示されている')
        else:
            print(f'  ❌ 予期しない応答: {exam_question_response.status_code}')
        
        # ステップ4: セッション情報のHTMLからの抽出試行
        print('ステップ4: セッション情報のHTMLからの抽出試行')
        
        # 最終的なページを取得
        final_response = session.get(f'{base_url}/exam_question', allow_redirects=True, timeout=15)
        print(f'  最終到達URL: {final_response.url}')
        print(f'  最終応答: {final_response.status_code}')
        
        if final_response.status_code == 200:
            content = final_response.text
            
            # JavaScriptやHTMLからセッション情報を抽出
            session_patterns = [
                (r'exam_session[\'\"]\s*:\s*({[^}]+})', 'exam_session JSON'),
                (r'session\[\'exam_type\'\]\s*=\s*[\'\"](.*?)[\'\"]', 'exam_type'),
                (r'exam_type[\'\"]\s*:\s*[\'\"](.*?)[\'\"]', 'exam_type JSON'),
                (r'基礎科目', '基礎科目キーワード'),
                (r'専門科目', '専門科目キーワード'),
                (r'status[\'\"]\s*:\s*[\'\"](.*?)[\'\"]', 'セッション状態')
            ]
            
            for pattern, description in session_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f'  ✅ {description}: {matches[0][:100]}...')
                else:
                    print(f'  ❌ {description}: 見つからない')
            
            # HTMLの構造分析
            print('  HTMLの構造分析:')
            print(f'    コンテンツ長: {len(content)}文字')
            print(f'    フォーム数: {content.count("<form")}')
            print(f'    input要素数: {content.count("<input")}')
            print(f'    CSRFトークン: {"csrf_token" in content}')
            
            # タイトルとメインコンテンツの確認
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                print(f'    ページタイトル: {title_match.group(1)}')
        
        # ステップ5: デバッグエンドポイントの確認（存在する場合）
        print('ステップ5: デバッグエンドポイントの確認')
        
        debug_endpoints = [
            '/debug/session',
            '/debug/session_info',
            '/api/debug/session',
            '/status',
            '/health'
        ]
        
        for endpoint in debug_endpoints:
            try:
                debug_response = session.get(f'{base_url}{endpoint}', timeout=10)
                if debug_response.status_code == 200:
                    print(f'  ✅ {endpoint}: 利用可能')
                    # JSON応答の場合は内容を一部表示
                    try:
                        debug_data = debug_response.json()
                        print(f'    内容: {str(debug_data)[:200]}...')
                    except:
                        print(f'    内容: {debug_response.text[:100]}...')
                else:
                    print(f'  ❌ {endpoint}: {debug_response.status_code}')
            except Exception as e:
                print(f'  ❌ {endpoint}: エラー')
        
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC セッション状態詳細調査完了')
        
        # 調査結果のまとめ
        analysis_summary = {
            'session_cookies': len(session.cookies),
            'exam_question_redirect': exam_question_response.status_code,
            'final_url': final_response.url,
            'final_status': final_response.status_code,
            'form_count': content.count('<form') if 'content' in locals() else 0,
            'has_csrf_token': 'csrf_token' in content if 'content' in locals() else False,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('ultrasync_session_debug_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_summary, f, ensure_ascii=False, indent=2)
        
        print(f'調査結果保存: ultrasync_session_debug_results.json')
        
        return analysis_summary
        
    except Exception as e:
        print(f'調査中にエラー: {e}')
        return None

if __name__ == '__main__':
    results = analyze_session_state()