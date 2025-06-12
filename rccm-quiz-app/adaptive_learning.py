"""
RCCM学習アプリ - アダプティブ学習システム
AI分析結果に基づいて個人に最適化された問題選択と学習プランを提供
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class AdaptiveLearningEngine:
    """アダプティブ学習エンジン"""
    
    def __init__(self):
        self.difficulty_weights = {
            'basic': 1.0,
            '基本': 1.0,
            'standard': 1.2,
            '標準': 1.2,
            'advanced': 1.5,
            '応用': 1.5,
            'expert': 2.0,
            '上級': 2.0
        }
        
        # 学習モード定義
        self.learning_modes = {
            'foundation': {
                'weak_area_ratio': 0.8,
                'new_question_ratio': 0.2,
                'review_ratio': 0.0,
                'difficulty_preference': 'basic'
            },
            'balanced': {
                'weak_area_ratio': 0.5,
                'new_question_ratio': 0.3,
                'review_ratio': 0.2,
                'difficulty_preference': 'mixed'
            },
            'challenge': {
                'weak_area_ratio': 0.3,
                'new_question_ratio': 0.4,
                'review_ratio': 0.3,
                'difficulty_preference': 'advanced'
            },
            'review': {
                'weak_area_ratio': 0.2,
                'new_question_ratio': 0.1,
                'review_ratio': 0.7,
                'difficulty_preference': 'mixed'
            }
        }
    
    def get_adaptive_questions(self, user_session: Dict, all_questions: List[Dict], 
                             ai_analysis: Dict, session_size: int = 10,
                             learning_mode: str = 'balanced') -> List[Dict]:
        """AI分析に基づくアダプティブ問題選択"""
        
        mode_config = self.learning_modes.get(learning_mode, self.learning_modes['balanced'])
        
        # 各カテゴリの問題数計算
        weak_area_count = int(session_size * mode_config['weak_area_ratio'])
        new_question_count = int(session_size * mode_config['new_question_ratio'])
        review_count = session_size - weak_area_count - new_question_count
        
        selected_questions = []
        
        # 1. 弱点エリアの問題
        weak_questions = self._select_weak_area_questions(
            user_session, all_questions, ai_analysis, weak_area_count, mode_config
        )
        selected_questions.extend(weak_questions)
        
        # 2. 復習問題（SRS）
        review_questions = self._select_review_questions(
            user_session, all_questions, review_count
        )
        selected_questions.extend(review_questions)
        
        # 3. 新規問題
        new_questions = self._select_new_questions(
            user_session, all_questions, selected_questions, 
            new_question_count, mode_config
        )
        selected_questions.extend(new_questions)
        
        # 4. 問題をシャッフル（学習効果向上のため）
        random.shuffle(selected_questions)
        
        # 5. セッション情報を記録
        self._record_session_plan(user_session, {
            'mode': learning_mode,
            'weak_area_questions': len(weak_questions),
            'review_questions': len(review_questions),
            'new_questions': len(new_questions),
            'total_questions': len(selected_questions)
        })
        
        logger.info(f"アダプティブ問題選択完了: 弱点{len(weak_questions)}問, 復習{len(review_questions)}問, 新規{len(new_questions)}問")
        
        return selected_questions[:session_size]
    
    def _select_weak_area_questions(self, user_session: Dict, all_questions: List[Dict],
                                   ai_analysis: Dict, count: int, mode_config: Dict) -> List[Dict]:
        """弱点エリアからの問題選択"""
        if count <= 0:
            return []
        
        weak_areas = ai_analysis.get('weak_areas', {})
        if not weak_areas:
            return []
        
        # 弱点エリアを優先度順にソート
        sorted_weak_areas = sorted(
            weak_areas.items(),
            key=lambda x: x[1].get('priority', 0),
            reverse=True
        )
        
        selected_questions = []
        questions_per_area = max(1, count // len(sorted_weak_areas))
        
        for category, weakness_info in sorted_weak_areas:
            if len(selected_questions) >= count:
                break
                
            # カテゴリの問題を取得
            category_questions = [
                q for q in all_questions 
                if q.get('category') == category
            ]
            
            if not category_questions:
                continue
            
            # 難易度フィルタリング
            filtered_questions = self._filter_by_difficulty_preference(
                category_questions, mode_config['difficulty_preference'], weakness_info
            )
            
            # 既回答問題の除外
            available_questions = self._filter_unasked_questions(
                user_session, filtered_questions
            )
            
            # 問題選択（重み付きランダム）
            area_questions = self._weighted_random_selection(
                available_questions, 
                min(questions_per_area, len(available_questions)),
                weakness_info
            )
            
            selected_questions.extend(area_questions)
        
        return selected_questions
    
    def _select_review_questions(self, user_session: Dict, all_questions: List[Dict],
                                count: int) -> List[Dict]:
        """SRS復習問題の選択"""
        if count <= 0:
            return []
        
        # 既存のSRS機能を活用（依存関係を回避）
        try:
            from app import get_due_questions
            due_questions = get_due_questions(user_session, all_questions)
            
            # 復習優先度でソート（期限切れ日数順）
            due_questions.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
            
            # 必要数だけ選択
            selected_reviews = [
                item['question'] for item in due_questions[:count]
            ]
            
            return selected_reviews
        except ImportError:
            # テスト環境での代替実装
            return self._get_due_questions_standalone(user_session, all_questions, count)
    
    def _get_due_questions_standalone(self, user_session: Dict, all_questions: List[Dict], count: int) -> List[Dict]:
        """スタンドアロン版の復習問題取得（テスト用）"""
        from datetime import datetime, timedelta
        
        srs_data = user_session.get('srs_data', {})
        if not srs_data:
            return []
        
        today = datetime.now().date()
        due_questions = []
        
        for question_id, data in srs_data.items():
            try:
                next_review = datetime.fromisoformat(data['next_review']).date()
                if next_review <= today:
                    question = next((q for q in all_questions if str(q.get('id', 0)) == question_id), None)
                    if question:
                        days_overdue = (today - next_review).days
                        due_questions.append({
                            'question': question,
                            'days_overdue': days_overdue
                        })
            except (ValueError, KeyError):
                continue
        
        # 優先度順にソート
        due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return [item['question'] for item in due_questions[:count]]
    
    def _select_new_questions(self, user_session: Dict, all_questions: List[Dict],
                            already_selected: List[Dict], count: int, 
                            mode_config: Dict) -> List[Dict]:
        """新規問題の選択"""
        if count <= 0:
            return []
        
        # 既に選択された問題のIDを取得
        selected_ids = {q.get('id') for q in already_selected}
        
        # 未回答の問題を取得
        answered_ids = {entry.get('id') for entry in user_session.get('history', [])}
        
        available_questions = [
            q for q in all_questions
            if q.get('id') not in answered_ids and q.get('id') not in selected_ids
        ]
        
        if not available_questions:
            # 全問題回答済みの場合、正答率が低い問題を再選択
            return self._select_low_accuracy_questions(user_session, all_questions, count)
        
        # 難易度バランス調整
        balanced_questions = self._balance_difficulty_distribution(
            available_questions, count, mode_config['difficulty_preference']
        )
        
        return balanced_questions
    
    def _filter_by_difficulty_preference(self, questions: List[Dict], 
                                       preference: str, weakness_info: Dict) -> List[Dict]:
        """難易度設定による問題フィルタリング"""
        if preference == 'mixed':
            return questions
        
        weakness_score = weakness_info.get('weakness_score', 0.5)
        
        # 弱点度合いに応じた難易度調整
        if weakness_score > 0.7:  # 非常に弱い分野
            target_difficulties = ['basic', '基本', 'standard', '標準']
        elif weakness_score > 0.4:  # 中程度の弱点
            target_difficulties = ['standard', '標準', 'advanced', '応用']
        else:  # 軽微な弱点
            target_difficulties = ['advanced', '応用', 'expert', '上級']
        
        if preference == 'basic':
            target_difficulties = ['basic', '基本']
        elif preference == 'advanced':
            target_difficulties = ['advanced', '応用', 'expert', '上級']
        
        filtered = [
            q for q in questions
            if q.get('difficulty', '標準') in target_difficulties
        ]
        
        return filtered if filtered else questions  # フィルタ結果が空の場合は元の問題を返す
    
    def _filter_unasked_questions(self, user_session: Dict, questions: List[Dict]) -> List[Dict]:
        """未回答問題の抽出"""
        answered_ids = {entry.get('id') for entry in user_session.get('history', [])}
        
        unasked = [q for q in questions if q.get('id') not in answered_ids]
        
        # 未回答問題が少ない場合、間違えた問題も含める
        if len(unasked) < 3:
            incorrect_questions = [
                q for q in questions
                if any(
                    entry.get('id') == q.get('id') and not entry.get('is_correct', False)
                    for entry in user_session.get('history', [])
                )
            ]
            unasked.extend(incorrect_questions)
        
        return unasked
    
    def _weighted_random_selection(self, questions: List[Dict], count: int,
                                 weakness_info: Dict) -> List[Dict]:
        """重み付きランダム選択"""
        if len(questions) <= count:
            return questions
        
        # 難易度による重み付け
        weakness_score = weakness_info.get('weakness_score', 0.5)
        
        weighted_questions = []
        for question in questions:
            difficulty = question.get('difficulty', '標準')
            base_weight = self.difficulty_weights.get(difficulty, 1.0)
            
            # 弱点度合いに応じた重み調整
            if weakness_score > 0.6:
                # 弱点が大きい場合、基本問題の重みを上げる
                if difficulty in ['basic', '基本']:
                    base_weight *= 2.0
            else:
                # 弱点が小さい場合、応用問題の重みを上げる
                if difficulty in ['advanced', '応用', 'expert', '上級']:
                    base_weight *= 1.5
            
            weighted_questions.append((question, base_weight))
        
        # 重み付き選択
        selected = []
        available = weighted_questions.copy()
        
        for _ in range(count):
            if not available:
                break
                
            weights = [w for _, w in available]
            total_weight = sum(weights)
            
            if total_weight == 0:
                selected.append(available.pop(0)[0])
                continue
            
            # 累積確率による選択
            rand_val = random.random() * total_weight
            cumulative = 0
            
            for i, (question, weight) in enumerate(available):
                cumulative += weight
                if rand_val <= cumulative:
                    selected.append(question)
                    available.pop(i)
                    break
        
        return selected
    
    def _balance_difficulty_distribution(self, questions: List[Dict], count: int,
                                       preference: str) -> List[Dict]:
        """難易度分布のバランス調整"""
        if preference == 'basic':
            basic_ratio, standard_ratio, advanced_ratio = 0.7, 0.3, 0.0
        elif preference == 'advanced':
            basic_ratio, standard_ratio, advanced_ratio = 0.0, 0.4, 0.6
        else:  # mixed
            basic_ratio, standard_ratio, advanced_ratio = 0.3, 0.4, 0.3
        
        # 難易度別に問題を分類
        basic_questions = [
            q for q in questions 
            if q.get('difficulty', '標準') in ['basic', '基本']
        ]
        standard_questions = [
            q for q in questions 
            if q.get('difficulty', '標準') in ['standard', '標準']
        ]
        advanced_questions = [
            q for q in questions 
            if q.get('difficulty', '標準') in ['advanced', '応用', 'expert', '上級']
        ]
        
        # 各難易度の問題数を計算
        basic_count = int(count * basic_ratio)
        standard_count = int(count * standard_ratio)
        advanced_count = count - basic_count - standard_count
        
        selected = []
        
        # 各難易度から選択
        if basic_questions:
            selected.extend(random.sample(
                basic_questions, 
                min(basic_count, len(basic_questions))
            ))
        
        if standard_questions:
            selected.extend(random.sample(
                standard_questions,
                min(standard_count, len(standard_questions))
            ))
        
        if advanced_questions:
            selected.extend(random.sample(
                advanced_questions,
                min(advanced_count, len(advanced_questions))
            ))
        
        # 不足分を補完
        while len(selected) < count and len(selected) < len(questions):
            remaining = [q for q in questions if q not in selected]
            if remaining:
                selected.append(random.choice(remaining))
            else:
                break
        
        return selected
    
    def _select_low_accuracy_questions(self, user_session: Dict, all_questions: List[Dict],
                                     count: int) -> List[Dict]:
        """正答率が低い問題の再選択"""
        history = user_session.get('history', [])
        
        # 問題別正答率計算
        question_stats = {}
        for entry in history:
            qid = entry.get('id')
            if qid not in question_stats:
                question_stats[qid] = {'correct': 0, 'total': 0}
            
            question_stats[qid]['total'] += 1
            if entry.get('is_correct', False):
                question_stats[qid]['correct'] += 1
        
        # 正答率の低い問題を特定
        low_accuracy_questions = []
        for question in all_questions:
            qid = question.get('id')
            if qid in question_stats:
                stats = question_stats[qid]
                accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                if accuracy < 0.7 and stats['total'] >= 2:  # 70%未満かつ2回以上回答
                    low_accuracy_questions.append((question, accuracy))
        
        # 正答率の低い順にソート
        low_accuracy_questions.sort(key=lambda x: x[1])
        
        return [q[0] for q in low_accuracy_questions[:count]]
    
    def _record_session_plan(self, user_session: Dict, plan_info: Dict):
        """セッションプランの記録"""
        if 'adaptive_sessions' not in user_session:
            user_session['adaptive_sessions'] = []
        
        session_record = {
            'timestamp': datetime.now().isoformat(),
            'plan': plan_info
        }
        
        user_session['adaptive_sessions'].append(session_record)
        
        # 最新10セッションのみ保持
        user_session['adaptive_sessions'] = user_session['adaptive_sessions'][-10:]
    
    def get_learning_mode_recommendation(self, user_session: Dict, ai_analysis: Dict) -> str:
        """学習モードの推奨"""
        weak_areas = ai_analysis.get('weak_areas', {})
        confidence = ai_analysis.get('confidence_score', 0.5)
        
        if confidence < 0.5:
            return 'foundation'  # データ不足時は基礎固め
        
        # 弱点の数と深刻度を評価
        high_priority_weaknesses = [
            area for area, info in weak_areas.items()
            if info.get('priority', 0) > 0.6
        ]
        
        if len(high_priority_weaknesses) >= 2:
            return 'foundation'  # 複数の深刻な弱点がある場合
        elif len(high_priority_weaknesses) == 1:
            return 'balanced'  # 1つの弱点がある場合
        elif weak_areas:
            return 'challenge'  # 軽微な弱点のみの場合
        else:
            return 'review'  # 弱点がない場合は復習メイン
    
    def calculate_session_effectiveness(self, user_session: Dict, session_results: List[Dict]) -> Dict[str, Any]:
        """セッションの効果測定"""
        if not session_results:
            return {}
        
        total_questions = len(session_results)
        correct_answers = sum(1 for result in session_results if result.get('is_correct', False))
        accuracy = correct_answers / total_questions
        
        # 弱点エリアの改善度
        weak_area_improvements = self._calculate_weak_area_improvement(session_results)
        
        # 学習効率（時間あたりの正答数）
        total_time = sum(result.get('elapsed', 0) for result in session_results)
        efficiency = correct_answers / (total_time / 60) if total_time > 0 else 0  # 正答数/分
        
        return {
            'accuracy': accuracy,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'efficiency': efficiency,
            'weak_area_improvements': weak_area_improvements,
            'recommendation': self._generate_session_feedback(accuracy, efficiency, weak_area_improvements)
        }
    
    def _calculate_weak_area_improvement(self, session_results: List[Dict]) -> Dict[str, float]:
        """弱点エリアの改善度計算"""
        category_performance = {}
        
        for result in session_results:
            category = result.get('category', '不明')
            if category not in category_performance:
                category_performance[category] = {'correct': 0, 'total': 0}
            
            category_performance[category]['total'] += 1
            if result.get('is_correct', False):
                category_performance[category]['correct'] += 1
        
        improvements = {}
        for category, perf in category_performance.items():
            if perf['total'] > 0:
                improvements[category] = perf['correct'] / perf['total']
        
        return improvements
    
    def _generate_session_feedback(self, accuracy: float, efficiency: float, 
                                 improvements: Dict[str, float]) -> str:
        """セッションフィードバックの生成"""
        if accuracy >= 0.8:
            feedback = "素晴らしい成績です！"
        elif accuracy >= 0.6:
            feedback = "良いペースで進歩しています。"
        else:
            feedback = "基礎をしっかり固めましょう。"
        
        if efficiency > 1.0:  # 1問/分以上
            feedback += " 回答速度も適切です。"
        elif efficiency < 0.5:
            feedback += " もう少し集中して取り組みましょう。"
        
        return feedback

# グローバルインスタンス
adaptive_engine = AdaptiveLearningEngine()