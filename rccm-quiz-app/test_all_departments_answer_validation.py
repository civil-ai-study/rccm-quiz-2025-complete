#!/usr/bin/env python3
"""
全12部門での回答値検証エラーの包括的テスト
"""

import requests
import json
import time
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# テスト対象URL（本番環境）
BASE_URL = "https://rccm-quiz-2025.onrender.com"

# 全12部門のリスト
DEPARTMENTS = [
    ('road', '道路'),
    ('tunnel', 'トンネル'),
    ('civil_planning', '河川、砂防及び海岸・海洋'),
    ('urban_planning', '都市計画及び地方計画'),
    ('landscape', '造園'),
    ('construction_env', '建設環境'),
    ('steel_concrete', '鋼構造及びコンクリート'),
    ('soil_foundation', '土質及び基礎'),
    ('construction_planning', '施工計画、施工設備及び積算'),
    ('water_supply', '上水道及び工業用水道'),
    ('forestry', '森林土木'),
    ('agriculture', '農業土木')
]

def test_department_answer_validation(session, department_key, department_name):
    """特定部門での回答値検証をテスト"""
    logger.info(f"\n{'='*60}")
    logger.info(f"部門テスト開始: {department_name} ({department_key})")
    
    try:
        # 1. 部門選択画面にアクセス
        resp = session.get(f"{BASE_URL}/department_select/specialist")
        if resp.status_code != 200:
            logger.error(f"部門選択画面アクセス失敗: {resp.status_code}")
            return {
                'department': department_key,
                'name': department_name,
                'status': 'failed',
                'error': f'部門選択画面アクセス失敗: {resp.status_code}'
            }
        
        # 2. 試験開始（POSTメソッド）
        start_data = {
            'questions': '5',  # 5問でテスト
            'year': 'all'
        }
        resp = session.post(f"{BASE_URL}/start_exam/{department_key}", data=start_data)
        
        if resp.status_code != 200:
            logger.error(f"試験開始失敗: {resp.status_code}")
            return {
                'department': department_key,
                'name': department_name,
                'status': 'failed',
                'error': f'試験開始失敗: {resp.status_code}'
            }
        
        # 3. 5問回答してエラーをチェック
        errors = []
        successful_answers = 0
        
        for i in range(5):
            logger.info(f"問題 {i+1}/5 を回答中...")
            
            # 現在の問題ページを取得
            resp = session.get(f"{BASE_URL}/exam")
            if resp.status_code != 200:
                errors.append({
                    'question_number': i+1,
                    'error': f'問題ページアクセス失敗: {resp.status_code}'
                })
                break
            
            # 問題IDを抽出（簡易的な方法）
            html_content = resp.text
            qid_start = html_content.find('name="qid" value="') + len('name="qid" value="')
            if qid_start > len('name="qid" value="'):
                qid_end = html_content.find('"', qid_start)
                question_id = html_content[qid_start:qid_end]
            else:
                # 別の方法で試す
                question_id = str(1000 + i)  # ダミーID
            
            # 各種回答値でテスト
            test_answers = ['A', 'B', 'C', 'D']
            answer = test_answers[i % 4]
            
            # 回答を送信
            answer_data = {
                'qid': question_id,
                'answer': answer,
                'elapsed': '10'
            }
            
            resp = session.post(f"{BASE_URL}/submit_answer", data=answer_data)
            
            if resp.status_code != 200:
                errors.append({
                    'question_number': i+1,
                    'answer': answer,
                    'status_code': resp.status_code,
                    'error': 'HTTPエラー'
                })
            elif '無効な回答が選択されました' in resp.text:
                errors.append({
                    'question_number': i+1,
                    'answer': answer,
                    'error': '無効な回答エラー発生！'
                })
                logger.error(f"❌ エラー発生: 問題{i+1}で「無効な回答が選択されました」")
            else:
                successful_answers += 1
                logger.info(f"✅ 問題{i+1}の回答成功")
            
            time.sleep(0.5)  # サーバー負荷軽減
        
        # 結果をまとめる
        return {
            'department': department_key,
            'name': department_name,
            'status': 'completed',
            'total_questions': 5,
            'successful_answers': successful_answers,
            'errors': errors,
            'error_rate': len(errors) / 5 * 100
        }
        
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return {
            'department': department_key,
            'name': department_name,
            'status': 'error',
            'error': str(e)
        }


def run_comprehensive_test():
    """全部門の包括的テストを実行"""
    print(f"\n{'='*80}")
    print(f"全12部門回答検証テスト - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # セッション作成
    session = requests.Session()
    
    # 全部門の結果を格納
    all_results = []
    departments_with_errors = []
    
    # 各部門をテスト
    for dept_key, dept_name in DEPARTMENTS:
        result = test_department_answer_validation(session, dept_key, dept_name)
        all_results.append(result)
        
        if result.get('errors'):
            departments_with_errors.append(result)
        
        # サーバー負荷軽減のため待機
        time.sleep(2)
    
    # 結果サマリー
    print(f"\n{'='*80}")
    print("テスト結果サマリー")
    print(f"{'='*80}\n")
    
    total_departments = len(DEPARTMENTS)
    error_departments = len(departments_with_errors)
    success_departments = total_departments - error_departments
    
    print(f"テスト部門数: {total_departments}")
    print(f"成功: {success_departments} 部門")
    print(f"エラー: {error_departments} 部門")
    
    if departments_with_errors:
        print(f"\n{'='*60}")
        print("エラーが発生した部門の詳細")
        print(f"{'='*60}\n")
        
        for dept in departments_with_errors:
            print(f"\n部門: {dept['name']} ({dept['department']})")
            print(f"エラー率: {dept['error_rate']:.1f}%")
            print("エラー詳細:")
            for error in dept['errors']:
                print(f"  - 問題{error['question_number']}: {error['error']}")
    else:
        print("\n✅ すべての部門でエラーは発生しませんでした！")
    
    # 結果をJSONファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_filename = f'all_departments_test_result_{timestamp}.json'
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'total_departments': total_departments,
            'success_departments': success_departments,
            'error_departments': error_departments,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果を {result_filename} に保存しました。")
    
    return all_results


if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\nテストが中断されました。")
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()