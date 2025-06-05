"""
RCCM学習アプリ - 設定管理
すべての設定値を一元管理
"""

import os

class Config:
    """基本設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rccm-quiz-secret-key-2024-ultra-secure'
    SESSION_COOKIE_NAME = 'rccm_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

class QuizConfig:
    """問題・学習設定"""
    QUESTIONS_PER_SESSION = int(os.environ.get('QUESTIONS_PER_SESSION', 10))
    
    # セッション長オプション
    SESSION_SIZES = {
        'quick': 5,      # 短時間学習
        'standard': 10,  # 標準
        'intensive': 20, # 集中学習
        'unlimited': -1  # 制限なし
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

class LogConfig:
    """ログ設定"""
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'rccm_app.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 環境別設定
class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# 設定選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 