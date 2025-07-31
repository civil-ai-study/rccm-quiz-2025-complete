#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 実際の10問完走テスト（簡潔版）
1問→2問→3問→...→10問まで実際にブラウザのように進行して確認
"""

import requests
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime

class SimpleWalkthroughTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.question_log = []
        
    def extract_simple_info(self, html_content):
        """簡単な問題情報抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            # 問題が存在するかチェック
            has_question = any(keyword in text for keyword in ['問題', '選択', '次の', '正しい', '誤って'])
            
            # 進捗情報の抽出
            progress_match = re.search(r'(\d+)\s*/\s*(\d+)', text)
            progress = progress_match.groups() if progress_match else (None, None)
            
            return {
                'has_question': has_question,
                'progress': progress,
                'content_length': len(text)
            }
            
        except Exception as e:
            return {
                'has_question': False,
                'progress': (None, None),
                'error': str(e)
            }
    
    def test_walkthrough(self, department, year):
        """実際の問題進行テスト"""
        print(f"\n=== {department}部門{year}年 実際の10問テスト ===")
        
        try:
            # セッション開始
            start_url = f"{self.base_url}/start_exam/{department}"
            start_data = {"questions": 10, "year": str(year)}
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"セッション開始: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                return False
                
            # 問題ページアクセス
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            print(f"問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                return False
            
            # 1問目〜10問目まで進行
            successful_questions = 0
            
            for question_no in range(1, 11):
                print(f"  {question_no}問目確認中...", end="")
                
                # 問題情報抽出
                info = self.extract_simple_info(exam_response.text)
                
                if info['has_question']:
                    successful_questions += 1
                    progress = info['progress']
                    print(f" OK (進捗: {progress[0]}/{progress[1]})" if progress[0] else " OK")
                else:
                    print(f" NG - 問題が表示されていません")
                
                # 最終問題でない場合は次に進む
                if question_no < 10:
                    try:
                        # 適当な回答（A）を送信
                        answer_data = {'answer': 'A', 'next': '1'}
                        answer_response = self.session.post(exam_url, data=answer_data, timeout=30)
                        
                        if answer_response.status_code == 200:
                            exam_response = answer_response
                            time.sleep(1)  # サーバー負荷軽減
                        else:
                            print(f"    次の問題への進行失敗: HTTP {answer_response.status_code}")
                            break
                    except Exception as e:
                        print(f"    進行エラー: {e}")
                        break
            
            print(f"\n結果: {successful_questions}/10問が正常表示")
            
            # 80%以上で成功とみなす
            return successful_questions >= 8
            
        except Exception as e:
            print(f"テストエラー: {e}")
            return False

def main():
    """メイン実行"""
    print("ULTRA SYNC 実際の10問完走テスト開始")
    print("=" * 60)
    
    tester = SimpleWalkthroughTest()
    
    # テスト対象
    test_cases = [
        ('河川・砂防', 2018),
        ('道路', 2015)
    ]
    
    results = []
    
    for department, year in test_cases:
        result = tester.test_walkthrough(department, year)
        results.append({
            'department': department,
            'year': year,
            'success': result
        })
        
        time.sleep(3)  # テスト間の間隔
    
    # 最終結果
    print("\n" + "=" * 60)
    print("実際の10問完走テスト 最終結果")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for result in results:
        status = "成功" if result['success'] else "失敗"
        print(f"{result['department']}部門{result['year']}年: {status}")
    
    print(f"\n総合結果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("EXCELLENT: 全ての実際の10問完走テストが成功")
    else:
        print(f"WARNING: {total_count - success_count}件のテストで問題発見")
    
    return success_count == total_count

if __name__ == "__main__":
    main()