#!/usr/bin/env python3
# 🎯 【手動必ず実施】本番環境でのウルトラシンクテスト

import requests
import json
from datetime import datetime
import time
import re

def manual_test_basic_exam_10_questions():
    """基礎科目（4-1共通）10問完走テスト"""
    
    print('🎯 【手動必ず実施】本番環境での基礎科目（4-1共通）10問完走テスト開始')
    print('=' * 70)
    
    # セッション開始
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ステップ1: ホームページアクセス
        print('ステップ1: ホームページアクセス')
        response = session.get(base_url, timeout=30)
        print(f'  ホームページ応答: {response.status_code}')
        if response.status_code != 200:
            raise Exception(f'ホームページアクセス失敗: {response.status_code}')
        
        # ステップ2: 基礎科目試験開始
        print('ステップ2: 基礎科目試験開始')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {
            'questions': '10',
            'year': '2024'
        }
        
        response = session.post(start_url, data=data, allow_redirects=True, timeout=30)
        print(f'  試験開始応答: {response.status_code}')
        print(f'  最終URL: {response.url}')
        
        if response.status_code != 200:
            print(f'  応答内容: {response.text[:500]}...')
            raise Exception(f'試験開始失敗: {response.status_code}')
        
        # ステップ3: 問題画面確認
        print('ステップ3: 問題画面確認')
        if '/exam' in response.url:
            print('  ✅ 正常に問題画面にリダイレクト')
            
            # 問題内容の確認
            content = response.text
            if '問題' in content or 'question' in content.lower():
                print('  ✅ 問題内容が表示されている')
                
                # 進捗表示の確認
                if '1/10' in content or '1 / 10' in content:
                    print('  ✅ 進捗表示（1/10）確認')
                else:
                    print('  ⚠️ 進捗表示が見つからない')
                
                # 選択肢の確認
                if all(option in content for option in ['A)', 'B)', 'C)', 'D)']):
                    print('  ✅ 選択肢A-D確認')
                else:
                    print('  ⚠️ 選択肢が不完全')
                
            else:
                print('  ❌ 問題内容が見つからない')
                print(f'  内容サンプル: {content[:200]}...')
        else:
            print(f'  ❌ 予期しないURL: {response.url}')
            return False
        
        # ステップ4: 10問完走シミュレーション
        print('ステップ4: 10問完走シミュレーション開始')
        
        for question_num in range(1, 11):
            print(f'  問題{question_num}の処理中...')
            
            # 回答送信
            answer_data = {
                'answer': 'A',  # テスト用の回答
                'question_id': str(question_num)
            }
            
            response = session.post(f'{base_url}/exam', data=answer_data, allow_redirects=True, timeout=30)
            
            if response.status_code != 200:
                print(f'    ❌ 問題{question_num}で失敗: {response.status_code}')
                return False
            
            # 最終問題かチェック
            if question_num == 10:
                if '/result' in response.url:
                    print('  ✅ 最終問題後、結果画面にリダイレクト')
                    print('  ✅ 10問完走成功！')
                    
                    # 結果画面の内容確認
                    result_content = response.text
                    if '結果' in result_content or 'result' in result_content.lower():
                        print('  ✅ 結果画面の内容確認')
                        
                        # スコア表示の確認
                        score_pattern = r'(\d+)\s*/\s*10'
                        score_match = re.search(score_pattern, result_content)
                        if score_match:
                            score = score_match.group(1)
                            print(f'  ✅ スコア表示確認: {score}/10')
                        else:
                            print('  ⚠️ スコア表示が見つからない')
                    
                    return True
                else:
                    print(f'  ❌ 最終問題後の予期しないURL: {response.url}')
                    return False
            else:
                # 次の問題が表示されているかチェック
                if f'{question_num + 1}/10' in response.text or f'{question_num + 1} / 10' in response.text:
                    print(f'    ✅ 問題{question_num + 1}に正常遷移')
                else:
                    print(f'    ⚠️ 問題{question_num + 1}への遷移が不明')
            
            time.sleep(0.5)  # 負荷軽減
        
        return True
        
    except Exception as e:
        print(f'\n❌ エラー発生: {e}')
        print('詳細調査が必要です')
        return False
    
    finally:
        print('\n' + '=' * 70)
        print(f'テスト完了時刻: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    success = manual_test_basic_exam_10_questions()
    if success:
        print('\n🎉 【手動必ず実施】基礎科目10問完走テスト - 成功')
    else:
        print('\n💥 【手動必ず実施】基礎科目10問完走テスト - 失敗')