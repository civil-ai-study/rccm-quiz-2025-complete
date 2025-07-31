#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC Test App - Render.com Deployment Verification
Minimal Flask app to test if basic deployment works
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    """Test homepage"""
    return """
    <html>
    <head><title>ULTRA SYNC Test - Render Deployment</title></head>
    <body>
        <h1>🚀 ULTRA SYNC Test App</h1>
        <p>✅ Flask app is running on Render.com!</p>
        <p>📅 Deployment test successful</p>
        <p>🔗 Environment: Production</p>
        <p>🌐 Host: 0.0.0.0</p>
        <p>📋 PORT: {}</p>
    </body>
    </html>
    """.format(os.environ.get('PORT', '10000'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "ULTRA SYNC Test App is healthy"}

if __name__ == '__main__':
    # Production environment configuration
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'
    debug_mode = 'PORT' not in os.environ
    
    print("=" * 50)
    print("ULTRA SYNC Test App Starting")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug_mode}")
    print("=" * 50)
    
    app.run(debug=debug_mode, host=host, port=port)