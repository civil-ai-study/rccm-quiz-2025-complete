#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC HTML出力デバッグ
問題ページのHTMLをファイルに保存して内容を詳細確認
"""

import requests
import re
from datetime import datetime

class UltraSyncHtmlOutputDebug:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def save_html_and_analyze(self):
        """HTMLを保存して分析"""
        print("ULTRA SYNC HTML保存分析")
        print(f"対象: 河川・砂防 2018年 問題ページHTML")
        print(f"分析時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        try:
            # Step 1: セッション開始
            print("\n1. セッション開始")
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 1, "year": "2018"}
            
            start_response = self.session.post(start_url, data=start_data, timeout=60)
            print(f"   セッション開始: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print(f"   ERROR: セッション開始失敗")
                return False
                
            # Step 2: 問題ページHTML取得
            print("\n2. 問題ページHTML取得・保存")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=60)
            print(f"   問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print(f"   ERROR: 問題ページアクセス失敗")
                return False
            
            page_content = exam_response.text
            
            # HTMLファイルに保存
            output_file = f"debug_exam_output_{datetime.now().strftime('%H%M%S')}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f"   HTML保存: {output_file}")
            print(f"   HTMLサイズ: {len(page_content)} 文字")
            
            # Step 3: エラーメッセージの詳細確認
            print(f"\n3. エラーメッセージ確認")
            
            # 一般的なエラーパターンを検索
            error_patterns = [
                r'<h1[^>]*>([^<]*[Ee]rror[^<]*)</h1>',
                r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>',
                r'エラー[：:](.{0,100})',
                r'Internal Server Error',
                r'404.*Not Found',
                r'500.*Internal Server Error'
            ]
            
            error_found = False
            for pattern in error_patterns:
                matches = re.findall(pattern, page_content, re.DOTALL | re.IGNORECASE)
                if matches:
                    error_found = True
                    print(f"   エラー発見: {len(matches)}件")
                    for match in matches[:2]:
                        if isinstance(match, str):
                            clean_match = re.sub(r'<[^>]+>', '', match).strip()
                            print(f"     - {clean_match[:80]}")
            
            if not error_found:
                print("   OK: 明確なエラーメッセージは検出されませんでした")
            
            # Step 4: HTMLタイトルとメタ情報確認
            print(f"\n4. ページ情報確認")
            
            title_match = re.search(r'<title[^>]*>(.*?)</title>', page_content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                print(f"   ページタイトル: {title}")
                
                if "エラー" in title:
                    print("   WARNING: エラーページの可能性")
                elif "問題" in title or "exam" in title.lower():
                    print("   OK: 問題ページのようです")
            
            # Step 5: 主要なHTMLセクションの確認
            print(f"\n5. HTMLセクション確認")
            
            # body内のメインコンテンツを確認
            body_match = re.search(r'<body[^>]*>(.*?)</body>', page_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                body_content = body_match.group(1)
                print(f"   body内容: {len(body_content)}文字")
                
                # body内の主要な要素を確認
                main_elements = {
                    'div': len(re.findall(r'<div[^>]*>', body_content)),
                    'p': len(re.findall(r'<p[^>]*>', body_content)),
                    'form': len(re.findall(r'<form[^>]*>', body_content)),
                    'input': len(re.findall(r'<input[^>]*>', body_content)),
                    'h1': len(re.findall(r'<h1[^>]*>', body_content)),
                    'h2': len(re.findall(r'<h2[^>]*>', body_content)),
                    'h3': len(re.findall(r'<h3[^>]*>', body_content))
                }
                
                for element, count in main_elements.items():
                    print(f"   <{element}>: {count}個")
            
            # Step 6: テキスト内容の検索
            print(f"\n6. 重要キーワード検索")
            
            # HTMLタグを除去してテキスト内容を確認
            text_content = re.sub(r'<[^>]+>', ' ', page_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            keywords = ['問題', '選択', '河川', '砂防', '正しい', '次の', 'について', 'RCCM']
            for keyword in keywords:
                count = text_content.count(keyword)
                print(f"   '{keyword}': {count}回")
            
            # Step 7: 実際の問題内容があるかの判定
            print(f"\n7. 問題内容存在判定")
            
            # 問題らしい内容があるかチェック
            question_indicators = [
                '問題' in text_content and ('選択' in text_content or '正しい' in text_content),
                '次の' in text_content and 'について' in text_content,
                '河川' in text_content or '砂防' in text_content,
                text_content.count('A.') > 0 or text_content.count('1.') > 0
            ]
            
            positive_indicators = sum(question_indicators)
            print(f"   問題指標: {positive_indicators}/4")
            
            if positive_indicators >= 2:
                print("   判定: 問題コンテンツが存在する可能性が高い")
                return True
            else:
                print("   判定: 問題コンテンツが存在しない")
                return False
                
        except Exception as e:
            print(f"   分析エラー: {e}")
            return False

def main():
    print("ULTRA SYNC HTML出力分析")
    print("目的: 問題ページHTMLの詳細保存・分析")
    print("=" * 60)
    
    debugger = UltraSyncHtmlOutputDebug()
    
    # HTML保存・分析
    analysis_result = debugger.save_html_and_analyze()
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC HTML分析結果")
    print("=" * 60)
    
    if analysis_result:
        print("分析結果: HTMLに問題コンテンツが存在")
        print("次のステップ: 問題表示ロジックの修正")
    else:
        print("分析結果: 問題コンテンツが存在しない")
        print("次のステップ: app.py問題生成機能の確認")
    
    return analysis_result

if __name__ == "__main__":
    main()