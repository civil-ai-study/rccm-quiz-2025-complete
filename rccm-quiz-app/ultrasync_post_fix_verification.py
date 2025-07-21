#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: 修正後動作検証システム
段階的テストによる副作用確認とパフォーマンス検証
"""

import requests
import json
import time
import sys
from datetime import datetime
from urllib.parse import urljoin

class UltraSyncPostFixVerifier:
    """🔥 ULTRA SYNC: 修正後動作検証クラス"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {}
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_stage1_road_department(self):
        """段階1: 道路部門基本動作確認"""
        self.log("🚀 段階1開始: 道路部門基本動作確認", "INFO")
        
        try:
            # テスト1-1: 道路部門ページアクセス
            url = urljoin(self.base_url, "/department_study/道路")
            self.log(f"アクセスURL: {url}")
            
            response = self.session.get(url)
            self.log(f"レスポンスステータス: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # ランダム学習ボタンのURL確認
                if "/exam?department=道路&type=specialist" in content:
                    self.log("✅ ランダム学習ボタンURL正常: /exam?department=道路&type=specialist")
                    self.test_results["stage1_road_url"] = "PASS"
                else:
                    self.log("❌ ランダム学習ボタンURL異常")
                    self.test_results["stage1_road_url"] = "FAIL"
                    
                # ページコンテンツ確認
                if "道路" in content and "ランダム学習" in content:
                    self.log("✅ 道路部門ページコンテンツ正常")
                    self.test_results["stage1_road_content"] = "PASS"
                else:
                    self.log("❌ 道路部門ページコンテンツ異常")
                    self.test_results["stage1_road_content"] = "FAIL"
                    
            else:
                self.log(f"❌ 道路部門ページアクセス失敗: {response.status_code}")
                self.test_results["stage1_road_access"] = "FAIL"
                return False
                
            self.test_results["stage1_road_access"] = "PASS"
            return True
            
        except Exception as e:
            self.log(f"❌ 段階1テストエラー: {str(e)}", "ERROR")
            self.test_results["stage1_error"] = str(e)
            return False
            
    def test_stage1_road_exam(self):
        """段階1: 道路部門試験開始テスト"""
        self.log("🚀 段階1-2開始: 道路部門試験開始テスト", "INFO")
        
        try:
            # テスト1-2: 道路部門試験開始
            url = urljoin(self.base_url, "/exam")
            params = {
                "department": "道路",
                "type": "specialist"
            }
            
            self.log(f"試験開始URL: {url}")
            self.log(f"パラメータ: {params}")
            
            response = self.session.get(url, params=params)
            self.log(f"レスポンスステータス: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # 問題表示確認
                if "問題" in content and ("選択肢" in content or "option" in content.lower()):
                    self.log("✅ 道路部門問題表示正常")
                    self.test_results["stage1_road_exam"] = "PASS"
                    
                    # 道路関連キーワード確認
                    road_keywords = ["道路", "アスファルト", "舗装", "交通", "橋梁"]
                    found_keywords = [kw for kw in road_keywords if kw in content]
                    if found_keywords:
                        self.log(f"✅ 道路関連キーワード検出: {found_keywords}")
                        self.test_results["stage1_road_keywords"] = "PASS"
                    else:
                        self.log("⚠️ 道路関連キーワード未検出（汎用問題の可能性）")
                        self.test_results["stage1_road_keywords"] = "WARN"
                        
                else:
                    self.log("❌ 道路部門問題表示異常")
                    self.test_results["stage1_road_exam"] = "FAIL"
                    
            else:
                self.log(f"❌ 道路部門試験開始失敗: {response.status_code}")
                self.test_results["stage1_road_exam"] = "FAIL"
                return False
                
            return True
            
        except Exception as e:
            self.log(f"❌ 段階1-2テストエラー: {str(e)}", "ERROR")
            self.test_results["stage1_exam_error"] = str(e)
            return False
            
    def test_stage2_other_departments(self):
        """段階2: 他部門への副作用チェック"""
        self.log("🚀 段階2開始: 他部門副作用チェック", "INFO")
        
        departments = ["河川・砂防", "トンネル", "基礎科目"]
        
        for dept in departments:
            try:
                self.log(f"テスト対象部門: {dept}")
                
                # 部門ページアクセステスト
                if dept == "基礎科目":
                    url = urljoin(self.base_url, "/department_study/基礎科目")
                else:
                    url = urljoin(self.base_url, f"/department_study/{dept}")
                    
                response = self.session.get(url)
                
                if response.status_code == 200:
                    self.log(f"✅ {dept}ページアクセス正常")
                    self.test_results[f"stage2_{dept}_access"] = "PASS"
                    
                    # 各部門の試験開始テスト
                    if dept == "基礎科目":
                        exam_url = urljoin(self.base_url, "/exam")
                        exam_params = {"department": "基礎科目", "type": "basic"}
                    else:
                        exam_url = urljoin(self.base_url, "/exam")
                        exam_params = {"department": dept, "type": "specialist"}
                        
                    exam_response = self.session.get(exam_url, params=exam_params)
                    
                    if exam_response.status_code == 200:
                        self.log(f"✅ {dept}試験開始正常")
                        self.test_results[f"stage2_{dept}_exam"] = "PASS"
                    else:
                        self.log(f"❌ {dept}試験開始異常: {exam_response.status_code}")
                        self.test_results[f"stage2_{dept}_exam"] = "FAIL"
                        
                else:
                    self.log(f"❌ {dept}ページアクセス異常: {response.status_code}")
                    self.test_results[f"stage2_{dept}_access"] = "FAIL"
                    
                time.sleep(0.5)  # サーバー負荷軽減
                
            except Exception as e:
                self.log(f"❌ {dept}テストエラー: {str(e)}", "ERROR")
                self.test_results[f"stage2_{dept}_error"] = str(e)
                
    def test_stage3_get_mixed_questions(self):
        """段階3: get_mixed_questions関数動作確認"""
        self.log("🚀 段階3開始: get_mixed_questions関数動作確認", "INFO")
        
        try:
            # 複数回テストして一貫性確認
            for i in range(3):
                self.log(f"テスト回数: {i+1}/3")
                
                url = urljoin(self.base_url, "/exam")
                params = {
                    "department": "道路",
                    "type": "specialist",
                    "questions": "10"
                }
                
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # 問題数確認（HTMLパースは簡略化）
                    question_indicators = content.count("問題") + content.count("Question")
                    
                    if question_indicators > 0:
                        self.log(f"✅ 試行{i+1}: 問題生成正常（指標数: {question_indicators}）")
                        self.test_results[f"stage3_trial_{i+1}"] = "PASS"
                    else:
                        self.log(f"❌ 試行{i+1}: 問題生成異常")
                        self.test_results[f"stage3_trial_{i+1}"] = "FAIL"
                        
                else:
                    self.log(f"❌ 試行{i+1}: サーバーエラー {response.status_code}")
                    self.test_results[f"stage3_trial_{i+1}"] = "FAIL"
                    
                time.sleep(1)  # サーバー負荷軽減
                
            # 総合判定
            passed_trials = sum(1 for k, v in self.test_results.items() 
                              if k.startswith("stage3_trial_") and v == "PASS")
            
            if passed_trials >= 2:
                self.log("✅ 段階3総合判定: PASS")
                self.test_results["stage3_overall"] = "PASS"
            else:
                self.log("❌ 段階3総合判定: FAIL")
                self.test_results["stage3_overall"] = "FAIL"
                
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
        
        # 段階3: 関数レベル動作確認
        self.test_stage3_get_mixed_questions()
        
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
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
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
            
        print("="*80)

def main():
    """メイン実行関数"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
        
    print(f"🔥 ULTRA SYNC 修正後動作検証開始")
    print(f"対象URL: {base_url}")
    print("-" * 80)
    
    verifier = UltraSyncPostFixVerifier(base_url)
    
    try:
        success = verifier.run_comprehensive_test()
        
        if success:
            print("\n🎉 テスト完了")
        else:
            print("\n💥 テスト中断")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  テスト中断（ユーザー操作）")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()