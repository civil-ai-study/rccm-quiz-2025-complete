#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のブラウザ動作をシミュレートした上下水道部門テスト
"""

from app import app
import time

def real_browser_simulation():
    """実際のブラウザ動作をシミュレートしたテスト"""
    print("=== 上下水道部門 実ブラウザシミュレーション ===")
    
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Multiple attempts to simulate real conditions
    for attempt in range(5):
        print(f"\n試行 {attempt + 1}/5:")
        
        with app.test_client() as client:
            try:
                # Simulate fresh browser session
                with client.session_transaction() as sess:
                    sess.clear()
                    sess['user_name'] = f'browser_sim_{attempt}'
                    sess.modified = True
                
                # Step 1: Access home page first (like real browser)
                print("  1. ホームページアクセス...")
                resp_home = client.get('/')
                print(f"     ホーム: {resp_home.status_code}")
                
                # Step 2: Department selection
                print("  2. 上下水道部門選択...")
                resp_dept = client.get('/quiz_department/上下水道')
                print(f"     部門選択: {resp_dept.status_code}")
                
                if resp_dept.status_code != 302:
                    print(f"     ERROR: 部門選択失敗 - {resp_dept.status_code}")
                    continue
                
                # Step 3: Follow redirect to exam
                print("  3. 試験画面への遷移...")
                resp_exam = client.get('/exam')
                print(f"     試験画面: {resp_exam.status_code}")
                
                if resp_exam.status_code == 500:
                    print("     ERROR: 内部サーバーエラー発生")
                    content = resp_exam.data.decode('utf-8', errors='ignore')
                    if '処理中に問題が発生しました' in content:
                        print("     確認: '処理中に問題が発生しました' エラー再現")
                        
                        # Extract error details
                        lines = content.split('\n')
                        for line in lines:
                            if 'エラー' in line or 'Error' in line or 'Exception' in line:
                                print(f"     エラー詳細: {line.strip()}")
                    else:
                        print(f"     エラー内容（最初の200文字）: {content[:200]}")
                    continue
                elif resp_exam.status_code == 200:
                    print("     SUCCESS: 正常に問題表示")
                    
                    # Check HTML content for issues
                    content = resp_exam.data.decode('utf-8', errors='ignore')
                    content_length = len(content)
                    print(f"     HTMLサイズ: {content_length}文字")
                    
                    # Look for error indicators in HTML
                    if '処理中に問題が発生しました' in content:
                        print("     WARNING: HTML内にエラーメッセージ検出")
                    elif content_length < 5000:
                        print("     WARNING: HTMLサイズが小さすぎる可能性")
                    else:
                        print("     問題表示正常")
                        
                        # Try answering
                        print("  4. 問題回答テスト...")
                        resp_answer = client.post('/exam', data={'answer': 'A'})
                        print(f"     回答処理: {resp_answer.status_code}")
                        
                        if resp_answer.status_code == 302:
                            print("     SUCCESS: 回答処理正常")
                        else:
                            print(f"     ERROR: 回答処理失敗 - {resp_answer.status_code}")
                else:
                    print(f"     予期しないステータス: {resp_exam.status_code}")
                
            except Exception as e:
                print(f"     EXCEPTION: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Small delay between attempts
        time.sleep(0.1)
    
    print("\n=== シミュレーション完了 ===")

def check_error_conditions():
    """エラー発生条件をチェック"""
    print("\n=== エラー発生条件チェック ===")
    
    # Check if there are any specific conditions that cause errors
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Test with different session states
    test_conditions = [
        {'name': 'Empty session', 'setup': lambda sess: sess.clear()},
        {'name': 'Missing user_name', 'setup': lambda sess: (sess.clear(), sess.update({'other_key': 'value'}))},
        {'name': 'Invalid user_name', 'setup': lambda sess: (sess.clear(), sess.update({'user_name': ''}))},
    ]
    
    for condition in test_conditions:
        print(f"\n条件: {condition['name']}")
        
        with app.test_client() as client:
            try:
                with client.session_transaction() as sess:
                    condition['setup'](sess)
                    sess.modified = True
                
                resp = client.get('/quiz_department/上下水道')
                print(f"  部門選択: {resp.status_code}")
                
                if resp.status_code == 302:
                    resp_exam = client.get('/exam')
                    print(f"  問題表示: {resp_exam.status_code}")
                    
                    if resp_exam.status_code == 500:
                        content = resp_exam.data.decode('utf-8', errors='ignore')
                        if '処理中に問題が発生しました' in content:
                            print(f"  ERROR REPRODUCED: {condition['name']}でエラー再現")
                            return condition['name']
                
            except Exception as e:
                print(f"  EXCEPTION: {str(e)}")
    
    return None

if __name__ == "__main__":
    real_browser_simulation()
    error_condition = check_error_conditions()
    
    if error_condition:
        print(f"\nエラー再現条件特定: {error_condition}")
    else:
        print("\nエラー再現せず - 別の原因の可能性")