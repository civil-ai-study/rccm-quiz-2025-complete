#!/usr/bin/env python3
"""
学習効率最適化エンジンのテスト
"""

import sys
import os
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from learning_optimizer import learning_optimizer

def create_test_session_with_time_patterns():
    """時間パターンのあるテストセッション作成"""
    session = {
        'history': [],
        'birth_date': '1990-05-15'  # テスト用生年月日
    }
    
    # 朝型パターンのテストデータ生成
    base_date = datetime.now() - timedelta(days=20)
    
    morning_hours = [8, 9, 10]  # 朝の時間帯
    evening_hours = [20, 21, 22]  # 夜の時間帯
    
    for day in range(20):
        # 朝の学習セッション（高パフォーマンス）
        for hour in morning_hours:
            for question in range(3):
                dt = base_date + timedelta(days=day, hours=hour, minutes=question*5)
                entry = {
                    'id': len(session['history']) + 1,
                    'category': 'テストカテゴリ',
                    'department': 'road',
                    'question_type': 'basic',
                    'is_correct': True if question < 2 else False,  # 高正答率
                    'user_answer': 'A',
                    'correct_answer': 'A' if question < 2 else 'B',
                    'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'elapsed': 35 + question * 5,  # 比較的早い
                    'difficulty': '標準'
                }
                session['history'].append(entry)
        
        # 夜の学習セッション（中程度パフォーマンス）
        if day % 2 == 0:  # 隔日
            for hour in evening_hours[:2]:  # 夜は短時間
                for question in range(2):
                    dt = base_date + timedelta(days=day, hours=hour, minutes=question*10)
                    entry = {
                        'id': len(session['history']) + 1,
                        'category': 'テストカテゴリ',
                        'department': 'road',
                        'question_type': 'specialist',
                        'is_correct': question == 0,  # 中程度の正答率
                        'user_answer': 'A',
                        'correct_answer': 'A' if question == 0 else 'B',
                        'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'elapsed': 50 + question * 10,  # 少し遅い
                        'difficulty': '標準'
                    }
                    session['history'].append(entry)
    
    return session

def test_learning_pattern_analysis():
    """学習パターン分析のテスト"""
    print("=== 学習パターン分析テスト ===")
    
    session = create_test_session_with_time_patterns()
    pattern = learning_optimizer.analyze_personal_learning_pattern(session)
    
    print(f"学習タイプ: {pattern['learning_type']}")
    print(f"分析信頼度: {pattern['analysis_confidence']:.2f}")
    print(f"一貫性スコア: {pattern['consistency']['consistency_score']:.2f}")
    print(f"学習日数: {pattern['consistency']['study_days']}")
    print(f"最長ストリーク: {pattern['consistency']['max_streak']}")
    
    # 時間帯別パフォーマンス
    if pattern['hourly_performance']:
        print("\n時間帯別効率 (上位5位):")
        sorted_hours = sorted(
            pattern['hourly_performance'].items(),
            key=lambda x: x[1]['efficiency_score'],
            reverse=True
        )[:5]
        
        for hour, data in sorted_hours:
            print(f"  {hour}:00 - 効率{data['efficiency_score']:.2f}, 正答率{data['accuracy']:.2f}, セッション{data['sessions']}回")
    
    # 最適時間
    if pattern['optimal_times']:
        print("\n最適学習時間:")
        for optimal in pattern['optimal_times'][:3]:
            print(f"  {optimal['hour']}:00 - 効率{optimal['efficiency_score']:.2f}")
    
    return True

def test_biorhythm_calculation():
    """バイオリズム計算テスト"""
    print("\n=== バイオリズム計算テスト ===")
    
    birth_date = '1990-05-15'
    test_date = datetime(2024, 1, 15)
    
    biorhythm = learning_optimizer.calculate_biorhythm_score(birth_date, test_date)
    
    print(f"身体リズム: {biorhythm['physical']:.3f}")
    print(f"感情リズム: {biorhythm['emotional']:.3f}")
    print(f"知性リズム: {biorhythm['intellectual']:.3f}")
    print(f"総合スコア: {biorhythm['composite']:.3f}")
    
    # 7日間の予測
    print("\n7日間のバイオリズム予測:")
    for i in range(7):
        future_date = test_date + timedelta(days=i)
        future_biorhythm = learning_optimizer.calculate_biorhythm_score(birth_date, future_date)
        print(f"  {future_date.strftime('%m/%d')}: 知性{future_biorhythm['intellectual']:.2f}, 総合{future_biorhythm['composite']:.2f}")
    
    return True

def test_optimal_schedule_recommendation():
    """最適スケジュール推奨テスト"""
    print("\n=== 最適スケジュール推奨テスト ===")
    
    session = create_test_session_with_time_patterns()
    recommendation = learning_optimizer.get_optimal_study_time_recommendation(session)
    
    print(f"学習パターンタイプ: {recommendation['learning_pattern_type']}")
    print(f"分析信頼度: {recommendation['confidence_level']:.2f}")
    print(f"日次学習制限: {recommendation['daily_study_limit']}分")
    
    # バイオリズム
    if recommendation['biorhythm_scores']:
        bio = recommendation['biorhythm_scores']
        print(f"バイオリズム総合: {bio['composite']:.2f}")
    
    # 推奨セッション
    if recommendation['optimal_schedule']['recommended_sessions']:
        print("\n推奨学習セッション:")
        for session in recommendation['optimal_schedule']['recommended_sessions']:
            print(f"  {session['start_time']} - {session['duration_minutes']}分 (効率予測: {session['efficiency_score']:.2f})")
            if session.get('recommended_activities'):
                print(f"    活動: {', '.join(session['recommended_activities'])}")
    
    # 効率予測
    if recommendation['efficiency_forecast']:
        forecast = recommendation['efficiency_forecast']
        print(f"\n効率予測:")
        print(f"  全体効率: {forecast['overall_efficiency']:.2f}")
        print(f"  バイオリズム影響: {forecast['biorhythm_impact']}")
        if forecast['peak_hours']:
            print(f"  ピーク時間: {', '.join([str(h) + ':00' for h in forecast['peak_hours']])}")
    
    return True

def test_realtime_tracking():
    """リアルタイム追跡テスト"""
    print("\n=== リアルタイム追跡テスト ===")
    
    session = create_test_session_with_time_patterns()
    
    # 現在のセッションシミュレーション
    current_session_data = {
        'start_time': datetime.now() - timedelta(minutes=20),
        'question_count': 8
    }
    
    tracking = learning_optimizer.track_real_time_efficiency(session, current_session_data)
    
    if 'error' not in tracking:
        print(f"現在の効率: {tracking['current_efficiency']:.2f}")
        print(f"疲労度: {tracking['fatigue_level']:.2f}")
        print(f"セッション時間: {tracking['session_duration']:.1f}分")
        print(f"継続推奨: {'はい' if tracking['should_continue'] else 'いいえ'}")
        print(f"推奨休憩時間: {tracking['recommended_break_duration']}分")
        print(f"次回最適時間: {tracking['next_optimal_time']}")
        print(f"効率トレンド: {tracking['efficiency_trend']}")
        
        # パフォーマンス予測
        prediction = tracking['performance_prediction']
        print(f"現在の予測正答率: {prediction['current_predicted_accuracy']:.2f}")
        print(f"継続時の予測正答率: {prediction['future_predicted_accuracy']:.2f}")
        print(f"推奨アクション: {prediction['recommended_action']}")
    else:
        print(f"エラー: {tracking['error']}")
        return False
    
    return True

def test_session_length_optimization():
    """セッション長最適化テスト"""
    print("\n=== セッション長最適化テスト ===")
    
    # 様々なセッション長でのテストデータ
    session = {'history': []}
    base_date = datetime.now() - timedelta(days=10)
    
    # ショートセッション（高効率）
    for day in range(5):
        for question in range(5):  # 15分程度
            dt = base_date + timedelta(days=day, hours=10, minutes=question*3)
            entry = {
                'id': len(session['history']) + 1,
                'is_correct': question < 4,  # 高正答率
                'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': 30,
                'category': 'test', 'department': 'road', 'question_type': 'basic'
            }
            session['history'].append(entry)
    
    # ロングセッション（効率低下）
    for day in range(5, 10):
        for question in range(15):  # 60分程度
            dt = base_date + timedelta(days=day, hours=14, minutes=question*4)
            entry = {
                'id': len(session['history']) + 1,
                'is_correct': question < 8,  # 後半で正答率低下
                'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': 35 + question * 2,  # 時間も増加
                'category': 'test', 'department': 'road', 'question_type': 'basic'
            }
            session['history'].append(entry)
    
    pattern = learning_optimizer.analyze_personal_learning_pattern(session)
    session_analysis = pattern['session_analysis']
    
    print(f"平均セッション長: {session_analysis['avg_session_length']:.1f}分")
    print(f"推奨セッション長: {session_analysis['optimal_session_length']}分")
    print(f"総セッション数: {session_analysis['session_count']}")
    
    if session_analysis.get('performance_by_length'):
        print("\nセッション長別パフォーマンス:")
        for length_cat, perf in session_analysis['performance_by_length'].items():
            print(f"  {length_cat}: 正答率{perf.get('avg_accuracy', 0):.2f}, 回数{perf['count']}")
    
    return True

def run_all_tests():
    """全テストの実行"""
    print("学習効率最適化エンジン - 統合テスト開始\n")
    
    tests = [
        ("学習パターン分析", test_learning_pattern_analysis),
        ("バイオリズム計算", test_biorhythm_calculation),
        ("最適スケジュール推奨", test_optimal_schedule_recommendation),
        ("リアルタイム追跡", test_realtime_tracking),
        ("セッション長最適化", test_session_length_optimization)
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
        print("\n🎉 全テストが成功しました！学習効率最適化エンジンは正常に動作しています。")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count}個のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)