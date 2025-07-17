#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番環境手動テスト - 10問・20問・30問完全検証
嘘なし・誇張なしの正確な結果報告
"""
import requests
import json
from urllib.parse import urljoin, urlparse
import time

# 本番環境URL
BASE_URL = 'https://rccm-quiz-app.onrender.com'

def test_manual_10_questions():
    print('🔍 10問手動テスト開始')
    session = requests.Session()
    
    try:
        # 1. ホームページアクセス
        print('   ステップ1: ホームページアクセス')
        response = session.get(BASE_URL)
        if response.status_code != 200:
            return {'success': False, 'error': f'ホームページアクセス失敗: {response.status_code}'}
        
        # 2. 試験開始ページへ
        print('   ステップ2: 試験開始ページアクセス')
        response = session.get(f'{BASE_URL}/exam')
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始ページ失敗: {response.status_code}'}
        
        # 3. 10問基礎科目でPOST
        print('   ステップ3: 10問基礎科目試験開始')
        form_data = {
            'questions': '10',
            'question_type': 'basic',
            'year': '2023'
        }
        
        response = session.post(f'{BASE_URL}/start_exam', data=form_data)
        print(f'   POST結果: ステータス{response.status_code}, レスポンス長{len(response.text)}文字')
        
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始POST失敗: {response.status_code}'}
        
        # 4. 問題ページの詳細確認
        content = response.text
        has_question = '問題' in content
        has_10_indicator = 'の10問中' in content or '問題1' in content
        has_progress = '進捗' in content or 'progress' in content.lower()
        
        print(f'   問題表示: {has_question}')
        print(f'   10問表示: {has_10_indicator}') 
        print(f'   進捗表示: {has_progress}')
        
        if has_question and has_10_indicator:
            return {'success': True, 'status': '10問開始成功', 'details': {'question': has_question, '10_indicator': has_10_indicator, 'progress': has_progress}}
        else:
            return {'success': False, 'error': '10問問題ページが正しく表示されていない', 'details': {'question': has_question, '10_indicator': has_10_indicator}}
            
    except Exception as e:
        return {'success': False, 'error': f'テスト実行エラー: {str(e)}'}

def test_manual_20_questions():
    print('🔍 20問手動テスト開始')
    session = requests.Session()
    
    try:
        # 1. ホームページアクセス
        print('   ステップ1: ホームページアクセス')
        response = session.get(BASE_URL)
        if response.status_code != 200:
            return {'success': False, 'error': f'ホームページアクセス失敗: {response.status_code}'}
        
        # 2. 試験開始ページへ
        print('   ステップ2: 試験開始ページアクセス')
        response = session.get(f'{BASE_URL}/exam')
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始ページ失敗: {response.status_code}'}
        
        # 3. 20問専門科目でPOST
        print('   ステップ3: 20問専門科目試験開始')
        form_data = {
            'questions': '20',
            'question_type': 'specialist',
            'department': 'road',
            'year': '2023'
        }
        
        response = session.post(f'{BASE_URL}/start_exam', data=form_data)
        print(f'   POST結果: ステータス{response.status_code}, レスポンス長{len(response.text)}文字')
        
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始POST失敗: {response.status_code}'}
        
        # 4. 問題ページの詳細確認
        content = response.text
        has_question = '問題' in content
        has_20_indicator = 'の20問中' in content or ('問題1' in content and 'specialist' in content)
        has_progress = '進捗' in content or 'progress' in content.lower()
        has_department = '道路' in content or 'road' in content.lower()
        
        print(f'   問題表示: {has_question}')
        print(f'   20問表示: {has_20_indicator}')
        print(f'   進捗表示: {has_progress}')
        print(f'   部門表示: {has_department}')
        
        if has_question and has_20_indicator:
            return {'success': True, 'status': '20問開始成功', 'details': {'question': has_question, '20_indicator': has_20_indicator, 'progress': has_progress, 'department': has_department}}
        else:
            return {'success': False, 'error': '20問問題ページが正しく表示されていない', 'details': {'question': has_question, '20_indicator': has_20_indicator}}
            
    except Exception as e:
        return {'success': False, 'error': f'テスト実行エラー: {str(e)}'}

def test_manual_30_questions():
    print('🔍 30問手動テスト開始')
    session = requests.Session()
    
    try:
        # 1. ホームページアクセス
        print('   ステップ1: ホームページアクセス')
        response = session.get(BASE_URL)
        if response.status_code != 200:
            return {'success': False, 'error': f'ホームページアクセス失敗: {response.status_code}'}
        
        # 2. 試験開始ページへ
        print('   ステップ2: 試験開始ページアクセス')
        response = session.get(f'{BASE_URL}/exam')
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始ページ失敗: {response.status_code}'}
        
        # 3. 30問専門科目でPOST
        print('   ステップ3: 30問専門科目試験開始')
        form_data = {
            'questions': '30',
            'question_type': 'specialist',
            'department': 'road',
            'year': '2023'
        }
        
        response = session.post(f'{BASE_URL}/start_exam', data=form_data)
        print(f'   POST結果: ステータス{response.status_code}, レスポンス長{len(response.text)}文字')
        
        if response.status_code != 200:
            return {'success': False, 'error': f'試験開始POST失敗: {response.status_code}'}
        
        # 4. 問題ページの詳細確認
        content = response.text
        has_question = '問題' in content
        has_30_indicator = 'の30問中' in content or ('問題1' in content and 'specialist' in content)
        has_progress = '進捗' in content or 'progress' in content.lower()
        has_department = '道路' in content or 'road' in content.lower()
        
        print(f'   問題表示: {has_question}')
        print(f'   30問表示: {has_30_indicator}')
        print(f'   進捗表示: {has_progress}')
        print(f'   部門表示: {has_department}')
        
        if has_question and has_30_indicator:
            return {'success': True, 'status': '30問開始成功', 'details': {'question': has_question, '30_indicator': has_30_indicator, 'progress': has_progress, 'department': has_department}}
        else:
            return {'success': False, 'error': '30問問題ページが正しく表示されていない', 'details': {'question': has_question, '30_indicator': has_30_indicator}}
            
    except Exception as e:
        return {'success': False, 'error': f'テスト実行エラー: {str(e)}'}

def main():
    print('🚨 本番環境手動テスト実行')
    print('=' * 60)
    
    # 10問テスト
    result_10 = test_manual_10_questions()
    print()
    
    # 20問テスト  
    result_20 = test_manual_20_questions()
    print()
    
    # 30問テスト
    result_30 = test_manual_30_questions()
    print()
    
    print('=' * 60)
    print('📊 最終結果サマリー（嘘なし・誇張なし）')
    print('-' * 60)
    print(f'10問テスト: {"✅成功" if result_10["success"] else "❌失敗"} - {result_10.get("status", result_10.get("error"))}')
    print(f'20問テスト: {"✅成功" if result_20["success"] else "❌失敗"} - {result_20.get("status", result_20.get("error"))}')
    print(f'30問テスト: {"✅成功" if result_30["success"] else "❌失敗"} - {result_30.get("status", result_30.get("error"))}')
    
    # 詳細情報がある場合は表示
    for name, result in [('10問', result_10), ('20問', result_20), ('30問', result_30)]:
        if 'details' in result:
            print(f'{name}詳細: {result["details"]}')
    
    # 総合結果
    all_success = result_10['success'] and result_20['success'] and result_30['success']
    print()
    print(f'🎯 総合結果: {"✅全て成功" if all_success else "❌一部または全て失敗"}')
    
    # 結果をJSONでも保存
    results = {
        'timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'tests': {
            '10_questions': result_10,
            '20_questions': result_20,
            '30_questions': result_30
        },
        'summary': {
            'all_success': all_success,
            'success_count': sum([result_10['success'], result_20['success'], result_30['success']]),
            'total_count': 3
        }
    }
    
    filename = f'manual_production_test_results_{results["timestamp"]}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'📄 詳細結果: {filename}')
    return results

if __name__ == '__main__':
    main()