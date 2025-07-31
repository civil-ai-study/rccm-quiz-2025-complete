#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 実際の10問完走テスト
1問→2問→3問→...→10問まで実際にブラウザのように進行して確認
"""

import requests
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime

class Real10QuestionWalkthroughTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.question_progression = []
        
    def extract_question_info(self, html_content):
        """問題情報を抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 問題番号の抽出
            question_number = None
            number_patterns = [
                r'問題\s*(\d+)',
                r'第\s*(\d+)\s*問',
                r'Q\s*(\d+)',
                r'(\d+)\s*問目'
            ]
            
            text = soup.get_text()
            for pattern in number_patterns:
                match = re.search(pattern, text)
                if match:
                    question_number = match.group(1)
                    break
            
            # 問題文の抽出（最初の長文テキストを問題文とみなす）
            paragraphs = soup.find_all('p')
            question_text = ""
            for p in paragraphs:
                if len(p.get_text().strip()) > 50:  # 50文字以上のテキストを問題文候補とする
                    question_text = p.get_text().strip()[:100] + "..."
                    break
            
            # 選択肢の抽出
            options = []
            option_patterns = [r'[A-D]\)', r'[A-D]\.', r'[ア-エ]']
            for pattern in option_patterns:
                matches = re.findall(f'{pattern}[^A-D\ア-エ]+', text)
                if matches:
                    options = [match.strip()[:50] + "..." for match in matches[:4]]
                    break
            
            # 進捗情報の抽出
            progress_info = {
                'current': None,
                'total': None
            }
            
            progress_patterns = [
                r'(\d+)\s*/\s*(\d+)',
                r'(\d+)\s*問目\s*/\s*(\d+)\s*問',
                r'問題\s*(\d+)\s*\(\s*全\s*(\d+)\s*問\s*\)'
            ]
            
            for pattern in progress_patterns:
                match = re.search(pattern, text)
                if match:
                    progress_info['current'] = int(match.group(1))
                    progress_info['total'] = int(match.group(2))
                    break
            
            return {
                'question_number': question_number,
                'question_text': question_text,
                'options': options,
                'progress': progress_info,
                'has_question': len(question_text) > 0,
                'page_length': len(text)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'has_question': False,
                'page_length': len(html_content) if html_content else 0
            }
    
    def real_walkthrough_test(self, department, year, target_questions=10):
        """実際の10問完走テスト"""
        print(f"\n{'='*80}")
        print(f"🎯 ULTRA SYNC 実際の10問完走テスト開始")
        print(f"部門: {department}")
        print(f"年度: {year}")
        print(f"目標問題数: {target_questions}問")
        print(f"開始時刻: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        try:
            # Step 1: セッション開始
            print(f"\n📋 Step 1: セッション開始")
            start_url = f"{self.base_url}/start_exam/{department}"
            start_data = {
                "questions": target_questions,
                "year": str(year)
            }
            
            print(f"   URL: {start_url}")
            print(f"   Data: {start_data}")
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"   Response: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print(f"❌ セッション開始失敗: HTTP {start_response.status_code}")
                return False
                
            # Step 2: 問題ページアクセス
            print(f"\n📋 Step 2: 問題ページアクセス")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=30)
            print(f"   URL: {exam_url}")
            print(f"   Response: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print(f"❌ 問題ページアクセス失敗: HTTP {exam_response.status_code}")
                return False
            
            # Step 3: 1問目～10問目まで実際に進行
            print(f"\n📋 Step 3: 1問目～{target_questions}問目まで実際に進行")
            
            for question_no in range(1, target_questions + 1):
                print(f"\n   🔍 {question_no}問目の確認")
                print(f"   ----------------------------------------")
                
                # 現在のページの問題情報を抽出
                question_info = self.extract_question_info(exam_response.text)
                
                print(f"   問題番号: {question_info.get('question_number', '不明')}")
                print(f"   問題文: {question_info.get('question_text', '取得失敗')[:80]}...")
                print(f"   選択肢数: {len(question_info.get('options', []))}個")
                print(f"   進捗: {question_info.get('progress', {}).get('current', '?')}/{question_info.get('progress', {}).get('total', '?')}")
                print(f"   問題存在: {'✅' if question_info.get('has_question') else '❌'}")
                
                # 記録保存
                self.question_progression.append({
                    'question_number': question_no,
                    'extracted_info': question_info,
                    'timestamp': datetime.now().isoformat(),
                    'success': question_info.get('has_question', False)
                })
                
                # 最終問題の場合はスキップ
                if question_no >= target_questions:
                    print(f"   🏁 最終問題({target_questions}問目)に到達")
                    break
                
                # 次の問題に進む（適当な答えを選択）
                print(f"   ⏭️ 次の問題へ進行中...")
                
                try:
                    # 回答送信（選択肢Aを選択）
                    answer_data = {
                        'answer': 'A',
                        'next': '1'
                    }
                    
                    answer_response = self.session.post(exam_url, data=answer_data, timeout=30)
                    
                    if answer_response.status_code == 200:
                        exam_response = answer_response  # 次の問題ページを更新
                        print(f"   ✅ {question_no+1}問目に進行成功")
                    else:
                        print(f"   ❌ {question_no+1}問目への進行失敗: HTTP {answer_response.status_code}")
                        break
                        
                    time.sleep(1)  # サーバー負荷軽減
                    
                except Exception as e:
                    print(f"   ❌ 進行エラー: {e}")
                    break
            
            # 結果サマリー
            print(f"\n{'='*80}")
            print(f"🎯 実際の10問完走テスト結果")
            print(f"{'='*80}")
            
            successful_questions = sum(1 for q in self.question_progression if q['success'])
            total_attempted = len(self.question_progression)
            
            print(f"   実際に確認した問題数: {total_attempted}問")
            print(f"   正常に表示された問題: {successful_questions}問")
            print(f"   成功率: {(successful_questions/total_attempted)*100:.1f}%" if total_attempted > 0 else "0%")
            
            # 詳細進行ログ
            print(f"\n📋 詳細進行ログ:")
            for i, q in enumerate(self.question_progression, 1):
                status = "✅" if q['success'] else "❌"
                print(f"   {i:2d}問目 {status}: {q['extracted_info'].get('question_text', '問題文取得失敗')[:60]}...")
            
            # 最終判定
            if successful_questions >= target_questions * 0.8:  # 80%以上で成功とみなす
                print(f"\n🎉 実際の10問完走テスト: 成功")
                print(f"   {successful_questions}/{target_questions}問が正常に表示されました")
                return True
            else:
                print(f"\n❌ 実際の10問完走テスト: 失敗")
                print(f"   {successful_questions}/{target_questions}問しか正常表示されませんでした")
                return False
                
        except Exception as e:
            print(f"\n❌ テスト実行エラー: {e}")
            return False

def main():
    """メイン実行"""
    tester = Real10QuestionWalkthroughTest()
    
    # テスト対象
    test_cases = [
        ('河川・砂防', 2018),
        ('道路', 2015)
    ]
    
    results = []
    
    for department, year in test_cases:
        print(f"\n🚀 {department}部門{year}年 実際の10問完走テスト開始")
        result = tester.real_walkthrough_test(department, year, 10)
        results.append({
            'department': department,
            'year': year,
            'success': result,
            'progression': tester.question_progression.copy()
        })
        
        # 次のテストのために進行記録をリセット
        tester.question_progression = []
        
        time.sleep(5)  # テスト間の間隔
    
    # 最終レポート
    print(f"\n{'='*100}")
    print(f"🎯 ULTRA SYNC 実際の10問完走テスト 最終レポート")
    print(f"{'='*100}")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"📊 総合結果: {success_count}/{total_count} テスト成功")
    print(f"📈 成功率: {(success_count/total_count)*100:.1f}%")
    
    for result in results:
        status = "✅ 成功" if result['success'] else "❌ 失敗"
        print(f"   {result['department']}部門{result['year']}年: {status}")
    
    if success_count == total_count:
        print(f"\n🏆 EXCELLENT: 全ての実際の10問完走テストが成功しました")
    else:
        print(f"\n⚠️ WARNING: {total_count - success_count}件のテストで問題が発見されました")
    
    return success_count == total_count

if __name__ == "__main__":
    main()