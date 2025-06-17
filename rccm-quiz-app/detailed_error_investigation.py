#!/usr/bin/env python3
"""
詳細エラー調査: 1問目から2問目への遷移時の問題を調査
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

class DetailedErrorInvestigation:
    def __init__(self):
        self.session = requests.Session()
        
    def investigate_session_flow(self):
        """セッション流れの詳細調査"""
        logger.info("=== セッション流れの詳細調査 ===")
        
        try:
            # セッション開始
            random_url = '/exam?department=road&type=specialist'
            response = self.session.get(f'{BASE_URL}{random_url}')
            
            logger.info(f"セッション開始 - Status: {response.status_code}")
            logger.info(f"セッション開始 - URL: {response.url}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # セッション情報をログ
            session_info = soup.find('div', class_='progress-info')
            if session_info:
                logger.info(f"セッション情報: {session_info.get_text()}")
            
            # 1問目の詳細
            question_text = soup.find(['div', 'p'], class_=re.compile(r'question'))
            if question_text:
                logger.info(f"1問目の問題文（一部）: {question_text.get_text()[:100]}...")
            
            choices = soup.find_all('input', {'name': 'answer'})
            logger.info(f"1問目の選択肢数: {len(choices)}")
            
            for i, choice in enumerate(choices):
                logger.info(f"  選択肢 {i+1}: {choice.get('value')} - {choice.get('id', 'no-id')}")
            
            # フォーム情報
            form = soup.find('form')
            if form:
                action = form.get('action')
                method = form.get('method', 'GET')
                logger.info(f"フォーム: {method} {action}")
                
                # 隠し入力を確認
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
                for hidden in hidden_inputs:
                    name = hidden.get('name')
                    value = hidden.get('value')
                    logger.info(f"  隠し入力: {name} = {value}")
            
            # 1問目に回答
            if choices:
                choice_value = choices[0]['value']
                logger.info(f"1問目回答選択: {choice_value}")
                
                form_data = {'answer': choice_value}
                
                # 隠し入力も含める
                for hidden in hidden_inputs:
                    name = hidden.get('name')
                    value = hidden.get('value')
                    if name and value:
                        form_data[name] = value
                
                logger.info(f"送信データ: {form_data}")
                
                action_url = form.get('action', '/submit_answer')
                response = self.session.post(f'{BASE_URL}{action_url}', data=form_data)
                
                logger.info(f"1問目回答送信 - Status: {response.status_code}")
                logger.info(f"1問目回答送信 - URL: {response.url}")
                
                # 2問目の状態を確認
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # エラーページかチェック
                title = soup.find('title')
                if title:
                    logger.info(f"2問目ページタイトル: {title.get_text()}")
                
                # エラーメッセージがあるかチェック
                error_messages = soup.find_all(['div', 'p'], class_=re.compile(r'error|alert'))
                for error in error_messages:
                    logger.error(f"エラーメッセージ: {error.get_text()}")
                
                # 2問目の選択肢
                choices_2 = soup.find_all('input', {'name': 'answer'})
                logger.info(f"2問目の選択肢数: {len(choices_2)}")
                
                if not choices_2:
                    # ページの内容を確認
                    page_text = soup.get_text()[:500]
                    logger.info(f"2問目ページの内容（最初の500文字）: {page_text}")
                    
                    # 特定のキーワードを探す
                    if 'エラー' in page_text:
                        logger.error("エラーページに遷移しました")
                    elif '結果' in page_text:
                        logger.info("結果ページに遷移しました")
                    elif 'セッション' in page_text:
                        logger.warning("セッション関連の問題の可能性")
                    
                    # HTMLの構造も確認
                    main_content = soup.find('main') or soup.find('div', class_='container')
                    if main_content:
                        logger.info(f"メインコンテンツ: {str(main_content)[:200]}...")
            
        except Exception as e:
            logger.error(f"調査中にエラー: {e}")
    
    def test_multiple_sessions(self):
        """複数セッションのテスト"""
        logger.info("\n=== 複数セッションのテスト ===")
        
        session_types = [
            ('/exam?department=road&type=specialist', '道路部門'),
            ('/exam?category=%E5%85%B1%E9%80%9A', '共通問題'),
            ('/exam?department=road&type=specialist&year=2018', '道路2018年'),
        ]
        
        for url, name in session_types:
            try:
                logger.info(f"\n--- {name} テスト ---")
                
                response = self.session.get(f'{BASE_URL}{url}')
                logger.info(f"{name} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    choices = soup.find_all('input', {'name': 'answer'})
                    logger.info(f"{name} - 選択肢数: {len(choices)}")
                    
                    if choices:
                        # 1問だけテスト
                        choice_value = choices[0]['value']
                        form = soup.find('form')
                        action_url = form.get('action', '/submit_answer')
                        
                        form_data = {'answer': choice_value}
                        
                        # 隠し入力も含める
                        hidden_inputs = form.find_all('input', {'type': 'hidden'})
                        for hidden in hidden_inputs:
                            name_attr = hidden.get('name')
                            value = hidden.get('value')
                            if name_attr and value:
                                form_data[name_attr] = value
                        
                        response = self.session.post(f'{BASE_URL}{action_url}', data=form_data)
                        logger.info(f"{name} - 回答後Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            next_choices = soup.find_all('input', {'name': 'answer'})
                            logger.info(f"{name} - 次問選択肢数: {len(next_choices)}")
                            
                            if not next_choices:
                                title = soup.find('title')
                                if title:
                                    logger.info(f"{name} - 遷移先タイトル: {title.get_text()}")
                        else:
                            logger.error(f"{name} - 回答送信失敗")
                    else:
                        logger.warning(f"{name} - 選択肢なし")
                else:
                    logger.error(f"{name} - セッション開始失敗")
                    
                # セッションをリセット
                self.session = requests.Session()
                
            except Exception as e:
                logger.error(f"{name} テスト中にエラー: {e}")
    
    def run_investigation(self):
        """調査実行"""
        logger.info("🔍 詳細エラー調査開始")
        
        self.investigate_session_flow()
        self.test_multiple_sessions()
        
        logger.info("\n📋 調査完了")

if __name__ == "__main__":
    investigator = DetailedErrorInvestigation()
    investigator.run_investigation()