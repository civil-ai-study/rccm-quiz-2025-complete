"""
RCCM学習アプリ - Redis + Flask-Session 次世代セッション管理設定
企業レベルのRedis統合システム設定
"""

import os
import redis
from redis.sentinel import Sentinel
from redis.connection import ConnectionPool
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis基本設定"""
    
    # Redis接続設定
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # SSL/TLS設定
    REDIS_SSL = os.environ.get('REDIS_SSL', 'False').lower() == 'true'
    REDIS_SSL_CERT_FILE = os.environ.get('REDIS_SSL_CERT_FILE')
    REDIS_SSL_KEY_FILE = os.environ.get('REDIS_SSL_KEY_FILE')
    REDIS_SSL_CA_CERT_FILE = os.environ.get('REDIS_SSL_CA_CERT_FILE')
    
    # 接続プール設定（高性能化）
    REDIS_MAX_CONNECTIONS = int(os.environ.get('REDIS_MAX_CONNECTIONS', 50))
    REDIS_CONNECTION_TIMEOUT = int(os.environ.get('REDIS_CONNECTION_TIMEOUT', 5))
    REDIS_SOCKET_TIMEOUT = int(os.environ.get('REDIS_SOCKET_TIMEOUT', 3))
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_HEALTH_CHECK_INTERVAL = 30


class RedisClusterConfig:
    """Redis Cluster設定（企業レベル）"""
    
    # Cluster設定
    REDIS_CLUSTER_ENABLED = os.environ.get('REDIS_CLUSTER_ENABLED', 'False').lower() == 'true'
    REDIS_CLUSTER_NODES = os.environ.get('REDIS_CLUSTER_NODES', 'localhost:7000,localhost:7001,localhost:7002').split(',')
    
    # Master-Slave設定
    REDIS_MASTER_SLAVE_ENABLED = os.environ.get('REDIS_MASTER_SLAVE_ENABLED', 'False').lower() == 'true'
    REDIS_MASTER_NAME = os.environ.get('REDIS_MASTER_NAME', 'rccm-master')
    
    # Sentinel設定（高可用性）
    REDIS_SENTINEL_ENABLED = os.environ.get('REDIS_SENTINEL_ENABLED', 'False').lower() == 'true'
    REDIS_SENTINEL_HOSTS = os.environ.get('REDIS_SENTINEL_HOSTS', 'localhost:26379').split(',')
    REDIS_SENTINEL_PASSWORD = os.environ.get('REDIS_SENTINEL_PASSWORD')


class SessionConfig:
    """Flask-Session設定"""
    
    # セッション設定
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'rccm_session:'
    
    # セッション有効期限設定
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 24))
    )
    
    # セッション暗号化
    SESSION_REDIS_SERIALIZATION_FORMAT = 'json'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # セッション最適化
    SESSION_REDIS_RETRY_ON_FAILURE = 3
    SESSION_REDIS_SOCKET_TIMEOUT = 3.0


class RedisSessionManager:
    """企業レベルRedisセッション管理システム"""
    
    def __init__(self):
        self.redis_client = None
        self.connection_pool = None
        self.sentinel = None
        self._health_check_enabled = True
        
    def initialize_redis_connection(self):
        """Redis接続初期化（フェイルオーバー対応）"""
        try:
            if RedisClusterConfig.REDIS_SENTINEL_ENABLED:
                return self._initialize_sentinel_connection()
            elif RedisClusterConfig.REDIS_CLUSTER_ENABLED:
                return self._initialize_cluster_connection()
            else:
                return self._initialize_single_connection()
                
        except Exception as e:
            logger.error(f"Redis接続初期化エラー: {e}")
            return self._initialize_fallback_connection()
    
    def _initialize_sentinel_connection(self):
        """Redis Sentinel接続（高可用性）"""
        try:
            sentinel_hosts = []
            for host_port in RedisClusterConfig.REDIS_SENTINEL_HOSTS:
                host, port = host_port.split(':')
                sentinel_hosts.append((host, int(port)))
            
            self.sentinel = Sentinel(
                sentinel_hosts,
                password=RedisClusterConfig.REDIS_SENTINEL_PASSWORD,
                socket_timeout=RedisConfig.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=RedisConfig.REDIS_CONNECTION_TIMEOUT
            )
            
            # マスター接続取得
            self.redis_client = self.sentinel.master_for(
                RedisClusterConfig.REDIS_MASTER_NAME,
                password=RedisConfig.REDIS_PASSWORD,
                db=RedisConfig.REDIS_DB,
                decode_responses=True,
                health_check_interval=RedisConfig.REDIS_HEALTH_CHECK_INTERVAL
            )
            
            logger.info("✅ Redis Sentinel接続成功")
            return self.redis_client
            
        except Exception as e:
            logger.error(f"Redis Sentinel接続エラー: {e}")
            raise
    
    def _initialize_cluster_connection(self):
        """Redis Cluster接続"""
        try:
            from rediscluster import RedisCluster
            
            startup_nodes = []
            for node in RedisClusterConfig.REDIS_CLUSTER_NODES:
                host, port = node.split(':')
                startup_nodes.append({"host": host, "port": int(port)})
            
            self.redis_client = RedisCluster(
                startup_nodes=startup_nodes,
                password=RedisConfig.REDIS_PASSWORD,
                decode_responses=True,
                skip_full_coverage_check=True,
                health_check_interval=RedisConfig.REDIS_HEALTH_CHECK_INTERVAL
            )
            
            logger.info("✅ Redis Cluster接続成功")
            return self.redis_client
            
        except Exception as e:
            logger.error(f"Redis Cluster接続エラー: {e}")
            raise
    
    def _initialize_single_connection(self):
        """単一Redis接続（高性能コネクションプール）"""
        try:
            # SSL設定
            ssl_config = {}
            if RedisConfig.REDIS_SSL:
                ssl_config = {
                    'ssl': True,
                    'ssl_cert_reqs': 'required',
                    'ssl_ca_certs': RedisConfig.REDIS_SSL_CA_CERT_FILE,
                    'ssl_certfile': RedisConfig.REDIS_SSL_CERT_FILE,
                    'ssl_keyfile': RedisConfig.REDIS_SSL_KEY_FILE,
                }
            
            # 高性能接続プール
            self.connection_pool = ConnectionPool(
                host=RedisConfig.REDIS_HOST,
                port=RedisConfig.REDIS_PORT,
                db=RedisConfig.REDIS_DB,
                password=RedisConfig.REDIS_PASSWORD,
                max_connections=RedisConfig.REDIS_MAX_CONNECTIONS,
                socket_timeout=RedisConfig.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=RedisConfig.REDIS_CONNECTION_TIMEOUT,
                retry_on_timeout=RedisConfig.REDIS_RETRY_ON_TIMEOUT,
                health_check_interval=RedisConfig.REDIS_HEALTH_CHECK_INTERVAL,
                **ssl_config
            )
            
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=True
            )
            
            # 接続テスト
            self.redis_client.ping()
            logger.info("✅ Redis単一接続成功（高性能プール）")
            return self.redis_client
            
        except Exception as e:
            logger.error(f"Redis単一接続エラー: {e}")
            raise
    
    def _initialize_fallback_connection(self):
        """フォールバック接続（基本設定）"""
        try:
            self.redis_client = redis.Redis(
                host=RedisConfig.REDIS_HOST,
                port=RedisConfig.REDIS_PORT,
                db=RedisConfig.REDIS_DB,
                password=RedisConfig.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            self.redis_client.ping()
            logger.warning("⚠️ Redis フォールバック接続使用")
            return self.redis_client
            
        except Exception as e:
            logger.critical(f"Redis フォールバック接続も失敗: {e}")
            return None
    
    def health_check(self):
        """Redis接続ヘルスチェック"""
        try:
            if not self.redis_client:
                return False
            
            # 基本接続確認
            ping_result = self.redis_client.ping()
            if not ping_result:
                return False
            
            # メモリ使用量確認
            info = self.redis_client.info('memory')
            memory_usage = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            if max_memory > 0 and memory_usage / max_memory > 0.9:
                logger.warning(f"⚠️ Redis メモリ使用量高: {memory_usage/max_memory:.1%}")
            
            # 接続数確認
            clients_info = self.redis_client.info('clients')
            connected_clients = clients_info.get('connected_clients', 0)
            
            if connected_clients > RedisConfig.REDIS_MAX_CONNECTIONS * 0.8:
                logger.warning(f"⚠️ Redis 接続数高: {connected_clients}")
            
            return True
            
        except Exception as e:
            logger.error(f"Redis ヘルスチェック失敗: {e}")
            return False
    
    def get_session_stats(self):
        """セッション統計情報取得"""
        try:
            if not self.redis_client:
                return {}
            
            # セッション関連キー数
            session_keys = self.redis_client.keys(SessionConfig.SESSION_KEY_PREFIX + '*')
            
            # TTL情報収集
            ttl_info = []
            for key in session_keys[:100]:  # サンプリング
                ttl = self.redis_client.ttl(key)
                if ttl > 0:
                    ttl_info.append(ttl)
            
            avg_ttl = sum(ttl_info) / len(ttl_info) if ttl_info else 0
            
            return {
                'total_sessions': len(session_keys),
                'average_ttl': avg_ttl,
                'sample_size': len(ttl_info),
                'redis_memory': self.redis_client.info('memory'),
                'redis_stats': self.redis_client.info('stats')
            }
            
        except Exception as e:
            logger.error(f"セッション統計取得エラー: {e}")
            return {}


# グローバルRedisセッション管理インスタンス
redis_session_manager = RedisSessionManager()


def get_redis_config():
    """Flask-Session用Redis設定取得"""
    redis_client = redis_session_manager.initialize_redis_connection()
    
    if not redis_client:
        raise ConnectionError("Redis接続を確立できません")
    
    return {
        'SESSION_TYPE': SessionConfig.SESSION_TYPE,
        'SESSION_REDIS': redis_client,
        'SESSION_PERMANENT': SessionConfig.SESSION_PERMANENT,
        'SESSION_USE_SIGNER': SessionConfig.SESSION_USE_SIGNER,
        'SESSION_KEY_PREFIX': SessionConfig.SESSION_KEY_PREFIX,
        'PERMANENT_SESSION_LIFETIME': SessionConfig.PERMANENT_SESSION_LIFETIME,
        'SESSION_COOKIE_SECURE': SessionConfig.SESSION_COOKIE_SECURE,
        'SESSION_COOKIE_HTTPONLY': SessionConfig.SESSION_COOKIE_HTTPONLY,
        'SESSION_COOKIE_SAMESITE': SessionConfig.SESSION_COOKIE_SAMESITE,
    }


def create_session_middleware():
    """セッションミドルウェア作成"""
    from flask_session import Session
    
    def init_session(app):
        """Flask-Sessionアプリ初期化"""
        try:
            # Redis設定適用
            redis_config = get_redis_config()
            app.config.update(redis_config)
            
            # Session初期化
            Session(app)
            
            logger.info("✅ Flask-Session + Redis 初期化完了")
            
        except Exception as e:
            logger.error(f"セッション初期化エラー: {e}")
            # フォールバック: ファイルベースセッション
            app.config.update({
                'SESSION_TYPE': 'filesystem',
                'SESSION_FILE_DIR': os.path.join(os.path.dirname(__file__), 'flask_session'),
                'SESSION_PERMANENT': True,
                'SESSION_USE_SIGNER': True,
            })
            Session(app)
            logger.warning("⚠️ ファイルベースセッションにフォールバック")
    
    return init_session