#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: 最小限のFlaskアプリテスト
副作用ゼロで基本動作確認
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ULTRA SYNC Test</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>🔥 ULTRA SYNC Test Success</h1>
        <p>Flask is working correctly!</p>
        <p>Python environment is operational.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🔥 ULTRA SYNC: Starting simple Flask test...")
    app.run(debug=True, host='0.0.0.0', port=5000)