#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: セッションセキュリティ強化モジュール
"""

import time
from datetime import datetime, timedelta
from flask import session

def secure_session_config(app):
    """セキュアなセッション設定"""
    app.config.update({
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PERMANENT_SESSION_LIFETIME': timedelta(hours=1),
        'SESSION_REFRESH_EACH_REQUEST': True
    })

def validate_session_security():
    """セッションセキュリティの検証"""
    current_time = time.time()
    
    # セッションタイムアウトチェック
    if 'session_start' in session:
        session_duration = current_time - session['session_start']
        if session_duration > 3600:  # 1時間
            session.clear()
            return False
    else:
        session['session_start'] = current_time
    
    # セッション更新
    session['last_activity'] = current_time
    session.permanent = True
    session.modified = True
    
    return True

def secure_session_cleanup():
    """セッションの安全なクリーンアップ"""
    sensitive_keys = ['password', 'secret', 'token', 'key']
    
    for key in list(session.keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            session.pop(key, None)
    
    session.modified = True