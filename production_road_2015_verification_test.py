#!/usr/bin/env python3
"""
道路部門2015年本番環境厳重検証テスト
ULTRA SYNC修正後の年度・カテゴリー混在完全チェック
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

class ProductionRoad2015Test:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.question_details = []
        self.contamination_issues = []
        
    def test_road_2015_access(self):
        """道路部門2015年アクセステスト"""
        print("道路部門2015年アクセステスト開始...")
        try:
            # 道路部門ページアクセス
            url = f"{self.base_url}/quiz_department/道路"
            response = self.session.get(url, timeout=45)
            
            if response.status_code == 200:
                print("道路部門ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 2015年選択オプションの確認
                if "2015" in response.text:
                    print("2015年選択オプション確認")
                    return True
                else:
                    print("2015年選択オプションが見つからない")
                    return False
            else:
                print(f"道路部門アクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"道路部門アクセスエラー: {e}")
            return False
    
    def test_road_2015_quiz_start(self):
        """道路部門2015年クイズ開始テスト"""
        print("道路部門2015年クイズ開始テスト...")
        try:
            # 2015年指定でクイズ開始
            url = f"{self.base_url}/start_exam/道路"
            data = {
                "questions": 10,
                "year": "2015"  # 2015年を明示指定
            }
            
            response = self.session.post(url, data=data, timeout=45)
            
            if response.status_code == 200:
                print("道路部門2015年クイズ開始成功")
                
                # エラーメッセージでないことを確認
                if "利用できません" in response.text or "無効な年度" in response.text:
                    print("予期しないエラーメッセージが表示されました")
                    with open("road_2015_unexpected_error.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
                
                # 問題表示の確認
                if "問題" in response.text:
                    print("問題表示確認")
                    return True
                else:
                    print("問題が正しく表示されていない")
                    with open("road_2015_quiz_start_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"クイズ開始失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"クイズ開始エラー: {e}")
            return False
    
    def extract_question_analysis(self, html_content, question_no):
        """問題内容の詳細分析"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            question_text = soup.get_text()
            
            analysis = {
                "question_number": question_no,
                "question_text_length": len(question_text),
                "years_found": [],
                "road_keywords": [],
                "other_category_keywords": [],
                "contamination_detected": False
            }
            
            # 年度検索（2015年以外の年度が含まれているか）
            year_pattern = r'(19|20)\d{2}年?'
            years = re.findall(year_pattern, question_text)
            if years:
                unique_years = list(set([y + "年" for y in years]))
                analysis["years_found"] = unique_years
                
                # 2015年以外の年度が含まれているかチェック
                non_2015_years = [y for y in unique_years if "2015" not in y]
                if non_2015_years:
                    analysis["contamination_detected"] = True
                    print(f"    年度混在検出: {non_2015_years}")
            
            # 道路関連キーワード
            road_keywords = [
                "道路", "舗装", "アスファルト", "コンクリート舗装", "交通", "車道", "歩道",
                "橋梁", "トンネル", "交差点", "信号", "標識", "車線", "路面", "排水"
            ]
            
            # 他分野キーワード
            other_keywords = {
                "河川・砂防": ["河川", "砂防", "ダム", "堤防", "治水", "洪水", "流量", "土石流"],
                "都市計画": ["都市計画", "区域区分", "用途地域", "開発許可", "市街化"],
                "造園": ["造園", "公園", "緑地", "植栽", "庭園", "樹木"],
                "建設環境": ["環境影響評価", "騒音", "振動", "大気汚染", "環境基準"],
                "鋼構造": ["鋼構造", "鉄骨", "溶接", "ボルト", "鋼材"],
                "土質": ["土質", "地盤", "基礎", "杭", "支持力", "地耐力"],
                "施工計画": ["工程管理", "品質管理", "安全管理", "施工計画"],
                "上下水道": ["上水道", "下水道", "浄水", "配水", "管路"],
                "森林土木": ["森林", "林道", "治山", "山地", "森林整備"],
                "農業土木": ["農業", "農地", "灌漑", "排水", "農道"]
            }
            
            # キーワードマッチング
            for keyword in road_keywords:
                if keyword in question_text:
                    analysis["road_keywords"].append(keyword)
            
            for category, keywords in other_keywords.items():
                for keyword in keywords:
                    if keyword in question_text:
                        analysis["other_category_keywords"].append(f"{category}:{keyword}")
                        analysis["contamination_detected"] = True
                        print(f"    他分野キーワード検出: {category}:{keyword}")
            
            return analysis
            
        except Exception as e:
            print(f"問題分析エラー: {e}")
            return {"error": str(e), "question_number": question_no}
    
    def test_road_2015_detailed_flow(self):
        """道路部門2015年詳細問題フロー検証"""
        print("道路部門2015年詳細問題フロー検証開始...")
        
        contamination_count = 0
        
        try:
            # 1. クイズ開始
            start_url = f"{self.base_url}/start_exam/道路"
            start_data = {"questions": 10, "year": "2015"}
            
            start_response = self.session.post(start_url, data=start_data, timeout=45)
            
            if start_response.status_code != 200:
                print(f"クイズ開始失敗: {start_response.status_code}")
                return False
            
            print("クイズ開始成功")
            
            # 2. 各問題の詳細チェック
            for question_no in range(1, 11):
                print(f"第{question_no}問 詳細分析中...")
                
                # 現在の問題ページを分析
                if question_no == 1:
                    current_html = start_response.text
                else:
                    # 現在のページを取得
                    try:
                        quiz_response = self.session.get(f"{self.base_url}/quiz", timeout=30)
                        current_html = quiz_response.text
                    except:
                        current_html = ""
                
                # 問題分析実行
                if current_html:
                    analysis = self.extract_question_analysis(current_html, question_no)
                    self.question_details.append(analysis)
                    
                    if analysis.get("contamination_detected"):
                        contamination_count += 1
                        self.contamination_issues.append(analysis)
                    
                    # 問題ページ保存
                    with open(f"road_2015_question_{question_no}.html", "w", encoding="utf-8") as f:
                        f.write(current_html)
                
                # 回答送信（最後の問題以外）
                if question_no < 10:
                    answer_url = f"{self.base_url}/quiz"
                    answer_data = {
                        "answer": "1",
                        "current": question_no
                    }
                    
                    answer_response = self.session.post(answer_url, data=answer_data, timeout=45)
                    
                    if answer_response.status_code == 200:
                        print(f"  第{question_no}問 回答成功")
                        time.sleep(3)  # 詳細分析のため長めの待機
                    else:
                        print(f"  第{question_no}問 回答失敗: {answer_response.status_code}")
                        return False
                else:
                    # 最後の問題
                    final_answer_data = {
                        "answer": "1",
                        "current": question_no
                    }
                    final_response = self.session.post(f"{self.base_url}/quiz", data=final_answer_data, timeout=45)
                    
                    if final_response.status_code == 200:
                        print(f"  第{question_no}問 最終回答成功")
                        
                        # 結果画面保存
                        with open("road_2015_final_results.html", "w", encoding="utf-8") as f:
                            f.write(final_response.text)
                        print("  結果画面保存完了")
                        
                        # 結果画面チェック
                        if "結果" in final_response.text or "スコア" in final_response.text:
                            print("  結果画面正常表示確認")
                            return True
                        else:
                            print("  結果画面表示異常")
                            return False
            
            return True
            
        except Exception as e:
            print(f"詳細フロー検証エラー: {e}")
            return False
    
    def generate_road_2015_analysis_report(self):
        """道路部門2015年分析レポート生成"""
        print("道路部門2015年分析レポート生成中...")
        
        report = {
            "test_time": datetime.now().isoformat(),
            "department": "道路",
            "year": "2015",
            "total_questions_analyzed": len(self.question_details),
            "contamination_issues": self.contamination_issues,
            "question_details": self.question_details,
            "summary": {
                "contaminated_questions": len(self.contamination_issues),
                "clean_questions": len(self.question_details) - len(self.contamination_issues),
                "contamination_rate": (len(self.contamination_issues) / len(self.question_details) * 100) if self.question_details else 0
            }
        }
        
        # レポート保存
        with open("road_2015_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def run_comprehensive_road_2015_test(self):
        """道路部門2015年包括的テスト実行"""
        print("道路部門2015年包括的検証テスト開始")
        print(f"テスト開始時刻: {datetime.now()}")
        print("=" * 60)
        
        results = {
            "test_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. 道路部門アクセステスト
        results["tests"]["road_access"] = self.test_road_2015_access()
        
        # 2. 2015年クイズ開始テスト
        results["tests"]["quiz_start_2015"] = self.test_road_2015_quiz_start()
        
        # 3. 詳細問題フロー検証
        results["tests"]["detailed_flow"] = self.test_road_2015_detailed_flow()
        
        # 4. 分析レポート生成
        analysis_report = self.generate_road_2015_analysis_report()
        
        # 結果サマリー
        print("=" * 60)
        print("道路部門2015年検証結果サマリー")
        
        passed = sum(1 for test in results["tests"].values() if test)
        total = len(results["tests"])
        
        for test_name, result in results["tests"].items():
            status = "成功" if result else "失敗"
            print(f"{test_name}: {status}")
        
        print(f"\n基本テスト合格率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # 汚染分析結果
        print("\n汚染分析結果:")
        print(f"総問題数: {analysis_report['total_questions_analyzed']}")
        print(f"汚染問題数: {analysis_report['summary']['contaminated_questions']}")
        print(f"クリーン問題数: {analysis_report['summary']['clean_questions']}")
        print(f"汚染率: {analysis_report['summary']['contamination_rate']:.1f}%")
        
        if analysis_report['contamination_issues']:
            print("\n汚染問題詳細:")
            for issue in analysis_report['contamination_issues']:
                print(f"  第{issue['question_number']}問:")
                if issue.get('years_found'):
                    print(f"    年度混在: {issue['years_found']}")
                if issue.get('other_category_keywords'):
                    print(f"    他分野キーワード: {issue['other_category_keywords']}")
        
        # 最終判定
        if analysis_report['summary']['contamination_rate'] == 0:
            print("\n✅ 全問題がクリーン!道路部門2015年問題セット正常")
        elif analysis_report['summary']['contamination_rate'] < 20:
            print(f"\n⚠️ 軽微な汚染検出({analysis_report['summary']['contamination_rate']:.1f}%)")
        else:
            print(f"\n❌ 重大な汚染検出({analysis_report['summary']['contamination_rate']:.1f}%)")
        
        # 最終結果保存
        results["analysis"] = analysis_report
        with open("road_2015_comprehensive_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results

if __name__ == "__main__":
    tester = ProductionRoad2015Test()
    tester.run_comprehensive_road_2015_test()