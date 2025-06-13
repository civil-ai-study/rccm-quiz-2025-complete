#!/usr/bin/env python3
"""
動的難易度制御システムのテスト
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from difficulty_controller import difficulty_controller
from adaptive_learning import adaptive_engine

def create_test_session(questions_count=20, accuracy_rate=0.7, avg_time=45, department='road'):
    """テスト用のユーザーセッションを作成"""
    session = {
        'history': [],
        'session_id': 'test_session_001',
        'selected_department': department
    }
    
    # 履歴データを生成
    base_time = datetime.now() - timedelta(days=10)
    
    for i in range(questions_count):
        is_correct = (i / questions_count) < accuracy_rate
        elapsed_time = avg_time + (i % 10 - 5) * 5  # 時間にバリエーション
        
        history_item = {
            'id': i + 1,
            'category': f'カテゴリ{(i % 3) + 1}',
            'department': department,
            'question_type': 'basic' if i < questions_count // 2 else 'specialist',
            'is_correct': is_correct,
            'user_answer': 'A',
            'correct_answer': 'A' if is_correct else 'B',
            'date': (base_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed': elapsed_time,
            'difficulty': '標準'
        }
        
        session['history'].append(history_item)
    
    return session

def test_learner_assessment():
    """学習者レベル評価のテスト"""
    print("=== 学習者レベル評価テスト ===")
    
    # 初心者レベルのテストケース
    beginner_session = create_test_session(5, 0.4, 80, 'road')
    assessment = difficulty_controller.assess_learner_level(beginner_session, 'road')
    
    print(f"初心者テストケース:")
    print(f"  レベル: {assessment['level_name']}")
    print(f"  推奨難易度: {assessment['recommended_difficulty']}")
    print(f"  信頼度: {assessment['confidence']:.2f}")
    print(f"  部門調整係数: {assessment['department_factor']}")
    
    # 上級者レベルのテストケース
    advanced_session = create_test_session(50, 0.85, 25, 'comprehensive')
    assessment = difficulty_controller.assess_learner_level(advanced_session, 'comprehensive')
    
    print(f"\n上級者テストケース:")
    print(f"  レベル: {assessment['level_name']}")
    print(f"  推奨難易度: {assessment['recommended_difficulty']}")
    print(f"  信頼度: {assessment['confidence']:.2f}")
    print(f"  部門調整係数: {assessment['department_factor']}")
    
    return True

def test_difficulty_adjustment():
    """難易度調整のテスト"""
    print("\n=== 難易度調整テスト ===")
    
    # サンプル問題データ
    sample_questions = [
        {'id': i, 'question_type': 'basic', 'difficulty': '基本', 'category': 'カテゴリ1', 'department': 'road'}
        for i in range(10)
    ] + [
        {'id': i+10, 'question_type': 'specialist', 'difficulty': '標準', 'category': 'カテゴリ2', 'department': 'road'}
        for i in range(10)
    ] + [
        {'id': i+20, 'question_type': 'specialist', 'difficulty': '応用', 'category': 'カテゴリ3', 'department': 'road'}
        for i in range(10)
    ]
    
    # 中級者の学習者評価
    intermediate_session = create_test_session(20, 0.65, 50, 'road')
    learner_assessment = difficulty_controller.assess_learner_level(intermediate_session, 'road')
    
    # 問題難易度調整
    adjusted_questions = difficulty_controller.adjust_question_difficulty(
        sample_questions, learner_assessment, 10
    )
    
    print(f"元の問題数: {len(sample_questions)}")
    print(f"調整後問題数: {len(adjusted_questions)}")
    print(f"学習者レベル: {learner_assessment['level_name']}")
    
    # 難易度分布の確認
    difficulty_count = {}
    for q in adjusted_questions:
        diff = q.get('difficulty', '標準')
        difficulty_count[diff] = difficulty_count.get(diff, 0) + 1
    
    print(f"調整後難易度分布: {difficulty_count}")
    
    return True

def test_adaptive_integration():
    """アダプティブ学習との統合テスト"""
    print("\n=== アダプティブ学習統合テスト ===")
    
    # テストセッション
    session = create_test_session(15, 0.6, 60, 'civil_planning')
    
    # 学習者インサイト取得
    insights = adaptive_engine.get_learner_insights(session, 'civil_planning')
    
    if 'error' not in insights:
        print(f"学習者レベル: {insights['learner_level']}")
        print(f"レベル名: {insights['level_name']}")
        print(f"評価信頼度: {insights['confidence']:.2f}")
        print(f"推奨難易度: {insights['recommended_difficulty']}")
        print(f"部門調整係数: {insights['department_factor']}")
        
        # 推奨事項の表示
        if insights.get('study_recommendations'):
            print("\n学習推奨事項:")
            for i, rec in enumerate(insights['study_recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # 動的セッション設定の確認
        if insights.get('dynamic_config'):
            config = insights['dynamic_config']
            print(f"\n動的セッション設定:")
            print(f"  目標正答率: {config.get('target_accuracy', 0):.0%}")
            print(f"  時間係数: {config.get('time_limit_multiplier', 1.0):.1f}")
            print(f"  フィードバック強度: {config.get('feedback_intensity', 'standard')}")
            print(f"  ヒント利用可能: {config.get('hint_availability', False)}")
    else:
        print(f"エラー: {insights['error']}")
        return False
    
    return True

def test_performance_monitoring():
    """パフォーマンス監視テスト"""
    print("\n=== パフォーマンス監視テスト ===")
    
    session = create_test_session(10, 0.5, 70, 'road')
    
    # 最近の結果（下降傾向をシミュレート）
    recent_results = []
    for i in range(5):
        result = {
            'is_correct': i < 1,  # 最初の1問だけ正解
            'elapsed': 80 + i * 10,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        recent_results.append(result)
    
    # パフォーマンス監視と調整
    adjustment = adaptive_engine.monitor_and_adjust_difficulty(session, recent_results)
    
    print(f"調整が必要: {adjustment.get('adjusted', False)}")
    if adjustment.get('adjusted'):
        print(f"  現在レベル: {adjustment['old_level']}")
        print(f"  新レベル: {adjustment['new_level']}")
        print(f"  調整信頼度: {adjustment['confidence']:.2f}")
        if adjustment.get('recommendations'):
            print("  推奨事項:")
            for rec in adjustment['recommendations']:
                print(f"    - {rec}")
    else:
        print(f"  理由: {adjustment.get('reason', '不明')}")
    
    return True

def run_all_tests():
    """全テストの実行"""
    print("動的難易度制御システム - 統合テスト開始\n")
    
    tests = [
        ("学習者レベル評価", test_learner_assessment),
        ("難易度調整", test_difficulty_adjustment),
        ("アダプティブ学習統合", test_adaptive_integration),
        ("パフォーマンス監視", test_performance_monitoring)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
            print(f"✅ {test_name}: {'成功' if result else '失敗'}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ {test_name}: エラー - {e}")
        
        print("-" * 50)
    
    # 結果サマリー
    print("\n=== テスト結果サマリー ===")
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"成功: {success_count}/{total_count}")
    
    for test_name, success, error in results:
        status = "✅ 成功" if success else f"❌ 失敗{f' ({error})' if error else ''}"
        print(f"  {test_name}: {status}")
    
    if success_count == total_count:
        print("\n🎉 全テストが成功しました！動的難易度制御システムは正常に動作しています。")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count}個のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)