#!/usr/bin/env python3
"""
河川・砂防部門2020年年度別問題詳細検証テスト
年度混在・カテゴリー混在の厳重チェック
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

class ProductionRiver2020Test:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.question_details = []
        self.category_issues = []
        self.year_issues = []
        
    def test_river_2020_selection(self):
        """河川・砂防2020年選択テスト"""
        print("河川・砂防部門2020年選択テスト開始...")
        try:
            # 河川・砂防部門ページアクセス
            url = f"{self.base_url}/quiz_department/河川・砂防"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                print("河川・砂防部門ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 2020年選択オプションの確認
                if "2020" in response.text:
                    print("2020年選択オプション確認")
                    return True
                else:
                    print("2020年選択オプションが見つからない")
                    with open("river_department_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"河川・砂防部門アクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"河川・砂防選択エラー: {e}")
            return False
    
    def test_river_2020_quiz_start(self):
        """河川・砂防2020年クイズ開始テスト"""
        print("河川・砂防2020年クイズ開始テスト...")
        try:
            # 2020年指定でクイズ開始
            url = f"{self.base_url}/start_exam/河川・砂防"
            data = {
                "questions": 10,
                "year": "2020"  # 2020年を明示指定
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                print("河川・砂防2020年クイズ開始成功")
                
                # 問題表示の確認
                if "問題" in response.text:
                    print("問題表示確認")
                    return True
                else:
                    print("問題が正しく表示されていない")
                    with open("river_2020_quiz_start_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"クイズ開始失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"クイズ開始エラー: {e}")
            return False
    
    def extract_question_details(self, html_content):
        """問題詳細の抽出と解析"""
        try:
            # HTMLパースして問題内容を抽出
            soup = BeautifulSoup(html_content, 'html.parser')
            
            details = {
                "question_text": "",
                "year_found": [],
                "category_keywords": [],
                "river_keywords": [],
                "other_category_keywords": []
            }
            
            # 問題文の抽出
            question_text = soup.get_text()
            details["question_text"] = question_text
            
            # 年度チェック（2020年以外の年度が含まれているか）
            year_pattern = r'(19|20)\d{2}年?'
            years = re.findall(year_pattern, question_text)
            details["year_found"] = [y + "年" for y in years if y]
            
            # 河川・砂防関連キーワード
            river_keywords = [
                "河川", "砂防", "ダム", "堤防", "治水", "洪水", "水位", "流量", 
                "河道", "護岸", "堰", "水門", "排水", "流域", "氾濫", "土石流",
                "砂防ダム", "治山", "渓流", "土砂災害"
            ]
            
            # 他カテゴリーのキーワード
            other_keywords = {
                "道路": ["道路", "舗装", "アスファルト", "交通", "車道", "歩道"],
                "都市計画": ["都市計画", "区域区分", "用途地域", "開発許可"],
                "造園": ["造園", "公園", "緑地", "植栽", "庭園"],
                "建設環境": ["環境影響評価", "騒音", "振動", "大気汚染"],
                "鋼構造": ["鋼構造", "鉄骨", "溶接", "ボルト"],
                "コンクリート": ["コンクリート", "セメント", "骨材", "配合"],
                "土質": ["土質", "地盤", "基礎", "杭", "支持力"],
                "施工計画": ["工程", "施工計画", "品質管理", "安全管理"],
                "上下水道": ["上水道", "下水道", "浄水", "配水", "管路"],
                "森林土木": ["森林", "林道", "治山", "山地"],
                "農業土木": ["農業", "農地", "灌漑", "排水", "農道"],
                "トンネル": ["トンネル", "掘削", "覆工", "地山"]
            }
            
            # キーワードマッチング
            for keyword in river_keywords:
                if keyword in question_text:
                    details["river_keywords"].append(keyword)
            
            for category, keywords in other_keywords.items():
                for keyword in keywords:
                    if keyword in question_text:
                        details["other_category_keywords"].append(f"{category}:{keyword}")
            
            return details
            
        except Exception as e:
            print(f"問題詳細抽出エラー: {e}")
            return None
    
    def test_detailed_question_flow(self):
        """詳細問題フロー検証（各問題の内容チェック）"""
        print("河川・砂防2020年詳細問題フロー検証開始...")
        try:
            # 1. クイズ開始
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 10, "year": "2020"}
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            
            if start_response.status_code != 200:
                print(f"クイズ開始失敗: {start_response.status_code}")
                return False
            
            print("クイズ開始成功")
            
            # 2. 各問題の詳細チェック
            for question_no in range(1, 11):
                print(f"第{question_no}問 詳細チェック中...")
                
                # 現在の問題ページを保存
                question_file = f"river_2020_question_{question_no}.html"
                with open(question_file, "w", encoding="utf-8") as f:
                    if question_no == 1:
                        f.write(start_response.text)  # 最初の問題
                    else:
                        # 前の問題の回答後のページを使用
                        pass
                
                # 問題詳細の抽出
                if question_no == 1:
                    details = self.extract_question_details(start_response.text)
                else:
                    # 現在のレスポンスから詳細抽出
                    try:
                        current_response = self.session.get(f"{self.base_url}/quiz", timeout=30)
                        details = self.extract_question_details(current_response.text)
                    except:
                        details = {"error": "詳細取得失敗"}
                
                if details:
                    details["question_number"] = question_no
                    self.question_details.append(details)
                    
                    # 年度チェック
                    if details.get("year_found"):
                        non_2020_years = [y for y in details["year_found"] if "2020" not in y]
                        if non_2020_years:
                            self.year_issues.append({
                                "question": question_no,
                                "found_years": non_2020_years,
                                "expected": "2020年のみ"
                            })
                            print(f"  年度混在検出: {non_2020_years}")
                    
                    # カテゴリーチェック
                    if details.get("other_category_keywords"):
                        self.category_issues.append({
                            "question": question_no,
                            "other_keywords": details["other_category_keywords"],
                            "river_keywords": details.get("river_keywords", [])
                        })
                        print(f"  他カテゴリーキーワード検出: {details['other_category_keywords']}")
                    
                    if details.get("river_keywords"):
                        print(f"  河川・砂防キーワード: {details['river_keywords'][:3]}...")
                
                # 回答送信（最後の問題以外）
                if question_no < 10:
                    answer_url = f"{self.base_url}/quiz"
                    answer_data = {
                        "answer": "1",
                        "current": question_no
                    }
                    
                    answer_response = self.session.post(answer_url, data=answer_data, timeout=30)
                    
                    if answer_response.status_code == 200:
                        print(f"  第{question_no}問 回答成功")
                        time.sleep(2)  # 詳細確認のため待機時間延長
                    else:
                        print(f"  第{question_no}問 回答失敗: {answer_response.status_code}")
                        return False
                else:
                    # 最後の問題
                    final_answer_data = {
                        "answer": "1",
                        "current": question_no
                    }
                    final_response = self.session.post(f"{self.base_url}/quiz", data=final_answer_data, timeout=30)
                    
                    if final_response.status_code == 200:
                        print(f"  第{question_no}問 最終回答成功")
                        
                        # 結果画面保存
                        with open("river_2020_final_results.html", "w", encoding="utf-8") as f:
                            f.write(final_response.text)
                        print("  結果画面保存完了")
                        
                        return True
            
            return True
            
        except Exception as e:
            print(f"詳細問題フロー検証エラー: {e}")
            return False
    
    def generate_analysis_report(self):
        """分析レポート生成"""
        print("分析レポート生成中...")
        
        report = {
            "test_time": datetime.now().isoformat(),
            "department": "河川・砂防",
            "year": "2020",
            "total_questions": len(self.question_details),
            "year_issues": self.year_issues,
            "category_issues": self.category_issues,
            "question_details": self.question_details,
            "summary": {
                "year_contamination_count": len(self.year_issues),
                "category_contamination_count": len(self.category_issues),
                "clean_questions": len(self.question_details) - len(self.year_issues) - len(self.category_issues)
            }
        }
        
        # レポート保存
        with open("river_2020_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("河川・砂防2020年詳細検証テスト開始")
        print(f"テスト開始時刻: {datetime.now()}")
        print("=" * 60)
        
        results = {
            "test_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. 河川・砂防選択テスト
        results["tests"]["river_selection"] = self.test_river_2020_selection()
        
        # 2. 2020年クイズ開始テスト
        results["tests"]["quiz_start_2020"] = self.test_river_2020_quiz_start()
        
        # 3. 詳細問題フロー検証
        results["tests"]["detailed_flow"] = self.test_detailed_question_flow()
        
        # 4. 分析レポート生成
        analysis_report = self.generate_analysis_report()
        
        # 結果サマリー
        print("=" * 60)
        print("河川・砂防2020年検証結果サマリー")
        
        passed = sum(1 for test in results["tests"].values() if test)
        total = len(results["tests"])
        
        for test_name, result in results["tests"].items():
            status = "成功" if result else "失敗"
            print(f"{test_name}: {status}")
        
        print(f"\n基本テスト合格率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # 詳細分析結果
        print("\n詳細分析結果:")
        print(f"総問題数: {analysis_report['total_questions']}")
        print(f"年度混在問題: {analysis_report['summary']['year_contamination_count']}問")
        print(f"カテゴリー混在問題: {analysis_report['summary']['category_contamination_count']}問")
        print(f"クリーンな問題: {analysis_report['summary']['clean_questions']}問")
        
        if analysis_report['year_issues']:
            print("\n年度混在詳細:")
            for issue in analysis_report['year_issues']:
                print(f"  第{issue['question']}問: {issue['found_years']}")
        
        if analysis_report['category_issues']:
            print("\nカテゴリー混在詳細:")
            for issue in analysis_report['category_issues']:
                print(f"  第{issue['question']}問: {issue['other_keywords']}")
        
        # 最終判定
        if analysis_report['summary']['year_contamination_count'] == 0 and analysis_report['summary']['category_contamination_count'] == 0:
            print("\n全問題がクリーン!河川・砂防2020年問題セット正常")
        else:
            print("\n問題混在が検出されました")
        
        # 結果保存
        results["analysis"] = analysis_report
        with open("river_2020_comprehensive_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results

if __name__ == "__main__":
    tester = ProductionRiver2020Test()
    tester.run_comprehensive_test()