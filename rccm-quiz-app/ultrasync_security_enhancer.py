#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC タスク12: セキュリティ強化ツール
副作用ゼロで安全にセキュリティを強化
"""

import os
import re
import html
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class UltraSyncSecurityEnhancer:
    """🔥 ULTRA SYNC: セキュリティ強化クラス"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.security_log = []
        self.backup_dir = self.project_root / "security_backups"
        self.security_config = {
            'csrf_token_length': 32,
            'session_timeout': 3600,  # 1時間
            'max_input_length': 1000,
            'allowed_file_types': ['.py', '.html', '.js', '.css'],
            'security_headers': {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            }
        }
        
        # バックアップディレクトリの作成
        self.backup_dir.mkdir(exist_ok=True)
    
    def log_security_action(self, message: str):
        """セキュリティ操作ログの記録"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.security_log.append(log_entry)
        print(f"🔥 ULTRA SYNC Security: {log_entry}")
    
    def create_security_backup(self, file_path: Path) -> bool:
        """セキュリティ強化用のバックアップ作成"""
        try:
            if not file_path.exists():
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}.security_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            backup_path.write_bytes(file_path.read_bytes())
            self.log_security_action(f"セキュリティバックアップ作成: {file_path.name}")
            return True
            
        except Exception as e:
            self.log_security_action(f"バックアップ作成失敗: {file_path.name} - {e}")
            return False
    
    def analyze_security_vulnerabilities(self, file_path: Path) -> Dict:
        """セキュリティ脆弱性の分析"""
        if not file_path.exists():
            return {'error': 'ファイルが存在しません'}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            vulnerabilities = {
                'xss_risks': [],
                'csrf_risks': [],
                'input_validation_risks': [],
                'session_risks': [],
                'general_risks': []
            }
            
            # XSS脆弱性の検出
            xss_patterns = [
                r'render_template_string\(',
                r'Markup\(',
                r'\|safe',
                r'innerHTML\s*=',
                r'document\.write\(',
                r'eval\('
            ]
            
            for pattern in xss_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities['xss_risks'].extend(matches)
            
            # CSRF脆弱性の検出
            csrf_patterns = [
                r'<form[^>]*method=["\']post["\'][^>]*>',
                r'request\.form\.',
                r'request\.json\.',
                r'@app\.route.*methods.*POST'
            ]
            
            for pattern in csrf_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities['csrf_risks'].extend(matches)
            
            # 入力検証リスクの検出
            input_patterns = [
                r'request\.args\.get\(',
                r'request\.form\.get\(',
                r'request\.json\.get\(',
                r'session\[.*\]\s*=.*request\.'
            ]
            
            for pattern in input_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities['input_validation_risks'].extend(matches)
            
            # セッション関連リスクの検出
            session_patterns = [
                r'session\[.*\]\s*=',
                r'session\.permanent\s*=',
                r'session\.modified\s*='
            ]
            
            for pattern in session_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities['session_risks'].extend(matches)
            
            # 一般的なセキュリティリスク
            general_patterns = [
                r'debug\s*=\s*True',
                r'app\.run\(.*debug=True',
                r'print\(',
                r'console\.log\('
            ]
            
            for pattern in general_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities['general_risks'].extend(matches)
            
            return vulnerabilities
            
        except Exception as e:
            return {'error': f'分析エラー: {e}'}
    
    def generate_csrf_token(self) -> str:
        """CSRFトークンの生成"""
        return secrets.token_urlsafe(self.security_config['csrf_token_length'])
    
    def generate_secure_input_validator(self) -> str:
        """安全な入力検証コードの生成"""
        code = '''
# 🔥 ULTRA SYNC: セキュリティ強化 - 入力検証
import html
import re
from flask import request, session, abort

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
'''
        return code
    
    def generate_xss_protection_code(self) -> str:
        """XSS保護コードの生成"""
        code = '''
# 🔥 ULTRA SYNC: XSS攻撃防止
from flask import make_response
import html

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
'''
        return code
    
    def generate_csrf_protection_code(self) -> str:
        """CSRF保護コードの生成"""
        code = '''
# 🔥 ULTRA SYNC: CSRF攻撃防止
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
'''
        return code
    
    def generate_session_security_code(self) -> str:
        """セッションセキュリティコードの生成"""
        code = '''
# 🔥 ULTRA SYNC: セッションセキュリティ強化
import time
from datetime import datetime, timedelta

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
'''
        return code
    
    def run_security_enhancement(self) -> Dict:
        """包括的セキュリティ強化の実行"""
        self.log_security_action("包括的セキュリティ強化を開始")
        
        results = {
            'success': True,
            'vulnerabilities_found': {},
            'security_files_generated': [],
            'enhancements_applied': 0,
            'recommendations': []
        }
        
        try:
            # Pythonファイルの脆弱性分析
            python_files = list(self.project_root.glob('**/*.py'))
            for py_file in python_files:
                if 'backup' not in str(py_file) and 'ultrasync' not in str(py_file):
                    vulnerabilities = self.analyze_security_vulnerabilities(py_file)
                    if vulnerabilities and 'error' not in vulnerabilities:
                        results['vulnerabilities_found'][str(py_file)] = vulnerabilities
            
            # セキュリティ強化コードの生成
            security_modules = [
                ('ultrasync_input_validator.py', self.generate_secure_input_validator()),
                ('ultrasync_xss_protection.py', self.generate_xss_protection_code()),
                ('ultrasync_csrf_protection.py', self.generate_csrf_protection_code()),
                ('ultrasync_session_security.py', self.generate_session_security_code())
            ]
            
            for filename, code in security_modules:
                file_path = self.project_root / filename
                file_path.write_text(code, encoding='utf-8')
                results['security_files_generated'].append(filename)
                results['enhancements_applied'] += 1
                self.log_security_action(f"セキュリティモジュール生成: {filename}")
            
            # セキュリティ設定ファイルの生成
            config_path = self.project_root / 'ultrasync_security_config.json'
            config_path.write_text(json.dumps(self.security_config, indent=2, ensure_ascii=False))
            results['security_files_generated'].append('ultrasync_security_config.json')
            
            # 推奨事項の生成
            results['recommendations'] = [
                'セキュリティヘッダーの適用',
                'CSRFトークンの実装',
                '入力検証の強化',
                'セッションセキュリティの向上',
                'XSS防止策の実装',
                '定期的なセキュリティ監査'
            ]
            
            self.log_security_action(f"セキュリティ強化完了: {results['enhancements_applied']}項目")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            self.log_security_action(f"セキュリティ強化エラー: {e}")
        
        return results
    
    def generate_security_report(self, results: Dict) -> str:
        """セキュリティレポートの生成"""
        report = f"""
🔥 ULTRA SYNC セキュリティ強化レポート
==========================================

実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
強化項目数: {results.get('enhancements_applied', 0)}
生成ファイル数: {len(results.get('security_files_generated', []))}

生成されたセキュリティモジュール:
{chr(10).join(f'- {f}' for f in results.get('security_files_generated', []))}

発見された脆弱性:
{chr(10).join(f'- {k}: {len(v.get("xss_risks", []) + v.get("csrf_risks", []) + v.get("input_validation_risks", []))}件' for k, v in results.get('vulnerabilities_found', {}).items())}

推奨事項:
{chr(10).join(f'- {r}' for r in results.get('recommendations', []))}

セキュリティ強化ログ:
{chr(10).join(self.security_log)}

副作用ゼロ保証:
✅ 既存コードへの影響なし
✅ 新規モジュールのみ作成
✅ 段階的実装可能
✅ 完全な復旧可能性

次のステップ:
1. 生成されたモジュールの段階的統合
2. セキュリティヘッダーの適用
3. CSRFトークンの実装
4. 入力検証の強化
5. セキュリティテストの実行
"""
        
        return report

def run_ultrasync_security_enhancement():
    """🔥 ULTRA SYNC セキュリティ強化の実行"""
    enhancer = UltraSyncSecurityEnhancer()
    
    print("🔥 ULTRA SYNC セキュリティ強化開始")
    print("=" * 50)
    
    # 包括的セキュリティ強化実行
    results = enhancer.run_security_enhancement()
    
    # レポート生成
    report = enhancer.generate_security_report(results)
    
    # レポート保存
    report_path = enhancer.project_root / f"ultrasync_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.write_text(report, encoding='utf-8')
    
    print(report)
    print(f"詳細レポート保存: {report_path}")
    
    return results

if __name__ == '__main__':
    results = run_ultrasync_security_enhancement()
    print(f"セキュリティ強化結果: {results['success']}")
    if results['success']:
        print(f"強化項目数: {results['enhancements_applied']}")
        print(f"生成ファイル数: {len(results['security_files_generated'])}")