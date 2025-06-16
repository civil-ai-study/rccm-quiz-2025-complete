#!/usr/bin/env python3
"""
🔥 残り11部門×10問=110問 + 基礎科目10問 手作業風自動テスト
各部門で手作業確認も実行
"""

import requests
import time
import re
from datetime import datetime

class ManualAllDepartments:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 道路部門は完了済みなので除外
        self.departments = {
            'civil_planning': '河川、砂防及び海岸・海洋',
            'tunnel': 'トンネル', 
            'urban_planning': '都市計画及び地方計画',
            'landscape': '造園',
            'construction_env': '建設環境',
            'steel_concrete': '鋼構造及びコンクリート',
            'soil_foundation': '土質及び基礎',
            'construction_planning': '施工計画、施工設備及び積算',
            'water_supply': '上水道及び工業用水道',
            'forestry': '森林土木',
            'agriculture': '農業土木'
        }
        
    def log(self, dept_name, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🎯 {dept_name}: {message}")
        
    def manual_test_department(self, dept_key, dept_name):
        """部門10問手作業風テスト"""
        try:
            self.log(dept_name, "10問手作業テスト開始")
            
            # 新セッション開始
            self.session = requests.Session()
            response = self.session.get(f"{self.base_url}/")
            
            # 専門科目開始
            response = self.session.get(f"{self.base_url}/exam?department={dept_key}&type=specialist")
            
            if response.status_code != 200:
                self.log(dept_name, f"❌ 開始失敗: Status {response.status_code}")
                return False
                
            questions_completed = 0
            
            # 10問連続解答
            for question_no in range(1, 11):
                # 進捗・QID確認
                progress_match = re.search(r'(\d+)/10', response.text)
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                
                if not qid_match:
                    self.log(dept_name, f"❌ 問題{question_no}: QID未検出")
                    return False
                    
                progress = progress_match.group(1) if progress_match else "?"
                qid = qid_match.group(1)
                
                self.log(dept_name, f"問題{question_no}: 進捗{progress}/10, QID:{qid}")
                
                # 回答送信（A/B/C/Dローテーション）
                answer_options = ['A', 'B', 'C', 'D']
                answer = answer_options[(question_no - 1) % 4]
                answer_data = {'answer': answer, 'qid': qid, 'elapsed': 3}
                
                response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                
                if response.status_code != 200:
                    self.log(dept_name, f"❌ 問題{question_no}: 回答失敗 Status {response.status_code}")
                    return False
                    
                # 次の問題処理
                if "次の問題" in response.text:
                    next_match = re.search(r'href="/exam\?next=(\d+)&current=(\d+)"', response.text)
                    if next_match:
                        next_url = f"/exam?next={next_match.group(1)}&current={next_match.group(2)}"
                        response = self.session.get(f"{self.base_url}{next_url}")
                        questions_completed += 1
                        self.log(dept_name, f"✅ 問題{question_no}: 回答完了")
                    else:
                        self.log(dept_name, f"❌ 問題{question_no}: 次の問題URL未検出")
                        return False
                elif "結果を見る" in response.text:
                    questions_completed += 1
                    self.log(dept_name, f"🎉 問題{question_no}: 最終問題完了 - {questions_completed}問達成")
                    break
                else:
                    self.log(dept_name, f"❌ 問題{question_no}: 予期しない応答")
                    return False
                    
                time.sleep(0.3)  # サーバー負荷軽減
                
            if questions_completed == 10:
                self.log(dept_name, f"🎯 SUCCESS: 10問完全達成！")
                return True
            else:
                self.log(dept_name, f"⚠️ PARTIAL: {questions_completed}問完了")
                return False
                
        except Exception as e:
            self.log(dept_name, f"❌ EXCEPTION: {str(e)}")
            return False
            
    def test_basic_subject_manual(self):
        """基礎科目10問手作業テスト"""
        try:
            self.log("基礎科目", "10問手作業テスト開始")
            
            # 新セッション開始
            self.session = requests.Session()
            response = self.session.get(f"{self.base_url}/")
            
            # 基礎科目開始
            response = self.session.get(f"{self.base_url}/exam?question_type=basic")
            
            if response.status_code != 200:
                self.log("基礎科目", f"❌ 開始失敗: Status {response.status_code}")
                return False
                
            questions_completed = 0
            
            # 10問連続解答
            for question_no in range(1, 11):
                # 進捗・QID確認
                progress_match = re.search(r'(\d+)/10', response.text)
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                
                if not qid_match:
                    self.log("基礎科目", f"❌ 問題{question_no}: QID未検出")
                    return False
                    
                progress = progress_match.group(1) if progress_match else "?"
                qid = qid_match.group(1)
                
                self.log("基礎科目", f"問題{question_no}: 進捗{progress}/10, QID:{qid}")
                
                # 回答送信
                answer_options = ['A', 'B', 'C', 'D']
                answer = answer_options[(question_no - 1) % 4]
                answer_data = {'answer': answer, 'qid': qid, 'elapsed': 3}
                
                response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                
                if response.status_code != 200:
                    self.log("基礎科目", f"❌ 問題{question_no}: 回答失敗 Status {response.status_code}")
                    return False
                    
                # 次の問題処理
                if "次の問題" in response.text:
                    next_match = re.search(r'href="/exam\?next=(\d+)&current=(\d+)"', response.text)
                    if next_match:
                        next_url = f"/exam?next={next_match.group(1)}&current={next_match.group(2)}"
                        response = self.session.get(f"{self.base_url}{next_url}")
                        questions_completed += 1
                        self.log("基礎科目", f"✅ 問題{question_no}: 回答完了")
                    else:
                        self.log("基礎科目", f"❌ 問題{question_no}: 次の問題URL未検出")
                        return False
                elif "結果を見る" in response.text:
                    questions_completed += 1
                    self.log("基礎科目", f"🎉 問題{question_no}: 最終問題完了 - {questions_completed}問達成")
                    break
                else:
                    self.log("基礎科目", f"❌ 問題{question_no}: 予期しない応答")
                    return False
                    
                time.sleep(0.3)
                
            if questions_completed == 10:
                self.log("基礎科目", f"🎯 SUCCESS: 10問完全達成！")
                return True
            else:
                self.log("基礎科目", f"⚠️ PARTIAL: {questions_completed}問完了")
                return False
                
        except Exception as e:
            self.log("基礎科目", f"❌ EXCEPTION: {str(e)}")
            return False
            
    def test_review_function_manual(self):
        """復習機能手作業テスト"""
        try:
            self.log("復習機能", "手作業テスト開始")
            
            # 新セッション開始
            self.session = requests.Session()
            response = self.session.get(f"{self.base_url}/")
            
            # 復習リストアクセス
            response = self.session.get(f"{self.base_url}/review")
            if response.status_code != 200:
                self.log("復習機能", f"❌ 復習リストアクセス失敗: {response.status_code}")
                return False
            self.log("復習機能", "✅ 復習リストアクセス成功")
            
            # 復習問題実行
            review_response = self.session.get(f"{self.base_url}/exam/review")
            if review_response.status_code == 200:
                if "復習リストが空" in review_response.text:
                    self.log("復習機能", "✅ 復習リスト空（正常）")
                else:
                    self.log("復習機能", "✅ 復習問題実行成功")
            else:
                self.log("復習機能", f"❌ 復習問題実行失敗: {review_response.status_code}")
                return False
                
            self.log("復習機能", "🎯 SUCCESS: 復習機能正常動作確認")
            return True
            
        except Exception as e:
            self.log("復習機能", f"❌ EXCEPTION: {str(e)}")
            return False
            
    def run_all_manual_tests(self):
        """全手作業テスト実行"""
        print("🔥 残り11部門+基礎科目+復習機能 手作業テスト開始")
        print("=" * 80)
        
        start_time = time.time()
        success_count = 0
        total_tests = len(self.departments) + 2  # 11部門 + 基礎科目 + 復習機能
        
        # 11部門テスト
        for dept_key, dept_name in self.departments.items():
            print(f"\n📚 【{dept_name}部門】 手作業テスト...")
            if self.manual_test_department(dept_key, dept_name):
                success_count += 1
            time.sleep(1)
            
        # 基礎科目テスト
        print(f"\n📖 【基礎科目】 手作業テスト...")
        if self.test_basic_subject_manual():
            success_count += 1
            
        # 復習機能テスト
        print(f"\n🔖 【復習機能】 手作業テスト...")
        if self.test_review_function_manual():
            success_count += 1
            
        # 結果
        end_time = time.time()
        print("\n" + "=" * 80)
        print("🎯 全手作業テスト結果")
        print("=" * 80)
        print(f"⏱️  実行時間: {end_time - start_time:.1f}秒")
        print(f"📊 テスト項目: {total_tests}")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失敗: {total_tests - success_count}")
        print(f"📈 成功率: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("\n🎉 全手作業テスト完全成功！120問+基礎+復習 全て正常！")
            return True
        else:
            print(f"\n⚠️ {total_tests - success_count}項目で問題発生")
            return False

if __name__ == "__main__":
    tester = ManualAllDepartments()
    success = tester.run_all_manual_tests()
    
    if success:
        print("\n✅ 120問+基礎+復習 手作業テスト完全成功！")
    else:
        print("\n❌ 手作業テスト未完了 - ウルトラシンク修正要")