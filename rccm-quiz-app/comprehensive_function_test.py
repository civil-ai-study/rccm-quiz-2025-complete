#!/usr/bin/env python3
"""
🔥 CRITICAL: 包括的機能テスト - ウルトラシンク対応
基礎科目全問題 + 復習機能 + 全画面リンク + ナビゲーション
"""

import requests
import time
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

class ComprehensiveFunctionTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        self.errors = []
        
    def log(self, category, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(status, "ℹ️")
        print(f"[{timestamp}] {status_icon} {category}: {message}")
        
        if status == "ERROR":
            self.errors.append(f"{category}: {message}")
            
    def extract_links_from_page(self, html):
        """ページから全リンクを抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            links.append({'href': href, 'text': text})
        return links
        
    def test_basic_subject_all_questions(self):
        """基礎科目(4-1)全問題テスト"""
        self.log("基礎科目", "全問題解答テスト開始")
        
        try:
            # 基礎科目開始
            response = self.session.get(f"{self.base_url}/exam?question_type=basic")
            
            if response.status_code != 200:
                self.log("基礎科目", f"開始失敗: Status {response.status_code}", "ERROR")
                return False
                
            questions_completed = 0
            max_questions = 50  # 安全のため50問まで（実際は10問セッション）
            
            for question_no in range(1, max_questions + 1):
                # 進捗とQID抽出
                progress_match = re.search(r'(\d+)/10', response.text)
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                
                if not qid_match:
                    self.log("基礎科目", f"問題{question_no}: QID未検出 - セッション終了", "WARNING")
                    break
                    
                current_progress = progress_match.group(1) if progress_match else "?"
                qid = qid_match.group(1)
                
                self.log("基礎科目", f"問題{question_no}: 進捗{current_progress}/10, QID:{qid}")
                
                # 回答送信
                answer_data = {'answer': 'A', 'qid': qid, 'elapsed': 2}
                response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                
                if response.status_code != 200:
                    self.log("基礎科目", f"問題{question_no}: 回答失敗 Status {response.status_code}", "ERROR")
                    break
                    
                # 次の問題へ進む処理
                if "次の問題" in response.text:
                    next_match = re.search(r'href="/exam\?next=(\d+)&current=(\d+)"', response.text)
                    if next_match:
                        next_url = f"/exam?next={next_match.group(1)}&current={next_match.group(2)}"
                        response = self.session.get(f"{self.base_url}{next_url}")
                        questions_completed += 1
                    else:
                        self.log("基礎科目", f"問題{question_no}: 次の問題URL未検出", "ERROR")
                        break
                elif "結果を見る" in response.text:
                    questions_completed += 1
                    self.log("基礎科目", f"問題{question_no}: セッション完了 - {questions_completed}問達成", "SUCCESS")
                    break
                else:
                    self.log("基礎科目", f"問題{question_no}: 予期しない応答", "ERROR")
                    break
                    
                time.sleep(0.2)
                
            self.test_results['basic_subject'] = {"completed": questions_completed, "status": "SUCCESS" if questions_completed >= 10 else "PARTIAL"}
            return questions_completed >= 10
            
        except Exception as e:
            self.log("基礎科目", f"例外発生: {str(e)}", "ERROR")
            self.test_results['basic_subject'] = {"status": "ERROR", "error": str(e)}
            return False
            
    def test_review_functions(self):
        """復習機能完全テスト"""
        self.log("復習機能", "完全機能テスト開始")
        
        try:
            # 1. 復習リストアクセス
            response = self.session.get(f"{self.base_url}/review")
            if response.status_code != 200:
                self.log("復習機能", f"復習リストアクセス失敗: {response.status_code}", "ERROR")
                return False
            self.log("復習機能", "復習リストアクセス成功", "SUCCESS")
            
            # 2. 復習リストの内容確認
            if "復習リストが空" in response.text:
                self.log("復習機能", "復習リスト空 - 問題を間違えて復習登録テスト", "INFO")
                
                # 基礎科目で意図的に間違い回答して復習登録
                exam_response = self.session.get(f"{self.base_url}/exam?question_type=basic")
                if exam_response.status_code == 200:
                    qid_match = re.search(r'name="qid" value="(\d+)"', exam_response.text)
                    if qid_match:
                        # 間違い回答で復習登録
                        wrong_answer_data = {'answer': 'D', 'qid': qid_match.group(1), 'elapsed': 3}
                        wrong_response = self.session.post(f"{self.base_url}/exam", data=wrong_answer_data)
                        
                        if "復習登録" in wrong_response.text:
                            self.log("復習機能", "間違い回答による復習登録確認", "SUCCESS")
                        else:
                            self.log("復習機能", "復習登録ボタン未検出", "WARNING")
            else:
                self.log("復習機能", "復習リストに既存データあり", "INFO")
                
            # 3. 復習問題実行テスト
            review_exam_response = self.session.get(f"{self.base_url}/exam/review")
            if review_exam_response.status_code == 200:
                if "復習リストが空" in review_exam_response.text:
                    self.log("復習機能", "復習問題実行 - リスト空（正常）", "SUCCESS")
                else:
                    self.log("復習機能", "復習問題実行 - 問題表示確認", "SUCCESS")
            else:
                self.log("復習機能", f"復習問題実行失敗: {review_exam_response.status_code}", "ERROR")
                return False
                
            # 4. 復習機能リンクテスト
            links_to_test = [
                "/review",
                "/review?department=road", 
                "/statistics"
            ]
            
            for link in links_to_test:
                test_response = self.session.get(f"{self.base_url}{link}")
                if test_response.status_code == 200:
                    self.log("復習機能", f"リンクテスト成功: {link}", "SUCCESS")
                else:
                    self.log("復習機能", f"リンクテスト失敗: {link} - Status {test_response.status_code}", "ERROR")
                    
            self.test_results['review_functions'] = {"status": "SUCCESS"}
            return True
            
        except Exception as e:
            self.log("復習機能", f"例外発生: {str(e)}", "ERROR")
            self.test_results['review_functions'] = {"status": "ERROR", "error": str(e)}
            return False
            
    def test_all_navigation_links(self):
        """全ナビゲーションリンクテスト"""
        self.log("ナビゲーション", "全リンクテスト開始")
        
        # メインナビゲーションリンク
        nav_links = [
            "/",
            "/statistics", 
            "/categories",
            "/review",
            "/reset",
            "/help"
        ]
        
        # 部門別リンク
        departments = ['road', 'civil_planning', 'tunnel', 'urban_planning', 'landscape', 
                      'construction_env', 'steel_concrete', 'soil_foundation', 
                      'construction_planning', 'water_supply', 'forestry', 'agriculture']
        
        for dept in departments:
            nav_links.append(f"/department_study/{dept}")
            nav_links.append(f"/exam?department={dept}&type=specialist")
            
        # 基礎科目リンク
        nav_links.extend([
            "/exam?question_type=basic",
            "/exam/review"
        ])
        
        success_count = 0
        total_links = len(nav_links)
        
        for link in nav_links:
            try:
                response = self.session.get(f"{self.base_url}{link}")
                if response.status_code == 200:
                    self.log("ナビゲーション", f"✓ {link}", "SUCCESS")
                    success_count += 1
                elif response.status_code == 302:
                    self.log("ナビゲーション", f"↗ {link} (リダイレクト)", "INFO")
                    success_count += 1
                else:
                    self.log("ナビゲーション", f"✗ {link} - Status {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log("ナビゲーション", f"✗ {link} - Exception: {str(e)}", "ERROR")
                
            time.sleep(0.1)
            
        success_rate = (success_count / total_links) * 100
        self.log("ナビゲーション", f"テスト完了: {success_count}/{total_links} ({success_rate:.1f}%)", "SUCCESS" if success_rate >= 95 else "WARNING")
        
        self.test_results['navigation'] = {"success_count": success_count, "total": total_links, "rate": success_rate}
        return success_rate >= 95
        
    def test_all_page_interactions(self):
        """全ページインタラクションテスト"""
        self.log("ページ機能", "インタラクション機能テスト開始")
        
        try:
            # 1. ホームページの全リンクテスト
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                links = self.extract_links_from_page(response.text)
                self.log("ページ機能", f"ホームページから{len(links)}個のリンクを検出", "INFO")
                
                for link in links[:10]:  # 最初の10個をテスト
                    if link['href'].startswith('/') or link['href'].startswith('http'):
                        try:
                            if link['href'].startswith('/'):
                                test_url = f"{self.base_url}{link['href']}"
                            else:
                                test_url = link['href']
                                
                            test_response = self.session.get(test_url, timeout=5)
                            if test_response.status_code in [200, 302]:
                                self.log("ページ機能", f"✓ リンク: {link['text'][:30]}", "SUCCESS")
                            else:
                                self.log("ページ機能", f"✗ リンク: {link['text'][:30]} - Status {test_response.status_code}", "ERROR")
                        except:
                            self.log("ページ機能", f"⚠ リンク: {link['text'][:30]} - アクセス不可", "WARNING")
                            
            # 2. フォーム機能テスト（基礎科目）
            exam_response = self.session.get(f"{self.base_url}/exam?question_type=basic")
            if exam_response.status_code == 200 and 'form' in exam_response.text:
                self.log("ページ機能", "フォーム機能検出・テスト実行", "SUCCESS")
            else:
                self.log("ページ機能", "フォーム機能テスト失敗", "ERROR")
                
            # 3. JavaScript機能テスト（タイマー等）
            if 'timer-display' in exam_response.text:
                self.log("ページ機能", "JavaScript機能検出（タイマー等）", "SUCCESS")
            else:
                self.log("ページ機能", "JavaScript機能未検出", "WARNING")
                
            self.test_results['page_interactions'] = {"status": "SUCCESS"}
            return True
            
        except Exception as e:
            self.log("ページ機能", f"例外発生: {str(e)}", "ERROR")
            self.test_results['page_interactions'] = {"status": "ERROR", "error": str(e)}
            return False
            
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🚀 包括的機能テスト開始 - ウルトラシンク対応")
        print("=" * 80)
        
        start_time = time.time()
        
        # 1. 基礎科目全問題テスト
        print("\n📚 基礎科目(4-1)全問題テスト...")
        basic_success = self.test_basic_subject_all_questions()
        
        # 2. 復習機能テスト
        print("\n🔖 復習機能完全テスト...")
        review_success = self.test_review_functions()
        
        # 3. ナビゲーションテスト
        print("\n🧭 ナビゲーション全リンクテスト...")
        nav_success = self.test_all_navigation_links()
        
        # 4. ページ機能テスト
        print("\n💻 ページ機能インタラクションテスト...")
        page_success = self.test_all_page_interactions()
        
        # 最終結果
        end_time = time.time()
        total_tests = 4
        passed_tests = sum([basic_success, review_success, nav_success, page_success])
        
        print("\n" + "=" * 80)
        print("🎯 包括的機能テスト最終結果")
        print("=" * 80)
        print(f"⏱️  実行時間: {end_time - start_time:.1f}秒")
        print(f"📊 テスト項目: {total_tests}")
        print(f"✅ 成功: {passed_tests}")
        print(f"❌ 失敗: {total_tests - passed_tests}")
        print(f"📈 成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        # 詳細結果
        print("\n📋 詳細結果:")
        print(f"  {'✅' if basic_success else '❌'} 基礎科目全問題テスト")
        print(f"  {'✅' if review_success else '❌'} 復習機能完全テスト")
        print(f"  {'✅' if nav_success else '❌'} ナビゲーション全リンクテスト")
        print(f"  {'✅' if page_success else '❌'} ページ機能インタラクションテスト")
        
        # エラー詳細
        if self.errors:
            print(f"\n⚠️ 検出されたエラー ({len(self.errors)}件):")
            for error in self.errors[:10]:  # 最初の10件のみ表示
                print(f"  • {error}")
                
        if passed_tests == total_tests and len(self.errors) == 0:
            print("\n🎉 ウルトラシンク完全成功！全機能正常動作確認！")
            return True
        else:
            print(f"\n⚠️ 不完全な結果 - ウルトラシンク修正が必要")
            return False

if __name__ == "__main__":
    print("🔧 サーバー動作確認中...")
    time.sleep(1)
    
    tester = ComprehensiveFunctionTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ 包括的機能テスト完全成功！")
    else:
        print("\n❌ テスト未完了 - ウルトラシンク修正実行中...")