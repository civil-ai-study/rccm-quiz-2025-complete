"""
RCCM学習アプリ - マルチモーダル学習支援システム
図表・画像問題対応とビジュアル学習機能の実装
"""

import os
import base64
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class MultimodalLearningManager:
    """マルチモーダル学習管理システム"""
    
    def __init__(self):
        # サポートする画像形式
        self.supported_image_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'
        }
        
        # 図表タイプ定義
        self.visual_content_types = {
            'diagram': {
                'name': '図解・ダイアグラム',
                'icon': 'fas fa-project-diagram',
                'color': '#007bff',
                'learning_methods': ['visual_analysis', 'step_by_step', 'interactive']
            },
            'chart': {
                'name': 'グラフ・チャート',
                'icon': 'fas fa-chart-bar',
                'color': '#28a745',
                'learning_methods': ['data_reading', 'trend_analysis', 'comparison']
            },
            'technical_drawing': {
                'name': '技術図面',
                'icon': 'fas fa-drafting-compass',
                'color': '#dc3545',
                'learning_methods': ['detail_focus', 'dimension_reading', 'symbol_recognition']
            },
            'photo': {
                'name': '現場写真',
                'icon': 'fas fa-camera',
                'color': '#ffc107',
                'learning_methods': ['observation', 'identification', 'practical_analysis']
            },
            'map': {
                'name': '地図・配置図',
                'icon': 'fas fa-map',
                'color': '#17a2b8',
                'learning_methods': ['spatial_understanding', 'location_analysis', 'scale_reading']
            }
        }
        
        # ビジュアル学習モード
        self.visual_learning_modes = {
            'visual_analysis': {
                'name': 'ビジュアル分析モード',
                'description': '図表を詳細に分析して理解を深める',
                'techniques': ['zoom_focus', 'annotation', 'comparison'],
                'suitable_for': ['diagram', 'technical_drawing']
            },
            'interactive_exploration': {
                'name': 'インタラクティブ探索',
                'description': '画像の各部分をクリックして詳細を学習',
                'techniques': ['hotspot_clicking', 'progressive_reveal', 'guided_tour'],
                'suitable_for': ['diagram', 'technical_drawing', 'photo']
            },
            'pattern_recognition': {
                'name': 'パターン認識学習',
                'description': '類似パターンを比較して理解を促進',
                'techniques': ['side_by_side', 'difference_highlighting', 'classification'],
                'suitable_for': ['chart', 'photo', 'map']
            },
            'step_by_step': {
                'name': 'ステップバイステップ学習',
                'description': '段階的に情報を表示して理解を促進',
                'techniques': ['progressive_disclosure', 'guided_sequence', 'checkpoint_review'],
                'suitable_for': ['diagram', 'technical_drawing']
            }
        }
    
    def analyze_visual_content(self, question_data: Dict) -> Dict[str, Any]:
        """ビジュアルコンテンツの分析"""
        try:
            analysis = {
                'has_visual_content': False,
                'visual_type': None,
                'recommended_learning_mode': None,
                'complexity_level': 'medium',
                'learning_enhancements': [],
                'accessibility_features': [],
                'estimated_study_time': 60  # 秒
            }
            
            # 画像ファイルの存在確認
            image_path = question_data.get('image_path')
            if image_path and os.path.exists(image_path):
                analysis['has_visual_content'] = True
                analysis['visual_type'] = self._detect_visual_type(image_path, question_data)
                analysis['recommended_learning_mode'] = self._recommend_learning_mode(analysis['visual_type'])
                analysis['complexity_level'] = self._assess_visual_complexity(question_data)
                analysis['learning_enhancements'] = self._generate_learning_enhancements(analysis['visual_type'])
                analysis['accessibility_features'] = self._generate_accessibility_features(question_data)
                analysis['estimated_study_time'] = self._estimate_visual_study_time(analysis['complexity_level'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"ビジュアルコンテンツ分析エラー: {e}")
            return {'has_visual_content': False, 'error': str(e)}
    
    def generate_visual_learning_session(self, question_data: Dict, learning_mode: str, 
                                       user_preferences: Dict = None) -> Dict[str, Any]:
        """ビジュアル学習セッションの生成"""
        try:
            if user_preferences is None:
                user_preferences = {}
            
            visual_analysis = self.analyze_visual_content(question_data)
            
            if not visual_analysis['has_visual_content']:
                return {'success': False, 'reason': 'ビジュアルコンテンツが見つかりません'}
            
            mode_config = self.visual_learning_modes.get(learning_mode, self.visual_learning_modes['visual_analysis'])
            
            session = {
                'session_id': f"visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'question_id': question_data.get('id'),
                'learning_mode': learning_mode,
                'visual_type': visual_analysis['visual_type'],
                'complexity_level': visual_analysis['complexity_level'],
                'estimated_duration': visual_analysis['estimated_study_time'],
                'learning_steps': self._generate_learning_steps(question_data, mode_config, visual_analysis),
                'interaction_elements': self._generate_interaction_elements(question_data, mode_config),
                'assessment_criteria': self._generate_assessment_criteria(visual_analysis),
                'accessibility_options': visual_analysis['accessibility_features'],
                'enhancement_tools': visual_analysis['learning_enhancements']
            }
            
            return {'success': True, 'session': session}
            
        except Exception as e:
            logger.error(f"ビジュアル学習セッション生成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_visual_interaction(self, session_id: str, interaction_data: Dict) -> Dict[str, Any]:
        """ビジュアルインタラクションの処理"""
        try:
            interaction_type = interaction_data.get('type')
            coordinates = interaction_data.get('coordinates', {})
            timestamp = datetime.now()
            
            response = {
                'success': True,
                'interaction_id': f"{session_id}_{timestamp.strftime('%H%M%S')}",
                'feedback': '',
                'next_action': None,
                'learning_points': [],
                'progress_update': {}
            }
            
            if interaction_type == 'click_hotspot':
                response.update(self._handle_hotspot_click(coordinates, interaction_data))
            elif interaction_type == 'zoom_area':
                response.update(self._handle_zoom_interaction(coordinates, interaction_data))
            elif interaction_type == 'annotation_add':
                response.update(self._handle_annotation_add(interaction_data))
            elif interaction_type == 'comparison_toggle':
                response.update(self._handle_comparison_toggle(interaction_data))
            else:
                response['feedback'] = 'インタラクションタイプが認識されませんでした'
            
            return response
            
        except Exception as e:
            logger.error(f"ビジュアルインタラクション処理エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_visual_summary(self, session_data: Dict, user_interactions: List[Dict]) -> Dict[str, Any]:
        """ビジュアル学習セッションの要約生成"""
        try:
            summary = {
                'session_id': session_data.get('session_id'),
                'total_interactions': len(user_interactions),
                'learning_completion': 0.0,
                'key_insights': [],
                'areas_of_focus': [],
                'recommended_review': [],
                'visual_comprehension_score': 0.0,
                'time_spent': 0,
                'next_steps': []
            }
            
            # インタラクション分析
            interaction_analysis = self._analyze_user_interactions(user_interactions)
            summary.update(interaction_analysis)
            
            # 学習完了度計算
            completion_score = self._calculate_learning_completion(session_data, user_interactions)
            summary['learning_completion'] = completion_score
            
            # ビジュアル理解度スコア
            comprehension_score = self._calculate_visual_comprehension(user_interactions)
            summary['visual_comprehension_score'] = comprehension_score
            
            # 推奨事項生成
            recommendations = self._generate_visual_learning_recommendations(summary, session_data)
            summary['next_steps'] = recommendations
            
            return summary
            
        except Exception as e:
            logger.error(f"ビジュアル学習要約生成エラー: {e}")
            return {'error': str(e)}
    
    def get_accessibility_features(self, question_data: Dict, user_needs: Dict = None) -> Dict[str, Any]:
        """アクセシビリティ機能の取得"""
        try:
            if user_needs is None:
                user_needs = {}
            
            features = {
                'alt_text': self._generate_alt_text(question_data),
                'high_contrast_mode': True,
                'text_scaling': True,
                'audio_description': self._generate_audio_description(question_data),
                'tactile_description': self._generate_tactile_description(question_data),
                'keyboard_navigation': True,
                'screen_reader_support': True,
                'color_blind_support': self._generate_color_blind_support(question_data)
            }
            
            # ユーザーニーズに基づく調整
            if user_needs.get('visual_impairment'):
                features['priority_audio'] = True
                features['detailed_descriptions'] = True
            
            if user_needs.get('motor_impairment'):
                features['large_click_areas'] = True
                features['voice_control'] = True
            
            return features
            
        except Exception as e:
            logger.error(f"アクセシビリティ機能取得エラー: {e}")
            return {}
    
    def _detect_visual_type(self, image_path: str, question_data: Dict) -> str:
        """ビジュアルタイプの検出"""
        # ファイル名や問題文からヒントを取得
        filename = os.path.basename(image_path).lower()
        question_text = question_data.get('question', '').lower()
        
        # キーワードベースの分類
        if any(keyword in filename or keyword in question_text 
               for keyword in ['chart', 'graph', 'グラフ', 'チャート']):
            return 'chart'
        elif any(keyword in filename or keyword in question_text 
                 for keyword in ['diagram', '図解', 'ダイアグラム', 'フロー']):
            return 'diagram'
        elif any(keyword in filename or keyword in question_text 
                 for keyword in ['drawing', '図面', '設計図', 'plan']):
            return 'technical_drawing'
        elif any(keyword in filename or keyword in question_text 
                 for keyword in ['photo', '写真', '現場', 'site']):
            return 'photo'
        elif any(keyword in filename or keyword in question_text 
                 for keyword in ['map', '地図', 'layout', '配置']):
            return 'map'
        else:
            return 'diagram'  # デフォルト
    
    def _recommend_learning_mode(self, visual_type: str) -> str:
        """学習モードの推奨"""
        recommendations = {
            'diagram': 'step_by_step',
            'chart': 'pattern_recognition',
            'technical_drawing': 'visual_analysis',
            'photo': 'interactive_exploration',
            'map': 'pattern_recognition'
        }
        return recommendations.get(visual_type, 'visual_analysis')
    
    def _assess_visual_complexity(self, question_data: Dict) -> str:
        """ビジュアルの複雑度評価"""
        question_text = question_data.get('question', '')
        options_count = len([k for k in question_data.keys() if k.startswith('option_')])
        
        # 複雑度判定要因
        complexity_indicators = 0
        
        if len(question_text) > 200:
            complexity_indicators += 1
        if options_count > 4:
            complexity_indicators += 1
        if any(keyword in question_text.lower() 
               for keyword in ['詳細', '複数', '比較', '分析', '計算']):
            complexity_indicators += 1
        
        if complexity_indicators >= 2:
            return 'high'
        elif complexity_indicators == 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_learning_enhancements(self, visual_type: str) -> List[str]:
        """学習支援機能の生成"""
        enhancements = ['zoom_tool', 'annotation_tool', 'highlight_tool']
        
        type_specific_enhancements = {
            'chart': ['data_table_view', 'trend_line_overlay'],
            'diagram': ['step_navigation', 'component_labeling'],
            'technical_drawing': ['measurement_tool', 'layer_toggle'],
            'photo': ['detail_popup', 'comparison_mode'],
            'map': ['scale_indicator', 'coordinate_display']
        }
        
        enhancements.extend(type_specific_enhancements.get(visual_type, []))
        return enhancements
    
    def _generate_accessibility_features(self, question_data: Dict) -> List[str]:
        """アクセシビリティ機能の生成"""
        return [
            'alt_text_available',
            'high_contrast_toggle',
            'text_size_adjustment',
            'keyboard_shortcuts',
            'screen_reader_compatible'
        ]
    
    def _estimate_visual_study_time(self, complexity_level: str) -> int:
        """ビジュアル学習時間の推定（秒）"""
        time_estimates = {
            'low': 45,
            'medium': 60,
            'high': 90
        }
        return time_estimates.get(complexity_level, 60)
    
    def _generate_learning_steps(self, question_data: Dict, mode_config: Dict, 
                                visual_analysis: Dict) -> List[Dict]:
        """学習ステップの生成"""
        steps = []
        
        # 基本ステップ
        steps.append({
            'step_id': 1,
            'title': '初期観察',
            'description': '画像全体を見て、何が描かれているかを把握しましょう',
            'duration': 15,
            'interaction_type': 'observation',
            'guidance': '急がずに、画像の全体的な印象を掴んでください'
        })
        
        # ビジュアルタイプ別のステップ
        visual_type = visual_analysis['visual_type']
        
        if visual_type == 'diagram':
            steps.extend([
                {
                    'step_id': 2,
                    'title': '要素の特定',
                    'description': '図の各要素を特定し、その関係性を理解しましょう',
                    'duration': 20,
                    'interaction_type': 'element_identification',
                    'guidance': '矢印や線でつながれた要素に注目してください'
                },
                {
                    'step_id': 3,
                    'title': 'フローの理解',
                    'description': 'プロセスの流れや情報の流れを追跡しましょう',
                    'duration': 25,
                    'interaction_type': 'flow_tracing',
                    'guidance': '開始点から終了点まで、順序立てて理解してください'
                }
            ])
        elif visual_type == 'chart':
            steps.extend([
                {
                    'step_id': 2,
                    'title': 'データの読み取り',
                    'description': '軸の値や凡例を確認し、データを正確に読み取りましょう',
                    'duration': 20,
                    'interaction_type': 'data_reading',
                    'guidance': 'X軸、Y軸の単位と範囲を確認してください'
                },
                {
                    'step_id': 3,
                    'title': 'トレンド分析',
                    'description': 'データの傾向や特徴的なパターンを見つけましょう',
                    'duration': 25,
                    'interaction_type': 'trend_analysis',
                    'guidance': '最高値、最低値、変化の傾向に注目してください'
                }
            ])
        
        # 最終ステップ
        steps.append({
            'step_id': len(steps) + 1,
            'title': '理解の確認',
            'description': '学習した内容を整理し、問題に答える準備をしましょう',
            'duration': 15,
            'interaction_type': 'comprehension_check',
            'guidance': '重要なポイントを再確認してください'
        })
        
        return steps
    
    def _generate_interaction_elements(self, question_data: Dict, mode_config: Dict) -> List[Dict]:
        """インタラクション要素の生成"""
        elements = []
        
        # 基本的なインタラクション要素
        elements.extend([
            {
                'type': 'zoom_control',
                'position': 'bottom-right',
                'functionality': 'image_zoom',
                'description': '画像の拡大・縮小'
            },
            {
                'type': 'annotation_tool',
                'position': 'top-right',
                'functionality': 'add_notes',
                'description': 'メモの追加'
            },
            {
                'type': 'highlight_tool',
                'position': 'top-left',
                'functionality': 'mark_important',
                'description': '重要箇所のマーキング'
            }
        ])
        
        # モード固有の要素
        techniques = mode_config.get('techniques', [])
        
        if 'hotspot_clicking' in techniques:
            elements.append({
                'type': 'hotspot_areas',
                'position': 'overlay',
                'functionality': 'interactive_exploration',
                'description': 'クリック可能エリア'
            })
        
        if 'progressive_reveal' in techniques:
            elements.append({
                'type': 'reveal_control',
                'position': 'bottom-center',
                'functionality': 'step_by_step_reveal',
                'description': '段階的表示制御'
            })
        
        return elements
    
    def _generate_assessment_criteria(self, visual_analysis: Dict) -> Dict[str, Any]:
        """評価基準の生成"""
        criteria = {
            'visual_attention': {
                'name': 'ビジュアル注意力',
                'description': '重要な視覚的要素に注目できているか',
                'weight': 0.3
            },
            'pattern_recognition': {
                'name': 'パターン認識',
                'description': '視覚的パターンを正確に識別できているか',
                'weight': 0.3
            },
            'detail_comprehension': {
                'name': '詳細理解',
                'description': '細部の情報を正確に理解できているか',
                'weight': 0.2
            },
            'integration_ability': {
                'name': '統合能力',
                'description': '視覚情報を全体的に統合できているか',
                'weight': 0.2
            }
        }
        
        return criteria
    
    def _handle_hotspot_click(self, coordinates: Dict, interaction_data: Dict) -> Dict:
        """ホットスポットクリックの処理"""
        x, y = coordinates.get('x', 0), coordinates.get('y', 0)
        
        # 座標に基づくフィードバック生成（実際の実装では画像解析が必要）
        feedback = f"座標({x}, {y})をクリックしました。"
        learning_points = ["クリックした領域の詳細を確認しました"]
        
        return {
            'feedback': feedback,
            'learning_points': learning_points,
            'next_action': 'continue_exploration'
        }
    
    def _handle_zoom_interaction(self, coordinates: Dict, interaction_data: Dict) -> Dict:
        """ズームインタラクションの処理"""
        zoom_level = interaction_data.get('zoom_level', 1.0)
        
        feedback = f"拡大率{zoom_level:.1f}倍で詳細を確認中です。"
        learning_points = ["画像の詳細部分を拡大して観察しました"]
        
        return {
            'feedback': feedback,
            'learning_points': learning_points,
            'next_action': 'analyze_details'
        }
    
    def _handle_annotation_add(self, interaction_data: Dict) -> Dict:
        """注釈追加の処理"""
        annotation_text = interaction_data.get('annotation', '')
        
        feedback = "注釈を追加しました。学習ポイントを記録することは理解促進に効果的です。"
        learning_points = [f"注釈を追加: {annotation_text}"]
        
        return {
            'feedback': feedback,
            'learning_points': learning_points,
            'next_action': 'continue_learning'
        }
    
    def _handle_comparison_toggle(self, interaction_data: Dict) -> Dict:
        """比較モード切り替えの処理"""
        comparison_mode = interaction_data.get('comparison_enabled', False)
        
        if comparison_mode:
            feedback = "比較モードが有効になりました。複数の要素を比較して学習しましょう。"
            learning_points = ["比較分析モードを開始しました"]
        else:
            feedback = "比較モードを終了しました。"
            learning_points = ["比較分析を完了しました"]
        
        return {
            'feedback': feedback,
            'learning_points': learning_points,
            'next_action': 'continue_analysis'
        }
    
    def _analyze_user_interactions(self, interactions: List[Dict]) -> Dict:
        """ユーザーインタラクションの分析"""
        analysis = {
            'interaction_types': defaultdict(int),
            'total_time': 0,
            'engagement_level': 'medium',
            'learning_patterns': []
        }
        
        for interaction in interactions:
            interaction_type = interaction.get('type', 'unknown')
            analysis['interaction_types'][interaction_type] += 1
            analysis['total_time'] += interaction.get('duration', 0)
        
        # エンゲージメントレベルの判定
        total_interactions = len(interactions)
        if total_interactions >= 10:
            analysis['engagement_level'] = 'high'
        elif total_interactions >= 5:
            analysis['engagement_level'] = 'medium'
        else:
            analysis['engagement_level'] = 'low'
        
        return analysis
    
    def _calculate_learning_completion(self, session_data: Dict, interactions: List[Dict]) -> float:
        """学習完了度の計算"""
        expected_steps = len(session_data.get('learning_steps', []))
        completed_steps = len([i for i in interactions if i.get('step_completed', False)])
        
        if expected_steps == 0:
            return 0.0
        
        return min(1.0, completed_steps / expected_steps)
    
    def _calculate_visual_comprehension(self, interactions: List[Dict]) -> float:
        """ビジュアル理解度の計算"""
        # インタラクションの質と量に基づくスコア計算
        quality_indicators = 0
        total_possible = 5
        
        # 多様なインタラクションタイプ
        interaction_types = set(i.get('type') for i in interactions)
        if len(interaction_types) >= 3:
            quality_indicators += 1
        
        # 適切な滞在時間
        total_time = sum(i.get('duration', 0) for i in interactions)
        if 30 <= total_time <= 180:  # 30秒〜3分
            quality_indicators += 1
        
        # 詳細確認（ズーム等）
        detail_interactions = [i for i in interactions if i.get('type') == 'zoom_area']
        if detail_interactions:
            quality_indicators += 1
        
        # 注釈やメモ
        annotation_interactions = [i for i in interactions if i.get('type') == 'annotation_add']
        if annotation_interactions:
            quality_indicators += 1
        
        # 完了度
        if len(interactions) >= 5:
            quality_indicators += 1
        
        return quality_indicators / total_possible
    
    def _generate_visual_learning_recommendations(self, summary: Dict, session_data: Dict) -> List[str]:
        """ビジュアル学習推奨事項の生成"""
        recommendations = []
        
        completion = summary.get('learning_completion', 0)
        comprehension = summary.get('visual_comprehension_score', 0)
        engagement = summary.get('engagement_level', 'medium')
        
        if completion < 0.7:
            recommendations.append("学習ステップを最後まで完了することをお勧めします")
        
        if comprehension < 0.6:
            recommendations.append("画像の詳細をもっと注意深く観察してみてください")
            recommendations.append("ズーム機能を使って重要な部分を拡大確認しましょう")
        
        if engagement == 'low':
            recommendations.append("インタラクティブ機能をより活用して学習効果を高めましょう")
        
        # ビジュアルタイプ別の推奨
        visual_type = session_data.get('visual_type')
        if visual_type == 'chart':
            recommendations.append("データの数値を正確に読み取る練習をしましょう")
        elif visual_type == 'diagram':
            recommendations.append("各要素の関係性を整理して理解を深めましょう")
        
        return recommendations
    
    def _generate_alt_text(self, question_data: Dict) -> str:
        """代替テキストの生成"""
        # 実際の実装では画像解析AIを使用
        return "図表の代替テキスト説明"
    
    def _generate_audio_description(self, question_data: Dict) -> str:
        """音声説明の生成"""
        return "図表の音声による詳細説明"
    
    def _generate_tactile_description(self, question_data: Dict) -> str:
        """触覚説明の生成"""
        return "図表の触覚的特徴の説明"
    
    def _generate_color_blind_support(self, question_data: Dict) -> Dict:
        """色覚異常対応機能の生成"""
        return {
            'alternative_colors': True,
            'pattern_overlay': True,
            'text_labels': True
        }

# グローバルインスタンス
multimodal_manager = MultimodalLearningManager()