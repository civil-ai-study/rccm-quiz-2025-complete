"""
RCCM学習アプリ - ゲーミフィケーション機能
バッジシステム、ストリーク管理、学習カレンダー
"""

from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# バッジ定義
ACHIEVEMENT_BADGES = {
    'first_quiz': {
        'name': '初回問題完了',
        'description': '初めて問題を完了しました！',
        'icon': '🎯',
        'color': 'primary'
    },
    'perfect_score': {
        'name': '満点達成',
        'description': '問題で満点を獲得しました！',
        'icon': '💯',
        'color': 'success'
    },
    'category_master_concrete': {
        'name': 'コンクリートマスター',
        'description': 'コンクリート分野で80%以上の正答率を達成',
        'icon': '🏗️',
        'color': 'info'
    },
    'category_master_structure': {
        'name': '構造マスター',
        'description': '構造分野で80%以上の正答率を達成',
        'icon': '🏢',
        'color': 'info'
    },
    'speed_demon': {
        'name': 'スピードデーモン',
        'description': '平均回答時間が30秒以下を達成',
        'icon': '⚡',
        'color': 'warning'
    },
    'comeback_kid': {
        'name': 'カムバック',
        'description': '50%以下から80%以上に改善',
        'icon': '💪',
        'color': 'danger'
    },
    'night_owl': {
        'name': '夜更かし勉強',
        'description': '深夜（22時以降）に学習完了',
        'icon': '🦉',
        'color': 'dark'
    },
    'early_bird': {
        'name': '早起き勉強',
        'description': '早朝（6時前）に学習完了',
        'icon': '🐦',
        'color': 'info'
    },
    'study_streak_7': {
        'name': '7日連続学習',
        'description': '7日間連続で学習を続けました',
        'icon': '🔥',
        'color': 'warning'
    },
    'study_streak_30': {
        'name': '30日連続学習',
        'description': '30日間連続で学習を続けました',
        'icon': '👑',
        'color': 'success'
    },
    'hundred_questions': {
        'name': '百問達成',
        'description': '累計100問に回答しました',
        'icon': '💯',
        'color': 'primary'
    },
    'accuracy_master': {
        'name': '正答率マスター',
        'description': '全体正答率90%以上を達成',
        'icon': '🎖️',
        'color': 'success'
    }
}

class GamificationManager:
    """ゲーミフィケーション機能の管理クラス"""
    
    def __init__(self):
        self.achievements = ACHIEVEMENT_BADGES
    
    def update_streak(self, user_session):
        """学習ストリークの更新"""
        today = datetime.now().date()
        last_study = user_session.get('last_study_date')
        current_streak = user_session.get('study_streak', 0)
        max_streak = user_session.get('max_study_streak', 0)
        
        # 文字列を日付オブジェクトに変換
        if isinstance(last_study, str):
            try:
                last_study = datetime.fromisoformat(last_study).date()
            except:
                last_study = None
        
        if last_study is None:
            # 初回学習
            current_streak = 1
        elif (today - last_study).days == 1:
            # 連続学習
            current_streak += 1
        elif (today - last_study).days == 0:
            # 同日学習（ストリーク維持）
            pass
        else:
            # ストリーク途切れ
            current_streak = 1
        
        # 最大ストリーク更新
        max_streak = max(max_streak, current_streak)
        
        user_session['study_streak'] = current_streak
        user_session['max_study_streak'] = max_streak
        user_session['last_study_date'] = today.isoformat()
        
        logger.info(f"ストリーク更新: {current_streak}日連続")
        
        # ストリークバッジの確認
        new_badges = []
        if current_streak == 7:
            new_badges.append('study_streak_7')
        elif current_streak == 30:
            new_badges.append('study_streak_30')
        
        return current_streak, new_badges
    
    def check_badges(self, user_session, recent_performance=None):
        """新しいバッジの確認"""
        earned_badges = user_session.get('earned_badges', [])
        new_badges = []
        
        history = user_session.get('history', [])
        if not history:
            return new_badges
        
        # 統計計算
        total_questions = len(history)
        correct_count = sum(1 for h in history if h.get('is_correct'))
        accuracy = correct_count / total_questions if total_questions > 0 else 0
        
        # 初回問題バッジ
        if 'first_quiz' not in earned_badges and total_questions >= 1:
            new_badges.append('first_quiz')
        
        # 百問達成バッジ
        if 'hundred_questions' not in earned_badges and total_questions >= 100:
            new_badges.append('hundred_questions')
        
        # 正答率マスターバッジ
        if 'accuracy_master' not in earned_badges and accuracy >= 0.9 and total_questions >= 50:
            new_badges.append('accuracy_master')
        
        # 満点バッジ（最新セッション）
        if recent_performance and 'perfect_score' not in earned_badges:
            if recent_performance.get('accuracy') == 1.0:
                new_badges.append('perfect_score')
        
        # カテゴリマスターバッジ
        category_stats = user_session.get('category_stats', {})
        for category, stats in category_stats.items():
            badge_key = f"category_master_{category.lower().replace(' ', '_')}"
            if badge_key in self.achievements and badge_key not in earned_badges:
                if stats.get('total', 0) >= 20 and (stats.get('correct', 0) / stats.get('total', 1)) >= 0.8:
                    new_badges.append(badge_key)
        
        # スピードデーモンバッジ
        if 'speed_demon' not in earned_badges and total_questions >= 30:
            avg_time = sum(h.get('elapsed', 0) for h in history) / total_questions
            if avg_time <= 30:
                new_badges.append('speed_demon')
        
        # 時間帯バッジ
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 2:
            if 'night_owl' not in earned_badges:
                new_badges.append('night_owl')
        elif current_hour <= 6:
            if 'early_bird' not in earned_badges:
                new_badges.append('early_bird')
        
        # カムバックバッジ（前半50問と後半50問の比較）
        if 'comeback_kid' not in earned_badges and total_questions >= 100:
            first_half = history[:50]
            last_half = history[-50:]
            
            first_accuracy = sum(1 for h in first_half if h.get('is_correct')) / 50
            last_accuracy = sum(1 for h in last_half if h.get('is_correct')) / 50
            
            if first_accuracy <= 0.5 and last_accuracy >= 0.8:
                new_badges.append('comeback_kid')
        
        # 新しいバッジを記録
        for badge in new_badges:
            if badge not in earned_badges:
                earned_badges.append(badge)
        
        user_session['earned_badges'] = earned_badges
        
        if new_badges:
            logger.info(f"新しいバッジ獲得: {new_badges}")
        
        return new_badges
    
    def get_badge_info(self, badge_id):
        """バッジ情報の取得"""
        return self.achievements.get(badge_id, {
            'name': 'Unknown Badge',
            'description': '',
            'icon': '🏆',
            'color': 'secondary'
        })
    
    def generate_study_calendar(self, user_session, months=3):
        """学習カレンダーデータの生成"""
        history = user_session.get('history', [])
        calendar_data = defaultdict(lambda: {
            'questions': 0,
            'correct': 0,
            'study_time': 0,
            'sessions': 0
        })
        
        # 日付別の学習データを集計
        session_dates = set()
        for entry in history:
            date_str = entry.get('date', '')[:10]
            if date_str:
                calendar_data[date_str]['questions'] += 1
                if entry.get('is_correct'):
                    calendar_data[date_str]['correct'] += 1
                calendar_data[date_str]['study_time'] += entry.get('elapsed', 0)
                session_dates.add(date_str)
        
        # セッション数を計算
        for date in session_dates:
            calendar_data[date]['sessions'] = 1  # 簡易版：1日1セッション
        
        # 指定月数分のデータを生成
        today = datetime.now().date()
        start_date = today - timedelta(days=30 * months)
        
        result = {}
        current_date = start_date
        while current_date <= today:
            date_str = current_date.isoformat()
            data = calendar_data.get(date_str, {
                'questions': 0, 'correct': 0, 'study_time': 0, 'sessions': 0
            })
            
            # カレンダー表示用の追加情報
            data['date'] = date_str
            data['accuracy'] = data['correct'] / data['questions'] if data['questions'] > 0 else 0
            data['intensity'] = min(data['questions'] / 10, 1.0)  # 学習強度（0-1）
            
            result[date_str] = data
            current_date += timedelta(days=1)
        
        return result
    
    def get_study_insights(self, user_session):
        """学習インサイトの生成"""
        history = user_session.get('history', [])
        if not history:
            return {
                'total_questions': 0,
                'overall_accuracy': 0,
                'total_study_time': 0,
                'avg_time_per_question': 0,
                'recent_accuracy': 0,
                'study_streak': user_session.get('study_streak', 0),
                'max_streak': user_session.get('max_study_streak', 0),
                'peak_study_hour': 12,
                'strengths': [],
                'weaknesses': [],
                'badges_earned': len(user_session.get('earned_badges', [])),
                'improvement_trend': 0
            }
        
        # 基本統計
        total_questions = len(history)
        correct_count = sum(1 for h in history if h.get('is_correct'))
        total_time = sum(h.get('elapsed', 0) for h in history)
        
        # 最近の傾向（直近20問）
        recent_history = history[-20:] if len(history) >= 20 else history
        recent_accuracy = sum(1 for h in recent_history if h.get('is_correct')) / len(recent_history)
        
        # 学習パターン分析
        study_hours = defaultdict(int)
        for entry in history:
            date_str = entry.get('date', '')
            if date_str:
                try:
                    hour = datetime.fromisoformat(date_str).hour
                    study_hours[hour] += 1
                except:
                    pass
        
        peak_hour = max(study_hours.items(), key=lambda x: x[1])[0] if study_hours else 12
        
        # カテゴリ別強み・弱み
        category_stats = user_session.get('category_stats', {})
        strengths = []
        weaknesses = []
        
        for category, stats in category_stats.items():
            if stats.get('total', 0) >= 10:
                accuracy = stats.get('correct', 0) / stats.get('total', 1)
                if accuracy >= 0.8:
                    strengths.append(category)
                elif accuracy <= 0.6:
                    weaknesses.append(category)
        
        return {
            'total_questions': total_questions,
            'overall_accuracy': correct_count / total_questions,
            'total_study_time': total_time,
            'avg_time_per_question': total_time / total_questions,
            'recent_accuracy': recent_accuracy,
            'study_streak': user_session.get('study_streak', 0),
            'max_streak': user_session.get('max_study_streak', 0),
            'peak_study_hour': peak_hour,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'badges_earned': len(user_session.get('earned_badges', [])),
            'improvement_trend': recent_accuracy - (correct_count / total_questions)
        }

# グローバルインスタンス
gamification_manager = GamificationManager()