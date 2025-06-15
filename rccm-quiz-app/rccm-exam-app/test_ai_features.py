#!/usr/bin/env python3
"""
AI機能（弱点分析・アダプティブ学習）のテストスクリプト
"""

import sys
import os
from datetime import datetime, timedelta
import random

# パスを設定
sys.path.insert(0, os.path.dirname(__file__))

def test_ai_analyzer():
    """AI分析エンジンのテスト"""
    print("🧠 AI分析エンジンテスト開始")
    
    try:
        from ai_analyzer import AILearningAnalyzer
        
        analyzer = AILearningAnalyzer()
        print("✅ AILearningAnalyzer初期化成功")
        
        # テスト用の学習履歴生成
        test_session = generate_realistic_history()
        
        # AI分析実行
        analysis_result = analyzer.analyze_weak_areas(test_session)
        
        print(f"✅ AI弱点分析完了:")
        print(f"   - 弱点エリア数: {len(analysis_result.get('weak_areas', {}))}")
        print(f"   - 信頼度: {analysis_result.get('confidence_score', 0):.2f}")
        print(f"   - 学習プランタイプ: {analysis_result.get('learning_plan', {}).get('plan_type', 'unknown')}")
        
        # 弱点エリアの詳細表示
        for category, info in analysis_result.get('weak_areas', {}).items():
            print(f"   - {category}: 弱点度{info.get('weakness_score', 0):.2f}, 優先度{info.get('priority', 0):.2f}")
        
        return True, analysis_result
        
    except Exception as e:
        print(f"❌ AI分析エラー: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def test_adaptive_learning():
    """アダプティブ学習エンジンのテスト"""
    print("\n🎯 アダプティブ学習エンジンテスト開始")
    
    try:
        from adaptive_learning import AdaptiveLearningEngine
        
        engine = AdaptiveLearningEngine()
        print("✅ AdaptiveLearningEngine初期化成功")
        
        # テスト用データ
        test_session = generate_realistic_history()
        test_questions = generate_test_questions()
        test_ai_analysis = {
            'weak_areas': {
                'コンクリート': {'weakness_score': 0.7, 'priority': 0.8},
                '構造': {'weakness_score': 0.3, 'priority': 0.2}
            },
            'confidence_score': 0.8
        }
        
        # 学習モード推奨テスト
        recommended_mode = engine.get_learning_mode_recommendation(test_session, test_ai_analysis)
        print(f"✅ 推奨学習モード: {recommended_mode}")
        
        # アダプティブ問題選択テスト
        for mode in ['foundation', 'balanced', 'challenge', 'review']:
            adaptive_questions = engine.get_adaptive_questions(
                test_session, test_questions, test_ai_analysis, 10, mode
            )
            print(f"✅ {mode}モード: {len(adaptive_questions)}問選択")
            
            # 問題の内訳確認
            categories = {}
            for q in adaptive_questions:
                cat = q.get('category', '不明')
                categories[cat] = categories.get(cat, 0) + 1
            print(f"   カテゴリ分布: {categories}")
        
        return True
        
    except Exception as e:
        print(f"❌ アダプティブ学習エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """統合テスト"""
    print("\n🔄 統合テスト開始")
    
    try:
        from ai_analyzer import ai_analyzer
        from adaptive_learning import adaptive_engine
        
        # テスト用データ
        test_session = generate_realistic_history()
        test_questions = generate_test_questions()
        
        # Step 1: AI分析
        print("Step 1: AI分析実行")
        analysis = ai_analyzer.analyze_weak_areas(test_session)
        
        # Step 2: 学習モード推奨
        print("Step 2: 学習モード推奨")
        mode = adaptive_engine.get_learning_mode_recommendation(test_session, analysis)
        
        # Step 3: アダプティブ問題選択
        print("Step 3: アダプティブ問題選択")
        questions = adaptive_engine.get_adaptive_questions(
            test_session, test_questions, analysis, 15, mode
        )
        
        # Step 4: セッション効果測定
        print("Step 4: セッション効果測定")
        session_results = simulate_quiz_session(questions)
        effectiveness = adaptive_engine.calculate_session_effectiveness(
            test_session, session_results
        )
        
        print(f"✅ 統合テスト完了:")
        print(f"   - 分析信頼度: {analysis.get('confidence_score', 0):.2f}")
        print(f"   - 推奨モード: {mode}")
        print(f"   - 選択問題数: {len(questions)}")
        print(f"   - セッション正答率: {effectiveness.get('accuracy', 0):.2f}")
        print(f"   - 学習効率: {effectiveness.get('efficiency', 0):.2f} 問/分")
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_realistic_history():
    """リアルな学習履歴を生成"""
    history = []
    categories = ['コンクリート', '構造', '施工', '維持管理']
    
    # 30日間の学習をシミュレート
    for day in range(30):
        date = datetime.now() - timedelta(days=29-day)
        
        # 1日5-15問をシミュレート
        daily_questions = random.randint(5, 15)
        
        for q in range(daily_questions):
            category = random.choice(categories)
            
            # カテゴリごとに正答率を調整（弱点を作る）
            if category == 'コンクリート':
                is_correct = random.random() > 0.4  # 60%正答率（弱点）
            elif category == '構造':
                is_correct = random.random() > 0.25  # 75%正答率
            else:
                is_correct = random.random() > 0.2   # 80%正答率
            
            elapsed_time = random.normalvariate(45, 15)  # 平均45秒、標準偏差15秒
            elapsed_time = max(10, min(elapsed_time, 120))  # 10-120秒の範囲
            
            history.append({
                'id': len(history) + 1,
                'category': category,
                'is_correct': is_correct,
                'user_answer': 'A',
                'correct_answer': 'A' if is_correct else 'B',
                'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': elapsed_time,
                'difficulty': random.choice(['基本', '標準', '応用'])
            })
    
    # カテゴリ統計も生成
    category_stats = {}
    for entry in history:
        cat = entry['category']
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'correct': 0}
        category_stats[cat]['total'] += 1
        if entry['is_correct']:
            category_stats[cat]['correct'] += 1
    
    return {
        'history': history,
        'category_stats': category_stats,
        'srs_data': {},
        'earned_badges': ['first_quiz', 'study_streak_7']
    }

def generate_test_questions():
    """テスト用問題データを生成"""
    questions = []
    categories = ['コンクリート', '構造', '施工', '維持管理']
    difficulties = ['基本', '標準', '応用']
    
    for i in range(100):
        questions.append({
            'id': i + 1,
            'category': random.choice(categories),
            'question': f'テスト問題{i+1}の内容です。',
            'option_a': '選択肢A',
            'option_b': '選択肢B',
            'option_c': '選択肢C',
            'option_d': '選択肢D',
            'correct_answer': 'A',
            'difficulty': random.choice(difficulties),
            'explanation': 'テスト用の解説です。'
        })
    
    return questions

def simulate_quiz_session(questions):
    """問題セッションをシミュレート"""
    results = []
    
    for question in questions:
        # 弱点分野は正答率を下げる
        if question.get('category') == 'コンクリート':
            is_correct = random.random() > 0.3
        else:
            is_correct = random.random() > 0.2
        
        elapsed_time = random.normalvariate(40, 10)
        elapsed_time = max(15, min(elapsed_time, 90))
        
        results.append({
            'id': question.get('id'),
            'category': question.get('category'),
            'is_correct': is_correct,
            'elapsed': elapsed_time
        })
    
    return results

def performance_test():
    """パフォーマンステスト"""
    print("\n⚡ パフォーマンステスト開始")
    
    try:
        import time
        from ai_analyzer import ai_analyzer
        from adaptive_learning import adaptive_engine
        
        # 大量データでのテスト
        large_session = generate_realistic_history()
        # 履歴を10倍に拡張
        large_session['history'] = large_session['history'] * 10
        
        test_questions = generate_test_questions()
        
        start_time = time.time()
        
        # AI分析実行
        analysis = ai_analyzer.analyze_weak_areas(large_session)
        analysis_time = time.time() - start_time
        
        # アダプティブ学習実行
        start_time = time.time()
        questions = adaptive_engine.get_adaptive_questions(
            large_session, test_questions, analysis, 20, 'balanced'
        )
        adaptive_time = time.time() - start_time
        
        print(f"✅ パフォーマンステスト完了:")
        print(f"   - 履歴データ数: {len(large_session['history'])}")
        print(f"   - AI分析時間: {analysis_time:.3f}秒")
        print(f"   - アダプティブ選択時間: {adaptive_time:.3f}秒")
        print(f"   - 総処理時間: {analysis_time + adaptive_time:.3f}秒")
        
        if analysis_time + adaptive_time < 1.0:  # 1秒以内
            print("✅ パフォーマンス良好")
        else:
            print("⚠️ パフォーマンス要改善")
        
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステストエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RCCM Quiz App - AI Features Test Suite")
    print("=" * 60)
    
    # テスト実行
    test1_success, analysis_result = test_ai_analyzer()
    test2_success = test_adaptive_learning()
    test3_success = test_integration()
    test4_success = performance_test()
    
    print("\n" + "=" * 60)
    print("テスト結果サマリー:")
    print(f"✅ AI分析エンジン: {'成功' if test1_success else '失敗'}")
    print(f"✅ アダプティブ学習: {'成功' if test2_success else '失敗'}")
    print(f"✅ 統合テスト: {'成功' if test3_success else '失敗'}")
    print(f"✅ パフォーマンス: {'成功' if test4_success else '失敗'}")
    
    if all([test1_success, test2_success, test3_success, test4_success]):
        print("\n🎉 全てのAI機能テストが成功しました！")
        print("Phase 2のAI弱点分析とアダプティブ学習機能は正常に動作します。")
    else:
        print("\n❌ 一部のテストが失敗しました。")
    
    print("=" * 60)