#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLパターンの詳細確認
"""

from app import app

def check_html_pattern():
    """施工計画部門のHTMLパターンを詳細確認"""
    print("=== HTMLパターン確認 ===")
    
    with app.test_client() as client:
        # セッション初期化
        with client.session_transaction() as sess:
            sess.clear()
            sess['user_name'] = 'test'
        
        dept = '施工計画'
        print(f"対象部門: {dept}")
        
        # quiz_departmentアクセス → examアクセス
        resp1 = client.get(f'/quiz_department/{dept}')
        
        if resp1.status_code == 302:
            location = resp1.headers.get('Location', '')
            resp2 = client.get(location)
            
            if resp2.status_code == 200:
                html = resp2.data.decode('utf-8', errors='ignore')
                
                # 全部門テストと同じ判定条件
                has_value_a = 'value="A"' in html
                has_value_b = 'value="B"' in html
                has_value_c = 'value="C"' in html
                has_value_d = 'value="D"' in html
                
                print(f"HTML判定結果:")
                print(f"  value=\"A\": {has_value_a}")
                print(f"  value=\"B\": {has_value_b}")
                print(f"  value=\"C\": {has_value_c}")
                print(f"  value=\"D\": {has_value_d}")
                
                has_options = has_value_a and has_value_b and has_value_c and has_value_d
                print(f"  総合判定: {has_options}")
                
                # 詳細分析: HTMLサイズとradioボタン数
                html_size = len(html)
                radio_count = html.count('type="radio"')
                question_text_count = html.count('question-text')
                option_text_count = html.count('option-text')
                
                print(f"\nHTML詳細:")
                print(f"  HTMLサイズ: {html_size}文字")
                print(f"  radioボタン数: {radio_count}")
                print(f"  question-text: {question_text_count}")
                print(f"  option-text: {option_text_count}")
                
                # エラーメッセージの有無
                if 'error' in html.lower() or 'エラー' in html:
                    print("  ⚠️ エラーメッセージが含まれています")
                    # エラー部分を抽出
                    error_keywords = ['error', 'エラー', '問題が発生', 'failed']
                    for keyword in error_keywords:
                        if keyword in html.lower():
                            start = html.lower().find(keyword)
                            if start != -1:
                                context = html[max(0, start-50):start+100]
                                print(f"    '{keyword}' 周辺: {context}")
                                break
                else:
                    print("  ✅ エラーメッセージは含まれていません")
                
                return has_options
            else:
                print(f"examページエラー: {resp2.status_code}")
                return False
        else:
            print(f"quiz_departmentページエラー: {resp1.status_code}")
            return False

if __name__ == "__main__":
    result = check_html_pattern()
    print(f"\n最終結果: {'SUCCESS' if result else 'FAILED'}")