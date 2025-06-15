"""
RCCM学習アプリ - 高度な個人化機能
ML推薦、適応UI、カスタム学習プラン、個人化されたUX
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import math
import random

logger = logging.getLogger(__name__)

class AdvancedPersonalizationEngine:
    """高度な個人化エンジン"""
    
    def __init__(self, user_data_dir: str = 'user_data', personalization_data_dir: str = 'personalization_data'):
        self.user_data_dir = user_data_dir
        self.personalization_data_dir = personalization_data_dir
        self.user_profiles_file = os.path.join(personalization_data_dir, 'user_profiles.json')
        self.ml_models_file = os.path.join(personalization_data_dir, 'ml_models.json')
        self.ui_preferences_file = os.path.join(personalization_data_dir, 'ui_preferences.json')
        
        # ディレクトリ作成
        os.makedirs(personalization_data_dir, exist_ok=True)
        
        # 学習スタイル定義
        self.learning_styles = {
            'visual': {
                'name': '視覚的学習者',
                'description': '図表や画像で理解しやすい',
                'preferences': ['diagrams', 'charts', 'color_coding', 'mind_maps']
            },
            'auditory': {
                'name': '聴覚的学習者', 
                'description': '音声や説明で理解しやすい',
                'preferences': ['audio_explanations', 'discussion', 'verbal_repetition']
            },
            'kinesthetic': {
                'name': '体験的学習者',
                'description': '実践や操作で理解しやすい',
                'preferences': ['hands_on', 'practice_problems', 'real_examples']
            },
            'reading': {
                'name': '読み書き学習者',
                'description': 'テキストや文章で理解しやすい',
                'preferences': ['detailed_text', 'note_taking', 'written_explanations']
            }
        }
        
        logger.info("高度な個人化エンジン初期化完了")
    
    # === ユーザープロファイル分析 ===
    
    def analyze_user_profile(self, user_id: str) -> Dict[str, Any]:
        """包括的ユーザープロファイル分析"""
        try:
            user_data = self._load_user_data(user_id)
            if not user_data:
                return self._create_default_profile(user_id)
            
            history = user_data.get('history', [])
            
            # 学習パターン分析
            learning_patterns = self._analyze_learning_patterns(history)
            
            # 学習スタイル推定
            learning_style = self._estimate_learning_style(history, user_data)
            
            # 認知負荷分析
            cognitive_load = self._analyze_cognitive_load(history)
            
            # 時間管理パターン
            time_patterns = self._analyze_time_patterns(history)
            
            # 動機づけプロファイル
            motivation_profile = self._analyze_motivation_profile(history, user_data)
            
            # 学習効果性分析
            learning_effectiveness = self._analyze_learning_effectiveness(history)
            
            # 個人化推奨生成
            personalization_recommendations = self._generate_personalization_recommendations(
                learning_patterns, learning_style, cognitive_load, time_patterns, motivation_profile
            )
            
            profile = {
                'user_id': user_id,
                'updated_at': datetime.now().isoformat(),
                'learning_patterns': learning_patterns,
                'learning_style': learning_style,
                'cognitive_load': cognitive_load,
                'time_patterns': time_patterns,
                'motivation_profile': motivation_profile,
                'learning_effectiveness': learning_effectiveness,
                'personalization_recommendations': personalization_recommendations,
                'confidence_score': self._calculate_profile_confidence(history)
            }
            
            # プロファイル保存
            self._save_user_profile(user_id, profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"ユーザープロファイル分析エラー: {e}")
            return self._create_default_profile(user_id)
    
    def get_ml_recommendations(self, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """機械学習ベースの推薦"""
        try:
            user_profile = self.analyze_user_profile(user_id)
            user_data = self._load_user_data(user_id)
            
            # コンテンツ推薦
            content_recommendations = self._generate_content_recommendations(user_profile, user_data, context)
            
            # 学習経路推薦
            learning_path = self._generate_learning_path(user_profile, user_data)
            
            # 難易度調整推薦
            difficulty_adjustments = self._recommend_difficulty_adjustments(user_profile, user_data)
            
            # タイミング推薦
            timing_recommendations = self._recommend_optimal_timing(user_profile)
            
            # 学習方法推薦
            method_recommendations = self._recommend_learning_methods(user_profile)
            
            return {
                'content_recommendations': content_recommendations,
                'learning_path': learning_path,
                'difficulty_adjustments': difficulty_adjustments,
                'timing_recommendations': timing_recommendations,
                'method_recommendations': method_recommendations,
                'confidence': user_profile['confidence_score']
            }
            
        except Exception as e:
            logger.error(f"ML推薦エラー: {e}")
            return {'error': str(e)}
    
    def customize_ui(self, user_id: str) -> Dict[str, Any]:
        """UI個人化設定"""
        try:
            user_profile = self.analyze_user_profile(user_id)
            ui_preferences = self._load_ui_preferences(user_id)
            
            # 学習スタイルに基づくUI調整
            ui_customizations = self._generate_ui_customizations(user_profile, ui_preferences)
            
            # レイアウト最適化
            layout_optimizations = self._optimize_layout(user_profile)
            
            # 色彩・フォント調整
            visual_customizations = self._customize_visual_elements(user_profile)
            
            # インタラクション調整
            interaction_customizations = self._customize_interactions(user_profile)
            
            # 情報密度調整
            information_density = self._adjust_information_density(user_profile)
            
            customizations = {
                'ui_customizations': ui_customizations,
                'layout_optimizations': layout_optimizations,
                'visual_customizations': visual_customizations,
                'interaction_customizations': interaction_customizations,
                'information_density': information_density,
                'responsive_adjustments': self._get_responsive_adjustments(user_profile)
            }
            
            # UI設定を保存
            self._save_ui_preferences(user_id, customizations)
            
            return customizations
            
        except Exception as e:
            logger.error(f"UI個人化エラー: {e}")
            return {}
    
    def create_custom_learning_plan(self, user_id: str, goals: Dict[str, Any] = None) -> Dict[str, Any]:
        """カスタム学習プラン生成"""
        try:
            user_profile = self.analyze_user_profile(user_id)
            user_data = self._load_user_data(user_id)
            
            # 目標設定
            if not goals:
                goals = self._infer_learning_goals(user_profile, user_data)
            
            # 学習段階分析
            current_stage = self._analyze_learning_stage(user_profile, user_data)
            
            # 個人化学習経路
            learning_path = self._create_personalized_path(user_profile, goals, current_stage)
            
            # スケジュール最適化
            schedule = self._optimize_learning_schedule(user_profile, goals)
            
            # 進捗マイルストーン
            milestones = self._create_progress_milestones(goals, learning_path)
            
            # 適応的調整機能
            adaptive_features = self._setup_adaptive_features(user_profile)
            
            custom_plan = {
                'plan_id': f"custom_{user_id}_{datetime.now().strftime('%Y%m%d')}",
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'goals': goals,
                'current_stage': current_stage,
                'learning_path': learning_path,
                'schedule': schedule,
                'milestones': milestones,
                'adaptive_features': adaptive_features,
                'estimated_completion': self._estimate_completion_time(learning_path, user_profile),
                'success_probability': self._calculate_success_probability(user_profile, goals)
            }
            
            # プラン保存
            self._save_learning_plan(user_id, custom_plan)
            
            return custom_plan
            
        except Exception as e:
            logger.error(f"カスタム学習プラン生成エラー: {e}")
            return {'error': str(e)}
    
    def adaptive_ui_adjustment(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """リアルタイムUI適応調整"""
        try:
            # インタラクションデータから学習
            ui_insights = self._analyze_interaction_data(interaction_data)
            
            # 現在の設定取得
            current_ui = self._load_ui_preferences(user_id)
            
            # 適応的調整計算
            adjustments = self._calculate_adaptive_adjustments(ui_insights, current_ui)
            
            # 調整実行
            if adjustments['confidence'] > 0.7:  # 閾値
                updated_ui = self._apply_ui_adjustments(current_ui, adjustments)
                self._save_ui_preferences(user_id, updated_ui)
                
                return {
                    'adjusted': True,
                    'adjustments': adjustments,
                    'ui_settings': updated_ui
                }
            else:
                return {
                    'adjusted': False,
                    'reason': 'Insufficient confidence in adjustments'
                }
                
        except Exception as e:
            logger.error(f"適応UI調整エラー: {e}")
            return {'error': str(e)}
    
    def get_personalized_dashboard(self, user_id: str) -> Dict[str, Any]:
        """個人化ダッシュボード"""
        try:
            user_profile = self.analyze_user_profile(user_id)
            user_data = self._load_user_data(user_id)
            
            # 重要指標選択
            key_metrics = self._select_key_metrics(user_profile)
            
            # ウィジェット配置最適化
            widget_layout = self._optimize_widget_layout(user_profile)
            
            # 個人化された洞察
            personalized_insights = self._generate_personalized_insights(user_profile, user_data)
            
            # 推奨アクション
            recommended_actions = self._generate_recommended_actions(user_profile, user_data)
            
            # 進捗可視化設定
            progress_visualizations = self._configure_progress_visualizations(user_profile)
            
            return {
                'key_metrics': key_metrics,
                'widget_layout': widget_layout,
                'personalized_insights': personalized_insights,
                'recommended_actions': recommended_actions,
                'progress_visualizations': progress_visualizations,
                'refresh_intervals': self._get_optimal_refresh_intervals(user_profile)
            }
            
        except Exception as e:
            logger.error(f"個人化ダッシュボードエラー: {e}")
            return {}
    
    # === プライベートメソッド ===
    
    def _analyze_learning_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """学習パターン分析"""
        if not history:
            return {}
        
        # 学習時間パターン
        study_times = []
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get('date', ''))
                study_times.append(dt.hour)
            except:
                continue
        
        # 学習頻度パターン
        study_dates = set()
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get('date', ''))
                study_dates.add(dt.date())
            except:
                continue
        
        # 正答率推移
        accuracy_trend = []
        window_size = 10
        for i in range(0, len(history), window_size):
            window = history[i:i+window_size]
            correct = sum(1 for h in window if h.get('is_correct', False))
            accuracy_trend.append(correct / len(window))
        
        # セッション長パターン
        session_lengths = self._calculate_session_lengths(history)
        
        return {
            'preferred_study_hours': self._get_preferred_hours(study_times),
            'study_frequency': len(study_dates),
            'consistency_score': self._calculate_consistency(list(study_dates)),
            'accuracy_trend': accuracy_trend,
            'improvement_rate': self._calculate_improvement_rate(accuracy_trend),
            'session_length_preference': {
                'average': sum(session_lengths) / len(session_lengths) if session_lengths else 0,
                'preferred_range': self._get_preferred_session_range(session_lengths)
            },
            'learning_velocity': len(history) / max((max(study_dates) - min(study_dates)).days, 1) if study_dates else 0
        }
    
    def _estimate_learning_style(self, history: List[Dict], user_data: Dict) -> Dict[str, Any]:
        """学習スタイル推定"""
        style_scores = {style: 0.0 for style in self.learning_styles.keys()}
        
        # 回答時間から推定
        avg_time = sum(h.get('elapsed', 0) for h in history) / len(history) if history else 0
        
        if avg_time > 60:  # 長時間考える → 読み書き型
            style_scores['reading'] += 0.3
        elif avg_time < 30:  # 直感的 → 視覚型
            style_scores['visual'] += 0.3
        
        # エラーパターンから推定
        error_patterns = self._analyze_error_patterns(history)
        
        # 時間帯から推定
        study_hours = [datetime.fromisoformat(h.get('date', '')).hour for h in history if h.get('date')]
        if study_hours:
            avg_hour = sum(study_hours) / len(study_hours)
            if 9 <= avg_hour <= 12:  # 午前集中 → 読み書き型
                style_scores['reading'] += 0.2
            elif 14 <= avg_hour <= 17:  # 午後活動 → 体験型
                style_scores['kinesthetic'] += 0.2
        
        # 最も高いスコアのスタイルを選択
        primary_style = max(style_scores, key=style_scores.get)
        
        return {
            'primary_style': primary_style,
            'style_scores': style_scores,
            'confidence': max(style_scores.values()),
            'style_description': self.learning_styles[primary_style],
            'mixed_style': len([s for s in style_scores.values() if s > 0.3]) > 1
        }
    
    def _analyze_cognitive_load(self, history: List[Dict]) -> Dict[str, Any]:
        """認知負荷分析"""
        if not history:
            return {}
        
        # 難易度別パフォーマンス
        difficulty_performance = defaultdict(list)
        for entry in history:
            difficulty = entry.get('difficulty', 'standard')
            is_correct = entry.get('is_correct', False)
            elapsed = entry.get('elapsed', 0)
            
            difficulty_performance[difficulty].append({
                'correct': is_correct,
                'time': elapsed
            })
        
        # 負荷指標計算
        cognitive_load_indicators = {}
        for difficulty, performances in difficulty_performance.items():
            if performances:
                avg_time = sum(p['time'] for p in performances) / len(performances)
                accuracy = sum(1 for p in performances if p['correct']) / len(performances)
                
                # 認知負荷 = 時間×(1-正答率)
                cognitive_load = avg_time * (1 - accuracy)
                
                cognitive_load_indicators[difficulty] = {
                    'load_score': cognitive_load,
                    'accuracy': accuracy,
                    'avg_time': avg_time,
                    'sample_size': len(performances)
                }
        
        # 最適難易度推定
        optimal_difficulty = self._estimate_optimal_difficulty(cognitive_load_indicators)
        
        return {
            'cognitive_load_indicators': cognitive_load_indicators,
            'optimal_difficulty': optimal_difficulty,
            'load_tolerance': self._calculate_load_tolerance(history),
            'fatigue_patterns': self._analyze_fatigue_patterns(history)
        }
    
    def _analyze_time_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """時間管理パターン分析"""
        if not history:
            return {}
        
        # 学習時間帯分析
        hourly_performance = defaultdict(list)
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get('date', ''))
                hour = dt.hour
                accuracy = 1 if entry.get('is_correct', False) else 0
                hourly_performance[hour].append(accuracy)
            except:
                continue
        
        # 最適時間帯特定
        best_hours = []
        for hour, accuracies in hourly_performance.items():
            if len(accuracies) >= 3:  # 最小サンプル数
                avg_accuracy = sum(accuracies) / len(accuracies)
                if avg_accuracy > 0.7:
                    best_hours.append(hour)
        
        # 学習継続時間分析
        session_durations = self._calculate_session_lengths(history)
        
        return {
            'optimal_hours': sorted(best_hours),
            'hourly_performance': dict(hourly_performance),
            'peak_performance_time': self._find_peak_performance_time(hourly_performance),
            'session_duration_preference': {
                'optimal_duration': self._find_optimal_session_duration(session_durations),
                'fatigue_threshold': self._estimate_fatigue_threshold(history)
            },
            'weekly_patterns': self._analyze_weekly_patterns(history)
        }
    
    def _analyze_motivation_profile(self, history: List[Dict], user_data: Dict) -> Dict[str, Any]:
        """動機づけプロファイル分析"""
        # 継続性分析
        study_dates = []
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get('date', ''))
                study_dates.append(dt.date())
            except:
                continue
        
        study_dates = sorted(set(study_dates))
        
        # ストリーク計算
        max_streak = self._calculate_max_streak(study_dates)
        current_streak = self._calculate_current_streak(study_dates)
        
        # チャレンジ志向分析
        challenge_seeking = self._analyze_challenge_seeking(history)
        
        # 進捗感応性
        progress_sensitivity = self._analyze_progress_sensitivity(history)
        
        # 報酬反応性
        reward_responsiveness = self._analyze_reward_responsiveness(user_data)
        
        return {
            'persistence_level': self._calculate_persistence_level(history),
            'max_study_streak': max_streak,
            'current_streak': current_streak,
            'challenge_seeking': challenge_seeking,
            'progress_sensitivity': progress_sensitivity,
            'reward_responsiveness': reward_responsiveness,
            'motivation_type': self._classify_motivation_type(challenge_seeking, progress_sensitivity, reward_responsiveness)
        }
    
    def _analyze_learning_effectiveness(self, history: List[Dict]) -> Dict[str, Any]:
        """学習効果性分析"""
        if len(history) < 20:
            return {'insufficient_data': True}
        
        # 学習曲線分析
        learning_curve = self._calculate_learning_curve(history)
        
        # 記憶定着率
        retention_rate = self._calculate_retention_rate(history)
        
        # 転移学習効果
        transfer_effect = self._analyze_transfer_learning(history)
        
        # 学習効率
        learning_efficiency = self._calculate_learning_efficiency(history)
        
        return {
            'learning_curve': learning_curve,
            'retention_rate': retention_rate,
            'transfer_effect': transfer_effect,
            'learning_efficiency': learning_efficiency,
            'plateau_detection': self._detect_learning_plateau(learning_curve)
        }
    
    def _generate_personalization_recommendations(self, learning_patterns: Dict, learning_style: Dict, 
                                                cognitive_load: Dict, time_patterns: Dict, 
                                                motivation_profile: Dict) -> List[Dict[str, Any]]:
        """個人化推奨生成"""
        recommendations = []
        
        # 学習時間最適化
        if time_patterns.get('optimal_hours'):
            recommendations.append({
                'type': 'timing',
                'priority': 'high',
                'title': '最適学習時間の活用',
                'description': f"{time_patterns['optimal_hours']}時台の学習効果が高いです",
                'action': 'schedule_optimization'
            })
        
        # 学習スタイル適応
        primary_style = learning_style.get('primary_style')
        if primary_style:
            style_info = self.learning_styles[primary_style]
            recommendations.append({
                'type': 'learning_style',
                'priority': 'high',
                'title': f'{style_info["name"]}向け学習法',
                'description': style_info['description'],
                'action': 'style_adaptation',
                'preferences': style_info['preferences']
            })
        
        # 認知負荷調整
        if cognitive_load.get('optimal_difficulty'):
            recommendations.append({
                'type': 'difficulty',
                'priority': 'medium',
                'title': '難易度調整',
                'description': f"現在の最適難易度: {cognitive_load['optimal_difficulty']}",
                'action': 'difficulty_adjustment'
            })
        
        # 動機づけ強化
        motivation_type = motivation_profile.get('motivation_type')
        if motivation_type:
            recommendations.append({
                'type': 'motivation',
                'priority': 'medium',
                'title': '動機づけ最適化',
                'description': f"{motivation_type}タイプに適した報酬システム",
                'action': 'motivation_enhancement'
            })
        
        return recommendations
    
    def _generate_content_recommendations(self, user_profile: Dict, user_data: Dict, 
                                        context: Dict = None) -> List[Dict[str, Any]]:
        """コンテンツ推薦生成"""
        recommendations = []
        
        history = user_data.get('history', [])
        if not history:
            return self._get_default_content_recommendations()
        
        # 弱点分野特定
        weak_areas = self._identify_weak_content_areas(history)
        
        # 学習スタイルに基づく推薦
        learning_style = user_profile.get('learning_style', {})
        
        for area in weak_areas:
            recommendations.append({
                'type': 'weakness_focused',
                'content_area': area['category'],
                'priority': area['priority'],
                'recommended_approach': self._get_style_specific_approach(learning_style, area),
                'estimated_benefit': area['improvement_potential']
            })
        
        # 進捗に基づく推薦
        next_level_content = self._recommend_next_level_content(history, user_profile)
        recommendations.extend(next_level_content)
        
        return recommendations[:10]  # 上位10件
    
    def _generate_learning_path(self, user_profile: Dict, user_data: Dict) -> Dict[str, Any]:
        """学習経路生成"""
        history = user_data.get('history', [])
        
        # 現在のレベル評価
        current_level = self._assess_current_level(history)
        
        # 目標設定
        target_level = self._infer_target_level(user_profile, user_data)
        
        # 経路ステップ生成
        path_steps = self._generate_path_steps(current_level, target_level, user_profile)
        
        return {
            'current_level': current_level,
            'target_level': target_level,
            'steps': path_steps,
            'estimated_duration': self._estimate_path_duration(path_steps, user_profile),
            'checkpoints': self._create_learning_checkpoints(path_steps)
        }
    
    def _generate_ui_customizations(self, user_profile: Dict, ui_preferences: Dict) -> Dict[str, Any]:
        """UI カスタマイゼーション生成"""
        learning_style = user_profile.get('learning_style', {})
        cognitive_load = user_profile.get('cognitive_load', {})
        
        customizations = {}
        
        # 学習スタイルに基づく調整
        primary_style = learning_style.get('primary_style')
        
        if primary_style == 'visual':
            customizations.update({
                'color_scheme': 'high_contrast',
                'use_icons': True,
                'diagram_emphasis': True,
                'visual_progress_indicators': True
            })
        elif primary_style == 'reading':
            customizations.update({
                'font_size': 'large',
                'line_spacing': 'wide',
                'text_heavy_layout': True,
                'detailed_explanations': True
            })
        elif primary_style == 'kinesthetic':
            customizations.update({
                'interactive_elements': True,
                'gesture_controls': True,
                'tactile_feedback': True,
                'hands_on_examples': True
            })
        
        # 認知負荷に基づく調整
        load_tolerance = cognitive_load.get('load_tolerance', 'medium')
        
        if load_tolerance == 'low':
            customizations.update({
                'simplified_interface': True,
                'reduced_distractions': True,
                'single_focus_mode': True
            })
        elif load_tolerance == 'high':
            customizations.update({
                'information_dense': True,
                'multi_panel_layout': True,
                'advanced_features': True
            })
        
        return customizations
    
    # === ヘルパーメソッド ===
    
    def _load_user_data(self, user_id: str) -> Dict[str, Any]:
        """ユーザーデータ読み込み"""
        filepath = os.path.join(self.user_data_dir, f"{user_id}.json")
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"ユーザーデータ読み込みエラー {filepath}: {e}")
            return {}
    
    def _save_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """ユーザープロファイル保存"""
        try:
            profiles = {}
            if os.path.exists(self.user_profiles_file):
                with open(self.user_profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            
            profiles[user_id] = profile
            
            with open(self.user_profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"ユーザープロファイル保存エラー: {e}")
    
    def _load_ui_preferences(self, user_id: str) -> Dict[str, Any]:
        """UI設定読み込み"""
        try:
            if os.path.exists(self.ui_preferences_file):
                with open(self.ui_preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    return preferences.get(user_id, {})
            return {}
        except Exception as e:
            logger.warning(f"UI設定読み込みエラー: {e}")
            return {}
    
    def _save_ui_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """UI設定保存"""
        try:
            all_preferences = {}
            if os.path.exists(self.ui_preferences_file):
                with open(self.ui_preferences_file, 'r', encoding='utf-8') as f:
                    all_preferences = json.load(f)
            
            all_preferences[user_id] = preferences
            
            with open(self.ui_preferences_file, 'w', encoding='utf-8') as f:
                json.dump(all_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"UI設定保存エラー: {e}")
    
    def _create_default_profile(self, user_id: str) -> Dict[str, Any]:
        """デフォルトプロファイル作成"""
        return {
            'user_id': user_id,
            'updated_at': datetime.now().isoformat(),
            'learning_patterns': {},
            'learning_style': {'primary_style': 'reading', 'confidence': 0.1},
            'cognitive_load': {},
            'time_patterns': {},
            'motivation_profile': {},
            'learning_effectiveness': {},
            'personalization_recommendations': [],
            'confidence_score': 0.1
        }
    
    def _calculate_profile_confidence(self, history: List[Dict]) -> float:
        """プロファイル信頼度計算"""
        if not history:
            return 0.1
        
        # データ量による信頼度
        data_confidence = min(len(history) / 100, 1.0)
        
        # データ期間による信頼度
        dates = []
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get('date', ''))
                dates.append(dt.date())
            except:
                continue
        
        if dates:
            date_range = (max(dates) - min(dates)).days
            time_confidence = min(date_range / 30, 1.0)  # 30日で最大信頼度
        else:
            time_confidence = 0.1
        
        return (data_confidence + time_confidence) / 2
    
    def _get_preferred_hours(self, study_times: List[int]) -> List[int]:
        """好みの学習時間帯取得"""
        if not study_times:
            return []
        
        hour_counts = Counter(study_times)
        avg_count = sum(hour_counts.values()) / len(hour_counts)
        
        return [hour for hour, count in hour_counts.items() if count > avg_count]
    
    def _calculate_consistency(self, study_dates: List) -> float:
        """学習一貫性計算"""
        if len(study_dates) < 2:
            return 0.0
        
        study_dates = sorted(study_dates)
        intervals = []
        for i in range(1, len(study_dates)):
            interval = (study_dates[i] - study_dates[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # 間隔の標準偏差が小さいほど一貫性が高い
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = math.sqrt(variance)
        
        # 一貫性スコア（0-1）
        consistency = max(0, 1 - (std_dev / mean_interval)) if mean_interval > 0 else 0
        return consistency
    
    # その他の多数のヘルパーメソッドは実装を簡略化
    def _calculate_improvement_rate(self, accuracy_trend: List[float]) -> float:
        if len(accuracy_trend) < 2:
            return 0.0
        return accuracy_trend[-1] - accuracy_trend[0]
    
    def _calculate_session_lengths(self, history: List[Dict]) -> List[int]:
        # セッション長計算（簡略化）
        return [len(history) // 10] if history else [0]
    
    def _get_preferred_session_range(self, session_lengths: List[int]) -> Tuple[int, int]:
        if not session_lengths:
            return (10, 20)
        return (min(session_lengths), max(session_lengths))
    
    # 残りのメソッドも同様に簡略化実装
    def _analyze_error_patterns(self, history: List[Dict]) -> Dict:
        return {}
    
    def _estimate_optimal_difficulty(self, cognitive_load_indicators: Dict) -> str:
        return 'medium'
    
    def _calculate_load_tolerance(self, history: List[Dict]) -> str:
        return 'medium'
    
    def _analyze_fatigue_patterns(self, history: List[Dict]) -> Dict:
        return {}
    
    def _find_peak_performance_time(self, hourly_performance: Dict) -> int:
        if not hourly_performance:
            return 14  # デフォルト
        best_hour = max(hourly_performance.keys(), 
                       key=lambda h: sum(hourly_performance[h]) / len(hourly_performance[h]))
        return best_hour
    
    def _find_optimal_session_duration(self, session_durations: List[int]) -> int:
        return sum(session_durations) // len(session_durations) if session_durations else 30
    
    def _estimate_fatigue_threshold(self, history: List[Dict]) -> int:
        return 60  # 60分
    
    def _analyze_weekly_patterns(self, history: List[Dict]) -> Dict:
        return {}
    
    def _calculate_max_streak(self, study_dates: List) -> int:
        return 1  # 簡略化
    
    def _calculate_current_streak(self, study_dates: List) -> int:
        return 1  # 簡略化
    
    def _analyze_challenge_seeking(self, history: List[Dict]) -> float:
        return 0.5  # 中程度
    
    def _analyze_progress_sensitivity(self, history: List[Dict]) -> float:
        return 0.5  # 中程度
    
    def _analyze_reward_responsiveness(self, user_data: Dict) -> float:
        return 0.5  # 中程度
    
    def _calculate_persistence_level(self, history: List[Dict]) -> float:
        return min(len(history) / 50, 1.0)  # 50問で最大
    
    def _classify_motivation_type(self, challenge: float, progress: float, reward: float) -> str:
        if challenge > 0.6:
            return 'achievement_oriented'
        elif progress > 0.6:
            return 'progress_oriented'
        elif reward > 0.6:
            return 'reward_oriented'
        else:
            return 'balanced'
    
    def _calculate_learning_curve(self, history: List[Dict]) -> List[float]:
        # 簡略化された学習曲線
        window_size = 10
        curve = []
        for i in range(0, len(history), window_size):
            window = history[i:i+window_size]
            accuracy = sum(1 for h in window if h.get('is_correct', False)) / len(window)
            curve.append(accuracy)
        return curve
    
    def _calculate_retention_rate(self, history: List[Dict]) -> float:
        return 0.7  # 70% デフォルト
    
    def _analyze_transfer_learning(self, history: List[Dict]) -> float:
        return 0.6  # 60% デフォルト
    
    def _calculate_learning_efficiency(self, history: List[Dict]) -> float:
        if not history:
            return 0.0
        correct_count = sum(1 for h in history if h.get('is_correct', False))
        return correct_count / len(history)
    
    def _detect_learning_plateau(self, learning_curve: List[float]) -> bool:
        if len(learning_curve) < 5:
            return False
        # 最近5点の変化が少ない場合はプラトー
        recent_changes = [abs(learning_curve[i] - learning_curve[i-1]) 
                         for i in range(-4, 0)]
        return sum(recent_changes) < 0.1

# 残りのメソッドも簡略化して実装継続...
    def _save_learning_plan(self, user_id: str, plan: Dict[str, Any]):
        """学習プラン保存"""
        try:
            plans_file = os.path.join(self.personalization_data_dir, 'learning_plans.json')
            plans = {}
            if os.path.exists(plans_file):
                with open(plans_file, 'r', encoding='utf-8') as f:
                    plans = json.load(f)
            
            plans[user_id] = plan
            
            with open(plans_file, 'w', encoding='utf-8') as f:
                json.dump(plans, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"学習プラン保存エラー: {e}")

# グローバルインスタンス
advanced_personalization = AdvancedPersonalizationEngine()