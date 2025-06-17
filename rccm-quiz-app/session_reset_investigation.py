#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッションリセット問題の詳細調査
"""

import requests
import time
from bs4 import BeautifulSoup
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionResetInvestigation:
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def investigate_session_behavior(self):
        """セッション動作の詳細調査"""
        logger.info("=== セッション動作調査開始 ===")
        
        # Phase 1: 年度別試験開始
        logger.info("Phase 1: 2018年度道路問題を開始")
        category_encoded = urllib.parse.quote('道路')
        exam_url = f"{self.base_url}/exam?category={category_encoded}&year=2018"
        
        response = self.session.get(exam_url)
        logger.info(f"年度別試験開始: {response.status_code}")
        
        # セッション情報を確認
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            progress = soup.find(string=lambda text: text and '問題' in text and '/' in text)
            logger.info(f"現在の進捗: {progress}")
            
            # 年度情報の確認
            year_info = soup.find(string=lambda text: text and '年度' in text)
            logger.info(f"年度情報: {year_info}")
        
        # Phase 2: 通常問題に切り替え
        logger.info("\nPhase 2: 通常問題に切り替え")
        exam_url = f"{self.base_url}/exam?category={category_encoded}"
        
        response = self.session.get(exam_url)
        logger.info(f"通常試験開始: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            progress = soup.find(string=lambda text: text and '問題' in text and '/' in text)
            logger.info(f"セッション切替後の進捗: {progress}")
            
            # 年度情報の確認
            year_info = soup.find(string=lambda text: text and '年度' in text)
            logger.info(f"年度情報: {year_info}")
            
            # セッション詳細をHTMLから抽出
            self.extract_session_details(response.text)
        
        # Phase 3: セッション強制リセット試行
        logger.info("\nPhase 3: セッション強制リセット試行")
        
        # カテゴリページ経由でリセット
        cat_response = self.session.get(f"{self.base_url}/categories")
        logger.info(f"カテゴリページアクセス: {cat_response.status_code}")
        
        # 再度試験開始
        response = self.session.get(exam_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            progress = soup.find(string=lambda text: text and '問題' in text and '/' in text)
            logger.info(f"リセット試行後の進捗: {progress}")

    def extract_session_details(self, html_content):
        """HTMLからセッション詳細を抽出"""
        logger.info("\n--- セッション詳細 ---")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # JavaScriptの変数を検索
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('session' in script.string.lower() or 'exam' in script.string.lower()):
                logger.info(f"関連スクリプト: {script.string[:200]}...")
        
        # フォーム情報を確認
        forms = soup.find_all('form')
        for form in forms:
            logger.info(f"フォーム action: {form.get('action')}")
            inputs = form.find_all('input')
            for inp in inputs:
                if inp.get('name') in ['csrf_token', 'category', 'year', 'exam_type']:
                    logger.info(f"  {inp.get('name')}: {inp.get('value')}")

    def test_session_isolation(self):
        """セッション隔離テスト"""
        logger.info("\n=== セッション隔離テスト ===")
        
        # セッション1: 道路
        session1 = requests.Session()
        session1.headers.update({'User-Agent': 'TestSession1'})
        
        # セッション2: トンネル
        session2 = requests.Session()
        session2.headers.update({'User-Agent': 'TestSession2'})
        
        # 同時に異なる部門を開始
        category1 = urllib.parse.quote('道路')
        category2 = urllib.parse.quote('トンネル')
        
        exam_url1 = f"{self.base_url}/exam?category={category1}&year=2018"
        exam_url2 = f"{self.base_url}/exam?category={category2}&year=2015"
        
        response1 = session1.get(exam_url1)
        response2 = session2.get(exam_url2)
        
        logger.info(f"セッション1（道路2018年）: {response1.status_code}")
        logger.info(f"セッション2（トンネル2015年）: {response2.status_code}")
        
        # 進捗確認
        if response1.status_code == 200:
            soup1 = BeautifulSoup(response1.text, 'html.parser')
            progress1 = soup1.find(string=lambda text: text and '問題' in text and '/' in text)
            logger.info(f"セッション1進捗: {progress1}")
        
        if response2.status_code == 200:
            soup2 = BeautifulSoup(response2.text, 'html.parser')
            progress2 = soup2.find(string=lambda text: text and '問題' in text and '/' in text)
            logger.info(f"セッション2進捗: {progress2}")

def main():
    investigator = SessionResetInvestigation()
    investigator.investigate_session_behavior()
    investigator.test_session_isolation()

if __name__ == "__main__":
    main()