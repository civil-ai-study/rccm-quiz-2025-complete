
# Phase4エンコーディング完全修正 - app.py先頭に追加
import sys
import os
from flask import Flask, make_response

# システムレベルのUTF-8設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Flask設定でUTF-8を強制
app = Flask(__name__)
app.config['DEFAULT_CHARSET'] = 'utf-8'
app.config['JSON_AS_ASCII'] = False

# すべてのレスポンスにUTF-8ヘッダーを付加するミドルウェア
@app.after_request
def after_request(response):
    """すべてのHTTPレスポンスにUTF-8 charsetを明示的に設定"""
    if response.mimetype == 'text/html':
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    elif response.mimetype == 'application/json':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    elif response.mimetype.startswith('text/'):
        response.headers['Content-Type'] = f'{response.mimetype}; charset=utf-8'
    return response
