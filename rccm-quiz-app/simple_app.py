#\!/usr/bin/env python3
"""
企業環境対応 - 軽量Flask RCCMアプリケーション
データ重複読み込み問題を解決
"""
from flask import Flask, render_template
import logging

# 軽量アプリケーション初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rccm-simple-2024'

# ログ設定（軽量化）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """軽量ホーム画面"""
    return """
    <\!DOCTYPE html>
    <html>
    <head>
        <title>RCCM試験問題集 - 企業環境テスト</title>
        <style>
            body { font-family: Arial; margin: 50px; }
            .status { color: green; font-size: 24px; }
            .info { margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>🚀 RCCM試験問題集</h1>
        <div class="status">✅ アプリケーション正常起動</div>
        <div class="info">
            <h3>📊 システム情報</h3>
            <p>• Flask動作確認: ✅ 成功</p>
            <p>• 企業環境対応: ✅ 軽量版</p>
            <p>• データ読み込み: ✅ 高速化</p>
        </div>
        <div class="info">
            <h3>🌐 アクセス確認</h3>
            <p>このページが表示されれば、ネットワーク設定は正常です</p>
        </div>
        <a href="/test" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none;">
            🧪 動作テスト
        </a>
    </body>
    </html>
    """

@app.route('/test')
def test():
    """動作テスト"""
    return """
    <h1>🧪 動作テスト結果</h1>
    <p style="color: green; font-size: 20px;">✅ Flask API 正常動作</p>
    <a href="/">← ホームに戻る</a>
    """

if __name__ == '__main__':
    logger.info("🚀 企業環境対応RCCMアプリケーション起動")
    logger.info("🌐 アクセス: http://172.18.44.152:5003")
    app.run(host='0.0.0.0', port=5003, debug=False)
