#!/usr/bin/env python3
"""
RCCM試験問題集アプリケーション - 年度選択と表示年度の不一致問題調査
"""

import requests
import json
from bs4 import BeautifulSoup
import sys
import re
from urllib.parse import urljoin, parse_qs, urlparse

class YearMismatchInvestigator:
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def check_server_status(self):
        """サーバーの状態を確認"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            print(f"✅ サーバー接続成功: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ サーバー接続失敗: {e}")
            return False
            
    def navigate_to_department_selection(self):
        """部門選択ページへ遷移"""
        try:
            response = self.session.get(f"{self.base_url}/departments", timeout=10)
            print(f"✅ 部門選択ページ取得成功: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ 部門選択ページ取得失敗: {e}")
            return None
            
    def navigate_to_question_types(self, department_id="road"):
        """問題種別選択ページへ遷移"""
        try:
            url = f"{self.base_url}/question_types/{department_id}"
            response = self.session.get(url, timeout=10)
            print(f"✅ 問題種別選択ページ取得成功: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ 問題種別選択ページ取得失敗: {e}")
            return None
            
    def navigate_to_department_categories(self, department_id="road", question_type="specialist"):
        """部門カテゴリ選択ページへ遷移"""
        try:
            url = f"{self.base_url}/department_categories/{department_id}/{question_type}"
            response = self.session.get(url, timeout=10)
            print(f"✅ 部門カテゴリ選択ページ取得成功: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ 部門カテゴリ選択ページ取得失敗: {e}")
            return None
            
    def test_year_selection(self, department_id="road", question_type="specialist", year=2017):
        """年度選択テスト"""
        print(f"\n=== 年度選択テスト: {department_id}部門 {question_type} {year}年度 ===")
        
        # 年度選択URL生成
        url = f"{self.base_url}/exam?department={department_id}&question_type={question_type}&year={year}"
        
        print(f"📌 生成されたURL: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"✅ 年度選択リクエスト成功: {response.status_code}")
            
            if response.status_code == 200:
                return self.analyze_exam_page(response, year)
            else:
                print(f"❌ 予期しないステータスコード: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 年度選択リクエスト失敗: {e}")
            return None
            
    def analyze_exam_page(self, response, expected_year):
        """試験ページの年度表示を分析"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 年度バッジを探す
        year_badge = soup.find('span', class_='year-badge')
        displayed_year = None
        
        if year_badge:
            year_text = year_badge.get_text(strip=True)
            # 年度を抽出（📅 2017年度過去問 -> 2017）
            year_match = re.search(r'(\d{4})', year_text)
            if year_match:
                displayed_year = int(year_match.group(1))
                print(f"📅 表示年度: {displayed_year}年度")
            else:
                print(f"❌ 年度抽出失敗: {year_text}")
        else:
            print("❌ 年度バッジが見つかりません")
            
        # 問題データの年度フィールドをチェック
        question_data = self.extract_question_data(soup)
        
        # 結果分析
        result = {
            'expected_year': expected_year,
            'displayed_year': displayed_year,
            'question_year': question_data.get('year') if question_data else None,
            'match_display': displayed_year == expected_year if displayed_year else False,
            'match_data': question_data.get('year') == expected_year if question_data and question_data.get('year') else False,
            'question_id': question_data.get('id') if question_data else None,
            'question_text': question_data.get('question', '')[:100] + '...' if question_data and question_data.get('question') else None
        }
        
        print(f"📊 分析結果:")
        print(f"   期待年度: {expected_year}")
        print(f"   表示年度: {displayed_year} {'✅' if result['match_display'] else '❌'}")
        print(f"   問題年度: {question_data.get('year') if question_data else 'N/A'} {'✅' if result['match_data'] else '❌'}")
        print(f"   問題ID: {question_data.get('id') if question_data else 'N/A'}")
        
        return result
        
    def extract_question_data(self, soup):
        """問題データを抽出"""
        try:
            # 問題IDを探す
            qid_input = soup.find('input', {'name': 'qid'})
            if qid_input:
                question_id = qid_input.get('value')
                print(f"🔍 問題ID: {question_id}")
                
                # 問題テキストを探す
                question_content = soup.find('div', id='question-content')
                question_text = question_content.get_text(strip=True) if question_content else None
                
                return {
                    'id': question_id,
                    'question': question_text,
                    'year': None  # 年度は別途CSVから取得する必要がある
                }
            else:
                print("❌ 問題IDが見つかりません")
                return None
                
        except Exception as e:
            print(f"❌ 問題データ抽出エラー: {e}")
            return None
            
    def run_comprehensive_test(self):
        """包括的なテストを実行"""
        print("🔍 RCCM試験問題集アプリケーション - 年度選択と表示年度の不一致問題調査")
        print("=" * 80)
        
        # サーバー状態確認
        if not self.check_server_status():
            print("❌ サーバーに接続できません。アプリケーションが起動していることを確認してください。")
            return
            
        # テスト結果格納
        test_results = []
        
        # 1. 道路部門で2017年を選択
        print("\n📋 テスト1: 道路部門で2017年を選択")
        result = self.test_year_selection("road", "specialist", 2017)
        if result:
            test_results.append(result)
            
        # 2. 複数年度での検証
        years_to_test = [2018, 2017, 2016, 2015]
        for year in years_to_test:
            print(f"\n📋 テスト2: 道路部門で{year}年を選択")
            result = self.test_year_selection("road", "specialist", year)
            if result:
                test_results.append(result)
                
        # 3. 他部門での検証
        other_departments = ["tunnel", "river"]
        for dept in other_departments:
            print(f"\n📋 テスト3: {dept}部門で2017年を選択")
            result = self.test_year_selection(dept, "specialist", 2017)
            if result:
                test_results.append(result)
                
        # 結果サマリー
        self.print_test_summary(test_results)
        
    def print_test_summary(self, results):
        """テスト結果のサマリーを出力"""
        print("\n" + "=" * 80)
        print("📊 テスト結果サマリー")
        print("=" * 80)
        
        total_tests = len(results)
        display_match_count = sum(1 for r in results if r['match_display'])
        data_match_count = sum(1 for r in results if r['match_data'])
        
        print(f"総テスト数: {total_tests}")
        print(f"表示年度一致: {display_match_count}/{total_tests} ({display_match_count/total_tests*100:.1f}%)")
        print(f"問題年度一致: {data_match_count}/{total_tests} ({data_match_count/total_tests*100:.1f}%)")
        
        print("\n詳細結果:")
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. 期待:{result['expected_year']} 表示:{result['displayed_year']} 問題:{result['question_year']} "
                  f"ID:{result['question_id']} "
                  f"{'✅' if result['match_display'] and result['match_data'] else '❌'}")
                  
        # 問題の特定
        if display_match_count < total_tests or data_match_count < total_tests:
            print("\n🔍 問題の特定:")
            if display_match_count < total_tests:
                print("❌ 表示年度の不一致が発生しています")
            if data_match_count < total_tests:
                print("❌ 問題データの年度不一致が発生しています")
                
            print("\n🔧 推奨される調査項目:")
            print("1. app.py の exam() 関数での年度パラメータ処理")
            print("2. get_mixed_questions() 関数での年度フィルタリング")
            print("3. CSVデータの年度フィールドの整合性")
            print("4. セッション管理での year パラメータの保存/復元")
        else:
            print("\n✅ すべてのテストが成功しました")

def main():
    """メイン関数"""
    investigator = YearMismatchInvestigator()
    investigator.run_comprehensive_test()

if __name__ == "__main__":
    main()