"""
RCCM学習アプリ - 学習効率最適化エンジン
個人の学習パターンとバイオリズム分析による最適学習時間推奨システム
"""

import math
import statistics
from datetime import datetime, timedelta, time
from collections import defaultdict, deque
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LearningOptimizer:
    """学習効率最適化エンジン"""
    
    def __init__(self):
        # バイオリズム周期（日数）
        self.biorhythm_cycles = {
            'physical': 23,      # 身体リズム
            'emotional': 28,     # 感情リズム
            'intellectual': 33   # 知性リズム
        }
        
        # 時間帯別学習効率ベースライン
        self.time_efficiency_baseline = {
            6: 0.85,   # 早朝
            7: 0.90,
            8: 0.92,
            9: 0.95,   # 午前のピーク
            10: 0.98,
            11: 0.95,
            12: 0.80,  # 昼食時間
            13: 0.75,  # 午後の眠気
            14: 0.80,
            15: 0.85,
            16: 0.90,
            17: 0.85,
            18: 0.80,
            19: 0.85,  # 夕方の復活
            20: 0.90,
            21: 0.85,
            22: 0.75,  # 夜間の低下
            23: 0.65
        }
        
        # 学習パターン分析用パラメータ
        self.pattern_analysis_window = 30  # 日数
        self.minimum_sessions_for_analysis = 10
        self.optimal_session_length = 25  # 分
        self.break_efficiency_factor = 0.85
        
        # 疲労度計算パラメータ
        self.fatigue_accumulation_rate = 0.02
        self.fatigue_recovery_rate = 0.05
        self.max_daily_study_minutes = 240  # 4時間
        
    def analyze_personal_learning_pattern(self, user_session: Dict) -> Dict[str, Any]:
        """個人の学習パターン分析"""
        try:
            history = user_session.get('history', [])
            if len(history) < self.minimum_sessions_for_analysis:
                return self._generate_default_pattern()
            
            # 時間帯別パフォーマンス分析
            hourly_performance = self._analyze_hourly_performance(history)
            
            # 学習セッション長分析
            session_length_analysis = self._analyze_session_lengths(history)
            
            # 学習継続性分析
            consistency_analysis = self._analyze_learning_consistency(history)
            
            # 疲労パターン分析
            fatigue_pattern = self._analyze_fatigue_patterns(history)
            
            # 最適学習時間の特定
            optimal_times = self._identify_optimal_learning_times(hourly_performance)
            
            pattern = {
                'hourly_performance': hourly_performance,
                'session_analysis': session_length_analysis,
                'consistency': consistency_analysis,
                'fatigue_pattern': fatigue_pattern,
                'optimal_times': optimal_times,
                'learning_type': self._classify_learning_type(hourly_performance, session_length_analysis),
                'recommended_schedule': self._generate_personal_schedule(optimal_times, session_length_analysis),
                'analysis_confidence': self._calculate_pattern_confidence(len(history))
            }
            
            logger.info(f"学習パターン分析完了: タイプ={pattern['learning_type']}, 信頼度={pattern['analysis_confidence']:.2f}")
            
            return pattern
            
        except Exception as e:
            logger.error(f"学習パターン分析エラー: {e}")
            return self._generate_default_pattern()
    
    def calculate_biorhythm_score(self, birth_date: str, target_date: datetime = None) -> Dict[str, float]:
        """バイオリズムスコア計算"""
        try:
            if target_date is None:
                target_date = datetime.now()
            
            birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
            days_lived = (target_date - birth_datetime).days
            
            biorhythm_scores = {}
            
            for rhythm_type, cycle_length in self.biorhythm_cycles.items():
                # サイン波でバイオリズムを計算
                phase = (days_lived % cycle_length) / cycle_length * 2 * math.pi
                score = math.sin(phase)
                biorhythm_scores[rhythm_type] = score
            
            # 総合スコア（知性リズムを重視）
            biorhythm_scores['composite'] = (
                biorhythm_scores['physical'] * 0.2 +
                biorhythm_scores['emotional'] * 0.3 +
                biorhythm_scores['intellectual'] * 0.5
            )
            
            return biorhythm_scores
            
        except Exception as e:
            logger.error(f"バイオリズム計算エラー: {e}")
            return {
                'physical': 0.0,
                'emotional': 0.0,
                'intellectual': 0.0,
                'composite': 0.0
            }
    
    def get_optimal_study_time_recommendation(self, user_session: Dict, 
                                            target_date: datetime = None) -> Dict[str, Any]:
        """最適学習時間推奨"""
        try:
            if target_date is None:
                target_date = datetime.now()
            
            # 個人学習パターン取得
            learning_pattern = self.analyze_personal_learning_pattern(user_session)
            
            # バイオリズム計算（生年月日が設定されている場合）
            birth_date = user_session.get('birth_date')
            biorhythm_scores = {}
            if birth_date:
                biorhythm_scores = self.calculate_biorhythm_score(birth_date, target_date)
            
            # 時間帯別推奨度計算
            hourly_recommendations = self._calculate_hourly_recommendations(
                learning_pattern, biorhythm_scores, target_date
            )
            
            # 最適学習スケジュール生成
            optimal_schedule = self._generate_optimal_schedule(
                hourly_recommendations, learning_pattern, target_date
            )
            
            # 学習効率予測
            efficiency_forecast = self._forecast_learning_efficiency(
                learning_pattern, biorhythm_scores, target_date
            )
            
            recommendation = {
                'target_date': target_date.strftime('%Y-%m-%d'),
                'biorhythm_scores': biorhythm_scores,
                'hourly_recommendations': hourly_recommendations,
                'optimal_schedule': optimal_schedule,
                'efficiency_forecast': efficiency_forecast,
                'learning_pattern_type': learning_pattern['learning_type'],
                'confidence_level': learning_pattern['analysis_confidence'],
                'daily_study_limit': self._calculate_daily_study_limit(learning_pattern),
                'break_recommendations': self._generate_break_recommendations(learning_pattern)
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"最適学習時間推奨エラー: {e}")
            return self._generate_default_recommendation()
    
    def track_real_time_efficiency(self, user_session: Dict, current_session_data: Dict) -> Dict[str, Any]:
        """リアルタイム学習効率追跡"""
        try:
            current_time = datetime.now()
            session_start = current_session_data.get('start_time', current_time)
            session_duration = (current_time - session_start).total_seconds() / 60  # 分
            
            # 現在の推定効率
            current_efficiency = self._estimate_current_efficiency(
                user_session, current_time, session_duration
            )
            
            # 疲労度評価
            fatigue_level = self._calculate_current_fatigue(user_session, current_time)
            
            # セッション継続推奨判定
            should_continue = self._should_continue_session(
                current_efficiency, fatigue_level, session_duration
            )
            
            # 次回推奨時間
            next_optimal_time = self._predict_next_optimal_time(user_session, current_time)
            
            tracking_result = {
                'current_efficiency': current_efficiency,
                'fatigue_level': fatigue_level,
                'session_duration': session_duration,
                'should_continue': should_continue,
                'recommended_break_duration': self._calculate_break_duration(fatigue_level),
                'next_optimal_time': next_optimal_time,
                'efficiency_trend': self._calculate_efficiency_trend(user_session),
                'performance_prediction': self._predict_session_performance(
                    current_efficiency, fatigue_level, session_duration
                )
            }
            
            return tracking_result
            
        except Exception as e:
            logger.error(f"リアルタイム効率追跡エラー: {e}")
            return {'error': str(e)}
    
    def _analyze_hourly_performance(self, history: List[Dict]) -> Dict[int, Dict[str, float]]:
        """時間帯別パフォーマンス分析"""
        hourly_data = defaultdict(lambda: {'accuracy': [], 'speed': [], 'sessions': 0})
        
        for entry in history:
            try:
                date_str = entry.get('date', '')
                if not date_str:
                    continue
                
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                hour = dt.hour
                
                hourly_data[hour]['accuracy'].append(1 if entry.get('is_correct') else 0)
                elapsed = entry.get('elapsed', 60)
                hourly_data[hour]['speed'].append(elapsed)
                hourly_data[hour]['sessions'] += 1
                
            except (ValueError, TypeError):
                continue
        
        # 統計計算
        hourly_performance = {}
        for hour, data in hourly_data.items():
            if data['sessions'] > 0:
                avg_accuracy = statistics.mean(data['accuracy']) if data['accuracy'] else 0
                avg_speed = statistics.mean(data['speed']) if data['speed'] else 60
                
                # 効率スコア計算（正答率重視、速度も考慮）
                efficiency_score = avg_accuracy * 0.7 + (1 - min(avg_speed / 120, 1)) * 0.3
                
                hourly_performance[hour] = {
                    'accuracy': avg_accuracy,
                    'avg_speed': avg_speed,
                    'efficiency_score': efficiency_score,
                    'sessions': data['sessions'],
                    'confidence': min(data['sessions'] / 10, 1.0)  # セッション数ベースの信頼度
                }
        
        return hourly_performance
    
    def _analyze_session_lengths(self, history: List[Dict]) -> Dict[str, Any]:
        """学習セッション長分析"""
        sessions = defaultdict(list)
        
        # セッションをグループ化
        current_session = []
        last_time = None
        
        for entry in history:
            try:
                date_str = entry.get('date', '')
                if not date_str:
                    continue
                
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                
                if last_time and (dt - last_time).total_seconds() > 1800:  # 30分以上空いた場合新セッション
                    if current_session:
                        self._process_session_group(current_session, sessions)
                    current_session = []
                
                current_session.append(entry)
                last_time = dt
                
            except (ValueError, TypeError):
                continue
        
        if current_session:
            self._process_session_group(current_session, sessions)
        
        # 分析結果
        analysis = {
            'avg_session_length': 0,
            'optimal_session_length': self.optimal_session_length,
            'session_count': len(sessions),
            'length_distribution': {},
            'performance_by_length': {}
        }
        
        if sessions:
            lengths = []
            for session_id, session_data in sessions.items():
                length = session_data['duration']
                lengths.append(length)
                
                # 長さ別パフォーマンス
                length_category = self._categorize_session_length(length)
                if length_category not in analysis['performance_by_length']:
                    analysis['performance_by_length'][length_category] = {
                        'accuracy': [],
                        'count': 0
                    }
                
                analysis['performance_by_length'][length_category]['accuracy'].append(
                    session_data['accuracy']
                )
                analysis['performance_by_length'][length_category]['count'] += 1
            
            analysis['avg_session_length'] = statistics.mean(lengths)
            
            # パフォーマンス統計を計算
            for category, data in analysis['performance_by_length'].items():
                if data['accuracy']:
                    data['avg_accuracy'] = statistics.mean(data['accuracy'])
                else:
                    data['avg_accuracy'] = 0
        
        return analysis
    
    def _analyze_learning_consistency(self, history: List[Dict]) -> Dict[str, Any]:
        """学習継続性分析"""
        if not history:
            return {'consistency_score': 0, 'study_days': 0, 'max_streak': 0}
        
        # 日別学習日を特定
        study_dates = set()
        for entry in history:
            try:
                date_str = entry.get('date', '')
                if date_str:
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    study_dates.add(dt.date())
            except (ValueError, TypeError):
                continue
        
        if not study_dates:
            return {'consistency_score': 0, 'study_days': 0, 'max_streak': 0}
        
        # ストリーク計算
        sorted_dates = sorted(study_dates)
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # 一貫性スコア（過去30日間での学習頻度）
        end_date = max(study_dates)
        start_date = end_date - timedelta(days=29)
        recent_study_days = sum(1 for date in study_dates if start_date <= date <= end_date)
        consistency_score = min(recent_study_days / 20, 1.0)  # 20日/30日を満点とする
        
        return {
            'consistency_score': consistency_score,
            'study_days': len(study_dates),
            'max_streak': max_streak,
            'recent_study_days': recent_study_days,
            'study_frequency': len(study_dates) / max((datetime.now().date() - min(study_dates)).days + 1, 1)
        }
    
    def _analyze_fatigue_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """疲労パターン分析"""
        daily_performance = defaultdict(list)
        
        for entry in history:
            try:
                date_str = entry.get('date', '')
                if not date_str:
                    continue
                
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                date_key = dt.date()
                
                # その日の何問目かを追跡
                daily_performance[date_key].append({
                    'accuracy': 1 if entry.get('is_correct') else 0,
                    'speed': entry.get('elapsed', 60),
                    'time': dt.time()
                })
                
            except (ValueError, TypeError):
                continue
        
        # 疲労パターンの分析
        fatigue_indicators = {
            'accuracy_decline_rate': 0,
            'speed_decline_rate': 0,
            'optimal_session_count': 0,
            'fatigue_threshold': 20  # 問題数
        }
        
        decline_rates = []
        speed_decline_rates = []
        
        for date, daily_data in daily_performance.items():
            if len(daily_data) >= 10:  # 十分なデータがある日のみ
                # 前半と後半で比較
                mid_point = len(daily_data) // 2
                first_half = daily_data[:mid_point]
                second_half = daily_data[mid_point:]
                
                first_accuracy = statistics.mean([d['accuracy'] for d in first_half])
                second_accuracy = statistics.mean([d['accuracy'] for d in second_half])
                
                first_speed = statistics.mean([d['speed'] for d in first_half])
                second_speed = statistics.mean([d['speed'] for d in second_half])
                
                accuracy_decline = first_accuracy - second_accuracy
                speed_decline = (second_speed - first_speed) / first_speed if first_speed > 0 else 0
                
                decline_rates.append(accuracy_decline)
                speed_decline_rates.append(speed_decline)
        
        if decline_rates:
            fatigue_indicators['accuracy_decline_rate'] = statistics.mean(decline_rates)
        if speed_decline_rates:
            fatigue_indicators['speed_decline_rate'] = statistics.mean(speed_decline_rates)
        
        return fatigue_indicators
    
    def _identify_optimal_learning_times(self, hourly_performance: Dict) -> List[Dict]:
        """最適学習時間の特定"""
        optimal_times = []
        
        # 効率スコアでソート
        sorted_hours = sorted(
            hourly_performance.items(),
            key=lambda x: x[1]['efficiency_score'],
            reverse=True
        )
        
        # 上位の時間帯を選択（信頼度も考慮）
        for hour, data in sorted_hours:
            if data['confidence'] >= 0.3 and data['efficiency_score'] >= 0.7:
                optimal_times.append({
                    'hour': hour,
                    'efficiency_score': data['efficiency_score'],
                    'confidence': data['confidence'],
                    'sessions': data['sessions']
                })
        
        return optimal_times[:5]  # 上位5時間帯
    
    def _classify_learning_type(self, hourly_performance: Dict, session_analysis: Dict) -> str:
        """学習タイプの分類"""
        if not hourly_performance:
            return 'unknown'
        
        # 朝型・夜型の判定
        morning_hours = [6, 7, 8, 9, 10]
        evening_hours = [19, 20, 21, 22]
        
        morning_efficiency = statistics.mean([
            hourly_performance.get(h, {}).get('efficiency_score', 0)
            for h in morning_hours
        ])
        
        evening_efficiency = statistics.mean([
            hourly_performance.get(h, {}).get('efficiency_score', 0)
            for h in evening_hours
        ])
        
        avg_session_length = session_analysis.get('avg_session_length', 0)
        
        if morning_efficiency > evening_efficiency + 0.1:
            if avg_session_length > 45:
                return 'morning_intensive'
            else:
                return 'morning_light'
        elif evening_efficiency > morning_efficiency + 0.1:
            if avg_session_length > 45:
                return 'evening_intensive'
            else:
                return 'evening_light'
        else:
            if avg_session_length > 45:
                return 'flexible_intensive'
            else:
                return 'flexible_light'
    
    def _generate_personal_schedule(self, optimal_times: List[Dict], session_analysis: Dict) -> Dict[str, Any]:
        """個人向けスケジュール生成"""
        if not optimal_times:
            return self._generate_default_schedule()
        
        schedule = {
            'primary_session': {},
            'secondary_sessions': [],
            'session_length': min(session_analysis.get('avg_session_length', 25), 45),
            'break_intervals': 5,
            'daily_target': 60  # 分
        }
        
        # 最も効率の良い時間を主要セッションに
        best_time = optimal_times[0]
        schedule['primary_session'] = {
            'start_hour': best_time['hour'],
            'duration': schedule['session_length'],
            'efficiency_expected': best_time['efficiency_score']
        }
        
        # 追加セッション
        remaining_times = optimal_times[1:3]  # 最大2つの追加セッション
        for time_slot in remaining_times:
            schedule['secondary_sessions'].append({
                'start_hour': time_slot['hour'],
                'duration': min(schedule['session_length'], 20),
                'efficiency_expected': time_slot['efficiency_score']
            })
        
        return schedule
    
    def _calculate_hourly_recommendations(self, learning_pattern: Dict, 
                                        biorhythm_scores: Dict, target_date: datetime) -> Dict[int, float]:
        """時間帯別推奨度計算"""
        recommendations = {}
        hourly_performance = learning_pattern.get('hourly_performance', {})
        
        for hour in range(6, 24):  # 6時から23時まで
            base_score = self.time_efficiency_baseline.get(hour, 0.5)
            
            # 個人パフォーマンスの影響
            personal_score = 0
            if hour in hourly_performance:
                personal_data = hourly_performance[hour]
                personal_score = personal_data['efficiency_score'] * personal_data['confidence']
            
            # バイオリズムの影響
            biorhythm_bonus = 0
            if biorhythm_scores:
                intellectual_rhythm = biorhythm_scores.get('intellectual', 0)
                biorhythm_bonus = intellectual_rhythm * 0.1  # 最大10%の影響
            
            # 総合推奨度
            total_score = base_score * 0.4 + personal_score * 0.5 + biorhythm_bonus + 0.1
            recommendations[hour] = max(0, min(1, total_score))
        
        return recommendations
    
    def _generate_optimal_schedule(self, hourly_recommendations: Dict, 
                                 learning_pattern: Dict, target_date: datetime) -> Dict[str, Any]:
        """最適スケジュール生成"""
        # 推奨度の高い時間帯を特定
        sorted_hours = sorted(
            hourly_recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        optimal_schedule = {
            'recommended_sessions': [],
            'peak_efficiency_period': None,
            'total_daily_minutes': 0
        }
        
        session_length = learning_pattern.get('session_analysis', {}).get('optimal_session_length', 25)
        daily_limit = self._calculate_daily_study_limit(learning_pattern)
        
        accumulated_minutes = 0
        for hour, score in sorted_hours:
            if accumulated_minutes >= daily_limit:
                break
            
            if score >= 0.7:  # 高効率時間帯のみ
                session_duration = min(session_length, daily_limit - accumulated_minutes)
                
                optimal_schedule['recommended_sessions'].append({
                    'start_time': f"{hour:02d}:00",
                    'duration_minutes': session_duration,
                    'efficiency_score': score,
                    'recommended_activities': self._get_activity_recommendations(score, session_duration)
                })
                
                accumulated_minutes += session_duration
                
                # ピーク効率期間の設定
                if not optimal_schedule['peak_efficiency_period'] and score >= 0.8:
                    optimal_schedule['peak_efficiency_period'] = {
                        'start_hour': hour,
                        'efficiency_score': score
                    }
        
        optimal_schedule['total_daily_minutes'] = accumulated_minutes
        
        return optimal_schedule
    
    def _get_activity_recommendations(self, efficiency_score: float, duration: int) -> List[str]:
        """効率度に基づく活動推奨"""
        activities = []
        
        if efficiency_score >= 0.8:
            if duration >= 30:
                activities.extend([
                    "新しい概念の学習",
                    "応用問題への挑戦",
                    "弱点分野の集中学習"
                ])
            else:
                activities.extend([
                    "重要ポイントの復習",
                    "基礎問題の確認"
                ])
        elif efficiency_score >= 0.6:
            activities.extend([
                "標準問題の練習",
                "既習内容の整理",
                "軽い復習"
            ])
        else:
            activities.extend([
                "簡単な復習問題",
                "過去の学習内容確認",
                "休憩を多めに取る学習"
            ])
        
        return activities
    
    def _process_session_group(self, session_group: List[Dict], sessions: Dict):
        """セッショングループの処理"""
        if not session_group:
            return
        
        # セッション時間計算
        start_time = datetime.strptime(session_group[0]['date'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(session_group[-1]['date'], '%Y-%m-%d %H:%M:%S')
        duration = (end_time - start_time).total_seconds() / 60
        
        # 正答率計算
        correct_count = sum(1 for entry in session_group if entry.get('is_correct'))
        accuracy = correct_count / len(session_group) if session_group else 0
        
        session_id = f"{start_time.strftime('%Y%m%d_%H%M')}_{len(session_group)}"
        sessions[session_id] = {
            'duration': duration,
            'accuracy': accuracy,
            'question_count': len(session_group),
            'start_time': start_time
        }
    
    def _categorize_session_length(self, length: float) -> str:
        """セッション長のカテゴリ分け"""
        if length <= 15:
            return 'short'
        elif length <= 30:
            return 'medium'
        elif length <= 60:
            return 'long'
        else:
            return 'extended'
    
    def _generate_default_pattern(self) -> Dict[str, Any]:
        """デフォルト学習パターン"""
        return {
            'hourly_performance': {},
            'session_analysis': {
                'avg_session_length': 25,
                'optimal_session_length': 25,
                'session_count': 0
            },
            'consistency': {'consistency_score': 0},
            'fatigue_pattern': {'accuracy_decline_rate': 0},
            'optimal_times': [],
            'learning_type': 'flexible_light',
            'recommended_schedule': self._generate_default_schedule(),
            'analysis_confidence': 0.0
        }
    
    def _generate_default_schedule(self) -> Dict[str, Any]:
        """デフォルトスケジュール"""
        return {
            'primary_session': {
                'start_hour': 10,
                'duration': 25,
                'efficiency_expected': 0.7
            },
            'secondary_sessions': [
                {
                    'start_hour': 20,
                    'duration': 20,
                    'efficiency_expected': 0.6
                }
            ],
            'session_length': 25,
            'break_intervals': 5,
            'daily_target': 60
        }
    
    def _generate_default_recommendation(self) -> Dict[str, Any]:
        """デフォルト推奨"""
        return {
            'target_date': datetime.now().strftime('%Y-%m-%d'),
            'biorhythm_scores': {},
            'hourly_recommendations': {h: 0.5 for h in range(6, 24)},
            'optimal_schedule': {
                'recommended_sessions': [
                    {
                        'start_time': '10:00',
                        'duration_minutes': 25,
                        'efficiency_score': 0.7,
                        'recommended_activities': ['標準問題の練習']
                    }
                ],
                'total_daily_minutes': 25
            },
            'learning_pattern_type': 'unknown',
            'confidence_level': 0.0
        }
    
    def _calculate_pattern_confidence(self, history_length: int) -> float:
        """パターン信頼度計算"""
        if history_length < 10:
            return 0.2
        elif history_length < 50:
            return 0.5 + (history_length - 10) * 0.01
        else:
            return 0.9
    
    def _calculate_daily_study_limit(self, learning_pattern: Dict) -> int:
        """日次学習時間制限計算"""
        learning_type = learning_pattern.get('learning_type', 'flexible_light')
        
        if 'intensive' in learning_type:
            return min(180, self.max_daily_study_minutes)
        else:
            return min(120, self.max_daily_study_minutes)
    
    def _estimate_current_efficiency(self, user_session: Dict, current_time: datetime, 
                                   session_duration: float) -> float:
        """現在の学習効率推定"""
        base_efficiency = self.time_efficiency_baseline.get(current_time.hour, 0.5)
        
        # セッション時間による効率低下
        duration_factor = max(0.5, 1 - (session_duration - self.optimal_session_length) * 0.01)
        
        # 疲労による効率低下
        fatigue_factor = max(0.3, 1 - session_duration * self.fatigue_accumulation_rate)
        
        return base_efficiency * duration_factor * fatigue_factor
    
    def _calculate_current_fatigue(self, user_session: Dict, current_time: datetime) -> float:
        """現在の疲労度計算"""
        today_history = []
        today_str = current_time.strftime('%Y-%m-%d')
        
        for entry in user_session.get('history', []):
            if entry.get('date', '').startswith(today_str):
                today_history.append(entry)
        
        # 今日の学習時間から疲労度を推定
        study_minutes = len(today_history) * 2  # 1問約2分と仮定
        fatigue_level = min(1.0, study_minutes / 120)  # 2時間で最大疲労
        
        return fatigue_level
    
    def _should_continue_session(self, efficiency: float, fatigue: float, duration: float) -> bool:
        """セッション継続判定"""
        if duration >= 60:  # 1時間超過
            return False
        if fatigue >= 0.8:  # 高疲労
            return False
        if efficiency < 0.4:  # 低効率
            return False
        
        return True
    
    def _calculate_break_duration(self, fatigue_level: float) -> int:
        """休憩時間計算"""
        if fatigue_level < 0.3:
            return 5
        elif fatigue_level < 0.6:
            return 10
        else:
            return 15
    
    def _predict_next_optimal_time(self, user_session: Dict, current_time: datetime) -> str:
        """次回最適時間予測"""
        pattern = self.analyze_personal_learning_pattern(user_session)
        optimal_times = pattern.get('optimal_times', [])
        
        current_hour = current_time.hour
        
        # 今日の残り時間で最適な時間を探す
        for optimal_time in optimal_times:
            if optimal_time['hour'] > current_hour:
                return f"{optimal_time['hour']:02d}:00"
        
        # 今日に適切な時間がない場合、明日の最初の最適時間
        if optimal_times:
            return f"明日 {optimal_times[0]['hour']:02d}:00"
        
        return "明日 10:00"
    
    def _calculate_efficiency_trend(self, user_session: Dict) -> str:
        """効率トレンド計算"""
        history = user_session.get('history', [])
        if len(history) < 10:
            return 'insufficient_data'
        
        recent_10 = history[-10:]
        previous_10 = history[-20:-10] if len(history) >= 20 else []
        
        recent_accuracy = sum(1 for h in recent_10 if h.get('is_correct')) / len(recent_10)
        
        if previous_10:
            previous_accuracy = sum(1 for h in previous_10 if h.get('is_correct')) / len(previous_10)
            
            if recent_accuracy > previous_accuracy + 0.1:
                return 'improving'
            elif recent_accuracy < previous_accuracy - 0.1:
                return 'declining'
        
        return 'stable'
    
    def _predict_session_performance(self, efficiency: float, fatigue: float, duration: float) -> Dict[str, float]:
        """セッションパフォーマンス予測"""
        # 基本予測精度
        base_accuracy = efficiency * 0.8
        
        # 疲労による低下
        fatigue_impact = fatigue * 0.2
        predicted_accuracy = max(0.1, base_accuracy - fatigue_impact)
        
        # 継続した場合の予測
        if duration < 30:
            future_accuracy = predicted_accuracy * 0.95  # 軽微な低下
        else:
            future_accuracy = predicted_accuracy * (1 - duration * 0.005)  # 時間とともに低下
        
        return {
            'current_predicted_accuracy': predicted_accuracy,
            'future_predicted_accuracy': max(0.1, future_accuracy),
            'recommended_action': 'continue' if future_accuracy > 0.5 else 'break'
        }
    
    def _forecast_learning_efficiency(self, learning_pattern: Dict, biorhythm_scores: Dict, 
                                    target_date: datetime) -> Dict[str, Any]:
        """学習効率予測"""
        forecast = {
            'overall_efficiency': 0.7,
            'peak_hours': [],
            'low_efficiency_hours': [],
            'biorhythm_impact': 'neutral'
        }
        
        # バイオリズムの影響
        if biorhythm_scores:
            intellectual = biorhythm_scores.get('intellectual', 0)
            if intellectual > 0.5:
                forecast['biorhythm_impact'] = 'positive'
                forecast['overall_efficiency'] += 0.1
            elif intellectual < -0.5:
                forecast['biorhythm_impact'] = 'negative'
                forecast['overall_efficiency'] -= 0.1
        
        # 個人パターンからのピーク時間予測
        optimal_times = learning_pattern.get('optimal_times', [])
        for time_data in optimal_times:
            if time_data['efficiency_score'] > 0.8:
                forecast['peak_hours'].append(time_data['hour'])
            elif time_data['efficiency_score'] < 0.5:
                forecast['low_efficiency_hours'].append(time_data['hour'])
        
        return forecast
    
    def _generate_break_recommendations(self, learning_pattern: Dict) -> Dict[str, Any]:
        """休憩推奨生成"""
        learning_type = learning_pattern.get('learning_type', 'flexible_light')
        
        if 'intensive' in learning_type:
            return {
                'short_break_interval': 25,  # 25分ごと
                'short_break_duration': 5,
                'long_break_interval': 90,   # 90分ごと
                'long_break_duration': 15,
                'recommended_activities': [
                    '軽いストレッチ',
                    '深呼吸',
                    '水分補給',
                    '目の休憩'
                ]
            }
        else:
            return {
                'short_break_interval': 20,  # 20分ごと
                'short_break_duration': 5,
                'long_break_interval': 60,   # 60分ごと
                'long_break_duration': 10,
                'recommended_activities': [
                    '軽い散歩',
                    'リラックス',
                    '水分補給'
                ]
            }

# グローバルインスタンス
learning_optimizer = LearningOptimizer()