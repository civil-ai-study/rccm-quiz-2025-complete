#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RCCM試験詳細プレイセッション
問題内容を詳細に表示してプレイ
"""

import requests
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime

class DetailedPlaySession:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def show_page_content(self, html_content, question_num):
        """ページ内容を詳細表示"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            print(f"\n=== 第{question_num}問 ページ内容 ===")
            
            # ページの主要部分を表示
            lines = text.split('\n')
            important_lines = []
            
            for line in lines:
                line = line.strip()
                if len(line) > 10:  # 10文字以上の行のみ
                    # フィルタリング（不要な部分を除外）
                    if not any(skip in line.lower() for skip in ['copyright', 'claude', 'generated', 'javascript']):
                        important_lines.append(line)
            
            # 最初の20行を表示
            print("主要内容:")
            for i, line in enumerate(important_lines[:20], 1):
                print(f"{i:2d}: {line[:100]}...")
            
            # 問題らしき部分を特定
            question_candidates = []
            for line in important_lines:
                if any(pattern in line for pattern in ['問題', 'について', 'として', 'なるもの', 'か。']):
                    if len(line) > 20:
                        question_candidates.append(line)
            
            if question_candidates:
                print(f"\n問題候補:")
                for i, candidate in enumerate(question_candidates[:3], 1):
                    print(f"{i}: {candidate[:120]}...")
            
            # 選択肢らしき部分を特定
            options = re.findall(r'[A-D][）\)\.]\s*([^A-D\n]{10,100})', text)
            if options:
                print(f"\n選択肢候補:")
                for i, option in enumerate(options[:4], 1):
                    print(f"{chr(64+i)}: {option.strip()[:80]}...")
            
            return len(question_candidates) > 0
            
        except Exception as e:
            print(f"コンテンツ表示エラー: {e}")
            return False
    
    def detailed_play(self, department, year):
        """詳細プレイセッション"""
        print(f"RCCM試験詳細プレイセッション開始")
        print(f"部門: {department} / 年度: {year}年")
        print(f"開始: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # セッション開始
            print("\n1. セッション開始...")
            start_url = f"{self.base_url}/start_exam/{department}"
            start_data = {"questions": 5, "year": str(year)}  # 5問に限定
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"   結果: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print("   セッション開始失敗")
                return False
            
            # 初回問題ページ
            print("\n2. 問題ページアクセス...")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            print(f"   結果: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print("   問題ページアクセス失敗")
                return False
            
            # 各問題を詳細表示
            for q_num in range(1, 6):  # 5問まで
                print(f"\n{'='*60}")
                print(f"第{q_num}問 詳細確認")
                print(f"{'='*60}")
                
                time.sleep(1)  # 読み込み時間
                
                # ページ内容を詳細表示
                has_question = self.show_page_content(exam_response.text, q_num)
                
                if has_question:
                    print(f"\n第{q_num}問: 問題内容を確認しました")
                    
                    # 回答を選択
                    print("回答を考えています...")
                    time.sleep(2)
                    
                    my_answer = ['A', 'B', 'C', 'D'][q_num % 4]
                    print(f"選択した回答: {my_answer}")
                else:
                    print(f"\n第{q_num}問: 問題内容が不明です")
                    my_answer = 'A'
                
                # 最終問題でなければ次に進む
                if q_num < 5:
                    print(f"\n第{q_num + 1}問に進みます...")
                    
                    try:
                        answer_data = {'answer': my_answer, 'next': '1'}
                        answer_response = self.session.post(exam_url, data=answer_data, timeout=30)
                        
                        if answer_response.status_code == 200:
                            exam_response = answer_response
                            print(f"次の問題に進行成功")
                        else:
                            print(f"進行失敗: HTTP {answer_response.status_code}")
                            break
                            
                        time.sleep(2)  # 間隔
                        
                    except Exception as e:
                        print(f"進行エラー: {e}")
                        break
            
            print(f"\n{'='*60}")
            print(f"詳細プレイセッション完了")
            print(f"完了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            return True
            
        except Exception as e:
            print(f"プレイエラー: {e}")
            return False

def main():
    print("RCCM試験詳細プレイセッション")
    print("=" * 60)
    
    player = DetailedPlaySession()
    result = player.detailed_play('河川・砂防', 2018)
    
    if result:
        print("詳細プレイセッション完了")
    else:
        print("プレイセッションで問題発生")

if __name__ == "__main__":
    main()