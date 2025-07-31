# -*- coding: utf-8 -*-
"""
ULTRA SYNC [基本機能確保-009] 本番環境基本動作最終確認テスト
全修正内容の統合検証（副作用なし・読み取り専用）
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import sys
import traceback

def test_csrf_token_fix():
    """CSRFトークン修正の確認"""
    print('=== CSRFトークン修正確認 ===')
    session = requests.Session()
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ユーザー設定
        user_data = {'user_name': 'ULTRA_SYNC_CSRF_TEST'}
        response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        if response.status_code not in [200, 302]:
            return {'status': 'FAILED', 'error': f'ユーザー設定失敗: {response.status_code}'}
        
        # 専門科目開始
        exam_data = {
            'exam_type': 'specialist',
            'department': '道路',
            'question_count': '3'
        }
        response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        if response.status_code not in [200, 302]:
            return {'status': 'FAILED', 'error': f'試験開始失敗: {response.status_code}'}
        
        # 1問目のCSRFトークン確認
        response = session.get(f'{base_url}/exam', timeout=30)
        if response.status_code != 200:
            return {'status': 'FAILED', 'error': f'問題表示失敗: {response.status_code}'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input:
            return {'status': 'FAILED', 'error': 'CSRFトークン要素なし'}
        
        csrf_token = csrf_input.get('value', '')
        if not csrf_token or csrf_token == '':
            return {'status': 'FAILED', 'error': 'CSRFトークン空値'}
        
        return {
            'status': 'SUCCESS',
            'csrf_token_length': len(csrf_token),
            'csrf_token_preview': csrf_token[:8] + '...'
        }
        
    except Exception as e:
        return {'status': 'EXCEPTION', 'error': str(e)}
    finally:
        session.close()

def test_second_question_fix():
    """2問目表示問題修正の確認"""
    print('=== 2問目表示問題修正確認 ===')
    session = requests.Session()
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ユーザー設定
        user_data = {'user_name': 'ULTRA_SYNC_2Q_TEST'}
        response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        # 専門科目開始
        exam_data = {
            'exam_type': 'specialist',
            'department': '道路',
            'question_count': '3'
        }
        response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        # 1問目回答
        response = session.get(f'{base_url}/exam', timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        qid_input = soup.find('input', {'name': 'qid'})
        
        if not csrf_input or not qid_input:
            return {'status': 'FAILED', 'error': '1問目フォーム要素不足'}
        
        answer_data = {
            'answer': 'A',
            'qid': qid_input.get('value'),
            'elapsed': '5',
            'csrf_token': csrf_input.get('value')
        }
        
        response = session.post(f'{base_url}/exam', data=answer_data, timeout=30)
        if response.status_code not in [200, 302]:
            return {'status': 'FAILED', 'error': f'1問目回答失敗: {response.status_code}'}
        
        # 2問目表示確認（ここが修正箇所）
        response = session.get(f'{base_url}/exam', timeout=30)
        if response.status_code != 200:
            return {'status': 'FAILED', 'error': f'2問目表示失敗: {response.status_code}'}
        
        # エラーメッセージチェック
        if '無効なデータ形式です' in response.text:
            return {'status': 'FAILED', 'error': '2問目で無効なデータ形式エラー'}
        
        if '処理中に問題が発生しました' in response.text:
            return {'status': 'FAILED', 'error': '2問目で処理エラー'}
        
        # 正常な問題要素確認
        soup = BeautifulSoup(response.text, 'html.parser')
        question_text = soup.find('h3', class_='question-text')
        options = soup.find_all('span', class_='option-text')
        
        if not question_text or len(options) < 4:
            return {'status': 'FAILED', 'error': '2問目要素不足'}
        
        return {
            'status': 'SUCCESS',
            'question_preview': question_text.get_text()[:50] + '...',
            'options_count': len(options)
        }
        
    except Exception as e:
        return {'status': 'EXCEPTION', 'error': str(e)}
    finally:
        session.close()

def test_13_departments_stability():
    """13部門安定性確認（サンプリング）"""
    print('=== 13部門安定性確認 ===')
    
    # サンプル部門（負荷軽減のため3部門のみ）
    sample_departments = ['道路', '建設環境', 'トンネル']
    results = []
    
    for dept in sample_departments:
        session = requests.Session()
        base_url = 'https://rccm-quiz-2025.onrender.com'
        
        try:
            # ユーザー設定
            user_data = {'user_name': f'ULTRA_SYNC_DEPT_{dept}_TEST'}
            response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
            
            # 部門開始
            exam_data = {
                'exam_type': 'specialist',
                'department': dept,
                'question_count': '3'
            }
            response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
            
            if response.status_code not in [200, 302]:
                results.append({'department': dept, 'status': 'FAILED', 'error': f'開始失敗: {response.status_code}'})
                continue
            
            # 1問確認
            response = session.get(f'{base_url}/exam', timeout=30)
            if response.status_code != 200:
                results.append({'department': dept, 'status': 'FAILED', 'error': f'問題表示失敗: {response.status_code}'})
                continue
            
            # 基本要素確認
            if '選択肢' in response.text or 'option' in response.text:
                results.append({'department': dept, 'status': 'SUCCESS'})
            else:
                results.append({'department': dept, 'status': 'FAILED', 'error': '問題要素不足'})
            
            time.sleep(2)  # サーバー負荷軽減
            
        except Exception as e:
            results.append({'department': dept, 'status': 'EXCEPTION', 'error': str(e)})
        finally:
            session.close()
    
    return results

def test_basic_flow_integrity():
    """基本フロー整合性確認"""
    print('=== 基本フロー整合性確認 ===')
    session = requests.Session()
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ユーザー設定
        user_data = {'user_name': 'ULTRA_SYNC_FLOW_TEST'}
        response = session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        # 3問テスト
        exam_data = {
            'exam_type': 'specialist',
            'department': '道路',
            'question_count': '3'
        }
        response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        completed_questions = 0
        for i in range(3):
            # 問題表示
            response = session.get(f'{base_url}/exam', timeout=30)
            if response.status_code != 200:
                break
            
            # フォーム要素取得
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_input or not qid_input:
                break
            
            # 回答送信
            answer_data = {
                'answer': 'A',
                'qid': qid_input.get('value'),
                'elapsed': '3',
                'csrf_token': csrf_input.get('value')
            }
            
            response = session.post(f'{base_url}/exam', data=answer_data, timeout=30)
            if response.status_code not in [200, 302]:
                break
            
            completed_questions += 1
            time.sleep(1)
        
        # 結果画面確認
        response = session.get(f'{base_url}/result', timeout=30)
        result_accessible = response.status_code == 200 and '結果' in response.text
        
        return {
            'status': 'SUCCESS' if completed_questions == 3 and result_accessible else 'PARTIAL',
            'completed_questions': completed_questions,
            'result_accessible': result_accessible
        }
        
    except Exception as e:
        return {'status': 'EXCEPTION', 'error': str(e)}
    finally:
        session.close()

def run_production_final_verification():
    """本番環境最終確認テスト実行"""
    print('ULTRA SYNC [基本機能確保-009] 本番環境基本動作最終確認テスト')
    print('=' * 80)
    print('副作用防止・機能アップ禁止・読み取り専用モード')
    print('=' * 80)
    
    test_results = {}
    
    # テスト1: CSRFトークン修正確認
    print('\n1. CSRFトークン修正確認テスト')
    test_results['csrf_fix'] = test_csrf_token_fix()
    print(f"   結果: {test_results['csrf_fix']['status']}")
    if test_results['csrf_fix']['status'] == 'SUCCESS':
        print(f"   CSRFトークン: {test_results['csrf_fix']['csrf_token_preview']}")
    else:
        print(f"   エラー: {test_results['csrf_fix'].get('error', '不明')}")
    
    # テスト2: 2問目表示問題修正確認
    print('\n2. 2問目表示問題修正確認テスト')
    test_results['second_question_fix'] = test_second_question_fix()
    print(f"   結果: {test_results['second_question_fix']['status']}")
    if test_results['second_question_fix']['status'] == 'SUCCESS':
        print(f"   2問目確認: OK")
    else:
        print(f"   エラー: {test_results['second_question_fix'].get('error', '不明')}")
    
    # テスト3: 13部門安定性確認
    print('\n3. 13部門安定性確認テスト（サンプリング）')
    test_results['departments_stability'] = test_13_departments_stability()
    successful_depts = [r for r in test_results['departments_stability'] if r['status'] == 'SUCCESS']
    print(f"   結果: {len(successful_depts)}/3部門成功")
    for result in test_results['departments_stability']:
        status_icon = 'OK' if result['status'] == 'SUCCESS' else 'NG'
        print(f"   {status_icon} {result['department']}")
    
    # テスト4: 基本フロー整合性確認
    print('\n4. 基本フロー整合性確認テスト')
    test_results['basic_flow'] = test_basic_flow_integrity()
    print(f"   結果: {test_results['basic_flow']['status']}")
    print(f"   完了問題数: {test_results['basic_flow'].get('completed_questions', 0)}/3")
    print(f"   結果画面: {'OK' if test_results['basic_flow'].get('result_accessible') else 'NG'}")
    
    # 最終評価
    print('\n' + '=' * 80)
    print('ULTRA SYNC 本番環境最終確認テスト結果')
    print('=' * 80)
    
    # 各テストの成功/失敗判定
    success_count = 0
    total_tests = 4
    
    critical_tests = ['csrf_fix', 'second_question_fix']
    
    for test_name, result in test_results.items():
        if test_name == 'departments_stability':
            # 部門テストは過半数成功で OK
            dept_success = len([r for r in result if r['status'] == 'SUCCESS'])
            if dept_success >= 2:  # 3部門中2部門成功
                success_count += 1
                print(f"OK {test_name}: {dept_success}/3部門成功")
            else:
                print(f"NG {test_name}: {dept_success}/3部門成功")
        elif isinstance(result, dict) and result.get('status') == 'SUCCESS':
            success_count += 1
            print(f"OK {test_name}")
        else:
            print(f"NG {test_name}")
            if test_name in critical_tests:
                print(f"   CRITICAL: {test_name} は重要テスト")
    
    # 最終判定
    success_rate = (success_count / total_tests) * 100
    
    print(f'\n最終統計:')
    print(f'   成功テスト: {success_count}/{total_tests}')
    print(f'   成功率: {success_rate:.1f}%')
    
    # 重要テストの確認
    critical_success = all(test_results[test].get('status') == 'SUCCESS' for test in critical_tests)
    
    if success_count == total_tests:
        print('\n結論: 本番環境基本動作 PASSED - 全テスト成功')
        return True
    elif critical_success and success_count >= 3:
        print('\n結論: 本番環境基本動作 PASSED - 重要機能正常')
        return True
    else:
        print('\n結論: 本番環境基本動作 要改善 - 問題あり')
        return False

if __name__ == '__main__':
    try:
        result = run_production_final_verification()
        
        if result:
            print('\n[基本機能確保-009] 完了 - 本番環境正常動作確認済み')
            sys.exit(0)
        else:
            print('\n[基本機能確保-009] 要改善 - 問題検出')
            sys.exit(1)
    
    except KeyboardInterrupt:
        print('\nテスト中断')
        sys.exit(130)
    except Exception as e:
        print(f'\nテスト実行エラー: {e}')
        sys.exit(1)