#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ E2E テスト セットアップ検証スクリプト
=====================================

ULTRATHIN E2E テストの環境とセットアップを検証します。

Author: Claude Code
Version: 1.0.0
Date: 2025-07-05
"""

import sys
import os
import importlib.util
import subprocess
from typing import Dict, List, Tuple

class E2ETestSetupValidator:
    """
    E2E テスト環境の検証クラス
    """
    
    def __init__(self):
        self.validation_results = {
            "overall_status": "pending",
            "checks": [],
            "recommendations": []
        }
    
    def check_python_version(self) -> Tuple[bool, str]:
        """
        Python バージョンの確認
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 7:
                return True, f"Python {version.major}.{version.minor}.{version.micro}"
            else:
                return False, f"Python {version.major}.{version.minor}.{version.micro} (3.7以上が必要)"
        except Exception as e:
            return False, f"Python バージョン確認エラー: {e}"
    
    def check_selenium_installation(self) -> Tuple[bool, str]:
        """
        Selenium インストール確認
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            import selenium
            return True, f"Selenium {selenium.__version__}"
        except ImportError:
            return False, "Selenium がインストールされていません"
        except Exception as e:
            return False, f"Selenium 確認エラー: {e}"
    
    def check_chrome_availability(self) -> Tuple[bool, str]:
        """
        Chrome ブラウザの確認
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            # Chrome の実行可能性確認
            chrome_commands = [
                "google-chrome --version",
                "chrome --version",
                "chromium --version",
                "chromium-browser --version"
            ]
            
            for cmd in chrome_commands:
                try:
                    result = subprocess.run(
                        cmd.split(), 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    if result.returncode == 0:
                        return True, f"Chrome 確認: {result.stdout.strip()}"
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return False, "Chrome ブラウザが見つかりません"
            
        except Exception as e:
            return False, f"Chrome 確認エラー: {e}"
    
    def check_test_files(self) -> Tuple[bool, str]:
        """
        テストファイルの確認
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            required_files = [
                "ultrathin_selenium_e2e_test_zero_sideeffects.py",
                "run_ultrathin_e2e_test.py",
                "ULTRATHIN_E2E_TEST_README.md"
            ]
            
            missing_files = []
            existing_files = []
            
            for file_name in required_files:
                if os.path.exists(file_name):
                    existing_files.append(file_name)
                else:
                    missing_files.append(file_name)
            
            if missing_files:
                return False, f"不足ファイル: {', '.join(missing_files)}"
            else:
                return True, f"全必要ファイル存在: {len(existing_files)}個"
                
        except Exception as e:
            return False, f"ファイル確認エラー: {e}"
    
    def check_test_script_syntax(self) -> Tuple[bool, str]:
        """
        テストスクリプトの構文確認
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            test_file = "ultrathin_selenium_e2e_test_zero_sideeffects.py"
            
            if not os.path.exists(test_file):
                return False, f"テストファイルが見つかりません: {test_file}"
            
            # 構文チェック
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec is None:
                return False, "テストファイルの構文に問題があります"
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # クラスの存在確認
            if hasattr(module, 'UltraThinE2ETestZeroSideEffects'):
                return True, "テストスクリプト構文OK"
            else:
                return False, "テストクラスが見つかりません"
                
        except Exception as e:
            return False, f"構文確認エラー: {e}"
    
    def check_port_availability(self, port: int = 5000) -> Tuple[bool, str]:
        """
        ポートの使用確認
        
        Args:
            port: 確認するポート番号
            
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                return True, f"ポート {port} でサービスが実行中"
            else:
                return False, f"ポート {port} でサービスが見つかりません"
                
        except Exception as e:
            return False, f"ポート確認エラー: {e}"
    
    def run_validation(self) -> Dict:
        """
        全検証の実行
        
        Returns:
            Dict: 検証結果
        """
        print("🛡️ E2E テスト セットアップ検証開始")
        print("=" * 50)
        
        # 検証項目の定義
        validation_checks = [
            ("Python バージョン", self.check_python_version),
            ("Selenium インストール", self.check_selenium_installation),
            ("Chrome ブラウザ", self.check_chrome_availability),
            ("テストファイル", self.check_test_files),
            ("スクリプト構文", self.check_test_script_syntax),
            ("アプリケーション", lambda: self.check_port_availability(5000))
        ]
        
        passed_checks = 0
        failed_checks = 0
        
        for check_name, check_func in validation_checks:
            try:
                success, message = check_func()
                
                check_result = {
                    "name": check_name,
                    "status": "passed" if success else "failed",
                    "message": message
                }
                
                self.validation_results["checks"].append(check_result)
                
                if success:
                    print(f"✅ {check_name}: {message}")
                    passed_checks += 1
                else:
                    print(f"❌ {check_name}: {message}")
                    failed_checks += 1
                    
            except Exception as e:
                print(f"❌ {check_name}: 検証エラー - {e}")
                failed_checks += 1
                
                check_result = {
                    "name": check_name,
                    "status": "error",
                    "message": f"検証エラー: {e}"
                }
                self.validation_results["checks"].append(check_result)
        
        # 総合結果
        total_checks = len(validation_checks)
        success_rate = (passed_checks / total_checks) * 100
        
        print(f"\n📊 検証結果:")
        print(f"  - 総検証数: {total_checks}")
        print(f"  - 成功: {passed_checks}")
        print(f"  - 失敗: {failed_checks}")
        print(f"  - 成功率: {success_rate:.1f}%")
        
        if failed_checks == 0:
            self.validation_results["overall_status"] = "passed"
            print("\n✅ 全ての検証が成功しました！")
            print("E2E テストを実行する準備が整いました。")
        else:
            self.validation_results["overall_status"] = "failed"
            print(f"\n⚠️ {failed_checks}個の検証が失敗しました。")
            self.generate_recommendations()
        
        return self.validation_results
    
    def generate_recommendations(self):
        """
        推奨事項の生成
        """
        print("\n🔧 推奨事項:")
        
        for check in self.validation_results["checks"]:
            if check["status"] == "failed":
                check_name = check["name"]
                
                if "Python" in check_name:
                    print("  - Python 3.7以上をインストールしてください")
                    self.validation_results["recommendations"].append("Python 3.7以上のインストール")
                
                elif "Selenium" in check_name:
                    print("  - pip install selenium でSeleniumをインストールしてください")
                    self.validation_results["recommendations"].append("Selenium パッケージのインストール")
                
                elif "Chrome" in check_name:
                    print("  - Google Chrome または Chromium をインストールしてください")
                    self.validation_results["recommendations"].append("Chrome ブラウザのインストール")
                
                elif "ファイル" in check_name:
                    print("  - 必要なテストファイルが不足しています")
                    self.validation_results["recommendations"].append("テストファイルの確認")
                
                elif "構文" in check_name:
                    print("  - テストスクリプトの構文に問題があります")
                    self.validation_results["recommendations"].append("テストスクリプトの修正")
                
                elif "アプリケーション" in check_name:
                    print("  - アプリケーションをポート5000で起動してください")
                    print("    例: python app.py")
                    self.validation_results["recommendations"].append("アプリケーションの起動")


def main():
    """
    メイン実行関数
    """
    validator = E2ETestSetupValidator()
    results = validator.run_validation()
    
    # 結果に基づく終了コード
    if results["overall_status"] == "passed":
        print("\n🚀 E2E テスト実行コマンド:")
        print("python run_ultrathin_e2e_test.py")
        return 0
    else:
        print("\n❌ セットアップに問題があります。上記の推奨事項を確認してください。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)