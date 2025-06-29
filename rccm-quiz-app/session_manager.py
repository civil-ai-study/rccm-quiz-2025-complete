"""
RCCM学習アプリ - 次世代セッション管理システム
Redis + Flask-Session 統合セッション管理
"""

import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import session, request, current_app
import redis
from redis_config import redis_session_manager, SessionConfig

logger = logging.getLogger(__name__)


class AdvancedSessionManager:
    """次世代セッション管理システム"""
    
    def __init__(self):
        self.redis_client = None
        self.session_stats = {}
        self.migration_log = []
        
    def initialize(self):
        """セッション管理システム初期化"""
        try:
            self.redis_client = redis_session_manager.redis_client
            if not self.redis_client:
                raise ConnectionError("Redis接続が利用できません")
            
            logger.info("✅ 次世代セッション管理システム初期化完了")
            return True
            
        except Exception as e:
            logger.error(f"セッション管理システム初期化エラー: {e}")
            return False
    
    def migrate_file_session_to_redis(self, file_session_dir: str) -> Dict[str, Any]:
        """ファイルベースセッションからRedisへの移行"""
        migration_result = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'migrated_sessions': []
        }
        
        try:
            import os
            import glob
            
            if not os.path.exists(file_session_dir):
                logger.warning(f"セッションディレクトリが存在しません: {file_session_dir}")
                return migration_result
            
            # ファイルセッション検索
            session_files = glob.glob(os.path.join(file_session_dir, 'session_*'))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'rb') as f:
                        # セッションデータ読み込み
                        session_data = pickle.load(f)
                    
                    # セッションID抽出
                    session_id = os.path.basename(session_file).replace('session_', '')
                    
                    # Redisにマイグレーション
                    redis_key = f"{SessionConfig.SESSION_KEY_PREFIX}{session_id}"
                    
                    # セッションデータをJSON形式で保存
                    redis_data = self._serialize_session_data(session_data)
                    
                    # TTL設定付きで保存
                    self.redis_client.setex(
                        redis_key,
                        int(SessionConfig.PERMANENT_SESSION_LIFETIME.total_seconds()),
                        redis_data
                    )
                    
                    migration_result['success'] += 1
                    migration_result['migrated_sessions'].append({
                        'session_id': session_id,
                        'file_path': session_file,
                        'redis_key': redis_key,
                        'data_size': len(redis_data)
                    })
                    
                    logger.info(f"セッション移行成功: {session_id}")
                    
                except Exception as e:
                    migration_result['failed'] += 1
                    migration_result['errors'].append(f"{session_file}: {str(e)}")
                    logger.error(f"セッション移行エラー {session_file}: {e}")
            
            # 移行ログ記録
            self.migration_log.append({
                'timestamp': datetime.now().isoformat(),
                'source_dir': file_session_dir,
                'result': migration_result
            })
            
            logger.info(f"セッション移行完了: 成功={migration_result['success']}, 失敗={migration_result['failed']}")
            
        except Exception as e:
            migration_result['errors'].append(f"Migration process error: {str(e)}")
            logger.error(f"セッション移行プロセスエラー: {e}")
        
        return migration_result
    
    def _serialize_session_data(self, session_data: Dict[str, Any]) -> str:
        """セッションデータのシリアライズ（Redis互換）"""
        try:
            # 特殊オブジェクトの処理
            serializable_data = {}
            
            for key, value in session_data.items():
                try:
                    # JSON serializable チェック
                    json.dumps(value)
                    serializable_data[key] = value
                except (TypeError, ValueError):
                    # 特殊オブジェクトを文字列に変換
                    if isinstance(value, datetime):
                        serializable_data[key] = value.isoformat()
                    elif hasattr(value, '__dict__'):
                        serializable_data[key] = str(value)
                    else:
                        serializable_data[key] = repr(value)
            
            return json.dumps(serializable_data, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"セッションデータシリアライズエラー: {e}")
            # フォールバック: pickle
            return pickle.dumps(session_data).decode('latin1')
    
    def create_session_backup(self, backup_key: str = None) -> str:
        """現在のセッション状態のバックアップ作成"""
        try:
            if not backup_key:
                backup_key = f"session_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 全セッションキー取得
            session_keys = self.redis_client.keys(f"{SessionConfig.SESSION_KEY_PREFIX}*")
            
            backup_data = {}
            for key in session_keys:
                try:
                    session_data = self.redis_client.get(key)
                    ttl = self.redis_client.ttl(key)
                    
                    backup_data[key] = {
                        'data': session_data,
                        'ttl': ttl
                    }
                except Exception as e:
                    logger.warning(f"セッションバックアップ取得エラー {key}: {e}")
            
            # バックアップ保存
            backup_json = json.dumps(backup_data, ensure_ascii=False)
            backup_redis_key = f"rccm_session_backup:{backup_key}"
            
            # 7日間保持
            self.redis_client.setex(backup_redis_key, 7*24*3600, backup_json)
            
            logger.info(f"セッションバックアップ作成: {backup_key} ({len(backup_data)}セッション)")
            return backup_key
            
        except Exception as e:
            logger.error(f"セッションバックアップエラー: {e}")
            return None
    
    def restore_session_backup(self, backup_key: str) -> bool:
        """セッションバックアップからの復旧"""
        try:
            backup_redis_key = f"rccm_session_backup:{backup_key}"
            backup_json = self.redis_client.get(backup_redis_key)
            
            if not backup_json:
                logger.error(f"バックアップが見つかりません: {backup_key}")
                return False
            
            backup_data = json.loads(backup_json)
            
            restored_count = 0
            for session_key, session_info in backup_data.items():
                try:
                    session_data = session_info['data']
                    ttl = session_info.get('ttl', 3600)
                    
                    if ttl > 0:
                        self.redis_client.setex(session_key, ttl, session_data)
                    else:
                        self.redis_client.set(session_key, session_data)
                    
                    restored_count += 1
                    
                except Exception as e:
                    logger.warning(f"セッション復旧エラー {session_key}: {e}")
            
            logger.info(f"セッション復旧完了: {restored_count}セッション復旧")
            return True
            
        except Exception as e:
            logger.error(f"セッション復旧エラー: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """期限切れセッションのクリーンアップ"""
        try:
            session_keys = self.redis_client.keys(f"{SessionConfig.SESSION_KEY_PREFIX}*")
            
            cleaned_count = 0
            for key in session_keys:
                try:
                    ttl = self.redis_client.ttl(key)
                    if ttl == -1:  # TTLが設定されていない
                        # デフォルトTTL設定
                        self.redis_client.expire(key, int(SessionConfig.PERMANENT_SESSION_LIFETIME.total_seconds()))
                    elif ttl == -2:  # キーが存在しない
                        cleaned_count += 1
                        
                except Exception as e:
                    logger.warning(f"セッションクリーンアップエラー {key}: {e}")
            
            logger.info(f"期限切れセッションクリーンアップ: {cleaned_count}セッション削除")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"セッションクリーンアップエラー: {e}")
            return 0
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """セッション分析データ取得"""
        try:
            session_keys = self.redis_client.keys(f"{SessionConfig.SESSION_KEY_PREFIX}*")
            
            analytics = {
                'total_sessions': len(session_keys),
                'session_sizes': [],
                'ttl_distribution': [],
                'active_sessions': 0,
                'recent_sessions': 0
            }
            
            now = datetime.now()
            recent_threshold = now - timedelta(hours=1)
            
            for key in session_keys[:1000]:  # サンプリング制限
                try:
                    # セッションサイズ
                    size = self.redis_client.memory_usage(key) or 0
                    analytics['session_sizes'].append(size)
                    
                    # TTL情報
                    ttl = self.redis_client.ttl(key)
                    if ttl > 0:
                        analytics['ttl_distribution'].append(ttl)
                        analytics['active_sessions'] += 1
                    
                    # 最近のアクティビティ
                    session_data_str = self.redis_client.get(key)
                    if session_data_str:
                        try:
                            session_data = json.loads(session_data_str)
                            last_access = session_data.get('_permanent', {}).get('last_access')
                            if last_access:
                                last_access_dt = datetime.fromisoformat(last_access)
                                if last_access_dt > recent_threshold:
                                    analytics['recent_sessions'] += 1
                        except:
                            pass
                            
                except Exception as e:
                    logger.debug(f"セッション分析エラー {key}: {e}")
            
            # 統計計算
            if analytics['session_sizes']:
                analytics['avg_session_size'] = sum(analytics['session_sizes']) / len(analytics['session_sizes'])
                analytics['max_session_size'] = max(analytics['session_sizes'])
            
            if analytics['ttl_distribution']:
                analytics['avg_ttl'] = sum(analytics['ttl_distribution']) / len(analytics['ttl_distribution'])
            
            return analytics
            
        except Exception as e:
            logger.error(f"セッション分析エラー: {e}")
            return {}


# セッション関連デコレーター
def redis_session_required(f):
    """Redis セッション必須デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Redisセッション接続確認
            if not redis_session_manager.health_check():
                logger.warning("Redis接続不安定 - フォールバック処理")
                # フォールバック処理をここに実装
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Redis セッションエラー: {e}")
            # エラーハンドリング
            return {"error": "セッションエラーが発生しました"}, 500
    
    return decorated_function


def session_analytics(f):
    """セッション分析データ収集デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        
        try:
            result = f(*args, **kwargs)
            
            # セッション使用状況記録
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 分析データ収集（非同期）
            if redis_session_manager.redis_client:
                try:
                    analytics_key = "rccm_session_analytics"
                    analytics_data = {
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'duration': duration,
                        'timestamp': start_time.isoformat(),
                        'session_size': len(str(session)) if session else 0
                    }
                    
                    # 分析データ追加（リスト形式、最新1000件まで）
                    redis_session_manager.redis_client.lpush(
                        analytics_key, 
                        json.dumps(analytics_data)
                    )
                    redis_session_manager.redis_client.ltrim(analytics_key, 0, 999)
                    
                except Exception as analytics_error:
                    logger.debug(f"セッション分析データ収集エラー: {analytics_error}")
            
            return result
            
        except Exception as e:
            logger.error(f"セッション分析デコレーターエラー: {e}")
            raise
    
    return decorated_function


# グローバルセッション管理インスタンス
advanced_session_manager = AdvancedSessionManager()


def initialize_session_system():
    """セッションシステム初期化"""
    return advanced_session_manager.initialize()


def get_session_migration_status():
    """セッション移行状況取得"""
    return {
        'migration_log': advanced_session_manager.migration_log,
        'redis_status': redis_session_manager.health_check(),
        'session_stats': advanced_session_manager.get_session_analytics()
    }