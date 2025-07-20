"""
RCCM学習アプリ - アダプティブ学習システム（部門別対応版）
AI分析結果に基づいて個人に最適化された問題選択と学習プランを提供
RCCM 12部門別の特化学習アルゴリズムを実装
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

# RCCM設定をインポート
from config import RCCMConfig
from difficulty_controller import difficulty_controller

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
        
        # 学習モード定義（RCCM部門対応版）
        self.learning_modes = {
            'foundation': {
                'weak_area_ratio': 0.8,
                'new_question_ratio': 0.2,
                'review_ratio': 0.0,
                'difficulty_preference': 'basic',
                'department_focus': True,
                'basic_specialist_ratio': 0.7  # 基礎重視
            },
            'balanced': {
                'weak_area_ratio': 0.5,
                'new_question_ratio': 0.3,
                'review_ratio': 0.2,
                'difficulty_preference': 'mixed',
                'department_focus': False,
                'basic_specialist_ratio': 0.5  # バランス
            },
            'specialist_focused': {
                'weak_area_ratio': 0.4,
                'new_question_ratio': 0.4,
                'review_ratio': 0.2,
                'difficulty_preference': 'advanced',
                'department_focus': True,
                'basic_specialist_ratio': 0.3  # 専門重視
            },
            'department_mastery': {
                'weak_area_ratio': 0.6,
                'new_question_ratio': 0.3,
                'review_ratio': 0.1,
                'difficulty_preference': 'mixed',
                'department_focus': True,
                'basic_specialist_ratio': 0.4  # 部門特化
            },
            'exam_preparation': {
                'weak_area_ratio': 0.3,
                'new_question_ratio': 0.2,
                'review_ratio': 0.5,
                'difficulty_preference': 'exam_level',
                'department_focus': True,
                'basic_specialist_ratio': 0.45  # 試験準備
            },
            'challenge': {
                'weak_area_ratio': 0.3,
                'new_question_ratio': 0.4,
                'review_ratio': 0.3,
                'difficulty_preference': 'advanced',
                'department_focus': False,
                'basic_specialist_ratio': 0.3
            },
            'basic_to_specialist': {
                'weak_area_ratio': 0.4,
                'new_question_ratio': 0.4,
                'review_ratio': 0.2,
                'difficulty_preference': 'progressive',
                'department_focus': True,
                'basic_specialist_ratio': 'adaptive',  # 動的調整
                'foundation_threshold': 0.7,  # 基礎理解の閾値
                'progression_strategy': 'mastery_based'  # 習熟度ベース進行
            },
            'foundation_reinforced': {
                'weak_area_ratio': 0.5,
                'new_question_ratio': 0.3,
                'review_ratio': 0.2,
                'difficulty_preference': 'foundation_first',
                'department_focus': True,
                'basic_specialist_ratio': 'foundation_priority',  # 基礎優先
                'reinforcement_ratio': 0.6,  # 基礎強化の比率
                'bridge_learning': True  # 橋渡し学習
            }
        }
        
        # 部門別学習特性
        self.department_learning_patterns = {
            'road': {
                'foundation_categories': ['構造力学', 'コンクリート', '土質及び基礎'],
                'application_categories': ['道路設計', '舗装工学', '道路維持管理'],
                'learning_sequence': ['基礎理論', '設計基準', '施工技術', '維持管理'],
                'difficulty_progression': 'gradual'
            },
            'civil_planning': {
                'foundation_categories': ['水理学', '河川工学'],
                'application_categories': ['砂防工学', '海岸工学', '環境対策'],
                'learning_sequence': ['水理基礎', '河川計画', '災害対策', '環境配慮'],
                'difficulty_progression': 'steep'
            },
            'construction_env': {
                'foundation_categories': ['環境基準', '法規制'],
                'application_categories': ['環境アセスメント', '環境保全技術'],
                'learning_sequence': ['基準理解', '評価手法', '対策技術', '実務応用'],
                'difficulty_progression': 'moderate'
            },
            'comprehensive': {
                'foundation_categories': ['品質管理', 'プロジェクト管理'],
                'application_categories': ['総合技術監理', 'リスク管理'],
                'learning_sequence': ['管理基礎', '統合技術', '監理実務', '意思決定'],
                'difficulty_progression': 'complex'
            },
            'port_airport': {
                'foundation_categories': ['構造力学', '地盤工学'],
                'application_categories': ['港湾工学', '空港工学', '海洋工学'],
                'learning_sequence': ['基礎構造', '設計基準', '施工技術', '維持管理'],
                'difficulty_progression': 'moderate'
            },
            'railway': {
                'foundation_categories': ['軌道工学', '構造力学'],
                'application_categories': ['鉄道設計', '信号システム', '電気設備'],
                'learning_sequence': ['軌道基礎', '設計基準', '信号制御', '運行管理'],
                'difficulty_progression': 'gradual'
            },
            'urban_planning': {
                'foundation_categories': ['都市計画', '法規制'],
                'application_categories': ['まちづくり', '景観設計', '交通計画'],
                'learning_sequence': ['計画基礎', '法制度', '設計技術', '事業実施'],
                'difficulty_progression': 'moderate'
            },
            'construction_mgmt': {
                'foundation_categories': ['建設管理', '工程管理'],
                'application_categories': ['現場管理', 'コスト管理', '安全管理'],
                'learning_sequence': ['管理基礎', '計画立案', '現場実践', '改善活動'],
                'difficulty_progression': 'gradual'
            },
            'power_civil': {
                'foundation_categories': ['電力土木', '水理学'],
                'application_categories': ['発電設備', 'ダム工学', '送電線路'],
                'learning_sequence': ['電力基礎', '水力発電', 'ダム設計', '送電技術'],
                'difficulty_progression': 'steep'
            },
            'forestry': {
                'foundation_categories': ['森林工学', '水文学'],
                'application_categories': ['森林土木', '治山工学', '林道工学'],
                'learning_sequence': ['森林基礎', '治山技術', '林道設計', '環境保全'],
                'difficulty_progression': 'moderate'
            },
            'fisheries': {
                'foundation_categories': ['水産土木', '海洋工学'],
                'application_categories': ['漁港工学', '栽培漁業施設', '海岸保全'],
                'learning_sequence': ['水産基礎', '漁港設計', '施設計画', '環境配慮'],
                'difficulty_progression': 'moderate'
            },
            'agriculture': {
                'foundation_categories': ['農業土木', '水利工学'],
                'application_categories': ['灌漑排水', '農地整備', '農村計画'],
                'learning_sequence': ['農業基礎', '水利技術', '農地設計', '地域計画'],
                'difficulty_progression': 'gradual'
            }
        }
    
    def get_adaptive_questions(self, user_session: Dict, all_questions: List[Dict], 
                             ai_analysis: Dict, session_size: int = 10,
                             learning_mode: str = 'balanced', department: str = None) -> List[Dict]:
        """AI分析に基づくアダプティブ問題選択（部門別対応版）"""
        
        # None チェック
        if user_session.get('history') is None:
            user_session['history'] = []
        
        mode_config = self.learning_modes.get(learning_mode, self.learning_modes['balanced'])
        
        # 学習者レベル評価（動的難易度制御）
        learner_assessment = difficulty_controller.assess_learner_level(user_session, department)
        logger.info(f"学習者レベル評価: {learner_assessment['level_name']} (信頼度: {learner_assessment['confidence']:.2f})")
        
        # 連携学習モードの特別処理
        if learning_mode in ['basic_to_specialist', 'foundation_reinforced']:
            return self._get_integrated_learning_questions(
                user_session, all_questions, ai_analysis, session_size, mode_config, department
            )
        
        # 部門フィルタリング
        if department and mode_config.get('department_focus', False):
            filtered_questions = [q for q in all_questions if q.get('department') == department]
            logger.info(f"部門別適応学習: {department}, 対象問題数: {len(filtered_questions)}")
        else:
            filtered_questions = all_questions
        
        # 動的難易度調整（学習者レベルに基づく問題フィルタリング）
        difficulty_adjusted_questions = difficulty_controller.adjust_question_difficulty(
            filtered_questions, learner_assessment, len(filtered_questions)
        )
        logger.info(f"動的難易度調整: {len(filtered_questions)}問 → {len(difficulty_adjusted_questions)}問")
        
        # 調整後の問題を使用
        filtered_questions = difficulty_adjusted_questions
        
        # 各カテゴリの問題数計算
        weak_area_count = int(session_size * mode_config['weak_area_ratio'])
        new_question_count = int(session_size * mode_config['new_question_ratio'])
        review_count = session_size - weak_area_count - new_question_count
        
        selected_questions = []
        
        # 1. 弱点エリアの問題（部門特化）
        weak_questions = self._select_weak_area_questions_advanced(
            user_session, filtered_questions, ai_analysis, weak_area_count, mode_config, department
        )
        selected_questions.extend(weak_questions)
        
        # 2. 復習問題（SRS + 部門考慮）
        review_questions = self._select_review_questions_advanced(
            user_session, filtered_questions, review_count, department
        )
        selected_questions.extend(review_questions)
        
        # 3. 新規問題（部門特有の学習順序考慮）
        new_questions = self._select_new_questions_advanced(
            user_session, filtered_questions, selected_questions, 
            new_question_count, mode_config, department
        )
        selected_questions.extend(new_questions)
        
        # 4. 部門特有の学習順序で並び替え
        if department and mode_config.get('department_focus', False):
            selected_questions = self._apply_department_learning_sequence(
                selected_questions, department
            )
        else:
            # 4. 問題をシャッフル（学習効果向上のため）
            random.shuffle(selected_questions)
        
        # 5. セッション情報を記録
        self._record_session_plan(user_session, {
            'mode': learning_mode,
            'department': department,
            'weak_area_questions': len(weak_questions),
            'review_questions': len(review_questions),
            'new_questions': len(new_questions),
            'total_questions': len(selected_questions),
            'department_focused': bool(department and mode_config.get('department_focus', False)),
            'learner_level': learner_assessment['overall_level'],
            'difficulty_confidence': learner_assessment['confidence']
        })
        
        # 6. 動的セッション設定を適用
        dynamic_config = difficulty_controller.get_dynamic_session_config(learner_assessment)
        user_session['dynamic_session_config'] = dynamic_config
        logger.info(f"動的セッション設定適用: 目標正答率{dynamic_config['target_accuracy']:.0%}, 時間係数{dynamic_config['time_limit_multiplier']:.1f}")
        
        logger.info(f"アダプティブ問題選択完了: 弱点{len(weak_questions)}問, 復習{len(review_questions)}問, 新規{len(new_questions)}問")
        
        return selected_questions[:session_size]
    
    def _select_weak_area_questions_advanced(self, user_session: Dict, all_questions: List[Dict],
                                           ai_analysis: Dict, count: int, mode_config: Dict, department: str = None) -> List[Dict]:
        """高度な弱点エリアからの問題選択（部門別対応版）"""
        if count <= 0:
            return []
        
        weak_areas = ai_analysis.get('weak_areas', {})
        if not weak_areas:
            return []
        
        # 部門特有の弱点パターンを適用
        if department and department in self.department_learning_patterns:
            dept_pattern = self.department_learning_patterns[department]
            # 基礎カテゴリと応用カテゴリの優先度調整
            prioritized_areas = self._prioritize_by_department_pattern(weak_areas, dept_pattern)
        else:
            prioritized_areas = sorted(
                weak_areas.items(),
                key=lambda x: x[1].get('priority', 0),
                reverse=True
            )
        
        selected_questions = []
        questions_per_area = max(1, count // max(len(prioritized_areas), 1))
        
        for category, weakness_info in prioritized_areas:
            if len(selected_questions) >= count:
                break
                
            # カテゴリと部門の問題を取得
            category_questions = [
                q for q in all_questions 
                if q.get('category') == category and 
                (not department or q.get('department') == department)
            ]
            
            if not category_questions:
                continue
            
            # 部門特有の難易度調整
            filtered_questions = self._apply_department_difficulty_filter(
                category_questions, mode_config, department, weakness_info
            )
            
            # 既回答問題の除外
            available_questions = self._filter_unasked_questions(
                user_session, filtered_questions
            )
            
            # 部門学習順序を考慮した選択
            area_questions = self._select_by_learning_sequence(
                available_questions, 
                min(questions_per_area, len(available_questions)),
                department, category, weakness_info
            )
            
            selected_questions.extend(area_questions)
        
        return selected_questions
    
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
    
    def _select_review_questions_advanced(self, user_session: Dict, all_questions: List[Dict],
                                        count: int, department: str = None) -> List[Dict]:
        """高度なSRS復習問題の選択（部門別対応版）"""
        if count <= 0:
            return []
        
        # 既存のSRS機能を活用
        try:
            from app import get_due_questions
            due_questions = get_due_questions(user_session, all_questions)
        except (ImportError, AttributeError, ModuleNotFoundError) as e:
            logger.warning(f"SRS機能のインポートエラー: {e}")
            due_questions = []
            
            # 部門フィルタリング
            if department:
                due_questions = [
                    item for item in due_questions 
                    if item['question'].get('department') == department
                ]
            
            # 部門特有の復習優先度でソート
            if department and department in self.department_learning_patterns:
                due_questions = self._sort_by_department_review_priority(
                    due_questions, department
                )
            else:
                # 通常の期限切れ日数順
                due_questions.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
            
            # 必要数だけ選択
            selected_reviews = [
                item['question'] for item in due_questions[:count]
            ]
            
            return selected_reviews
        except ImportError:
            # テスト環境での代替実装
            return self._get_due_questions_standalone_advanced(
                user_session, all_questions, count, department
            )
    
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
                if not isinstance(data, dict) or 'next_review' not in data:
                    continue
                next_review = datetime.fromisoformat(data['next_review']).date()
                if next_review <= today:
                    question = next((q for q in all_questions if str(q.get('id', 0)) == question_id), None)
                    if question:
                        days_overdue = (today - next_review).days
                        due_questions.append({
                            'question': question,
                            'days_overdue': days_overdue
                        })
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"SRSデータの日付パースエラー (ID: {question_id}): {e}")
                continue
        
        # 優先度順にソート
        due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return [item['question'] for item in due_questions[:count]]
    
    def _select_new_questions_advanced(self, user_session: Dict, all_questions: List[Dict],
                                     already_selected: List[Dict], count: int, 
                                     mode_config: Dict, department: str = None) -> List[Dict]:
        """高度な新規問題の選択（部門別学習順序対応版）"""
        if count <= 0:
            return []
        
        # 既に選択された問題のIDを取得
        selected_ids = {q.get('id') for q in already_selected}
        
        # 未回答の問題を取得（部門フィルタ適用）
        answered_ids = {entry.get('id') for entry in user_session.get('history', [])}
        
        available_questions = [
            q for q in all_questions
            if q.get('id') not in answered_ids and 
               q.get('id') not in selected_ids and
               (not department or q.get('department') == department)
        ]
        
        if not available_questions:
            # 全問題回答済みの場合、正答率が低い問題を再選択
            return self._select_low_accuracy_questions_advanced(
                user_session, all_questions, count, department
            )
        
        # 部門特有の学習順序を適用
        if department and department in self.department_learning_patterns:
            sequenced_questions = self._apply_department_learning_sequence_to_new(
                available_questions, department, user_session
            )
        else:
            sequenced_questions = available_questions
        
        # 4-1基礎と4-2専門のバランス調整
        basic_specialist_ratio = mode_config.get('basic_specialist_ratio', 0.5)
        balanced_questions = self._balance_basic_specialist_distribution(
            sequenced_questions, count, basic_specialist_ratio
        )
        
        return balanced_questions
    
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
    
    def _apply_department_learning_sequence(self, questions: List[Dict], department: str) -> List[Dict]:
        """部門特有の学習順序で問題を並び替え"""
        if department not in self.department_learning_patterns:
            return questions
        
        dept_pattern = self.department_learning_patterns[department]
        learning_sequence = dept_pattern.get('learning_sequence', [])
        
        # 学習順序に基づいて問題を分類
        sequenced_groups = []
        unsequenced = []
        
        for seq_item in learning_sequence:
            group = [q for q in questions if self._matches_sequence_item(q, seq_item)]
            if group:
                sequenced_groups.append(group)
        
        # 順序に該当しない問題
        sequenced_ids = {q.get('id') for group in sequenced_groups for q in group}
        unsequenced = [q for q in questions if q.get('id') not in sequenced_ids]
        
        # 順序通りに配置
        result = []
        for group in sequenced_groups:
            result.extend(group)
        result.extend(unsequenced)
        
        return result
    
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
    
    # === 新しい部門別学習メソッド ===
    
    def _prioritize_by_department_pattern(self, weak_areas: Dict, dept_pattern: Dict) -> List[Tuple]:
        """部門パターンに基づく弱点エリアの優先順位付け"""
        foundation_categories = dept_pattern.get('foundation_categories', [])
        application_categories = dept_pattern.get('application_categories', [])
        
        prioritized = []
        
        # 基礎カテゴリを優先
        for category, info in weak_areas.items():
            if category in foundation_categories:
                # 基礎の弱点は優先度を1.5倍に
                adjusted_info = info.copy()
                adjusted_info['priority'] = info.get('priority', 0) * 1.5
                prioritized.append((category, adjusted_info))
        
        # 応用カテゴリ
        for category, info in weak_areas.items():
            if category in application_categories and category not in foundation_categories:
                prioritized.append((category, info))
        
        # その他のカテゴリ
        processed_categories = {cat for cat, _ in prioritized}
        for category, info in weak_areas.items():
            if category not in processed_categories:
                prioritized.append((category, info))
        
        # 優先度でソート
        prioritized.sort(key=lambda x: x[1].get('priority', 0), reverse=True)
        
        return prioritized
    
    def _apply_department_difficulty_filter(self, questions: List[Dict], mode_config: Dict, 
                                          department: str, weakness_info: Dict) -> List[Dict]:
        """部門特有の難易度フィルタリング"""
        preference = mode_config['difficulty_preference']
        weakness_score = weakness_info.get('weakness_score', 0.5)
        
        # 部門別の難易度調整係数
        dept_difficulty_adjustment = {
            'road': 1.0,  # 標準
            'civil_planning': 1.2,  # より難しい
            'construction_env': 1.15,
            'comprehensive': 1.3  # 最高難易度
        }
        
        adjustment = dept_difficulty_adjustment.get(department, 1.0)
        adjusted_weakness = weakness_score * adjustment
        
        # 調整された弱点度に基づく難易度選択
        if adjusted_weakness > 0.8:
            target_difficulties = ['basic', '基本']
        elif adjusted_weakness > 0.6:
            target_difficulties = ['basic', '基本', 'standard', '標準']
        elif adjusted_weakness > 0.4:
            target_difficulties = ['standard', '標準', 'advanced', '応用']
        else:
            target_difficulties = ['advanced', '応用', 'expert', '上級']
        
        if preference == 'basic':
            target_difficulties = ['basic', '基本']
        elif preference == 'advanced':
            target_difficulties = ['advanced', '応用', 'expert', '上級']
        
        filtered = [
            q for q in questions
            if q.get('difficulty', '標準') in target_difficulties
        ]
        
        return filtered if filtered else questions
    
    def _select_by_learning_sequence(self, questions: List[Dict], count: int,
                                   department: str, category: str, weakness_info: Dict) -> List[Dict]:
        """学習順序を考慮した問題選択"""
        if not department or department not in self.department_learning_patterns:
            return self._weighted_random_selection(questions, count, weakness_info)
        
        dept_pattern = self.department_learning_patterns[department]
        learning_sequence = dept_pattern.get('learning_sequence', [])
        
        # カテゴリに対応する学習順序のインデックスを取得
        sequence_priority = 0
        for i, seq_item in enumerate(learning_sequence):
            if self._matches_sequence_item({'category': category}, seq_item):
                sequence_priority = i
                break
        
        # 学習順序の早いものを優先的に選択
        if sequence_priority < len(learning_sequence) // 2:
            # 前半の学習項目：基礎重視
            basic_questions = [q for q in questions if q.get('difficulty', '標準') in ['basic', '基本', 'standard', '標準']]
            if basic_questions:
                return self._weighted_random_selection(basic_questions, count, weakness_info)
        
        return self._weighted_random_selection(questions, count, weakness_info)
    
    def _sort_by_department_review_priority(self, due_questions: List[Dict], department: str) -> List[Dict]:
        """部門特有の復習優先度でソート"""
        if department not in self.department_learning_patterns:
            return due_questions
        
        dept_pattern = self.department_learning_patterns[department]
        foundation_categories = dept_pattern.get('foundation_categories', [])
        
        # 基礎カテゴリの復習を優先
        foundation_reviews = []
        other_reviews = []
        
        for item in due_questions:
            question = item['question']
            if question.get('category') in foundation_categories:
                foundation_reviews.append(item)
            else:
                other_reviews.append(item)
        
        # それぞれを期限切れ日数でソート
        foundation_reviews.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
        other_reviews.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
        
        return foundation_reviews + other_reviews
    
    def _get_due_questions_standalone_advanced(self, user_session: Dict, all_questions: List[Dict], 
                                             count: int, department: str = None) -> List[Dict]:
        """スタンドアロン版の復習問題取得（部門対応版）"""
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
                    if question and (not department or question.get('department') == department):
                        days_overdue = (today - next_review).days
                        due_questions.append({
                            'question': question,
                            'days_overdue': days_overdue
                        })
            except (ValueError, KeyError):
                continue
        
        # 部門特有の優先度でソート
        if department:
            due_questions = self._sort_by_department_review_priority(due_questions, department)
        else:
            due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return [item['question'] for item in due_questions[:count]]
    
    def _select_low_accuracy_questions_advanced(self, user_session: Dict, all_questions: List[Dict],
                                              count: int, department: str = None) -> List[Dict]:
        """正答率が低い問題の再選択（部門対応版）"""
        history = user_session.get('history', [])
        
        # 部門フィルタリング
        if department:
            history = [h for h in history if h.get('department') == department]
        
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
            if (not department or question.get('department') == department) and qid in question_stats:
                stats = question_stats[qid]
                accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                if accuracy < 0.7 and stats['total'] >= 2:
                    low_accuracy_questions.append((question, accuracy))
        
        # 正答率の低い順にソート
        low_accuracy_questions.sort(key=lambda x: x[1])
        
        return [q[0] for q in low_accuracy_questions[:count]]
    
    def _apply_department_learning_sequence_to_new(self, questions: List[Dict], 
                                                 department: str, user_session: Dict) -> List[Dict]:
        """新規問題に部門特有の学習順序を適用"""
        if department not in self.department_learning_patterns:
            return questions
        
        dept_pattern = self.department_learning_patterns[department]
        learning_sequence = dept_pattern.get('learning_sequence', [])
        foundation_categories = dept_pattern.get('foundation_categories', [])
        
        # 学習履歴を分析して現在の学習段階を判定
        history = user_session.get('history', [])
        dept_history = [h for h in history if h.get('department') == department]
        
        # 基礎カテゴリの理解度をチェック
        foundation_mastery = self._check_foundation_mastery(dept_history, foundation_categories)
        
        # 理解度に基づいて推奨順序を決定
        if foundation_mastery < 0.7:  # 基礎が不十分
            # 基礎カテゴリを優先
            foundation_questions = [q for q in questions if q.get('category') in foundation_categories]
            other_questions = [q for q in questions if q.get('category') not in foundation_categories]
            return foundation_questions + other_questions
        else:
            # 学習順序に従って配置
            return self._apply_department_learning_sequence(questions, department)
    
    def _balance_basic_specialist_distribution(self, questions: List[Dict], count: int, 
                                             basic_specialist_ratio: float) -> List[Dict]:
        """4-1基礎と4-2専門の分布バランス調整"""
        basic_questions = [q for q in questions if q.get('question_type') == 'basic']
        specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
        
        basic_count = int(count * basic_specialist_ratio)
        specialist_count = count - basic_count
        
        selected = []
        
        # 基礎問題を選択
        if basic_questions:
            selected.extend(random.sample(
                basic_questions, 
                min(basic_count, len(basic_questions))
            ))
        
        # 専門問題を選択
        if specialist_questions:
            selected.extend(random.sample(
                specialist_questions,
                min(specialist_count, len(specialist_questions))
            ))
        
        # 不足分を補完
        while len(selected) < count and len(selected) < len(questions):
            remaining = [q for q in questions if q not in selected]
            if remaining:
                selected.append(random.choice(remaining))
            else:
                break
        
        return selected
    
    def _matches_sequence_item(self, question: Dict, sequence_item: str) -> bool:
        """問題が学習順序の項目にマッチするかチェック"""
        category = question.get('category', '')
        return sequence_item in category or category in sequence_item
    
    def _check_foundation_mastery(self, dept_history: List[Dict], foundation_categories: List[str]) -> float:
        """基礎カテゴリの習得度をチェック"""
        if not foundation_categories or not dept_history:
            return 0.0
        
        foundation_history = [h for h in dept_history if h.get('category') in foundation_categories]
        
        if not foundation_history:
            return 0.0
        
        correct_count = sum(1 for h in foundation_history if h.get('is_correct', False))
        return correct_count / len(foundation_history)
    
    # === 連携学習モード専用メソッド ===
    
    def _get_integrated_learning_questions(self, user_session: Dict, all_questions: List[Dict],
                                         ai_analysis: Dict, session_size: int, mode_config: Dict, 
                                         department: str = None) -> List[Dict]:
        """連携学習モード専用の問題選択"""
        logger.info(f"連携学習モード開始: {mode_config.get('progression_strategy', 'standard')}")
        
        # 基礎理解度を評価
        foundation_mastery = self._assess_foundation_mastery(user_session, department)
        logger.info(f"基礎習熟度: {foundation_mastery:.2f}")
        
        # 学習段階を決定
        learning_stage = self._determine_learning_stage(foundation_mastery, mode_config)
        
        if learning_stage == 'foundation_building':
            return self._get_foundation_building_questions(
                user_session, all_questions, session_size, department
            )
        elif learning_stage == 'bridge_learning':
            return self._get_bridge_learning_questions(
                user_session, all_questions, ai_analysis, session_size, department
            )
        elif learning_stage == 'specialist_progression':
            return self._get_specialist_progression_questions(
                user_session, all_questions, ai_analysis, session_size, department
            )
        else:  # integrated_mastery
            return self._get_integrated_mastery_questions(
                user_session, all_questions, ai_analysis, session_size, department
            )
    
    def _assess_foundation_mastery(self, user_session: Dict, department: str = None) -> float:
        """基礎理解度の詳細評価"""
        history = user_session.get('history', [])
        
        # 部門フィルタリング
        if department:
            history = [h for h in history if h.get('department') == department]
        
        # 4-1基礎問題の成績を分析
        basic_history = [h for h in history if h.get('question_type') == 'basic']
        
        if len(basic_history) < 5:
            return 0.0
        
        # 最近の成績重視（最新20問）
        recent_basic = basic_history[-20:] if len(basic_history) > 20 else basic_history
        
        # 重要カテゴリの習熟度
        if department and department in self.department_learning_patterns:
            foundation_categories = self.department_learning_patterns[department]['foundation_categories']
            foundation_performance = self._evaluate_category_performance(recent_basic, foundation_categories)
        else:
            foundation_performance = sum(1 for h in recent_basic if h.get('is_correct', False)) / len(recent_basic)
        
        # 安定性評価（直近10問での一貫性）
        stability = self._calculate_performance_stability(recent_basic[-10:]) if len(recent_basic) >= 10 else 0.5
        
        # 総合評価（成績70% + 安定性30%）
        mastery_score = foundation_performance * 0.7 + stability * 0.3
        
        return min(mastery_score, 1.0)
    
    def _determine_learning_stage(self, foundation_mastery: float, mode_config: Dict) -> str:
        """学習段階の決定"""
        threshold = mode_config.get('foundation_threshold', 0.7)
        
        if foundation_mastery < 0.4:
            return 'foundation_building'  # 基礎構築段階
        elif foundation_mastery < threshold:
            return 'bridge_learning'  # 橋渡し学習段階
        elif foundation_mastery < 0.85:
            return 'specialist_progression'  # 専門進歩段階
        else:
            return 'integrated_mastery'  # 統合習熟段階
    
    def _get_foundation_building_questions(self, user_session: Dict, all_questions: List[Dict],
                                         session_size: int, department: str = None) -> List[Dict]:
        """基礎構築段階の問題選択"""
        logger.info("基礎構築段階: 4-1基礎問題に集中")
        
        # 4-1基礎問題のみを選択
        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
        
        # 部門フィルタリング
        if department:
            basic_questions = [q for q in basic_questions if q.get('department') == department]
        
        # 基礎重要カテゴリを優先
        if department and department in self.department_learning_patterns:
            foundation_categories = self.department_learning_patterns[department]['foundation_categories']
            priority_questions = [q for q in basic_questions if q.get('category') in foundation_categories]
            other_questions = [q for q in basic_questions if q.get('category') not in foundation_categories]
            
            # 優先カテゴリから70%、その他から30%
            priority_count = int(session_size * 0.7)
            other_count = session_size - priority_count
            
            selected = []
            if priority_questions:
                selected.extend(random.sample(priority_questions, min(priority_count, len(priority_questions))))
            if other_questions and len(selected) < session_size:
                selected.extend(random.sample(other_questions, min(other_count, len(other_questions))))
            
            return selected[:session_size]
        
        return random.sample(basic_questions, min(session_size, len(basic_questions)))
    
    def _get_bridge_learning_questions(self, user_session: Dict, all_questions: List[Dict],
                                     ai_analysis: Dict, session_size: int, department: str = None) -> List[Dict]:
        """橋渡し学習段階の問題選択"""
        logger.info("橋渡し学習段階: 基礎強化+専門導入")
        
        # 4-1基礎60% + 4-2専門40%の構成
        basic_count = int(session_size * 0.6)
        specialist_count = session_size - basic_count
        
        selected = []
        
        # 基礎問題：弱点分野を重点的に
        weak_areas = ai_analysis.get('weak_areas', {})
        basic_questions = self._select_basic_reinforcement_questions(
            user_session, all_questions, weak_areas, basic_count, department
        )
        selected.extend(basic_questions)
        
        # 専門問題：易しめの導入レベル
        specialist_questions = self._select_introductory_specialist_questions(
            user_session, all_questions, specialist_count, department
        )
        selected.extend(specialist_questions)
        
        # 学習順序に基づく並び替え
        if department:
            selected = self._arrange_by_learning_sequence(selected, department)
        
        return selected
    
    def _get_specialist_progression_questions(self, user_session: Dict, all_questions: List[Dict],
                                            ai_analysis: Dict, session_size: int, department: str = None) -> List[Dict]:
        """専門進歩段階の問題選択"""
        logger.info("専門進歩段階: 基礎維持+専門発展")
        
        # 4-1基礎30% + 4-2専門70%の構成
        basic_count = int(session_size * 0.3)
        specialist_count = session_size - basic_count
        
        selected = []
        
        # 基礎問題：維持レベル（復習中心）
        basic_questions = self._select_maintenance_basic_questions(
            user_session, all_questions, basic_count, department
        )
        selected.extend(basic_questions)
        
        # 専門問題：段階的レベルアップ
        specialist_questions = self._select_progressive_specialist_questions(
            user_session, all_questions, ai_analysis, specialist_count, department
        )
        selected.extend(specialist_questions)
        
        return selected
    
    def _get_integrated_mastery_questions(self, user_session: Dict, all_questions: List[Dict],
                                        ai_analysis: Dict, session_size: int, department: str = None) -> List[Dict]:
        """統合習熟段階の問題選択"""
        logger.info("統合習熟段階: 高度な専門問題+実践的統合")
        
        # 4-1基礎20% + 4-2専門80%の構成
        basic_count = int(session_size * 0.2)
        specialist_count = session_size - basic_count
        
        selected = []
        
        # 基礎問題：高難易度維持
        basic_questions = self._select_advanced_basic_questions(
            user_session, all_questions, basic_count, department
        )
        selected.extend(basic_questions)
        
        # 専門問題：実践レベル
        specialist_questions = self._select_practical_specialist_questions(
            user_session, all_questions, ai_analysis, specialist_count, department
        )
        selected.extend(specialist_questions)
        
        return selected
    
    def _evaluate_category_performance(self, history: List[Dict], categories: List[str]) -> float:
        """特定カテゴリの成績評価"""
        if not categories or not history:
            return 0.0
        
        category_history = [h for h in history if h.get('category') in categories]
        if not category_history:
            return 0.0
        
        return sum(1 for h in category_history if h.get('is_correct', False)) / len(category_history)
    
    def _calculate_performance_stability(self, recent_history: List[Dict]) -> float:
        """成績の安定性を計算"""
        if len(recent_history) < 5:
            return 0.5
        
        results = [1 if h.get('is_correct', False) else 0 for h in recent_history]
        
        # 連続正答・誤答の極端さを避ける
        transitions = sum(1 for i in range(1, len(results)) if results[i] != results[i-1])
        max_transitions = len(results) - 1
        
        if max_transitions == 0:
            return 0.5
        
        stability = 1 - abs(transitions / max_transitions - 0.5) * 2
        return max(0.0, min(1.0, stability))
    
    def _select_basic_reinforcement_questions(self, user_session: Dict, all_questions: List[Dict],
                                            weak_areas: Dict, count: int, department: str = None) -> List[Dict]:
        """基礎強化問題の選択"""
        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
        
        if department:
            basic_questions = [q for q in basic_questions if q.get('department') == department]
        
        # 弱点カテゴリを優先
        if weak_areas:
            weak_categories = list(weak_areas.keys())
            weak_questions = [q for q in basic_questions if q.get('category') in weak_categories]
            strong_questions = [q for q in basic_questions if q.get('category') not in weak_categories]
            
            weak_count = min(int(count * 0.7), len(weak_questions))
            strong_count = count - weak_count
            
            selected = []
            if weak_questions:
                selected.extend(random.sample(weak_questions, weak_count))
            if strong_questions and strong_count > 0:
                selected.extend(random.sample(strong_questions, min(strong_count, len(strong_questions))))
            
            return selected[:count]
        
        return random.sample(basic_questions, min(count, len(basic_questions)))
    
    def _select_introductory_specialist_questions(self, user_session: Dict, all_questions: List[Dict],
                                                count: int, department: str = None) -> List[Dict]:
        """導入レベル専門問題の選択"""
        specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
        
        if department:
            specialist_questions = [q for q in specialist_questions if q.get('department') == department]
        
        # 基本・標準難易度を優先
        easy_questions = [q for q in specialist_questions if q.get('difficulty', '標準') in ['basic', '基本', 'standard', '標準']]
        
        if len(easy_questions) >= count:
            return random.sample(easy_questions, count)
        else:
            # 不足分は他の難易度から補完
            remaining = [q for q in specialist_questions if q not in easy_questions]
            easy_questions.extend(random.sample(remaining, min(count - len(easy_questions), len(remaining))))
            return easy_questions[:count]
    
    def _select_maintenance_basic_questions(self, user_session: Dict, all_questions: List[Dict],
                                          count: int, department: str = None) -> List[Dict]:
        """維持レベル基礎問題の選択"""
        # SRS復習問題を優先的に選択
        try:
            from app import get_due_questions
            due_questions = get_due_questions(user_session, all_questions)
            basic_due = [item['question'] for item in due_questions 
                        if item['question'].get('question_type') == 'basic' and 
                        (not department or item['question'].get('department') == department)]
        except (ImportError, AttributeError, ModuleNotFoundError) as e:
            logger.warning(f"SRS機能のインポートエラー: {e}")
            basic_due = []
            
            if len(basic_due) >= count:
                return basic_due[:count]
            else:
                # 不足分はランダム選択
                basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
                if department:
                    basic_questions = [q for q in basic_questions if q.get('department') == department]
                
                additional = random.sample(basic_questions, min(count - len(basic_due), len(basic_questions)))
                return basic_due + additional
        except Exception as e:
            logger.warning(f"適応学習選択エラー: {e}")
            # フォールバック
            basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
            if department:
                basic_questions = [q for q in basic_questions if q.get('department') == department]
            return random.sample(basic_questions, min(count, len(basic_questions)))
    
    def _select_progressive_specialist_questions(self, user_session: Dict, all_questions: List[Dict],
                                               ai_analysis: Dict, count: int, department: str = None) -> List[Dict]:
        """段階的専門問題の選択"""
        specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
        
        if department:
            specialist_questions = [q for q in specialist_questions if q.get('department') == department]
        
        # 難易度バランス調整
        basic_spec = [q for q in specialist_questions if q.get('difficulty', '標準') in ['basic', '基本']]
        standard_spec = [q for q in specialist_questions if q.get('difficulty', '標準') in ['standard', '標準']]
        advanced_spec = [q for q in specialist_questions if q.get('difficulty', '標準') in ['advanced', '応用', 'expert', '上級']]
        
        # 30% 基本、50% 標準、20% 応用の配分
        basic_count = int(count * 0.3)
        standard_count = int(count * 0.5)
        advanced_count = count - basic_count - standard_count
        
        selected = []
        if basic_spec:
            selected.extend(random.sample(basic_spec, min(basic_count, len(basic_spec))))
        if standard_spec:
            selected.extend(random.sample(standard_spec, min(standard_count, len(standard_spec))))
        if advanced_spec:
            selected.extend(random.sample(advanced_spec, min(advanced_count, len(advanced_spec))))
        
        # 不足分補完
        while len(selected) < count and len(selected) < len(specialist_questions):
            remaining = [q for q in specialist_questions if q not in selected]
            if remaining:
                selected.append(random.choice(remaining))
            else:
                break
        
        return selected[:count]
    
    def _select_advanced_basic_questions(self, user_session: Dict, all_questions: List[Dict],
                                       count: int, department: str = None) -> List[Dict]:
        """高難易度基礎問題の選択"""
        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
        
        if department:
            basic_questions = [q for q in basic_questions if q.get('department') == department]
        
        # 応用・上級レベルの基礎問題を優先
        advanced_basic = [q for q in basic_questions if q.get('difficulty', '標準') in ['advanced', '応用', 'expert', '上級']]
        
        if len(advanced_basic) >= count:
            return random.sample(advanced_basic, count)
        else:
            # 不足分は標準レベルから補完
            standard_basic = [q for q in basic_questions if q.get('difficulty', '標準') in ['standard', '標準']]
            additional = random.sample(standard_basic, min(count - len(advanced_basic), len(standard_basic)))
            return advanced_basic + additional
    
    def _select_practical_specialist_questions(self, user_session: Dict, all_questions: List[Dict],
                                             ai_analysis: Dict, count: int, department: str = None) -> List[Dict]:
        """実践レベル専門問題の選択"""
        specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
        
        if department:
            specialist_questions = [q for q in specialist_questions if q.get('department') == department]
        
        # 応用・上級レベル中心
        practical_questions = [q for q in specialist_questions if q.get('difficulty', '標準') in ['advanced', '応用', 'expert', '上級']]
        
        if len(practical_questions) >= count:
            return random.sample(practical_questions, count)
        else:
            # 不足分は標準レベルから補完
            standard_questions = [q for q in specialist_questions if q.get('difficulty', '標準') in ['standard', '標準']]
            additional = random.sample(standard_questions, min(count - len(practical_questions), len(standard_questions)))
            return practical_questions + additional
    
    def _arrange_by_learning_sequence(self, questions: List[Dict], department: str) -> List[Dict]:
        """学習順序に基づく問題配置"""
        if department not in self.department_learning_patterns:
            return questions
        
        learning_sequence = self.department_learning_patterns[department]['learning_sequence']
        
        # 基礎問題を先に、専門問題を後に配置
        basic_questions = [q for q in questions if q.get('question_type') == 'basic']
        specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
        
        # 基礎問題内での順序調整
        sequenced_basic = self._apply_department_learning_sequence(basic_questions, department)
        
        # 専門問題内での順序調整
        sequenced_specialist = self._apply_department_learning_sequence(specialist_questions, department)
        
        return sequenced_basic + sequenced_specialist
    
    def filter_questions_by_department(self, questions: List[Dict], department: str) -> List[Dict]:
        """部門別問題フィルタリング"""
        if not department:
            return questions
        
        filtered_questions = [q for q in questions if q.get('department') == department]
        logger.info(f"部門フィルタリング: {department} -> {len(filtered_questions)}問")
        
        return filtered_questions
    
    def monitor_and_adjust_difficulty(self, user_session: Dict, recent_results: List[Dict]) -> Dict[str, Any]:
        """リアルタイムパフォーマンス監視と難易度調整"""
        try:
            # 動的難易度制御によるパフォーマンス監視
            adjustment_result = difficulty_controller.monitor_performance_and_adjust(user_session, recent_results)
            
            if adjustment_result.get('adjustment_needed', False):
                logger.info(f"難易度調整が推奨されました: {adjustment_result['current_level']} → {adjustment_result['suggested_level']}")
                
                # 新しい学習者レベル評価を実行
                new_assessment = difficulty_controller.assess_learner_level(user_session)
                
                # セッション設定を更新
                new_config = difficulty_controller.get_dynamic_session_config(new_assessment)
                user_session['dynamic_session_config'] = new_config
                user_session['difficulty_level'] = adjustment_result['suggested_level']
                
                logger.info(f"動的難易度調整実行: レベル{adjustment_result['suggested_level']}, 目標正答率{new_config['target_accuracy']:.0%}")
                
                return {
                    'adjusted': True,
                    'old_level': adjustment_result['current_level'],
                    'new_level': adjustment_result['suggested_level'],
                    'confidence': adjustment_result['confidence'],
                    'recommendations': adjustment_result['recommendations'],
                    'new_config': new_config
                }
            else:
                return {
                    'adjusted': False,
                    'reason': adjustment_result.get('reason', 'パフォーマンス安定'),
                    'current_performance': adjustment_result.get('current_performance', {})
                }
                
        except Exception as e:
            logger.error(f"難易度監視・調整エラー: {e}")
            return {'adjusted': False, 'error': str(e)}
    
    def get_learner_insights(self, user_session: Dict, department: str = None) -> Dict[str, Any]:
        """学習者インサイトの取得（難易度制御情報を含む）"""
        try:
            # 現在の学習者レベル評価
            learner_assessment = difficulty_controller.assess_learner_level(user_session, department)
            
            # 最近のパフォーマンス分析
            recent_history = user_session.get('history', [])[-20:]  # 最近20問
            if recent_history:
                recent_performance = difficulty_controller._analyze_current_performance(recent_history)
            else:
                recent_performance = {'accuracy': 0, 'avg_time': 0, 'sample_size': 0, 'trend': 'unknown'}
            
            # 推奨アクション
            dynamic_config = user_session.get('dynamic_session_config', {})
            
            insights = {
                'learner_level': learner_assessment['overall_level'],
                'level_name': learner_assessment['level_name'],
                'confidence': learner_assessment['confidence'],
                'assessments': learner_assessment['assessments'],
                'recent_performance': recent_performance,
                'recommended_difficulty': learner_assessment['recommended_difficulty'],
                'dynamic_config': dynamic_config,
                'department_factor': learner_assessment.get('department_factor', 1.0),
                'next_adjustment_threshold': learner_assessment.get('next_adjustment_threshold', 20),
                'study_recommendations': self._generate_study_recommendations(learner_assessment, recent_performance)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"学習者インサイト取得エラー: {e}")
            return {'error': str(e)}
    
    def _generate_study_recommendations(self, learner_assessment: Dict, recent_performance: Dict) -> List[str]:
        """学習推奨事項の生成"""
        recommendations = []
        
        level = learner_assessment['overall_level']
        accuracy_score = learner_assessment['assessments']['accuracy']['score']
        speed_score = learner_assessment['assessments']['speed']['score']
        
        # レベル別推奨事項
        if level == 'beginner':
            recommendations.append("基礎問題から始めて、確実に理解を深めましょう")
            recommendations.append("復習機能を活用して、反復学習を心がけてください")
        elif level == 'intermediate':
            recommendations.append("基礎と応用のバランスを取りながら学習しましょう")
            if accuracy_score < 0.6:
                recommendations.append("正答率向上のため、基礎の復習を増やすことをお勧めします")
        elif level == 'advanced':
            recommendations.append("応用問題に積極的に挑戦してみてください")
            if speed_score < 0.5:
                recommendations.append("解答速度向上のため、時間を意識した練習をお勧めします")
        elif level == 'expert':
            recommendations.append("難問への挑戦で更なるスキルアップを目指しましょう")
            recommendations.append("他の部門の学習も検討してみてください")
        
        # パフォーマンストレンド別推奨事項
        trend = recent_performance.get('trend', 'stable')
        if trend == 'improving':
            recommendations.append("順調に成績が向上しています！この調子で継続してください")
        elif trend == 'declining':
            recommendations.append("最近の成績が下降気味です。休息を取るか、基礎に戻ることをお勧めします")
        
        return recommendations

# グローバルインスタンス
adaptive_engine = AdaptiveLearningEngine()