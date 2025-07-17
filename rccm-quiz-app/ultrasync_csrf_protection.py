#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: CSRF攻撃防止モジュール
"""

import secrets
from flask import session, request, abort
from functools import wraps

def generate_csrf_token():
    """CSRFトークンの生成"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_csrf_token(token: str) -> bool:
    """CSRFトークンの検証"""
    session_token = session.get('csrf_token')
    if not session_token or not token:
        return False
    
    return secrets.compare_digest(session_token, token)

def csrf_protect(f):
    """CSRF保護デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not validate_csrf_token(token):
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

def inject_csrf_token():
    """テンプレートへのCSRFトークン注入"""
    return {'csrf_token': generate_csrf_token()}