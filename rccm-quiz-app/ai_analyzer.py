"""
RCCM学習アプリ - AI弱点分析エンジン（部門別対応版）
学習データを分析して個人に最適化された学習プランを提案
RCCM 12部門別の特化分析機能を実装
"""

import math
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import logging

# RCCM設定をインポート
from config import RCCMConfig

logger = logging.getLogger(__name__)

class AILearningAnalyzer:
    """AI駆動の学習分析エンジン"""
    
    def __init__(self):
        self.confidence_threshold = 0.7  # 分析結果の信頼度閾値
        self.min_samples = 5  # 分析に必要な最小サンプル数
    
    def analyze_weakness_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """弱点パターン分析（AIダッシュボード用）"""
        if not history:
            return {'patterns': [], 'confidence': 0.0, 'total_analyzed': 0}
        
        # カテゴリ別正答率分析
        category_accuracy = defaultdict(list)
        for item in history:
            if 'category' in item and 'is_correct' in item:
                category_accuracy[item['category']].append(item['is_correct'])
        
        patterns = []
        for category, results in category_accuracy.items():
            accuracy = sum(results) / len(results) if results else 0
            if accuracy < 0.6:  # 60%未満を弱点とする
                patterns.append({
                    'category': category,
                    'accuracy': accuracy,
                    'sample_size': len(results),
                    'weakness_level': 'high' if accuracy < 0.4 else 'medium'
                })
        
        return {
            'patterns': patterns,
            'confidence': min(1.0, len(history) / 20),  # 20問で最大信頼度
            'total_analyzed': len(history)
        }
    
    def determine_learning_style(self, history: List[Dict]) -> Dict[str, Any]:
        """学習スタイル判定（AIダッシュボード用）"""
        if not history:
            return {'style': 'unknown', 'confidence': 0.0}
        
        # 回答時間分析
        response_times = []
        for item in history:
            if isinstance(item, dict):
                response_time = item.get('response_time', 0)
                if isinstance(response_time, (int, float)) and response_time > 0:
                    response_times.append(response_time)
        
        try:
            avg_time = statistics.mean(response_times) if response_times else 0
        except (TypeError, ValueError, statistics.StatisticsError):
            avg_time = 0
        
        # 正答率の時系列変化
        correct_rates = []
        for i in range(0, len(history), 5):
            batch = history[i:i+5]
            if batch:
                rate = sum(1 for item in batch if item.get('is_correct', False)) / len(batch)
                correct_rates.append(rate)
        
        # 学習スタイル判定
        if avg_time > 60:  # 1分以上
            style = 'analytical'  # 分析型
        elif avg_time < 20:  # 20秒未満
            style = 'intuitive'  # 直感型
        else:
            style = 'balanced'  # バランス型
        
        return {
            'style': style,
            'confidence': min(1.0, len(history) / 15),
            'avg_response_time': avg_time,
            'improvement_trend': correct_rates[-1] - correct_rates[0] if len(correct_rates) > 1 else 0
        }
    
    def predict_performance(self, srs_data: Dict) -> Dict[str, Any]:
        """パフォーマンス予測（AIダッシュボード用）"""
        if not srs_data:
            return {'predicted_score': 0, 'confidence': 0.0}
        
        # SRSデータから習熟度を計算
        mastery_scores = []
        for qid, data in srs_data.items():
            if isinstance(data, dict):
                total = data.get('total_attempts', 0)
                correct = data.get('correct_count', 0)
                if (isinstance(total, (int, float)) and 
                    isinstance(correct, (int, float)) and 
                    total > 0):
                    mastery_scores.append(correct / total)
        
        if not mastery_scores:
            return {'predicted_score': 0, 'confidence': 0.0}
        
        try:
            avg_mastery = statistics.mean(mastery_scores)
        except (TypeError, ValueError, statistics.StatisticsError):
            return {'predicted_score': 0, 'confidence': 0.0}
        predicted_score = min(100, avg_mastery * 100 + 10)  # 予測スコア
        
        return {
            'predicted_score': round(predicted_score, 1),
            'confidence': min(1.0, len(mastery_scores) / 10),
            'mastery_level': 'high' if avg_mastery > 0.8 else 'medium' if avg_mastery > 0.6 else 'low',
            'analyzed_questions': len(mastery_scores)
        }
    
    def generate_recommendations(self, history: List[Dict], srs_data: Dict) -> List[Dict]:
        """学習推奨事項生成（AIダッシュボード用）"""
        recommendations = []
        
        # 弱点分析結果から推奨
        weakness_analysis = self.analyze_weakness_patterns(history)
        for pattern in weakness_analysis.get('patterns', []):
            recommendations.append({
                'type': 'weakness_focus',
                'title': f"{pattern['category']}の集中学習",
                'description': f"正答率{pattern['accuracy']:.1%}の分野を重点的に学習することをお勧めします",
                'priority': 'high' if pattern['weakness_level'] == 'high' else 'medium'
            })
        
        # 学習スタイルから推奨
        style_analysis = self.determine_learning_style(history)
        if style_analysis['style'] == 'analytical':
            recommendations.append({
                'type': 'study_method',
                'title': '詳細解説モードの活用',
                'description': '分析型の学習スタイルのため、解説をじっくり読むことをお勧めします',
                'priority': 'medium'
            })
        
        return recommendations[:5]  # 上位5つの推奨事項
        
    def analyze_weak_areas(self, user_session: Dict, department_filter: str = None) -> Dict[str, Any]:
        """包括的な弱点分析（部門別対応版）"""
        history = user_session.get('history', [])
        
        # None チェック
        if history is None:
            history = []
        
        # 部門別フィルタリング
        if department_filter:
            history = [h for h in history if h.get('department') == department_filter]
            logger.info(f"部門別分析: {department_filter}, 対象履歴: {len(history)}件")
        
        if len(history) < self.min_samples:
            return self._insufficient_data_response(department_filter)
        
        # 複数の角度から弱点を分析（部門別対応）
        category_analysis = self._analyze_by_category(history)
        department_analysis = self._analyze_by_department(history)
        question_type_analysis = self._analyze_by_question_type(history)
        difficulty_analysis = self._analyze_by_difficulty(history)
        time_analysis = self._analyze_response_time(history)
        trend_analysis = self._analyze_learning_trend(history)
        error_pattern_analysis = self._analyze_error_patterns(history)
        
        # RCCM特化分析
        rccm_specific_analysis = self._analyze_rccm_specific_patterns(history, department_filter)
        
        # 総合的な弱点スコア計算（部門別考慮）
        weak_areas = self._calculate_comprehensive_weakness_score(
            category_analysis, difficulty_analysis, time_analysis, 
            trend_analysis, error_pattern_analysis, department_analysis, question_type_analysis
        )
        
        # 学習推奨プラン生成（部門特化）
        learning_plan = self._generate_learning_plan(weak_areas, history, department_filter)
        
        return {
            'weak_areas': weak_areas,
            'learning_plan': learning_plan,
            'department_analysis': department_analysis,
            'question_type_analysis': question_type_analysis,
            'rccm_specific': rccm_specific_analysis,
            'analysis_details': {
                'category': category_analysis,
                'department': department_analysis,
                'question_type': question_type_analysis,
                'difficulty': difficulty_analysis,
                'time': time_analysis,
                'trend': trend_analysis,
                'error_patterns': error_pattern_analysis,
                'rccm_specific': rccm_specific_analysis
            },
            'confidence_score': self._calculate_confidence_score(len(history)),
            'recommendation_priority': self._prioritize_recommendations(weak_areas, department_filter),
            'department_filter': department_filter,
            'filtered_history_count': len(history)
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
    
    def _analyze_by_department(self, history: List[Dict]) -> Dict[str, Any]:
        """RCCM部門別分析"""
        department_stats = defaultdict(lambda: {
            'total': 0, 'correct': 0, 'avg_time': 0, 
            'recent_performance': [], 'categories': set()
        })
        
        for i, entry in enumerate(history):
            department = entry.get('department', 'unknown')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            category = entry.get('category', '')
            
            department_stats[department]['total'] += 1
            if is_correct:
                department_stats[department]['correct'] += 1
            department_stats[department]['avg_time'] += elapsed_time
            department_stats[department]['categories'].add(category)
            
            # 最近10問のパフォーマンス
            if i >= len(history) - 10:
                department_stats[department]['recent_performance'].append(is_correct)
        
        # 分析結果の計算
        analysis = {}
        for department, stats in department_stats.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                avg_time = stats['avg_time'] / stats['total']
                recent_accuracy = (
                    sum(stats['recent_performance']) / len(stats['recent_performance'])
                    if stats['recent_performance'] else accuracy
                )
                
                # 部門特有の弱点スコア計算
                weakness_score = self._calculate_department_weakness_score(
                    department, accuracy, recent_accuracy, avg_time, stats['total']
                )
                
                # 部門情報を取得
                dept_info = RCCMConfig.DEPARTMENTS.get(department, {
                    'name': department, 'description': '不明な部門'
                })
                
                analysis[department] = {
                    'name': dept_info.get('name', department),
                    'accuracy': accuracy,
                    'recent_accuracy': recent_accuracy,
                    'avg_time': avg_time,
                    'total_questions': stats['total'],
                    'weakness_score': weakness_score,
                    'improvement_trend': recent_accuracy - accuracy,
                    'category_coverage': len(stats['categories']),
                    'confidence': min(stats['total'] / 15, 1.0),  # 15問で100%信頼度
                    'department_specific_insights': self._get_department_insights(department, stats)
                }
        
        return analysis
    
    def _analyze_by_question_type(self, history: List[Dict]) -> Dict[str, Any]:
        """問題種別分析（4-1基礎 vs 4-2専門）"""
        type_stats = defaultdict(lambda: {
            'total': 0, 'correct': 0, 'avg_time': 0, 'recent_performance': []
        })
        
        for i, entry in enumerate(history):
            question_type = entry.get('question_type', 'unknown')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            
            type_stats[question_type]['total'] += 1
            if is_correct:
                type_stats[question_type]['correct'] += 1
            type_stats[question_type]['avg_time'] += elapsed_time
            
            # 最近のパフォーマンス
            if i >= len(history) - 10:
                type_stats[question_type]['recent_performance'].append(is_correct)
        
        analysis = {}
        for qtype, stats in type_stats.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                avg_time = stats['avg_time'] / stats['total']
                recent_accuracy = (
                    sum(stats['recent_performance']) / len(stats['recent_performance'])
                    if stats['recent_performance'] else accuracy
                )
                
                # 問題種別情報を取得
                type_info = RCCMConfig.QUESTION_TYPES.get(qtype, {
                    'name': qtype, 'description': '不明な問題種別'
                })
                
                analysis[qtype] = {
                    'name': type_info.get('name', qtype),
                    'accuracy': accuracy,
                    'recent_accuracy': recent_accuracy,
                    'avg_time': avg_time,
                    'total_questions': stats['total'],
                    'weakness_score': 1 - accuracy,
                    'improvement_trend': recent_accuracy - accuracy,
                    'confidence': min(stats['total'] / 10, 1.0),
                    'learning_recommendation': self._get_question_type_recommendation(qtype, accuracy)
                }
        
        return analysis
    
    def _analyze_rccm_specific_patterns(self, history: List[Dict], department_filter: str = None) -> Dict[str, Any]:
        """RCCM試験特有のパターン分析"""
        # 4-1基礎と4-2専門の関連性分析
        basic_performance = {}
        specialist_performance = {}
        
        for entry in history:
            category = entry.get('category', '')
            question_type = entry.get('question_type', '')
            is_correct = entry.get('is_correct', False)
            
            if question_type == 'basic':
                if category not in basic_performance:
                    basic_performance[category] = {'total': 0, 'correct': 0}
                basic_performance[category]['total'] += 1
                if is_correct:
                    basic_performance[category]['correct'] += 1
            elif question_type == 'specialist':
                if category not in specialist_performance:
                    specialist_performance[category] = {'total': 0, 'correct': 0}
                specialist_performance[category]['total'] += 1
                if is_correct:
                    specialist_performance[category]['correct'] += 1
        
        # 基礎→専門の学習効果分析
        foundation_impact = {}
        for category in basic_performance:
            if category in specialist_performance:
                basic_acc = (basic_performance[category]['correct'] / 
                           basic_performance[category]['total'] if 
                           basic_performance[category]['total'] > 0 else 0)
                specialist_acc = (specialist_performance[category]['correct'] / 
                               specialist_performance[category]['total'] if 
                               specialist_performance[category]['total'] > 0 else 0)
                
                foundation_impact[category] = {
                    'basic_accuracy': basic_acc,
                    'specialist_accuracy': specialist_acc,
                    'correlation': specialist_acc - basic_acc,
                    'foundation_strength': basic_acc >= 0.7
                }
        
        # 部門特有の学習パターン
        department_patterns = {}
        if department_filter and department_filter in RCCMConfig.DEPARTMENTS:
            dept_history = [h for h in history if h.get('department') == department_filter]
            department_patterns = self._analyze_department_specific_patterns(dept_history, department_filter)
        
        return {
            'foundation_impact': foundation_impact,
            'department_patterns': department_patterns,
            'basic_vs_specialist': {
                'basic_total': sum(stats['total'] for stats in basic_performance.values()),
                'specialist_total': sum(stats['total'] for stats in specialist_performance.values()),
                'balance_recommendation': self._get_balance_recommendation(basic_performance, specialist_performance)
            },
            'rccm_readiness': self._assess_rccm_exam_readiness(history, department_filter)
        }
    
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
        
        try:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
        except (TypeError, ValueError, statistics.StatisticsError):
            return {}
        
        # time_consistency計算の安全化
        time_consistency = 1
        if len(times) > 1 and avg_time > 0:
            try:
                stdev_time = statistics.stdev(times)
                time_consistency = 1 - (stdev_time / avg_time)
            except (TypeError, ValueError, statistics.StatisticsError, ZeroDivisionError):
                time_consistency = 1
        
        analysis = {
            'avg_time': avg_time,
            'median_time': median_time,
            'time_consistency': max(0, min(1, time_consistency)),  # 0-1範囲に制限
            'speed_category': self._categorize_speed(avg_time),
        }
        
        # correct_vs_incorrect分析の安全化
        if correct_times and incorrect_times:
            try:
                correct_avg = statistics.mean(correct_times)
                incorrect_avg = statistics.mean(incorrect_times)
                analysis['correct_vs_incorrect'] = {
                    'correct_avg': correct_avg,
                    'incorrect_avg': incorrect_avg,
                    'time_difference': incorrect_avg - correct_avg
                }
            except (TypeError, ValueError, statistics.StatisticsError):
                pass  # correct_vs_incorrectセクションを省略
        
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
        
        # 学習安定性の安全計算
        stability = 0
        volatility = 0
        if len(accuracy_trend) > 1:
            try:
                stdev_accuracy = statistics.stdev(accuracy_trend)
                stability = 1 - stdev_accuracy
                volatility = stdev_accuracy
            except (TypeError, ValueError, statistics.StatisticsError):
                stability = 0
                volatility = 0
        
        return {
            'trend': 'improving' if overall_trend > 0.1 else 'declining' if overall_trend < -0.1 else 'stable',
            'recent_trend': recent_trend,
            'overall_trend': overall_trend,
            'stability': max(0, min(1, stability)),  # 0-1範囲に制限
            'accuracy_points': accuracy_trend,
            'volatility': max(0, volatility)  # 非負値に制限
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
                                              error_analysis: Dict,
                                              department_analysis: Dict = None,
                                              question_type_analysis: Dict = None) -> Dict[str, Any]:
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
    
    def _generate_learning_plan(self, weak_areas: Dict, history: List[Dict], department_filter: str = None) -> Dict[str, Any]:
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
    
    def _insufficient_data_response(self, department_filter: str = None) -> Dict[str, Any]:
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
        
        if total_errors == 0:
            return {}
        
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
    
    def _prioritize_recommendations(self, weak_areas: Dict, department_filter: str = None) -> List[Dict[str, Any]]:
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
    
    # === 新しい部門別分析のヘルパーメソッド ===
    
    def _calculate_department_weakness_score(self, department: str, accuracy: float, 
                                           recent_accuracy: float, avg_time: float, 
                                           sample_size: float) -> float:
        """部門特有の弱点スコア計算"""
        # 基本弱点スコア
        base_weakness = 1 - accuracy
        
        # 部門特有の難易度調整
        dept_difficulty_factor = self._get_department_difficulty_factor(department)
        adjusted_weakness = base_weakness * dept_difficulty_factor
        
        # 最近のパフォーマンス考慮
        trend_factor = 1 - recent_accuracy
        
        # 時間効率（部門により基準時間が異なる）
        target_time = self._get_department_target_time(department)
        if target_time > 0:
            time_factor = max(0, (avg_time - target_time) / target_time * 0.3)
        else:
            time_factor = 0
        
        # サンプルサイズによる信頼度
        confidence = min(sample_size / 15, 1.0)
        
        weakness_score = (adjusted_weakness * 0.4 + trend_factor * 0.4 + time_factor) * confidence
        
        return min(max(weakness_score, 0), 1)
    
    def _get_department_difficulty_factor(self, department: str) -> float:
        """部門別の難易度調整係数"""
        difficulty_factors = {
            'civil_planning': 1.2,  # 河川・砂防は複雑
            'construction_env': 1.15,  # 建設環境も難しい
            'comprehensive': 1.25,  # 総合技術監理が最難関
            'power_civil': 1.1,
            'forestry': 1.05,
            'road': 1.0,  # 標準
            'port_airport': 1.05,
            'railway': 1.05,
            'urban_planning': 1.1,
            'construction_mgmt': 1.1,
            'fisheries': 1.05,
            'agriculture': 1.05
        }
        return difficulty_factors.get(department, 1.0)
    
    def _get_department_target_time(self, department: str) -> float:
        """部門別の目標回答時間（秒）"""
        target_times = {
            'civil_planning': 75,  # 複雑な計算問題が多い
            'construction_env': 70,
            'comprehensive': 80,  # 幅広い知識が必要
            'power_civil': 65,
            'road': 60,  # 標準
            'port_airport': 65,
            'railway': 65,
            'urban_planning': 70,
            'construction_mgmt': 70,
            'forestry': 60,
            'fisheries': 60,
            'agriculture': 60
        }
        return target_times.get(department, 60)
    
    def _get_department_insights(self, department: str, stats: Dict) -> List[str]:
        """部門別の学習インサイト"""
        insights = []
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        # 部門特有のアドバイス
        dept_advice = {
            'road': [
                "道路分野は基礎が重要です。構造力学と材料の理解を深めましょう。",
                "舗装工学と道路設計基準をしっかり復習してください。"
            ],
            'civil_planning': [
                "河川・砂防分野は水理学の基礎が重要です。",
                "災害対策と環境への配慮も重要なポイントです。"
            ],
            'construction_env': [
                "環境アセスメントと環境保全技術を重点的に学習しましょう。",
                "最新の環境基準と法規制の理解が必要です。"
            ],
            'comprehensive': [
                "総合技術監理は幅広い知識が必要です。",
                "プロジェクトマネジメントと品質管理を重視してください。"
            ]
        }
        
        specific_advice = dept_advice.get(department, ["継続的な学習で知識を深めましょう。"])
        
        if accuracy < 0.6:
            insights.extend(specific_advice)
            insights.append("基礎知識の見直しから始めることをお勧めします。")
        elif accuracy < 0.8:
            insights.append("応用問題にも挑戦して理解を深めましょう。")
        else:
            insights.append("優秀な成績です。より難しい問題で実力を試してみてください。")
        
        return insights[:3]  # 最大3つのインサイト
    
    def _get_question_type_recommendation(self, question_type: str, accuracy: float) -> str:
        """問題種別別の学習推奨"""
        if question_type == 'basic':
            if accuracy < 0.7:
                return "4-1基礎は試験の土台です。徹底的に復習して確実に理解しましょう。"
            else:
                return "基礎は十分です。4-2専門分野への応用を意識しましょう。"
        elif question_type == 'specialist':
            if accuracy < 0.6:
                return "専門分野の基礎から見直し、段階的に理解を深めましょう。"
            elif accuracy < 0.8:
                return "専門知識を実践的な問題で活用できるよう練習しましょう。"
            else:
                return "優秀です。最新の技術動向も把握しておきましょう。"
        else:
            return "継続的な学習で知識を深めていきましょう。"
    
    def _analyze_department_specific_patterns(self, dept_history: List[Dict], department: str) -> Dict[str, Any]:
        """部門特有のパターン分析"""
        if not dept_history:
            return {}
        
        # カテゴリ間の関連性分析
        category_performance = {}
        for entry in dept_history:
            category = entry.get('category', '')
            is_correct = entry.get('is_correct', False)
            
            if category not in category_performance:
                category_performance[category] = {'total': 0, 'correct': 0}
            category_performance[category]['total'] += 1
            if is_correct:
                category_performance[category]['correct'] += 1
        
        # 部門特有の学習パターン
        patterns = {
            'category_strengths': [],
            'category_weaknesses': [],
            'learning_sequence_recommendation': []
        }
        
        for category, perf in category_performance.items():
            if perf['total'] >= 3:  # 最低3問以上
                accuracy = perf['correct'] / perf['total']
                if accuracy >= 0.8:
                    patterns['category_strengths'].append(category)
                elif accuracy < 0.5:
                    patterns['category_weaknesses'].append(category)
        
        # 部門別の学習順序推奨
        if department == 'road':
            patterns['learning_sequence_recommendation'] = [
                "構造力学・材料", "土質及び基礎", "道路設計", "舗装工学", "道路維持管理"
            ]
        elif department == 'civil_planning':
            patterns['learning_sequence_recommendation'] = [
                "水理学", "河川工学", "砂防工学", "海岸工学", "環境対策"
            ]
        
        return patterns
    
    def _get_balance_recommendation(self, basic_perf: Dict, specialist_perf: Dict) -> str:
        """4-1基礎と4-2専門のバランス推奨"""
        basic_total = sum(stats['total'] for stats in basic_perf.values())
        specialist_total = sum(stats['total'] for stats in specialist_perf.values())
        
        if basic_total == 0 and specialist_total == 0:
            return "4-1基礎問題から始めることをお勧めします。"
        elif basic_total < 20:
            return "4-1基礎問題をもう少し練習してから4-2専門に進みましょう。"
        elif specialist_total < basic_total * 0.5:
            return "基礎は十分です。4-2専門問題により多く取り組みましょう。"
        elif specialist_total > basic_total * 2:
            return "専門に偏りすぎています。4-1基礎の復習も大切です。"
        else:
            return "基礎と専門のバランスが良好です。"
    
    def _assess_rccm_exam_readiness(self, history: List[Dict], department_filter: str = None) -> Dict[str, Any]:
        """RCCM試験準備度評価"""
        if not history:
            return {'readiness_level': 'insufficient_data'}
        
        # 基本統計
        total_questions = len(history)
        if total_questions == 0:
            return {'readiness_level': 'insufficient_data'}
        
        correct_count = sum(1 for h in history if h.get('is_correct', False))
        overall_accuracy = correct_count / total_questions
        
        # 4-1 vs 4-2 の成績
        basic_questions = [h for h in history if h.get('question_type') == 'basic']
        specialist_questions = [h for h in history if h.get('question_type') == 'specialist']
        
        basic_accuracy = (sum(1 for h in basic_questions if h.get('is_correct', False)) / 
                         len(basic_questions) if basic_questions else 0)
        specialist_accuracy = (sum(1 for h in specialist_questions if h.get('is_correct', False)) / 
                             len(specialist_questions) if specialist_questions else 0)
        
        # 準備度判定
        if total_questions < 50:
            readiness_level = 'early_stage'
        elif basic_accuracy >= 0.7 and specialist_accuracy >= 0.6 and total_questions >= 100:
            readiness_level = 'exam_ready'
        elif basic_accuracy >= 0.6 and specialist_accuracy >= 0.5:
            readiness_level = 'approaching_ready'
        else:
            readiness_level = 'needs_improvement'
        
        readiness_messages = {
            'early_stage': '学習初期段階です。まずは基礎固めに集中しましょう。',
            'needs_improvement': '基礎知識の強化が必要です。苦手分野を重点的に学習してください。',
            'approaching_ready': '順調に進歩しています。弱点を補強すれば合格レベルに到達できます。',
            'exam_ready': '試験準備は順調です。実戦形式の練習で仕上げましょう。'
        }
        
        return {
            'readiness_level': readiness_level,
            'message': readiness_messages.get(readiness_level, '継続的な学習を続けましょう。'),
            'basic_accuracy': basic_accuracy,
            'specialist_accuracy': specialist_accuracy,
            'overall_accuracy': overall_accuracy,
            'total_experience': total_questions,
            'recommended_next_steps': self._get_next_steps_recommendation(readiness_level, basic_accuracy, specialist_accuracy)
        }
    
    def _get_next_steps_recommendation(self, readiness_level: str, basic_acc: float, specialist_acc: float) -> List[str]:
        """次のステップ推奨"""
        recommendations = []
        
        if readiness_level == 'early_stage':
            recommendations = [
                "4-1基礎問題を毎日10問解く",
                "間違えた問題の解説を必ず読む",
                "基本的な公式と定義を覚える"
            ]
        elif readiness_level == 'needs_improvement':
            if basic_acc < 0.6:
                recommendations.append("4-1基礎の徹底復習")
            if specialist_acc < 0.5:
                recommendations.append("4-2専門の基礎理解")
            recommendations.append("弱点カテゴリの集中学習")
        elif readiness_level == 'approaching_ready':
            recommendations = [
                "模擬試験形式での練習",
                "時間を意識した問題演習",
                "最新の法規制・技術動向の確認"
            ]
        else:  # exam_ready
            recommendations = [
                "実戦形式の模擬試験",
                "苦手分野の最終チェック",
                "試験当日の時間配分練習"
            ]
        
        return recommendations

# グローバルインスタンス
ai_analyzer = AILearningAnalyzer()