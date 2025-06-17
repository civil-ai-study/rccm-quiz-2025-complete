#!/usr/bin/env python3
"""
河川・砂防及び海岸・海洋部門の年度不一致問題調査
詳細な原因分析スクリプト
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import pandas as pd
import os

class CivilPlanningInvestigation:
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_data_files(self):
        """データファイルの存在確認"""
        self.log("=== データファイル存在確認 ===")
        
        data_dir = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data"
        years = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
        
        for year in years:
            filename = f"4-2_{year}.csv"
            filepath = os.path.join(data_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # CSVファイル読み込み
                    df = pd.read_csv(filepath, encoding='utf-8')
                    
                    # 河川関連問題の確認
                    river_questions = df[df['category'].str.contains('河川', na=False)]
                    civil_planning_questions = df[df['category'].str.contains('河川、砂防及び海岸・海洋', na=False)]
                    
                    self.log(f"{year}年度: ファイル存在, 総問題数={len(df)}, 河川問題数={len(river_questions)}, 河川・砂防・海岸問題数={len(civil_planning_questions)}")
                    
                    # カテゴリー一覧表示
                    unique_categories = df['category'].unique()
                    river_related = [cat for cat in unique_categories if '河川' in str(cat)]
                    if river_related:
                        self.log(f"  河川関連カテゴリー: {river_related}")
                    
                except Exception as e:
                    self.log(f"{year}年度: ファイル読み込みエラー - {e}")
            else:
                self.log(f"{year}年度: ファイルが存在しません - {filepath}")
    
    def test_direct_access(self, year):
        """指定年度への直接アクセステスト"""
        self.log(f"=== {year}年度 直接アクセステスト ===")
        
        # 部門選択画面から開始
        try:
            # 1. 部門選択画面
            dept_url = f"{self.base_url}/departments"
            self.log(f"1. 部門選択画面アクセス: {dept_url}")
            response = self.session.get(dept_url)
            self.log(f"   ステータス: {response.status_code}")
            
            # 2. 河川・砂防部門の専門科目選択
            categories_url = f"{self.base_url}/categories?department=civil_planning"
            self.log(f"2. 河川・砂防部門専門科目選択: {categories_url}")
            response = self.session.get(categories_url)
            self.log(f"   ステータス: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 年度リンクを探す
                year_links = soup.find_all('a', href=re.compile(f'year={year}'))
                self.log(f"   {year}年度リンク発見数: {len(year_links)}")
                for link in year_links:
                    self.log(f"   リンク: {link.get('href')}")
            
            # 3. 直接試験画面アクセス
            exam_url = f"{self.base_url}/exam?department=civil_planning&question_type=specialist&year={year}"
            self.log(f"3. 直接試験画面アクセス: {exam_url}")
            response = self.session.get(exam_url)
            self.log(f"   ステータス: {response.status_code}")
            
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', '')
                self.log(f"   リダイレクト先: {redirect_location}")
                
                # リダイレクト先にアクセス
                if redirect_location:
                    redirect_url = f"{self.base_url}{redirect_location}" if redirect_location.startswith('/') else redirect_location
                    self.log(f"4. リダイレクト先アクセス: {redirect_url}")
                    redirect_response = self.session.get(redirect_url)
                    self.log(f"   リダイレクト先ステータス: {redirect_response.status_code}")
                    
                    if redirect_response.status_code == 200:
                        soup = BeautifulSoup(redirect_response.text, 'html.parser')
                        title = soup.find('title')
                        if title:
                            self.log(f"   リダイレクト先タイトル: {title.get_text()}")
            
            elif response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 年度バッジ確認
                year_badge = None
                for text in soup.find_all(string=re.compile(f'{year}年度')):
                    year_badge = text.strip()
                    break
                
                self.log(f"   年度バッジ: {year_badge}")
                
                # 問題内容確認
                question_div = soup.find('div', class_='question-content')
                if question_div:
                    self.log(f"   問題内容発見: あり")
                else:
                    self.log(f"   問題内容発見: なし")
                
                # タイトル確認
                title = soup.find('title')
                if title:
                    self.log(f"   ページタイトル: {title.get_text()}")
        
        except Exception as e:
            self.log(f"アクセステストエラー: {e}")
    
    def check_app_logic(self):
        """アプリケーションロジック確認"""
        self.log("=== アプリケーションロジック確認 ===")
        
        # app.pyの該当部分を確認（簡易版）
        try:
            # セッション情報確認
            session_url = f"{self.base_url}/api/session-info"
            response = self.session.get(session_url)
            if response.status_code == 200:
                self.log(f"セッション情報: {response.text}")
            
            # 問題データAPI確認
            api_url = f"{self.base_url}/api/questions?department=civil_planning&year=2008"
            response = self.session.get(api_url)
            self.log(f"問題データAPI レスポンス: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                self.log(f"問題データ数: {len(data.get('questions', []))}")
            
        except Exception as e:
            self.log(f"アプリケーションロジック確認エラー: {e}")
    
    def run_comprehensive_investigation(self):
        """包括的調査実行"""
        self.log("=== 河川・砂防及び海岸・海洋部門 年度不一致問題 包括調査 ===")
        
        # 1. データファイル確認
        self.check_data_files()
        
        # 2. 各年度の直接アクセステスト
        problem_years = [2008, 2009, 2010, 2011, 2012, 2013, 2015, 2016, 2017, 2018]
        for year in problem_years:
            self.test_direct_access(year)
            print()  # 空行
        
        # 3. 正常年度との比較（2014年度）
        self.log("=== 正常年度(2014年度)との比較 ===")
        self.test_direct_access(2014)
        
        # 4. アプリケーションロジック確認
        self.check_app_logic()
        
        self.log("=== 調査完了 ===")

def main():
    """メイン関数"""
    investigator = CivilPlanningInvestigation()
    investigator.run_comprehensive_investigation()

if __name__ == "__main__":
    main()