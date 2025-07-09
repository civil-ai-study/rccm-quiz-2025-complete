"""
RCCM学習アプリ - 管理者ダッシュボード
問題管理、ユーザー進捗監視、システム分析機能
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import hashlib

from utils import load_rccm_data_files
from config import RCCMConfig

logger = logging.getLogger(__name__)

class AdminDashboard:
    """管理者ダッシュボード機能"""
    
    def __init__(self, data_dir: str = 'data', user_data_dir: str = 'user_data'):
        self.data_dir = data_dir
        self.user_data_dir = user_data_dir
        self.questions = load_rccm_data_files(data_dir)
        logger.info(f"管理者ダッシュボード初期化: {len(self.questions)}問読み込み完了")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """システム全体概要"""
        user_stats = self._analyze_all_users()
        question_stats = self._analyze_question_data()
        performance_stats = self._get_performance_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'questions': question_stats,
            'users': user_stats,
            'performance': performance_stats,
            'alerts': self._get_system_alerts()
        }
    
    def get_question_management_data(self) -> Dict[str, Any]:
        """問題管理データ"""
        return {
            'total_questions': len(self.questions),
            'by_department': self._count_by_department(),
            'by_category': self._count_by_category(),
            'by_year': self._count_by_year(),
            'by_type': self._count_by_type(),
            'difficulty_distribution': self._analyze_difficulty_distribution(),
            'question_quality': self._analyze_question_quality(),
            'data_integrity': self._check_data_integrity()
        }
    
    def get_user_progress_overview(self) -> Dict[str, Any]:
        """ユーザー進捗概要"""
        all_users = self._load_all_user_data()
        
        progress_summary = {
            'total_users': len(all_users),
            'active_users_last_7days': 0,
            'active_users_last_30days': 0,
            'completion_rates': [],
            'average_accuracy': 0,
            'total_sessions': 0,
            'department_popularity': defaultdict(int),
            'learning_patterns': defaultdict(int)
        }
        
        cutoff_7days = datetime.now() - timedelta(days=7)
        cutoff_30days = datetime.now() - timedelta(days=30)
        
        total_accuracy = 0
        valid_users = 0
        
        for user_id, user_data in all_users.items():
            history = user_data.get('history', [])
            if not history:
                continue
                
            valid_users += 1
            
            # 最終アクティビティ日時
            last_activity = self._get_last_activity(history)
            if last_activity:
                if last_activity >= cutoff_7days:
                    progress_summary['active_users_last_7days'] += 1
                if last_activity >= cutoff_30days:
                    progress_summary['active_users_last_30days'] += 1
            
            # 正答率計算
            correct_count = sum(1 for h in history if h.get('is_correct', False))
            user_accuracy = correct_count / len(history) if history else 0
            total_accuracy += user_accuracy
            
            # セッション数
            progress_summary['total_sessions'] += len(history)
            
            # 部門別人気度
            for entry in history:
                dept = entry.get('department')
                if dept:
                    progress_summary['department_popularity'][dept] += 1
            
            # 学習パターン分析
            learning_mode = self._analyze_user_learning_pattern(history)
            progress_summary['learning_patterns'][learning_mode] += 1
        
        if valid_users > 0:
            progress_summary['average_accuracy'] = total_accuracy / valid_users
        
        # 辞書をリストに変換（JSON化のため）
        progress_summary['department_popularity'] = dict(progress_summary['department_popularity'])
        progress_summary['learning_patterns'] = dict(progress_summary['learning_patterns'])
        
        return progress_summary
    
    def get_detailed_user_analysis(self, user_id: str = None) -> Dict[str, Any]:
        """詳細ユーザー分析"""
        if user_id:
            return self._analyze_single_user(user_id)
        else:
            return self._analyze_all_users_detailed()
    
    def get_content_analytics(self) -> Dict[str, Any]:
        """コンテンツ分析"""
        user_data = self._load_all_user_data()
        
        # 問題別統計
        question_stats = defaultdict(lambda: {
            'attempted': 0, 'correct': 0, 'avg_time': 0, 'times': []
        })
        
        for user_id, data in user_data.items():
            for entry in data.get('history', []):
                q_id = entry.get('id')
                if q_id:
                    stats = question_stats[q_id]
                    stats['attempted'] += 1
                    if entry.get('is_correct', False):
                        stats['correct'] += 1
                    
                    elapsed = entry.get('elapsed', 0)
                    if elapsed > 0:
                        stats['times'].append(elapsed)
        
        # 統計計算
        for q_id, stats in question_stats.items():
            if stats['times']:
                stats['avg_time'] = sum(stats['times']) / len(stats['times'])
            stats['accuracy'] = stats['correct'] / stats['attempted'] if stats['attempted'] > 0 else 0
            del stats['times']  # 大きなデータを削除
        
        # 上位/下位問題の特定
        sorted_by_difficulty = sorted(
            [(q_id, stats) for q_id, stats in question_stats.items() if stats['attempted'] >= 10],
            key=lambda x: x[1]['accuracy']
        )
        
        hardest_questions = sorted_by_difficulty[:10]
        easiest_questions = sorted_by_difficulty[-10:]
        
        # カテゴリ別分析
        category_performance = self._analyze_category_performance(user_data)
        
        return {
            'question_statistics': dict(question_stats),
            'hardest_questions': [{'id': q_id, 'stats': stats} for q_id, stats in hardest_questions],
            'easiest_questions': [{'id': q_id, 'stats': stats} for q_id, stats in easiest_questions],
            'category_performance': category_performance,
            'content_gaps': self._identify_content_gaps(question_stats),
            'recommendations': self._generate_content_recommendations(question_stats)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス指標"""
        return {
            'system_performance': self._get_performance_metrics(),
            'data_quality_score': self._calculate_data_quality_score(),
            'user_engagement_score': self._calculate_engagement_score(),
            'learning_effectiveness': self._calculate_learning_effectiveness(),
            'technical_metrics': self._get_technical_metrics()
        }
    
    def generate_reports(self, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """レポート生成"""
        if report_type == 'comprehensive':
            return {
                'overview': self.get_system_overview(),
                'questions': self.get_question_management_data(),
                'users': self.get_user_progress_overview(),
                'content': self.get_content_analytics(),
                'performance': self.get_performance_metrics()
            }
        elif report_type == 'users':
            return self.get_user_progress_overview()
        elif report_type == 'content':
            return self.get_content_analytics()
        elif report_type == 'performance':
            return self.get_performance_metrics()
        else:
            return {'error': 'Unknown report type'}
    
    # === プライベートメソッド ===
    
    def _analyze_all_users(self) -> Dict[str, Any]:
        """全ユーザー分析"""
        user_data = self._load_all_user_data()
        
        return {
            'total_count': len(user_data),
            'active_count': sum(1 for data in user_data.values() if data.get('history')),
            'completion_rate': self._calculate_overall_completion_rate(user_data),
            'engagement_metrics': self._calculate_engagement_metrics(user_data)
        }
    
    def _analyze_question_data(self) -> Dict[str, Any]:
        """問題データ分析"""
        return {
            'total_questions': len(self.questions),
            'department_distribution': self._count_by_department(),
            'category_distribution': self._count_by_category(),
            'year_distribution': self._count_by_year(),
            'data_quality_issues': self._identify_data_issues()
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス指標取得"""
        return {
            'average_load_time': self._measure_load_time(),
            'cache_hit_rate': self._get_cache_metrics(),
            'error_rate': self._calculate_error_rate(),
            'response_time': self._measure_response_time()
        }
    
    def _get_system_alerts(self) -> List[Dict[str, str]]:
        """システムアラート"""
        alerts = []
        
        # データ品質チェック
        data_issues = self._identify_data_issues()
        if data_issues['critical_issues'] > 0:
            alerts.append({
                'type': 'critical',
                'message': f'重要なデータ品質問題が{data_issues["critical_issues"]}件あります',
                'category': 'data_quality'
            })
        
        # ユーザーアクティビティチェック
        user_data = self._load_all_user_data()
        inactive_users = self._count_inactive_users(user_data)
        if inactive_users > len(user_data) * 0.7:  # 70%以上が非アクティブ
            alerts.append({
                'type': 'warning',
                'message': f'非アクティブユーザーが{inactive_users}人います',
                'category': 'user_engagement'
            })
        
        return alerts
    
    def _count_by_department(self) -> Dict[str, int]:
        """部門別集計"""
        counts = defaultdict(int)
        for q in self.questions:
            dept = q.get('department', 'unknown')
            counts[dept] += 1
        return dict(counts)
    
    def _count_by_category(self) -> Dict[str, int]:
        """カテゴリ別集計"""
        counts = defaultdict(int)
        for q in self.questions:
            category = q.get('category', 'unknown')
            counts[category] += 1
        return dict(counts)
    
    def _count_by_year(self) -> Dict[str, int]:
        """年度別集計"""
        counts = defaultdict(int)
        for q in self.questions:
            year = q.get('year', 'unknown')
            counts[str(year)] += 1
        return dict(counts)
    
    def _count_by_type(self) -> Dict[str, int]:
        """問題種別集計"""
        counts = defaultdict(int)
        for q in self.questions:
            q_type = q.get('question_type', 'unknown')
            counts[q_type] += 1
        return dict(counts)
    
    def _analyze_difficulty_distribution(self) -> Dict[str, Any]:
        """難易度分布分析"""
        user_data = self._load_all_user_data()
        question_difficulties = {}
        
        # 各問題の実際の難易度を統計から計算
        for q in self.questions:
            q_id = q.get('id')
            if q_id:
                stats = self._get_question_stats(q_id, user_data)
                if stats['total_attempts'] >= 5:  # 最低5回以上の挑戦
                    question_difficulties[q_id] = {
                        'accuracy': stats['accuracy'],
                        'avg_time': stats['avg_time'],
                        'difficulty_level': self._categorize_difficulty(stats['accuracy'])
                    }
        
        # 難易度レベル別集計
        difficulty_counts = defaultdict(int)
        for stats in question_difficulties.values():
            difficulty_counts[stats['difficulty_level']] += 1
        
        return {
            'question_difficulties': question_difficulties,
            'distribution': dict(difficulty_counts),
            'average_accuracy': sum(s['accuracy'] for s in question_difficulties.values()) / len(question_difficulties) if question_difficulties else 0
        }
    
    def _analyze_question_quality(self) -> Dict[str, Any]:
        """問題品質分析"""
        quality_issues = []
        
        for q in self.questions:
            # 必須フィールドチェック
            if not q.get('question'):
                quality_issues.append(f"問題ID {q.get('id', 'unknown')}: 問題文が空")
            
            # 選択肢チェック
            options = [q.get(f'option_{c}') for c in ['a', 'b', 'c', 'd']]
            if any(not opt for opt in options):
                quality_issues.append(f"問題ID {q.get('id', 'unknown')}: 選択肢が不完全")
            
            # 正答チェック
            correct = q.get('correct_answer')
            if correct not in ['a', 'b', 'c', 'd']:
                quality_issues.append(f"問題ID {q.get('id', 'unknown')}: 正答設定が無効")
        
        return {
            'total_issues': len(quality_issues),
            'issues': quality_issues[:20],  # 最大20件表示
            'quality_score': 1 - (len(quality_issues) / len(self.questions)) if self.questions else 0
        }
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """データ整合性チェック"""
        integrity_report = {
            'total_questions': len(self.questions),
            'unique_ids': len(set(q.get('id') for q in self.questions if q.get('id'))),
            'missing_ids': sum(1 for q in self.questions if not q.get('id')),
            'duplicate_ids': [],
            'encoding_issues': 0,
            'structure_issues': 0
        }
        
        # 重複IDチェック
        id_counts = Counter(q.get('id') for q in self.questions if q.get('id'))
        duplicates = [qid for qid, count in id_counts.items() if count > 1]
        integrity_report['duplicate_ids'] = duplicates
        
        return integrity_report
    
    def _load_all_user_data(self) -> Dict[str, Dict]:
        """全ユーザーデータ読み込み"""
        user_data = {}
        
        if not os.path.exists(self.user_data_dir):
            return user_data
        
        try:
            if not os.path.exists(self.user_data_dir):
                logger.warning(f"ユーザーデータディレクトリが存在しません: {self.user_data_dir}")
                return user_data
            
            for filename in os.listdir(self.user_data_dir):
                if filename.endswith('.json'):
                    user_id = filename[:-5]  # .json除去
                    file_path = os.path.join(self.user_data_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            user_data[user_id] = json.load(f)
                    except (FileNotFoundError, PermissionError, json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.warning(f"ユーザーデータ読み込みエラー {filename}: {e}")
                    except Exception as e:
                        logger.error(f"予期しないエラー {filename}: {e}")
        except (OSError, PermissionError) as e:
            logger.error(f"ディレクトリアクセスエラー {self.user_data_dir}: {e}")
        
        return user_data
    
    def _get_last_activity(self, history: List[Dict]) -> Optional[datetime]:
        """最終アクティビティ日時取得"""
        if not history:
            return None
        
        try:
            # 有効な日付を持つエントリのみをフィルタ
            valid_entries = [entry for entry in history if entry.get('date')]
            if not valid_entries:
                return None
            
            last_entry = max(valid_entries, key=lambda x: x.get('date', ''))
            date_str = last_entry.get('date', '')
            if not date_str:
                return None
            
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"日付パースエラー: {e}")
            return None
        except:
            return None
    
    def _analyze_user_learning_pattern(self, history: List[Dict]) -> str:
        """ユーザー学習パターン分析"""
        if len(history) < 5:
            return 'beginner'
        
        # 最近の正答率
        recent_accuracy = sum(1 for h in history[-10:] if h.get('is_correct', False)) / min(10, len(history))
        
        # 学習頻度
        dates = [h.get('date') for h in history if h.get('date')]
        if len(dates) >= 2:
            try:
                first_date = datetime.fromisoformat(dates[0])
                last_date = datetime.fromisoformat(dates[-1])
                study_period = (last_date - first_date).days
                frequency = len(history) / max(study_period, 1)
            except:
                frequency = 0
        else:
            frequency = 0
        
        if recent_accuracy >= 0.8 and frequency >= 1:
            return 'advanced'
        elif recent_accuracy >= 0.6 and frequency >= 0.5:
            return 'intermediate'
        elif frequency >= 1:
            return 'intensive'
        else:
            return 'casual'
    
    def _analyze_single_user(self, user_id: str) -> Dict[str, Any]:
        """単一ユーザー詳細分析"""
        filepath = os.path.join(self.user_data_dir, f"{user_id}.json")
        
        if not os.path.exists(filepath):
            return {'error': 'User not found'}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
        except (FileNotFoundError, PermissionError) as e:
            return {'error': f'ファイルアクセスエラー: {e}'}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return {'error': f'データ読み込みエラー: {e}'}
        except Exception as e:
            return {'error': f'予期しないエラー: {e}'}
        
        history = user_data.get('history', [])
        
        return {
            'user_id': user_id,
            'total_questions': len(history),
            'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0,
            'study_pattern': self._analyze_user_learning_pattern(history),
            'department_focus': self._analyze_department_focus(history),
            'learning_progress': self._analyze_learning_progress(history),
            'weak_areas': self._identify_user_weak_areas(history),
            'achievements': self._calculate_user_achievements(history)
        }
    
    def _analyze_all_users_detailed(self) -> Dict[str, Any]:
        """全ユーザー詳細分析"""
        user_data = self._load_all_user_data()
        
        detailed_stats = {
            'user_segments': defaultdict(int),
            'accuracy_distribution': [],
            'engagement_levels': defaultdict(int),
            'department_preferences': defaultdict(int)
        }
        
        for user_id, data in user_data.items():
            history = data.get('history', [])
            if not history:
                continue
            
            # ユーザーセグメント
            pattern = self._analyze_user_learning_pattern(history)
            detailed_stats['user_segments'][pattern] += 1
            
            # 正答率分布
            accuracy = sum(1 for h in history if h.get('is_correct', False)) / len(history)
            detailed_stats['accuracy_distribution'].append(accuracy)
            
            # エンゲージメントレベル
            engagement = self._calculate_user_engagement(history)
            detailed_stats['engagement_levels'][engagement] += 1
            
            # 部門選好
            for entry in history:
                dept = entry.get('department')
                if dept:
                    detailed_stats['department_preferences'][dept] += 1
        
        # 辞書をdict型に変換
        for key in ['user_segments', 'engagement_levels', 'department_preferences']:
            detailed_stats[key] = dict(detailed_stats[key])
        
        return detailed_stats
    
    def _analyze_category_performance(self, user_data: Dict[str, Dict]) -> Dict[str, Any]:
        """カテゴリ別パフォーマンス分析"""
        category_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'times': []})
        
        for data in user_data.values():
            for entry in data.get('history', []):
                category = entry.get('category')
                if category:
                    stats = category_stats[category]
                    stats['total'] += 1
                    if entry.get('is_correct', False):
                        stats['correct'] += 1
                    
                    elapsed = entry.get('elapsed', 0)
                    if elapsed > 0:
                        stats['times'].append(elapsed)
        
        # 統計計算
        result = {}
        for category, stats in category_stats.items():
            result[category] = {
                'total_attempts': stats['total'],
                'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                'avg_time': sum(stats['times']) / len(stats['times']) if stats['times'] else 0,
                'difficulty_level': self._categorize_difficulty(stats['correct'] / stats['total'] if stats['total'] > 0 else 0)
            }
        
        return result
    
    def _identify_content_gaps(self, question_stats: Dict) -> List[Dict[str, Any]]:
        """コンテンツギャップ特定"""
        gaps = []
        
        # 使用頻度の低い問題
        unused_questions = [q_id for q_id, stats in question_stats.items() if stats['attempted'] < 3]
        if unused_questions:
            gaps.append({
                'type': 'underutilized_content',
                'count': len(unused_questions),
                'description': f'{len(unused_questions)}問の使用頻度が低い'
            })
        
        # 難易度の偏り
        accuracies = [stats['accuracy'] for stats in question_stats.values() if stats['attempted'] >= 5]
        if accuracies:
            avg_accuracy = sum(accuracies) / len(accuracies)
            if avg_accuracy > 0.85:
                gaps.append({
                    'type': 'too_easy',
                    'description': '全体的に問題が簡単すぎる可能性'
                })
            elif avg_accuracy < 0.4:
                gaps.append({
                    'type': 'too_difficult',
                    'description': '全体的に問題が難しすぎる可能性'
                })
        
        return gaps
    
    def _generate_content_recommendations(self, question_stats: Dict) -> List[str]:
        """コンテンツ推奨生成"""
        recommendations = []
        
        # 難易度分布の分析
        easy_count = sum(1 for stats in question_stats.values() if stats['accuracy'] > 0.8 and stats['attempted'] >= 5)
        hard_count = sum(1 for stats in question_stats.values() if stats['accuracy'] < 0.4 and stats['attempted'] >= 5)
        
        if hard_count > easy_count * 2:
            recommendations.append("難しい問題が多すぎます。基礎レベルの問題を追加することを検討してください。")
        
        if easy_count > hard_count * 3:
            recommendations.append("易しい問題が多すぎます。上級レベルの問題を追加することを検討してください。")
        
        # 使用されていない問題の確認
        unused_count = sum(1 for stats in question_stats.values() if stats['attempted'] == 0)
        if unused_count > 0:
            recommendations.append(f"{unused_count}問が一度も使用されていません。問題の可視性を改善してください。")
        
        return recommendations
    
    def _calculate_data_quality_score(self) -> float:
        """データ品質スコア計算"""
        quality_metrics = self._analyze_question_quality()
        integrity_metrics = self._check_data_integrity()
        
        # 品質スコア（0-1）
        quality_score = quality_metrics.get('quality_score', 0)
        
        # 整合性スコア
        total_questions = integrity_metrics['total_questions']
        integrity_issues = (
            integrity_metrics['missing_ids'] + 
            len(integrity_metrics['duplicate_ids']) +
            integrity_metrics['encoding_issues'] +
            integrity_metrics['structure_issues']
        )
        integrity_score = 1 - (integrity_issues / total_questions) if total_questions > 0 else 0
        
        return (quality_score + integrity_score) / 2
    
    def _calculate_engagement_score(self) -> float:
        """エンゲージメントスコア計算"""
        user_data = self._load_all_user_data()
        if not user_data:
            return 0
        
        active_users = sum(1 for data in user_data.values() if data.get('history'))
        engagement_score = active_users / len(user_data)
        
        return engagement_score
    
    def _calculate_learning_effectiveness(self) -> Dict[str, float]:
        """学習効果計算"""
        user_data = self._load_all_user_data()
        
        improvement_scores = []
        retention_scores = []
        
        for data in user_data.values():
            history = data.get('history', [])
            if len(history) >= 10:
                # 改善度: 最初の5問と最後の5問の正答率比較
                early_accuracy = sum(1 for h in history[:5] if h.get('is_correct', False)) / 5
                recent_accuracy = sum(1 for h in history[-5:] if h.get('is_correct', False)) / 5
                improvement = recent_accuracy - early_accuracy
                improvement_scores.append(improvement)
                
                # 定着度: 一定期間後の正答率維持
                if len(history) >= 20:
                    mid_accuracy = sum(1 for h in history[10:15] if h.get('is_correct', False)) / 5
                    retention = recent_accuracy - mid_accuracy
                    retention_scores.append(retention)
        
        return {
            'average_improvement': sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0,
            'knowledge_retention': sum(retention_scores) / len(retention_scores) if retention_scores else 0
        }
    
    def _get_technical_metrics(self) -> Dict[str, Any]:
        """技術指標取得"""
        return {
            'data_load_time': self._measure_load_time(),
            'memory_usage': self._estimate_memory_usage(),
            'file_sizes': self._get_file_sizes(),
            'error_logs': self._get_recent_errors()
        }
    
    # === ヘルパーメソッド ===
    
    def _categorize_difficulty(self, accuracy: float) -> str:
        """難易度カテゴリ化"""
        if accuracy >= 0.8:
            return 'easy'
        elif accuracy >= 0.6:
            return 'medium'
        elif accuracy >= 0.4:
            return 'hard'
        else:
            return 'very_hard'
    
    def _get_question_stats(self, question_id: int, user_data: Dict) -> Dict[str, Any]:
        """問題統計取得"""
        attempts = 0
        correct = 0
        times = []
        
        for data in user_data.values():
            for entry in data.get('history', []):
                if entry.get('id') == question_id:
                    attempts += 1
                    if entry.get('is_correct', False):
                        correct += 1
                    
                    elapsed = entry.get('elapsed', 0)
                    if elapsed > 0:
                        times.append(elapsed)
        
        return {
            'total_attempts': attempts,
            'correct_attempts': correct,
            'accuracy': correct / attempts if attempts > 0 else 0,
            'avg_time': sum(times) / len(times) if times else 0
        }
    
    def _calculate_overall_completion_rate(self, user_data: Dict) -> float:
        """全体完了率計算"""
        if not user_data:
            return 0
        
        total_possible = len(self.questions) * len(user_data)
        total_attempted = sum(len(data.get('history', [])) for data in user_data.values())
        
        return total_attempted / total_possible if total_possible > 0 else 0
    
    def _calculate_engagement_metrics(self, user_data: Dict) -> Dict[str, float]:
        """エンゲージメント指標計算"""
        if not user_data:
            return {'active_ratio': 0, 'avg_sessions': 0, 'retention_rate': 0}
        
        active_users = sum(1 for data in user_data.values() if data.get('history'))
        total_sessions = sum(len(data.get('history', [])) for data in user_data.values())
        
        return {
            'active_ratio': active_users / len(user_data),
            'avg_sessions': total_sessions / len(user_data),
            'retention_rate': self._calculate_retention_rate(user_data)
        }
    
    def _calculate_retention_rate(self, user_data: Dict) -> float:
        """リテンション率計算"""
        # 簡単な実装: 30日以内にアクティビティがあるユーザーの割合
        cutoff = datetime.now() - timedelta(days=30)
        retained_users = 0
        
        for data in user_data.values():
            last_activity = self._get_last_activity(data.get('history', []))
            if last_activity and last_activity >= cutoff:
                retained_users += 1
        
        return retained_users / len(user_data) if user_data else 0
    
    def _identify_data_issues(self) -> Dict[str, int]:
        """データ問題特定"""
        return {
            'critical_issues': 0,  # 実装必要
            'warnings': 0,
            'info': 0
        }
    
    def _count_inactive_users(self, user_data: Dict) -> int:
        """非アクティブユーザー数"""
        cutoff = datetime.now() - timedelta(days=30)
        inactive = 0
        
        for data in user_data.values():
            last_activity = self._get_last_activity(data.get('history', []))
            if not last_activity or last_activity < cutoff:
                inactive += 1
        
        return inactive
    
    def _measure_load_time(self) -> float:
        """読み込み時間測定"""
        import time
        start = time.time()
        # ダミー処理
        _ = len(self.questions)
        return time.time() - start
    
    def _get_cache_metrics(self) -> Dict[str, float]:
        """キャッシュ指標"""
        return {'hit_rate': 0.75, 'miss_rate': 0.25}  # ダミー値
    
    def _calculate_error_rate(self) -> float:
        """エラー率計算"""
        return 0.01  # ダミー値
    
    def _measure_response_time(self) -> float:
        """応答時間測定"""
        return 0.1  # ダミー値
    
    def _estimate_memory_usage(self) -> Dict[str, str]:
        """メモリ使用量推定"""
        import sys
        return {
            'questions_data': f"{sys.getsizeof(self.questions) / 1024:.1f} KB",
            'total_estimated': "< 50 MB"
        }
    
    def _get_file_sizes(self) -> Dict[str, str]:
        """ファイルサイズ取得"""
        sizes = {}
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(self.data_dir, filename)
                    size = os.path.getsize(filepath)
                    sizes[filename] = f"{size / 1024:.1f} KB"
        except:
            pass
        return sizes
    
    def _get_recent_errors(self) -> List[str]:
        """最近のエラー取得"""
        return []  # ログファイル解析実装必要
    
    def _analyze_department_focus(self, history: List[Dict]) -> Dict[str, int]:
        """部門集中度分析"""
        dept_counts = defaultdict(int)
        for entry in history:
            dept = entry.get('department')
            if dept:
                dept_counts[dept] += 1
        return dict(dept_counts)
    
    def _analyze_learning_progress(self, history: List[Dict]) -> Dict[str, Any]:
        """学習進捗分析"""
        if len(history) < 10:
            return {'status': 'insufficient_data'}
        
        # 10問ずつのグループに分けて正答率の推移を見る
        group_size = 10
        accuracies = []
        
        for i in range(0, len(history), group_size):
            group = history[i:i+group_size]
            correct = sum(1 for entry in group if entry.get('is_correct', False))
            accuracy = correct / len(group)
            accuracies.append(accuracy)
        
        # トレンド計算
        if len(accuracies) >= 2:
            trend = accuracies[-1] - accuracies[0]
            if trend > 0.1:
                progress_status = 'improving'
            elif trend < -0.1:
                progress_status = 'declining'
            else:
                progress_status = 'stable'
        else:
            progress_status = 'unknown'
        
        return {
            'status': progress_status,
            'accuracy_progression': accuracies,
            'overall_trend': trend if len(accuracies) >= 2 else 0
        }
    
    def _identify_user_weak_areas(self, history: List[Dict]) -> List[str]:
        """ユーザー弱点特定"""
        category_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        
        for entry in history:
            category = entry.get('category')
            if category:
                stats = category_stats[category]
                stats['total'] += 1
                if entry.get('is_correct', False):
                    stats['correct'] += 1
        
        # 正答率の低いカテゴリを特定
        weak_areas = []
        for category, stats in category_stats.items():
            if stats['total'] >= 3:  # 最低3問以上
                accuracy = stats['correct'] / stats['total']
                if accuracy < 0.6:
                    weak_areas.append(category)
        
        return weak_areas
    
    def _calculate_user_achievements(self, history: List[Dict]) -> List[str]:
        """ユーザー達成項目計算"""
        achievements = []
        
        if len(history) >= 100:
            achievements.append('問題100問達成')
        
        if len(history) >= 50:
            recent_accuracy = sum(1 for entry in history[-50:] if entry.get('is_correct', False)) / 50
            if recent_accuracy >= 0.8:
                achievements.append('直近50問で80%以上の正答率')
        
        # 連続正解記録
        max_streak = 0
        current_streak = 0
        for entry in history:
            if entry.get('is_correct', False):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        if max_streak >= 10:
            achievements.append(f'最大連続正解{max_streak}問')
        
        return achievements
    
    def _calculate_user_engagement(self, history: List[Dict]) -> str:
        """ユーザーエンゲージメント計算"""
        if len(history) < 10:
            return 'low'
        elif len(history) < 50:
            return 'medium'
        else:
            return 'high'

# グローバルインスタンス
admin_dashboard = AdminDashboard()