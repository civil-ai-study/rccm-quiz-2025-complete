"""
RCCM学習アプリ - ソーシャル学習機能
学習グループ、ピア比較、ディスカッション、協調学習機能
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import random

logger = logging.getLogger(__name__)

class SocialLearningManager:
    """ソーシャル学習機能管理"""
    
    def __init__(self, user_data_dir: str = 'user_data', social_data_dir: str = 'social_data'):
        self.user_data_dir = user_data_dir
        self.social_data_dir = social_data_dir
        self.groups_file = os.path.join(social_data_dir, 'groups.json')
        self.discussions_file = os.path.join(social_data_dir, 'discussions.json')
        self.peer_interactions_file = os.path.join(social_data_dir, 'peer_interactions.json')
        
        # ディレクトリ作成
        os.makedirs(social_data_dir, exist_ok=True)
        
        logger.info("ソーシャル学習機能初期化完了")
    
    # === 学習グループ管理 ===
    
    def create_study_group(self, creator_id: str, group_name: str, description: str = '', 
                          department: str = None, target_exam_date: str = None) -> Dict[str, Any]:
        """学習グループ作成"""
        try:
            groups = self._load_groups()
            
            group_id = hashlib.md5(f"{group_name}{creator_id}{datetime.now()}".encode()).hexdigest()[:12]
            
            new_group = {
                'id': group_id,
                'name': group_name,
                'description': description,
                'creator_id': creator_id,
                'department': department,
                'target_exam_date': target_exam_date,
                'created_at': datetime.now().isoformat(),
                'members': [creator_id],
                'moderators': [creator_id],
                'is_public': True,
                'settings': {
                    'allow_join_requests': True,
                    'require_approval': False,
                    'max_members': 50,
                    'study_schedule': [],
                    'shared_goals': []
                },
                'statistics': {
                    'total_members': 1,
                    'active_members': 1,
                    'discussions_count': 0,
                    'shared_questions': 0,
                    'group_sessions': 0
                }
            }
            
            groups[group_id] = new_group
            self._save_groups(groups)
            
            logger.info(f"学習グループ作成: {group_name} (ID: {group_id})")
            return {
                'success': True,
                'group_id': group_id,
                'group': new_group
            }
            
        except Exception as e:
            logger.error(f"グループ作成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def join_group(self, user_id: str, group_id: str, request_message: str = '') -> Dict[str, Any]:
        """グループ参加"""
        try:
            groups = self._load_groups()
            
            if group_id not in groups:
                return {'success': False, 'error': 'グループが見つかりません'}
            
            group = groups[group_id]
            
            # 既に参加済みチェック
            if user_id in group['members']:
                return {'success': False, 'error': '既にグループに参加しています'}
            
            # 参加人数制限チェック
            if len(group['members']) >= group['settings']['max_members']:
                return {'success': False, 'error': 'グループの参加人数が上限に達しています'}
            
            # 承認が必要な場合
            if group['settings']['require_approval']:
                # 参加リクエストとして処理（簡略化）
                group['members'].append(user_id)
                message = f"{user_id}さんがグループに参加しました"
            else:
                # 直接参加
                group['members'].append(user_id)
                message = f"{user_id}さんがグループに参加しました"
            
            # 統計更新
            group['statistics']['total_members'] = len(group['members'])
            
            groups[group_id] = group
            self._save_groups(groups)
            
            # グループ活動記録
            self._record_group_activity(group_id, 'member_joined', user_id, message)
            
            logger.info(f"グループ参加: ユーザー{user_id} → グループ{group_id}")
            return {
                'success': True,
                'message': message,
                'group': group
            }
            
        except Exception as e:
            logger.error(f"グループ参加エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def leave_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """グループ退会"""
        try:
            groups = self._load_groups()
            
            if group_id not in groups:
                return {'success': False, 'error': 'グループが見つかりません'}
            
            group = groups[group_id]
            
            if user_id not in group['members']:
                return {'success': False, 'error': 'グループに参加していません'}
            
            # メンバーから削除
            group['members'].remove(user_id)
            
            # モデレーターからも削除
            if user_id in group['moderators']:
                group['moderators'].remove(user_id)
                
                # 作成者が退会する場合、他のモデレーターに権限移譲
                if user_id == group['creator_id'] and group['members']:
                    new_creator = group['members'][0]
                    group['creator_id'] = new_creator
                    if new_creator not in group['moderators']:
                        group['moderators'].append(new_creator)
            
            # グループが空になった場合は削除
            if not group['members']:
                del groups[group_id]
                self._save_groups(groups)
                return {'success': True, 'message': 'グループが削除されました'}
            
            # 統計更新
            group['statistics']['total_members'] = len(group['members'])
            
            groups[group_id] = group
            self._save_groups(groups)
            
            self._record_group_activity(group_id, 'member_left', user_id, f"{user_id}さんがグループを退会しました")
            
            logger.info(f"グループ退会: ユーザー{user_id} ← グループ{group_id}")
            return {'success': True, 'message': 'グループを退会しました'}
            
        except Exception as e:
            logger.error(f"グループ退会エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーの参加グループ取得"""
        try:
            groups = self._load_groups()
            user_groups = []
            
            for group_id, group in groups.items():
                if user_id in group['members']:
                    # 簡略化された情報を返す
                    user_groups.append({
                        'id': group_id,
                        'name': group['name'],
                        'description': group['description'],
                        'department': group['department'],
                        'member_count': len(group['members']),
                        'is_moderator': user_id in group['moderators'],
                        'is_creator': user_id == group['creator_id'],
                        'created_at': group['created_at'],
                        'recent_activity': self._get_recent_group_activity(group_id)
                    })
            
            return user_groups
            
        except Exception as e:
            logger.error(f"ユーザーグループ取得エラー: {e}")
            return []
    
    def discover_groups(self, user_id: str, department: str = None, 
                       limit: int = 20) -> List[Dict[str, Any]]:
        """グループ発見"""
        try:
            groups = self._load_groups()
            user_data = self._load_user_data(user_id)
            
            recommendations = []
            
            for group_id, group in groups.items():
                # 既に参加済みのグループは除外
                if user_id in group['members']:
                    continue
                
                # 公開グループのみ
                if not group.get('is_public', True):
                    continue
                
                # 部門フィルタ
                if department and group.get('department') != department:
                    continue
                
                # 参加人数制限チェック
                if len(group['members']) >= group['settings']['max_members']:
                    continue
                
                # 推奨スコア計算
                score = self._calculate_group_match_score(user_data, group)
                
                recommendations.append({
                    'group': {
                        'id': group_id,
                        'name': group['name'],
                        'description': group['description'],
                        'department': group['department'],
                        'member_count': len(group['members']),
                        'created_at': group['created_at'],
                        'target_exam_date': group.get('target_exam_date')
                    },
                    'match_score': score,
                    'reasons': self._get_match_reasons(user_data, group)
                })
            
            # スコア順でソート
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"グループ発見エラー: {e}")
            return []
    
    # === ピア比較機能 ===
    
    def get_peer_comparison(self, user_id: str, comparison_type: str = 'department') -> Dict[str, Any]:
        """ピア比較分析"""
        try:
            user_data = self._load_user_data(user_id)
            if not user_data:
                return {'error': 'ユーザーデータが見つかりません'}
            
            all_users = self._load_all_user_data()
            
            # 比較対象ユーザーを選択
            peers = self._select_peers(user_id, user_data, all_users, comparison_type)
            
            if not peers:
                return {'message': '比較対象のユーザーが見つかりませんでした'}
            
            # 比較分析
            comparison_result = {
                'user_stats': self._calculate_user_stats(user_data),
                'peer_stats': self._calculate_peer_stats(peers),
                'rankings': self._calculate_rankings(user_id, user_data, peers),
                'improvement_suggestions': self._generate_improvement_suggestions(user_data, peers),
                'peer_count': len(peers),
                'comparison_type': comparison_type
            }
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"ピア比較エラー: {e}")
            return {'error': str(e)}
    
    def get_leaderboard(self, department: str = None, time_period: str = 'month') -> List[Dict[str, Any]]:
        """リーダーボード取得"""
        try:
            all_users = self._load_all_user_data()
            
            # 時間期間フィルタ
            cutoff_date = self._get_time_cutoff(time_period)
            
            user_scores = []
            for user_id, user_data in all_users.items():
                history = user_data.get('history', [])
                
                # 期間フィルタ
                if cutoff_date:
                    filtered_history = []
                    for h in history:
                        try:
                            date_str = h.get('date', '')
                            if date_str:
                                date_obj = datetime.fromisoformat(date_str)
                                if date_obj >= cutoff_date:
                                    filtered_history.append(h)
                        except (ValueError, TypeError):
                            continue
                    history = filtered_history
                
                # 部門フィルタ
                if department:
                    history = [h for h in history if h.get('department') == department]
                
                if not history:
                    continue
                
                # スコア計算
                score = self._calculate_leaderboard_score(history)
                
                user_scores.append({
                    'user_id': user_id,
                    'score': score,
                    'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history),
                    'total_questions': len(history),
                    'study_streak': self._calculate_study_streak(history),
                    'department_focus': self._get_primary_department(history)
                })
            
            # スコア順でソート
            user_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # ランキング付与
            for i, user_score in enumerate(user_scores):
                user_score['rank'] = i + 1
            
            return user_scores[:50]  # トップ50
            
        except Exception as e:
            logger.error(f"リーダーボード取得エラー: {e}")
            return []
    
    # === ディスカッション機能 ===
    
    def create_discussion(self, user_id: str, title: str, content: str, 
                         question_id: int = None, group_id: str = None, 
                         category: str = 'general') -> Dict[str, Any]:
        """ディスカッション作成"""
        try:
            discussions = self._load_discussions()
            
            discussion_id = hashlib.md5(f"{title}{user_id}{datetime.now()}".encode()).hexdigest()[:12]
            
            new_discussion = {
                'id': discussion_id,
                'title': title,
                'content': content,
                'author_id': user_id,
                'question_id': question_id,
                'group_id': group_id,
                'category': category,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'replies': [],
                'votes': {'up': 0, 'down': 0, 'voters': []},
                'tags': self._extract_tags(content),
                'is_solved': False,
                'is_pinned': False,
                'view_count': 0
            }
            
            discussions[discussion_id] = new_discussion
            self._save_discussions(discussions)
            
            # グループディスカッションの場合、グループ統計更新
            if group_id:
                self._update_group_discussion_count(group_id)
            
            logger.info(f"ディスカッション作成: {title} (ID: {discussion_id})")
            return {
                'success': True,
                'discussion_id': discussion_id,
                'discussion': new_discussion
            }
            
        except Exception as e:
            logger.error(f"ディスカッション作成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def reply_to_discussion(self, user_id: str, discussion_id: str, content: str, 
                           parent_reply_id: str = None) -> Dict[str, Any]:
        """ディスカッション返信"""
        try:
            discussions = self._load_discussions()
            
            if discussion_id not in discussions:
                return {'success': False, 'error': 'ディスカッションが見つかりません'}
            
            reply_id = hashlib.md5(f"{content}{user_id}{datetime.now()}".encode()).hexdigest()[:8]
            
            reply = {
                'id': reply_id,
                'content': content,
                'author_id': user_id,
                'created_at': datetime.now().isoformat(),
                'parent_reply_id': parent_reply_id,
                'votes': {'up': 0, 'down': 0, 'voters': []},
                'is_solution': False
            }
            
            discussions[discussion_id]['replies'].append(reply)
            discussions[discussion_id]['updated_at'] = datetime.now().isoformat()
            
            self._save_discussions(discussions)
            
            logger.info(f"ディスカッション返信: ユーザー{user_id} → ディスカッション{discussion_id}")
            return {
                'success': True,
                'reply_id': reply_id,
                'reply': reply
            }
            
        except Exception as e:
            logger.error(f"ディスカッション返信エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_discussions(self, group_id: str = None, category: str = None, 
                       question_id: int = None, limit: int = 20) -> List[Dict[str, Any]]:
        """ディスカッション一覧取得"""
        try:
            discussions = self._load_discussions()
            
            filtered_discussions = []
            
            for discussion_id, discussion in discussions.items():
                # フィルタ適用
                if group_id and discussion.get('group_id') != group_id:
                    continue
                if category and discussion.get('category') != category:
                    continue
                if question_id and discussion.get('question_id') != question_id:
                    continue
                
                # 簡略化された情報を返す
                filtered_discussions.append({
                    'id': discussion_id,
                    'title': discussion['title'],
                    'author_id': discussion['author_id'],
                    'category': discussion['category'],
                    'created_at': discussion['created_at'],
                    'updated_at': discussion['updated_at'],
                    'reply_count': len(discussion['replies']),
                    'vote_score': discussion['votes']['up'] - discussion['votes']['down'],
                    'is_solved': discussion['is_solved'],
                    'is_pinned': discussion['is_pinned'],
                    'view_count': discussion['view_count'],
                    'tags': discussion['tags']
                })
            
            # ソート（ピン留め → 更新日時順）
            filtered_discussions.sort(
                key=lambda x: (not x['is_pinned'], x['updated_at']), 
                reverse=True
            )
            
            return filtered_discussions[:limit]
            
        except Exception as e:
            logger.error(f"ディスカッション一覧取得エラー: {e}")
            return []
    
    def get_discussion_detail(self, discussion_id: str, viewer_id: str = None) -> Dict[str, Any]:
        """ディスカッション詳細取得"""
        try:
            discussions = self._load_discussions()
            
            if discussion_id not in discussions:
                return {'error': 'ディスカッションが見つかりません'}
            
            discussion = discussions[discussion_id].copy()
            
            # 閲覧数増加
            if viewer_id:
                discussion['view_count'] += 1
                discussions[discussion_id]['view_count'] = discussion['view_count']
                self._save_discussions(discussions)
            
            return discussion
            
        except Exception as e:
            logger.error(f"ディスカッション詳細取得エラー: {e}")
            return {'error': str(e)}
    
    # === 協調学習機能 ===
    
    def create_study_session(self, creator_id: str, group_id: str, session_name: str,
                           scheduled_time: str, session_type: str = 'group_study') -> Dict[str, Any]:
        """学習セッション作成"""
        try:
            session_id = hashlib.md5(f"{session_name}{creator_id}{datetime.now()}".encode()).hexdigest()[:12]
            
            session = {
                'id': session_id,
                'name': session_name,
                'creator_id': creator_id,
                'group_id': group_id,
                'session_type': session_type,
                'scheduled_time': scheduled_time,
                'created_at': datetime.now().isoformat(),
                'status': 'scheduled',
                'participants': [creator_id],
                'settings': {
                    'max_participants': 10,
                    'question_count': 20,
                    'time_limit': 3600,  # 1時間
                    'competitive_mode': False
                },
                'results': []
            }
            
            # セッションファイルに保存
            sessions_file = os.path.join(self.social_data_dir, 'study_sessions.json')
            sessions = self._load_json_file(sessions_file, {})
            sessions[session_id] = session
            self._save_json_file(sessions_file, sessions)
            
            logger.info(f"学習セッション作成: {session_name} (ID: {session_id})")
            return {
                'success': True,
                'session_id': session_id,
                'session': session
            }
            
        except Exception as e:
            logger.error(f"学習セッション作成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_recommended_study_partners(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """学習パートナー推奨"""
        try:
            user_data = self._load_user_data(user_id)
            all_users = self._load_all_user_data()
            
            if not user_data:
                return []
            
            recommendations = []
            
            for other_id, other_data in all_users.items():
                if other_id == user_id:
                    continue
                
                # 類似度計算
                similarity_score = self._calculate_user_similarity(user_data, other_data)
                
                if similarity_score > 0.3:  # 閾値
                    recommendations.append({
                        'user_id': other_id,
                        'similarity_score': similarity_score,
                        'common_interests': self._find_common_interests(user_data, other_data),
                        'study_level': self._assess_study_level(other_data),
                        'activity_level': self._assess_activity_level(other_data)
                    })
            
            # 類似度順でソート
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"学習パートナー推奨エラー: {e}")
            return []
    
    # === プライベートメソッド ===
    
    def _load_groups(self) -> Dict[str, Any]:
        """グループデータ読み込み"""
        return self._load_json_file(self.groups_file, {})
    
    def _save_groups(self, groups: Dict[str, Any]):
        """グループデータ保存"""
        self._save_json_file(self.groups_file, groups)
    
    def _load_discussions(self) -> Dict[str, Any]:
        """ディスカッションデータ読み込み"""
        return self._load_json_file(self.discussions_file, {})
    
    def _save_discussions(self, discussions: Dict[str, Any]):
        """ディスカッションデータ保存"""
        self._save_json_file(self.discussions_file, discussions)
    
    def _load_json_file(self, filepath: str, default: Any) -> Any:
        """JSONファイル読み込み"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.warning(f"JSONファイル読み込みエラー {filepath}: {e}")
            return default
    
    def _save_json_file(self, filepath: str, data: Any):
        """JSONファイル保存"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"JSONファイル保存エラー {filepath}: {e}")
    
    def _load_user_data(self, user_id: str) -> Dict[str, Any]:
        """ユーザーデータ読み込み"""
        filepath = os.path.join(self.user_data_dir, f"{user_id}.json")
        return self._load_json_file(filepath, {})
    
    def _load_all_user_data(self) -> Dict[str, Dict[str, Any]]:
        """全ユーザーデータ読み込み"""
        all_users = {}
        
        if not os.path.exists(self.user_data_dir):
            return all_users
        
        for filename in os.listdir(self.user_data_dir):
            if filename.endswith('.json'):
                user_id = filename[:-5]
                all_users[user_id] = self._load_user_data(user_id)
        
        return all_users
    
    def _calculate_group_match_score(self, user_data: Dict, group: Dict) -> float:
        """グループマッチスコア計算"""
        score = 0.0
        
        # 部門一致
        if group.get('department') == self._get_primary_department(user_data.get('history', [])):
            score += 0.4
        
        # 学習レベル類似性
        user_level = self._assess_study_level(user_data)
        # グループの平均レベルとの比較（簡略化）
        score += 0.3
        
        # アクティビティレベル
        if self._assess_activity_level(user_data) == 'high':
            score += 0.3
        
        return min(score, 1.0)
    
    def _get_match_reasons(self, user_data: Dict, group: Dict) -> List[str]:
        """マッチ理由取得"""
        reasons = []
        
        if group.get('department') == self._get_primary_department(user_data.get('history', [])):
            reasons.append('同じ専門分野')
        
        if group.get('target_exam_date'):
            reasons.append('試験日程が近い')
        
        if len(group['members']) < 10:
            reasons.append('小規模で親密な学習環境')
        
        return reasons
    
    def _record_group_activity(self, group_id: str, activity_type: str, user_id: str, message: str):
        """グループ活動記録"""
        # 簡略化実装
        logger.info(f"グループ活動: {group_id} - {activity_type} - {message}")
    
    def _get_recent_group_activity(self, group_id: str) -> List[Dict[str, Any]]:
        """最近のグループ活動取得"""
        # 簡略化実装
        return []
    
    def _select_peers(self, user_id: str, user_data: Dict, all_users: Dict, comparison_type: str) -> List[Dict]:
        """ピア選択"""
        peers = []
        user_dept = self._get_primary_department(user_data.get('history', []))
        
        for other_id, other_data in all_users.items():
            if other_id == user_id:
                continue
            
            if comparison_type == 'department':
                other_dept = self._get_primary_department(other_data.get('history', []))
                if user_dept == other_dept:
                    peers.append(other_data)
            elif comparison_type == 'level':
                user_level = self._assess_study_level(user_data)
                other_level = self._assess_study_level(other_data)
                if user_level == other_level:
                    peers.append(other_data)
        
        return peers[:20]  # 最大20人
    
    def _calculate_user_stats(self, user_data: Dict) -> Dict[str, Any]:
        """ユーザー統計計算"""
        history = user_data.get('history', [])
        
        if not history:
            return {}
        
        correct_count = sum(1 for h in history if h.get('is_correct', False))
        
        return {
            'total_questions': len(history),
            'accuracy': correct_count / len(history),
            'study_streak': self._calculate_study_streak(history),
            'primary_department': self._get_primary_department(history),
            'study_level': self._assess_study_level(user_data)
        }
    
    def _calculate_peer_stats(self, peers: List[Dict]) -> Dict[str, Any]:
        """ピア統計計算"""
        if not peers:
            return {}
        
        total_questions = [len(peer.get('history', [])) for peer in peers]
        accuracies = []
        
        for peer in peers:
            history = peer.get('history', [])
            if history:
                correct = sum(1 for h in history if h.get('is_correct', False))
                accuracies.append(correct / len(history))
        
        return {
            'peer_count': len(peers),
            'avg_total_questions': sum(total_questions) / len(total_questions) if total_questions else 0,
            'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            'accuracy_range': {
                'min': min(accuracies) if accuracies else 0,
                'max': max(accuracies) if accuracies else 0
            }
        }
    
    def _calculate_rankings(self, user_id: str, user_data: Dict, peers: List[Dict]) -> Dict[str, Any]:
        """ランキング計算"""
        user_score = self._calculate_leaderboard_score(user_data.get('history', []))
        peer_scores = [self._calculate_leaderboard_score(peer.get('history', [])) for peer in peers]
        
        all_scores = peer_scores + [user_score]
        all_scores.sort(reverse=True)
        
        user_rank = all_scores.index(user_score) + 1
        
        return {
            'user_rank': user_rank,
            'total_peers': len(peers) + 1,
            'percentile': (len(peers) + 1 - user_rank) / (len(peers) + 1) * 100
        }
    
    def _generate_improvement_suggestions(self, user_data: Dict, peers: List[Dict]) -> List[str]:
        """改善提案生成"""
        suggestions = []
        
        user_accuracy = self._calculate_user_stats(user_data)['accuracy']
        peer_stats = self._calculate_peer_stats(peers)
        
        if user_accuracy < peer_stats['avg_accuracy']:
            suggestions.append("同レベルの学習者と比べて正答率が低めです。基礎固めに重点を置きましょう")
        
        if len(user_data.get('history', [])) < peer_stats['avg_total_questions']:
            suggestions.append("学習量を増やすことで成績向上が期待できます")
        
        return suggestions
    
    def _get_time_cutoff(self, time_period: str) -> Optional[datetime]:
        """時間期間のカットオフ日取得"""
        now = datetime.now()
        
        if time_period == 'week':
            return now - timedelta(weeks=1)
        elif time_period == 'month':
            return now - timedelta(days=30)
        elif time_period == 'year':
            return now - timedelta(days=365)
        else:
            return None
    
    def _calculate_leaderboard_score(self, history: List[Dict]) -> float:
        """リーダーボードスコア計算"""
        if not history:
            return 0
        
        # 正答率 × 問題数 × 継続性ボーナス
        correct_count = sum(1 for h in history if h.get('is_correct', False))
        accuracy = correct_count / len(history)
        volume_bonus = min(len(history) / 100, 2.0)  # 最大2倍
        streak_bonus = self._calculate_study_streak(history) / 10  # 連続日数ボーナス
        
        return accuracy * volume_bonus * (1 + streak_bonus)
    
    def _calculate_study_streak(self, history: List[Dict]) -> int:
        """学習連続日数計算"""
        if not history:
            return 0
        
        # 簡略化実装
        dates = set()
        for entry in history:
            try:
                date_str = entry.get('date', '')
                if date_str:
                    date = datetime.fromisoformat(date_str).date()
                    dates.add(date)
            except (ValueError, TypeError):
                continue
        
        return len(dates)
    
    def _get_primary_department(self, history: List[Dict]) -> str:
        """主要学習部門取得"""
        if not history:
            return 'unknown'
        
        dept_counts = Counter(h.get('department', 'unknown') for h in history)
        return dept_counts.most_common(1)[0][0]
    
    def _assess_study_level(self, user_data: Dict) -> str:
        """学習レベル評価"""
        history = user_data.get('history', [])
        
        if len(history) < 10:
            return 'beginner'
        elif len(history) < 50:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _assess_activity_level(self, user_data: Dict) -> str:
        """アクティビティレベル評価"""
        history = user_data.get('history', [])
        
        if len(history) >= 100:
            return 'high'
        elif len(history) >= 30:
            return 'medium'
        else:
            return 'low'
    
    def _extract_tags(self, content: str) -> List[str]:
        """コンテンツからタグ抽出"""
        # 簡略化実装
        keywords = ['基礎', '専門', '難しい', '計算', '法規', '設計', '施工']
        tags = []
        
        for keyword in keywords:
            if keyword in content:
                tags.append(keyword)
        
        return tags[:5]  # 最大5つ
    
    def _update_group_discussion_count(self, group_id: str):
        """グループディスカッション数更新"""
        try:
            groups = self._load_groups()
            if group_id in groups:
                groups[group_id]['statistics']['discussions_count'] += 1
                self._save_groups(groups)
        except Exception as e:
            logger.error(f"グループディスカッション数更新エラー: {e}")
    
    def _calculate_user_similarity(self, user_data: Dict, other_data: Dict) -> float:
        """ユーザー間類似度計算"""
        score = 0.0
        
        # 部門類似性
        user_dept = self._get_primary_department(user_data.get('history', []))
        other_dept = self._get_primary_department(other_data.get('history', []))
        if user_dept == other_dept:
            score += 0.4
        
        # レベル類似性
        user_level = self._assess_study_level(user_data)
        other_level = self._assess_study_level(other_data)
        if user_level == other_level:
            score += 0.3
        
        # アクティビティ類似性
        user_activity = self._assess_activity_level(user_data)
        other_activity = self._assess_activity_level(other_data)
        if user_activity == other_activity:
            score += 0.3
        
        return score
    
    def _find_common_interests(self, user_data: Dict, other_data: Dict) -> List[str]:
        """共通興味分野特定"""
        user_history = user_data.get('history', [])
        other_history = other_data.get('history', [])
        
        user_categories = set(h.get('category', '') for h in user_history)
        other_categories = set(h.get('category', '') for h in other_history)
        
        common = user_categories.intersection(other_categories)
        return list(common)[:5]  # 最大5つ

# グローバルインスタンス
social_learning_manager = SocialLearningManager()