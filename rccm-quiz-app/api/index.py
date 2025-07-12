#!/usr/bin/env python3
"""
🚀 ULTRASYNC段階68: Vercel対応エントリーポイント
慎重な段階的本番環境構築 - Vercel Serverless対応
"""

import os
import sys
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # パス設定（Vercel対応）
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    # 環境変数設定
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # SECRET_KEY自動生成（本番環境対応）
    if not os.environ.get('SECRET_KEY'):
        import secrets
        fallback_key = secrets.token_hex(32)
        os.environ['SECRET_KEY'] = fallback_key
        logger.info("🚨 ULTRASYNC: SECRET_KEY自動生成完了")
    
    # メインアプリケーションインポート
    from app import app
    
    logger.info("✅ ULTRASYNC: Vercelアプリケーション起動完了")
    
    # Vercel用のハンドラー関数
    def handler(request, context):
        """Vercel Serverless handler"""
        return app(request, context)
    
    # WSGIアプリケーション（従来互換）
    application = app
    
    # Vercel用のエクスポート
    app = app
    
except Exception as e:
    logger.error(f"❌ ULTRASYNC Vercelエラー: {e}")
    
    # フォールバック用の最小アプリ
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_fallback():
        return f'''
        <h1>🚨 ULTRASYNC エラー状態</h1>
        <p>エラー: {e}</p>
        <p>フォールバック状態で起動中...</p>
        '''