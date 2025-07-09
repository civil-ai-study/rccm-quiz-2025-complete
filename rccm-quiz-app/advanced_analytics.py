"""
RCCM学習アプリ - 高度な統計分析エンジン
詳細な学習分析、予測モデル、比較分析を提供
"""

import statistics
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """高度な統計分析エンジン"""
    
    def __init__(self):
        self.confidence_levels = {
            'very_high': 0.9,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'very_low': 0.2
        }
    
    def analyze_time_series(self, history: List[Dict]) -> Dict[str, Any]:
        """時系列分析（高度分析用）"""
        if not history:
            return {'trends': [], 'patterns': []}
        
        # 日別正答率の計算
        daily_performance = defaultdict(list)
        for item in history:
            date_str = item.get('timestamp', '')[:10] if item.get('timestamp') else 'unknown'
            daily_performance[date_str].append(item.get('is_correct', False))
        
        trends = []
        for date, results in daily_performance.items():
            if results:
                accuracy = sum(results) / len(results)
                trends.append({
                    'date': date,
                    'accuracy': accuracy,
                    'question_count': len(results)
                })
        
        return {
            'trends': sorted(trends, key=lambda x: x['date']),
            'total_days': len(trends),
            'avg_daily_questions': statistics.mean([t['question_count'] for t in trends]) if trends and all(isinstance(t.get('question_count'), (int, float)) for t in trends) else 0
        }
    
    def analyze_difficulty_distribution(self, srs_data: Dict) -> Dict[str, Any]:
        """難易度分布分析（高度分析用）"""
        if not srs_data:
            return {'distribution': {}, 'summary': {}}
        
        difficulty_counts = defaultdict(int)
        difficulty_accuracy = defaultdict(list)
        
        for qid, data in srs_data.items():
            if isinstance(data, dict):
                difficulty = data.get('difficulty_level', 5)
                total = data.get('total_attempts', 0)
                correct = data.get('correct_count', 0)
                
                difficulty_counts[difficulty] += 1
                if total > 0:
                    difficulty_accuracy[difficulty].append(correct / total)
        
        distribution = {}
        for level in range(1, 11):  # 1-10の難易度
            count = difficulty_counts.get(level, 0)
            try:
                accuracy = statistics.mean(difficulty_accuracy[level]) if difficulty_accuracy[level] else 0
            except (TypeError, ValueError, statistics.StatisticsError):
                accuracy = 0
            distribution[str(level)] = {
                'count': count,
                'accuracy': accuracy
            }
        
        return {
            'distribution': distribution,
            'summary': {
                'total_questions': sum(difficulty_counts.values()),
                'avg_difficulty': statistics.mean(list(difficulty_counts.keys())) if difficulty_counts else 5
            }
        }
    
    def generate_learning_curve(self, history: List[Dict]) -> Dict[str, Any]:
        """学習曲線生成（高度分析用）"""
        if len(history) < 5:
            return {'curve_points': [], 'trend': 'insufficient_data'}
        
        # 5問ごとの正答率を計算
        curve_points = []
        for i in range(0, len(history), 5):
            batch = history[i:i+5]
            if batch:
                accuracy = sum(1 for item in batch if item.get('is_correct', False)) / len(batch)
                curve_points.append({
                    'session': i // 5 + 1,
                    'accuracy': accuracy,
                    'questions': len(batch)
                })
        
        # トレンド分析
        if len(curve_points) >= 2:
            first_half = curve_points[:len(curve_points)//2]
            second_half = curve_points[len(curve_points)//2:]
            
            try:
                first_avg = statistics.mean([p['accuracy'] for p in first_half]) if first_half else 0
                second_avg = statistics.mean([p['accuracy'] for p in second_half]) if second_half else 0
            except (TypeError, ValueError, statistics.StatisticsError) as e:
                logger.warning(f"学習曲線トレンド分析で統計エラー: {e}")
                first_avg = second_avg = 0
            
            if second_avg > first_avg + 0.1:
                trend = 'improving'
            elif second_avg < first_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'curve_points': curve_points,
            'trend': trend,
            'improvement_rate': (curve_points[-1]['accuracy'] - curve_points[0]['accuracy']) if len(curve_points) >= 2 else 0
        }
    
    def calculate_success_probability(self, history: List[Dict], srs_data: Dict) -> Dict[str, Any]:
        """成功確率計算（高度分析用）"""
        if not history and not srs_data:
            return {'probability': 0, 'confidence': 0}
        
        # 最近の成績から予測
        recent_accuracy = 0
        if history:
            recent_items = history[-20:]  # 最新20問
            recent_accuracy = sum(1 for item in recent_items if item.get('is_correct', False)) / len(recent_items)
        
        # SRSデータから習熟度計算
        mastery_level = 0
        if srs_data:
            mastery_scores = []
            for qid, data in srs_data.items():
                if isinstance(data, dict):
                    total = data.get('total_attempts', 0)
                    correct = data.get('correct_count', 0)
                    if total > 0:
                        mastery_scores.append(correct / total)
            try:
                mastery_level = statistics.mean(mastery_scores) if mastery_scores else 0
            except (TypeError, ValueError, statistics.StatisticsError) as e:
                logger.warning(f"成功確率計算で習熟度エラー: {e}")
                mastery_level = 0
        
        # 総合確率計算
        combined_score = (recent_accuracy * 0.6 + mastery_level * 0.4)
        success_probability = min(95, combined_score * 100)  # 最大95%
        
        return {
            'probability': round(success_probability, 1),
            'confidence': 0.8 if len(history) > 10 else 0.5,
            'factors': {
                'recent_performance': recent_accuracy,
                'overall_mastery': mastery_level
            }
        }
    
    def create_department_heatmap(self, history: List[Dict]) -> Dict[str, Any]:
        """部門別ヒートマップ作成（高度分析用）"""
        department_data = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for item in history:
            dept = item.get('department', 'unknown')
            department_data[dept]['total'] += 1
            if item.get('is_correct', False):
                department_data[dept]['correct'] += 1
        
        heatmap = {}
        for dept, data in department_data.items():
            accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0
            heatmap[dept] = {
                'accuracy': accuracy,
                'intensity': min(1.0, data['total'] / 20),  # 問題数による強度
                'question_count': data['total']
            }
        
        return {
            'heatmap': heatmap,
            'total_departments': len(heatmap),
            'coverage': sum(1 for d in heatmap.values() if d['question_count'] > 0)
        }
    
    def calculate_study_efficiency(self, history: List[Dict]) -> Dict[str, Any]:
        """学習効率計算（高度分析用）"""
        if not history:
            return {'efficiency': 0, 'factors': {}}
        
        # 回答時間あたりの正答率
        time_efficiency = []
        accuracy_over_time = []
        
        for item in history:
            response_time = item.get('response_time', 60)  # デフォルト60秒
            is_correct = item.get('is_correct', False)
            
            if response_time > 0:
                efficiency = (1 if is_correct else 0) / (response_time / 60)  # 分単位
                time_efficiency.append(efficiency)
            
            accuracy_over_time.append(1 if is_correct else 0)
        
        try:
            avg_efficiency = statistics.mean(time_efficiency) if time_efficiency else 0
            overall_accuracy = statistics.mean(accuracy_over_time) if accuracy_over_time else 0
        except (TypeError, ValueError, statistics.StatisticsError) as e:
            logger.warning(f"学習効率計算で統計エラー: {e}")
            avg_efficiency = overall_accuracy = 0
        
        return {
            'efficiency': round(avg_efficiency, 3),
            'factors': {
                'time_management': avg_efficiency,
                'accuracy': overall_accuracy,
                'consistency': 1 - statistics.stdev(time_efficiency) if len(time_efficiency) > 1 else 0
            },
            'rating': 'high' if avg_efficiency > 0.8 else 'medium' if avg_efficiency > 0.4 else 'low'
        }
    
    def estimate_cognitive_load(self, srs_data: Dict) -> Dict[str, Any]:
        """認知負荷推定（高度分析用）"""
        if not srs_data:
            return {'load': 0, 'factors': {}}
        
        # 難易度の分散と平均から認知負荷を推定
        difficulties = []
        attempts = []
        
        for qid, data in srs_data.items():
            if isinstance(data, dict):
                difficulty = data.get('difficulty_level', 5)
                total_attempts = data.get('total_attempts', 0)
                
                difficulties.append(difficulty)
                attempts.append(total_attempts)
        
        if not difficulties:
            return {'load': 0, 'factors': {}}
        
        try:
            avg_difficulty = statistics.mean(difficulties) if difficulties else 5
            difficulty_variance = statistics.variance(difficulties) if len(difficulties) > 1 else 0
            avg_attempts = statistics.mean(attempts) if attempts else 0
        except (TypeError, ValueError, statistics.StatisticsError) as e:
            logger.warning(f"認知負荷推定で統計計算エラー: {e}")
            avg_difficulty = 5
            difficulty_variance = 0
            avg_attempts = 0
        
        # 認知負荷スコア計算
        cognitive_load = (avg_difficulty / 10) * 0.4 + (difficulty_variance / 10) * 0.3 + min(1, avg_attempts / 5) * 0.3
        
        return {
            'load': round(cognitive_load, 3),
            'factors': {
                'average_difficulty': avg_difficulty,
                'difficulty_variance': difficulty_variance,
                'retry_frequency': avg_attempts
            },
            'level': 'high' if cognitive_load > 0.7 else 'medium' if cognitive_load > 0.4 else 'low'
        }
    
    def generate_study_plan(self, history: List[Dict], srs_data: Dict, bookmarks: List) -> Dict[str, Any]:
        """学習プラン生成（高度分析用）"""
        recommendations = []
        
        # 弱点分野の特定
        weak_areas = self._identify_weak_areas(history)
        for area in weak_areas:
            recommendations.append({
                'type': 'weakness_focus',
                'priority': 'high',
                'title': f"{area['category']}の強化",
                'description': f"正答率{area['accuracy']:.1%}の改善が必要",
                'estimated_time': '30分/日'
            })
        
        # 復習スケジュール
        if srs_data:
            due_reviews = sum(1 for data in srs_data.values() 
                            if isinstance(data, dict) and self._is_review_due(data))
            if due_reviews > 0:
                recommendations.append({
                    'type': 'review',
                    'priority': 'medium',
                    'title': f'復習問題 {due_reviews}問',
                    'description': 'スケジュールされた復習問題を完了してください',
                    'estimated_time': f'{due_reviews * 2}分'
                })
        
        return {
            'recommendations': recommendations[:6],
            'total_study_time': sum(self._parse_time(r.get('estimated_time', '0分')) for r in recommendations),
            'priority_areas': len([r for r in recommendations if r['priority'] == 'high'])
        }
    
    def _identify_weak_areas(self, history: List[Dict]) -> List[Dict]:
        """弱点分野特定のヘルパー"""
        category_performance = defaultdict(list)
        
        for item in history:
            category = item.get('category', 'unknown')
            is_correct = item.get('is_correct', False)
            category_performance[category].append(is_correct)
        
        weak_areas = []
        for category, results in category_performance.items():
            if len(results) >= 3:  # 最低3問以上
                accuracy = sum(results) / len(results)
                if accuracy < 0.7:  # 70%未満を弱点とする
                    weak_areas.append({
                        'category': category,
                        'accuracy': accuracy,
                        'sample_size': len(results)
                    })
        
        return sorted(weak_areas, key=lambda x: x['accuracy'])[:3]  # 上位3つの弱点
    
    def _is_review_due(self, srs_data: Dict) -> bool:
        """復習期限チェックのヘルパー"""
        next_review = srs_data.get('next_review', '')
        if not next_review:
            return False
        
        try:
            review_date = datetime.fromisoformat(next_review.replace('Z', '+00:00'))
            return review_date <= datetime.now()
        except (ValueError, TypeError) as e:
            logger.warning(f"復習期限チェックで日付パースエラー: {next_review}: {e}")
            return False
    
    def _parse_time(self, time_str: str) -> int:
        """時間文字列をパースして分数に変換"""
        if '分' in time_str:
            try:
                return int(time_str.replace('分', '').replace('/日', ''))
            except (ValueError, TypeError) as e:
                logger.warning(f"時間文字列パースエラー: {time_str}: {e}")
                return 0
        return 0
    
    def analyze_memory_retention(self, srs_data: Dict) -> Dict[str, Any]:
        """記憶保持分析（AIダッシュボード用）"""
        if not srs_data:
            return {'retention_rate': 0, 'factors': {}}
        
        retention_scores = []
        for qid, data in srs_data.items():
            if isinstance(data, dict):
                total = data.get('total_attempts', 0)
                correct = data.get('correct_count', 0)
                interval = data.get('interval_days', 1)
                
                if total > 0:
                    # 間隔が長いほど記憶保持が困難
                    base_retention = correct / total
                    interval_factor = max(0.5, 1 - (interval - 1) * 0.1)  # 間隔による減衰
                    retention_scores.append(base_retention * interval_factor)
        
        if not retention_scores:
            return {'retention_rate': 0, 'factors': {}}
        
        avg_retention = statistics.mean(retention_scores)
        
        return {
            'retention_rate': round(avg_retention, 3),
            'factors': {
                'consistency': 1 - statistics.stdev(retention_scores) if len(retention_scores) > 1 else 1,
                'long_term_memory': sum(1 for score in retention_scores if score > 0.8) / len(retention_scores)
            },
            'level': 'excellent' if avg_retention > 0.8 else 'good' if avg_retention > 0.6 else 'needs_improvement'
        }
    
    def generate_comprehensive_report(self, user_session: Dict, 
                                    exam_results: List[Dict] = None) -> Dict[str, Any]:
        """包括的な学習レポートの生成"""
        
        history = user_session.get('history', [])
        if not history:
            return self._empty_report()
        
        # 基本統計
        basic_stats = self._calculate_basic_statistics(history)
        
        # 学習傾向分析
        trend_analysis = self._analyze_learning_trends(history)
        
        # パフォーマンス予測
        performance_prediction = self._predict_future_performance(history)
        
        # 時間分析
        time_analysis = self._analyze_time_patterns(history)
        
        # 難易度分析
        difficulty_analysis = self._analyze_difficulty_progression(history)
        
        # 知識領域マップ
        knowledge_map = self._generate_knowledge_map(history)
        
        # 学習効率分析
        efficiency_analysis = self._analyze_learning_efficiency(history)
        
        # 比較分析（匿名）
        comparative_analysis = self._generate_comparative_analysis(history)
        
        # 試験準備度評価
        exam_readiness = self._assess_exam_readiness(history, exam_results)
        
        # 推奨アクション
        recommendations = self._generate_advanced_recommendations(
            basic_stats, trend_analysis, performance_prediction, exam_readiness
        )
        
        return {
            'report_id': self._generate_report_id(),
            'generated_at': datetime.now().isoformat(),
            'basic_statistics': basic_stats,
            'trend_analysis': trend_analysis,
            'performance_prediction': performance_prediction,
            'time_analysis': time_analysis,
            'difficulty_analysis': difficulty_analysis,
            'knowledge_map': knowledge_map,
            'efficiency_analysis': efficiency_analysis,
            'comparative_analysis': comparative_analysis,
            'exam_readiness': exam_readiness,
            'recommendations': recommendations,
            'confidence_score': self._calculate_report_confidence(len(history))
        }
    
    def _calculate_basic_statistics(self, history: List[Dict]) -> Dict[str, Any]:
        """基本統計の計算"""
        
        if not history:
            return {}
        
        total_questions = len(history)
        correct_answers = sum(1 for h in history if h.get('is_correct', False))
        
        # 時間分析
        times = [h.get('elapsed', 0) for h in history if h.get('elapsed', 0) > 0]
        
        # カテゴリ別分析
        category_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'times': []})
        for h in history:
            cat = h.get('category', '不明')
            category_stats[cat]['total'] += 1
            if h.get('is_correct', False):
                category_stats[cat]['correct'] += 1
            if h.get('elapsed', 0) > 0:
                category_stats[cat]['times'].append(h.get('elapsed', 0))
        
        # 最近の傾向（直近30問）
        recent_history = history[-30:] if len(history) > 30 else history
        recent_accuracy = sum(1 for h in recent_history if h.get('is_correct', False)) / len(recent_history)
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'overall_accuracy': correct_answers / total_questions,
            'recent_accuracy': recent_accuracy,
            'improvement_rate': recent_accuracy - (correct_answers / total_questions),
            'avg_response_time': statistics.mean(times) if times else 0,
            'response_time_std': statistics.stdev(times) if len(times) > 1 else 0,
            'median_response_time': statistics.median(times) if times else 0,
            'category_performance': {
                cat: {
                    'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                    'avg_time': statistics.mean(stats['times']) if stats['times'] else 0,
                    'total_questions': stats['total']
                }
                for cat, stats in category_stats.items()
            },
            'study_span_days': self._calculate_study_span(history),
            'active_study_days': len(set(h.get('date', '')[:10] for h in history if h.get('date')))
        }
    
    def _analyze_learning_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """学習傾向分析"""
        
        if len(history) < 10:
            return {'trend': 'insufficient_data'}
        
        # 時系列正答率の計算
        window_size = max(5, len(history) // 10)  # 動的ウィンドウサイズ
        accuracy_series = []
        time_series = []
        
        for i in range(window_size, len(history) + 1, window_size // 2):
            window = history[max(0, i-window_size):i]
            if window:
                accuracy = sum(1 for h in window if h.get('is_correct', False)) / len(window)
                accuracy_series.append(accuracy)
                
                # 時間スタンプ
                if window[-1].get('date'):
                    time_series.append(window[-1]['date'][:10])
        
        if len(accuracy_series) < 3:
            return {'trend': 'insufficient_data'}
        
        # 傾向の計算
        trend_slope = self._calculate_trend_slope(accuracy_series)
        trend_confidence = self._calculate_trend_confidence(accuracy_series)
        
        # 季節性分析
        seasonal_patterns = self._analyze_seasonal_patterns(history)
        
        # 学習頻度分析
        frequency_analysis = self._analyze_study_frequency(history)
        
        # 成績の安定性
        stability = 1 - statistics.stdev(accuracy_series)
        
        return {
            'trend': self._classify_trend(trend_slope),
            'trend_slope': trend_slope,
            'trend_confidence': trend_confidence,
            'stability': stability,
            'accuracy_series': accuracy_series,
            'time_series': time_series,
            'seasonal_patterns': seasonal_patterns,
            'frequency_analysis': frequency_analysis,
            'learning_velocity': self._calculate_learning_velocity(accuracy_series),
            'plateau_detection': self._detect_learning_plateau(accuracy_series)
        }
    
    def _predict_future_performance(self, history: List[Dict]) -> Dict[str, Any]:
        """将来のパフォーマンス予測"""
        
        if len(history) < 20:
            return {'prediction': 'insufficient_data'}
        
        # 最近の傾向から予測
        recent_accuracy = []
        window_size = 10
        
        for i in range(len(history) - 30, len(history), window_size):
            if i > 0:
                window = history[i:i+window_size]
                if window:
                    accuracy = sum(1 for h in window if h.get('is_correct', False)) / len(window)
                    recent_accuracy.append(accuracy)
        
        if len(recent_accuracy) < 2:
            return {'prediction': 'insufficient_data'}
        
        # 線形回帰による予測
        predicted_accuracy = self._linear_regression_predict(recent_accuracy, periods=3)
        
        # 信頼区間の計算
        confidence_interval = self._calculate_confidence_interval(recent_accuracy)
        
        # 目標達成予測
        target_accuracy = 0.8  # 80%を目標とする
        days_to_target = self._predict_days_to_target(recent_accuracy, target_accuracy)
        
        return {
            'current_trend': recent_accuracy,
            'predicted_accuracy_1week': predicted_accuracy[0],
            'predicted_accuracy_2week': predicted_accuracy[1],
            'predicted_accuracy_1month': predicted_accuracy[2],
            'confidence_interval': confidence_interval,
            'days_to_80_percent': days_to_target,
            'prediction_confidence': self._calculate_prediction_confidence(len(recent_accuracy)),
            'risk_factors': self._identify_risk_factors(history),
            'improvement_potential': self._calculate_improvement_potential(recent_accuracy)
        }
    
    def _analyze_time_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """時間パターン分析"""
        
        # 時間別分析
        hourly_performance = defaultdict(lambda: {'total': 0, 'correct': 0, 'times': []})
        daily_performance = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        for h in history:
            if h.get('date'):
                try:
                    dt = datetime.fromisoformat(h['date'])
                    hour = dt.hour
                    day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
                    
                    hourly_performance[hour]['total'] += 1
                    daily_performance[day_of_week]['total'] += 1
                    
                    if h.get('is_correct', False):
                        hourly_performance[hour]['correct'] += 1
                        daily_performance[day_of_week]['correct'] += 1
                    
                    if h.get('elapsed', 0) > 0:
                        hourly_performance[hour]['times'].append(h.get('elapsed', 0))
                        
                except ValueError:
                    continue
        
        # 最適な学習時間の特定
        best_hours = sorted(
            [(hour, stats['correct'] / stats['total'] if stats['total'] > 0 else 0)
             for hour, stats in hourly_performance.items()],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        best_days = sorted(
            [(day, stats['correct'] / stats['total'] if stats['total'] > 0 else 0)
             for day, stats in daily_performance.items()],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        return {
            'hourly_performance': dict(hourly_performance),
            'daily_performance': dict(daily_performance),
            'best_study_hours': [hour for hour, _ in best_hours],
            'best_study_days': [day for day, _ in best_days],
            'peak_performance_time': best_hours[0][0] if best_hours else None,
            'consistency_score': self._calculate_time_consistency(hourly_performance),
            'optimal_session_length': self._calculate_optimal_session_length(history)
        }
    
    def _analyze_difficulty_progression(self, history: List[Dict]) -> Dict[str, Any]:
        """難易度進歩分析"""
        
        difficulty_order = {'基本': 1, '標準': 2, '応用': 3, '上級': 4}
        
        difficulty_performance = defaultdict(lambda: {'total': 0, 'correct': 0, 'progression': []})
        
        for i, h in enumerate(history):
            difficulty = h.get('difficulty', '標準')
            difficulty_performance[difficulty]['total'] += 1
            if h.get('is_correct', False):
                difficulty_performance[difficulty]['correct'] += 1
            
            # 進歩の追跡
            difficulty_performance[difficulty]['progression'].append({
                'index': i,
                'correct': h.get('is_correct', False),
                'date': h.get('date', '')[:10]
            })
        
        # 難易度別成長率
        growth_rates = {}
        for difficulty, perf in difficulty_performance.items():
            if len(perf['progression']) > 10:
                first_half = perf['progression'][:len(perf['progression'])//2]
                second_half = perf['progression'][len(perf['progression'])//2:]
                
                first_accuracy = sum(1 for p in first_half if p['correct']) / len(first_half)
                second_accuracy = sum(1 for p in second_half if p['correct']) / len(second_half)
                
                growth_rates[difficulty] = second_accuracy - first_accuracy
        
        return {
            'difficulty_performance': dict(difficulty_performance),
            'growth_rates': growth_rates,
            'ready_for_next_level': self._assess_difficulty_readiness(difficulty_performance),
            'difficulty_preference': self._identify_difficulty_preference(difficulty_performance),
            'mastery_levels': self._calculate_mastery_levels(difficulty_performance)
        }
    
    def _generate_knowledge_map(self, history: List[Dict]) -> Dict[str, Any]:
        """知識領域マップの生成"""
        
        # カテゴリ間の関連性分析
        category_combinations = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        # 連続する問題のカテゴリを分析
        for i in range(len(history) - 1):
            current_cat = history[i].get('category', '不明')
            next_cat = history[i + 1].get('category', '不明')
            
            if current_cat != next_cat:
                combo_key = f"{current_cat}->{next_cat}"
                category_combinations[combo_key]['total'] += 1
                if history[i + 1].get('is_correct', False):
                    category_combinations[combo_key]['correct'] += 1
        
        # 知識の相関関係
        knowledge_correlations = self._calculate_knowledge_correlations(history)
        
        # 強み・弱みマップ
        strength_weakness_map = self._create_strength_weakness_map(history)
        
        return {
            'category_transitions': dict(category_combinations),
            'knowledge_correlations': knowledge_correlations,
            'strength_weakness_map': strength_weakness_map,
            'learning_pathways': self._suggest_learning_pathways(knowledge_correlations),
            'knowledge_gaps': self._identify_knowledge_gaps(history)
        }
    
    def _analyze_learning_efficiency(self, history: List[Dict]) -> Dict[str, Any]:
        """学習効率分析"""
        
        # 問題あたりの学習効果
        learning_curves = self._calculate_learning_curves(history)
        
        # 時間対効果分析
        time_effectiveness = self._analyze_time_effectiveness(history)
        
        # 忘却曲線分析
        forgetting_analysis = self._analyze_forgetting_patterns(history)
        
        # 最適な復習間隔
        optimal_intervals = self._calculate_optimal_review_intervals(history)
        
        return {
            'learning_curves': learning_curves,
            'time_effectiveness': time_effectiveness,
            'forgetting_analysis': forgetting_analysis,
            'optimal_review_intervals': optimal_intervals,
            'efficiency_score': self._calculate_overall_efficiency(learning_curves, time_effectiveness),
            'improvement_suggestions': self._suggest_efficiency_improvements(time_effectiveness)
        }
    
    def _generate_comparative_analysis(self, history: List[Dict]) -> Dict[str, Any]:
        """比較分析（匿名化）"""
        
        # 同レベル学習者との比較（模擬データ）
        total_questions = len(history)
        accuracy = sum(1 for h in history if h.get('is_correct', False)) / total_questions if total_questions > 0 else 0
        
        # 仮想的な比較データ（実際の実装では他のユーザーの匿名化データを使用）
        percentile_rank = self._calculate_percentile_rank(accuracy, total_questions)
        
        return {
            'percentile_rank': percentile_rank,
            'above_average_categories': self._identify_above_average_categories(history),
            'below_average_categories': self._identify_below_average_categories(history),
            'relative_strengths': self._identify_relative_strengths(history),
            'improvement_opportunities': self._identify_improvement_opportunities(history)
        }
    
    def _assess_exam_readiness(self, history: List[Dict], 
                             exam_results: List[Dict] = None) -> Dict[str, Any]:
        """試験準備度評価"""
        
        if not history:
            return {'readiness': 'insufficient_data'}
        
        # 基本指標
        total_questions = len(history)
        overall_accuracy = sum(1 for h in history if h.get('is_correct', False)) / total_questions
        
        # カテゴリ別準備度
        category_readiness = self._assess_category_readiness(history)
        
        # 最近のパフォーマンス
        recent_performance = self._assess_recent_performance(history)
        
        # 模擬試験結果の分析
        mock_exam_analysis = {}
        if exam_results:
            mock_exam_analysis = self._analyze_mock_exam_results(exam_results)
        
        # 総合準備度スコア
        readiness_score = self._calculate_readiness_score(
            overall_accuracy, category_readiness, recent_performance, mock_exam_analysis
        )
        
        return {
            'readiness_score': readiness_score,
            'readiness_level': self._classify_readiness_level(readiness_score),
            'category_readiness': category_readiness,
            'recent_performance': recent_performance,
            'mock_exam_analysis': mock_exam_analysis,
            'recommended_study_time': self._recommend_study_time(readiness_score),
            'focus_areas': self._identify_focus_areas(category_readiness),
            'exam_strategy': self._suggest_exam_strategy(readiness_score, category_readiness)
        }
    
    # 以下、各分析メソッドのヘルパー関数
    
    def _calculate_study_span(self, history: List[Dict]) -> int:
        """学習期間の計算"""
        dates = [h.get('date', '')[:10] for h in history if h.get('date')]
        if not dates:
            return 0
        
        # 不正な日付フォーマットをフィルタリング
        valid_dates = []
        for date_str in dates:
            try:
                # 日付形式の検証と修正
                if len(date_str) == 10 and date_str.count('-') == 2:
                    parts = date_str.split('-')
                    if len(parts) == 3 and all(part.isdigit() or (part.startswith('-') and part[1:].isdigit()) for part in parts):
                        # 負の値を修正
                        year = int(parts[0])
                        month = max(1, min(12, abs(int(parts[1]))))
                        day = max(1, min(31, abs(int(parts[2]))))
                        
                        corrected_date = f"{year:04d}-{month:02d}-{day:02d}"
                        datetime.fromisoformat(corrected_date)  # 検証
                        valid_dates.append(corrected_date)
            except (ValueError, IndexError):
                continue
        
        if not valid_dates:
            return 0
        
        valid_dates = sorted(set(valid_dates))
        if len(valid_dates) < 2:
            return 1
        
        start_date = datetime.fromisoformat(valid_dates[0])
        end_date = datetime.fromisoformat(valid_dates[-1])
        return (end_date - start_date).days + 1
    
    def _calculate_trend_slope(self, accuracy_series: List[float]) -> float:
        """傾向の傾きを計算"""
        if len(accuracy_series) < 2:
            return 0
        
        n = len(accuracy_series)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(accuracy_series)
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(accuracy_series))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def _calculate_trend_confidence(self, accuracy_series: List[float]) -> float:
        """傾向の信頼度を計算"""
        if len(accuracy_series) < 3:
            return 0
        
        slope = self._calculate_trend_slope(accuracy_series)
        variance = statistics.variance(accuracy_series)
        
        # 信頼度は傾きの絶対値と分散の逆数に基づく
        confidence = abs(slope) / (variance + 0.01)  # 0.01は分母が0になることを防ぐ
        return min(confidence, 1.0)
    
    def _classify_trend(self, slope: float) -> str:
        """傾向の分類"""
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'
    
    def _empty_report(self) -> Dict[str, Any]:
        """空レポートの生成"""
        return {
            'report_id': self._generate_report_id(),
            'generated_at': datetime.now().isoformat(),
            'status': 'insufficient_data',
            'message': '分析に十分なデータがありません。まずは問題に挑戦してください。'
        }
    
    def _generate_report_id(self) -> str:
        """レポートIDの生成"""
        return f"REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _calculate_report_confidence(self, data_points: int) -> float:
        """レポートの信頼度計算"""
        if data_points < 10:
            return 0.2
        elif data_points < 50:
            return 0.5
        elif data_points < 100:
            return 0.7
        else:
            return 0.9
    
    # その他のヘルパーメソッドは簡略化のため省略
    # 実際の実装では各メソッドの詳細な実装が必要
    
    def _analyze_seasonal_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """季節性パターンの分析（簡略版）"""
        return {'detected': False, 'pattern': 'none'}
    
    def _analyze_study_frequency(self, history: List[Dict]) -> Dict[str, Any]:
        """学習頻度分析（簡略版）"""
        return {'frequency': 'regular', 'consistency': 0.8}
    
    def _calculate_learning_velocity(self, accuracy_series: List[float]) -> float:
        """学習速度計算（簡略版）"""
        return 0.1
    
    def _detect_learning_plateau(self, accuracy_series: List[float]) -> bool:
        """学習プラトー検出（簡略版）"""
        return False
    
    def _linear_regression_predict(self, data: List[float], periods: int) -> List[float]:
        """線形回帰予測（簡略版）"""
        if not data:
            return [0.7] * periods
        return [min(1.0, max(0.0, data[-1] + 0.05 * i)) for i in range(1, periods + 1)]
    
    def _calculate_confidence_interval(self, data: List[float]) -> Tuple[float, float]:
        """信頼区間計算（簡略版）"""
        if not data:
            return (0.5, 0.9)
        mean_val = statistics.mean(data)
        return (max(0, mean_val - 0.1), min(1, mean_val + 0.1))
    
    def _predict_days_to_target(self, recent_accuracy: List[float], target: float) -> Optional[int]:
        """目標達成予測日数（簡略版）"""
        if not recent_accuracy:
            return None
        current = recent_accuracy[-1]
        if current >= target:
            return 0
        return int((target - current) / 0.01)  # 仮の改善率
    
    def _calculate_prediction_confidence(self, data_points: int) -> float:
        """予測信頼度計算"""
        return min(data_points / 20, 0.9)
    
    def _identify_risk_factors(self, history: List[Dict]) -> List[str]:
        """リスク要因特定（簡略版）"""
        return []
    
    def _calculate_improvement_potential(self, recent_accuracy: List[float]) -> float:
        """改善ポテンシャル計算（簡略版）"""
        if not recent_accuracy:
            return 0.5
        return max(0, 1.0 - max(recent_accuracy))
    
    def _calculate_time_consistency(self, hourly_performance: Dict) -> float:
        """時間一貫性計算（簡略版）"""
        return 0.7
    
    def _calculate_optimal_session_length(self, history: List[Dict]) -> int:
        """最適セッション長計算（簡略版）"""
        return 45  # 分
    
    def _assess_difficulty_readiness(self, difficulty_performance: Dict) -> Dict[str, bool]:
        """難易度準備度評価（簡略版）"""
        return {'応用': True, '上級': False}
    
    def _identify_difficulty_preference(self, difficulty_performance: Dict) -> str:
        """難易度選好特定（簡略版）"""
        return '標準'
    
    def _calculate_mastery_levels(self, difficulty_performance: Dict) -> Dict[str, float]:
        """習熟度レベル計算（簡略版）"""
        return {'基本': 0.9, '標準': 0.7, '応用': 0.5}
    
    def _calculate_knowledge_correlations(self, history: List[Dict]) -> Dict[str, float]:
        """知識相関計算（簡略版）"""
        return {}
    
    def _create_strength_weakness_map(self, history: List[Dict]) -> Dict[str, str]:
        """強み弱みマップ作成（簡略版）"""
        return {'コンクリート': 'strength', '構造': 'weakness'}
    
    def _suggest_learning_pathways(self, correlations: Dict) -> List[str]:
        """学習経路提案（簡略版）"""
        return ['基礎 → 応用', '理論 → 実践']
    
    def _identify_knowledge_gaps(self, history: List[Dict]) -> List[str]:
        """知識ギャップ特定（簡略版）"""
        return []
    
    def _calculate_learning_curves(self, history: List[Dict]) -> Dict[str, List[float]]:
        """学習曲線計算（簡略版）"""
        return {}
    
    def _analyze_time_effectiveness(self, history: List[Dict]) -> Dict[str, float]:
        """時間効果分析（簡略版）"""
        return {'efficiency': 0.8}
    
    def _analyze_forgetting_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """忘却パターン分析（簡略版）"""
        return {}
    
    def _calculate_optimal_review_intervals(self, history: List[Dict]) -> Dict[str, int]:
        """最適復習間隔計算（簡略版）"""
        return {'基本': 3, '標準': 7, '応用': 14}
    
    def _calculate_overall_efficiency(self, learning_curves: Dict, time_effectiveness: Dict) -> float:
        """総合効率計算（簡略版）"""
        return 0.75
    
    def _suggest_efficiency_improvements(self, time_effectiveness: Dict) -> List[str]:
        """効率改善提案（簡略版）"""
        return ['短時間集中学習を心がける', '復習間隔を最適化する']
    
    def _calculate_percentile_rank(self, accuracy: float, total_questions: int) -> int:
        """パーセンタイル順位計算（簡略版）"""
        return min(95, max(5, int(accuracy * 100)))
    
    def _identify_above_average_categories(self, history: List[Dict]) -> List[str]:
        """平均以上カテゴリ特定（簡略版）"""
        return ['コンクリート']
    
    def _identify_below_average_categories(self, history: List[Dict]) -> List[str]:
        """平均以下カテゴリ特定（簡略版）"""
        return ['構造']
    
    def _identify_relative_strengths(self, history: List[Dict]) -> List[str]:
        """相対的強み特定（簡略版）"""
        return ['基礎理論', '計算問題']
    
    def _identify_improvement_opportunities(self, history: List[Dict]) -> List[str]:
        """改善機会特定（簡略版）"""
        return ['応用問題対応', '時間短縮']
    
    def _assess_category_readiness(self, history: List[Dict]) -> Dict[str, float]:
        """カテゴリ別準備度評価（簡略版）"""
        return {'コンクリート': 0.8, '構造': 0.6, '施工': 0.7, '維持管理': 0.5}
    
    def _assess_recent_performance(self, history: List[Dict]) -> Dict[str, Any]:
        """最近のパフォーマンス評価（簡略版）"""
        return {'trend': 'improving', 'stability': 0.8}
    
    def _analyze_mock_exam_results(self, exam_results: List[Dict]) -> Dict[str, Any]:
        """模擬試験結果分析（簡略版）"""
        return {'avg_score': 0.75, 'improvement': 0.05}
    
    def _calculate_readiness_score(self, accuracy: float, category_readiness: Dict, 
                                 recent_performance: Dict, mock_exam_analysis: Dict) -> float:
        """準備度スコア計算"""
        base_score = accuracy * 0.4
        category_score = statistics.mean(category_readiness.values()) * 0.3 if category_readiness else 0
        recent_score = recent_performance.get('stability', 0.5) * 0.2
        mock_score = mock_exam_analysis.get('avg_score', 0.5) * 0.1
        
        return base_score + category_score + recent_score + mock_score
    
    def _classify_readiness_level(self, score: float) -> str:
        """準備度レベル分類"""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.6:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _recommend_study_time(self, readiness_score: float) -> int:
        """推奨学習時間（時間）"""
        if readiness_score >= 0.8:
            return 20
        elif readiness_score >= 0.7:
            return 40
        elif readiness_score >= 0.6:
            return 60
        else:
            return 100
    
    def _identify_focus_areas(self, category_readiness: Dict) -> List[str]:
        """重点分野特定"""
        return [cat for cat, score in category_readiness.items() if score < 0.7]
    
    def _suggest_exam_strategy(self, readiness_score: float, category_readiness: Dict) -> List[str]:
        """試験戦略提案"""
        strategies = []
        
        if readiness_score < 0.7:
            strategies.append('基礎知識の徹底復習')
        
        weak_areas = self._identify_focus_areas(category_readiness)
        if weak_areas:
            strategies.append(f'弱点分野({", ".join(weak_areas)})の重点学習')
        
        strategies.append('模擬試験による実践練習')
        strategies.append('時間配分の練習')
        
        return strategies
    
    def _generate_advanced_recommendations(self, basic_stats: Dict, trend_analysis: Dict,
                                         performance_prediction: Dict, exam_readiness: Dict) -> List[Dict[str, Any]]:
        """高度な推奨事項生成"""
        recommendations = []
        
        # パフォーマンスベースの推奨
        if basic_stats.get('overall_accuracy', 0) < 0.7:
            recommendations.append({
                'type': 'urgent',
                'title': '基礎力強化が必要',
                'description': '全体正答率が70%を下回っています。基礎知識の復習を優先してください。',
                'action': '基礎問題を重点的に学習',
                'priority': 'high'
            })
        
        # 傾向ベースの推奨
        if trend_analysis.get('trend') == 'declining':
            recommendations.append({
                'type': 'warning',
                'title': '成績下降傾向',
                'description': '最近の成績が下降傾向にあります。学習方法の見直しが必要です。',
                'action': '学習方法の変更を検討',
                'priority': 'high'
            })
        
        # 予測ベースの推奨
        if performance_prediction.get('days_to_80_percent', 999) > 60:
            recommendations.append({
                'type': 'improvement',
                'title': '学習効率の向上',
                'description': '現在のペースでは目標達成に時間がかかりすぎます。',
                'action': 'AI適応学習モードの活用',
                'priority': 'medium'
            })
        
        # 試験準備度ベースの推奨
        readiness_level = exam_readiness.get('readiness_level', 'needs_improvement')
        if readiness_level in ['fair', 'needs_improvement']:
            recommendations.append({
                'type': 'exam_prep',
                'title': '試験準備の強化',
                'description': '試験準備度が不十分です。模擬試験を活用してください。',
                'action': '試験シミュレーションモードの実施',
                'priority': 'high'
            })
        
        return recommendations

# グローバルインスタンス
advanced_analytics = AdvancedAnalytics()