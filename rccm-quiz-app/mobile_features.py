"""
RCCM学習アプリ - モバイル機能強化
PWA機能、オフライン対応、音声機能、タッチ操作最適化
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MobileFeatureManager:
    """モバイル機能管理クラス"""
    
    def __init__(self):
        self.offline_data_dir = 'offline_data'
        self.voice_settings = {
            'enabled': True,
            'language': 'ja-JP',
            'rate': 1.0,
            'pitch': 1.0,
            'volume': 0.8
        }
        
        # タッチジェスチャー設定
        self.touch_gestures = {
            'swipe_threshold': 50,  # px
            'tap_delay': 300,       # ms
            'long_press_delay': 500, # ms
            'double_tap_delay': 400  # ms
        }
        
        # オフライン同期設定
        self.sync_settings = {
            'auto_sync_enabled': True,
            'sync_interval_minutes': 30,
            'max_offline_sessions': 50,
            'max_offline_size_mb': 10
        }
        
        self._ensure_offline_dir()
    
    def _ensure_offline_dir(self):
        """オフラインデータディレクトリの作成"""
        if not os.path.exists(self.offline_data_dir):
            os.makedirs(self.offline_data_dir)
            logger.info(f"オフラインデータディレクトリを作成: {self.offline_data_dir}")
    
    def get_pwa_manifest(self) -> Dict[str, Any]:
        """PWAマニフェストの生成"""
        return {
            "name": "RCCM試験問題集 - AI学習アシスタント",
            "short_name": "RCCM問題集",
            "description": "AI搭載のRCCM試験対策アプリ - オフライン学習、音声読み上げ対応",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#667eea",
            "theme_color": "#667eea",
            "orientation": "portrait-primary",
            "scope": "/",
            "icons": [
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "categories": ["education", "productivity", "utilities"],
            "lang": "ja",
            "dir": "ltr",
            "shortcuts": [
                {
                    "name": "問題開始",
                    "short_name": "問題",
                    "description": "すぐに問題を開始",
                    "url": "/quiz?quick=true",
                    "icons": [{"src": "/static/icons/icon-96x96.png", "sizes": "96x96"}]
                },
                {
                    "name": "AI分析",
                    "short_name": "AI分析",
                    "description": "弱点分析を表示",
                    "url": "/ai_analysis",
                    "icons": [{"src": "/static/icons/icon-96x96.png", "sizes": "96x96"}]
                },
                {
                    "name": "模擬試験",
                    "short_name": "模擬試験",
                    "description": "試験シミュレーション",
                    "url": "/exam_simulator",
                    "icons": [{"src": "/static/icons/icon-96x96.png", "sizes": "96x96"}]
                },
                {
                    "name": "統計",
                    "short_name": "統計",
                    "description": "学習統計を確認",
                    "url": "/statistics",
                    "icons": [{"src": "/static/icons/icon-96x96.png", "sizes": "96x96"}]
                }
            ],
            "screenshots": [
                {
                    "src": "/static/screenshots/desktop-1.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide",
                    "label": "デスクトップ版メイン画面"
                },
                {
                    "src": "/static/screenshots/mobile-1.png", 
                    "sizes": "360x640",
                    "type": "image/png",
                    "form_factor": "narrow",
                    "label": "モバイル版問題画面"
                }
            ],
            "related_applications": [],
            "prefer_related_applications": False
        }
    
    def save_offline_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """オフラインセッションの保存"""
        try:
            file_path = os.path.join(self.offline_data_dir, f"session_{session_id}.json")
            
            # データサイズチェック
            data_str = json.dumps(session_data, ensure_ascii=False)
            size_mb = len(data_str.encode('utf-8')) / (1024 * 1024)
            
            if size_mb > self.sync_settings['max_offline_size_mb']:
                logger.warning(f"セッションデータが大きすぎます: {size_mb:.2f}MB")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'session_id': session_id,
                    'data': session_data,
                    'saved_at': datetime.now().isoformat(),
                    'size_mb': size_mb
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"オフラインセッション保存: {session_id} ({size_mb:.2f}MB)")
            return True
            
        except Exception as e:
            logger.error(f"オフラインセッション保存エラー: {e}")
            return False
    
    def load_offline_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """オフラインセッションの読み込み"""
        try:
            file_path = os.path.join(self.offline_data_dir, f"session_{session_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"オフラインセッション読み込み: {session_id}")
            return data.get('data')
            
        except Exception as e:
            logger.error(f"オフラインセッション読み込みエラー: {e}")
            return None
    
    def get_offline_sessions(self) -> List[Dict[str, Any]]:
        """オフラインセッション一覧の取得"""
        sessions = []
        
        try:
            for filename in os.listdir(self.offline_data_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    file_path = os.path.join(self.offline_data_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        'session_id': data['session_id'],
                        'saved_at': data['saved_at'],
                        'size_mb': data.get('size_mb', 0),
                        'filename': filename
                    })
            
            # 保存日時でソート
            sessions.sort(key=lambda x: x['saved_at'], reverse=True)
            
            # 最大数を超えている場合は古いものを削除
            if len(sessions) > self.sync_settings['max_offline_sessions']:
                for session in sessions[self.sync_settings['max_offline_sessions']:]:
                    self.delete_offline_session(session['session_id'])
                sessions = sessions[:self.sync_settings['max_offline_sessions']]
            
            return sessions
            
        except Exception as e:
            logger.error(f"オフラインセッション一覧取得エラー: {e}")
            return []
    
    def delete_offline_session(self, session_id: str) -> bool:
        """オフラインセッションの削除"""
        try:
            file_path = os.path.join(self.offline_data_dir, f"session_{session_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"オフラインセッション削除: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"オフラインセッション削除エラー: {e}")
            return False
    
    def sync_offline_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """オフラインデータの同期"""
        sync_result = {
            'success': False,
            'synced_sessions': 0,
            'failed_sessions': 0,
            'errors': []
        }
        
        try:
            offline_sessions = self.get_offline_sessions()
            
            for session_info in offline_sessions:
                session_id = session_info['session_id']
                
                try:
                    # オフラインデータをメインセッションにマージ
                    offline_data = self.load_offline_session(session_id)
                    
                    if offline_data:
                        self._merge_session_data(session_data, offline_data)
                        self.delete_offline_session(session_id)
                        sync_result['synced_sessions'] += 1
                        
                except Exception as e:
                    sync_result['failed_sessions'] += 1
                    sync_result['errors'].append(f"セッション {session_id}: {str(e)}")
                    logger.error(f"セッション同期エラー ({session_id}): {e}")
            
            sync_result['success'] = sync_result['failed_sessions'] == 0
            logger.info(f"オフライン同期完了: 成功{sync_result['synced_sessions']}, 失敗{sync_result['failed_sessions']}")
            
            return sync_result
            
        except Exception as e:
            sync_result['errors'].append(str(e))
            logger.error(f"オフライン同期エラー: {e}")
            return sync_result
    
    def _merge_session_data(self, main_data: Dict[str, Any], offline_data: Dict[str, Any]):
        """セッションデータのマージ"""
        # 履歴のマージ
        if 'history' in offline_data:
            if 'history' not in main_data:
                main_data['history'] = []
            main_data['history'].extend(offline_data['history'])
        
        # SRSデータのマージ
        if 'srs_data' in offline_data:
            if 'srs_data' not in main_data:
                main_data['srs_data'] = {}
            main_data['srs_data'].update(offline_data['srs_data'])
        
        # 統計データのマージ
        if 'category_stats' in offline_data:
            if 'category_stats' not in main_data:
                main_data['category_stats'] = {}
            
            for category, stats in offline_data['category_stats'].items():
                if category in main_data['category_stats']:
                    main_data['category_stats'][category]['total'] += stats.get('total', 0)
                    main_data['category_stats'][category]['correct'] += stats.get('correct', 0)
                else:
                    main_data['category_stats'][category] = stats
        
        # バッジデータのマージ
        if 'earned_badges' in offline_data:
            if 'earned_badges' not in main_data:
                main_data['earned_badges'] = []
            
            for badge in offline_data['earned_badges']:
                if badge not in main_data['earned_badges']:
                    main_data['earned_badges'].append(badge)
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """音声設定の取得"""
        return self.voice_settings.copy()
    
    def update_voice_settings(self, settings: Dict[str, Any]) -> bool:
        """音声設定の更新"""
        try:
            for key, value in settings.items():
                if key in self.voice_settings:
                    self.voice_settings[key] = value
            
            logger.info("音声設定を更新")
            return True
            
        except Exception as e:
            logger.error(f"音声設定更新エラー: {e}")
            return False
    
    def get_touch_settings(self) -> Dict[str, Any]:
        """タッチジェスチャー設定の取得"""
        return self.touch_gestures.copy()
    
    def update_touch_settings(self, settings: Dict[str, Any]) -> bool:
        """タッチジェスチャー設定の更新"""
        try:
            for key, value in settings.items():
                if key in self.touch_gestures:
                    self.touch_gestures[key] = value
            
            logger.info("タッチ設定を更新")
            return True
            
        except Exception as e:
            logger.error(f"タッチ設定更新エラー: {e}")
            return False
    
    def get_mobile_optimized_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """モバイル最適化された問題データの生成"""
        mobile_question = question.copy()
        
        # 長いテキストの調整
        if len(mobile_question.get('question', '')) > 200:
            mobile_question['has_long_text'] = True
        
        # 画像がある場合の最適化フラグ
        if 'image' in mobile_question or 'diagram' in mobile_question:
            mobile_question['has_image'] = True
        
        # 音声読み上げ用テキストの準備
        mobile_question['speech_text'] = self._prepare_speech_text(mobile_question)
        
        return mobile_question
    
    def _prepare_speech_text(self, question: Dict[str, Any]) -> str:
        """音声読み上げ用テキストの準備"""
        speech_parts = []
        
        # 問題文
        if question.get('question'):
            speech_parts.append(f"問題。{question['question']}")
        
        # 選択肢
        for option in ['a', 'b', 'c', 'd']:
            option_text = question.get(f'option_{option}')
            if option_text:
                speech_parts.append(f"選択肢{option.upper()}。{option_text}")
        
        return '。'.join(speech_parts)
    
    def generate_mobile_cache_data(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """モバイル用キャッシュデータの生成"""
        # 基本的な問題データ（重要な情報のみ）
        essential_questions = []
        
        for q in questions[:100]:  # 最初の100問のみキャッシュ
            essential_q = {
                'id': q.get('id'),
                'category': q.get('category'),
                'difficulty': q.get('difficulty'),
                'question': q.get('question'),
                'option_a': q.get('option_a'),
                'option_b': q.get('option_b'),
                'option_c': q.get('option_c'),
                'option_d': q.get('option_d'),
                'correct_answer': q.get('correct_answer')
            }
            essential_questions.append(essential_q)
        
        # カテゴリ情報
        categories = list(set(q.get('category') for q in questions if q.get('category')))
        
        # 難易度情報
        difficulties = list(set(q.get('difficulty') for q in questions if q.get('difficulty')))
        
        cache_data = {
            'questions': essential_questions,
            'categories': categories,
            'difficulties': difficulties,
            'cached_at': datetime.now().isoformat(),
            'version': '1.0',
            'total_available': len(questions)
        }
        
        return cache_data
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス指標の取得"""
        try:
            offline_sessions = self.get_offline_sessions()
            total_size = sum(session.get('size_mb', 0) for session in offline_sessions)
            
            return {
                'offline_sessions_count': len(offline_sessions),
                'total_offline_size_mb': round(total_size, 2),
                'cache_usage_percent': min(100, (total_size / self.sync_settings['max_offline_size_mb']) * 100),
                'auto_sync_enabled': self.sync_settings['auto_sync_enabled'],
                'voice_enabled': self.voice_settings['enabled'],
                'last_sync': self._get_last_sync_time()
            }
            
        except Exception as e:
            logger.error(f"パフォーマンス指標取得エラー: {e}")
            return {}
    
    def _get_last_sync_time(self) -> Optional[str]:
        """最後の同期時間の取得"""
        try:
            sync_file = os.path.join(self.offline_data_dir, 'last_sync.txt')
            if os.path.exists(sync_file):
                with open(sync_file, 'r') as f:
                    return f.read().strip()
            return None
        except:
            return None
    
    def update_last_sync_time(self):
        """最後の同期時間の更新"""
        try:
            sync_file = os.path.join(self.offline_data_dir, 'last_sync.txt')
            with open(sync_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"同期時間更新エラー: {e}")

# グローバルインスタンス
mobile_manager = MobileFeatureManager()