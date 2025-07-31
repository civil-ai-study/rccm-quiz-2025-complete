#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC エラー位置精密特定
どの関数・処理でTypeErrorが発生しているかを特定
"""

import requests
import re
from datetime import datetime

def test_individual_routes():
    """個別ルートでの型エラー発生箇所特定"""
    print("ULTRA SYNC エラー位置精密特定")
    print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    session = requests.Session()
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    test_results = {}
    
    # テスト1: start_examのみ
    print("\n1. start_exam単体テスト")
    try:
        start_url = f"{base_url}/start_exam/河川・砂防"
        start_data = {"questions": 1, "year": "2018"}
        
        start_response = session.post(start_url, data=start_data, timeout=30)
        
        if "not supported between instances" in start_response.text:
            test_results['start_exam'] = 'ERROR'
            print("  結果: start_examでエラー発生")
        else:
            test_results['start_exam'] = 'OK'
            print("  結果: start_examは正常")
    except Exception as e:
        test_results['start_exam'] = f'EXCEPTION: {e}'
        print(f"  結果: start_examで例外 - {e}")
    
    # テスト2: examルートの直接アクセス（セッション設定後）
    print("\n2. examルート直接テスト")
    try:
        exam_url = f"{base_url}/exam"
        exam_response = session.get(exam_url, timeout=30)
        
        if "not supported between instances" in exam_response.text:
            test_results['exam_direct'] = 'ERROR'
            print("  結果: examルートでエラー発生")
        else:
            test_results['exam_direct'] = 'OK'
            print("  結果: examルートは正常")
    except Exception as e:
        test_results['exam_direct'] = f'EXCEPTION: {e}'
        print(f"  結果: examルートで例外 - {e}")
    
    # テスト3: 基礎科目での同様テスト（比較用）
    print("\n3. 基礎科目比較テスト")
    try:
        basic_session = requests.Session()
        basic_start_url = f"{base_url}/start_exam/基礎科目"
        basic_start_data = {"questions": 1, "year": ""}
        
        basic_start_response = basic_session.post(basic_start_url, data=basic_start_data, timeout=30)
        
        if "not supported between instances" in basic_start_response.text:
            test_results['basic_start'] = 'ERROR'
            print("  結果: 基礎科目start_examでもエラー発生")
        else:
            test_results['basic_start'] = 'OK'
            print("  結果: 基礎科目start_examは正常")
            
            # 基礎科目のexamルート
            basic_exam_response = basic_session.get(f"{base_url}/exam", timeout=30)
            if "not supported between instances" in basic_exam_response.text:
                test_results['basic_exam'] = 'ERROR'
                print("  結果: 基礎科目examルートでもエラー発生")
            else:
                test_results['basic_exam'] = 'OK'
                print("  結果: 基礎科目examルートは正常")
                
    except Exception as e:
        test_results['basic_test'] = f'EXCEPTION: {e}'
        print(f"  結果: 基礎科目テストで例外 - {e}")
    
    return test_results

def analyze_error_pattern(test_results):
    """エラーパターンの分析"""
    print(f"\n4. エラーパターン分析")
    
    print("  テスト結果:")
    for test_name, result in test_results.items():
        print(f"    {test_name}: {result}")
    
    # パターン分析
    error_count = sum(1 for result in test_results.values() if result == 'ERROR')
    ok_count = sum(1 for result in test_results.values() if result == 'OK')
    
    print(f"\n  エラー発生: {error_count}箇所")
    print(f"  正常動作: {ok_count}箇所")
    
    if error_count > 0:
        if 'start_exam' in test_results and test_results['start_exam'] == 'ERROR':
            print("  判定: start_exam関数内に未修正の型エラー")
            return 'start_exam_error'
        elif 'exam_direct' in test_results and test_results['exam_direct'] == 'ERROR':
            print("  判定: exam関数内に未修正の型エラー")
            return 'exam_error'
        else:
            print("  判定: その他の箇所に型エラー")
            return 'other_error'
    else:
        print("  判定: 型エラー解決済みまたは別問題")
        return 'resolved_or_other'

def suggest_next_action(error_pattern):
    """次のアクション提案"""
    print(f"\n5. 次のアクション提案")
    
    if error_pattern == 'start_exam_error':
        print("  推奨アクション:")
        print("    1. start_exam関数内の詳細調査")
        print("    2. 専門科目データ読み込み処理の確認")
        print("    3. セッション初期化処理の型安全化")
        return ['check_start_exam_function', 'check_data_loading', 'check_session_init']
        
    elif error_pattern == 'exam_error':
        print("  推奨アクション:")
        print("    1. exam関数内の未修正箇所特定")
        print("    2. 問題データ取得処理の確認")
        print("    3. セッション状態判定処理の型安全化")
        return ['check_exam_function', 'check_question_retrieval', 'check_session_state']
        
    elif error_pattern == 'resolved_or_other':
        print("  推奨アクション:")
        print("    1. キャッシュクリア後の再テスト")
        print("    2. 別の部門での動作確認")
        print("    3. ブラウザキャッシュ確認")
        return ['cache_clear', 'test_other_departments', 'browser_cache_check']
        
    else:
        print("  推奨アクション:")
        print("    1. より詳細なエラートレース")
        print("    2. ログファイルの確認")
        print("    3. サーバーサイドデバッグ")
        return ['detailed_trace', 'log_check', 'server_debug']

def main():
    print("ULTRA SYNC エラー位置精密特定システム")
    print("目的: TypeError発生箇所のピンポイント特定")
    print("=" * 60)
    
    # テスト実行
    test_results = test_individual_routes()
    
    # パターン分析
    error_pattern = analyze_error_pattern(test_results)
    
    # 次アクション提案
    suggested_actions = suggest_next_action(error_pattern)
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 精密特定結果")
    print("=" * 60)
    
    print(f"エラーパターン: {error_pattern}")
    print(f"提案アクション数: {len(suggested_actions)}")
    print("推奨優先順位: 上記リスト順")
    
    return error_pattern, suggested_actions

if __name__ == "__main__":
    main()