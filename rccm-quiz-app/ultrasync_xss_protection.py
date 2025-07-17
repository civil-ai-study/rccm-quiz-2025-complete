#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: XSS攻撃防止モジュール
"""

from flask import make_response, render_template
import html
import re

def add_security_headers(response):
    """セキュリティヘッダーの追加"""
    security_headers = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
    
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response

def safe_render_template(template_name: str, **context):
    """安全なテンプレートレンダリング"""
    # コンテキストの値をエスケープ
    safe_context = {}
    for key, value in context.items():
        if isinstance(value, str):
            safe_context[key] = html.escape(value)
        else:
            safe_context[key] = value
    
    response = make_response(render_template(template_name, **safe_context))
    return add_security_headers(response)

def sanitize_error_message(error_msg: str) -> str:
    """エラーメッセージの安全化"""
    if not error_msg:
        return "システムエラーが発生しました"
    
    # 機密情報の除去
    sanitized = re.sub(r'File ".*?"', 'File "[REDACTED]"', error_msg)
    sanitized = re.sub(r'line \d+', 'line [REDACTED]', sanitized)
    sanitized = html.escape(sanitized)
    
    return sanitized