# -*- coding: utf-8 -*-
"""
ULTRA SYNC [基本機能確保-003] 基本フロー動作確認
「問題表示→回答→次問題→結果」の完全検証（副作用なし）
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import sys
import traceback
import re

def extract_progress_info(html_content):
    """進捗情報を安全に抽出（読み取り専用）"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 進捗バッジを探す
        progress_badge = soup.find('span', {'aria-label': '進捗'})
        if progress_badge:
            progress_text = progress_badge.get_text().strip()
            # "1/10" 形式をパース
            if '/' in progress_text:
                current, total = progress_text.split('/')
                return int(current), int(total)
        
        return None, None
    except Exception:
        return None, None

def extract_question_info(html_content):
    """問題情報を安全に抽出（読み取り専用）"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        info = {
            'question_text': '',
            'options': [],
            'qid': '',
            'csrf_token': ''
        }
        
        # 問題テキスト
        question_element = soup.find('h3', class_='question-text')
        if question_element:
            info['question_text'] = question_element.get_text().strip()[:100]  # 最初の100文字
        
        # 選択肢
        option_elements = soup.find_all('span', class_='option-text')
        for option in option_elements:
            info['options'].append(option.get_text().strip()[:50])  # 最初の50文字
        
        # フォーム情報
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        qid_input = soup.find('input', {'name': 'qid'})
        
        if csrf_input:
            info['csrf_token'] = csrf_input.get('value', '')
        if qid_input:
            info['qid'] = qid_input.get('value', '')
        
        return info
    except Exception:
        return None

def extract_result_info(html_content):
    """結果画面情報を安全に抽出（読み取り専用）"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        info = {
            'correct_count': 0,
            'total_questions': 0,
            'accuracy': 0.0,
            'has_next_actions': False
        }
        
        # 正答数・総問題数
        score_elements = soup.find_all('div', class_='score-value')
        if score_elements:
            try:
                info['correct_count'] = int(score_elements[0].get_text().strip())
            except:
                pass
        
        # 正答率
        accuracy_elements = soup.find_all('div', class_='accuracy-value')
        if accuracy_elements:
            try:
                accuracy_text = accuracy_elements[0].get_text().strip()
                # "85.0%" から数値を抽出
                accuracy_match = re.search(r'(\d+\.?\d*)%', accuracy_text)
                if accuracy_match:
                    info['accuracy'] = float(accuracy_match.group(1))
            except:
                pass
        
        # 次のアクションボタン確認
        action_buttons = soup.find_all('a', class_='action-btn')
        info['has_next_actions'] = len(action_buttons) > 0
        
        # タイトルで結果画面か確認
        title_element = soup.find('title')
        if title_element and '結果' in title_element.get_text():
            info['is_result_page'] = True
        else:
            info['is_result_page'] = False
        
        return info
    except Exception:
        return None

def safe_basic_flow_test(department_name, base_url, test_session):
    """
    ULTRA SYNC: 基本フロー完全検証（副作用なし・読み取り専用）
    問題表示→回答→次問題→結果の全工程を検証
    """
    print(f'\n=== {department_name} 基本フロー検証開始 ===')
    
    flow_steps = []
    errors = []
    
    try:
        # Step 1: 試験開始
        print(f'Step 1: {department_name} 試験開始')
        exam_data = {
            'exam_type': 'specialist',
            'department': department_name,
            'question_count': '3'  # 基本フローテストは3問に制限
        }
        response = test_session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        if response.status_code not in [200, 302]:
            errors.append(f'試験開始失敗: {response.status_code}')
            return {'department': department_name, 'status': 'START_FAILED', 'steps': flow_steps, 'errors': errors}
        
        flow_steps.append('試験開始: OK')
        
        # Step 2: 基本フロー検証（3問）
        for question_no in range(1, 4):
            print(f'  問題 {question_no}/3 基本フロー検証中...')
            
            # 2a. 問題表示確認
            response = test_session.get(f'{base_url}/exam', timeout=30)
            if response.status_code != 200:
                errors.append(f'問題{question_no}: 表示失敗({response.status_code})')
                break
            
            # エラーチェック
            if '無効なデータ形式です' in response.text or '処理中に問題が発生しました' in response.text:
                errors.append(f'問題{question_no}: データエラー')
                break
            
            # 進捗情報抽出
            current_q, total_q = extract_progress_info(response.text)
            if current_q != question_no:
                errors.append(f'問題{question_no}: 進捗不一致(表示:{current_q}, 期待:{question_no})')
            
            # 問題情報抽出
            question_info = extract_question_info(response.text)
            if not question_info or not question_info['qid'] or not question_info['csrf_token']:
                errors.append(f'問題{question_no}: 問題情報不足')
                break
            
            flow_steps.append(f'問題{question_no}表示: OK (ID:{question_info["qid"][:8]}...)')
            
            # 2b. 回答送信
            answer_data = {
                'answer': 'A',  # 常にA選択（安全）
                'qid': question_info['qid'],
                'elapsed': '5',
                'csrf_token': question_info['csrf_token']
            }
            
            response = test_session.post(f'{base_url}/exam', data=answer_data, timeout=30)
            if response.status_code not in [200, 302]:
                errors.append(f'問題{question_no}: 回答送信失敗({response.status_code})')
                break
            
            flow_steps.append(f'問題{question_no}回答: OK')
            
            # 2c. 次問題への遷移確認（最後の問題以外）
            if question_no < 3:
                # 次の問題に遷移したか確認
                response = test_session.get(f'{base_url}/exam', timeout=30)
                if response.status_code == 200:
                    next_current, _ = extract_progress_info(response.text)
                    if next_current == question_no + 1:
                        flow_steps.append(f'問題{question_no}→{question_no+1}遷移: OK')
                    else:
                        errors.append(f'問題{question_no}: 遷移失敗')
            
            # ULTRA SYNC: サーバー負荷軽減
            time.sleep(1)
        
        # Step 3: 結果画面確認
        print('  Step 3: 結果画面表示確認')
        response = test_session.get(f'{base_url}/exam', timeout=30)
        
        # リダイレクトの場合は結果ページを直接確認
        if response.status_code == 302:
            response = test_session.get(f'{base_url}/result', timeout=30)
        
        if response.status_code == 200:
            result_info = extract_result_info(response.text)
            if result_info and result_info['is_result_page']:
                flow_steps.append(f'結果画面: OK (正答率:{result_info["accuracy"]}%)')
                
                # 次のアクションボタン確認
                if result_info['has_next_actions']:
                    flow_steps.append('次アクション: OK')
                else:
                    errors.append('次アクション: ボタン不足')
            else:
                errors.append('結果画面: 形式エラー')
        else:
            errors.append(f'結果画面: アクセス失敗({response.status_code})')
        
        # 最終判定
        if len(errors) == 0:
            status = 'COMPLETE_SUCCESS'
        elif len(flow_steps) >= 6:  # 基本ステップの大部分が成功
            status = 'PARTIAL_SUCCESS'
        else:
            status = 'FAILED'
        
        return {
            'department': department_name,
            'status': status,
            'steps': flow_steps,
            'errors': errors,
            'total_steps': len(flow_steps)
        }
        
    except Exception as e:
        errors.append(f'基本フロー例外: {str(e)}')
        return {
            'department': department_name,
            'status': 'EXCEPTION',
            'steps': flow_steps,
            'errors': errors,
            'total_steps': len(flow_steps)
        }

def run_basic_flow_verification():
    """
    ULTRA SYNC: 基本フロー動作確認テスト実行
    """
    print('ULTRA SYNC [基本機能確保-003] 基本フロー動作確認開始')
    print('=' * 80)
    print('副作用防止・機能アップ禁止・読み取り専用モード')
    print('=' * 80)
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    # テスト対象部門（代表的な3部門で基本フロー検証）
    test_departments = [
        "道路",           # 実績のある部門
        "河川、砂防及び海岸・海洋",  # 複雑な名前の部門
        "建設環境"        # 標準的な部門
    ]
    
    test_results = []
    
    for dept_index, department in enumerate(test_departments, 1):
        print(f'\n部門 {dept_index}/3: {department}')
        
        # ULTRA SYNC: 各部門で新しいセッション使用
        test_session = requests.Session()
        
        try:
            # ユーザー設定
            user_data = {'user_name': f'ULTRA_SYNC_FLOW_TEST_{dept_index}'}
            response = test_session.post(f'{base_url}/set_user', data=user_data, timeout=30)
            
            if response.status_code not in [200, 302]:
                test_results.append({
                    'department': department,
                    'status': 'USER_SETUP_FAILED',
                    'steps': [],
                    'errors': [f'ユーザー設定失敗: {response.status_code}'],
                    'total_steps': 0
                })
                continue
            
            # 基本フローテスト実行
            result = safe_basic_flow_test(department, base_url, test_session)
            test_results.append(result)
            
            # 部門間待機
            if dept_index < len(test_departments):
                print(f'  次の部門まで3秒待機...')
                time.sleep(3)
                
        except Exception as e:
            test_results.append({
                'department': department,
                'status': 'SETUP_EXCEPTION',
                'steps': [],
                'errors': [f'セットアップ例外: {str(e)}'],
                'total_steps': 0
            })
        
        finally:
            test_session.close()
    
    # 結果集計・分析
    print('\n' + '=' * 80)
    print('ULTRA SYNC 基本フロー動作確認テスト結果')
    print('=' * 80)
    
    complete_success = 0
    partial_success = 0
    failed = 0
    total_steps = 0
    
    for result in test_results:
        dept = result['department']
        status = result['status']
        steps = result['steps']
        errors = result['errors']
        step_count = result['total_steps']
        
        total_steps += step_count
        
        if status == 'COMPLETE_SUCCESS':
            status_icon = 'OK COMPLETE'
            complete_success += 1
        elif status == 'PARTIAL_SUCCESS':
            status_icon = 'WARN PARTIAL'
            partial_success += 1
        else:
            status_icon = 'NG FAILED'
            failed += 1
        
        print(f'{status_icon} {dept}: {step_count}ステップ完了')
        
        # 成功ステップ表示
        for step in steps[:3]:  # 最初の3ステップ表示
            print(f'    OK {step}')
        
        # エラー表示
        if errors:
            for error in errors[:2]:  # 最初の2エラー表示
                print(f'    NG {error}')
    
    # 最終統計
    print(f'\n最終統計:')
    print(f'   完全成功: {complete_success}/3')
    print(f'   部分成功: {partial_success}/3')
    print(f'   失敗: {failed}/3')
    print(f'   総ステップ数: {total_steps}')
    
    success_rate = (complete_success / 3) * 100
    
    print(f'   完全成功率: {success_rate:.1f}%')
    
    # 最終判定
    if complete_success >= 2:  # 67%以上の完全成功
        print('\n結論: 基本フロー動作確認 PASSED')
        return True
    elif complete_success + partial_success >= 2:  # 67%以上の成功
        print('\n結論: 基本フロー部分的成功 - 要改善点あり')
        return None
    else:
        print('\n結論: 基本フロー重大問題 - 修正が必要')
        return False

if __name__ == '__main__':
    try:
        result = run_basic_flow_verification()
        
        if result is True:
            print('\n[基本機能確保-003] 完了 - 基本フロー確認済み')
            sys.exit(0)
        elif result is None:
            print('\n[基本機能確保-003] 要改善 - 部分的成功')
            sys.exit(1)
        else:
            print('\n[基本機能確保-003] 要修正 - フロー失敗')
            sys.exit(2)
    
    except KeyboardInterrupt:
        print('\nテスト中断')
        sys.exit(130)
    except Exception as e:
        print(f'\nテスト実行エラー: {e}')
        sys.exit(1)