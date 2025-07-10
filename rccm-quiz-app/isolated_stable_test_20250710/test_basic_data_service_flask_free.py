#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービスFlask非依存テスト
basic_data_service.py単体動作確認・Flask環境なしでの検証
"""

import sys
import os
import json
from datetime import datetime

def test_basic_data_service_standalone():
    """基礎科目データサービス単体テスト"""
    print("🔧 基礎科目データサービス単体テスト実行中...")
    
    test_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_data_service_standalone_flask_free',
        'standalone_tests': {},
        'overall_success': False
    }
    
    try:
        # モジュール読み込みテスト
        import_test = {}
        try:
            from basic_data_service import (
                BasicDataService, 
                SecurityError,
                validate_basic_exam_answer,
                get_basic_data_service_info
            )
            import_test['module_import_successful'] = True
            import_test['classes_available'] = True
        except Exception as e:
            import_test['module_import_successful'] = False
            import_test['import_error'] = str(e)
        
        test_results['standalone_tests']['import'] = import_test
        
        if not import_test.get('module_import_successful'):
            test_results['overall_success'] = False
            return test_results
        
        # データサービスインスタンス作成
        service = BasicDataService()
        
        # 1. セキュリティチェックテスト
        security_test = {}
        try:
            service._validate_file_access_security()
            security_test['access_validation_passed'] = True
            security_test['security_check_successful'] = True
        except Exception as e:
            security_test['access_validation_passed'] = False
            security_test['security_error'] = str(e)
        
        test_results['standalone_tests']['security'] = security_test
        
        # 2. データ読み込みテスト
        data_loading_test = {}
        try:
            questions = service.load_basic_questions()
            data_loading_test['questions_loaded'] = True
            data_loading_test['questions_count'] = len(questions)
            data_loading_test['sample_question_structure'] = list(questions[0].keys()) if questions else []
            data_loading_test['all_questions_have_required_fields'] = all(
                all(field in q for field in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'])
                for q in questions
            ) if questions else False
        except Exception as e:
            data_loading_test['questions_loaded'] = False
            data_loading_test['loading_error'] = str(e)
        
        test_results['standalone_tests']['data_loading'] = data_loading_test
        
        # 3. 問題選択テスト
        question_selection_test = {}
        try:
            if data_loading_test.get('questions_loaded'):
                # 10問選択テスト
                session_questions_10 = service.get_questions_for_session(10, randomize=True)
                question_selection_test['selection_10_successful'] = len(session_questions_10) == 10
                
                # ランダム性確認（2回実行して異なる順序であることを確認）
                session_questions_10_b = service.get_questions_for_session(10, randomize=True)
                question_selection_test['randomization_working'] = (
                    [q['question'] for q in session_questions_10] != [q['question'] for q in session_questions_10_b]
                )
                
                # 順序固定テスト
                session_questions_fixed = service.get_questions_for_session(10, randomize=False)
                question_selection_test['fixed_order_working'] = len(session_questions_fixed) == 10
                
                # メタデータ付与確認
                question_selection_test['session_order_added'] = all(
                    'session_order' in q and 'question_id' in q for q in session_questions_10
                )
            else:
                question_selection_test['selection_10_successful'] = False
                question_selection_test['reason'] = 'questions_not_loaded'
        except Exception as e:
            question_selection_test['selection_10_successful'] = False
            question_selection_test['selection_error'] = str(e)
        
        test_results['standalone_tests']['question_selection'] = question_selection_test
        
        # 4. 回答検証テスト
        answer_validation_test = {}
        try:
            valid_answers = ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']  # 大文字小文字両方
            invalid_answers = ['E', 'F', '1', '2', 'あ', 'い', '', None, 123]
            
            valid_results = [validate_basic_exam_answer(str(answer)) for answer in valid_answers]
            invalid_results = [validate_basic_exam_answer(str(answer)) if answer is not None else False for answer in invalid_answers]
            
            answer_validation_test['all_valid_accepted'] = all(valid_results)
            answer_validation_test['all_invalid_rejected'] = not any(invalid_results)
            answer_validation_test['case_insensitive_working'] = all(valid_results[:8])  # A-D, a-d
        except Exception as e:
            answer_validation_test['all_valid_accepted'] = False
            answer_validation_test['validation_error'] = str(e)
        
        test_results['standalone_tests']['answer_validation'] = answer_validation_test
        
        # 5. キャッシュ機能テスト
        cache_test = {}
        try:
            # キャッシュクリア
            service.questions_cache = None
            service.cache_timestamp = None
            
            # 初回読み込み
            start_time = datetime.now()
            questions_1 = service.load_basic_questions()
            first_load_time = (datetime.now() - start_time).total_seconds()
            
            # 2回目読み込み（キャッシュ使用）
            start_time = datetime.now()
            questions_2 = service.load_basic_questions()
            second_load_time = (datetime.now() - start_time).total_seconds()
            
            # キャッシュが動作していることを確認（時間は微小差でも良い）
            cache_test['cache_working'] = (
                second_load_time <= first_load_time and  # 2回目は同等以下の時間
                service._is_cache_valid() and  # キャッシュが有効
                service.questions_cache is not None  # キャッシュデータが存在
            )
            cache_test['data_consistency'] = len(questions_1) == len(questions_2)
            cache_test['first_load_time'] = first_load_time
            cache_test['second_load_time'] = second_load_time
            cache_test['cache_valid'] = service._is_cache_valid()
        except Exception as e:
            cache_test['cache_working'] = False
            cache_test['cache_error'] = str(e)
        
        test_results['standalone_tests']['cache'] = cache_test
        
        # 6. エラーハンドリングテスト
        error_handling_test = {}
        try:
            # 不正な問題数要求
            try:
                service.get_questions_for_session(0)
                error_handling_test['zero_questions_handled'] = False
            except ValueError:
                error_handling_test['zero_questions_handled'] = True
            
            # 過大な問題数要求
            available_count = len(service.load_basic_questions())
            try:
                service.get_questions_for_session(available_count + 100)
                error_handling_test['excessive_questions_handled'] = False
            except ValueError:
                error_handling_test['excessive_questions_handled'] = True
            
            error_handling_test['error_handling_working'] = (
                error_handling_test['zero_questions_handled'] and
                error_handling_test['excessive_questions_handled']
            )
        except Exception as e:
            error_handling_test['error_handling_working'] = False
            error_handling_test['error_handling_error'] = str(e)
        
        test_results['standalone_tests']['error_handling'] = error_handling_test
        
        # 7. 総合判定
        all_tests_passed = all([
            import_test.get('module_import_successful', False),
            security_test.get('access_validation_passed', False),
            data_loading_test.get('questions_loaded', False),
            question_selection_test.get('selection_10_successful', False),
            answer_validation_test.get('all_valid_accepted', False),
            answer_validation_test.get('all_invalid_rejected', False),
            cache_test.get('cache_working', False),
            error_handling_test.get('error_handling_working', False)
        ])
        
        test_results['overall_success'] = all_tests_passed
        
        # 成功率計算
        total_checks = 8
        passed_checks = sum([
            import_test.get('module_import_successful', False),
            security_test.get('access_validation_passed', False),
            data_loading_test.get('questions_loaded', False),
            question_selection_test.get('selection_10_successful', False),
            answer_validation_test.get('all_valid_accepted', False),
            answer_validation_test.get('all_invalid_rejected', False),
            cache_test.get('cache_working', False),
            error_handling_test.get('error_handling_working', False)
        ])
        
        test_results['success_rate'] = (passed_checks / total_checks) * 100
        test_results['passed_checks'] = passed_checks
        test_results['total_checks'] = total_checks
        
        print(f"✅ 単体テスト結果: {test_results['success_rate']:.1f}% ({passed_checks}/{total_checks})")
        
    except Exception as e:
        test_results['error'] = str(e)
        test_results['overall_success'] = False
        print(f"❌ 単体テストエラー: {e}")
    
    return test_results

def comprehensive_flask_free_data_service_test():
    """包括的Flask非依存データサービステスト"""
    
    print("🎯 【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービスFlask非依存テスト開始")
    print(f"📅 テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 目的: basic_data_service.py単体動作確認")
    print("🎯 範囲: モジュール読み込み・データ処理・キャッシュ・エラーハンドリング")
    print("🛡️ 安全性: Flask環境なし・基礎科目専用・既存システム影響ゼロ")
    print("=" * 80)
    
    comprehensive_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_suite': 'basic_data_service_flask_free_comprehensive',
        'standalone_test_results': {},
        'overall_success': False,
        'implementation_quality': 'unknown'
    }
    
    # 1. 単体テスト実行
    print("\n1️⃣ 基礎科目データサービス単体テスト...")
    standalone_results = test_basic_data_service_standalone()
    comprehensive_results['standalone_test_results'] = standalone_results
    
    # 2. 総合品質評価
    print("\n2️⃣ 総合品質評価...")
    
    success_rate = standalone_results.get('success_rate', 0)
    overall_success = standalone_results.get('overall_success', False)
    
    comprehensive_results['overall_success'] = overall_success
    comprehensive_results['success_rate'] = success_rate
    
    if success_rate >= 95:
        comprehensive_results['implementation_quality'] = 'excellent'
    elif success_rate >= 85:
        comprehensive_results['implementation_quality'] = 'good'
    elif success_rate >= 70:
        comprehensive_results['implementation_quality'] = 'acceptable'
    else:
        comprehensive_results['implementation_quality'] = 'needs_improvement'
    
    # 3. テスト結果出力
    print("\n3️⃣ テスト結果出力...")
    
    output_filename = f"BASIC_DATA_SERVICE_FLASK_FREE_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        print(f"✅ テスト結果出力: {output_filename}")
    except Exception as e:
        print(f"❌ 結果出力失敗: {e}")
    
    # 4. 最終判定
    print("\n" + "=" * 80)
    print("🎯 【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービスFlask非依存テスト結果")
    print("=" * 80)
    
    if comprehensive_results['overall_success']:
        print("✅ 最終判定: データサービス単体実装完了")
        print("✅ モジュール読み込み: 成功")
        print("✅ セキュリティチェック: 成功")
        print("✅ データ読み込み: 成功")
        print("✅ 問題選択機能: 成功")
        print("✅ 回答検証機能: 成功")
        print("✅ キャッシュ機能: 成功")
        print("✅ エラーハンドリング: 成功")
        
        print(f"\n📊 品質スコア: {success_rate:.1f}% ({comprehensive_results['implementation_quality']})")
        
        print(f"\n🚀 次段階: Flask統合テスト実行可能")
        print("💡 推奨: Flask環境でのセッション管理統合テストも実施")
        
    else:
        print("❌ 最終判定: データサービス実装に改善点発見")
        print("🔧 必要対応: 品質向上後再検証必要")
        print(f"📊 成功率: {success_rate:.1f}%")
    
    return comprehensive_results

def main():
    """メイン実行関数"""
    results = comprehensive_flask_free_data_service_test()
    
    if results['overall_success']:
        print("\n🎉 基礎科目データサービスFlask非依存テスト完了")
        print("📋 データサービス: 単体実装確認済み")
        print("📋 次: Flask環境での統合テスト推奨")
        sys.exit(0)
    else:
        print("\n🚨 基礎科目データサービスFlask非依存テストで改善点発見")
        print("💡 対応: 品質向上後再実行必要")
        sys.exit(1)

if __name__ == "__main__":
    main()