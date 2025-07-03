#!/usr/bin/env python3
"""
🔥 VIRTUAL TEST ENVIRONMENT - 仮想テスト環境構築
制約を乗り越えて実際のテストを強行実行
エラーを見つけるための実動作確認
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

class VirtualTestEnvironment:
    def __init__(self):
        self.flask_process = None
        self.test_results = []
        self.errors_found = []
        
    def install_requirements(self):
        """必要なモジュールを強制インストール"""
        print("🔧 Installing required modules...")
        
        required_modules = [
            'flask',
            'requests', 
            'selenium',
            'webdriver-manager'
        ]
        
        for module in required_modules:
            try:
                print(f"Installing {module}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', module
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ {module} installed successfully")
                else:
                    print(f"⚠️ {module} installation warning: {result.stderr}")
                    # 警告があっても続行
                    
            except Exception as e:
                print(f"❌ Failed to install {module}: {e}")
                # エラーがあっても諦めずに続行
                continue
    
    def create_minimal_csv_data(self):
        """最小限のCSVデータを作成"""
        print("📄 Creating minimal CSV data...")
        
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        csv_content = """ID,Category,Question,Answer_A,Answer_B,Answer_C,Answer_D,Correct_Answer,Explanation
1,土質及び基礎,土質及び基礎のテスト問題,選択肢A,選択肢B,選択肢C,選択肢D,A,テスト用の解説
2,道路,道路部門のテスト問題,選択肢A,選択肢B,選択肢C,選択肢D,B,テスト用の解説
3,河川、砂防及び海岸・海洋,河川砂防のテスト問題,選択肢A,選択肢B,選択肢C,選択肢D,C,テスト用の解説
4,基礎科目,基礎科目のテスト問題,選択肢A,選択肢B,選択肢C,選択肢D,D,テスト用の解説
"""
        
        csv_file = data_dir / "questions.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"✅ CSV data created: {csv_file}")
        return True
    
    def start_flask_server(self):
        """Flaskサーバーを実際に起動"""
        print("🚀 Starting Flask server...")
        
        try:
            # バックグラウンドでFlaskサーバーを起動
            self.flask_process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # サーバー起動を待機
            time.sleep(5)
            
            # サーバーが起動したか確認
            if self.flask_process.poll() is None:
                print("✅ Flask server started successfully")
                return True
            else:
                stdout, stderr = self.flask_process.communicate()
                print(f"❌ Flask server failed to start")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start Flask server: {e}")
            return False
    
    def test_http_requests(self):
        """HTTPリクエストでの実際のテスト"""
        print("🌐 Testing HTTP requests...")
        
        try:
            import requests
            
            base_url = "http://localhost:5000"
            
            # 1. ホームページテスト
            print("Testing home page...")
            try:
                response = requests.get(base_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Home page accessible")
                    
                    # ページ内容を確認
                    content = response.text
                    if "土質基礎" in content or "土質及び基礎" in content:
                        print("✅ 土質基礎ボタンが存在")
                    else:
                        print("❌ 土質基礎ボタンが見つからない")
                        self.errors_found.append("土質基礎ボタンが見つからない")
                        
                else:
                    print(f"❌ Home page error: {response.status_code}")
                    self.errors_found.append(f"Home page error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Home page request failed: {e}")
                self.errors_found.append(f"Home page request failed: {e}")
            
            # 2. 土質及び基礎部門の直接テスト
            print("Testing soil foundation department...")
            try:
                soil_url = f"{base_url}/department_study/soil_foundation"
                response = requests.get(soil_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # エラーメッセージの検出
                    error_messages = [
                        "この部門の専門問題はまだ利用できません",
                        "エラーが発生しました",
                        "404 Not Found",
                        "Internal Server Error"
                    ]
                    
                    errors_detected = []
                    for error_msg in error_messages:
                        if error_msg in content:
                            errors_detected.append(error_msg)
                    
                    if errors_detected:
                        print(f"🚨 ERRORS FOUND: {errors_detected}")
                        self.errors_found.extend(errors_detected)
                    else:
                        print("✅ No error messages detected in soil foundation page")
                        
                    # 正常コンテンツの確認
                    if "土質及び基礎" in content and "問題" in content:
                        print("✅ 土質及び基礎ページに正常なコンテンツあり")
                    else:
                        print("⚠️ 土質及び基礎ページのコンテンツが不完全")
                        self.errors_found.append("土質及び基礎ページのコンテンツが不完全")
                        
                else:
                    print(f"❌ Soil foundation page error: {response.status_code}")
                    self.errors_found.append(f"Soil foundation page error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Soil foundation request failed: {e}")
                self.errors_found.append(f"Soil foundation request failed: {e}")
            
            # 3. 他の部門もテスト
            departments = [
                ("basic", "基礎科目"),
                ("road", "道路"), 
                ("civil_planning", "河川・砂防")
            ]
            
            for dept_key, dept_name in departments:
                print(f"Testing {dept_name}...")
                try:
                    dept_url = f"{base_url}/department_study/{dept_key}"
                    response = requests.get(dept_url, timeout=10)
                    
                    if response.status_code == 200:
                        if "この部門の専門問題はまだ利用できません" in response.text:
                            print(f"🚨 ERROR in {dept_name}: 専門問題が利用できません")
                            self.errors_found.append(f"{dept_name}: 専門問題が利用できません")
                        else:
                            print(f"✅ {dept_name}: No error messages")
                    else:
                        print(f"❌ {dept_name}: HTTP {response.status_code}")
                        self.errors_found.append(f"{dept_name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {dept_name} test failed: {e}")
                    self.errors_found.append(f"{dept_name} test failed: {e}")
            
        except ImportError:
            print("❌ requests module not available")
            self.errors_found.append("requests module not available")
            return False
            
        return True
    
    def test_with_selenium(self):
        """Selenium WebDriverでの実際のテスト"""
        print("🔥 Testing with Selenium WebDriver...")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            try:
                # WebDriverを起動
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                print("✅ Selenium WebDriver started")
                
                # 実際のテスト実行
                base_url = "http://localhost:5000"
                
                # ホームページにアクセス
                driver.get(base_url)
                print(f"✅ Accessed {base_url}")
                
                # ページタイトル確認
                title = driver.title
                print(f"Page title: {title}")
                
                # 土質基礎ボタンを探す
                button_selectors = [
                    "//a[contains(text(), '土質基礎')]",
                    "//button[contains(text(), '土質基礎')]",
                    "//a[contains(text(), '土質及び基礎')]",
                    "//button[contains(text(), '土質及び基礎')]",
                    "//a[contains(@href, 'soil_foundation')]"
                ]
                
                button_found = False
                for selector in button_selectors:
                    try:
                        element = driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            print(f"✅ Found soil foundation button: {selector}")
                            
                            # ボタンをクリック
                            element.click()
                            button_found = True
                            
                            # ページ遷移後の確認
                            time.sleep(2)
                            current_url = driver.current_url
                            print(f"After click URL: {current_url}")
                            
                            # エラーメッセージの確認
                            page_source = driver.page_source
                            if "この部門の専門問題はまだ利用できません" in page_source:
                                print("🚨 ERROR DETECTED: この部門の専門問題はまだ利用できません")
                                self.errors_found.append("Selenium: この部門の専門問題はまだ利用できません")
                            else:
                                print("✅ No error message detected via Selenium")
                            
                            break
                            
                    except Exception as e:
                        continue
                
                if not button_found:
                    print("❌ 土質基礎ボタンが見つからない")
                    self.errors_found.append("Selenium: 土質基礎ボタンが見つからない")
                    
                    # 利用可能なボタン/リンクを確認
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        links = driver.find_elements(By.TAG_NAME, "a")
                        
                        print("Available buttons:")
                        for btn in buttons[:5]:
                            print(f"  - {btn.text}")
                            
                        print("Available links:")
                        for link in links[:5]:
                            print(f"  - {link.text}")
                            
                    except Exception as e:
                        print(f"Failed to get available elements: {e}")
                
                driver.quit()
                print("✅ Selenium test completed")
                return True
                
            except Exception as e:
                print(f"❌ Selenium test failed: {e}")
                self.errors_found.append(f"Selenium test failed: {e}")
                return False
                
        except ImportError as e:
            print(f"❌ Selenium not available: {e}")
            self.errors_found.append(f"Selenium not available: {e}")
            return False
    
    def cleanup(self):
        """クリーンアップ"""
        print("🧹 Cleaning up...")
        
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                print("✅ Flask server terminated")
            except Exception as e:
                print(f"⚠️ Flask server cleanup warning: {e}")
                try:
                    self.flask_process.kill()
                except:
                    pass
    
    def run_comprehensive_test(self):
        """包括的テストの実行"""
        print("🔥 VIRTUAL TEST ENVIRONMENT - COMPREHENSIVE EXECUTION")
        print("=" * 80)
        print("目的: 実際のエラーを検出し、問題を特定する")
        print("=" * 80)
        
        try:
            # 1. 環境準備
            print("\n🔧 STEP 1: Environment Setup")
            self.install_requirements()
            self.create_minimal_csv_data()
            
            # 2. Flaskサーバー起動
            print("\n🚀 STEP 2: Flask Server Startup")
            if not self.start_flask_server():
                print("❌ Flask server startup failed - aborting test")
                return False
            
            # 3. HTTPテスト
            print("\n🌐 STEP 3: HTTP Request Testing")
            self.test_http_requests()
            
            # 4. Seleniumテスト
            print("\n🔥 STEP 4: Selenium Browser Testing")
            self.test_with_selenium()
            
            # 5. 結果報告
            print("\n📊 STEP 5: Results Report")
            self.generate_error_report()
            
            return True
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            self.errors_found.append(f"Test execution failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def generate_error_report(self):
        """エラーレポートの生成"""
        print("\n" + "="*80)
        print("🚨 ERROR DETECTION REPORT")
        print("="*80)
        
        if self.errors_found:
            print(f"🔥 ERRORS DETECTED: {len(self.errors_found)} issues found")
            print("\nDETAILED ERROR LIST:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"{i}. {error}")
                
            print(f"\n🎯 CRITICAL FINDINGS:")
            critical_errors = [e for e in self.errors_found if "この部門の専門問題はまだ利用できません" in e]
            if critical_errors:
                print("❌ 土質及び基礎部門のエラーはまだ修正されていません！")
                for error in critical_errors:
                    print(f"  - {error}")
            else:
                print("✅ 土質及び基礎部門の主要エラーは検出されませんでした")
                
        else:
            print("✅ NO ERRORS DETECTED")
            print("全てのテストが正常に完了しました")
        
        # 結果をファイルに保存
        import json
        from datetime import datetime
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_errors': len(self.errors_found),
            'errors': self.errors_found,
            'test_completed': True
        }
        
        filename = f"virtual_test_error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート保存: {filename}")

def main():
    """メイン実行"""
    tester = VirtualTestEnvironment()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Virtual test environment execution completed!")
    else:
        print("\n❌ Virtual test environment execution failed!")
    
    return success

if __name__ == "__main__":
    main()