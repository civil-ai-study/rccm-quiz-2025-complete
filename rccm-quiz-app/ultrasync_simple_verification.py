#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: 修正後動作検証システム（urllib使用版）
段階的テストによる副作用確認とパフォーマンス検証
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
import sys
from datetime import datetime
from http.cookiejar import CookieJar

class UltraSyncSimpleVerifier:
    """🔥 ULTRA SYNC: 修正後動作検証クラス（urllib使用）"""
    
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
        self.test_results = {}
        
        # Cookie対応
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        urllib.request.install_opener(self.opener)
        
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def safe_request(self, url, data=None, method="GET"):
        """安全なHTTPリクエスト"""
        try:
            if data and method == "POST":
                data = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=data)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                req = urllib.request.Request(url)
                
            req.add_header('User-Agent', 'ULTRASYNC-Verifier/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return response.getcode(), content
                
        except urllib.error.HTTPError as e:
            return e.code, str(e)
        except urllib.error.URLError as e:
            return 0, str(e)
        except Exception as e:
            return -1, str(e)
            
    def test_stage1_road_department(self):
        """段階1: 道路部門基本動作確認"""
        self.log("段階1開始: 道路部門基本動作確認", "INFO")
        
        try:
            # テスト1-1: 道路部門ページアクセス
            url = urllib.parse.urljoin(self.base_url, "/department_study/道路")
            self.log(f"アクセスURL: {url}")
            
            status_code, content = self.safe_request(url)
            self.log(f"レスポンスステータス: {status_code}")
            
            if status_code == 200:
                # ランダム学習ボタンのURL確認
                if "/exam?department=道路&type=specialist" in content:
                    self.log("OK ランダム学習ボタンURL正常: /exam?department=道路&type=specialist")
                    self.test_results["stage1_road_url"] = "PASS"
                else:
                    self.log("NG ランダム学習ボタンURL異常")
                    self.test_results["stage1_road_url"] = "FAIL"
                    
                # ページコンテンツ確認
                if "道路" in content and ("ランダム学習" in content or "random" in content.lower()):
                    self.log("OK 道路部門ページコンテンツ正常")
                    self.test_results["stage1_road_content"] = "PASS"
                else:
                    self.log("NG 道路部門ページコンテンツ異常")
                    self.test_results["stage1_road_content"] = "FAIL"
                    
                self.test_results["stage1_road_access"] = "PASS"
                return True
                
            else:
                self.log(f"❌ 道路部門ページアクセス失敗: {status_code}")
                self.test_results["stage1_road_access"] = "FAIL"
                return False
                
        except Exception as e:
            self.log(f"❌ 段階1テストエラー: {str(e)}", "ERROR")
            self.test_results["stage1_error"] = str(e)
            return False
            
    def test_stage1_road_exam(self):
        """段階1: 道路部門試験開始テスト"""
        self.log("🚀 段階1-2開始: 道路部門試験開始テスト", "INFO")
        
        try:
            # テスト1-2: 道路部門試験開始
            base_url = urllib.parse.urljoin(self.base_url, "/exam")
            params = urllib.parse.urlencode({
                "department": "道路",
                "type": "specialist",
                "questions": "10"
            })
            url = f"{base_url}?{params}"
            
            self.log(f"試験開始URL: {url}")
            
            status_code, content = self.safe_request(url)
            self.log(f"レスポンスステータス: {status_code}")
            
            if status_code == 200:
                # 問題表示確認
                if "問題" in content and ("選択肢" in content or "option" in content.lower()):
                    self.log("✅ 道路部門問題表示正常")
                    self.test_results["stage1_road_exam"] = "PASS"
                    
                    # 道路関連キーワード確認（より柔軟に）
                    road_keywords = ["道路", "アスファルト", "舗装", "交通", "橋梁", "土木", "工学"]
                    found_keywords = [kw for kw in road_keywords if kw in content]
                    if found_keywords:
                        self.log(f"✅ 関連キーワード検出: {found_keywords}")
                        self.test_results["stage1_road_keywords"] = "PASS"
                    else:
                        self.log("⚠️ 特定キーワード未検出（汎用問題の可能性）")
                        self.test_results["stage1_road_keywords"] = "WARN"
                        
                    # 問題数確認（より正確に）
                    question_count = content.count("問題") + content.count("Question") + content.count("<form")
                    if question_count > 0:
                        self.log(f"✅ 問題要素検出: {question_count}個")
                        self.test_results["stage1_question_count"] = "PASS"
                    else:
                        self.log("❌ 問題要素未検出")
                        self.test_results["stage1_question_count"] = "FAIL"
                        
                else:
                    self.log("❌ 道路部門問題表示異常")
                    self.test_results["stage1_road_exam"] = "FAIL"
                    
                return True
                
            else:
                self.log(f"❌ 道路部門試験開始失敗: {status_code}")
                self.test_results["stage1_road_exam"] = "FAIL"
                return False
                
        except Exception as e:
            self.log(f"❌ 段階1-2テストエラー: {str(e)}", "ERROR")
            self.test_results["stage1_exam_error"] = str(e)
            return False
            
    def test_stage2_other_departments(self):
        """段階2: 他部門への副作用チェック"""
        self.log("🚀 段階2開始: 他部門副作用チェック", "INFO")
        
        departments = [
            ("河川・砂防", "specialist"),
            ("トンネル", "specialist"), 
            ("基礎科目", "basic")
        ]
        
        for dept, exam_type in departments:
            try:
                self.log(f"テスト対象部門: {dept}")
                
                # 部門ページアクセステスト
                if dept == "基礎科目":
                    dept_url = urllib.parse.urljoin(self.base_url, "/department_study/基礎科目")
                else:
                    dept_url = urllib.parse.urljoin(self.base_url, f"/department_study/{dept}")
                    
                status_code, content = self.safe_request(dept_url)
                
                if status_code == 200:
                    self.log(f"✅ {dept}ページアクセス正常")
                    self.test_results[f"stage2_{dept}_access"] = "PASS"
                    
                    # 各部門の試験開始テスト
                    exam_base_url = urllib.parse.urljoin(self.base_url, "/exam")
                    exam_params = urllib.parse.urlencode({
                        "department": dept,
                        "type": exam_type,
                        "questions": "5"  # 負荷軽減のため5問に
                    })
                    exam_url = f"{exam_base_url}?{exam_params}"
                    
                    exam_status, exam_content = self.safe_request(exam_url)
                    
                    if exam_status == 200:
                        self.log(f"✅ {dept}試験開始正常")
                        self.test_results[f"stage2_{dept}_exam"] = "PASS"
                    else:
                        self.log(f"❌ {dept}試験開始異常: {exam_status}")
                        self.test_results[f"stage2_{dept}_exam"] = "FAIL"
                        
                else:
                    self.log(f"❌ {dept}ページアクセス異常: {status_code}")
                    self.test_results[f"stage2_{dept}_access"] = "FAIL"
                    
                time.sleep(1)  # サーバー負荷軽減
                
            except Exception as e:
                self.log(f"❌ {dept}テストエラー: {str(e)}", "ERROR")
                self.test_results[f"stage2_{dept}_error"] = str(e)
                
    def test_stage3_consistency_check(self):
        """段階3: 一貫性チェック（複数回実行）"""
        self.log("🚀 段階3開始: 一貫性チェック", "INFO")
        
        try:
            # 道路部門で複数回テスト
            consistent_results = []
            
            for i in range(3):
                self.log(f"一貫性テスト回数: {i+1}/3")
                
                base_url = urllib.parse.urljoin(self.base_url, "/exam")
                params = urllib.parse.urlencode({
                    "department": "道路",
                    "type": "specialist",
                    "questions": "5"  # 負荷軽減
                })
                url = f"{base_url}?{params}"
                
                status_code, content = self.safe_request(url)
                
                if status_code == 200 and "問題" in content:
                    consistent_results.append(True)
                    self.log(f"✅ 試行{i+1}: 正常")
                else:
                    consistent_results.append(False)
                    self.log(f"❌ 試行{i+1}: 異常 (status: {status_code})")
                    
                time.sleep(2)  # サーバー負荷軽減
                
            # 一貫性判定
            success_rate = sum(consistent_results) / len(consistent_results)
            
            if success_rate >= 0.8:  # 80%以上成功
                self.log(f"✅ 一貫性テスト成功率: {success_rate*100:.1f}%")
                self.test_results["stage3_consistency"] = "PASS"
            else:
                self.log(f"❌ 一貫性テスト成功率不足: {success_rate*100:.1f}%")
                self.test_results["stage3_consistency"] = "FAIL"
                
        except Exception as e:
            self.log(f"❌ 段階3テストエラー: {str(e)}", "ERROR")
            self.test_results["stage3_error"] = str(e)
            
    def run_comprehensive_test(self):
        """包括テスト実行"""
        self.log("🔥 ULTRA SYNC 修正後包括テスト開始", "INFO")
        start_time = time.time()
        
        # 段階1: 道路部門基本動作確認
        stage1_success = True
        stage1_success &= self.test_stage1_road_department()
        stage1_success &= self.test_stage1_road_exam()
        
        if not stage1_success:
            self.log("❌ 段階1失敗 - 以降のテストを中断", "ERROR")
            return False
            
        # 段階2: 副作用チェック
        self.test_stage2_other_departments()
        
        # 段階3: 一貫性チェック
        self.test_stage3_consistency_check()
        
        # 結果サマリー
        end_time = time.time()
        duration = end_time - start_time
        
        self.log(f"🔥 ULTRA SYNC 包括テスト完了 (実行時間: {duration:.2f}秒)", "INFO")
        self.generate_report()
        
        return True
        
    def generate_report(self):
        """テスト結果レポート生成"""
        self.log("📊 テスト結果レポート生成", "INFO")
        
        # 結果集計
        total_tests = len(self.test_results)
        passed_tests = sum(1 for v in self.test_results.values() if v == "PASS")
        failed_tests = sum(1 for v in self.test_results.values() if v == "FAIL")
        warned_tests = sum(1 for v in self.test_results.values() if v == "WARN")
        error_tests = sum(1 for k in self.test_results.keys() if "error" in k)
        
        print("\n" + "="*80)
        print("🔥 ULTRA SYNC 修正後動作検証レポート")
        print("="*80)
        print(f"総テスト数: {total_tests}")
        print(f"✅ 成功: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        print(f"⚠️  警告: {warned_tests}")
        print(f"🚨 エラー: {error_tests}")
        
        if total_tests > 0:
            print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        else:
            print("成功率: 0.0%")
            
        print("\n詳細結果:")
        
        for test_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(result, "🚨")
            print(f"{status_icon} {test_name}: {result}")
            
        print("\n" + "="*80)
        
        # 致命的問題チェック
        critical_failures = [k for k, v in self.test_results.items() 
                           if v == "FAIL" and ("stage1" in k or "road" in k)]
        
        if critical_failures:
            print("🚨 致命的問題検出:")
            for failure in critical_failures:
                print(f"   - {failure}")
            print("👉 即座に修正が必要です！")
        else:
            print("✅ 致命的問題は検出されませんでした")
            
        # 修正効果評価
        road_tests = [k for k in self.test_results.keys() if "road" in k]
        road_passed = [k for k, v in self.test_results.items() if "road" in k and v == "PASS"]
        
        if road_tests:
            road_success_rate = len(road_passed) / len(road_tests)
            print(f"\n📊 道路部門修正効果: {road_success_rate*100:.1f}% ({len(road_passed)}/{len(road_tests)})")
            
            if road_success_rate >= 0.8:
                print("🎉 修正は有効です！道路部門の動作が改善されました")
            else:
                print("⚠️  修正効果が不十分です。追加の調整が必要かもしれません")
                
        print("="*80)

def main():
    """メイン実行関数"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5005"
        
    print("ULTRA SYNC 修正後動作検証開始")
    print(f"対象URL: {base_url}")
    print("-" * 80)
    
    verifier = UltraSyncSimpleVerifier(base_url)
    
    try:
        success = verifier.run_comprehensive_test()
        
        if success:
            print("\nテスト完了")
        else:
            print("\nテスト中断")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nテスト中断（ユーザー操作）")
        sys.exit(1)
    except Exception as e:
        print(f"\n予期しないエラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()