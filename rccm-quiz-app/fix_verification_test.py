#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re

def test_fixed_questions():
    """修正後の基礎科目問題テスト"""
    
    print('🔧 修正後の基礎科目テスト開始...')

    base_url = 'http://localhost:5003'
    session = requests.Session()

    # 基礎科目開始
    response = session.get(f'{base_url}/department_study/basic')
    if response.status_code != 200:
        print('❌ 基礎科目アクセス失敗')
        return False

    print('✅ 基礎科目アクセス成功')

    # 修正された問題を含む範囲で何問かテスト
    for i in range(5):
        print(f'🎯 問題{i+1}/5')
        
        response = session.get(f'{base_url}/exam')
        if 'セッション情報が異常です' in response.text:
            print(f'❌ 問題{i+1}: セッション異常')
            return False
        
        # 問題内容をチェック
        if '②－①－③－④' in response.text:
            print(f'❌ 問題{i+1}: 未修正の数字記号が検出された')
            return False
        elif '使用材料の単位重量' in response.text:
            print(f'✅ 問題{i+1}: 修正された材料重量問題を確認')
            if 'アスファルト舗装－コンクリート－鉄筋コンクリート－鋼' in response.text:
                print(f'   ✅ 正しい選択肢テキストを確認')
            else:
                print(f'   ⚠️ 選択肢テキストが見つからない')
        else:
            print(f'✅ 問題{i+1}: 正常な問題表示')
        
        # 解答送信
        qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
        qid = qid_match.group(1) if qid_match else '1'
        
        answer_data = {'qid': qid, 'answer': 'A', 'elapsed': '2.0'}
        response = session.post(f'{base_url}/exam', data=answer_data)
        
        if response.status_code == 200:
            print(f'   ✅ QID {qid}: 解答送信成功')
        else:
            print(f'   ❌ QID {qid}: 解答送信失敗')
            return False
        
        time.sleep(0.2)

    print('🎉 修正後テスト完了')
    return True

if __name__ == '__main__':
    success = test_fixed_questions()
    if not success:
        exit(1)
    print('✅ 修正確認テスト成功')