"""
RCCM学習アプリ - 試験シミュレーションエンジン
本格的な試験環境を再現し、実際の試験に近い体験を提供
"""

import random
import math
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ExamSimulator:
    """試験シミュレーションエンジン"""
    
    def __init__(self):
        # RCCM試験の実際の設定に基づく
        self.exam_configs = {
            'standard': {
                'name': '標準模擬試験',
                'total_questions': 40,
                'time_limit_minutes': 150,  # 2時間30分
                'passing_score': 0.6,  # 60%
                'category_distribution': {
                    'コンクリート': 12,
                    '構造': 10,
                    '施工': 10,
                    '維持管理': 8
                },
                'difficulty_distribution': {
                    '基本': 0.3,
                    '標準': 0.5,
                    '応用': 0.2
                }
            },
            'full': {
                'name': '本試験完全再現',
                'total_questions': 60,
                'time_limit_minutes': 180,  # 3時間
                'passing_score': 0.65,  # 65%
                'category_distribution': {
                    'コンクリート': 18,
                    '構造': 15,
                    '施工': 15,
                    '維持管理': 12
                },
                'difficulty_distribution': {
                    '基本': 0.25,
                    '標準': 0.5,
                    '応用': 0.25
                }
            },
            'quick': {
                'name': 'クイック模擬試験',
                'total_questions': 20,
                'time_limit_minutes': 60,  # 1時間
                'passing_score': 0.6,
                'category_distribution': {
                    'コンクリート': 6,
                    '構造': 5,
                    '施工': 5,
                    '維持管理': 4
                },
                'difficulty_distribution': {
                    '基本': 0.4,
                    '標準': 0.4,
                    '応用': 0.2
                }
            }
        }
        
        # 試験環境設定
        self.exam_features = {
            'randomize_questions': True,
            'randomize_options': True,
            'no_review_during_exam': True,
            'auto_submit_on_timeout': True,
            'show_remaining_time': True,
            'warn_before_submit': True,
            'prevent_browser_back': True
        }
    
    def generate_exam_session(self, all_questions: List[Dict], 
                            exam_type: str = 'standard',
                            user_session: Dict = None) -> Dict[str, Any]:
        """試験セッションの生成"""
        
        config = self.exam_configs.get(exam_type, self.exam_configs['standard'])
        
        # 試験問題の選択
        exam_questions = self._select_exam_questions(all_questions, config, user_session)
        
        # 問題をランダム化
        if self.exam_features['randomize_questions']:
            random.shuffle(exam_questions)
        
        # 選択肢をランダム化
        if self.exam_features['randomize_options']:
            exam_questions = self._randomize_question_options(exam_questions)
        
        # 試験セッションデータ作成
        exam_session = {
            'exam_id': self._generate_exam_id(),
            'exam_type': exam_type,
            'config': config,
            'questions': exam_questions,
            'start_time': datetime.now().isoformat(),
            'time_limit_minutes': config['time_limit_minutes'],
            'current_question': 0,
            'answers': {},
            'flagged_questions': [],
            'status': 'in_progress',
            'warnings_given': [],
            'browser_activity': []
        }
        
        logger.info(f"試験セッション生成完了: {exam_type}, {len(exam_questions)}問")
        
        return exam_session
    
    def _select_exam_questions(self, all_questions: List[Dict], 
                             config: Dict, user_session: Dict = None) -> List[Dict]:
        """試験問題の選択"""
        
        selected_questions = []
        
        # カテゴリ別に問題を選択
        for category, count in config['category_distribution'].items():
            category_questions = [
                q for q in all_questions 
                if q.get('category') == category
            ]
            
            if len(category_questions) < count:
                logger.warning(f"カテゴリ '{category}' の問題数が不足: {len(category_questions)}/{count}")
                selected_questions.extend(category_questions)
            else:
                # 難易度分布を考慮した選択
                difficulty_selected = self._select_by_difficulty(
                    category_questions, count, config['difficulty_distribution']
                )
                selected_questions.extend(difficulty_selected)
        
        # 不足分を補完
        total_needed = config['total_questions']
        if len(selected_questions) < total_needed:
            remaining_count = total_needed - len(selected_questions)
            selected_ids = {q.get('id') for q in selected_questions}
            
            remaining_questions = [
                q for q in all_questions 
                if q.get('id') not in selected_ids
            ]
            
            if remaining_questions:
                additional = random.sample(
                    remaining_questions, 
                    min(remaining_count, len(remaining_questions))
                )
                selected_questions.extend(additional)
        
        return selected_questions[:total_needed]
    
    def _select_by_difficulty(self, questions: List[Dict], count: int, 
                            difficulty_dist: Dict[str, float]) -> List[Dict]:
        """難易度分布に基づく問題選択"""
        
        # 難易度別に分類
        difficulty_groups = defaultdict(list)
        for question in questions:
            difficulty = question.get('difficulty', '標準')
            difficulty_groups[difficulty].append(question)
        
        selected = []
        
        # 各難易度から指定比率で選択
        for difficulty, ratio in difficulty_dist.items():
            needed_count = int(count * ratio)
            available = difficulty_groups.get(difficulty, [])
            
            if available:
                selected_count = min(needed_count, len(available))
                selected.extend(random.sample(available, selected_count))
        
        # 不足分を他の難易度から補完
        while len(selected) < count:
            all_remaining = [
                q for q in questions 
                if q not in selected
            ]
            
            if not all_remaining:
                break
                
            selected.append(random.choice(all_remaining))
        
        return selected[:count]
    
    def _randomize_question_options(self, questions: List[Dict]) -> List[Dict]:
        """選択肢の順序をランダム化"""
        
        randomized_questions = []
        
        for question in questions:
            # 元の問題をコピー
            randomized_q = question.copy()
            
            # 選択肢とその正解を取得
            options = {
                'A': question.get('option_a', ''),
                'B': question.get('option_b', ''),
                'C': question.get('option_c', ''),
                'D': question.get('option_d', '')
            }
            
            correct_answer = question.get('correct_answer', 'A')
            correct_text = options[correct_answer]
            
            # 選択肢をシャッフル
            option_texts = list(options.values())
            random.shuffle(option_texts)
            
            # 新しい選択肢を設定
            new_options = ['A', 'B', 'C', 'D']
            randomized_q['option_a'] = option_texts[0]
            randomized_q['option_b'] = option_texts[1]
            randomized_q['option_c'] = option_texts[2]
            randomized_q['option_d'] = option_texts[3]
            
            # 新しい正解を特定
            for i, text in enumerate(option_texts):
                if text == correct_text:
                    randomized_q['correct_answer'] = new_options[i]
                    break
            
            # 元の選択肢順序を記録（デバッグ用）
            randomized_q['original_mapping'] = {
                correct_answer: randomized_q['correct_answer']
            }
            
            randomized_questions.append(randomized_q)
        
        return randomized_questions
    
    def _generate_exam_id(self) -> str:
        """試験IDの生成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        return f"EXAM_{timestamp}_{random_suffix}"
    
    def submit_exam_answer(self, exam_session: Dict, question_index: int, 
                          answer: str, time_spent: float) -> Dict[str, Any]:
        """試験回答の提出"""
        
        if exam_session['status'] != 'in_progress':
            return {'success': False, 'error': '試験は既に終了しています'}
        
        # 回答を記録
        exam_session['answers'][question_index] = {
            'answer': answer,
            'time_spent': time_spent,
            'timestamp': datetime.now().isoformat()
        }
        
        # 次の問題に進む
        exam_session['current_question'] = question_index + 1
        
        # 試験終了判定
        total_questions = len(exam_session['questions'])
        if exam_session['current_question'] >= total_questions:
            return self.finish_exam(exam_session)
        
        return {
            'success': True,
            'next_question': exam_session['current_question'],
            'remaining_questions': total_questions - exam_session['current_question']
        }
    
    def flag_question(self, exam_session: Dict, question_index: int) -> bool:
        """問題のフラグ設定"""
        if question_index not in exam_session['flagged_questions']:
            exam_session['flagged_questions'].append(question_index)
        return True
    
    def unflag_question(self, exam_session: Dict, question_index: int) -> bool:
        """問題のフラグ解除"""
        if question_index in exam_session['flagged_questions']:
            exam_session['flagged_questions'].remove(question_index)
        return True
    
    def get_time_remaining(self, exam_session: Dict) -> int:
        """残り時間の計算（分）"""
        start_time = datetime.fromisoformat(exam_session['start_time'])
        elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
        remaining_minutes = exam_session['time_limit_minutes'] - elapsed_minutes
        return max(0, int(remaining_minutes))
    
    def should_give_time_warning(self, exam_session: Dict) -> Optional[str]:
        """時間警告の判定"""
        remaining_minutes = self.get_time_remaining(exam_session)
        warnings_given = exam_session['warnings_given']
        
        if remaining_minutes <= 10 and '10min' not in warnings_given:
            exam_session['warnings_given'].append('10min')
            return '残り時間10分です'
        elif remaining_minutes <= 30 and '30min' not in warnings_given:
            exam_session['warnings_given'].append('30min')
            return '残り時間30分です'
        elif remaining_minutes <= 60 and '60min' not in warnings_given:
            exam_session['warnings_given'].append('60min')
            return '残り時間1時間です'
        
        return None
    
    def auto_submit_check(self, exam_session: Dict) -> bool:
        """自動提出チェック"""
        return self.get_time_remaining(exam_session) <= 0
    
    def finish_exam(self, exam_session: Dict) -> Dict[str, Any]:
        """試験終了処理"""
        
        exam_session['status'] = 'completed'
        exam_session['end_time'] = datetime.now().isoformat()
        
        # 採点実行
        results = self.score_exam(exam_session)
        exam_session['results'] = results
        
        logger.info(f"試験終了: {exam_session['exam_id']}, スコア: {results['score']:.1%}")
        
        return {
            'success': True,
            'exam_completed': True,
            'results': results
        }
    
    def score_exam(self, exam_session: Dict) -> Dict[str, Any]:
        """試験採点"""
        
        questions = exam_session['questions']
        answers = exam_session['answers']
        config = exam_session['config']
        
        # 基本採点
        total_questions = len(questions)
        correct_answers = 0
        category_scores = defaultdict(lambda: {'correct': 0, 'total': 0})
        difficulty_scores = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        detailed_results = []
        
        for i, question in enumerate(questions):
            user_answer = answers.get(i, {}).get('answer', '')
            correct_answer = question.get('correct_answer', '')
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_answers += 1
            
            # カテゴリ別スコア
            category = question.get('category', '不明')
            category_scores[category]['total'] += 1
            if is_correct:
                category_scores[category]['correct'] += 1
            
            # 難易度別スコア
            difficulty = question.get('difficulty', '標準')
            difficulty_scores[difficulty]['total'] += 1
            if is_correct:
                difficulty_scores[difficulty]['correct'] += 1
            
            # 詳細結果
            detailed_results.append({
                'question_id': question.get('id'),
                'question_number': i + 1,
                'category': category,
                'difficulty': difficulty,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'time_spent': answers.get(i, {}).get('time_spent', 0),
                'question_text': question.get('question', '')[:100] + '...'
            })
        
        # 総合スコア計算
        score = correct_answers / total_questions if total_questions > 0 else 0
        passed = score >= config['passing_score']
        
        # 時間分析
        start_time = datetime.fromisoformat(exam_session['start_time'])
        end_time = datetime.fromisoformat(exam_session['end_time'])
        total_time_minutes = (end_time - start_time).total_seconds() / 60
        
        # 平均回答時間
        total_answer_time = sum(
            answer_data.get('time_spent', 0) 
            for answer_data in answers.values()
        )
        avg_time_per_question = total_answer_time / len(answers) if answers else 0
        
        return {
            'exam_id': exam_session['exam_id'],
            'exam_type': exam_session['exam_type'],
            'score': score,
            'percentage': score * 100,
            'passed': passed,
            'passing_score': config['passing_score'] * 100,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'incorrect_answers': total_questions - correct_answers,
            'category_scores': dict(category_scores),
            'difficulty_scores': dict(difficulty_scores),
            'total_time_minutes': total_time_minutes,
            'avg_time_per_question': avg_time_per_question,
            'time_efficiency': self._calculate_time_efficiency(total_time_minutes, config['time_limit_minutes']),
            'detailed_results': detailed_results,
            'exam_date': exam_session['start_time'][:10],
            'recommendations': self._generate_exam_recommendations(category_scores, difficulty_scores, score)
        }
    
    def _calculate_time_efficiency(self, used_time: float, time_limit: float) -> str:
        """時間効率の計算"""
        if time_limit <= 0:
            return 'unknown'
        
        efficiency_ratio = used_time / time_limit
        
        if efficiency_ratio < 0.7:
            return 'excellent'  # 効率的
        elif efficiency_ratio < 0.9:
            return 'good'       # 良好
        elif efficiency_ratio < 1.0:
            return 'adequate'   # 適切
        else:
            return 'overtime'   # 時間超過
    
    def _generate_exam_recommendations(self, category_scores: Dict, 
                                     difficulty_scores: Dict, 
                                     overall_score: float) -> List[str]:
        """試験結果に基づく推奨事項"""
        recommendations = []
        
        # 全体スコアに基づく推奨
        if overall_score >= 0.8:
            recommendations.append("素晴らしい成績です！継続的な学習で更なる向上を目指しましょう。")
        elif overall_score >= 0.6:
            recommendations.append("合格レベルに達しています。弱点分野を強化して確実な合格を目指しましょう。")
        else:
            recommendations.append("基礎からの復習が必要です。重点分野を集中的に学習しましょう。")
        
        # カテゴリ別推奨
        weak_categories = []
        for category, scores in category_scores.items():
            if scores['total'] > 0:
                accuracy = scores['correct'] / scores['total']
                if accuracy < 0.6:
                    weak_categories.append(category)
        
        if weak_categories:
            recommendations.append(f"弱点分野: {', '.join(weak_categories)}の学習を強化してください。")
        
        # 難易度別推奨
        for difficulty, scores in difficulty_scores.items():
            if scores['total'] > 0:
                accuracy = scores['correct'] / scores['total']
                if accuracy < 0.5 and difficulty == '基本':
                    recommendations.append("基本問題の正答率が低いです。基礎知識の復習を重点的に行ってください。")
                elif accuracy < 0.4 and difficulty == '応用':
                    recommendations.append("応用問題への対応力向上が必要です。実践的な問題演習を増やしてください。")
        
        return recommendations
    
    def get_exam_summary(self, exam_session: Dict) -> Dict[str, Any]:
        """試験サマリーの取得"""
        return {
            'exam_id': exam_session['exam_id'],
            'exam_type': exam_session['exam_type'],
            'status': exam_session['status'],
            'progress': {
                'current_question': exam_session['current_question'],
                'total_questions': len(exam_session['questions']),
                'answered_questions': len(exam_session['answers']),
                'flagged_questions': len(exam_session['flagged_questions'])
            },
            'time_info': {
                'remaining_minutes': self.get_time_remaining(exam_session),
                'time_limit_minutes': exam_session['time_limit_minutes']
            }
        }

# グローバルインスタンス
exam_simulator = ExamSimulator()