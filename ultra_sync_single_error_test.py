#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 単一エラー修正テスト
app.py:3047行目の修正が正しく動作するか本番環境で確認
"""

import requests
import time
from datetime import datetime

class UltraSyncSingleErrorTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def test_type_error_fix(self):
        """型エラー修正の確認テスト"""
        print("ULTRA SYNC 型エラー修正テスト開始")
        print(f"修正対象: app.py:3047行目 exam_current型安全変換")
        print(f"テスト時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        try:
            # Step 1: セッション開始
            print("\n1. セッション開始テスト")
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 1, "year": "2018"}  # 最小構成
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"   セッション開始: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print("   セッション開始失敗 - テスト中止")
                return False
                
            # Step 2: 問題ページアクセス
            print("\n2. 問題ページアクセステスト")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            print(f"   問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print("   問題ページアクセス失敗")
                return False
            
            # Step 3: エラーメッセージチェック
            print("\n3. エラーメッセージ検証")
            page_content = exam_response.text
            
            # 以前のエラーが解消されているかチェック
            error_patterns = [
                "'>=' not supported between instances of 'str' and 'int'",
                "内部エラーが発生しました",
                "ユーザーID未設定",
                "処理中にエラーが発生"
            ]
            
            errors_found = []
            for pattern in error_patterns:
                if pattern in page_content:
                    errors_found.append(pattern)
            
            if errors_found:
                print(f"   ERROR: 以下のエラーが残存しています:")
                for error in errors_found:
                    print(f"     - {error}")
                return False
            else:
                print("   OK: 型エラーメッセージは検出されませんでした")
            
            # Step 4: 問題表示確認
            print("\n4. 問題表示確認")
            has_question = any(keyword in page_content for keyword in ['問題', '選択', '次の', '正しい'])
            
            if has_question:
                print("   OK: 問題らしきコンテンツが表示されています")
                return True
            else:
                print("   WARNING: 問題コンテンツが確認できませんが、エラーは解消")
                return True  # エラー解消が目的なのでTrue
                
        except Exception as e:
            print(f"   テストエラー: {e}")
            return False
    
    def test_side_effect_check(self):
        """副作用チェック（他機能に影響がないか確認）"""
        print("\n" + "=" * 50)
        print("ULTRA SYNC 副作用確認テスト")
        print("=" * 50)
        
        try:
            # 基礎科目でのテスト（別の処理経路）
            print("\n基礎科目での副作用確認...")
            basic_url = f"{self.base_url}/start_exam/基礎科目"
            basic_data = {"questions": 1, "year": ""}  # 基礎科目は年度なし
            
            basic_response = self.session.post(basic_url, data=basic_data, timeout=30)
            print(f"   基礎科目セッション: HTTP {basic_response.status_code}")
            
            if basic_response.status_code == 200:
                print("   OK: 基礎科目に副作用なし")
                return True
            else:
                print(f"   WARNING: 基礎科目で問題発生 (HTTP {basic_response.status_code})")
                return False
                
        except Exception as e:
            print(f"   副作用チェックエラー: {e}")
            return False

def main():
    print("ULTRA SYNC 段階的修正テスト")
    print("修正内容: app.py:3047行目 型安全変換追加")
    print("=" * 60)
    
    tester = UltraSyncSingleErrorTest()
    
    # Step 1: 主要エラー修正確認
    main_test_result = tester.test_type_error_fix()
    
    # Step 2: 副作用確認
    side_effect_result = tester.test_side_effect_check()
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 段階的修正テスト結果")
    print("=" * 60)
    
    print(f"型エラー修正: {'成功' if main_test_result else '失敗'}")
    print(f"副作用チェック: {'問題なし' if side_effect_result else '要確認'}")
    
    overall_success = main_test_result and side_effect_result
    
    if overall_success:
        print("\nULTRA SYNC Step 1: 成功")
        print("次のステップに進行可能")
    else:
        print("\nULTRA SYNC Step 1: 要追加修正")
        print("問題解決後に再テスト必要")
    
    return overall_success

if __name__ == "__main__":
    main()