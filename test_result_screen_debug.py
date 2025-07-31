# -*- coding: utf-8 -*-
"""
ULTRA SYNC 結果画面アクセスフロー詳細デバッグ
副作用なし・読み取り専用での問題特定
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import sys

def debug_result_screen_access():
    """結果画面アクセスフローの詳細デバッグ"""
    print('ULTRA SYNC 結果画面アクセスフロー詳細デバッグ')
    print('=' * 60)
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    session = requests.Session()
    
    try:
        # ユーザー設定
        user_data = {'user_name': 'ULTRA_SYNC_DEBUG_USER'}
        response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        print(f'ユーザー設定: {response.status_code}')
        
        # 3問テスト開始
        exam_data = {
            'exam_type': 'specialist',
            'department': '道路',
            'question_count': '3'
        }
        response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        print(f'試験開始: {response.status_code}')
        
        # 3問回答
        for i in range(3):
            print(f'問題 {i+1}/3 処理中...')
            
            # 問題表示
            response = session.get(f'{base_url}/exam', timeout=30)
            print(f'  問題表示: {response.status_code}')
            
            if response.status_code != 200:
                print(f'  エラー: 問題表示失敗')
                break
            
            # フォーム情報抽出
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_input or not qid_input:
                print(f'  エラー: フォーム情報不足')
                break
            
            # 回答送信
            answer_data = {
                'answer': 'A',
                'qid': qid_input.get('value'),
                'elapsed': '5',
                'csrf_token': csrf_input.get('value')
            }
            
            response = session.post(f'{base_url}/exam', data=answer_data, timeout=30)
            print(f'  回答送信: {response.status_code}')
            
            # レスポンス内容チェック
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f'  リダイレクト先: {location}')
            elif response.status_code == 200:
                # 次の問題 or 結果画面かチェック
                if 'result' in response.url.lower() or '結果' in response.text:
                    print(f'  結果画面検出')
                    break
                elif 'question' in response.text or '問題' in response.text:
                    print(f'  次の問題検出')
        
        print('\n=== 最終状態確認 ===')
        
        # 1. /exam への最終アクセス
        response = session.get(f'{base_url}/exam', timeout=30)
        print(f'/exam アクセス: {response.status_code}')
        if response.status_code == 302:
            print(f'  リダイレクト先: {response.headers.get("Location", "")}')
        elif response.status_code == 200:
            if '結果' in response.text or 'result' in response.text.lower():
                print('  結果画面内容検出')
            elif '問題' in response.text:
                print('  問題画面内容検出')
            else:
                print('  不明な内容')
        
        # 2. /result への直接アクセス
        response = session.get(f'{base_url}/result', timeout=30)
        print(f'/result 直接アクセス: {response.status_code}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f'  ページタイトル: {title.get_text()}')
            
            # 結果画面要素チェック
            score_elements = soup.find_all('div', class_='score-value')
            accuracy_elements = soup.find_all('div', class_='accuracy-value')
            action_buttons = soup.find_all('a', class_='action-btn')
            
            print(f'  スコア要素数: {len(score_elements)}')
            print(f'  正答率要素数: {len(accuracy_elements)}')
            print(f'  アクションボタン数: {len(action_buttons)}')
            
            if '結果' in response.text:
                print('  結果画面内容確認: OK')
            else:
                print('  結果画面内容確認: NG')
        else:
            print(f'  アクセス失敗: {response.status_code}')
        
        # 3. セッション状態確認（可能な範囲で）
        print('\n=== セッション状態推定 ===')
        response = session.get(f'{base_url}/', timeout=30)  # ホームページアクセス
        if '最近の結果' in response.text or 'history' in response.text.lower():
            print('セッションに履歴データあり（推定）')
        else:
            print('セッション履歴不明')
    
    except Exception as e:
        print(f'デバッグエラー: {e}')
    
    finally:
        session.close()

if __name__ == '__main__':
    debug_result_screen_access()