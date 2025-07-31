# -*- coding: utf-8 -*-
"""
[基本機能確保-001] 4-2専門科目2問目表示問題の徹底的検証テスト
本番環境 https://rccm-quiz-2025.onrender.com での実際のテスト実行
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import sys
import traceback

def test_second_question_issue():
    """2問目表示問題を本番環境で再現テスト"""
    print('[基本機能確保-001] 4-2専門科目2問目表示問題の検証テスト実行中...')
    print('=' * 80)
    
    # セッション管理用
    session = requests.Session()
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # 1. ホームページアクセス
        print('Step 1: ホームページアクセス')
        response = session.get(base_url, timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            print('   OK ホームページアクセス成功')
        else:
            print(f'   NG ホームページアクセス失敗: {response.status_code}')
            return 'HOMEPAGE_FAILED'
        
        # 2. ユーザー名設定（テスト用）
        print('\nStep 2: ユーザー名設定')
        user_data = {'user_name': 'ULTRA_SYNC_TEST_USER'}
        response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code in [200, 302]:
            print('   OK ユーザー名設定成功')
        else:
            print(f'   NG ユーザー名設定失敗: {response.status_code}')
            return 'USER_SETUP_FAILED'
        
        # 3. 4-2専門科目開始（道路部門）
        print('\nStep 3: 4-2専門科目開始（道路部門）')
        exam_data = {
            'exam_type': 'specialist',
            'department': '道路',
            'question_count': '10'
        }
        response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code in [200, 302]:
            print('   OK 専門科目開始成功')
            if response.status_code == 302:
                print(f'   リダイレクト先: {response.headers.get("Location", "不明")}')
        else:
            print(f'   NG 専門科目開始失敗: {response.status_code}')
            print(f'   Response text preview: {response.text[:500]}')
            return 'EXAM_START_FAILED'
        
        # 4. 1問目表示確認
        print('\nStep 4: 1問目表示確認')
        response = session.get(f'{base_url}/exam', timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            print('   OK 1問目表示成功')
            # HTMLコンテンツの詳細確認
            if '選択肢' in response.text or 'option' in response.text:
                print('   OK 選択肢要素確認済み')
            else:
                print('   WARN 選択肢要素が見つからない可能性')
                print(f'   Content preview: {response.text[:1000]}')
        else:
            print(f'   NG 1問目表示失敗: {response.status_code}')
            return 'FIRST_QUESTION_FAILED'
        
        # 5. HTMLを解析してフォームデータを取得
        print('\nStep 5: 1問目フォームデータ解析')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # CSRFトークンとQIDを取得
        csrf_token = None
        qid = None
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        qid_input = soup.find('input', {'name': 'qid'})
        
        if csrf_input:
            csrf_token = csrf_input.get('value')
        if qid_input:
            qid = qid_input.get('value')
        
        print(f'   CSRFトークン: {csrf_token[:20] if csrf_token else "None"}...')
        print(f'   問題ID: {qid}')
        
        if not csrf_token or not qid:
            print('   NG 必要なフォームデータが見つからない')
            print('   DEBUG HTML Form 要素確認:')
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                print(f'     Form {i}: {form.get("action", "no action")} method={form.get("method", "GET")}')
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f'       Input: name={inp.get("name")} value={inp.get("value", "")[:50]}')
            return 'FORM_DATA_MISSING'
        
        # 6. 1問目回答送信（Aを選択）
        print('\nStep 6: 1問目回答送信（A選択）')
        
        answer_data = {
            'answer': 'A',
            'qid': qid,
            'elapsed': '10',
            'csrf_token': csrf_token
        }
        
        print(f'   送信データ: {answer_data}')
        response = session.post(f'{base_url}/exam', data=answer_data, timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code in [200, 302]:
            print('   OK 1問目回答送信成功')
            if response.status_code == 302:
                print(f'   リダイレクト先: {response.headers.get("Location", "不明")}')
        else:
            print(f'   NG 1問目回答送信失敗: {response.status_code}')
            print(f'   Response text preview: {response.text[:1000]}')
            return 'FIRST_ANSWER_FAILED'
        
        # 7. 2問目表示確認（ここが問題の箇所）
        print('\nStep 7: 2問目表示確認（問題発生箇所）')
        print('   CRITICAL TEST: ここで無効なデータ形式エラーが発生するか確認')
        
        response = session.get(f'{base_url}/exam', timeout=30)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            # エラーメッセージチェック
            if '無効なデータ形式です' in response.text:
                print('   ERROR 2問目で無効なデータ形式エラー発生!')
                print('   DEBUG エラー再現成功 - 修正が必要')
                
                # エラー詳細を抽出
                print('\n   DEBUG エラー詳細情報:')
                soup2 = BeautifulSoup(response.text, 'html.parser')
                error_elements = soup2.find_all(text=lambda text: '無効なデータ形式' in str(text))
                for error in error_elements:
                    print(f'     エラーテキスト: {error.strip()}')
                
                return 'ERROR_REPRODUCED'
                
            elif '処理中に問題が発生しました' in response.text:
                print('   ERROR 2問目で処理中に問題が発生しましたエラー発生!')
                print('   DEBUG 関連エラー発生 - 修正が必要')
                return 'RELATED_ERROR'
                
            elif '選択肢' in response.text or 'option' in response.text:
                print('   OK 2問目表示成功')
                print('   SUCCESS 問題は修正済みの可能性')
                
                # 2問目の内容を軽く確認
                soup2 = BeautifulSoup(response.text, 'html.parser')
                question_text = soup2.find('h3', class_='question-text')
                if question_text:
                    print(f'   問題内容: {question_text.text[:100]}...')
                
                return 'SUCCESS'
            else:
                print('   WARN 2問目表示内容に問題の可能性')
                print(f'   Content preview: {response.text[:1000]}')
                return 'SUSPICIOUS'
        else:
            print(f'   NG 2問目表示失敗: {response.status_code}')
            print(f'   Response text preview: {response.text[:1000]}')
            return 'SECOND_QUESTION_FAILED'
    
    except requests.exceptions.RequestException as e:
        print(f'ERROR ネットワークエラー: {e}')
        return 'NETWORK_ERROR'
    except Exception as e:
        print(f'ERROR 予期しないエラー: {e}')
        print(f'ERROR エラー詳細: {traceback.format_exc()}')
        return 'UNEXPECTED_ERROR'

def run_comprehensive_test():
    """包括的なテスト実行"""
    print('ULTRA SYNC 2問目表示問題検証テスト開始')
    print('=' * 80)
    
    test_results = []
    
    # 複数回テストして安定性確認
    for i in range(3):
        print(f'\nテスト実行 {i+1}/3')
        print('-' * 40)
        
        result = test_second_question_issue()
        test_results.append(result)
        
        print(f'テスト{i+1}結果: {result}')
        
        if i < 2:  # 最後のテスト以外は待機
            print('次のテスト前に5秒待機...')
            time.sleep(5)
    
    # 結果集計
    print('\n' + '=' * 80)
    print('ULTRA SYNC 2問目表示問題検証テスト結果')
    print('=' * 80)
    
    for i, result in enumerate(test_results):
        status_icon = 'OK' if result == 'SUCCESS' else 'NG' if 'ERROR' in result else 'WARN'
        print(f'テスト{i+1}: {status_icon} {result}')
    
    # 最終判定
    success_count = test_results.count('SUCCESS')
    error_count = sum(1 for r in test_results if 'ERROR' in r)
    
    print(f'\nテスト統計:')
    print(f'   成功: {success_count}/3')
    print(f'   エラー: {error_count}/3')
    print(f'   その他: {3 - success_count - error_count}/3')
    
    if success_count == 3:
        print('\n結論: 2問目表示問題は修正済み')
        return True
    elif error_count > 0:
        print('\n結論: 2問目表示問題が依然として存在')
        return False
    else:
        print('\n結論: 要追加調査')
        return None

if __name__ == '__main__':
    try:
        result = run_comprehensive_test()
        
        if result is True:
            print('\n[基本機能確保-001] 完了 - 問題修正確認済み')
            sys.exit(0)
        elif result is False:
            print('\n[基本機能確保-001] 継続 - 追加修正が必要')
            sys.exit(1)
        else:
            print('\n[基本機能確保-001] 要調査 - 結果が不明確')
            sys.exit(2)
    
    except KeyboardInterrupt:
        print('\nテスト中断')
        sys.exit(130)
    except Exception as e:
        print(f'\nテスト実行エラー: {e}')
        sys.exit(1)