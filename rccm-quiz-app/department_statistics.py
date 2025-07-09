"""
RCCM学習アプリ - 部門・問題種別別統計分析エンジン
詳細な学習進捗と成績分析機能を提供
"""

import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import logging

# RCCM設定をインポート
from config import RCCMConfig

logger = logging.getLogger(__name__)

class DepartmentStatisticsAnalyzer:
    """部門・問題種別別統計分析エンジン"""
    
    def __init__(self):
        self.department_weights = {
            'road': 1.0,  # 道路（基準）
            'civil_planning': 1.2,  # 河川・砂防（複雑）
            'construction_env': 1.15,  # 建設環境
            'comprehensive': 1.3,  # 総合技術監理（最難関）
            'port_airport': 1.1,  # 港湾・空港
            'railway': 1.05,  # 鉄道
            'urban_planning': 1.1,  # 都市計画
            'construction_mgmt': 1.1,  # 建設管理
            'power_civil': 1.2,  # 電力土木
            'forestry': 1.0,  # 森林土木
            'fisheries': 1.0,  # 水産土木
            'agriculture': 1.0  # 農業土木
        }
    
    def _safe_mean(self, values: List[float]) -> float:
        """安全な平均値計算"""
        try:
            return statistics.mean(values) if values else 0
        except (TypeError, ValueError, statistics.StatisticsError):
            return 0
    
    def generate_comprehensive_department_report(self, user_session: Dict) -> Dict[str, Any]:
        """包括的な部門別統計レポートを生成"""
        history = user_session.get('history', [])
        
        if not history:
            return self._empty_report()
        
        # 各種統計分析を実行
        department_analysis = self._analyze_department_performance(history)
        question_type_analysis = self._analyze_question_type_performance(history)
        cross_analysis = self._analyze_department_question_type_cross(history)
        time_series_analysis = self._analyze_time_series_trends(history)
        learning_efficiency = self._calculate_learning_efficiency(history)
        mastery_assessment = self._assess_mastery_levels(history)
        
        # 学習推奨を生成
        recommendations = self._generate_learning_recommendations(
            department_analysis, question_type_analysis, cross_analysis
        )
        
        # 総合レポート作成
        comprehensive_report = {
            'overview': self._generate_overview_stats(history),
            'department_analysis': department_analysis,
            'question_type_analysis': question_type_analysis,
            'cross_analysis': cross_analysis,
            'time_series_analysis': time_series_analysis,
            'learning_efficiency': learning_efficiency,
            'mastery_assessment': mastery_assessment,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat(),
            'total_questions_analyzed': len(history)
        }
        
        logger.info(f"部門別統計レポート生成完了: {len(history)}問分析")
        
        return comprehensive_report
    
    def _analyze_department_performance(self, history: List[Dict]) -> Dict[str, Any]:
        """部門別成績分析"""
        department_stats = defaultdict(lambda: {
            'total_questions': 0,
            'correct_answers': 0,
            'total_time': 0,
            'recent_performance': [],
            'categories': set(),
            'question_types': defaultdict(lambda: {'total': 0, 'correct': 0}),
            'difficulty_distribution': defaultdict(int),
            'weekly_progress': defaultdict(lambda: {'total': 0, 'correct': 0})
        })
        
        # 最近30問の範囲を設定
        recent_threshold = max(0, len(history) - 30)
        
        for i, entry in enumerate(history):
            department = entry.get('department', 'unknown')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            category = entry.get('category', '')
            question_type = entry.get('question_type', 'unknown')
            difficulty = entry.get('difficulty', '標準')
            date_str = entry.get('date', '')
            
            stats = department_stats[department]
            
            # 基本統計
            stats['total_questions'] += 1
            if is_correct:
                stats['correct_answers'] += 1
            stats['total_time'] += elapsed_time
            stats['categories'].add(category)
            
            # 問題種別統計
            stats['question_types'][question_type]['total'] += 1
            if is_correct:
                stats['question_types'][question_type]['correct'] += 1
            
            # 難易度分布
            stats['difficulty_distribution'][difficulty] += 1
            
            # 最近のパフォーマンス（最新30問）
            if i >= recent_threshold:
                stats['recent_performance'].append(is_correct)
            
            # 週次進捗（日付がある場合）
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                    week_key = date.strftime('%Y-W%U')  # 年-週番号
                    stats['weekly_progress'][week_key]['total'] += 1
                    if is_correct:
                        stats['weekly_progress'][week_key]['correct'] += 1
                except:
                    pass
        
        # 分析結果の計算
        analysis = {}
        for department, stats in department_stats.items():
            if stats['total_questions'] > 0:
                accuracy = stats['correct_answers'] / stats['total_questions']
                avg_time = stats['total_time'] / stats['total_questions']
                recent_accuracy = (
                    sum(stats['recent_performance']) / len(stats['recent_performance'])
                    if stats['recent_performance'] else accuracy
                )
                
                # 部門重みを考慮した調整済み成績
                dept_weight = self.department_weights.get(department, 1.0)
                weighted_accuracy = accuracy / dept_weight
                
                # 問題種別別分析
                type_analysis = {}
                for qtype, type_stats in stats['question_types'].items():
                    if type_stats['total'] > 0:
                        type_accuracy = type_stats['correct'] / type_stats['total']
                        type_analysis[qtype] = {
                            'accuracy': type_accuracy,
                            'total_questions': type_stats['total'],
                            'correct_answers': type_stats['correct']
                        }
                
                # 週次進捗分析
                weekly_trends = []
                for week, week_stats in sorted(stats['weekly_progress'].items()):
                    if week_stats['total'] > 0:
                        week_accuracy = week_stats['correct'] / week_stats['total']
                        weekly_trends.append({
                            'week': week,
                            'accuracy': week_accuracy,
                            'total_questions': week_stats['total']
                        })
                
                # 部門情報を取得
                dept_info = RCCMConfig.DEPARTMENTS.get(department, {
                    'name': department, 'description': '不明な部門'
                })
                
                analysis[department] = {
                    'name': dept_info.get('name', department),
                    'description': dept_info.get('description', ''),
                    'icon': dept_info.get('icon', '📋'),
                    'color': dept_info.get('color', '#6c757d'),
                    'total_questions': stats['total_questions'],
                    'correct_answers': stats['correct_answers'],
                    'accuracy': accuracy,
                    'recent_accuracy': recent_accuracy,
                    'weighted_accuracy': weighted_accuracy,
                    'avg_time_per_question': avg_time,
                    'categories_covered': len(stats['categories']),
                    'question_type_analysis': type_analysis,
                    'difficulty_distribution': dict(stats['difficulty_distribution']),
                    'weekly_trends': weekly_trends,
                    'improvement_trend': recent_accuracy - accuracy,
                    'performance_grade': self._calculate_performance_grade(accuracy, dept_weight),
                    'study_recommendation': self._get_department_study_recommendation(
                        department, accuracy, type_analysis
                    )
                }
        
        return analysis
    
    def _analyze_question_type_performance(self, history: List[Dict]) -> Dict[str, Any]:
        """問題種別別成績分析（4-1基礎 vs 4-2専門）"""
        type_stats = defaultdict(lambda: {
            'total_questions': 0,
            'correct_answers': 0,
            'total_time': 0,
            'departments': defaultdict(lambda: {'total': 0, 'correct': 0}),
            'categories': defaultdict(lambda: {'total': 0, 'correct': 0}),
            'difficulty_distribution': defaultdict(int),
            'time_series': []
        })
        
        for entry in history:
            question_type = entry.get('question_type', 'unknown')
            department = entry.get('department', 'unknown')
            category = entry.get('category', 'unknown')
            difficulty = entry.get('difficulty', '標準')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            date_str = entry.get('date', '')
            
            stats = type_stats[question_type]
            
            # 基本統計
            stats['total_questions'] += 1
            if is_correct:
                stats['correct_answers'] += 1
            stats['total_time'] += elapsed_time
            
            # 部門別統計
            stats['departments'][department]['total'] += 1
            if is_correct:
                stats['departments'][department]['correct'] += 1
            
            # カテゴリ別統計
            stats['categories'][category]['total'] += 1
            if is_correct:
                stats['categories'][category]['correct'] += 1
            
            # 難易度分布
            stats['difficulty_distribution'][difficulty] += 1
            
            # 時系列データ
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                    stats['time_series'].append({
                        'date': date.strftime('%Y-%m-%d'),
                        'is_correct': is_correct,
                        'elapsed_time': elapsed_time
                    })
                except:
                    pass
        
        # 分析結果の計算
        analysis = {}
        for question_type, stats in type_stats.items():
            if stats['total_questions'] > 0:
                accuracy = stats['correct_answers'] / stats['total_questions']
                avg_time = stats['total_time'] / stats['total_questions']
                
                # 部門別成績
                department_performance = {}
                for dept, dept_stats in stats['departments'].items():
                    if dept_stats['total'] > 0:
                        dept_accuracy = dept_stats['correct'] / dept_stats['total']
                        department_performance[dept] = {
                            'accuracy': dept_accuracy,
                            'total_questions': dept_stats['total'],
                            'department_name': RCCMConfig.DEPARTMENTS.get(dept, {}).get('name', dept)
                        }
                
                # カテゴリ別成績
                category_performance = {}
                for cat, cat_stats in stats['categories'].items():
                    if cat_stats['total'] > 0:
                        cat_accuracy = cat_stats['correct'] / cat_stats['total']
                        category_performance[cat] = {
                            'accuracy': cat_accuracy,
                            'total_questions': cat_stats['total']
                        }
                
                # 問題種別情報を取得
                type_info = RCCMConfig.QUESTION_TYPES.get(question_type, {
                    'name': question_type, 'description': '不明な問題種別'
                })
                
                analysis[question_type] = {
                    'name': type_info.get('name', question_type),
                    'description': type_info.get('description', ''),
                    'total_questions': stats['total_questions'],
                    'correct_answers': stats['correct_answers'],
                    'accuracy': accuracy,
                    'avg_time_per_question': avg_time,
                    'department_performance': department_performance,
                    'category_performance': category_performance,
                    'difficulty_distribution': dict(stats['difficulty_distribution']),
                    'performance_grade': self._calculate_performance_grade(accuracy, 1.0),
                    'study_focus': self._get_question_type_study_focus(question_type, accuracy)
                }
        
        return analysis
    
    def _analyze_department_question_type_cross(self, history: List[Dict]) -> Dict[str, Any]:
        """部門×問題種別のクロス分析"""
        cross_stats = defaultdict(lambda: defaultdict(lambda: {
            'total': 0, 'correct': 0, 'total_time': 0
        }))
        
        for entry in history:
            department = entry.get('department', 'unknown')
            question_type = entry.get('question_type', 'unknown')
            is_correct = entry.get('is_correct', False)
            elapsed_time = entry.get('elapsed', 0)
            
            stats = cross_stats[department][question_type]
            stats['total'] += 1
            if is_correct:
                stats['correct'] += 1
            stats['total_time'] += elapsed_time
        
        # クロス分析結果
        cross_analysis = {}
        correlations = []
        
        for department, dept_data in cross_stats.items():
            dept_analysis = {}
            for question_type, type_data in dept_data.items():
                if type_data['total'] > 0:
                    accuracy = type_data['correct'] / type_data['total']
                    avg_time = type_data['total_time'] / type_data['total']
                    
                    dept_analysis[question_type] = {
                        'accuracy': accuracy,
                        'total_questions': type_data['total'],
                        'avg_time': avg_time
                    }
            
            if dept_analysis:
                cross_analysis[department] = dept_analysis
                
                # 基礎→専門の相関分析
                if 'basic' in dept_analysis and 'specialist' in dept_analysis:
                    basic_acc = dept_analysis['basic']['accuracy']
                    specialist_acc = dept_analysis['specialist']['accuracy']
                    correlation = specialist_acc - basic_acc
                    
                    correlations.append({
                        'department': department,
                        'department_name': RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department),
                        'basic_accuracy': basic_acc,
                        'specialist_accuracy': specialist_acc,
                        'correlation': correlation,
                        'foundation_strength': basic_acc >= 0.7,
                        'learning_efficiency': specialist_acc / basic_acc if basic_acc > 0 else 0
                    })
        
        return {
            'cross_performance': cross_analysis,
            'basic_specialist_correlations': correlations,
            'overall_correlation': self._safe_mean([c['correlation'] for c in correlations]) if correlations else 0
        }
    
    def _analyze_time_series_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """時系列学習傾向分析"""
        if len(history) < 10:
            return {'trend': 'insufficient_data'}
        
        # 日付別集計
        daily_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        weekly_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        monthly_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        for entry in history:
            date_str = entry.get('date', '')
            is_correct = entry.get('is_correct', False)
            
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                    day_key = date.strftime('%Y-%m-%d')
                    week_key = date.strftime('%Y-W%U')
                    month_key = date.strftime('%Y-%m')
                    
                    daily_stats[day_key]['total'] += 1
                    weekly_stats[week_key]['total'] += 1
                    monthly_stats[month_key]['total'] += 1
                    
                    if is_correct:
                        daily_stats[day_key]['correct'] += 1
                        weekly_stats[week_key]['correct'] += 1
                        monthly_stats[month_key]['correct'] += 1
                except:
                    continue
        
        # トレンド分析
        def calculate_trend(stats_dict):
            if len(stats_dict) < 2:
                return []
            
            trend_data = []
            for period, stats in sorted(stats_dict.items()):
                if stats['total'] > 0:
                    accuracy = stats['correct'] / stats['total']
                    trend_data.append({
                        'period': period,
                        'accuracy': accuracy,
                        'total_questions': stats['total']
                    })
            return trend_data
        
        daily_trend = calculate_trend(daily_stats)
        weekly_trend = calculate_trend(weekly_stats)
        monthly_trend = calculate_trend(monthly_stats)
        
        # 全体的なトレンド方向の判定
        if weekly_trend and len(weekly_trend) >= 2:
            recent_weeks = weekly_trend[-3:] if len(weekly_trend) >= 3 else weekly_trend
            recent_avg = self._safe_mean([w['accuracy'] for w in recent_weeks])
            early_weeks = weekly_trend[:3] if len(weekly_trend) >= 3 else weekly_trend[:-1]
            early_avg = self._safe_mean([w['accuracy'] for w in early_weeks]) if early_weeks else 0
            
            trend_direction = 'improving' if recent_avg > early_avg + 0.05 else \
                            'declining' if recent_avg < early_avg - 0.05 else 'stable'
        else:
            trend_direction = 'insufficient_data'
        
        return {
            'daily_trend': daily_trend,
            'weekly_trend': weekly_trend,
            'monthly_trend': monthly_trend,
            'trend_direction': trend_direction,
            'analysis_period_days': len(daily_stats),
            'total_study_days': len([d for d in daily_stats.values() if d['total'] > 0])
        }
    
    def _calculate_learning_efficiency(self, history: List[Dict]) -> Dict[str, Any]:
        """学習効率の計算"""
        if not history:
            return {}
        
        total_time = sum(entry.get('elapsed', 0) for entry in history)
        total_questions = len(history)
        correct_answers = sum(1 for entry in history if entry.get('is_correct', False))
        
        # 基本効率指標
        avg_time_per_question = total_time / total_questions if total_questions > 0 else 0
        accuracy_rate = correct_answers / total_questions if total_questions > 0 else 0
        efficiency_score = correct_answers / (total_time / 60) if total_time > 0 else 0  # 正答数/分
        
        # 部門別効率
        department_efficiency = {}
        dept_stats = defaultdict(lambda: {'time': 0, 'questions': 0, 'correct': 0})
        
        for entry in history:
            department = entry.get('department', 'unknown')
            elapsed = entry.get('elapsed', 0)
            is_correct = entry.get('is_correct', False)
            
            dept_stats[department]['time'] += elapsed
            dept_stats[department]['questions'] += 1
            if is_correct:
                dept_stats[department]['correct'] += 1
        
        for department, stats in dept_stats.items():
            if stats['questions'] > 0 and stats['time'] > 0:
                dept_efficiency = stats['correct'] / (stats['time'] / 60)
                department_efficiency[department] = {
                    'efficiency_score': dept_efficiency,
                    'avg_time': stats['time'] / stats['questions'],
                    'accuracy': stats['correct'] / stats['questions']
                }
        
        return {
            'overall_efficiency_score': efficiency_score,
            'avg_time_per_question': avg_time_per_question,
            'accuracy_rate': accuracy_rate,
            'department_efficiency': department_efficiency,
            'efficiency_grade': self._grade_efficiency(efficiency_score),
            'time_management_advice': self._get_time_management_advice(avg_time_per_question)
        }
    
    def _assess_mastery_levels(self, history: List[Dict]) -> Dict[str, Any]:
        """習熟度レベルの評価"""
        # 部門別習熟度
        department_mastery = {}
        question_type_mastery = {}
        
        # 部門別習熟度計算
        dept_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'recent_correct': 0, 'recent_total': 0})
        
        recent_threshold = max(0, len(history) - 20)  # 最近20問
        
        for i, entry in enumerate(history):
            department = entry.get('department', 'unknown')
            question_type = entry.get('question_type', 'unknown')
            is_correct = entry.get('is_correct', False)
            
            # 部門別統計
            dept_stats[department]['total'] += 1
            if is_correct:
                dept_stats[department]['correct'] += 1
            
            # 最近の成績
            if i >= recent_threshold:
                dept_stats[department]['recent_total'] += 1
                if is_correct:
                    dept_stats[department]['recent_correct'] += 1
        
        for department, stats in dept_stats.items():
            if stats['total'] >= 5:  # 最低5問以上
                overall_accuracy = stats['correct'] / stats['total']
                recent_accuracy = (stats['recent_correct'] / stats['recent_total'] 
                                 if stats['recent_total'] > 0 else overall_accuracy)
                
                # 習熟度レベル判定
                mastery_level = self._determine_mastery_level(overall_accuracy, recent_accuracy, stats['total'])
                
                department_mastery[department] = {
                    'mastery_level': mastery_level,
                    'overall_accuracy': overall_accuracy,
                    'recent_accuracy': recent_accuracy,
                    'total_questions': stats['total'],
                    'improvement_trend': recent_accuracy - overall_accuracy,
                    'department_name': RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)
                }
        
        return {
            'department_mastery': department_mastery,
            'question_type_mastery': question_type_mastery,
            'overall_mastery_summary': self._generate_mastery_summary(department_mastery)
        }
    
    def _generate_learning_recommendations(self, dept_analysis: Dict, type_analysis: Dict, cross_analysis: Dict) -> Dict[str, Any]:
        """学習推奨事項の生成"""
        recommendations = {
            'priority_departments': [],
            'priority_question_types': [],
            'study_strategy': [],
            'time_allocation': {},
            'next_steps': []
        }
        
        # 優先部門の特定（成績の低い順）
        dept_priorities = []
        for dept_id, dept_data in dept_analysis.items():
            if dept_data['total_questions'] >= 3:
                priority_score = (1 - dept_data['accuracy']) * dept_data['total_questions']
                dept_priorities.append({
                    'department': dept_id,
                    'name': dept_data['name'],
                    'priority_score': priority_score,
                    'accuracy': dept_data['accuracy'],
                    'recommendation': dept_data['study_recommendation']
                })
        
        dept_priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        recommendations['priority_departments'] = dept_priorities[:3]
        
        # 問題種別の優先度
        for type_id, type_data in type_analysis.items():
            if type_data['total_questions'] >= 3:
                recommendations['priority_question_types'].append({
                    'question_type': type_id,
                    'name': type_data['name'],
                    'accuracy': type_data['accuracy'],
                    'focus': type_data['study_focus']
                })
        
        # 学習戦略
        if dept_priorities:
            lowest_dept = dept_priorities[0]
            if lowest_dept['accuracy'] < 0.5:
                recommendations['study_strategy'].append(
                    f"{lowest_dept['name']}の基礎から集中的に復習することを推奨します。"
                )
            elif lowest_dept['accuracy'] < 0.7:
                recommendations['study_strategy'].append(
                    f"{lowest_dept['name']}の応用問題で実力を向上させましょう。"
                )
        
        # 基礎→専門の相関から推奨
        correlations = cross_analysis.get('basic_specialist_correlations', [])
        for corr in correlations:
            if not corr['foundation_strength']:
                recommendations['study_strategy'].append(
                    f"{corr['department_name']}では基礎（4-1）の理解を深めることで専門（4-2）の成績向上が期待できます。"
                )
        
        return recommendations
    
    # ヘルパーメソッド群
    
    def _empty_report(self) -> Dict[str, Any]:
        """空のレポートを返す"""
        return {
            'overview': {
                'total_questions': 0, 
                'correct_answers': 0,
                'overall_accuracy': 0.0,
                'departments_studied': 0,
                'department_coverage': 0.0,
                'question_types_studied': 0,
                'performance_summary': '学習データがありません。問題に挑戦してください。'
            },
            'department_analysis': {},
            'question_type_analysis': {},
            'cross_analysis': {},
            'time_series_analysis': {'trend': 'no_data'},
            'learning_efficiency': {},
            'mastery_assessment': {},
            'recommendations': {
                'priority_departments': [],
                'priority_question_types': [],
                'study_strategy': ['まずは興味のある部門から学習を始めましょう。'],
                'time_allocation': {},
                'next_steps': []
            },
            'generated_at': datetime.now().isoformat(),
            'total_questions_analyzed': 0
        }
    
    def _generate_overview_stats(self, history: List[Dict]) -> Dict[str, Any]:
        """概要統計の生成"""
        total_questions = len(history)
        correct_answers = sum(1 for h in history if h.get('is_correct', False))
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        # 部門カバレッジ
        departments_studied = len(set(h.get('department') for h in history if h.get('department')))
        total_departments = len(RCCMConfig.DEPARTMENTS)
        
        # 問題種別カバレッジ
        types_studied = len(set(h.get('question_type') for h in history if h.get('question_type')))
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'overall_accuracy': accuracy,
            'departments_studied': departments_studied,
            'department_coverage': departments_studied / total_departments,
            'question_types_studied': types_studied,
            'performance_summary': self._get_performance_summary(accuracy)
        }
    
    def _calculate_performance_grade(self, accuracy: float, weight: float) -> str:
        """成績グレードの計算"""
        adjusted_accuracy = accuracy / weight
        
        if adjusted_accuracy >= 0.9:
            return 'A+'
        elif adjusted_accuracy >= 0.8:
            return 'A'
        elif adjusted_accuracy >= 0.7:
            return 'B+'
        elif adjusted_accuracy >= 0.6:
            return 'B'
        elif adjusted_accuracy >= 0.5:
            return 'C+'
        elif adjusted_accuracy >= 0.4:
            return 'C'
        else:
            return 'D'
    
    def _get_department_study_recommendation(self, department: str, accuracy: float, type_analysis: Dict) -> str:
        """部門別学習推奨"""
        if accuracy < 0.5:
            return f"基礎から徹底的に復習しましょう。"
        elif accuracy < 0.7:
            return f"応用問題で実力を向上させましょう。"
        elif accuracy < 0.85:
            return f"高難易度問題にチャレンジしましょう。"
        else:
            return f"優秀な成績です。他部門への展開を検討してください。"
    
    def _get_question_type_study_focus(self, question_type: str, accuracy: float) -> str:
        """問題種別別学習重点"""
        if question_type == 'basic':
            if accuracy < 0.7:
                return "基礎知識の徹底理解が必要です。"
            else:
                return "基礎は良好です。専門分野への応用を進めましょう。"
        elif question_type == 'specialist':
            if accuracy < 0.6:
                return "専門分野の基礎理解から始めましょう。"
            else:
                return "専門知識を実践に活用できるレベルです。"
        else:
            return "継続的な学習を続けてください。"
    
    def _determine_mastery_level(self, overall_accuracy: float, recent_accuracy: float, total_questions: int) -> str:
        """習熟度レベルの判定"""
        if total_questions < 10:
            return "初級"
        elif overall_accuracy >= 0.8 and recent_accuracy >= 0.8:
            return "上級"
        elif overall_accuracy >= 0.6 and recent_accuracy >= 0.6:
            return "中級"
        else:
            return "初級"
    
    def _generate_mastery_summary(self, department_mastery: Dict) -> Dict[str, Any]:
        """習熟度サマリーの生成"""
        if not department_mastery:
            return {'total_departments': 0, 'mastery_distribution': {}}
        
        mastery_counts = Counter(data['mastery_level'] for data in department_mastery.values())
        
        return {
            'total_departments': len(department_mastery),
            'mastery_distribution': dict(mastery_counts),
            'advanced_departments': [dept for dept, data in department_mastery.items() 
                                   if data['mastery_level'] == '上級'],
            'improvement_needed': [dept for dept, data in department_mastery.items() 
                                 if data['mastery_level'] == '初級']
        }
    
    def _grade_efficiency(self, efficiency_score: float) -> str:
        """効率グレードの判定"""
        if efficiency_score >= 2.0:
            return "非常に高効率"
        elif efficiency_score >= 1.5:
            return "高効率"
        elif efficiency_score >= 1.0:
            return "標準"
        elif efficiency_score >= 0.5:
            return "要改善"
        else:
            return "低効率"
    
    def _get_time_management_advice(self, avg_time: float) -> str:
        """時間管理アドバイス"""
        if avg_time < 30:
            return "回答が速すぎる可能性があります。じっくり考えて解答しましょう。"
        elif avg_time < 60:
            return "適切な回答時間です。この調子を維持しましょう。"
        elif avg_time < 90:
            return "やや時間がかかっています。効率的な解法を身につけましょう。"
        else:
            return "時間がかかりすぎています。基礎知識の定着を図りましょう。"
    
    def _get_performance_summary(self, accuracy: float) -> str:
        """成績サマリー"""
        if accuracy >= 0.85:
            return "優秀な成績です。"
        elif accuracy >= 0.7:
            return "良好な成績です。"
        elif accuracy >= 0.55:
            return "標準的な成績です。"
        else:
            return "改善の余地があります。"

# グローバルインスタンス
department_statistics = DepartmentStatisticsAnalyzer()