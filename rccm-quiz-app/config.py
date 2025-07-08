"""
RCCM学習アプリ - 設定管理
すべての設定値を一元管理
"""

import os

class Config:
    """基本設定 - セキュリティ強化版"""
    # 🛡️ セキュリティ強化: SECRET_KEY必須化
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("Production環境ではSECRET_KEYの環境変数設定が必須です")
        else:
            SECRET_KEY = 'rccm-quiz-app-development-key-2025'
    
    # 🛡️ セッションセキュリティ強化
    SESSION_COOKIE_NAME = 'rccm_session'
    SESSION_COOKIE_HTTPONLY = True  # XSS防止
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # HTTPS必須(本番)
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF防止
    PERMANENT_SESSION_LIFETIME = 3600  # 1時間でセッション期限切れ
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    
    # 🛡️ CSRF保護
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # CSRFトークン有効期限
    
    # 🛡️ セキュリティヘッダー
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # 🚨 ULTRATHIN区段階55緊急修正: ペイロードサイズ制限追加
    # 異常大ペイロードでのDoS攻撃防止
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB制限


class ExamConfig:
    """問題・学習設定"""
    # 🔥 CRITICAL: 絶対に10問固定（ユーザー要求による）
    QUESTIONS_PER_SESSION = 10
    
    # セッション長オプション
    SESSION_SIZES = {
        'quick': 10,     # 全て10問に統一
        'standard': 10,  # 全て10問に統一
        'intensive': 10, # 全て10問に統一
        'unlimited': 10  # 全て10問に統一
    }

class SRSConfig:
    """間隔反復学習設定"""
    # エビングハウス忘却曲線に基づく間隔
    INTERVALS = {
        0: 1,     # 初回不正解 → 1日後
        1: 3,     # 1回目正解 → 3日後
        2: 7,     # 2回目正解 → 1週間後
        3: 21,    # 3回目正解 → 3週間後
        4: 60,    # 4回目正解 → 2ヶ月後
        5: 180    # 5回目正解 → 6ヶ月後（マスター）
    }
    
    # 復習問題の比率（セッション内の最大%)
    MAX_REVIEW_RATIO = float(os.environ.get('MAX_REVIEW_RATIO', 0.5))

class DataConfig:
    """データ管理設定"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    QUESTIONS_CSV = os.path.join(BASE_DIR, 'data', 'questions.csv')
    
    # データバックアップ設定
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    AUTO_BACKUP = os.environ.get('AUTO_BACKUP', 'True').lower() == 'true'
    
    # キャッシュ設定
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))  # 1時間

class RCCMConfig:
    """RCCM専門部門設定"""
    
    # RCCM12専門部門定義（CSVデータに実際に存在する部門）
    DEPARTMENTS = {
        'road': {
            'id': 'road',
            'name': '道路',
            'full_name': '建設部門：道路',
            'description': '道路計画、道路設計、道路施工に関する専門技術',
            'icon': '🛣️',
            'color': '#FF9800'
        },
        'tunnel': {
            'id': 'tunnel',
            'name': 'トンネル',
            'full_name': '建設部門：トンネル',
            'description': 'トンネル計画、設計、施工に関する専門技術',
            'icon': '🚇',
            'color': '#795548'
        },
        'civil_planning': {
            'id': 'civil_planning',
            'name': '河川、砂防及び海岸・海洋',
            'full_name': '建設部門：河川、砂防及び海岸・海洋',
            'description': '河川工学、砂防工学、海岸・海洋工学に関する専門技術',
            'icon': '🌊',
            'color': '#2196F3'
        },
        'urban_planning': {
            'id': 'urban_planning',
            'name': '都市計画及び地方計画',
            'full_name': '建設部門：都市計画及び地方計画',
            'description': '都市計画、地方計画に関する専門技術',
            'icon': '🏙️',
            'color': '#9C27B0'
        },
        'landscape': {
            'id': 'landscape',
            'name': '造園',
            'full_name': '建設部門：造園',
            'description': '造園計画、設計、施工に関する専門技術',
            'icon': '🌸',
            'color': '#E91E63'
        },
        'construction_env': {
            'id': 'construction_env',
            'name': '建設環境',
            'full_name': '建設部門：建設環境',
            'description': '建設環境、環境保全に関する専門技術',
            'icon': '🌱',
            'color': '#4CAF50'
        },
        'steel_concrete': {
            'id': 'steel_concrete',
            'name': '鋼構造及びコンクリート',
            'full_name': '建設部門：鋼構造及びコンクリート',
            'description': '鋼構造、コンクリート構造に関する専門技術',
            'icon': '🏗️',
            'color': '#607D8B'
        },
        'soil_foundation': {
            'id': 'soil_foundation',
            'name': '土質及び基礎',
            'full_name': '建設部門：土質及び基礎',
            'description': '土質工学、基礎工学に関する専門技術',
            'icon': '🪨',
            'color': '#8D6E63'
        },
        'construction_planning': {
            'id': 'construction_planning',
            'name': '施工計画、施工設備及び積算',
            'full_name': '建設部門：施工計画、施工設備及び積算',
            'description': '施工計画、施工設備、積算に関する専門技術',
            'icon': '📋',
            'color': '#FF5722'
        },
        'water_supply': {
            'id': 'water_supply',
            'name': '上水道及び工業用水道',
            'full_name': '建設部門：上水道及び工業用水道',
            'description': '上水道、工業用水道に関する専門技術',
            'icon': '💧',
            'color': '#00BCD4'
        },
        'forestry': {
            'id': 'forestry',
            'name': '森林土木',
            'full_name': '建設部門：森林土木',
            'description': '森林土木、治山工事に関する専門技術',
            'icon': '🌲',
            'color': '#8BC34A'
        },
        'agriculture': {
            'id': 'agriculture',
            'name': '農業土木',
            'full_name': '建設部門：農業土木',
            'description': '農業基盤整備に関する専門技術',
            'icon': '🌾',
            'color': '#CDDC39'
        },
        # 🔥 CRITICAL FIX: 基礎科目(4-1)エントリ追加 - app.pyとの整合性確保
        'basic': {
            'id': 'basic',
            'name': '共通',
            'full_name': '4-1 必須科目（基礎技術）',
            'description': '土木工学基礎、測量、力学等の基礎技術問題（全部門共通）',
            'icon': '📚',
            'color': '#607D8B'
        }
    }
    
    # RCCM問題種別定義
    QUESTION_TYPES = {
        'basic': {
            'id': 'basic',
            'name': '4-1 必須科目',
            'full_name': '4-1 必須科目（基礎技術）',
            'description': '土木工学基礎、測量、力学等の基礎技術問題',
            'icon': '📚',
            'color': '#3F51B5',
            'file_prefix': '4-1'
        },
        'specialist': {
            'id': 'specialist',
            'name': '4-2 選択科目',
            'full_name': '4-2 選択科目（専門技術）',
            'description': '各専門部門の専門技術問題',
            'icon': '🎓',
            'color': '#F44336',
            'file_prefix': '4-2'
        }
    }
    
    # デフォルト設定
    DEFAULT_DEPARTMENT = 'road'  # 道路部門をデフォルトに
    DEFAULT_QUESTION_TYPE = 'basic'  # 基礎問題をデフォルトに

class LogConfig:
    """ログ設定"""
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'rccm_app.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 環境別設定
class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    TESTING = False

class EnterpriseConfig(Config):
    """企業環境用設定"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 28800  # 8時間
    TESTING = False
    
    # 企業セキュリティ強化
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # パフォーマンス設定
    SEND_FILE_MAX_AGE_DEFAULT = 0  # 静的ファイルキャッシュ無効
    TEMPLATES_AUTO_RELOAD = False
    
    # ログ設定（企業環境用）
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/rccm_app.log'
    
    # マルチユーザー設定
    MAX_CONCURRENT_USERS = int(os.environ.get('MAX_CONCURRENT_USERS', 100))


class RedisSessionConfig(Config):
    """Redis + Flask-Session 次世代セッション管理設定"""
    
    # Redis Session設定
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'rccm_session:'
    
    # Redis接続設定
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # 高可用性設定
    REDIS_SENTINEL_ENABLED = os.environ.get('REDIS_SENTINEL_ENABLED', 'False').lower() == 'true'
    REDIS_CLUSTER_ENABLED = os.environ.get('REDIS_CLUSTER_ENABLED', 'False').lower() == 'true'
    
    # セッション最適化
    SESSION_REDIS_SERIALIZATION_FORMAT = 'json'
    SESSION_REDIS_RETRY_ON_FAILURE = 3
    SESSION_REDIS_SOCKET_TIMEOUT = 3.0
    
    # セッション有効期限（デフォルト24時間）
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME_HOURS', 24)) * 3600
    
    # セッション暗号化強化
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Redis接続プール設定
    REDIS_MAX_CONNECTIONS = int(os.environ.get('REDIS_MAX_CONNECTIONS', 50))
    REDIS_CONNECTION_TIMEOUT = int(os.environ.get('REDIS_CONNECTION_TIMEOUT', 5))
    REDIS_SOCKET_TIMEOUT = int(os.environ.get('REDIS_SOCKET_TIMEOUT', 3))
    REDIS_HEALTH_CHECK_INTERVAL = 30


class ProductionRedisConfig(RedisSessionConfig):
    """本番環境用Redis設定"""
    DEBUG = False
    TESTING = False
    
    # 本番環境セキュリティ強化
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Redis SSL設定
    REDIS_SSL = True
    REDIS_SSL_CERT_REQS = 'required'
    
    # 高可用性設定有効化
    REDIS_SENTINEL_ENABLED = True
    REDIS_CLUSTER_ENABLED = os.environ.get('REDIS_CLUSTER_ENABLED', 'True').lower() == 'true'
    
    # セッション期限短縮（本番環境）
    PERMANENT_SESSION_LIFETIME = 8 * 3600  # 8時間
    
    # 高性能設定
    REDIS_MAX_CONNECTIONS = int(os.environ.get('REDIS_MAX_CONNECTIONS', 100))
    REDIS_CONNECTION_TIMEOUT = 2
    REDIS_SOCKET_TIMEOUT = 1
    USER_SESSION_TIMEOUT = 28800  # 8時間のアイドルタイムアウト（セッションライフタイムと統一）

class ServerConfig:
    """サーバー配置用設定"""
    
    # サーバー設定
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    WORKERS = int(os.environ.get('WORKERS', 4))
    
    # データベース設定（将来の拡張用）
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///rccm_app.db')
    
    # Redis設定（セッション管理用）
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # ファイルストレージ設定
    DATA_DIR = os.environ.get('DATA_DIR', '/app/data')
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', '/app/uploads')
    
    # バックアップ設定
    BACKUP_DIR = os.environ.get('BACKUP_DIR', '/app/backups')
    AUTO_BACKUP_INTERVAL = int(os.environ.get('AUTO_BACKUP_INTERVAL', 3600))  # 1時間

# 設定選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'enterprise': EnterpriseConfig,
    'default': DevelopmentConfig
} 