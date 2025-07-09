"""
RCCM学習アプリ - 動的難易度制御システム
学習者のレベルに応じて問題難易度を自動調整
"""

import math
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import List, Dict, Any, Tuple
import logging

# RCCM設定をインポート
from config import RCCMConfig

logger = logging.getLogger(__name__)

class DynamicDifficultyController:
    """動的難易度制御エンジン"""
    
    def __init__(self):
        # 難易度レベル定義（日本語難易度値対応）
        self.difficulty_levels = {
            'beginner': {
                'name': '初級',
                'target_accuracy': 0.75,
                'time_multiplier': 1.3,
                'question_types': ['basic'],
                'difficulties': ['基本', 'basic', '標準'],  # 日本語対応
                'learning_boost': 1.2
            },
            'intermediate': {
                'name': '中級',
                'target_accuracy': 0.65,
                'time_multiplier': 1.0,
                'question_types': ['basic', 'specialist'],
                'difficulties': ['基本', 'basic', '標準', 'standard'],  # 日本語対応
                'learning_boost': 1.0
            },
            'advanced': {
                'name': '上級',
                'target_accuracy': 0.55,
                'time_multiplier': 0.8,
                'question_types': ['basic', 'specialist'],
                'difficulties': ['標準', 'standard', '応用', 'advanced'],  # 日本語対応
                'learning_boost': 0.8
            },
            'expert': {
                'name': '専門家',
                'target_accuracy': 0.45,
                'time_multiplier': 0.7,
                'question_types': ['specialist'],
                'difficulties': ['応用', 'advanced', '上級', 'expert', '標準'],  # 日本語対応＋フォールバック
                'learning_boost': 0.6
            }
        }
        
        # 調整パラメータ
        self.adjustment_sensitivity = 0.1  # 調整の敏感度
        self.stability_threshold = 5  # 安定性判定の最小サンプル数
        self.performance_window = 20  # パフォーマンス評価の窓サイズ
        self.confidence_threshold = 0.7  # 難易度変更の信頼度閾値
        
        # 部門別難易度調整係数
        self.department_difficulty_factors = {
            'road': 1.0,  # 基準
            'civil_planning': 1.15,  # やや難しい
            'construction_env': 1.1,
            'comprehensive': 1.25,  # 最難関
            'port_airport': 1.05,
            'railway': 1.05,
            'urban_planning': 1.1,
            'construction_mgmt': 1.1,
            'power_civil': 1.2,
            'forestry': 1.0,
            'fisheries': 1.0,
            'agriculture': 1.0
        }
        
    def assess_learner_level(self, user_session: Dict, department: str = None) -> Dict[str, Any]:
        """学習者レベルの総合評価"""
        history = user_session.get('history', [])
        
        # 部門フィルタリング
        if department:
            history = [h for h in history if h.get('department') == department]
        
        if len(history) < 5:
            return self._initial_assessment()
        
        # 複数の指標で評価
        accuracy_assessment = self._assess_accuracy_level(history)
        speed_assessment = self._assess_speed_level(history)
        consistency_assessment = self._assess_consistency_level(history)
        progression_assessment = self._assess_progression_level(history)
        
        # 部門特有の調整
        department_factor = self.department_difficulty_factors.get(department, 1.0)
        
        # 総合レベル計算
        overall_level = self._calculate_overall_level(
            accuracy_assessment, speed_assessment, 
            consistency_assessment, progression_assessment, 
            department_factor
        )
        
        # 推奨難易度決定
        recommended_difficulty = self._determine_recommended_difficulty(overall_level, history)
        
        return {
            'overall_level': overall_level,
            'level_name': self.difficulty_levels[overall_level]['name'],
            'recommended_difficulty': recommended_difficulty,
            'assessments': {
                'accuracy': accuracy_assessment,
                'speed': speed_assessment,
                'consistency': consistency_assessment,
                'progression': progression_assessment
            },
            'department_factor': department_factor,
            'confidence': self._calculate_assessment_confidence(len(history)),
            'next_adjustment_threshold': self._get_next_adjustment_threshold(overall_level)
        }
    
    def adjust_question_difficulty(self, questions: List[Dict], learner_assessment: Dict, 
                                 target_count: int) -> List[Dict]:
        """学習者レベルに基づく問題難易度調整（日本語データ対応）"""
        
        level = learner_assessment['overall_level']
        level_config = self.difficulty_levels[level]
        
        logger.debug(f"難易度調整開始: レベル={level}, 対象問題数={len(questions)}, 要求数={target_count}")
        
        # 問題タイプでフィルタリング（まずここで基本的な絞り込み）
        type_filtered = [
            q for q in questions 
            if q.get('question_type') in level_config['question_types']
        ]
        
        logger.debug(f"問題タイプフィルタ後: {len(type_filtered)}問 (許可タイプ: {level_config['question_types']})")
        
        # 難易度でフィルタリング（日本語対応）
        suitable_questions = [
            q for q in type_filtered 
            if q.get('difficulty', '標準') in level_config['difficulties']
        ]
        
        logger.debug(f"難易度フィルタ後: {len(suitable_questions)}問 (許可難易度: {level_config['difficulties']})")
        
        # フィルタ結果が少なすぎる場合の安全措置
        if len(suitable_questions) == 0:
            logger.warning(f"⚠️ 難易度フィルタで全問題が除外されました。問題タイプフィルタ結果を使用します。")
            suitable_questions = type_filtered
        
        if len(suitable_questions) < target_count:
            # 不足分は隣接レベルから補完
            adjacent_questions = self._get_adjacent_level_questions(
                questions, level, target_count - len(suitable_questions)
            )
            suitable_questions.extend(adjacent_questions)
            logger.debug(f"隣接レベル補完後: {len(suitable_questions)}問")
        
        # 学習促進のための微調整
        adjusted_questions = self._apply_learning_boost(suitable_questions, level_config, target_count)
        
        final_count = min(len(adjusted_questions), target_count)
        logger.info(f"難易度調整完了: {len(questions)}問 → {final_count}問 (レベル: {level})")
        
        return adjusted_questions[:target_count]
    
    def get_dynamic_session_config(self, learner_assessment: Dict) -> Dict[str, Any]:
        """学習者レベルに基づく動的セッション設定"""
        
        level = learner_assessment['overall_level']
        level_config = self.difficulty_levels[level]
        
        # セッション設定を動的に調整
        config = {
            'target_accuracy': level_config['target_accuracy'],
            'time_limit_multiplier': level_config['time_multiplier'],
            'question_distribution': self._get_question_distribution(level),
            'feedback_intensity': self._get_feedback_intensity(level),
            'hint_availability': self._get_hint_availability(level),
            'review_frequency': self._get_review_frequency(level),
            'challenge_mode': level in ['advanced', 'expert']
        }
        
        return config
    
    def monitor_performance_and_adjust(self, user_session: Dict, recent_results: List[Dict]) -> Dict[str, Any]:
        """リアルタイムパフォーマンス監視と調整"""
        
        if len(recent_results) < self.stability_threshold:
            return {'adjustment_needed': False, 'reason': 'insufficient_data'}
        
        # 現在のパフォーマンス分析
        current_performance = self._analyze_current_performance(recent_results)
        
        # 期待パフォーマンスとの比較
        current_level = user_session.get('difficulty_level', 'intermediate')
        target_performance = self.difficulty_levels[current_level]['target_accuracy']
        
        performance_gap = current_performance['accuracy'] - target_performance
        
        # 調整の必要性判定
        adjustment_needed = abs(performance_gap) > self.adjustment_sensitivity
        
        if adjustment_needed:
            adjustment = self._calculate_difficulty_adjustment(
                performance_gap, current_performance, current_level
            )
            
            return {
                'adjustment_needed': True,
                'current_level': current_level,
                'suggested_level': adjustment['new_level'],
                'adjustment_reason': adjustment['reason'],
                'confidence': adjustment['confidence'],
                'performance_gap': performance_gap,
                'recommendations': adjustment['recommendations']
            }
        
        return {
            'adjustment_needed': False,
            'reason': 'performance_stable',
            'current_performance': current_performance
        }
    
    def _initial_assessment(self) -> Dict[str, Any]:
        """初期評価（履歴が少ない場合）"""
        return {
            'overall_level': 'intermediate',
            'level_name': '中級（初期設定）',
            'recommended_difficulty': 'standard',
            'assessments': {
                'accuracy': {'level': 'intermediate', 'score': 0.5},
                'speed': {'level': 'intermediate', 'score': 0.5},
                'consistency': {'level': 'intermediate', 'score': 0.5},
                'progression': {'level': 'intermediate', 'score': 0.5}
            },
            'department_factor': 1.0,
            'confidence': 0.3,
            'next_adjustment_threshold': 10
        }
    
    def _assess_accuracy_level(self, history: List[Dict]) -> Dict[str, Any]:
        """正答率レベルの評価"""
        
        recent_history = history[-self.performance_window:] if len(history) > self.performance_window else history
        
        if not recent_history:
            return {'level': 'intermediate', 'score': 0.5}
        
        # 全体正答率
        overall_accuracy = sum(1 for h in recent_history if h.get('is_correct', False)) / len(recent_history)
        
        # 難易度別正答率
        difficulty_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        for entry in recent_history:
            difficulty = entry.get('difficulty', '標準')
            difficulty_performance[difficulty]['total'] += 1
            if entry.get('is_correct', False):
                difficulty_performance[difficulty]['correct'] += 1
        
        # レベル判定
        if overall_accuracy >= 0.8:
            level = 'expert'
        elif overall_accuracy >= 0.7:
            level = 'advanced'
        elif overall_accuracy >= 0.6:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'level': level,
            'score': overall_accuracy,
            'overall_accuracy': overall_accuracy,
            'difficulty_breakdown': {
                diff: stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                for diff, stats in difficulty_performance.items()
            }
        }
    
    def _assess_speed_level(self, history: List[Dict]) -> Dict[str, Any]:
        """回答速度レベルの評価"""
        
        times = [h.get('elapsed', 0) for h in history if h.get('elapsed', 0) > 0]
        
        if not times:
            return {'level': 'intermediate', 'score': 0.5}
        
        try:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
        except (TypeError, ValueError, statistics.StatisticsError):
            return {'level': 'intermediate', 'score': 0.5}
        
        # 速度レベル判定（秒）
        if avg_time <= 30:
            level = 'expert'
        elif avg_time <= 45:
            level = 'advanced'
        elif avg_time <= 60:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        # 安定性評価
        consistency = 1
        if len(times) > 1 and avg_time > 0:
            try:
                stdev_time = statistics.stdev(times)
                consistency = 1 - (stdev_time / avg_time)
            except (TypeError, ValueError, statistics.StatisticsError, ZeroDivisionError):
                consistency = 1
        
        return {
            'level': level,
            'score': min(1.0, 90 / avg_time),  # 90秒を基準とした相対スコア
            'avg_time': avg_time,
            'median_time': median_time,
            'consistency': consistency
        }
    
    def _assess_consistency_level(self, history: List[Dict]) -> Dict[str, Any]:
        """一貫性レベルの評価"""
        
        if len(history) < 10:
            return {'level': 'intermediate', 'score': 0.5}
        
        # 最近20問の結果
        recent = history[-20:]
        results = [1 if h.get('is_correct', False) else 0 for h in recent]
        
        # 連続性の評価
        streaks = []
        current_streak = 1
        for i in range(1, len(results)):
            if results[i] == results[i-1]:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        streaks.append(current_streak)
        
        # 一貫性スコア
        try:
            avg_streak = statistics.mean(streaks) if streaks else 1
            max_streak = max(streaks) if streaks else 1
        except (TypeError, ValueError, statistics.StatisticsError):
            avg_streak = max_streak = 1
        
        # バリアンス（低いほど一貫）
        try:
            variance = statistics.variance(results) if len(results) > 1 else 0
        except (TypeError, ValueError, statistics.StatisticsError):
            variance = 0
        consistency_score = 1 - variance
        
        # レベル判定
        if consistency_score >= 0.8 and avg_streak <= 3:
            level = 'expert'  # 高い一貫性、適度な変化
        elif consistency_score >= 0.7:
            level = 'advanced'
        elif consistency_score >= 0.5:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'level': level,
            'score': consistency_score,
            'avg_streak': avg_streak,
            'max_streak': max_streak,
            'variance': variance
        }
    
    def _assess_progression_level(self, history: List[Dict]) -> Dict[str, Any]:
        """学習進歩レベルの評価"""
        
        if len(history) < 15:
            return {'level': 'intermediate', 'score': 0.5}
        
        # 時系列での正答率変化
        window_size = 5
        accuracies = []
        
        for i in range(window_size, len(history) + 1, window_size):
            window = history[i-window_size:i]
            accuracy = sum(1 for h in window if h.get('is_correct', False)) / len(window)
            accuracies.append(accuracy)
        
        if len(accuracies) < 2:
            return {'level': 'intermediate', 'score': 0.5}
        
        # 線形回帰による傾向分析
        x = list(range(len(accuracies)))
        y = accuracies
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # 傾き計算
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # 進歩レベル判定
        if slope > 0.05:
            level = 'expert'  # 急速な進歩
        elif slope > 0.02:
            level = 'advanced'  # 着実な進歩
        elif slope > -0.02:
            level = 'intermediate'  # 安定
        else:
            level = 'beginner'  # 下降傾向
        
        # 最近の改善度
        recent_improvement = accuracies[-1] - accuracies[0] if len(accuracies) >= 2 else 0
        
        return {
            'level': level,
            'score': max(0, min(1, slope * 10 + 0.5)),  # 傾きを0-1のスコアに変換
            'slope': slope,
            'recent_improvement': recent_improvement,
            'accuracy_trend': accuracies
        }
    
    def _calculate_overall_level(self, accuracy_assessment: Dict, speed_assessment: Dict,
                               consistency_assessment: Dict, progression_assessment: Dict,
                               department_factor: float) -> str:
        """総合レベルの計算"""
        
        # 各評価の重み
        weights = {
            'accuracy': 0.4,
            'speed': 0.2,
            'consistency': 0.2,
            'progression': 0.2
        }
        
        # レベルを数値に変換
        level_scores = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        
        # 重み付き平均
        weighted_score = (
            level_scores[accuracy_assessment['level']] * weights['accuracy'] +
            level_scores[speed_assessment['level']] * weights['speed'] +
            level_scores[consistency_assessment['level']] * weights['consistency'] +
            level_scores[progression_assessment['level']] * weights['progression']
        )
        
        # 部門難易度による調整
        adjusted_score = weighted_score / department_factor
        
        # レベル決定
        score_to_level = {
            1: 'beginner',
            2: 'intermediate',
            3: 'advanced',
            4: 'expert'
        }
        
        final_level = score_to_level[min(4, max(1, round(adjusted_score)))]
        
        return final_level
    
    def _determine_recommended_difficulty(self, level: str, history: List[Dict]) -> str:
        """推奨難易度の決定"""
        
        level_config = self.difficulty_levels[level]
        
        # 最近のパフォーマンスに基づく微調整
        recent_history = history[-10:] if len(history) > 10 else history
        
        if recent_history:
            recent_accuracy = sum(1 for h in recent_history if h.get('is_correct', False)) / len(recent_history)
            target_accuracy = level_config['target_accuracy']
            
            if recent_accuracy > target_accuracy + 0.1:
                # パフォーマンスが高い場合、少し難しく
                difficulties = level_config['difficulties']
                if len(difficulties) > 1:
                    return difficulties[-1]  # より難しい難易度
            elif recent_accuracy < target_accuracy - 0.1:
                # パフォーマンスが低い場合、少し易しく
                difficulties = level_config['difficulties']
                return difficulties[0]  # より易しい難易度
        
        # デフォルトの推奨難易度
        difficulties = level_config['difficulties']
        return difficulties[len(difficulties) // 2]  # 中間の難易度
    
    def _get_adjacent_level_questions(self, questions: List[Dict], current_level: str, needed_count: int) -> List[Dict]:
        """隣接レベルからの問題補完"""
        
        level_order = ['beginner', 'intermediate', 'advanced', 'expert']
        current_index = level_order.index(current_level)
        
        adjacent_questions = []
        
        # 上下のレベルから探索
        for offset in [1, -1, 2, -2]:
            if len(adjacent_questions) >= needed_count:
                break
                
            adj_index = current_index + offset
            if 0 <= adj_index < len(level_order):
                adj_level = level_order[adj_index]
                adj_config = self.difficulty_levels[adj_level]
                
                suitable = [
                    q for q in questions 
                    if (q.get('question_type') in adj_config['question_types'] and
                        q.get('difficulty', '標準') in adj_config['difficulties'] and
                        q not in adjacent_questions)
                ]
                
                adjacent_questions.extend(suitable[:needed_count - len(adjacent_questions)])
        
        return adjacent_questions
    
    def _apply_learning_boost(self, questions: List[Dict], level_config: Dict, target_count: int) -> List[Dict]:
        """学習促進のための問題調整"""
        
        boost_factor = level_config['learning_boost']
        
        if boost_factor > 1.0:
            # 学習促進が必要な場合、基礎問題を多めに
            basic_questions = [q for q in questions if q.get('question_type') == 'basic']
            specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
            
            basic_ratio = min(0.8, boost_factor - 0.2)
            basic_count = int(target_count * basic_ratio)
            specialist_count = target_count - basic_count
            
            selected = []
            selected.extend(basic_questions[:basic_count])
            selected.extend(specialist_questions[:specialist_count])
            
            return selected
        
        return questions
    
    def _get_question_distribution(self, level: str) -> Dict[str, float]:
        """問題タイプ分布の取得"""
        distributions = {
            'beginner': {'basic': 0.8, 'specialist': 0.2},
            'intermediate': {'basic': 0.6, 'specialist': 0.4},
            'advanced': {'basic': 0.4, 'specialist': 0.6},
            'expert': {'basic': 0.2, 'specialist': 0.8}
        }
        return distributions.get(level, {'basic': 0.5, 'specialist': 0.5})
    
    def _get_feedback_intensity(self, level: str) -> str:
        """フィードバック強度の取得"""
        intensities = {
            'beginner': 'detailed',
            'intermediate': 'standard',
            'advanced': 'concise',
            'expert': 'minimal'
        }
        return intensities.get(level, 'standard')
    
    def _get_hint_availability(self, level: str) -> bool:
        """ヒント利用可能性の判定"""
        return level in ['beginner', 'intermediate']
    
    def _get_review_frequency(self, level: str) -> int:
        """復習頻度の取得（問題数）"""
        frequencies = {
            'beginner': 3,  # 3問ごとに復習
            'intermediate': 5,
            'advanced': 7,
            'expert': 10
        }
        return frequencies.get(level, 5)
    
    def _analyze_current_performance(self, recent_results: List[Dict]) -> Dict[str, Any]:
        """現在のパフォーマンス分析"""
        
        accuracy = sum(1 for r in recent_results if r.get('is_correct', False)) / len(recent_results)
        
        times = [r.get('elapsed', 0) for r in recent_results if r.get('elapsed', 0) > 0]
        try:
            avg_time = statistics.mean(times) if times else 60
        except (TypeError, ValueError, statistics.StatisticsError):
            avg_time = 60
        
        return {
            'accuracy': accuracy,
            'avg_time': avg_time,
            'sample_size': len(recent_results),
            'trend': self._calculate_short_term_trend(recent_results)
        }
    
    def _calculate_short_term_trend(self, recent_results: List[Dict]) -> str:
        """短期トレンドの計算"""
        
        if len(recent_results) < 6:
            return 'stable'
        
        first_half = recent_results[:len(recent_results)//2]
        second_half = recent_results[len(recent_results)//2:]
        
        first_accuracy = sum(1 for r in first_half if r.get('is_correct', False)) / len(first_half)
        second_accuracy = sum(1 for r in second_half if r.get('is_correct', False)) / len(second_half)
        
        diff = second_accuracy - first_accuracy
        
        if diff > 0.1:
            return 'improving'
        elif diff < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_difficulty_adjustment(self, performance_gap: float, current_performance: Dict, current_level: str) -> Dict[str, Any]:
        """難易度調整の計算"""
        
        level_order = ['beginner', 'intermediate', 'advanced', 'expert']
        current_index = level_order.index(current_level)
        
        # 調整方向の決定
        if performance_gap > 0.15:  # パフォーマンスが高すぎる
            new_index = min(len(level_order) - 1, current_index + 1)
            reason = "パフォーマンスが期待を上回っているため、難易度を上げます"
        elif performance_gap < -0.15:  # パフォーマンスが低すぎる
            new_index = max(0, current_index - 1)
            reason = "パフォーマンスが期待を下回っているため、難易度を下げます"
        else:
            new_index = current_index
            reason = "パフォーマンスが適切範囲内のため、現在の難易度を維持します"
        
        new_level = level_order[new_index]
        
        # 信頼度計算
        confidence = min(1.0, abs(performance_gap) / 0.2)
        
        # 推奨事項
        recommendations = self._generate_adjustment_recommendations(current_level, new_level, current_performance)
        
        return {
            'new_level': new_level,
            'reason': reason,
            'confidence': confidence,
            'recommendations': recommendations
        }
    
    def _generate_adjustment_recommendations(self, current_level: str, new_level: str, performance: Dict) -> List[str]:
        """調整推奨事項の生成"""
        
        recommendations = []
        
        if new_level != current_level:
            level_names = {
                'beginner': '初級',
                'intermediate': '中級', 
                'advanced': '上級',
                'expert': '専門家'
            }
            
            recommendations.append(f"難易度を{level_names[current_level]}から{level_names[new_level]}に調整することを推奨します")
        
        if performance['avg_time'] > 90:
            recommendations.append("回答時間が長いため、基礎知識の復習を推奨します")
        elif performance['avg_time'] < 30:
            recommendations.append("回答が速すぎる可能性があります。慎重な検討を心がけてください")
        
        if performance['trend'] == 'declining':
            recommendations.append("最近の成績が下降傾向にあります。休息を取るか、基礎に戻ることを検討してください")
        elif performance['trend'] == 'improving':
            recommendations.append("成績が向上しています！この調子で学習を続けてください")
        
        return recommendations
    
    def _calculate_assessment_confidence(self, history_length: int) -> float:
        """評価信頼度の計算"""
        if history_length < 5:
            return 0.2
        elif history_length < 15:
            return 0.5
        elif history_length < 50:
            return 0.8
        else:
            return 0.95
    
    def _get_next_adjustment_threshold(self, current_level: str) -> int:
        """次回調整閾値の取得"""
        thresholds = {
            'beginner': 15,
            'intermediate': 20,
            'advanced': 25,
            'expert': 30
        }
        return thresholds.get(current_level, 20)

# グローバルインスタンス
difficulty_controller = DynamicDifficultyController()