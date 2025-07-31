#!/usr/bin/env python3
"""
修正後検証テスト：無効年度で適切にエラーが表示されるかの厳密確認
"""

import requests
import time
from datetime import datetime

class PostFixVerificationTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def test_invalid_year_error_handling(self, department, year):
        """修正後：無効年度で適切なエラーが表示されるかテスト"""
        print(f"\n=== {department}部門{year}年 無効年度エラーテスト ===")
        
        try:
            url = f"{self.base_url}/start_exam/{department}"
            data = {"questions": 10, "year": str(year)}
            
            print(f"リクエスト: {url}")
            print(f"データ: {data}")
            
            response = self.session.post(url, data=data, timeout=60)
            
            print(f"レスポンス: HTTP {response.status_code}")
            print(f"サイズ: {len(response.text)} bytes")
            
            # エラーメッセージの確認
            if "利用できません" in response.text or "無効な年度" in response.text or "見つかりません" in response.text:
                print("OK: 適切なエラーメッセージ表示")
                # エラーメッセージ内容抽出
                if "利用可能年度" in response.text:
                    print("OK 利用可能年度の案内も表示")
                return True
                
            elif "問題" in response.text and ("選択肢" in response.text or "回答" in response.text):
                print("ERROR 修正失敗：無効年度なのに問題が表示されている")
                # 修正失敗の証拠保存
                with open(f"fix_failed_{department}_{year}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"証拠ファイル保存: fix_failed_{department}_{year}.html")
                return False
                
            else:
                print("WARNING 不明なレスポンス")
                with open(f"unknown_response_{department}_{year}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                return False
                
        except Exception as e:
            print(f"ERROR テストエラー: {e}")
            return False
    
    def test_valid_year_functionality(self, department, year):
        """修正後：有効年度で正常動作するかテスト"""
        print(f"\n=== {department}部門{year}年 有効年度正常動作テスト ===")
        
        try:
            url = f"{self.base_url}/start_exam/{department}"
            data = {"questions": 10, "year": str(year)}
            
            print(f"リクエスト: {url}")
            print(f"データ: {data}")
            
            response = self.session.post(url, data=data, timeout=60)
            
            print(f"レスポンス: HTTP {response.status_code}")
            print(f"サイズ: {len(response.text)} bytes")
            
            if "問題" in response.text:
                print("OK 問題が正常に表示")
                
                # 副作用チェック：修正により有効年度が動作しなくなっていないか
                if "エラー" in response.text or "見つかりません" in response.text:
                    print("ERROR 副作用検出：有効年度でエラーが発生")
                    return False
                    
                return True
            else:
                print("ERROR 有効年度で問題が表示されない")
                with open(f"valid_year_failed_{department}_{year}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                return False
                
        except Exception as e:
            print(f"ERROR テストエラー: {e}")
            return False
    
    def run_comprehensive_verification(self):
        """修正効果の包括的検証"""
        print("修正後検証テスト開始")
        print(f"開始時刻: {datetime.now()}")
        print("=" * 60)
        
        results = {
            "test_time": datetime.now().isoformat(),
            "invalid_year_tests": {},
            "valid_year_tests": {}
        }
        
        # 無効年度テスト（修正の主目的）
        invalid_year_cases = [
            ("河川・砂防", 2020),
            ("道路", 2020), 
            ("都市計画", 2024),
            ("造園", 2025)
        ]
        
        print("【無効年度エラーハンドリングテスト】")
        for department, year in invalid_year_cases:
            result = self.test_invalid_year_error_handling(department, year)
            results["invalid_year_tests"][f"{department}_{year}"] = result
            time.sleep(3)  # サーバー負荷軽減
        
        # 有効年度テスト（副作用チェック）  
        valid_year_cases = [
            ("河川・砂防", 2018),
            ("道路", 2015),
            ("都市計画", 2019),
            ("造園", 2016)
        ]
        
        print("\n【有効年度正常動作テスト（副作用チェック）】")
        for department, year in valid_year_cases:
            result = self.test_valid_year_functionality(department, year)
            results["valid_year_tests"][f"{department}_{year}"] = result
            time.sleep(3)
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("修正効果検証結果サマリー")
        
        invalid_success = sum(1 for r in results["invalid_year_tests"].values() if r)
        invalid_total = len(results["invalid_year_tests"])
        
        valid_success = sum(1 for r in results["valid_year_tests"].values() if r)
        valid_total = len(results["valid_year_tests"])
        
        print(f"\n無効年度エラーハンドリング: {invalid_success}/{invalid_total} ({invalid_success/invalid_total*100:.1f}%)")
        print(f"有効年度正常動作: {valid_success}/{valid_total} ({valid_success/valid_total*100:.1f}%)")
        
        # 修正効果判定
        if invalid_success == invalid_total:
            print("OK 修正成功：無効年度で適切にエラー表示")
        else:
            print("ERROR 修正失敗：無効年度でまだ問題が表示される")
            failed_cases = [k for k, v in results["invalid_year_tests"].items() if not v]
            print(f"失敗ケース: {failed_cases}")
        
        if valid_success == valid_total:
            print("OK 副作用なし：有効年度は正常動作")
        else:
            print("WARNING 副作用あり：有効年度の動作に問題")
            
        # 総合判定
        overall_success = (invalid_success + valid_success) / (invalid_total + valid_total)
        print(f"\n総合成功率: {overall_success*100:.1f}%")
        
        if overall_success >= 0.9:
            print("EXCELLENT 修正効果：優秀")
        elif overall_success >= 0.7:
            print("OK 修正効果：良好") 
        else:
            print("ERROR 修正効果：要追加対応")
        
        # 結果保存
        with open("post_fix_verification_results.json", "w", encoding="utf-8") as f:
            import json
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results

if __name__ == "__main__":
    tester = PostFixVerificationTest()
    tester.run_comprehensive_verification()