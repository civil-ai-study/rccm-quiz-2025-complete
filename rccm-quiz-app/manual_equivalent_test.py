#!/usr/bin/env python3
# 🛡️ ULTRASYNC 手動テスト等価検証

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
from datetime import datetime

def manual_equivalent_test():
    """手動テストと等価な検証を実行"""
    
    print('🛡️ ULTRASYNC 手動等価テスト開始')
    print('=' * 60)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # セッションクリア
            sess.clear()
        
        try:
            # ステップ1: トップページアクセス
            print('ステップ1: トップページアクセス')
            response = client.get('/')
            print(f'  トップページ応答: {response.status_code}')
            if response.status_code != 200:
                print(f'  ❌ トップページアクセス失敗')
                return False
            print('  ✅ トップページ正常')
            
            # ステップ2: 基礎科目試験開始（POST）
            print('ステップ2: 基礎科目試験開始')
            start_data = {
                'questions': '10',
                'year': '2024'
            }
            start_response = client.post('/start_exam/基礎科目', 
                                       data=start_data, 
                                       follow_redirects=False)
            print(f'  start_exam応答: {start_response.status_code}')
            print(f'  リダイレクト先: {start_response.location if start_response.location else "なし"}')
            
            # ステップ3: セッション状態確認
            print('ステップ3: セッション状態確認')
            with client.session_transaction() as sess:
                exam_question_ids = sess.get('exam_question_ids', [])
                exam_current = sess.get('exam_current', 0)
                exam_category = sess.get('exam_category', '')
                
                print(f'  問題ID数: {len(exam_question_ids)}')
                print(f'  現在位置: {exam_current}')
                print(f'  試験カテゴリー: {exam_category}')
                
                if len(exam_question_ids) == 0:
                    print('  ❌ セッションに問題IDが設定されていない')
                    return False
                elif len(exam_question_ids) != 10:
                    print(f'  ❌ 問題数が10ではない: {len(exam_question_ids)}')
                    return False
                else:
                    print('  ✅ セッション正常初期化')
            
            # ステップ4: /examルートアクセス（1問目表示）
            print('ステップ4: 1問目表示確認')
            exam_response = client.get('/exam')
            print(f'  /exam応答: {exam_response.status_code}')
            
            if exam_response.status_code != 200:
                print(f'  ❌ /examアクセス失敗: {exam_response.status_code}')
                return False
            
            content = exam_response.data.decode('utf-8')
            
            # 進捗表示確認
            if '問題 1/10' in content:
                print('  ✅ 進捗表示正常: 問題 1/10')
            elif '1/10' in content:
                print('  ✅ 進捗表示確認: 1/10形式')
            else:
                print('  ❌ 進捗表示なし')
                
            # 問題フォーム確認
            if '<form' in content and 'name="answer"' in content:
                print('  ✅ 問題フォーム存在')
            else:
                print('  ❌ 問題フォーム不存在')
                return False
            
            # エラーメッセージ確認
            error_keywords = ['エラー', 'Error', '問題が見つかりません', 'データが存在しません']
            has_error = any(keyword in content for keyword in error_keywords)
            if has_error:
                print('  ❌ エラーメッセージ検出')
                return False
            else:
                print('  ✅ エラーなし')
            
            # ステップ5: 10問完走シミュレーション
            print('ステップ5: 10問完走シミュレーション')
            
            for question_num in range(1, 11):
                print(f'  問題 {question_num}/10 処理中...')
                
                # 現在の問題ID取得
                with client.session_transaction() as sess:
                    current_qid = sess['exam_question_ids'][sess.get('exam_current', 0)]
                
                # 回答送信
                answer_data = {
                    'qid': current_qid,
                    'answer': 'A',  # 適当な回答
                    'elapsed': '30'
                }
                
                # CSRFトークンを取得してPOST
                csrf_response = client.get('/exam')
                csrf_content = csrf_response.data.decode('utf-8')
                
                import re
                csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', csrf_content)
                if csrf_match:
                    answer_data['csrf_token'] = csrf_match.group(1)
                
                answer_response = client.post('/exam', 
                                            data=answer_data, 
                                            follow_redirects=True)
                
                if answer_response.status_code != 200:
                    print(f'    ❌ 問題{question_num}回答失敗: {answer_response.status_code}')
                    return False
                
                # 進捗確認
                with client.session_transaction() as sess:
                    current_progress = sess.get('exam_current', 0)
                    if question_num < 10:
                        expected_progress = question_num
                        if current_progress == expected_progress:
                            print(f'    ✅ 進捗正常: {current_progress}/{len(sess["exam_question_ids"])}')
                        else:
                            print(f'    ⚠️ 進捗不一致: 期待{expected_progress}, 実際{current_progress}')
            
            # ステップ6: 最終結果画面確認
            print('ステップ6: 最終結果画面確認')
            
            # 10問完了後の状態確認
            with client.session_transaction() as sess:
                final_current = sess.get('exam_current', 0)
                total_questions = len(sess.get('exam_question_ids', []))
                
                print(f'  最終進捗: {final_current}/{total_questions}')
                
                if final_current >= total_questions:
                    print('  ✅ 全問題完了')
                else:
                    print(f'  ❌ 未完了: {final_current}/{total_questions}')
                    return False
            
            # 結果画面アクセス
            result_response = client.get('/exam')
            result_content = result_response.data.decode('utf-8')
            
            if '結果' in result_content or 'result' in result_content.lower():
                print('  ✅ 結果画面表示')
            else:
                print('  ❌ 結果画面未表示')
                return False
            
            print('\n' + '=' * 60)
            print('🛡️ ULTRASYNC 手動等価テスト完了')
            print('✅ 基礎科目10問完走テスト成功')
            
            return True
            
        except Exception as e:
            print(f'テスト中にエラー: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = manual_equivalent_test()
    if success:
        print('\n🎯 結論: 基礎科目10問完走テストは正常に動作します')
    else:
        print('\n❌ 結論: 基礎科目10問完走テストに問題があります')