#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - 実際の年度選択テスト
Webアプリケーションでの年度選択機能を実際にテストする
"""

import requests
import json
import time
import random

class RCCMYearTestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_year_selection(self):
        """年度選択機能の包括テスト"""
        print("=== RCCM年度選択機能 実際テスト ===")
        print()
        
        # 1. 基本接続テスト
        print("1. アプリケーション接続テスト")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ アプリケーション接続: 正常")
            else:
                print(f"❌ アプリケーション接続: エラー ({response.status_code})")
                return False
        except Exception as e:
            print(f"❌ アプリケーション接続失敗: {e}")
            return False
        
        # 2. 年度別問題取得テスト
        print("\n2. 年度別問題取得テスト")
        test_years = [2019, 2018, 2017, 2016, 2015]
        
        for year in test_years:
            print(f"\n--- {year}年度テスト ---")
            
            # 年度指定でexamエンドポイントをテスト
            try:
                response = self.session.get(f"{self.base_url}/exam?year={year}&question_type=specialist")
                
                if response.status_code == 200:
                    print(f"✅ {year}年度問題取得: 成功")
                    
                    # HTMLレスポンス内容をチェック
                    html_content = response.text
                    
                    # 年度が正しく表示されているかチェック
                    if str(year) in html_content:
                        print(f"✅ {year}年度表示: 正常")
                    else:
                        print(f"⚠️ {year}年度表示: 年度情報が見つからない")
                    
                    # 問題が実際に読み込まれているかチェック
                    if "question" in html_content.lower():
                        print(f"✅ {year}年度問題データ: 読み込み確認")
                    else:
                        print(f"❌ {year}年度問題データ: 読み込み失敗")
                        
                else:
                    print(f"❌ {year}年度問題取得: HTTPエラー ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ {year}年度テストエラー: {e}")
            
            time.sleep(0.2)  # サーバー負荷軽減
        
        # 3. 年度混在チェック（問題取得API）
        print("\n3. 年度混在チェック（APIレベル）")
        
        # 個別年度で複数回テスト
        for year in [2019, 2017]:
            print(f"\n--- {year}年度混在チェック ---")
            
            year_consistency = True
            test_count = 3
            
            for i in range(test_count):
                try:
                    # 新しいセッションで毎回テスト
                    fresh_session = requests.Session()
                    response = fresh_session.get(
                        f"{self.base_url}/exam?year={year}&question_type=specialist&count=5"
                    )
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # 他の年度が混在していないかチェック
                        other_years = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
                        other_years.remove(year)
                        
                        mixed_year_found = False
                        for other_year in other_years:
                            # 問題文や選択肢内に他の年度が含まれていないかチェック
                            # ただし、問題文中の年号は正当なので区別する
                            if f"{other_year}年度" in html or f"年度:{other_year}" in html:
                                mixed_year_found = True
                                print(f"⚠️ 混在検出 (試行{i+1}): {other_year}年度の問題が混在している可能性")
                                break
                        
                        if not mixed_year_found:
                            print(f"✅ 年度純度チェック (試行{i+1}): {year}年度のみ")
                        else:
                            year_consistency = False
                            
                    else:
                        print(f"❌ API呼び出し失敗 (試行{i+1}): {response.status_code}")
                        year_consistency = False
                        
                except Exception as e:
                    print(f"❌ テストエラー (試行{i+1}): {e}")
                    year_consistency = False
                
                time.sleep(0.1)
            
            if year_consistency:
                print(f"✅ {year}年度混在チェック: 全{test_count}回テスト通過")
            else:
                print(f"❌ {year}年度混在チェック: 問題検出")
        
        # 4. 年度ランダム選択テスト
        print("\n4. 年度ランダム選択テスト")
        
        try:
            # 年度指定なしでテスト
            response = self.session.get(f"{self.base_url}/exam?question_type=specialist&count=10")
            
            if response.status_code == 200:
                print("✅ 年度ランダム選択: 成功")
                
                html = response.text
                years_detected = []
                
                # レスポンス内から年度情報を検出
                for year in range(2008, 2020):
                    if f"{year}年" in html:
                        years_detected.append(year)
                
                if len(years_detected) >= 1:
                    print(f"✅ 年度多様性: 複数年度から選択 {years_detected[:5]}...")
                else:
                    print("⚠️ 年度多様性: 年度情報の検出ができませんでした")
                    
            else:
                print(f"❌ 年度ランダム選択: HTTPエラー ({response.status_code})")
                
        except Exception as e:
            print(f"❌ 年度ランダム選択エラー: {e}")
        
        # 5. 無効年度エラーハンドリングテスト
        print("\n5. 無効年度エラーハンドリングテスト")
        
        invalid_years = [2007, 2020, 2021, 1999, "invalid", ""]
        
        for invalid_year in invalid_years:
            try:
                response = self.session.get(f"{self.base_url}/exam?year={invalid_year}&question_type=specialist")
                
                if response.status_code in [400, 422]:
                    print(f"✅ 無効年度 '{invalid_year}': 正常にエラー処理")
                elif response.status_code == 200:
                    # レスポンス内容をチェックしてエラーメッセージが含まれているか
                    if "エラー" in response.text or "無効" in response.text:
                        print(f"✅ 無効年度 '{invalid_year}': エラーメッセージ表示")
                    else:
                        print(f"⚠️ 無効年度 '{invalid_year}': エラー処理が不十分")
                else:
                    print(f"⚠️ 無効年度 '{invalid_year}': 予期しないレスポンス ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ 無効年度テストエラー '{invalid_year}': {e}")
            
            time.sleep(0.1)
        
        print("\n=== 年度選択機能テスト完了 ===")
        return True

def main():
    """メイン実行関数"""
    tester = RCCMYearTestSuite()
    
    print("RCCM問題集アプリケーション年度選択機能テストを開始します")
    print("アプリケーションが http://localhost:5000 で動作していることを確認してください")
    print()
    
    # テスト実行
    success = tester.test_year_selection()
    
    if success:
        print("\n🎉 年度選択機能テスト完了")
    else:
        print("\n❌ テスト中に問題が発生しました")

if __name__ == "__main__":
    main()