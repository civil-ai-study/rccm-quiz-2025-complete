#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービス統合テスト
basic_data_service.py + basic_session_manager.py完全統合動作確認
Flask非依存テスト + Flask環境テスト両方実行
"""

import sys
import os
import json
import tempfile
from datetime import datetime
from flask import Flask, session

def test_data_service_standalone():
    """データサービス単体テスト（Flask非依存）"""
    print("🔧 データサービス単体テスト実行中...")
    
    test_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_data_service_standalone',
        'standalone_tests': {},
        'overall_success': False
    }
    
    try:
        from basic_data_service import (
            BasicDataService, 
            SecurityError,
            validate_basic_exam_answer,
            get_basic_data_service_info
        )
        
        service = BasicDataService()
        
        # 1. セキュリティチェックテスト
        security_test = {}
        try:
            service._validate_file_access_security()
            security_test['access_validation'] = True
            security_test['security_check_passed'] = True
        except Exception as e:
            security_test['access_validation'] = False
            security_test['security_error'] = str(e)
        
        test_results['standalone_tests']['security'] = security_test
        
        # 2. データ読み込みテスト
        data_loading_test = {}
        try:
            questions = service.load_basic_questions()
            data_loading_test['questions_loaded'] = True
            data_loading_test['questions_count'] = len(questions)
            data_loading_test['sample_question_keys'] = list(questions[0].keys()) if questions else []
        except Exception as e:
            data_loading_test['questions_loaded'] = False
            data_loading_test['loading_error'] = str(e)
        
        test_results['standalone_tests']['data_loading'] = data_loading_test
        
        # 3. 問題選択テスト
        question_selection_test = {}
        try:
            if data_loading_test.get('questions_loaded'):
                session_questions = service.get_questions_for_session(10, randomize=True)
                question_selection_test['selection_successful'] = True
                question_selection_test['selected_count'] = len(session_questions)
                question_selection_test['first_question_has_order'] = 'session_order' in session_questions[0]
            else:
                question_selection_test['selection_successful'] = False
                question_selection_test['reason'] = 'questions_not_loaded'
        except Exception as e:
            question_selection_test['selection_successful'] = False
            question_selection_test['selection_error'] = str(e)
        
        test_results['standalone_tests']['question_selection'] = question_selection_test
        
        # 4. 回答検証テスト
        answer_validation_test = {}
        try:
            valid_answers = ['A', 'B', 'C', 'D']
            invalid_answers = ['E', '1', 'あ', '', None]
            
            validation_results = {
                'valid_answers': {answer: validate_basic_exam_answer(answer) for answer in valid_answers},
                'invalid_answers': {str(answer): validate_basic_exam_answer(answer) for answer in invalid_answers}
            }
            
            all_valid_passed = all(validation_results['valid_answers'].values())
            all_invalid_failed = not any(validation_results['invalid_answers'].values())
            
            answer_validation_test['validation_working'] = all_valid_passed and all_invalid_failed
            answer_validation_test['valid_count'] = sum(validation_results['valid_answers'].values())
            answer_validation_test['invalid_blocked'] = sum(1 for v in validation_results['invalid_answers'].values() if not v)
        except Exception as e:
            answer_validation_test['validation_working'] = False
            answer_validation_test['validation_error'] = str(e)
        
        test_results['standalone_tests']['answer_validation'] = answer_validation_test
        
        # 5. 統計情報テスト
        statistics_test = {}
        try:
            stats = get_basic_data_service_info()
            statistics_test['statistics_available'] = True
            statistics_test['total_questions'] = stats.get('total_available_questions', 0)
            statistics_test['service_version'] = stats.get('service_info', {}).get('version', 'unknown')
        except Exception as e:
            statistics_test['statistics_available'] = False
            statistics_test['statistics_error'] = str(e)
        
        test_results['standalone_tests']['statistics'] = statistics_test
        
        # 6. 総合判定
        all_tests_passed = all([
            security_test.get('security_check_passed', False),
            data_loading_test.get('questions_loaded', False),
            question_selection_test.get('selection_successful', False),
            answer_validation_test.get('validation_working', False),
            statistics_test.get('statistics_available', False)
        ])
        
        test_results['overall_success'] = all_tests_passed
        print(f"✅ 単体テスト結果: {'成功' if all_tests_passed else '失敗'}")
        
    except Exception as e:
        test_results['error'] = str(e)
        test_results['overall_success'] = False
        print(f"❌ 単体テストエラー: {e}")
    
    return test_results

def test_data_service_flask_integration():
    """データサービスFlask統合テスト"""
    print("🔧 データサービスFlask統合テスト実行中...")
    
    integration_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_data_service_flask_integration',
        'integration_tests': {},
        'overall_success': False
    }
    
    # テスト用Flaskアプリ作成
    app = Flask(__name__)
    app.secret_key = 'ultrathin_test_secret_key_data_service_integration'
    
    with app.app_context():
        with app.test_request_context():
            try:
                from basic_data_service import (
                    BasicDataService,
                    create_basic_session_with_questions,
                    get_basic_exam_current_question
                )
                from basic_session_manager import (
                    get_basic_exam_session,
                    is_basic_exam_session_active,
                    clear_basic_exam_session
                )
                
                # 1. セッション作成統合テスト
                session_creation_test = {}
                try:
                    session_id = create_basic_session_with_questions(10, {'test_mode': True})
                    session_creation_test['session_created'] = session_id is not None
                    session_creation_test['session_id_format'] = len(session_id) == 36 if session_id else False
                    session_creation_test['session_active'] = is_basic_exam_session_active()
                except Exception as e:
                    session_creation_test['session_created'] = False
                    session_creation_test['creation_error'] = str(e)
                
                integration_results['integration_tests']['session_creation'] = session_creation_test
                
                # 2. セッションデータ整合性テスト
                data_consistency_test = {}
                try:
                    session_data = get_basic_exam_session()
                    if session_data:
                        questions = session_data.get('questions', [])
                        metadata = session_data.get('metadata', {})
                        
                        data_consistency_test['session_data_available'] = True
                        data_consistency_test['questions_count'] = len(questions)
                        data_consistency_test['metadata_has_data_source'] = 'data_source' in metadata
                        data_consistency_test['metadata_has_service_info'] = 'service_version' in metadata
                        data_consistency_test['questions_have_basic_fields'] = all(
                            'question' in q and 'correct_answer' in q for q in questions
                        )
                    else:
                        data_consistency_test['session_data_available'] = False
                except Exception as e:
                    data_consistency_test['session_data_available'] = False
                    data_consistency_test['consistency_error'] = str(e)
                
                integration_results['integration_tests']['data_consistency'] = data_consistency_test
                
                # 3. 現在問題取得テスト
                current_question_test = {}
                try:
                    current_question = get_basic_exam_current_question()
                    if current_question:
                        current_question_test['current_question_available'] = True
                        current_question_test['has_session_order'] = 'session_order' in current_question
                        current_question_test['has_navigation_info'] = 'is_last_question' in current_question
                        current_question_test['question_content_valid'] = len(current_question.get('question', '')) > 0
                    else:
                        current_question_test['current_question_available'] = False
                except Exception as e:
                    current_question_test['current_question_available'] = False
                    current_question_test['retrieval_error'] = str(e)
                
                integration_results['integration_tests']['current_question'] = current_question_test
                
                # 4. サービス統合動作テスト
                service_integration_test = {}
                try:
                    service = BasicDataService()
                    
                    # セッション内問題取得テスト
                    question_0 = service.get_session_question_by_index(0)
                    question_1 = service.get_session_question_by_index(1)
                    
                    service_integration_test['indexed_question_access'] = question_0 is not None and question_1 is not None
                    service_integration_test['question_metadata_enriched'] = (
                        'current_index' in question_0 and 'total_questions' in question_0
                    ) if question_0 else False
                    
                    # 統計情報取得（セッション情報含む）
                    stats = service.get_basic_exam_statistics()
                    service_integration_test['stats_include_session'] = 'current_session' in stats
                    service_integration_test['session_stats_valid'] = (
                        stats.get('current_session', {}).get('session_active', False)
                    )
                    
                except Exception as e:
                    service_integration_test['indexed_question_access'] = False
                    service_integration_test['service_integration_error'] = str(e)
                
                integration_results['integration_tests']['service_integration'] = service_integration_test
                
                # 5. クリーンアップテスト
                cleanup_test = {}
                try:
                    clear_success = clear_basic_exam_session()
                    cleanup_test['session_cleared'] = clear_success
                    cleanup_test['session_no_longer_active'] = not is_basic_exam_session_active()
                except Exception as e:
                    cleanup_test['session_cleared'] = False
                    cleanup_test['cleanup_error'] = str(e)
                
                integration_results['integration_tests']['cleanup'] = cleanup_test
                
                # 6. 総合判定
                all_integration_passed = all([
                    session_creation_test.get('session_created', False),
                    data_consistency_test.get('session_data_available', False),
                    current_question_test.get('current_question_available', False),
                    service_integration_test.get('indexed_question_access', False),
                    cleanup_test.get('session_cleared', False)
                ])
                
                integration_results['overall_success'] = all_integration_passed
                print(f"✅ 統合テスト結果: {'成功' if all_integration_passed else '失敗'}")
                
            except Exception as e:
                integration_results['error'] = str(e)
                integration_results['overall_success'] = False
                print(f"❌ 統合テストエラー: {e}")
    
    return integration_results

def test_data_service_10_question_flow():
    """データサービス10問完走フローテスト"""
    print("🔧 データサービス10問完走フローテスト実行中...")
    
    flow_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_name': 'basic_data_service_10_question_flow',
        'flow_tests': {},
        'overall_success': False
    }
    
    app = Flask(__name__)
    app.secret_key = 'ultrathin_test_secret_key_10_question_flow'
    
    with app.app_context():
        with app.test_request_context():
            try:
                from basic_data_service import (
                    BasicDataService,
                    create_basic_session_with_questions,
                    validate_basic_exam_answer
                )
                from basic_session_manager import (
                    BasicExamSessionManager,
                    get_basic_exam_session,
                    clear_basic_exam_session
                )
                
                # 1. セッション開始
                session_start_test = {}
                try:
                    session_id = create_basic_session_with_questions(10, {'flow_test': True})
                    session_start_test['session_created'] = session_id is not None
                    
                    session_data = get_basic_exam_session()
                    session_start_test['initial_data_valid'] = session_data is not None
                    session_start_test['questions_loaded'] = len(session_data.get('questions', [])) == 10 if session_data else False
                    
                except Exception as e:
                    session_start_test['session_created'] = False
                    session_start_test['start_error'] = str(e)
                
                flow_results['flow_tests']['session_start'] = session_start_test
                
                # 2. 10問フロー実行
                question_flow_test = {}
                try:
                    if session_start_test.get('session_created'):
                        service = BasicDataService()
                        manager = BasicExamSessionManager()
                        
                        flow_success = []
                        answers_provided = ['A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B']  # 10問分
                        
                        for i in range(10):
                            # 問題更新
                            update_success = manager.update_current_question(i)
                            
                            # 現在問題取得
                            current_question = service.get_session_question_by_index(i)
                            
                            # 回答検証
                            answer = answers_provided[i]
                            answer_valid = validate_basic_exam_answer(answer)
                            
                            # 回答保存
                            save_success = manager.save_answer(i, answer) if answer_valid else False
                            
                            step_success = update_success and current_question is not None and save_success
                            flow_success.append(step_success)
                            
                            if not step_success:
                                break
                        
                        question_flow_test['all_questions_processed'] = len(flow_success) == 10
                        question_flow_test['all_steps_successful'] = all(flow_success)
                        question_flow_test['successful_steps'] = sum(flow_success)
                        question_flow_test['failed_steps'] = 10 - sum(flow_success)
                    else:
                        question_flow_test['all_questions_processed'] = False
                        question_flow_test['reason'] = 'session_not_created'
                        
                except Exception as e:
                    question_flow_test['all_questions_processed'] = False
                    question_flow_test['flow_error'] = str(e)
                
                flow_results['flow_tests']['question_flow'] = question_flow_test
                
                # 3. 結果計算テスト
                results_calculation_test = {}
                try:
                    if question_flow_test.get('all_questions_processed'):
                        manager = BasicExamSessionManager()
                        results = manager.calculate_results()
                        
                        results_calculation_test['results_calculated'] = results is not None
                        if results:
                            results_calculation_test['has_score'] = 'score_percentage' in results
                            results_calculation_test['has_details'] = len(results.get('result_details', [])) == 10
                            results_calculation_test['score_valid'] = 0 <= results.get('score_percentage', -1) <= 100
                    else:
                        results_calculation_test['results_calculated'] = False
                        results_calculation_test['reason'] = 'flow_incomplete'
                        
                except Exception as e:
                    results_calculation_test['results_calculated'] = False
                    results_calculation_test['calculation_error'] = str(e)
                
                flow_results['flow_tests']['results_calculation'] = results_calculation_test
                
                # 4. セッション完了確認
                completion_test = {}
                try:
                    session_data = get_basic_exam_session()
                    if session_data:
                        completion_test['session_data_intact'] = True
                        completion_test['all_answers_saved'] = len(session_data.get('answers', {})) == 10
                        completion_test['status_updated'] = session_data.get('status') == 'completed'
                    else:
                        completion_test['session_data_intact'] = False
                        
                    # クリーンアップ
                    clear_success = clear_basic_exam_session()
                    completion_test['cleanup_successful'] = clear_success
                    
                except Exception as e:
                    completion_test['session_data_intact'] = False
                    completion_test['completion_error'] = str(e)
                
                flow_results['flow_tests']['completion'] = completion_test
                
                # 5. 総合フロー判定
                all_flow_passed = all([
                    session_start_test.get('session_created', False),
                    question_flow_test.get('all_steps_successful', False),
                    results_calculation_test.get('results_calculated', False),
                    completion_test.get('cleanup_successful', False)
                ])
                
                flow_results['overall_success'] = all_flow_passed
                print(f"✅ 10問フローテスト結果: {'成功' if all_flow_passed else '失敗'}")
                
            except Exception as e:
                flow_results['error'] = str(e)
                flow_results['overall_success'] = False
                print(f"❌ 10問フローテストエラー: {e}")
    
    return flow_results

def comprehensive_data_service_test():
    """包括的データサービステスト"""
    
    print("🎯 【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービス統合テスト開始")
    print(f"📅 テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 目的: basic_data_service.py + basic_session_manager.py完全統合確認")
    print("🎯 範囲: 単体動作・Flask統合・10問完走フロー")
    print("🛡️ 安全性: 基礎科目専用・既存システム影響ゼロ")
    print("=" * 80)
    
    comprehensive_results = {
        'test_timestamp': datetime.now().isoformat(),
        'test_suite': 'basic_data_service_comprehensive_integration',
        'standalone_test_results': {},
        'flask_integration_results': {},
        'flow_test_results': {},
        'overall_success': False,
        'integration_quality': 'unknown'
    }
    
    # 1. 単体テスト実行
    print("\n1️⃣ データサービス単体テスト...")
    standalone_results = test_data_service_standalone()
    comprehensive_results['standalone_test_results'] = standalone_results
    
    # 2. Flask統合テスト実行
    print("\n2️⃣ Flask統合テスト...")
    flask_results = test_data_service_flask_integration()
    comprehensive_results['flask_integration_results'] = flask_results
    
    # 3. 10問完走フローテスト実行
    print("\n3️⃣ 10問完走フローテスト...")
    flow_results = test_data_service_10_question_flow()
    comprehensive_results['flow_test_results'] = flow_results
    
    # 4. 総合品質評価
    print("\n4️⃣ 総合品質評価...")
    
    quality_scores = {
        'standalone_quality': standalone_results.get('overall_success', False),
        'flask_integration_quality': flask_results.get('overall_success', False),
        'flow_completion_quality': flow_results.get('overall_success', False)
    }
    
    overall_success = all(quality_scores.values())
    success_rate = sum(quality_scores.values()) / len(quality_scores) * 100
    
    comprehensive_results['overall_success'] = overall_success
    comprehensive_results['quality_scores'] = quality_scores
    comprehensive_results['success_rate'] = success_rate
    
    if success_rate >= 100:
        comprehensive_results['integration_quality'] = 'excellent'
    elif success_rate >= 80:
        comprehensive_results['integration_quality'] = 'good'
    elif success_rate >= 60:
        comprehensive_results['integration_quality'] = 'acceptable'
    else:
        comprehensive_results['integration_quality'] = 'needs_improvement'
    
    # 5. テスト結果出力
    print("\n5️⃣ テスト結果出力...")
    
    output_filename = f"BASIC_DATA_SERVICE_INTEGRATION_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        print(f"✅ テスト結果出力: {output_filename}")
    except Exception as e:
        print(f"❌ 結果出力失敗: {e}")
    
    # 6. 最終判定
    print("\n" + "=" * 80)
    print("🎯 【ULTRATHIN区 PHASE 2-2-4】基礎科目データサービス統合テスト結果")
    print("=" * 80)
    
    if comprehensive_results['overall_success']:
        print("✅ 最終判定: データサービス統合完了")
        print("✅ 単体動作: 確認済み")
        print("✅ Flask統合: 確認済み")
        print("✅ 10問完走: 確認済み")
        print("✅ セッション管理統合: 確認済み")
        print("✅ 既存システム保護: 継続")
        
        print(f"\n📊 品質スコア:")
        print(f"   📋 単体動作: {'成功' if quality_scores['standalone_quality'] else '失敗'}")
        print(f"   📋 Flask統合: {'成功' if quality_scores['flask_integration_quality'] else '失敗'}")
        print(f"   📋 フロー完走: {'成功' if quality_scores['flow_completion_quality'] else '失敗'}")
        print(f"   📋 総合評価: {success_rate:.1f}% ({comprehensive_results['integration_quality']})")
        
        print(f"\n🚀 次段階: PHASE 2-2-5 新システム独立動作テスト進行可能")
        print("💡 推奨: Blueprint統合でのフル機能テストも実施")
        
    else:
        print("❌ 最終判定: データサービス統合に改善点発見")
        print("🔧 必要対応: 品質向上後再検証必要")
        
        # 問題詳細
        if not standalone_results.get('overall_success'):
            print("❌ 問題: 単体動作に不具合")
        if not flask_results.get('overall_success'):
            print("❌ 問題: Flask統合に不具合")
        if not flow_results.get('overall_success'):
            print("❌ 問題: 10問完走フローに不具合")
    
    return comprehensive_results

def main():
    """メイン実行関数"""
    results = comprehensive_data_service_test()
    
    if results['overall_success']:
        print("\n🎉 基礎科目データサービス統合テスト完了")
        print("📋 データサービス: 統合確認済み")
        print("📋 次: PHASE 2-2-5 新システム独立動作テスト")
        sys.exit(0)
    else:
        print("\n🚨 基礎科目データサービス統合テストで改善点発見")
        print("💡 対応: 品質向上後再実行必要")
        sys.exit(1)

if __name__ == "__main__":
    main()