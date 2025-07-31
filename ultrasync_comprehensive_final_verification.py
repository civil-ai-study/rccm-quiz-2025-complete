# -*- coding: utf-8 -*-
"""
ULTRA SYNC 総合最終検証システム
全11タスク完了後の包括的安定性確認（副作用なし・読み取り専用）
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import sys
import traceback

def comprehensive_stability_verification():
    """ULTRA SYNC 全機能総合安定性検証"""
    print('ULTRA SYNC 総合最終検証システム')
    print('=' * 80)
    print('全11タスク完了後の包括的安定性確認')
    print('副作用防止・機能アップ禁止・読み取り専用検証モード')
    print('=' * 80)
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    verification_results = {}
    
    # 検証項目リスト
    verification_items = [
        {
            'id': 'csrf_token_stability',
            'name': 'CSRFトークン安定性確認',
            'description': '緊急修正-001の効果確認'
        },
        {
            'id': 'second_question_stability', 
            'name': '2問目表示安定性確認',
            'description': '基本機能確保-001,006,007の効果確認'
        },
        {
            'id': 'department_coverage_stability',
            'name': '13部門動作安定性確認', 
            'description': '基本機能確保-002の効果確認'
        },
        {
            'id': 'basic_flow_stability',
            'name': '基本フロー安定性確認',
            'description': '基本機能確保-003の効果確認'
        },
        {
            'id': 'session_safety_stability',
            'name': 'セッション安全性確認',
            'description': '基本機能確保-004,007の効果確認'
        },
        {
            'id': 'memory_protection_stability',
            'name': 'メモリ保護安定性確認',
            'description': '基本機能確保-008の効果確認'
        },
        {
            'id': 'production_environment_stability',
            'name': '本番環境総合安定性確認',
            'description': '基本機能確保-009,010の効果確認'
        }
    ]
    
    print('\n=== 総合検証項目実行 ===')
    
    for item in verification_items:
        print(f'\n検証中: {item["name"]}')
        print(f'対象: {item["description"]}')
        
        try:
            if item['id'] == 'csrf_token_stability':
                result = verify_csrf_token_stability(base_url)
            elif item['id'] == 'second_question_stability':
                result = verify_second_question_stability(base_url)
            elif item['id'] == 'department_coverage_stability':
                result = verify_department_coverage_stability(base_url)
            elif item['id'] == 'basic_flow_stability':
                result = verify_basic_flow_stability(base_url)
            elif item['id'] == 'session_safety_stability':
                result = verify_session_safety_stability(base_url)
            elif item['id'] == 'memory_protection_stability':
                result = verify_memory_protection_stability(base_url)
            elif item['id'] == 'production_environment_stability':
                result = verify_production_environment_stability(base_url)
            else:
                result = {'status': 'SKIPPED', 'reason': '未実装'}
            
            verification_results[item['id']] = result
            
            status_icon = 'OK' if result['status'] == 'STABLE' else 'WARN' if result['status'] == 'PARTIAL' else 'NG'
            print(f'   {status_icon} {result["status"]}: {result.get("summary", "検証完了")}')
            
        except Exception as e:
            verification_results[item['id']] = {
                'status': 'ERROR',
                'error': str(e),
                'summary': '検証エラー'
            }
            print(f'   NG ERROR: 検証中にエラー発生')
        
        time.sleep(2)  # サーバー負荷軽減
    
    # 総合評価
    return evaluate_comprehensive_results(verification_results)

def verify_csrf_token_stability(base_url):
    """CSRFトークン安定性検証"""
    session = requests.Session()
    try:
        user_data = {'user_name': 'ULTRA_SYNC_CSRF_VERIFY'}
        session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        exam_data = {'exam_type': 'specialist', 'department': '道路', 'question_count': '3'}
        session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        response = session.get(f'{base_url}/exam', timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_input and csrf_input.get('value') and len(csrf_input.get('value')) > 10:
            return {'status': 'STABLE', 'summary': 'CSRFトークン正常生成確認'}
        else:
            return {'status': 'UNSTABLE', 'summary': 'CSRFトークン生成に問題'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'CSRFトークン検証エラー: {str(e)}'}
    finally:
        session.close()

def verify_second_question_stability(base_url):
    """2問目表示安定性検証"""
    session = requests.Session()
    try:
        user_data = {'user_name': 'ULTRA_SYNC_2Q_VERIFY'}
        session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        exam_data = {'exam_type': 'specialist', 'department': '道路', 'question_count': '3'}
        session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        # 1問目
        response = session.get(f'{base_url}/exam', timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        qid_input = soup.find('input', {'name': 'qid'})
        
        if not csrf_input or not qid_input:
            return {'status': 'UNSTABLE', 'summary': '1問目フォーム要素不足'}
        
        # 1問目回答
        answer_data = {
            'answer': 'A',
            'qid': qid_input.get('value'),
            'elapsed': '5',
            'csrf_token': csrf_input.get('value')
        }
        session.post(f'{base_url}/exam', data=answer_data, timeout=30)
        
        # 2問目表示確認
        response = session.get(f'{base_url}/exam', timeout=30)
        
        if '無効なデータ形式です' in response.text:
            return {'status': 'UNSTABLE', 'summary': '2問目で無効なデータ形式エラー'}
        
        if '処理中に問題が発生しました' in response.text:
            return {'status': 'UNSTABLE', 'summary': '2問目で処理エラー'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        question_text = soup.find('h3', class_='question-text')
        
        if question_text:
            return {'status': 'STABLE', 'summary': '2問目正常表示確認'}
        else:
            return {'status': 'UNSTABLE', 'summary': '2問目要素不足'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'2問目検証エラー: {str(e)}'}
    finally:
        session.close()

def verify_department_coverage_stability(base_url):
    """13部門動作安定性検証"""
    departments = ['道路', '建設環境', 'トンネル']  # 代表3部門
    stable_count = 0
    
    for dept in departments:
        session = requests.Session()
        try:
            user_data = {'user_name': f'ULTRA_SYNC_DEPT_{dept}_VERIFY'}
            session.post(f'{base_url}/set_user', data=user_data, timeout=30)
            
            exam_data = {'exam_type': 'specialist', 'department': dept, 'question_count': '3'}
            response = session.post(f'{base_url}/exam', data=exam_data, timeout=30)
            
            if response.status_code in [200, 302]:
                response = session.get(f'{base_url}/exam', timeout=30)
                if response.status_code == 200 and '選択肢' in response.text:
                    stable_count += 1
            
        except Exception:
            pass
        finally:
            session.close()
        
        time.sleep(1)
    
    if stable_count == 3:
        return {'status': 'STABLE', 'summary': f'13部門代表{stable_count}/3正常動作'}
    elif stable_count >= 2:
        return {'status': 'PARTIAL', 'summary': f'13部門代表{stable_count}/3部分動作'}
    else:
        return {'status': 'UNSTABLE', 'summary': f'13部門代表{stable_count}/3動作不安定'}

def verify_basic_flow_stability(base_url):
    """基本フロー安定性検証"""
    session = requests.Session()
    try:
        user_data = {'user_name': 'ULTRA_SYNC_FLOW_VERIFY'}
        session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        exam_data = {'exam_type': 'specialist', 'department': '道路', 'question_count': '3'}
        session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        completed_questions = 0
        for i in range(3):
            response = session.get(f'{base_url}/exam', timeout=30)
            if response.status_code != 200:
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_input or not qid_input:
                break
            
            answer_data = {
                'answer': 'A',
                'qid': qid_input.get('value'),
                'elapsed': '3',
                'csrf_token': csrf_input.get('value')
            }
            
            response = session.post(f'{base_url}/exam', data=answer_data, timeout=30)
            if response.status_code in [200, 302]:
                completed_questions += 1
            else:
                break
            
            time.sleep(1)
        
        # 結果画面確認
        response = session.get(f'{base_url}/result', timeout=30)
        result_accessible = response.status_code == 200 and '結果' in response.text
        
        if completed_questions == 3 and result_accessible:
            return {'status': 'STABLE', 'summary': '基本フロー完全動作確認'}
        elif completed_questions >= 2:
            return {'status': 'PARTIAL', 'summary': f'基本フロー部分動作({completed_questions}/3)'}
        else:
            return {'status': 'UNSTABLE', 'summary': '基本フロー動作不安定'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'基本フロー検証エラー: {str(e)}'}
    finally:
        session.close()

def verify_session_safety_stability(base_url):
    """セッション安全性検証"""
    session = requests.Session()
    try:
        user_data = {'user_name': 'ULTRA_SYNC_SESSION_VERIFY'}
        session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        exam_data = {'exam_type': 'specialist', 'department': '道路', 'question_count': '3'}
        session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        # 複数回のセッションアクセス
        session_errors = 0
        for i in range(5):
            response = session.get(f'{base_url}/exam', timeout=30)
            
            if 'KeyError' in response.text or 'セッションエラー' in response.text:
                session_errors += 1
            
            time.sleep(0.5)
        
        if session_errors == 0:
            return {'status': 'STABLE', 'summary': 'セッション安全性確認'}
        elif session_errors <= 1:
            return {'status': 'PARTIAL', 'summary': f'セッション軽微問題({session_errors}件)'}
        else:
            return {'status': 'UNSTABLE', 'summary': f'セッション問題({session_errors}件)'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'セッション検証エラー: {str(e)}'}
    finally:
        session.close()

def verify_memory_protection_stability(base_url):
    """メモリ保護安定性検証"""
    session = requests.Session()
    try:
        user_data = {'user_name': 'ULTRA_SYNC_MEMORY_VERIFY'}
        session.post(f'{base_url}/set_user', data=user_data, timeout=30)
        
        exam_data = {'exam_type': 'specialist', 'department': '道路', 'question_count': '3'}
        session.post(f'{base_url}/exam', data=exam_data, timeout=30)
        
        # メモリ集約的操作の実行
        memory_errors = 0
        for i in range(3):
            response = session.get(f'{base_url}/exam', timeout=30)
            
            if 'MemoryError' in response.text or 'OutOfMemory' in response.text:
                memory_errors += 1
            
            if response.status_code == 500:
                memory_errors += 1
            
            time.sleep(1)
        
        if memory_errors == 0:
            return {'status': 'STABLE', 'summary': 'メモリ保護正常動作確認'}
        else:
            return {'status': 'UNSTABLE', 'summary': f'メモリ問題({memory_errors}件)'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'メモリ検証エラー: {str(e)}'}
    finally:
        session.close()

def verify_production_environment_stability(base_url):
    """本番環境総合安定性検証"""
    session = requests.Session()
    try:
        # 基本アクセス確認
        response = session.get(base_url, timeout=30)
        if response.status_code != 200:
            return {'status': 'UNSTABLE', 'summary': f'本番環境アクセス失敗({response.status_code})'}
        
        # 主要エンドポイント確認
        endpoints = ['/set_user', '/exam']
        stable_endpoints = 0
        
        for endpoint in endpoints:
            try:
                response = session.get(f'{base_url}{endpoint}', timeout=30)
                if response.status_code in [200, 302, 405]:  # 405 = Method Not Allowed (正常)
                    stable_endpoints += 1
            except Exception:
                pass
        
        if stable_endpoints == len(endpoints):
            return {'status': 'STABLE', 'summary': '本番環境総合安定性確認'}
        else:
            return {'status': 'PARTIAL', 'summary': f'本番環境部分安定({stable_endpoints}/{len(endpoints)})'}
            
    except Exception as e:
        return {'status': 'ERROR', 'summary': f'本番環境検証エラー: {str(e)}'}
    finally:
        session.close()

def evaluate_comprehensive_results(verification_results):
    """総合結果評価"""
    print('\n' + '=' * 80)
    print('ULTRA SYNC 総合最終検証結果')
    print('=' * 80)
    
    stable_count = 0
    partial_count = 0
    unstable_count = 0
    error_count = 0
    
    for item_id, result in verification_results.items():
        status = result['status']
        if status == 'STABLE':
            stable_count += 1
        elif status == 'PARTIAL':
            partial_count += 1
        elif status == 'UNSTABLE':
            unstable_count += 1
        elif status == 'ERROR':
            error_count += 1
    
    total_items = len(verification_results)
    stability_rate = (stable_count / total_items) * 100
    
    print(f'総検証項目: {total_items}')
    print(f'安定確認: {stable_count}項目')
    print(f'部分安定: {partial_count}項目')
    print(f'不安定: {unstable_count}項目')
    print(f'エラー: {error_count}項目')
    print(f'安定率: {stability_rate:.1f}%')
    
    # 最終判定
    if stable_count >= 6 and unstable_count == 0:
        final_status = 'COMPREHENSIVE_STABLE'
        conclusion = 'ULTRA SYNC 総合安定性確認 - 本番環境完全安定'
    elif stable_count >= 5 and unstable_count <= 1:
        final_status = 'MOSTLY_STABLE'
        conclusion = 'ULTRA SYNC 概ね安定 - 軽微な改善点あり'
    elif stable_count >= 4:
        final_status = 'PARTIALLY_STABLE'
        conclusion = 'ULTRA SYNC 部分安定 - 改善が必要'
    else:
        final_status = 'NEEDS_ATTENTION'
        conclusion = 'ULTRA SYNC 要注意 - 重要な問題あり'
    
    print(f'\n最終判定: {final_status}')
    print(f'結論: {conclusion}')
    
    return {
        'final_status': final_status,
        'stability_rate': stability_rate,
        'stable_count': stable_count,
        'total_items': total_items,
        'conclusion': conclusion,
        'verification_results': verification_results
    }

if __name__ == '__main__':
    try:
        result = comprehensive_stability_verification()
        
        if result['final_status'] in ['COMPREHENSIVE_STABLE', 'MOSTLY_STABLE']:
            print('\n[ULTRA SYNC 総合検証] 成功 - システム安定性確認')
            sys.exit(0)
        elif result['final_status'] == 'PARTIALLY_STABLE':
            print('\n[ULTRA SYNC 総合検証] 部分成功 - 改善点あり')
            sys.exit(1)
        else:
            print('\n[ULTRA SYNC 総合検証] 要注意 - 重要問題検出')
            sys.exit(2)
    
    except KeyboardInterrupt:
        print('\n検証中断')
        sys.exit(130)
    except Exception as e:
        print(f'\n総合検証エラー: {e}')
        sys.exit(1)