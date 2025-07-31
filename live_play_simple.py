#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RCCM試験問題 ライブプレイセッション（簡潔版）
実際に問題を解いて進行する様子をリアルタイム表示
"""

import requests
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime

class SimplePlaySession:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.completed_questions = 0
        
    def extract_question(self, html_content):
        """問題内容を抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            # 問題文らしきテキストを探す
            lines = text.split('\n')
            question_text = ""
            
            for line in lines:
                line = line.strip()
                if len(line) > 30 and ('か。' in line or 'について' in line or 'として' in line):
                    if not any(skip in line for skip in ['Copyright', 'Claude', 'RCCM']):
                        question_text = line[:80] + "..." if len(line) > 80 else line
                        break
            
            # 選択肢を探す
            options = []
            for match in re.finditer(r'[A-D][）\.]([^A-D]{10,50})', text):
                options.append(f"{match.group(0)[:50]}...")
            
            # 進捗
            progress_match = re.search(r'(\d+)\s*/\s*(\d+)', text)
            progress = progress_match.groups() if progress_match else (None, None)
            
            return {
                'question': question_text,
                'options': options,
                'progress': progress,
                'valid': len(question_text) > 0
            }
            
        except Exception as e:
            return {'question': f"抽出エラー: {e}", 'options': [], 'progress': (None, None), 'valid': False}
    
    def display_question_info(self, data, q_num):
        """問題情報を表示"""
        print(f"\n--- 第{q_num}問 ---")
        if data['progress'][0]:
            print(f"進捗: {data['progress'][0]}/{data['progress'][1]}")
        
        if data['question']:
            print(f"問題: {data['question']}")
        
        if data['options']:
            print("選択肢:")
            for i, opt in enumerate(data['options'][:4], 1):
                print(f"  {opt}")
        
        print("-" * 40)
    
    def play_session(self, department, year):
        """実際にプレイセッションを実行"""
        print(f"\nRCCM試験ライブプレイ開始")
        print(f"部門: {department}")
        print(f"年度: {year}年")
        print(f"開始時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        try:
            # セッション開始
            print("セッションを開始しています...")
            start_url = f"{self.base_url}/start_exam/{department}"
            start_data = {"questions": 10, "year": str(year)}
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"セッション開始: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                return False
            
            # 問題ページアクセス
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            print(f"問題ページアクセス: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                return False
            
            # 問題を順次解く
            for q_num in range(1, 11):
                print(f"\n第{q_num}問を読み込み中...")
                time.sleep(1)
                
                # 問題を抽出
                question_data = self.extract_question(exam_response.text)
                
                if question_data['valid']:
                    self.display_question_info(question_data, q_num)
                    
                    # 回答を考える
                    print("回答を考えています...")
                    time.sleep(2)
                    
                    # 回答選択（適当にA〜Dから選択）
                    my_answer = ['A', 'B', 'C', 'D'][q_num % 4]
                    print(f"私の回答: {my_answer}")
                    
                    self.completed_questions += 1
                else:
                    print(f"第{q_num}問: 問題読み込み失敗")
                    my_answer = 'A'  # デフォルト値
                
                # 最終問題以外は次に進む
                if q_num < 10:
                    print("次の問題に進みます...")
                    
                    try:
                        answer_data = {'answer': my_answer, 'next': '1'}
                        answer_response = self.session.post(exam_url, data=answer_data, timeout=30)
                        
                        if answer_response.status_code == 200:
                            exam_response = answer_response
                            print(f"第{q_num + 1}問に進行成功")
                        else:
                            print(f"進行失敗: HTTP {answer_response.status_code}")
                            break
                            
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"進行エラー: {e}")
                        break
            
            # 結果発表
            print("\n" + "=" * 50)
            print("RCCM試験ライブプレイ完了！")
            print(f"部門: {department} ({year}年)")
            print(f"完了問題数: {self.completed_questions}/10問")
            print(f"完了時刻: {datetime.now().strftime('%H:%M:%S')}")
            
            if self.completed_questions >= 8:
                print("お疲れ様でした！無事に試験完了")
                return True
            else:
                print("一部問題でトラブル発生")
                return False
                
        except Exception as e:
            print(f"プレイエラー: {e}")
            return False

def main():
    print("RCCM試験ライブプレイセッション")
    print("=" * 50)
    
    player = SimplePlaySession()
    
    # 河川・砂防部門2018年でプレイ
    result = player.play_session('河川・砂防', 2018)
    
    print("\n" + "=" * 50)
    if result:
        print("ライブプレイセッション成功！")
    else:
        print("ライブプレイで問題発生")

if __name__ == "__main__":
    main()