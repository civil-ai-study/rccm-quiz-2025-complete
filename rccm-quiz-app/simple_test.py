#!/usr/bin/env python3
"""
🎯 ULTRASYNC段階49: 最小構成テストアプリ
Render.com動作確認用の最小Flask設定
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '🚀 RCCM Quiz App - ULTRASYNC Test Success! 🎯'

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'ULTRASYNC Health Check OK'}

if __name__ == '__main__':
    app.run(debug=True)