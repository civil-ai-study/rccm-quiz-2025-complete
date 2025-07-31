#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失敗時HTMLの詳細分析
"""

from app import app

def analyze_failed_html():
    """失敗時のHTMLを詳細分析"""
    print("=== 失敗時HTML詳細分析 ===")
    
    target_dept = '建設環境'
    
    with app.test_client() as client:
        # 失敗するまで繰り返し試行
        for attempt in range(10):
            print(f"\n試行 {attempt+1}/10:")
            
            # セッション初期化
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_name'] = f'test_{attempt}'
                sess.modified = True
            
            # quiz_department → exam
            resp1 = client.get(f'/quiz_department/{target_dept}')
            
            if resp1.status_code == 302:
                location = resp1.headers.get('Location', '')
                resp2 = client.get(location)
                
                if resp2.status_code == 200:
                    html = resp2.data.decode('utf-8', errors='ignore')
                    
                    has_values = (
                        'value="A"' in html and 
                        'value="B"' in html and
                        'value="C"' in html and 
                        'value="D"' in html
                    )
                    
                    html_size = len(html)
                    print(f"  HTMLサイズ: {html_size}, 成功: {has_values}")
                    
                    # 失敗ケースを発見した場合、詳細分析
                    if not has_values:
                        print("  🔍 失敗ケース発見 - 詳細分析開始")
                        
                        # HTMLの構造を確認
                        has_html_tag = '<html' in html
                        has_head_tag = '<head>' in html
                        has_body_tag = '<body>' in html
                        has_form_tag = '<form' in html
                        has_script_tag = '<script>' in html
                        
                        print(f"    HTML構造:")
                        print(f"      html tag: {has_html_tag}")
                        print(f"      head tag: {has_head_tag}")
                        print(f"      body tag: {has_body_tag}")
                        print(f"      form tag: {has_form_tag}")
                        print(f"      script tag: {has_script_tag}")
                        
                        # エラーメッセージの確認
                        error_indicators = [
                            'error', 'Error', 'エラー', 'Exception', 
                            'Traceback', 'Internal Server Error',
                            '500', '404', 'Not Found', '問題が発生'
                        ]
                        
                        found_errors = []
                        for indicator in error_indicators:
                            if indicator in html:
                                found_errors.append(indicator)
                        
                        if found_errors:
                            print(f"    エラー指標: {found_errors}")
                            
                            # エラー周辺のテキストを抽出
                            for error in found_errors[:2]:  # 最初の2つ
                                pos = html.find(error)
                                if pos != -1:
                                    context = html[max(0, pos-100):pos+200]
                                    # 制御文字を除去
                                    clean_context = ''.join(c for c in context if ord(c) >= 32 or c in '\n\r\t')
                                    print(f"    '{error}' 周辺: {clean_context[:100]}...")
                        
                        # HTMLの終端を確認
                        html_end = html[-200:]  # 最後の200文字
                        has_proper_end = '</html>' in html_end
                        print(f"    適切な終端: {has_proper_end}")
                        
                        if not has_proper_end:
                            print("    HTML終端部分:")
                            clean_end = ''.join(c for c in html_end if ord(c) >= 32 or c in '\n\r\t')
                            print(f"      {clean_end}")
                        
                        return True  # 失敗ケースの分析完了
                        
        print("\n❌ 10回試行しても失敗ケースが発生しませんでした")
        return False

if __name__ == "__main__":
    result = analyze_failed_html()
    print(f"\n分析結果: {'COMPLETED' if result else 'NO_FAILURE_FOUND'}")