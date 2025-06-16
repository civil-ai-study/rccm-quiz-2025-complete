#!/usr/bin/env python3
"""
🔥 CRITICAL: 実際の12部門×10問=120問完全解答テスト
ユーザー要求による徹底的な動作確認（ウルトラシンク）
"""

import requests
import time
import json
import re
from datetime import datetime

class Real10QuestionsTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.departments = {
            'road': '道路',
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
        self.test_results = {}
        
    def log(self, dept_name, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🎯 {dept_name}: {message}")
        
    def extract_progress(self, html):
        """進捗情報を抽出 (例: 3/10)"""
        progress_match = re.search(r'(\d+)/10', html)
        return progress_match.group(1) if progress_match else "?"
        
    def extract_question_id(self, html):
        """問題IDを抽出"""
        qid_match = re.search(r'name="qid" value="(\d+)"', html)
        return qid_match.group(1) if qid_match else None
        
    def test_department_10_questions(self, dept_key, dept_name):
        """1部門で実際に10問すべてを解答"""
        try:
            self.log(dept_name, "10問完全解答テスト開始")
            
            # 1. 部門専門科目開始
            response = self.session.get(f"{self.base_url}/exam?department={dept_key}&type=specialist")
            
            if response.status_code != 200:
                self.log(dept_name, f"❌ 専門科目開始失敗: Status {response.status_code}")
                return False
                
            questions_completed = 0
            
            # 2. 10問連続解答
            for question_no in range(1, 11):  # 1〜10問
                # 現在の進捗確認
                current_progress = self.extract_progress(response.text)
                qid = self.extract_question_id(response.text)
                
                self.log(dept_name, f"問題{question_no}: 進捗{current_progress}/10, QID:{qid}")
                
                if qid is None:
                    self.log(dept_name, f"❌ 問題{question_no}: 問題IDが見つからない")
                    break
                    
                # 回答データ準備
                answer_data = {
                    'answer': 'A',  # 常にAを選択（テスト目的）
                    'qid': qid,
                    'elapsed': 2
                }
                
                # 回答送信
                response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                
                if response.status_code != 200:
                    self.log(dept_name, f"❌ 問題{question_no}: 回答失敗 Status {response.status_code}")
                    break
                    
                # 結果解析
                if "次の問題" in response.text:
                    # 次の問題があることを確認
                    next_match = re.search(r'href="/exam\?next=(\d+)&current=(\d+)"', response.text)
                    if next_match:
                        next_url = f"/exam?next={next_match.group(1)}&current={next_match.group(2)}"
                        self.log(dept_name, f"✅ 問題{question_no}: 回答完了 → 次へ進行")
                        
                        # 次の問題へ
                        response = self.session.get(f"{self.base_url}{next_url}")
                        questions_completed += 1
                    else:
                        self.log(dept_name, f"❌ 問題{question_no}: 次の問題URLが見つからない")
                        break
                        
                elif "結果を見る" in response.text or "解答結果分析" in response.text:
                    # 10問目完了
                    questions_completed += 1
                    self.log(dept_name, f"🎉 問題{question_no}: 最終問題完了 - 10問達成！")
                    break
                else:
                    self.log(dept_name, f"❌ 問題{question_no}: 予期しない応答")
                    break
                    
                time.sleep(0.2)  # サーバー負荷軽減
                
            # 結果判定
            if questions_completed == 10:
                self.log(dept_name, f"🎯 SUCCESS: 10問完全達成！")
                self.test_results[dept_key] = {"status": "SUCCESS", "completed": 10}
                return True
            else:
                self.log(dept_name, f"⚠️ PARTIAL: {questions_completed}問で停止")
                self.test_results[dept_key] = {"status": "PARTIAL", "completed": questions_completed}
                return False
                
        except Exception as e:
            self.log(dept_name, f"❌ EXCEPTION: {str(e)}")
            self.test_results[dept_key] = {"status": "ERROR", "error": str(e)}
            return False
            
    def run_all_departments_test(self):
        """12部門すべてで10問ずつテスト"""
        print("🚀 12部門×10問=120問 完全解答テスト開始")
        print("=" * 80)
        
        start_time = time.time()
        successful_departments = 0
        total_questions_completed = 0
        
        for dept_key, dept_name in self.departments.items():
            print(f"\n📚 【{dept_name}部門】 開始...")
            
            if self.test_department_10_questions(dept_key, dept_name):
                successful_departments += 1
                total_questions_completed += 10
            else:
                completed = self.test_results.get(dept_key, {}).get('completed', 0)
                total_questions_completed += completed
                
            # 部門間の短い休憩
            time.sleep(1)
            
        # 最終結果
        end_time = time.time()
        print("\n" + "=" * 80)
        print("🎯 12部門×10問テスト 最終結果")
        print("=" * 80)
        print(f"⏱️  実行時間: {end_time - start_time:.1f}秒")
        print(f"📊 成功部門: {successful_departments}/12")
        print(f"📝 完了問題数: {total_questions_completed}/120")
        print(f"📈 成功率: {(successful_departments/12)*100:.1f}%")
        
        # 部門別詳細
        print("\n📋 部門別結果:")
        for dept_key, dept_name in self.departments.items():
            result = self.test_results.get(dept_key, {"status": "NOT_TESTED"})
            status = result['status']
            if status == "SUCCESS":
                print(f"  ✅ {dept_name}: 10問完全達成")
            elif status == "PARTIAL":
                completed = result.get('completed', 0)
                print(f"  ⚠️ {dept_name}: {completed}問で停止")
            elif status == "ERROR":
                print(f"  ❌ {dept_name}: エラー - {result.get('error', '')}")
            else:
                print(f"  ⚪ {dept_name}: 未テスト")
                
        if successful_departments == 12 and total_questions_completed == 120:
            print("\n🎉 完全成功！すべての部門で10問ずつ解答完了！")
            return True
        else:
            print(f"\n⚠️ 不完全な結果: {total_questions_completed}/120問完了")
            return False

if __name__ == "__main__":
    print("🔧 サーバー動作確認中...")
    time.sleep(1)
    
    tester = Real10QuestionsTest()
    success = tester.run_all_departments_test()
    
    if success:
        print("\n✅ 12部門×10問=120問テスト完全成功！")
    else:
        print("\n❌ テスト未完了 - 修正が必要")