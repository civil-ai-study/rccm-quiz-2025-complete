#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: セキュリティ強化 - 入力検証モジュール
"""

import html
import re
from flask import session, abort

def validate_user_input(input_value: str, max_length: int = 1000) -> str:
    """ユーザー入力の安全な検証"""
    if not input_value:
        return ""
    
    # 長さ制限
    if len(input_value) > max_length:
        input_value = input_value[:max_length]
    
    # HTMLエスケープ
    escaped_value = html.escape(input_value)
    
    # 危険な文字列の除去
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick='
    ]
    
    for pattern in dangerous_patterns:
        escaped_value = re.sub(pattern, '', escaped_value, flags=re.IGNORECASE)
    
    return escaped_value

def validate_department_name(department: str) -> bool:
    """部門名の検証"""
    allowed_departments = [
        '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
        '建設環境', '鋼構造・コンクリート', '土質・基礎', '施工計画',
        '上下水道', '森林土木', '農業土木', 'トンネル'
    ]
    return department in allowed_departments

def validate_answer_choice(answer: str) -> bool:
    """回答選択の検証"""
    allowed_choices = ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']
    return answer in allowed_choices

def secure_session_update(key: str, value: str) -> bool:
    """セッションの安全な更新"""
    try:
        # 入力検証
        if not key or not isinstance(key, str) or len(key) > 50:
            return False
        
        if not isinstance(value, (str, int, float, bool)):
            return False
        
        # 安全な値の設定
        if isinstance(value, str):
            value = validate_user_input(value)
        
        session[key] = value
        session.modified = True
        return True
        
    except Exception:
        return False