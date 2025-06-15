#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - サーバー起動スクリプト
企業環境での本格運用対応
"""

import os
import sys
import logging
from app import app
from config import config, ServerConfig

def setup_logging():
    """ログ設定"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    log_file = os.environ.get('LOG_FILE', 'rccm_app.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def setup_directories():
    """必要なディレクトリの作成"""
    dirs = [
        ServerConfig.DATA_DIR,
        ServerConfig.UPLOAD_DIR,
        ServerConfig.BACKUP_DIR,
        'user_data',
        'logs'
    ]
    
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"ディレクトリ作成: {dir_path}")

def get_config():
    """環境に応じた設定取得"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

def main():
    """メイン実行関数"""
    # 環境変数チェック
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"起動環境: {env}")
    
    # ログ設定
    setup_logging()
    
    # ディレクトリ作成
    setup_directories()
    
    # 設定適用
    config_class = get_config()
    app.config.from_object(config_class)
    
    # セキュリティヘッダー強化（企業環境）
    if env in ['production', 'enterprise']:
        @app.after_request
        def security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdnjs.cloudflare.com;"
            return response
    
    # サーバー起動
    host = ServerConfig.HOST
    port = ServerConfig.PORT
    debug = env == 'development'
    
    print(f"サーバー起動: http://{host}:{port}")
    print(f"デバッグモード: {debug}")
    print(f"データディレクトリ: {ServerConfig.DATA_DIR}")
    
    if env == 'development':
        # 開発環境
        app.run(host=host, port=port, debug=debug)
    else:
        # 本番環境（Gunicorn推奨）
        print("本番環境ではGunicornまたはuWSGIでの起動を推奨します:")
        print(f"gunicorn -w {ServerConfig.WORKERS} -b {host}:{port} app:app")
        
        # フォールバック: Flaskの本番モード
        app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    main()