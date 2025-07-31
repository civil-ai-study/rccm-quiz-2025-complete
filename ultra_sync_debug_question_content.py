#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 問題コンテンツデバッグ
問題ページのHTMLを詳細に調査して問題表示が失敗している原因を特定
"""

import requests
import re
from datetime import datetime

class UltraSyncDebugQuestionContent:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def debug_question_html(self):
        """問題ページのHTML構造を詳細デバッグ"""
        print("ULTRA SYNC 問題コンテンツHTML詳細デバッグ")
        print(f"対象: 河川・砂防 2018年 問題ページHTML構造")
        print(f"デバッグ時刻: {datetime.now().strftime('%H:%M:%S')}")
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
                
            # Step 2: 問題ページのHTML取得
            print("\n2. 問題ページHTML取得")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=60)
            print(f"   問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print(f"   ERROR: 問題ページアクセス失敗")
                return False
            
            page_content = exam_response.text
            print(f"   HTMLサイズ: {len(page_content)} 文字")
            
            # Step 3: HTMLの主要部分を抽出
            print("\n3. HTML構造の分析")
            
            # エラーメッセージの確認
            if "エラー" in page_content or "error" in page_content.lower():
                error_lines = [line.strip() for line in page_content.split('\n') if 'エラー' in line or 'error' in line.lower()]
                print(f"   ERROR発見: {len(error_lines)}件")
                for error in error_lines[:3]:  # 最初の3件のみ表示
                    print(f"     - {error[:80]}")
            
            # 問題文関連のHTMLを検索
            print(f"\n4. 問題文HTML検索")
            
            # 複数の問題文パターンで検索
            question_patterns = [
                r'<p[^>]*class="question-text"[^>]*>(.*?)</p>',
                r'<div[^>]*class="question"[^>]*>(.*?)</div>',
                r'<h3[^>]*>(.*?問題.*?)</h3>',
                r'問題\d+[：:](.*?)(?=選択|次の|A\.|1\.)',
                r'次の.*?について.*?正しいもの',
                r'<p[^>]*>(.*?について.*?正しい.*?)</p>'
            ]
            
            question_found = False
            for i, pattern in enumerate(question_patterns, 1):
                matches = re.findall(pattern, page_content, re.DOTALL | re.IGNORECASE)
                print(f"   パターン{i}: {len(matches)}件")
                if matches:
                    question_found = True
                    for match in matches[:2]:  # 最初の2件
                        clean_match = re.sub(r'<[^>]+>', '', match).strip()
                        print(f"     - {clean_match[:60]}...")
            
            # Step 5: 選択肢HTML検索
            print(f"\n5. 選択肢HTML検索")
            
            # 複数の選択肢パターンで検索
            option_patterns = [
                r'<input[^>]*name="answer"[^>]*value="([A-D])"[^>]*>',
                r'<option[^>]*value="([A-D])"[^>]*>',
                r'<label[^>]*>([A-D]\..*?)</label>',
                r'([A-D])\.?\s*(.*?)(?=[B-D]\.|$)',
                r'<li[^>]*>([A-D]\..*?)</li>'
            ]
            
            options_found = False
            for i, pattern in enumerate(option_patterns, 1):
                matches = re.findall(pattern, page_content, re.DOTALL | re.IGNORECASE)
                print(f"   選択肢パターン{i}: {len(matches)}件")
                if matches:
                    options_found = True
                    for match in matches[:4]:  # 最初の4件
                        if isinstance(match, tuple):
                            print(f"     - {match[0]}: {str(match[1])[:40]}...")
                        else:
                            print(f"     - {str(match)[:50]}...")
            
            # Step 6: HTMLの全体的な内容確認
            print(f"\n6. HTMLコンテンツの全体確認")
            
            # 重要なキーワードの存在確認
            keywords = ['問題', '選択', '河川', '砂防', '正しい', '次の', 'について']
            keyword_counts = {kw: page_content.count(kw) for kw in keywords}
            
            for kw, count in keyword_counts.items():
                print(f"   '{kw}': {count}回")
            
            # HTML内のform要素の確認
            form_count = len(re.findall(r'<form[^>]*>', page_content))
            input_count = len(re.findall(r'<input[^>]*>', page_content))
            print(f"   form要素: {form_count}個")
            print(f"   input要素: {input_count}個")
            
            # Step 7: HTMLの一部を実際に出力して確認
            print(f"\n7. HTMLサンプル出力（最初の1000文字）")
            print("-" * 50)
            print(page_content[:1000])
            print("-" * 50)
            
            # 判定結果
            if question_found and options_found:
                print(f"\n判定: 問題コンテンツは存在するが抽出方法に問題")
                return True
            elif question_found or options_found:
                print(f"\n判定: 一部のコンテンツのみ発見")
                return True
            else:
                print(f"\n判定: 問題コンテンツが存在しない可能性")
                return False
                
        except Exception as e:
            print(f"   デバッグエラー: {e}")
            return False

def main():
    print("ULTRA SYNC 問題表示デバッグ")
    print("目的: 問題ページのHTML構造を詳細調査")
    print("=" * 60)
    
    debugger = UltraSyncDebugQuestionContent()
    
    # HTML構造の詳細デバッグ
    debug_result = debugger.debug_question_html()
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 問題表示デバッグ結果")
    print("=" * 60)
    
    if debug_result:
        print("デバッグ完了: HTMLの詳細構造を確認")
        print("次のステップ: HTML抽出ロジックの修正")
    else:
        print("デバッグ結果: 根本的な問題表示エラー")
        print("次のステップ: app.py問題表示機能の確認")
    
    return debug_result

if __name__ == "__main__":
    main()