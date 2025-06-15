#!/usr/bin/env python3
"""
ゲーミフィケーション機能のテストスクリプト
Flaskの依存関係なしで機能をテスト
"""

import sys
import os
from datetime import datetime, timedelta

# パスを設定
sys.path.insert(0, os.path.dirname(__file__))

def test_gamification():
    """ゲーミフィケーション機能のテスト"""
    print("🎮 ゲーミフィケーション機能テスト開始")
    
    try:
        from gamification import GamificationManager
        
        # インスタンス作成
        gm = GamificationManager()
        print("✅ GamificationManager初期化成功")
        
        # テスト用セッション
        test_session = {
            'history': [],
            'category_stats': {},
            'earned_badges': []
        }
        
        # ストリーク機能テスト
        streak, streak_badges = gm.update_streak(test_session)
        print(f"✅ ストリーク機能: {streak}日, バッジ: {streak_badges}")
        
        # バッジチェック機能テスト
        new_badges = gm.check_badges(test_session)
        print(f"✅ バッジチェック機能: {new_badges}")
        
        # 学習インサイト機能テスト
        insights = gm.get_study_insights(test_session)
        print(f"✅ 学習インサイト機能: 総質問数: {insights.get('total_questions', 0)}")
        
        # 学習カレンダー機能テスト
        calendar_data = gm.generate_study_calendar(test_session)
        print(f"✅ 学習カレンダー機能: {len(calendar_data)}日分のデータ")
        
        # バッジ情報取得テスト
        badge_info = gm.get_badge_info('first_quiz')
        print(f"✅ バッジ情報取得: {badge_info['name']}")
        
        print("\n🎉 全ての機能テストが成功しました！")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_achievement_badges():
    """バッジシステムの詳細テスト"""
    print("\n🏆 バッジシステム詳細テスト")
    
    try:
        from gamification import ACHIEVEMENT_BADGES
        
        print(f"登録されたバッジ数: {len(ACHIEVEMENT_BADGES)}")
        
        for badge_id, badge_info in ACHIEVEMENT_BADGES.items():
            required_keys = ['name', 'description', 'icon', 'color']
            missing_keys = [key for key in required_keys if key not in badge_info]
            
            if missing_keys:
                print(f"❌ バッジ '{badge_id}' に不足キー: {missing_keys}")
            else:
                print(f"✅ バッジ '{badge_id}': {badge_info['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ バッジシステムエラー: {e}")
        return False

def simulate_learning_session():
    """学習セッションのシミュレーション"""
    print("\n📚 学習セッションシミュレーション")
    
    try:
        from gamification import GamificationManager
        
        gm = GamificationManager()
        
        # シミュレーション用セッション
        session = {
            'history': [],
            'category_stats': {},
            'earned_badges': []
        }
        
        # 複数日にわたる学習をシミュレート
        for day in range(8):  # 8日間の学習
            current_date = datetime.now() - timedelta(days=7-day)
            
            # 1日10問のシミュレート
            for q in range(10):
                history_item = {
                    'id': q + 1,
                    'category': 'コンクリート' if q % 2 == 0 else '構造',
                    'is_correct': q < 7,  # 70%の正答率
                    'date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'elapsed': 25.0 + (q * 2)  # 25-43秒の範囲
                }
                session['history'].append(history_item)
            
            # カテゴリ統計更新
            for category in ['コンクリート', '構造']:
                if category not in session['category_stats']:
                    session['category_stats'][category] = {'total': 0, 'correct': 0}
                session['category_stats'][category]['total'] += 5
                session['category_stats'][category]['correct'] += 3  # 60%正答率
            
            # ストリーク更新（最後の日のみ）
            if day == 7:
                streak, badges = gm.update_streak(session)
                print(f"Day {day+1}: ストリーク {streak}日, 新バッジ: {badges}")
        
        # バッジチェック
        performance = {'accuracy': 0.7, 'questions': 80}
        new_badges = gm.check_badges(session, performance)
        print(f"シミュレーション終了: 新バッジ {len(new_badges)}個獲得")
        
        # インサイト表示
        insights = gm.get_study_insights(session)
        print(f"学習統計: 総問題数{insights['total_questions']}, 正答率{insights['overall_accuracy']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ シミュレーションエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("RCCM Quiz App - Gamification Feature Test")
    print("=" * 50)
    
    # 基本機能テスト
    test1 = test_gamification()
    
    # バッジシステムテスト
    test2 = test_achievement_badges()
    
    # 学習セッションシミュレーション
    test3 = simulate_learning_session()
    
    print("\n" + "=" * 50)
    if test1 and test2 and test3:
        print("🎉 全テスト成功！ゲーミフィケーション機能は正常に動作します。")
    else:
        print("❌ 一部のテストが失敗しました。")
    print("=" * 50)