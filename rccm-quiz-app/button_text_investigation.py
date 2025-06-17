#!/usr/bin/env python3
"""
ボタンテキスト調査: 「次の問題へ」ボタンの正確なテキストを調査
"""

import requests
import json
import time
import logging
from bs4 import BeautifulSoup
import re

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = 'http://localhost:5003'

class ButtonTextInvestigation:
    def __init__(self):
        self.session = requests.Session()
        
    def investigate_result_page_buttons(self):
        """解答結果ページのボタンを調査"""
        logger.info("=== 解答結果ページのボタン調査 ===")
        
        try:
            # セッション開始
            response = self.session.get(f'{BASE_URL}/exam?department=road&type=specialist')
            
            # 1問目に回答
            soup = BeautifulSoup(response.text, 'html.parser')
            choices = soup.find_all('input', {'name': 'answer'})
            form = soup.find('form')
            
            form_data = {'answer': choices[0]['value']}
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value')
                if name and value:
                    form_data[name] = value
            
            action_url = form.get('action', '/exam')
            response = self.session.post(f'{BASE_URL}{action_url}', data=form_data)
            
            # 解答結果ページを解析
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').get_text()
            logger.info(f"結果ページタイトル: {title}")
            
            # すべてのボタンとリンクを探す
            logger.info("すべてのボタン:")
            buttons = soup.find_all('button')
            for i, button in enumerate(buttons):
                text = button.get_text(strip=True)
                if text:
                    logger.info(f"  ボタン {i+1}: '{text}'")
            
            logger.info("すべてのリンク:")
            links = soup.find_all('a')
            for i, link in enumerate(links):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if text and href:
                    logger.info(f"  リンク {i+1}: '{text}' -> {href}")
            
            # 「次」「問題」「続行」などのキーワードを含む要素を探す
            logger.info("次の問題関連要素:")
            next_elements = soup.find_all(['a', 'button'], string=re.compile(r'次|問題|続行|Continue|Next', re.I))
            for element in next_elements:
                text = element.get_text(strip=True)
                href = element.get('href', '')
                tag = element.name
                logger.info(f"  {tag}: '{text}' -> {href}")
            
            # クラス名での検索
            logger.info("next関連のクラス:")
            next_class_elements = soup.find_all(['a', 'button'], class_=re.compile(r'next|continue', re.I))
            for element in next_class_elements:
                text = element.get_text(strip=True)
                href = element.get('href', '')
                class_name = element.get('class', [])
                logger.info(f"  {element.name} (class={class_name}): '{text}' -> {href}")
            
            # HTMLの一部を確認（ボタン周辺）
            logger.info("解答結果ページHTMLサンプル（ボタン関連部分）:")
            main_content = soup.find('main') or soup.find('div', class_='container')
            if main_content:
                content_text = str(main_content)
                # 「次」を含む行を抽出
                lines = content_text.split('\n')
                for i, line in enumerate(lines):
                    if '次' in line or 'btn' in line or 'button' in line:
                        logger.info(f"  行 {i}: {line.strip()}")
                        
        except Exception as e:
            logger.error(f"調査中にエラー: {e}")
    
    def run_investigation(self):
        """調査実行"""
        logger.info("🔍 ボタンテキスト調査開始")
        self.investigate_result_page_buttons()
        logger.info("📋 調査完了")

if __name__ == "__main__":
    investigator = ButtonTextInvestigation()
    investigator.run_investigation()