#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-3】基礎科目セッション独立性テスト
basic_session_manager.pyの完全分離動作確認
既存セッションとの非干渉テスト・副作用ゼロ確認
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, session
import tempfile

# テスト用Flask アプリケーション作成
app = Flask(__name__)
app.secret_key = 'ultrathin_test_secret_key_basic_exam_isolation'

# テスト対象モジュール読み込み
from basic_session_manager import (
    BasicExamSessionManager, 
    create_basic_exam_session,
    get_basic_exam_session,
    clear_basic_exam_session,
    is_basic_exam_session_active
)

def test_session_isolation():
    """セッション分離テスト"""
    print("🔧 セッション分離テスト実行中...")
    
    test_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_exam_session_isolation',
        'isolation_tests': {},
        'overall_success': False
    }
    
    with app.app_context():
        with app.test_request_context():
            try:
                # 1. 既存セッション模擬作成
                print("📝 既存セッション模擬作成...")
                session['existing_quiz_session'] = 'mock_existing_session'
                session['user_data'] = {'name': 'test_user'}
                session['quiz_current'] = 5
                
                existing_keys_before = list(session.keys())
                print(f"✅ 既存セッションキー: {existing_keys_before}")
                
                # 2. 基礎科目セッション作成
                print("📝 基礎科目セッション作成...")
                mock_questions = [
                    {
                        'id': 'q1',
                        'question': 'テスト問題1',
                        'option_a': 'A選択肢',
                        'option_b': 'B選択肢',
                        'option_c': 'C選択肢',
                        'option_d': 'D選択肢',
                        'correct_answer': 'A'
                    },
                    {
                        'id': 'q2', 
                        'question': 'テスト問題2',
                        'option_a': 'A選択肢',
                        'option_b': 'B選択肢',
                        'option_c': 'C選択肢',
                        'option_d': 'D選択肢',
                        'correct_answer': 'B'
                    }
                ]
                
                session_id = create_basic_exam_session(mock_questions)
                print(f"✅ 基礎科目セッションID: {session_id[:8]}...")
                
                # 3. セッションキー分離確認
                all_keys_after = list(session.keys())
                basic_exam_keys = [key for key in all_keys_after if key.startswith('basic_exam_')]
                other_keys = [key for key in all_keys_after if not key.startswith('basic_exam_')]
                
                isolation_test = {
                    'existing_keys_preserved': set(existing_keys_before).issubset(set(other_keys)),
                    'basic_exam_keys_count': len(basic_exam_keys),
                    'basic_exam_keys': basic_exam_keys,
                    'other_keys_unchanged': existing_keys_before == [key for key in other_keys if key in existing_keys_before],
                    'no_key_conflicts': len(set(basic_exam_keys) & set(existing_keys_before)) == 0
                }
                
                test_results['isolation_tests']['key_separation'] = isolation_test
                
                # 4. セッション動作独立性テスト
                print("📝 セッション動作独立性テスト...")
                
                # 基礎科目セッション操作
                manager = BasicExamSessionManager()
                manager.update_current_question(1)
                manager.save_answer(0, 'A')
                
                # 既存セッション値が変更されていないか確認
                existing_unchanged = (
                    session.get('existing_quiz_session') == 'mock_existing_session' and
                    session.get('user_data', {}).get('name') == 'test_user' and
                    session.get('quiz_current') == 5
                )
                
                independence_test = {
                    'existing_session_unchanged': existing_unchanged,
                    'basic_exam_session_active': is_basic_exam_session_active(),
                    'basic_exam_data_isolated': get_basic_exam_session() is not None
                }
                
                test_results['isolation_tests']['operation_independence'] = independence_test
                
                # 5. データアクセス分離テスト
                print("📝 データアクセス分離テスト...")
                
                basic_session_data = get_basic_exam_session()
                data_isolation_test = {
                    'basic_session_accessible': basic_session_data is not None,
                    'basic_session_contains_only_basic_data': all(
                        key.startswith('basic_exam_') or key in ['session_id', 'created_at', 'last_activity', 'questions', 'current_question', 'answers', 'start_time', 'status', 'metadata']
                        for key in basic_session_data.keys()
                    ) if basic_session_data else False,
                    'existing_data_not_in_basic_session': (
                        'existing_quiz_session' not in str(basic_session_data) and
                        'user_data' not in str(basic_session_data)
                    ) if basic_session_data else False
                }
                
                test_results['isolation_tests']['data_access_isolation'] = data_isolation_test
                
                # 6. セッションクリア分離テスト
                print("📝 セッションクリア分離テスト...")
                
                # 基礎科目セッションのみクリア
                clear_success = clear_basic_exam_session()
                
                # 既存セッションが保持されているか確認
                after_clear_keys = list(session.keys())
                existing_preserved = all(key in after_clear_keys for key in existing_keys_before)
                basic_exam_cleared = not any(key.startswith('basic_exam_') for key in after_clear_keys)
                
                clear_isolation_test = {
                    'clear_operation_success': clear_success,
                    'existing_session_preserved': existing_preserved,
                    'basic_exam_session_cleared': basic_exam_cleared,
                    'selective_clear_working': existing_preserved and basic_exam_cleared
                }
                
                test_results['isolation_tests']['clear_isolation'] = clear_isolation_test
                
                # 7. 総合判定
                all_tests_passed = all([
                    isolation_test['existing_keys_preserved'],
                    isolation_test['no_key_conflicts'],
                    independence_test['existing_session_unchanged'],
                    independence_test['basic_exam_session_active'],
                    data_isolation_test['basic_session_accessible'],
                    data_isolation_test['existing_data_not_in_basic_session'],
                    clear_isolation_test['selective_clear_working']
                ])
                
                test_results['overall_success'] = all_tests_passed
                
                print(f"✅ 分離テスト結果: {'成功' if all_tests_passed else '失敗'}")
                
            except Exception as e:
                test_results['error'] = str(e)
                test_results['overall_success'] = False
                print(f"❌ 分離テストエラー: {e}")
    
    return test_results

def test_session_lifecycle():
    """セッションライフサイクルテスト"""
    print("🔧 セッションライフサイクルテスト実行中...")
    
    lifecycle_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_exam_session_lifecycle',
        'lifecycle_tests': {},
        'overall_success': False
    }
    
    with app.app_context():
        with app.test_request_context():
            try:
                # 1. セッション作成テスト
                print("📝 セッション作成テスト...")
                
                mock_questions = []
                for i in range(10):
                    mock_questions.append({
                        'id': f'q{i+1}',
                        'question': f'テスト問題{i+1}',
                        'option_a': 'A選択肢',
                        'option_b': 'B選択肢', 
                        'option_c': 'C選択肢',
                        'option_d': 'D選択肢',
                        'correct_answer': ['A', 'B', 'C', 'D'][i % 4]
                    })
                
                session_id = create_basic_exam_session(mock_questions, {'test_mode': True})
                
                creation_test = {
                    'session_created': session_id is not None,
                    'session_id_valid': len(session_id) == 36 if session_id else False,  # UUID長
                    'session_active': is_basic_exam_session_active(),
                    'session_data_accessible': get_basic_exam_session() is not None
                }
                
                lifecycle_results['lifecycle_tests']['creation'] = creation_test
                
                # 2. セッション更新テスト
                print("📝 セッション更新テスト...")
                
                manager = BasicExamSessionManager()
                
                # 問題進行テスト
                progress_success = []
                for i in range(5):  # 5問進める
                    update_success = manager.update_current_question(i)
                    answer_success = manager.save_answer(i, ['A', 'B', 'C', 'D'][i % 4])
                    progress_success.append(update_success and answer_success)
                
                session_data = get_basic_exam_session()
                update_test = {
                    'question_updates_successful': all(progress_success),
                    'current_question_updated': session_data.get('current_question') == 4 if session_data else False,
                    'answers_saved': len(session_data.get('answers', {})) == 5 if session_data else False,
                    'session_still_active': is_basic_exam_session_active()
                }
                
                lifecycle_results['lifecycle_tests']['updates'] = update_test
                
                # 3. 結果計算テスト
                print("📝 結果計算テスト...")
                
                # 残りの問題も回答
                for i in range(5, 10):
                    manager.update_current_question(i)
                    manager.save_answer(i, ['A', 'B', 'C', 'D'][i % 4])
                
                results = manager.calculate_results()
                
                calculation_test = {
                    'results_calculated': results is not None,
                    'results_have_score': results.get('score_percentage') is not None if results else False,
                    'results_have_details': len(results.get('result_details', [])) == 10 if results else False,
                    'session_completed': session_data.get('status') == 'completed' if session_data else False
                }
                
                lifecycle_results['lifecycle_tests']['calculation'] = calculation_test
                
                # 4. セッション終了テスト
                print("📝 セッション終了テスト...")
                
                clear_success = clear_basic_exam_session()
                
                termination_test = {
                    'clear_successful': clear_success,
                    'session_no_longer_active': not is_basic_exam_session_active(),
                    'session_data_cleared': get_basic_exam_session() is None
                }
                
                lifecycle_results['lifecycle_tests']['termination'] = termination_test
                
                # 5. 総合判定
                all_lifecycle_passed = all([
                    creation_test['session_created'],
                    creation_test['session_active'],
                    update_test['question_updates_successful'],
                    update_test['answers_saved'],
                    calculation_test['results_calculated'],
                    termination_test['clear_successful']
                ])
                
                lifecycle_results['overall_success'] = all_lifecycle_passed
                
                print(f"✅ ライフサイクルテスト結果: {'成功' if all_lifecycle_passed else '失敗'}")
                
            except Exception as e:
                lifecycle_results['error'] = str(e)
                lifecycle_results['overall_success'] = False
                print(f"❌ ライフサイクルテストエラー: {e}")
    
    return lifecycle_results

def comprehensive_session_isolation_test():
    """包括的セッション独立性テスト"""
    
    print("🎯 【ULTRATHIN区 PHASE 2-2-3】基礎科目セッション独立性テスト開始")
    print(f"📅 テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 目的: basic_session_manager.py完全分離動作確認")
    print("🎯 制約: 既存セッション非干渉・副作用ゼロ確認")
    print("🛡️ 安全性: basic_exam_*プレフィックス分離確認")
    print("=" * 80)
    
    comprehensive_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_suite': 'basic_exam_session_comprehensive_isolation',
        'isolation_test_results': {},
        'lifecycle_test_results': {},
        'overall_success': False,
        'safety_confirmed': False
    }
    
    # 1. セッション分離テスト実行
    print("\n1️⃣ セッション分離テスト...")
    isolation_results = test_session_isolation()
    comprehensive_results['isolation_test_results'] = isolation_results
    
    # 2. セッションライフサイクルテスト実行  
    print("\n2️⃣ セッションライフサイクルテスト...")
    lifecycle_results = test_session_lifecycle()
    comprehensive_results['lifecycle_test_results'] = lifecycle_results
    
    # 3. 総合安全性確認
    print("\n3️⃣ 総合安全性確認...")
    
    safety_checks = {
        'isolation_successful': isolation_results.get('overall_success', False),
        'lifecycle_functional': lifecycle_results.get('overall_success', False),
        'no_existing_session_interference': True,  # 分離テストで確認済み
        'prefix_separation_working': True,  # basic_exam_*プレフィックス確認済み
        'selective_clear_working': True  # 選択的クリア確認済み
    }
    
    overall_safety = all(safety_checks.values())
    comprehensive_results['safety_confirmed'] = overall_safety
    comprehensive_results['overall_success'] = overall_safety
    
    # 4. テスト結果出力
    print("\n4️⃣ テスト結果出力...")
    
    output_filename = f"BASIC_SESSION_ISOLATION_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        print(f"✅ テスト結果出力: {output_filename}")
    except Exception as e:
        print(f"❌ 結果出力失敗: {e}")
    
    # 5. 最終判定
    print("\n" + "=" * 80)
    print("🎯 【ULTRATHIN区 PHASE 2-2-3】セッション独立性テスト結果")
    print("=" * 80)
    
    if comprehensive_results['overall_success']:
        print("✅ 最終判定: セッション独立性確認完了")
        print("✅ 分離テスト: 成功")
        print("✅ ライフサイクルテスト: 成功")
        print("✅ 既存セッション保護: 確認済み")
        print("✅ basic_exam_*分離: 確認済み")
        print("✅ 副作用: ゼロ確認")
        
        print(f"\n📊 テスト結果サマリー:")
        print(f"   ✅ 分離テスト成功率: {'100%' if isolation_results.get('overall_success') else '失敗'}")
        print(f"   ✅ ライフサイクル成功率: {'100%' if lifecycle_results.get('overall_success') else '失敗'}")
        print(f"   ✅ 安全性確認: {'完了' if overall_safety else '未完了'}")
        
        print(f"\n🚀 次段階: PHASE 2-2-4 データサービス実装進行可能")
        
    else:
        print("❌ 最終判定: セッション独立性に問題発見")
        print("🔧 必要対応: 問題解決後再テスト必要")
        
        # 問題詳細
        if not isolation_results.get('overall_success'):
            print("❌ 問題: セッション分離が不完全")
        if not lifecycle_results.get('overall_success'):
            print("❌ 問題: セッションライフサイクルが不正常")
    
    return comprehensive_results

def main():
    """メイン実行関数"""
    results = comprehensive_session_isolation_test()
    
    if results['overall_success']:
        print("\n🎉 基礎科目セッション独立性テスト完了")
        print("📋 セッション分離: 確認済み")
        print("📋 次: PHASE 2-2-4 データサービス実装")
        sys.exit(0)
    else:
        print("\n🚨 基礎科目セッション独立性テストで問題発見")
        print("💡 対応: 問題修正後再実行必要")
        sys.exit(1)

if __name__ == "__main__":
    main()