#!/usr/bin/env python3
"""
ULTRA SYNC データフィルタリング修正効果検証テスト
副作用防止のため慎重に検証
"""

import requests
import json
import time
from datetime import datetime

class UltraSyncFilteringTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.test_results = []
        
    def test_invalid_year_error_handling(self):
        """無効年度のエラーハンドリング検証"""
        print("無効年度エラーハンドリング検証開始...")
        
        invalid_years = [2020, 2024, 2025, 2007, 2030]
        results = {}
        
        for year in invalid_years:
            try:
                print(f"  {year}年テスト中...")
                url = f"{self.base_url}/start_exam/河川・砂防"
                data = {"questions": 10, "year": str(year)}
                
                response = self.session.post(url, data=data, timeout=30)
                
                if response.status_code == 200:
                    # エラーページが返されているかチェック
                    if "利用できません" in response.text or "有効な年度" in response.text:
                        results[year] = "適切なエラーメッセージ"
                        print(f"    ✅ {year}年: 適切なエラーメッセージ表示")
                    else:
                        results[year] = "不適切な成功レスポンス"
                        print(f"    ❌ {year}年: 不適切な成功レスポンス")
                        # デバッグ用にレスポンス保存
                        with open(f"invalid_year_{year}_response.html", "w", encoding="utf-8") as f:
                            f.write(response.text)
                else:
                    results[year] = f"HTTPエラー: {response.status_code}"
                    print(f"    ⚠️ {year}年: HTTPエラー {response.status_code}")
                
                time.sleep(1)  # サーバー負荷軽減
                
            except Exception as e:
                results[year] = f"例外: {e}"
                print(f"    ❌ {year}年: 例外 {e}")
        
        return results
    
    def test_valid_year_functionality(self):
        """有効年度の正常動作確認"""
        print("有効年度正常動作確認開始...")
        
        valid_years = [2008, 2012, 2016, 2019]  # サンプル年度
        results = {}
        
        for year in valid_years:
            try:
                print(f"  {year}年テスト中...")
                url = f"{self.base_url}/start_exam/河川・砂防"
                data = {"questions": 10, "year": str(year)}
                
                response = self.session.post(url, data=data, timeout=30)
                
                if response.status_code == 200:
                    if "問題" in response.text and "選択肢" in response.text:
                        results[year] = "正常動作"
                        print(f"    ✅ {year}年: 正常に問題表示")
                    elif "利用できません" in response.text:
                        results[year] = "エラーメッセージ（想定外）"
                        print(f"    ❌ {year}年: 想定外のエラーメッセージ")
                    else:
                        results[year] = "不明なレスポンス"
                        print(f"    ⚠️ {year}年: 不明なレスポンス")
                        with open(f"valid_year_{year}_response.html", "w", encoding="utf-8") as f:
                            f.write(response.text)
                else:
                    results[year] = f"HTTPエラー: {response.status_code}"
                    print(f"    ❌ {year}年: HTTPエラー {response.status_code}")
                
                time.sleep(2)  # サーバー負荷軽減
                
            except Exception as e:
                results[year] = f"例外: {e}"
                print(f"    ❌ {year}年: 例外 {e}")
        
        return results
    
    def test_department_year_combination(self):
        """部門・年度組み合わせテスト"""
        print("部門・年度組み合わせテスト開始...")
        
        test_combinations = [
            ("道路", 2015),
            ("河川・砂防", 2018),
            ("都市計画", 2019),
            ("基礎科目(共通)", None)  # 基礎科目は年度なし
        ]
        
        results = {}
        
        for department, year in test_combinations:
            try:
                combo_key = f"{department}_{year if year else 'なし'}"
                print(f"  {combo_key}テスト中...")
                
                url = f"{self.base_url}/start_exam/{department}"
                data = {"questions": 10}
                if year:
                    data["year"] = str(year)
                
                response = self.session.post(url, data=data, timeout=30)
                
                if response.status_code == 200:
                    if "問題" in response.text:
                        results[combo_key] = "正常動作"
                        print(f"    ✅ {combo_key}: 正常に問題表示")
                    else:
                        results[combo_key] = "問題表示なし"
                        print(f"    ❌ {combo_key}: 問題が表示されていない")
                else:
                    results[combo_key] = f"HTTPエラー: {response.status_code}"
                    print(f"    ❌ {combo_key}: HTTPエラー {response.status_code}")
                
                time.sleep(2)
                
            except Exception as e:
                results[combo_key] = f"例外: {e}"
                print(f"    ❌ {combo_key}: 例外 {e}")
        
        return results
    
    def run_comprehensive_verification(self):
        """包括的修正効果検証"""
        print("ULTRA SYNC データフィルタリング修正効果検証開始")
        print(f"検証開始時刻: {datetime.now()}")
        print("=" * 60)
        
        verification_results = {
            "test_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. 無効年度エラーハンドリング検証
        print("【テスト1】無効年度エラーハンドリング検証")
        verification_results["tests"]["invalid_year_handling"] = self.test_invalid_year_error_handling()
        
        print("\n【テスト2】有効年度正常動作確認")
        verification_results["tests"]["valid_year_functionality"] = self.test_valid_year_functionality()
        
        print("\n【テスト3】部門・年度組み合わせテスト")
        verification_results["tests"]["department_year_combination"] = self.test_department_year_combination()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("ULTRA SYNC修正効果検証結果サマリー")
        
        # 無効年度テスト結果
        invalid_year_results = verification_results["tests"]["invalid_year_handling"]
        proper_error_count = sum(1 for result in invalid_year_results.values() 
                               if "適切なエラーメッセージ" in result)
        total_invalid = len(invalid_year_results)
        
        print(f"無効年度エラーハンドリング: {proper_error_count}/{total_invalid} 適切")
        
        # 有効年度テスト結果
        valid_year_results = verification_results["tests"]["valid_year_functionality"]
        normal_operation_count = sum(1 for result in valid_year_results.values() 
                                   if result == "正常動作")
        total_valid = len(valid_year_results)
        
        print(f"有効年度正常動作: {normal_operation_count}/{total_valid} 正常")
        
        # 組み合わせテスト結果
        combo_results = verification_results["tests"]["department_year_combination"]
        combo_success_count = sum(1 for result in combo_results.values() 
                                if result == "正常動作")
        total_combos = len(combo_results)
        
        print(f"部門・年度組み合わせ: {combo_success_count}/{total_combos} 正常")
        
        # 全体評価
        total_tests = proper_error_count + normal_operation_count + combo_success_count
        max_possible = total_invalid + total_valid + total_combos
        overall_success_rate = (total_tests / max_possible) * 100
        
        print(f"\n全体成功率: {total_tests}/{max_possible} ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 80:
            print("✅ ULTRA SYNC修正効果: 良好")
        elif overall_success_rate >= 60:
            print("⚠️ ULTRA SYNC修正効果: 部分的改善")
        else:
            print("❌ ULTRA SYNC修正効果: 要追加修正")
        
        # 副作用チェック
        if normal_operation_count == total_valid:
            print("✅ 副作用なし: 有効年度の正常動作を維持")
        else:
            print("⚠️ 副作用の可能性: 有効年度の動作に影響")
        
        # 結果保存
        with open("ultrasync_filtering_verification_results.json", "w", encoding="utf-8") as f:
            json.dump(verification_results, f, ensure_ascii=False, indent=2)
        
        return verification_results

if __name__ == "__main__":
    tester = UltraSyncFilteringTest()
    tester.run_comprehensive_verification()