#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなHTML確認
"""

from app import app

def simple_html_check():
    """シンプルなHTML内容確認"""
    print("=== シンプルHTML確認 ===")
    
    with app.test_client() as client:
        # セッション初期化
        with client.session_transaction() as sess:
            sess.clear()
            sess['user_name'] = 'test'
            sess.modified = True
        
        # 建設環境部門テスト
        resp1 = client.get('/quiz_department/建設環境')
        
        if resp1.status_code == 302:
            location = resp1.headers.get('Location', '')
            resp2 = client.get(location)
            
            if resp2.status_code == 200:
                html = resp2.data.decode('utf-8', errors='ignore')
                
                html_size = len(html)
                has_values = 'value="A"' in html and 'value="B"' in html
                
                print(f"HTMLサイズ: {html_size}")
                print(f"選択肢存在: {has_values}")
                
                # HTMLの基本構造
                print(f"HTML tag: {'<html' in html}")
                print(f"BODY tag: {'<body' in html}")
                print(f"FORM tag: {'<form' in html}")
                print(f"HTML終了: {'</html>' in html}")
                
                # エラー確認
                has_error = any(x in html.lower() for x in ['error', 'exception', 'traceback'])
                print(f"エラー存在: {has_error}")
                
                if has_error:
                    print("エラー詳細:")
                    lines = html.split('\n')
                    for i, line in enumerate(lines[:50]):  # 最初の50行
                        if any(x in line.lower() for x in ['error', 'exception', 'traceback']):
                            clean_line = ''.join(c for c in line if ord(c) >= 32 or c in '\n\r\t')
                            print(f"  Line {i}: {clean_line[:100]}")
                
                # HTMLの最後を確認
                if html_size < 20000:  # 小さいHTML（失敗ケース）の場合
                    print("\nHTML終端:")
                    end_part = html[-500:]  # 最後の500文字
                    clean_end = ''.join(c for c in end_part if ord(c) >= 32 or c in '\n\r\t')
                    print(clean_end[-200:])  # 最後の200文字を表示
                
                return has_values
        
        return False

if __name__ == "__main__":
    result = simple_html_check()
    print(f"\n結果: {'SUCCESS' if result else 'FAILED'}")