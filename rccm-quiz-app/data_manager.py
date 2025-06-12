"""
RCCM学習アプリ - データ永続化管理
セッションデータの永続化とバックアップ
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """
    学習データの永続化管理
    セッション + ファイル保存のハイブリッド方式
    """
    
    def __init__(self, data_dir: str = 'user_data'):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """データディレクトリの作成"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"データディレクトリ作成: {self.data_dir}")
    
    def get_user_id(self, session_id: str) -> str:
        """
        セッションIDからユーザーIDを生成
        プライバシー保護のため、ハッシュ化
        """
        return hashlib.md5(session_id.encode()).hexdigest()[:12]
    
    def save_user_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        ユーザーデータの保存
        """
        try:
            user_id = self.get_user_id(session_id)
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            # 既存データがあれば読み込み
            existing_data = {}
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"既存データ読み込みエラー: {e}")
            
            # データ更新
            existing_data.update(data)
            existing_data['last_updated'] = datetime.now().isoformat()
            existing_data['user_id'] = user_id
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"ユーザーデータ保存完了: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザーデータ保存エラー: {e}")
            return False
    
    def load_user_data(self, session_id: str) -> Dict[str, Any]:
        """
        ユーザーデータの読み込み
        """
        try:
            user_id = self.get_user_id(session_id)
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            if not os.path.exists(file_path):
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"ユーザーデータ読み込み完了: {user_id}")
            return data
            
        except Exception as e:
            logger.error(f"ユーザーデータ読み込みエラー: {e}")
            return {}
    
    def backup_user_data(self, session_id: str) -> bool:
        """
        ユーザーデータのバックアップ
        """
        try:
            user_id = self.get_user_id(session_id)
            source_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            if not os.path.exists(source_path):
                return True  # データがない場合は成功とみなす
            
            # バックアップディレクトリ
            backup_dir = os.path.join(self.data_dir, 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # バックアップファイル名（タイムスタンプ付き）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"{user_id}_{timestamp}.json")
            
            # バックアップ実行
            import shutil
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"ユーザーデータバックアップ完了: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザーデータバックアップエラー: {e}")
            return False
    
    def get_data_export(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        データエクスポート用
        """
        try:
            data = self.load_user_data(session_id)
            if not data:
                return None
            
            # エクスポート用データ構造
            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': self.get_user_id(session_id),
                'study_history': data.get('history', []),
                'srs_data': data.get('srs_data', {}),
                'category_stats': data.get('category_stats', {}),
                'bookmarks': data.get('bookmarks', []),
                'total_questions': len(data.get('history', [])),
                'study_days': len(set(h.get('date', '')[:10] for h in data.get('history', []) if h.get('date')))
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"データエクスポートエラー: {e}")
            return None

# Flask拡張: セッション + ファイル保存の統合
class SessionDataManager:
    """
    セッションとファイル保存を統合したデータ管理
    """
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def save_session_data(self, session, session_id: str):
        """
        セッションデータをファイルに保存
        """
        # 保存対象データの選択
        save_data = {
            'history': session.get('history', []),
            'srs_data': session.get('srs_data', {}),
            'category_stats': session.get('category_stats', {}),
        }
        
        # LocalStorageデータは含めない（クライアント側で管理）
        return self.data_manager.save_user_data(session_id, save_data)
    
    def load_session_data(self, session, session_id: str):
        """
        ファイルからセッションデータを復元
        """
        data = self.data_manager.load_user_data(session_id)
        
        if data:
            session['history'] = data.get('history', [])
            session['srs_data'] = data.get('srs_data', {}),
            session['category_stats'] = data.get('category_stats', {}),
            session.modified = True
            
            logger.info("セッションデータ復元完了")
            return True
        
        return False
    
    def auto_save_trigger(self, session, session_id: str):
        """
        自動保存のトリガー
        """
        # 一定の条件で自動保存
        history_count = len(session.get('history', []))
        
        # 10問ごと、または1時間ごとに自動保存
        if history_count > 0 and (history_count % 10 == 0):
            return self.save_session_data(session, session_id)
        
        return True 