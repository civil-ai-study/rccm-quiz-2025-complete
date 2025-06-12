"""
RCCM学習アプリ - AI弱点分析エンジン
学習データを分析して個人に最適化された学習プランを提案
"""

import math
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class AILearningAnalyzer:
    """AI駆動の学習分析エンジン"""
    
    def __init__(self):
        self.confidence_threshold = 0.7  # 分析結果の信頼度閾値
        self.min_samples = 5  # 分析に必要な最小サンプル数
        
    def analyze_weak_areas(self, user_session: Dict) -> Dict[str, Any]:
        """包括的な弱点分析"""
        history = user_session.get('history', [])
        if len(history) < self.min_samples:
            return self._insufficient_data_response()
        
        # 複数の角度から弱点を分析
        category_analysis = self._analyze_by_category(history)
        difficulty_analysis = self._analyze_by_difficulty(history)
        time_analysis = self._analyze_response_time(history)
        trend_analysis = self._analyze_learning_trend(history)
        error_pattern_analysis = self._analyze_error_patterns(history)
        
        # 総合的な弱点スコア計算
        weak_areas = self._calculate_comprehensive_weakness_score(
            category_analysis, difficulty_analysis, time_analysis, 
            trend_analysis, error_pattern_analysis
        )
        
        # 学習推奨プラン生成
        learning_plan = self._generate_learning_plan(weak_areas, history)
        
        return {
            'weak_areas': weak_areas,
            'learning_plan': learning_plan,
            'analysis_details': {
                'category': category_analysis,
                'difficulty': difficulty_analysis,
                'time': time_analysis,
                'trend': trend_analysis,
                'error_patterns': error_pattern_analysis
            },
            'confidence_score': self._calculate_confidence_score(len(history)),
            'recommendation_priority': self._prioritize_recommendations(weak_areas)
        }
    
    def _analyze_by_category(self, history: List[Dict]) -> Dict[str, Any]:
        """カテゴリ別分析"""
        category_stats = defaultdict(lambda: {
            'total': 0, 'correct': 0, 'avg_time': 0, 'recent_performance': []
        })
        
        # 最近30問の重み付け分析
        recent_history = history[-30:] if len(history) > 30 else history
        
        for i, entry in enumerate(history):
            category = entry.get('category', '不明')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            
            # 時間重み（最近の問題ほど重要）
            weight = 1.0 if i < len(history) - 30 else (i - (len(history) - 30)) / 30 + 1.0
            
            category_stats[category]['total'] += weight
            if is_correct:
                category_stats[category]['correct'] += weight
            category_stats[category]['avg_time'] += elapsed_time * weight
            
            # 最近のパフォーマンス追跡
            if i >= len(history) - 10:  # 最近10問
                category_stats[category]['recent_performance'].append(is_correct)
        
        # 分析結果の計算
        analysis = {}
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                avg_time = stats['avg_time'] / stats['total']
                recent_accuracy = (
                    sum(stats['recent_performance']) / len(stats['recent_performance'])
                    if stats['recent_performance'] else accuracy
                )
                
                # 弱点度合いの計算（0-1, 1が最も弱い）
                weakness_score = self._calculate_category_weakness(
                    accuracy, recent_accuracy, avg_time, stats['total']
                )
                
                analysis[category] = {
                    'accuracy': accuracy,
                    'recent_accuracy': recent_accuracy,
                    'avg_time': avg_time,
                    'total_questions': int(stats['total']),
                    'weakness_score': weakness_score,
                    'improvement_trend': recent_accuracy - accuracy,
                    'confidence': min(stats['total'] / 20, 1.0)  # 20問で100%信頼度
                }
        
        return analysis
    
    def _analyze_by_difficulty(self, history: List[Dict]) -> Dict[str, Any]:
        """難易度別分析"""
        difficulty_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        for entry in history:
            difficulty = entry.get('difficulty', '標準')
            is_correct = entry.get('is_correct', False)
            
            difficulty_stats[difficulty]['total'] += 1
            if is_correct:
                difficulty_stats[difficulty]['correct'] += 1
        
        analysis = {}
        for difficulty, stats in difficulty_stats.items():
            if stats['total'] >= 3:  # 最低3問以上
                accuracy = stats['correct'] / stats['total']
                analysis[difficulty] = {
                    'accuracy': accuracy,
                    'total_questions': stats['total'],
                    'weakness_score': 1 - accuracy,
                    'sample_size': 'sufficient' if stats['total'] >= 10 else 'limited'
                }
        
        return analysis
    
    def _analyze_response_time(self, history: List[Dict]) -> Dict[str, Any]:
        """回答時間分析"""
        times = [entry.get('elapsed', 0) for entry in history if entry.get('elapsed', 0) > 0]
        correct_times = [
            entry.get('elapsed', 0) for entry in history 
            if entry.get('is_correct', False) and entry.get('elapsed', 0) > 0
        ]
        incorrect_times = [
            entry.get('elapsed', 0) for entry in history 
            if not entry.get('is_correct', False) and entry.get('elapsed', 0) > 0
        ]
        
        if not times:
            return {}
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        
        analysis = {
            'avg_time': avg_time,
            'median_time': median_time,
            'time_consistency': 1 - (statistics.stdev(times) / avg_time) if len(times) > 1 else 1,
            'speed_category': self._categorize_speed(avg_time),
        }
        
        if correct_times and incorrect_times:
            analysis['correct_vs_incorrect'] = {
                'correct_avg': statistics.mean(correct_times),
                'incorrect_avg': statistics.mean(incorrect_times),
                'time_difference': statistics.mean(incorrect_times) - statistics.mean(correct_times)
            }
        
        return analysis
    
    def _analyze_learning_trend(self, history: List[Dict]) -> Dict[str, Any]:
        """学習傾向分析"""
        if len(history) < 10:
            return {'trend': 'insufficient_data'}
        
        # 時系列での正答率変化
        window_size = min(10, len(history) // 3)
        accuracy_trend = []
        
        for i in range(window_size, len(history) + 1, window_size):
            window = history[i-window_size:i]
            accuracy = sum(1 for entry in window if entry.get('is_correct', False)) / len(window)
            accuracy_trend.append(accuracy)
        
        # 傾向計算
        if len(accuracy_trend) >= 2:
            recent_trend = accuracy_trend[-1] - accuracy_trend[-2] if len(accuracy_trend) >= 2 else 0
            overall_trend = accuracy_trend[-1] - accuracy_trend[0]
        else:
            recent_trend = overall_trend = 0
        
        # 学習安定性
        stability = 1 - statistics.stdev(accuracy_trend) if len(accuracy_trend) > 1 else 0
        
        return {
            'trend': 'improving' if overall_trend > 0.1 else 'declining' if overall_trend < -0.1 else 'stable',
            'recent_trend': recent_trend,
            'overall_trend': overall_trend,
            'stability': stability,
            'accuracy_points': accuracy_trend,
            'volatility': statistics.stdev(accuracy_trend) if len(accuracy_trend) > 1 else 0
        }
    
    def _analyze_error_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """エラーパターン分析"""
        incorrect_answers = [
            entry for entry in history if not entry.get('is_correct', False)
        ]
        
        if len(incorrect_answers) < 3:
            return {'pattern': 'insufficient_errors'}
        
        # 時間帯別エラー率
        hour_errors = defaultdict(lambda: {'total': 0, 'errors': 0})
        for entry in history:
            try:
                hour = datetime.fromisoformat(entry.get('date', '')).hour
                hour_errors[hour]['total'] += 1
                if not entry.get('is_correct', False):
                    hour_errors[hour]['errors'] += 1
            except:
                continue
        
        worst_hours = []
        for hour, stats in hour_errors.items():
            if stats['total'] >= 3:
                error_rate = stats['errors'] / stats['total']
                worst_hours.append((hour, error_rate))
        
        worst_hours.sort(key=lambda x: x[1], reverse=True)
        
        # カテゴリ別連続エラー
        category_streaks = self._find_error_streaks_by_category(history)
        
        return {
            'total_errors': len(incorrect_answers),
            'error_rate': len(incorrect_answers) / len(history),
            'worst_performance_hours': worst_hours[:3],
            'category_error_streaks': category_streaks,
            'error_distribution': self._calculate_error_distribution(incorrect_answers)
        }
    
    def _calculate_category_weakness(self, accuracy: float, recent_accuracy: float, 
                                   avg_time: float, sample_size: float) -> float:
        """カテゴリの弱点度合いを計算（0-1, 1が最も弱い）"""
        # 基本弱点スコア（正答率の逆数）
        base_weakness = 1 - accuracy
        
        # 最近のパフォーマンス考慮
        trend_factor = 1 - recent_accuracy
        
        # 時間効率考慮（60秒を基準）
        time_factor = min(avg_time / 60, 2) - 1  # -1〜1の範囲
        time_factor = max(0, time_factor) * 0.3  # 時間は30%の重み
        
        # サンプルサイズによる信頼度調整
        confidence = min(sample_size / 20, 1.0)
        
        # 統合スコア計算
        weakness_score = (base_weakness * 0.4 + trend_factor * 0.4 + time_factor) * confidence
        
        return min(max(weakness_score, 0), 1)
    
    def _calculate_comprehensive_weakness_score(self, category_analysis: Dict, 
                                              difficulty_analysis: Dict, 
                                              time_analysis: Dict,
                                              trend_analysis: Dict, 
                                              error_analysis: Dict) -> Dict[str, Any]:
        """複数の分析結果を統合して包括的な弱点スコアを計算"""
        weak_areas = {}
        
        # カテゴリ別弱点の基本スコア
        for category, analysis in category_analysis.items():
            weakness_score = analysis['weakness_score']
            confidence = analysis['confidence']
            
            # トレンド分析による調整
            if trend_analysis.get('trend') == 'declining':
                weakness_score *= 1.2
            elif trend_analysis.get('trend') == 'improving':
                weakness_score *= 0.8
            
            # エラーパターンによる調整
            if category in error_analysis.get('category_error_streaks', {}):
                weakness_score *= 1.15
            
            weak_areas[category] = {
                'weakness_score': min(weakness_score, 1.0),
                'confidence': confidence,
                'priority': self._calculate_priority(weakness_score, confidence),
                'recommended_focus': self._get_focus_recommendation(analysis),
                'details': analysis
            }
        
        return weak_areas
    
    def _generate_learning_plan(self, weak_areas: Dict, history: List[Dict]) -> Dict[str, Any]:
        """個人化された学習プランを生成"""
        if not weak_areas:
            return self._generate_maintenance_plan(history)
        
        # 弱点エリアを優先度順にソート
        sorted_areas = sorted(
            weak_areas.items(), 
            key=lambda x: x[1]['priority'], 
            reverse=True
        )
        
        primary_focus = sorted_areas[0] if sorted_areas else None
        secondary_focus = sorted_areas[1] if len(sorted_areas) > 1 else None
        
        plan = {
            'plan_type': 'weakness_focused',
            'primary_focus': {
                'category': primary_focus[0],
                'recommended_questions': min(15, max(10, int(20 * primary_focus[1]['weakness_score']))),
                'study_approach': self._get_study_approach(primary_focus[1]),
                'expected_improvement_days': self._estimate_improvement_time(primary_focus[1])
            } if primary_focus else None,
            
            'secondary_focus': {
                'category': secondary_focus[0],
                'recommended_questions': 5,
                'study_approach': 'review_and_practice'
            } if secondary_focus else None,
            
            'review_sessions': self._plan_review_sessions(history),
            'daily_recommendation': self._generate_daily_recommendation(weak_areas, history),
            'motivation_message': self._generate_motivation_message(weak_areas, history)
        }
        
        return plan
    
    def _generate_daily_recommendation(self, weak_areas: Dict, history: List[Dict]) -> Dict[str, Any]:
        """日々の学習推奨を生成"""
        total_questions = len(history)
        
        if total_questions < 20:
            return {
                'type': 'foundation_building',
                'recommended_questions': 10,
                'focus': 'broad_exposure',
                'message': '幅広い分野の基礎固めをしましょう'
            }
        
        if weak_areas:
            primary_weakness = max(weak_areas.items(), key=lambda x: x[1]['priority'])
            return {
                'type': 'targeted_improvement',
                'recommended_questions': 8,
                'focus': primary_weakness[0],
                'message': f'{primary_weakness[0]}の強化に集中しましょう',
                'specific_advice': self._get_specific_advice(primary_weakness[1])
            }
        
        return {
            'type': 'maintenance',
            'recommended_questions': 5,
            'focus': 'mixed_review',
            'message': '学習成果を維持し、さらなる向上を目指しましょう'
        }
    
    def _insufficient_data_response(self) -> Dict[str, Any]:
        """データ不足時のレスポンス"""
        return {
            'weak_areas': {},
            'learning_plan': {
                'plan_type': 'data_collection',
                'recommended_questions': 10,
                'message': 'より正確な分析のため、さらに問題に挑戦してください',
                'focus': 'broad_exposure'
            },
            'analysis_details': {},
            'confidence_score': 0.0,
            'recommendation_priority': []
        }
    
    def _calculate_confidence_score(self, total_questions: int) -> float:
        """分析の信頼度スコアを計算"""
        if total_questions < 10:
            return 0.3
        elif total_questions < 30:
            return 0.6
        elif total_questions < 100:
            return 0.8
        else:
            return 0.95
    
    def _categorize_speed(self, avg_time: float) -> str:
        """回答速度のカテゴリ化"""
        if avg_time < 20:
            return 'very_fast'
        elif avg_time < 40:
            return 'fast'
        elif avg_time < 60:
            return 'normal'
        elif avg_time < 90:
            return 'slow'
        else:
            return 'very_slow'
    
    def _calculate_priority(self, weakness_score: float, confidence: float) -> float:
        """優先度の計算"""
        return weakness_score * confidence
    
    def _get_focus_recommendation(self, analysis: Dict) -> str:
        """学習重点推奨"""
        accuracy = analysis.get('accuracy', 0)
        avg_time = analysis.get('avg_time', 0)
        
        if accuracy < 0.5:
            return 'fundamental_review'
        elif accuracy < 0.7:
            return 'targeted_practice'
        elif avg_time > 60:
            return 'speed_improvement'
        else:
            return 'advanced_challenge'
    
    def _get_study_approach(self, weakness_info: Dict) -> str:
        """学習アプローチの推奨"""
        score = weakness_info.get('weakness_score', 0)
        if score > 0.7:
            return 'intensive_study'
        elif score > 0.4:
            return 'regular_practice'
        else:
            return 'light_review'
    
    def _estimate_improvement_time(self, weakness_info: Dict) -> int:
        """改善予想日数"""
        score = weakness_info.get('weakness_score', 0)
        confidence = weakness_info.get('confidence', 0.5)
        
        base_days = int(score * 14)  # 最大2週間
        confidence_factor = 2 - confidence  # 信頼度が低いほど時間がかかる
        
        return max(3, int(base_days * confidence_factor))
    
    def _find_error_streaks_by_category(self, history: List[Dict]) -> Dict[str, int]:
        """カテゴリ別の連続エラー数を検出"""
        category_streaks = {}
        current_streaks = defaultdict(int)
        
        for entry in history:
            category = entry.get('category', '不明')
            is_correct = entry.get('is_correct', False)
            
            if not is_correct:
                current_streaks[category] += 1
            else:
                if current_streaks[category] > 2:  # 3回以上の連続エラー
                    category_streaks[category] = max(
                        category_streaks.get(category, 0), 
                        current_streaks[category]
                    )
                current_streaks[category] = 0
        
        return category_streaks
    
    def _calculate_error_distribution(self, incorrect_answers: List[Dict]) -> Dict[str, float]:
        """エラーの分布を計算"""
        categories = [entry.get('category', '不明') for entry in incorrect_answers]
        category_counts = Counter(categories)
        total_errors = len(incorrect_answers)
        
        return {
            category: count / total_errors 
            for category, count in category_counts.items()
        }
    
    def _plan_review_sessions(self, history: List[Dict]) -> Dict[str, Any]:
        """復習セッションの計画"""
        total_questions = len(history)
        if total_questions < 20:
            return {'frequency': 'daily', 'questions_per_session': 5}
        elif total_questions < 100:
            return {'frequency': 'every_2_days', 'questions_per_session': 8}
        else:
            return {'frequency': 'every_3_days', 'questions_per_session': 10}
    
    def _generate_maintenance_plan(self, history: List[Dict]) -> Dict[str, Any]:
        """維持レベルの学習プラン"""
        return {
            'plan_type': 'maintenance',
            'daily_recommendation': {
                'type': 'maintenance',
                'recommended_questions': 5,
                'focus': 'mixed_review',
                'message': '素晴らしい学習成果を維持し、さらなる向上を目指しましょう'
            },
            'motivation_message': '全体的に優秀な成績です。継続的な学習で更なる高みを目指しましょう！'
        }
    
    def _generate_motivation_message(self, weak_areas: Dict, history: List[Dict]) -> str:
        """やる気を引き出すメッセージ生成"""
        total_questions = len(history)
        overall_accuracy = sum(1 for entry in history if entry.get('is_correct', False)) / total_questions
        
        if overall_accuracy > 0.8:
            return "素晴らしい成績です！弱点を克服すれば完璧に近づけます。"
        elif overall_accuracy > 0.6:
            return "良いペースで学習が進んでいます。重点分野を集中的に学習しましょう。"
        else:
            return "着実に基礎を固めていきましょう。継続が力になります。"
    
    def _get_specific_advice(self, weakness_info: Dict) -> str:
        """具体的なアドバイス生成"""
        score = weakness_info.get('weakness_score', 0)
        details = weakness_info.get('details', {})
        
        if score > 0.7:
            return "基礎から復習することをお勧めします。解説をしっかり読んで理解を深めましょう。"
        elif score > 0.4:
            return "間違えた問題の解説を重点的に確認し、類似問題で練習しましょう。"
        else:
            return "もう少しで完璧です！反復練習で確実な知識にしましょう。"
    
    def prioritize_recommendations(self, weak_areas: Dict) -> List[Dict[str, Any]]:
        """推奨事項の優先順位付け"""
        return self._prioritize_recommendations(weak_areas)
    
    def _prioritize_recommendations(self, weak_areas: Dict) -> List[Dict[str, Any]]:
        """推奨事項の優先順位付け（内部メソッド）"""
        recommendations = []
        
        for category, info in weak_areas.items():
            priority_score = info.get('priority', 0)
            if priority_score > 0.3:  # 閾値以上の弱点のみ
                recommendations.append({
                    'category': category,
                    'priority_score': priority_score,
                    'action': info.get('recommended_focus', 'practice'),
                    'urgency': 'high' if priority_score > 0.7 else 'medium' if priority_score > 0.5 else 'low'
                })
        
        return sorted(recommendations, key=lambda x: x['priority_score'], reverse=True)

# グローバルインスタンス
ai_analyzer = AILearningAnalyzer()