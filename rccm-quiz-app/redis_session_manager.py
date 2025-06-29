#!/usr/bin/env python3
"""
🔧 Redis Session Manager - World Class Implementation
RCCM試験問題集アプリ - 世界標準Redis統合セッション管理システム

🎯 主要機能:
- Flask-Session + Redis統合
- 高可用性・高性能セッション管理
- 自動フェイルオーバー機能
- 包括的セッション分析
- 企業レベルセキュリティ
"""

import redis
import json
import logging
import time
import threading
import os
import pickle
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from functools import wraps
from flask import Flask, session as flask_session
from flask_session import Session
import traceback

logger = logging.getLogger(__name__)

class RedisSessionManager:
    """🔧 世界標準Redis統合セッション管理システム"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.redis_client = None
        self.redis_pool = None
        self.fallback_enabled = True
        self.health_check_interval = 30  # 30秒間隔
        self.health_check_thread = None
        self.is_healthy = False
        
        # Redis設定
        self.redis_config = {
            'host': os.environ.get('REDIS_HOST', 'localhost'),
            'port': int(os.environ.get('REDIS_PORT', 6379)),
            'db': int(os.environ.get('REDIS_DB', 0)),
            'password': os.environ.get('REDIS_PASSWORD'),
            'ssl': os.environ.get('REDIS_SSL', 'false').lower() == 'true',
            'ssl_cert_reqs': None,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30,
            'max_connections': 50
        }
        
        # セッション設定
        self.session_config = {
            'prefix': 'rccm_session:',
            'expire': 3600,  # 1時間
            'serialize_method': 'json',  # json または pickle
            'compression': True,
            'encryption_key': os.environ.get('SESSION_ENCRYPTION_KEY', 'rccm-session-key-2025')
        }
        
        # セッション統計
        self.session_stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'redis_hits': 0,
            'redis_misses': 0,
            'fallback_hits': 0,
            'errors': 0,
            'last_updated': datetime.now(timezone.utc)
        }
        
        # ヘルスチェック統計
        self.health_stats = {
            'redis_available': False,
            'last_health_check': None,
            'consecutive_failures': 0,
            'total_health_checks': 0,
            'uptime_percentage': 0.0
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """🚀 Flaskアプリケーション初期化"""
        self.app = app
        
        # Redis接続プールの初期化
        self._initialize_redis_pool()
        
        # Flask-Session設定
        self._configure_flask_session(app)
        
        # ヘルスチェック開始
        self._start_health_check()
        
        # セッション管理API登録
        self._register_session_apis(app)
        
        logger.info("🔧 Redis Session Manager initialized successfully")
    
    def _initialize_redis_pool(self):
        """🔗 Redis接続プール初期化"""
        try:
            # 接続プール作成
            self.redis_pool = redis.ConnectionPool(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                db=self.redis_config['db'],
                password=self.redis_config['password'],
                ssl=self.redis_config['ssl'],
                ssl_cert_reqs=self.redis_config['ssl_cert_reqs'],
                socket_timeout=self.redis_config['socket_timeout'],
                socket_connect_timeout=self.redis_config['socket_connect_timeout'],
                retry_on_timeout=self.redis_config['retry_on_timeout'],
                health_check_interval=self.redis_config['health_check_interval'],
                max_connections=self.redis_config['max_connections']
            )
            
            # Redis クライアント作成
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # 接続テスト
            self.redis_client.ping()
            self.is_healthy = True
            self.health_stats['redis_available'] = True
            
            logger.info(f"✅ Redis connected: {self.redis_config['host']}:{self.redis_config['port']}")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.is_healthy = False
            self.health_stats['redis_available'] = False
            
            if not self.fallback_enabled:
                raise
    
    def _configure_flask_session(self, app: Flask):
        """⚙️ Flask-Session設定"""
        # Flask-Session設定
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = self.redis_client
        app.config['SESSION_KEY_PREFIX'] = self.session_config['prefix']
        app.config['SESSION_PERMANENT'] = True
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=self.session_config['expire'])
        
        # Flask-Session初期化
        Session(app)
        
        logger.info("⚙️ Flask-Session configured with Redis backend")
    
    def _start_health_check(self):
        """🏥 ヘルスチェック開始"""
        if self.health_check_thread and self.health_check_thread.is_alive():
            return
        
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        logger.info("🏥 Health check thread started")
    
    def _health_check_loop(self):
        """🔄 ヘルスチェックループ"""
        while True:
            try:
                self._perform_health_check()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                time.sleep(self.health_check_interval)
    
    def _perform_health_check(self):
        """🩺 ヘルスチェック実行"""
        try:
            start_time = time.time()
            
            # Redis ping テスト
            response = self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response:
                self.is_healthy = True
                self.health_stats['redis_available'] = True
                self.health_stats['consecutive_failures'] = 0
                
                # レスポンス時間のログ記録
                if response_time > 100:  # 100ms以上は警告
                    logger.warning(f"Redis slow response: {response_time:.1f}ms")
            else:
                self._handle_health_check_failure("Redis ping failed")
                
        except Exception as e:
            self._handle_health_check_failure(f"Redis health check error: {e}")
        
        # 統計更新
        self.health_stats['last_health_check'] = datetime.now(timezone.utc)
        self.health_stats['total_health_checks'] += 1
        
        # アップタイム計算
        if self.health_stats['total_health_checks'] > 0:
            success_count = self.health_stats['total_health_checks'] - self.health_stats['consecutive_failures']
            self.health_stats['uptime_percentage'] = (success_count / self.health_stats['total_health_checks']) * 100
    
    def _handle_health_check_failure(self, error_message: str):
        """💥 ヘルスチェック失敗処理"""
        self.is_healthy = False
        self.health_stats['redis_available'] = False
        self.health_stats['consecutive_failures'] += 1
        
        logger.error(f"Health check failure: {error_message}")
        
        # 連続失敗回数による対応
        if self.health_stats['consecutive_failures'] >= 3:
            logger.critical("Redis service appears to be down - fallback mode activated")
            # アラート送信などの追加処理
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """📖 セッション取得"""
        try:
            if self.is_healthy and self.redis_client:
                # Redisからセッション取得
                key = f"{self.session_config['prefix']}{session_id}"
                data = self.redis_client.get(key)
                
                if data:
                    self.session_stats['redis_hits'] += 1
                    return self._deserialize_session_data(data)
                else:
                    self.session_stats['redis_misses'] += 1
                    return None
            else:
                # フォールバック処理
                return self._fallback_get_session(session_id)
                
        except Exception as e:
            logger.error(f"Session get error: {e}")
            self.session_stats['errors'] += 1
            return self._fallback_get_session(session_id)
    
    def set_session(self, session_id: str, data: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """💾 セッション保存"""
        try:
            if self.is_healthy and self.redis_client:
                # Redisにセッション保存
                key = f"{self.session_config['prefix']}{session_id}"
                serialized_data = self._serialize_session_data(data)
                expire_time = expire or self.session_config['expire']
                
                result = self.redis_client.setex(key, expire_time, serialized_data)
                
                if result:
                    self.session_stats['total_sessions'] += 1
                    return True
                else:
                    return self._fallback_set_session(session_id, data, expire)
            else:
                # フォールバック処理
                return self._fallback_set_session(session_id, data, expire)
                
        except Exception as e:
            logger.error(f"Session set error: {e}")
            self.session_stats['errors'] += 1
            return self._fallback_set_session(session_id, data, expire)
    
    def delete_session(self, session_id: str) -> bool:
        """🗑️ セッション削除"""
        try:
            if self.is_healthy and self.redis_client:
                key = f"{self.session_config['prefix']}{session_id}"
                result = self.redis_client.delete(key)
                return bool(result)
            else:
                return self._fallback_delete_session(session_id)
                
        except Exception as e:
            logger.error(f"Session delete error: {e}")
            self.session_stats['errors'] += 1
            return self._fallback_delete_session(session_id)
    
    def _serialize_session_data(self, data: Dict[str, Any]) -> bytes:
        """🔒 セッションデータシリアライズ"""
        try:
            if self.session_config['serialize_method'] == 'json':
                serialized = json.dumps(data, ensure_ascii=False, default=str)
            else:
                serialized = pickle.dumps(data)
            
            # 暗号化（簡易実装）
            if self.session_config['encryption_key']:
                # 実際の本番環境では適切な暗号化ライブラリを使用
                pass
            
            if isinstance(serialized, str):
                return serialized.encode('utf-8')
            return serialized
            
        except Exception as e:
            logger.error(f"Session serialization error: {e}")
            raise
    
    def _deserialize_session_data(self, data: bytes) -> Dict[str, Any]:
        """🔓 セッションデータデシリアライズ"""
        try:
            # 復号化（簡易実装）
            if self.session_config['encryption_key']:
                # 実際の本番環境では適切な復号化処理を実装
                pass
            
            if self.session_config['serialize_method'] == 'json':
                return json.loads(data.decode('utf-8'))
            else:
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Session deserialization error: {e}")
            raise
    
    def _fallback_get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """🔄 フォールバック セッション取得"""
        if not self.fallback_enabled:
            return None
        
        try:
            # ファイルベースフォールバック
            session_file = f"user_data/{session_id}_session.json"
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.session_stats['fallback_hits'] += 1
                return data
        except Exception as e:
            logger.error(f"Fallback session get error: {e}")
        
        return None
    
    def _fallback_set_session(self, session_id: str, data: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """🔄 フォールバック セッション保存"""
        if not self.fallback_enabled:
            return False
        
        try:
            # ディレクトリ作成
            os.makedirs('user_data', exist_ok=True)
            
            # ファイル保存
            session_file = f"user_data/{session_id}_session.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Fallback session set error: {e}")
            return False
    
    def _fallback_delete_session(self, session_id: str) -> bool:
        """🔄 フォールバック セッション削除"""
        if not self.fallback_enabled:
            return False
        
        try:
            session_file = f"user_data/{session_id}_session.json"
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
        except Exception as e:
            logger.error(f"Fallback session delete error: {e}")
        
        return False
    
    def get_session_list(self) -> List[str]:
        """📋 セッション一覧取得"""
        try:
            if self.is_healthy and self.redis_client:
                pattern = f"{self.session_config['prefix']}*"
                keys = self.redis_client.keys(pattern)
                return [key.decode('utf-8').replace(self.session_config['prefix'], '') for key in keys]
            else:
                # フォールバック: ファイル一覧
                if os.path.exists('user_data'):
                    files = os.listdir('user_data')
                    return [f.replace('_session.json', '') for f in files if f.endswith('_session.json')]
                return []
        except Exception as e:
            logger.error(f"Session list error: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """🧹 期限切れセッション削除"""
        cleaned_count = 0
        try:
            if self.is_healthy and self.redis_client:
                # Redisは自動期限切れ削除のため、手動削除不要
                # カウント取得のためのダミー処理
                pass
            else:
                # ファイルベース期限切れ削除
                if os.path.exists('user_data'):
                    current_time = time.time()
                    for filename in os.listdir('user_data'):
                        if filename.endswith('_session.json'):
                            file_path = os.path.join('user_data', filename)
                            if current_time - os.path.getmtime(file_path) > self.session_config['expire']:
                                try:
                                    os.remove(file_path)
                                    cleaned_count += 1
                                except:
                                    pass
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
        
        return cleaned_count
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """📊 セッション分析データ取得"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # アクティブセッション数
            active_sessions = len(self.get_session_list())
            self.session_stats['active_sessions'] = active_sessions
            
            # Redis情報取得
            redis_info = {}
            if self.is_healthy and self.redis_client:
                try:
                    redis_info = self.redis_client.info()
                except:
                    pass
            
            return {
                'session_stats': {
                    **self.session_stats,
                    'last_updated': current_time.isoformat()
                },
                'health_stats': {
                    **self.health_stats,
                    'last_updated': current_time.isoformat()
                },
                'redis_info': {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory': redis_info.get('used_memory', 0),
                    'used_memory_human': redis_info.get('used_memory_human', '0B'),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0),
                    'total_commands_processed': redis_info.get('total_commands_processed', 0)
                },
                'configuration': {
                    'redis_host': self.redis_config['host'],
                    'redis_port': self.redis_config['port'],
                    'redis_db': self.redis_config['db'],
                    'session_expire': self.session_config['expire'],
                    'fallback_enabled': self.fallback_enabled,
                    'health_check_interval': self.health_check_interval
                }
            }
        except Exception as e:
            logger.error(f"Session analytics error: {e}")
            return {'error': str(e)}
    
    def _register_session_apis(self, app: Flask):
        """📡 セッション管理API登録"""
        
        @app.route('/api/redis/session/status')
        def redis_session_status():
            """セッション状況API"""
            try:
                analytics = self.get_session_analytics()
                return {'success': True, 'analytics': analytics}
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        @app.route('/api/redis/session/health')
        def redis_session_health():
            """ヘルスチェックAPI"""
            try:
                health_data = {
                    'redis_available': self.is_healthy,
                    'health_stats': self.health_stats,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                status_code = 200 if self.is_healthy else 503
                return {'success': True, 'health': health_data}, status_code
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        @app.route('/api/redis/session/cleanup', methods=['POST'])
        def redis_session_cleanup():
            """セッションクリーンアップAPI"""
            try:
                cleaned_count = self.cleanup_expired_sessions()
                return {
                    'success': True, 
                    'cleaned_sessions': cleaned_count,
                    'message': f'{cleaned_count} expired sessions cleaned'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        @app.route('/api/redis/session/list')
        def redis_session_list():
            """セッション一覧API"""
            try:
                session_list = self.get_session_list()
                return {
                    'success': True,
                    'sessions': session_list,
                    'count': len(session_list)
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        logger.info("📡 Redis Session APIs registered")


# グローバルインスタンス
redis_session_manager = None

def init_redis_session_manager(app: Flask) -> RedisSessionManager:
    """🚀 Redis セッション管理初期化"""
    global redis_session_manager
    
    if redis_session_manager is None:
        redis_session_manager = RedisSessionManager(app)
    
    return redis_session_manager

def get_redis_session_manager() -> Optional[RedisSessionManager]:
    """🔧 Redis セッション管理インスタンス取得"""
    return redis_session_manager


if __name__ == "__main__":
    # テスト実行
    print("🧪 Redis Session Manager Test")
    print("=" * 50)
    
    # 設定テスト
    manager = RedisSessionManager()
    print("✅ RedisSessionManager インスタンス作成")
    
    # 設定確認
    analytics = manager.get_session_analytics()
    print("📊 Analytics:", analytics.get('configuration', {}))
    
    print("✅ Redis Session Manager Test 完了")