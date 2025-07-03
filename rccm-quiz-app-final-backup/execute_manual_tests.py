#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 RCCM試験アプリ - 手動テスト実行統制スクリプト
CLAUDE.md完全準拠の厳格なテスト実行管理

実行方法: python3 execute_manual_tests.py
"""

import subprocess
import sys
import time
from datetime import datetime
import json
import os

class ManualTestExecutor:
    def __init__(self):
        self.test_start_time = datetime.now()
        self.results = []
        
    def log_execution(self, test_name, status, details):
        """テスト実行ログ"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔍"
        print(f"{status_icon} {test_name}: {details}")
    
    def check_app_running(self):
        """アプリケーションが起動しているかチェック"""
        print("🔍 アプリケーション起動状態確認中...")
        
        try:
            import requests
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                self.log_execution("アプリケーション起動確認", "SUCCESS", "アプリケーション正常稼働中")
                return True
            else:
                self.log_execution("アプリケーション起動確認", "FAILED", f"異常ステータス: {response.status_code}")
                return False
        except Exception as e:
            self.log_execution("アプリケーション起動確認", "FAILED", f"接続失敗: {str(e)}")
            return False
    
    def run_priority_tests(self):
        """最優先テスト実行（修正対象部門）"""
        print("\\n" + "="*60)
        print("🚨 PHASE 1: 最優先テスト（修正対象部門）")
        print("="*60)
        
        priority_tests = [
            {
                "script": "manual_test_water_supply.py",
                "name": "上水道部門テスト",
                "description": "修正対象部門の動作確認"
            },
            {
                "script": "manual_test_river.py", 
                "name": "河川・砂防部門テスト",
                "description": "修正対象部門の動作確認"
            }
        ]
        
        success_count = 0
        
        for test in priority_tests:
            print(f"\\n🎯 {test['name']} 実行中...")
            print(f"📝 目的: {test['description']}")
            
            try:
                result = subprocess.run([
                    sys.executable, test['script']
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.log_execution(test['name'], "SUCCESS", "全テスト成功")
                    success_count += 1
                else:
                    self.log_execution(test['name'], "FAILED", f"終了コード: {result.returncode}")
                    print(f"エラー出力: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.log_execution(test['name'], "FAILED", "タイムアウト（5分）")
            except Exception as e:
                self.log_execution(test['name'], "FAILED", f"実行エラー: {str(e)}")
        
        print(f"\\n📊 Priority Tests結果: {success_count}/{len(priority_tests)} 成功")
        return success_count == len(priority_tests)
    
    def run_comprehensive_test(self):
        """包括的テスト実行（全12部門）"""
        print("\\n" + "="*60)
        print("🧪 PHASE 2: 包括的テスト（全12部門）")
        print("="*60)
        
        print("🎯 全12部門 × 3問題数 = 36テストケース実行")
        print("⏱️ 推定所要時間: 30-60分")
        
        response = input("包括的テストを実行しますか？ [y/N]: ")
        if response.lower() != 'y':
            self.log_execution("包括的テスト", "SKIPPED", "ユーザーによりスキップ")
            return True
        
        try:
            result = subprocess.run([
                sys.executable, "comprehensive_12_departments_test.py"
            ], timeout=3600)  # 1時間タイムアウト
            
            if result.returncode == 0:
                self.log_execution("包括的テスト", "SUCCESS", "全12部門テスト完了")
                return True
            else:
                self.log_execution("包括的テスト", "FAILED", f"終了コード: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_execution("包括的テスト", "FAILED", "タイムアウト（1時間）")
            return False
        except Exception as e:
            self.log_execution("包括的テスト", "FAILED", f"実行エラー: {str(e)}")
            return False
    
    def run_additional_tests(self):
        """追加テスト実行（ペルソナ・セキュリティ等）"""
        print("\\n" + "="*60)
        print("🔍 PHASE 3: 追加テスト（オプション）")
        print("="*60)
        
        additional_tests = [
            "10ペルソナテスト",
            "エラーシナリオテスト", 
            "セキュリティテスト",
            "ブラウザ互換性テスト",
            "モバイルテスト",
            "アクセシビリティテスト",
            "パフォーマンステスト"
        ]
        
        print("利用可能な追加テスト:")
        for i, test in enumerate(additional_tests, 1):
            print(f"  {i}. {test}")
        
        response = input("追加テストを実行しますか？ [y/N]: ")
        if response.lower() != 'y':
            self.log_execution("追加テスト", "SKIPPED", "ユーザーによりスキップ")
            return True
        
        # 現在は実装なし（将来の拡張用）
        self.log_execution("追加テスト", "SKIPPED", "実装予定")
        return True
    
    def generate_final_report(self):
        """最終テストレポート生成"""
        print("\\n" + "="*60)
        print("📋 最終テストレポート生成")
        print("="*60)
        
        # 結果サマリー
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["status"] == "SUCCESS"])
        
        report = {
            "test_execution": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_duration": str(datetime.now() - self.test_start_time),
                "compliance": "CLAUDE.md完全準拠"
            },
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": f"{successful_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%"
            },
            "detailed_results": self.results
        }
        
        # レポートファイル保存
        filename = f"manual_test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 結果表示
        print(f"✅ 成功: {successful_tests}/{total_tests}")
        print(f"❌ 失敗: {total_tests - successful_tests}/{total_tests}")
        print(f"📈 成功率: {report['summary']['success_rate']}")
        print(f"📄 詳細レポート: {filename}")
        
        if successful_tests == total_tests:
            print("\\n🎉 全テスト成功！RCCM試験アプリは正常に動作しています。")
            return True
        else:
            print("\\n⚠️ 一部テストが失敗しました。詳細確認が必要です。")
            return False
    
    def execute_all_tests(self):
        """全テスト実行統制"""
        print("="*80)
        print("🧪 RCCM試験アプリ 包括的手動テスト実行")
        print(f"📅 実行開始: {self.test_start_time}")
        print(f"📋 準拠基準: CLAUDE.md完走テスト実行ルール")
        print("="*80)
        
        # Step 1: アプリケーション起動確認
        if not self.check_app_running():
            print("❌ アプリケーションが起動していません。")
            print("💡 解決方法: python app.py でアプリケーションを起動してください。")
            return False
        
        # Step 2: 最優先テスト（修正対象部門）
        priority_success = self.run_priority_tests()
        
        # Step 3: 包括的テスト（全12部門）
        comprehensive_success = self.run_comprehensive_test()
        
        # Step 4: 追加テスト（オプション）
        additional_success = self.run_additional_tests()
        
        # Step 5: 最終レポート生成
        final_success = self.generate_final_report()
        
        return priority_success and comprehensive_success and additional_success and final_success

if __name__ == "__main__":
    print("🚀 RCCM試験アプリ手動テスト実行開始")
    print("⚠️ このプロセスには時間がかかります")
    print("📋 CLAUDE.md準拠の厳格なテスト実行を行います")
    
    executor = ManualTestExecutor()
    success = executor.execute_all_tests()
    
    if success:
        print("\\n✅ 全テスト実行完了 - 成功")
    else:
        print("\\n❌ テスト実行中にエラーが発生しました")
    
    exit(0 if success else 1)