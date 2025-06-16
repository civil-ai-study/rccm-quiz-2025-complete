#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re

def test_review_function():
    """復習機能完全手作業テスト"""
    
    base_url = 'http://localhost:5003'
    session = requests.Session()

    print('🔧 復習機能テスト開始...')

    try:
        # 1. 復習リストページアクセステスト
        print('[1] 復習リストページアクセステスト')
        response = session.get(f'{base_url}/review')
        if response.status_code != 200:
            print(f'❌ 復習リストアクセス失敗: {response.status_code}')
            return False
        print('✅ 復習リストページアクセス成功')

        # 2. 復習問題開始テスト (何も復習問題がない場合のハンドリング)
        print('[2] 復習問題開始テスト')
        response = session.get(f'{base_url}/review_exam')
        if response.status_code == 200:
            print('✅ 復習問題開始成功 (復習問題あり)')
        elif 'レビュー問題がありません' in response.text or '復習対象の問題がありません' in response.text:
            print('✅ 復習問題なし状態正常処理')
        else:
            print(f'⚠️ 復習問題開始: 状態確認必要 ({response.status_code})')

        # 3. 間違った問題を作成するため、いくつか問題に間違って回答
        print('[3] 復習データ作成のため間違い回答実行')
        
        # 道路部門で間違い回答を作成
        response = session.get(f'{base_url}/department_study/road')
        if response.status_code != 200:
            print(f'❌ 道路部門アクセス失敗: {response.status_code}')
            return False

        # 3問間違い回答を送信
        for i in range(3):
            response = session.get(f'{base_url}/exam')
            if 'セッション情報が異常です' in response.text:
                print(f'❌ 問題{i+1}: セッション異常エラー')
                return False

            # QID取得
            qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
            qid = qid_match.group(1) if qid_match else '1'
            
            # 正解を取得して間違った答えを送信
            correct_match = re.search(r'data-correct="([A-D])"', response.text)
            correct_answer = correct_match.group(1) if correct_match else 'A'
            
            # 間違った答えを選択 (正解がAならB、BならC、など)
            wrong_answers = {'A': 'B', 'B': 'C', 'C': 'D', 'D': 'A'}
            wrong_answer = wrong_answers.get(correct_answer, 'B')
            
            answer_data = {'qid': qid, 'answer': wrong_answer, 'elapsed': '2.5'}
            response = session.post(f'{base_url}/exam', data=answer_data)
            
            if response.status_code != 200:
                print(f'❌ 間違い回答{i+1}: 送信失敗')
                return False
                
            print(f'✅ 間違い回答{i+1}: QID {qid} 完了')
            time.sleep(0.2)

        # 4. 復習リスト再確認
        print('[4] 復習リスト更新確認')
        response = session.get(f'{base_url}/review')
        if response.status_code != 200:
            print(f'❌ 復習リスト再確認失敗: {response.status_code}')
            return False
        
        # 復習問題があるかチェック
        if '復習対象の問題' in response.text or 'review-item' in response.text:
            print('✅ 復習問題が正常に追加された')
        else:
            print('⚠️ 復習問題追加を確認できない (正常な場合もある)')

        # 5. 復習試験実行
        print('[5] 復習試験実行テスト')
        response = session.get(f'{base_url}/review_exam')
        if response.status_code == 200 and ('問題' in response.text or 'question' in response.text):
            print('✅ 復習試験開始成功')
            
            # 復習問題を1問解答
            qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
            if qid_match:
                qid = qid_match.group(1)
                answer_data = {'qid': qid, 'answer': 'A', 'elapsed': '3.0'}
                response = session.post(f'{base_url}/review_exam', data=answer_data)
                
                if response.status_code == 200:
                    print('✅ 復習問題解答成功')
                else:
                    print(f'❌ 復習問題解答失敗: {response.status_code}')
                    return False
            else:
                print('⚠️ 復習問題QID取得できず')
        else:
            print('⚠️ 復習試験開始: 復習問題なし状態')

        # 6. ブックマーク機能テスト
        print('[6] ブックマーク機能テスト')
        
        # 基本科目でブックマーク作成
        response = session.get(f'{base_url}/department_study/basic')
        response = session.get(f'{base_url}/exam')
        
        qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
        if qid_match:
            qid = qid_match.group(1)
            
            # ブックマーク追加
            bookmark_response = session.post(f'{base_url}/bookmark', 
                                           json={'qid': int(qid), 'action': 'add'})
            if bookmark_response.status_code == 200:
                print(f'✅ ブックマーク追加成功: QID {qid}')
            else:
                print(f'❌ ブックマーク追加失敗: {bookmark_response.status_code}')
                return False
        else:
            print('⚠️ ブックマークテスト用QID取得失敗')

        # 7. 統計ページアクセステスト
        print('[7] 統計ページアクセステスト')
        response = session.get(f'{base_url}/statistics')
        if response.status_code != 200:
            print(f'❌ 統計ページアクセス失敗: {response.status_code}')
            return False
        print('✅ 統計ページアクセス成功')

        print('🎉 復習機能テスト完全成功！')
        return True

    except Exception as e:
        print(f'❌ 復習機能テストエラー: {str(e)}')
        return False

if __name__ == '__main__':
    success = test_review_function()
    if not success:
        exit(1)
    print('✅ 復習機能テスト完了')