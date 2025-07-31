#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC エラートレーステスト
型エラーが発生している正確な箇所を特定
"""

import requests
from datetime import datetime

class UltraSyncErrorTraceTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def test_step_by_step_trace(self):
        """段階的にエラーを特定"""
        print("ULTRA SYNC エラートレース特定テスト")
        print(f"目的: 型エラー発生箇所の正確な特定")
        print(f"テスト時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        try:
            # Step 1: セッション初期化テスト
            print("\n1. セッション初期化のみテスト")
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            
            # 最小パラメータでテスト
            start_data = {"questions": 1, "year": "2018"}
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            
            print(f"   セッション初期化: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print("   ERROR: セッション初期化で失敗")
                return False
            
            # Step 2: セッション状態確認
            print("\n2. セッション状態の確認")
            
            # リダイレクト先の確認
            if start_response.history:
                print(f"   リダイレクト発生: {len(start_response.history)}回")
                for i, resp in enumerate(start_response.history):
                    print(f"     {i+1}: HTTP {resp.status_code} → {resp.headers.get('Location', 'N/A')}")
            
            # レスポンス内容の確認
            content = start_response.text
            if "エラー" in content:
                print("   WARNING: セッション初期化段階でエラー検出")
                
                # エラー内容の抽出
                import re
                error_match = re.search(r'詳細[：:]\s*([^<]+)', content)
                if error_match:
                    error_detail = error_match.group(1).strip()
                    print(f"   エラー詳細: {error_detail}")
                    
                    # エラーが型エラーの場合
                    if "not supported between instances" in error_detail:
                        print("   確認: セッション初期化段階で型エラー発生")
                        return True  # エラー特定成功
            else:
                print("   OK: セッション初期化は成功")
            
            # Step 3: 問題ページ直接アクセス
            print("\n3. 問題ページ直接アクセステスト")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            
            print(f"   問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code == 200:
                exam_content = exam_response.text
                if "エラー" in exam_content:
                    print("   確認: 問題ページアクセス段階でエラー発生")
                    
                    # エラー内容の抽出
                    error_match = re.search(r'詳細[：:]\s*([^<]+)', exam_content)
                    if error_match:
                        error_detail = error_match.group(1).strip()
                        print(f"   エラー詳細: {error_detail}")
                        
                        return True  # エラー特定成功
                else:
                    print("   OK: 問題ページは正常")
                    return False  # エラーなし
            else:
                print(f"   ERROR: 問題ページアクセス失敗 HTTP {exam_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   テストエラー: {e}")
            return False
    
    def test_different_departments(self):
        """他部門でも同じエラーが発生するか確認"""
        print("\n" + "=" * 50)
        print("ULTRA SYNC 他部門エラー確認テスト")
        print("=" * 50)
        
        departments = [
            ("基礎科目", ""),  # 年度なし
            ("道路", "2015"),
            ("河川・砂防", "2018")
        ]
        
        for dept, year in departments:
            print(f"\n{dept}部門テスト (年度: {year if year else 'なし'})")
            
            try:
                start_url = f"{self.base_url}/start_exam/{dept}"
                start_data = {"questions": 1, "year": year}
                
                start_response = self.session.post(start_url, data=start_data, timeout=30)
                print(f"   セッション: HTTP {start_response.status_code}")
                
                if start_response.status_code == 200:
                    exam_response = self.session.get(f"{self.base_url}/exam", timeout=30)
                    print(f"   問題ページ: HTTP {exam_response.status_code}")
                    
                    if exam_response.status_code == 200:
                        if "エラー" in exam_response.text:
                            print("   結果: エラー発生")
                        else:
                            print("   結果: 正常")
                    else:
                        print(f"   結果: HTTP {exam_response.status_code}")
                else:
                    print(f"   結果: セッション失敗 HTTP {start_response.status_code}")
                    
            except Exception as e:
                print(f"   結果: 例外発生 {e}")

def main():
    print("ULTRA SYNC エラー特定テスト")
    print("目的: 型エラーの発生箇所を段階的に特定")
    print("=" * 60)
    
    tester = UltraSyncErrorTraceTest()
    
    # Step 1: エラートレーステスト
    trace_result = tester.test_step_by_step_trace()
    
    # Step 2: 他部門でのエラー確認
    tester.test_different_departments()
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC エラートレース結果")
    print("=" * 60)
    
    if trace_result:
        print("エラー特定: 成功")
        print("型エラーの発生箇所が特定されました")
        print("次のステップ: 該当箇所の修正")
    else:
        print("エラー特定: 不完全")
        print("さらなる調査が必要")
    
    return trace_result

if __name__ == "__main__":
    main()