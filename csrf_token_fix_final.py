#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク Task 8-9: CSRFトークン問題最終修正（ASCII安全・パス修正版）
目的: 400 Bad Requestエラーの根本原因であるCSRFトークン問題を完全解決
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def fix_csrf_token_implementation():
    """CSRF token実装の診断および修正"""
    print("=== Task 8-9: CSRF Token Implementation Complete Fix ===")
    print("Purpose: Fix 400 Bad Request errors caused by CSRF token issues")
    print()
    
    try:
        from app import app
        
        print("1. Flask-WTF CSRF Configuration Check")
        csrf_available = app.config.get('CSRF_AVAILABLE', False)
        wtf_csrf_enabled = app.config.get('WTF_CSRF_ENABLED', True)
        secret_key_configured = bool(app.config.get('SECRET_KEY'))
        
        print(f"  CSRF_AVAILABLE: {csrf_available}")
        print(f"  WTF_CSRF_ENABLED: {wtf_csrf_enabled}")
        print(f"  SECRET_KEY configured: {secret_key_configured}")
        
        # CSRF拡張機能確認
        csrf_extensions = [ext for ext in app.extensions.keys() if 'csrf' in ext.lower()]
        print(f"  CSRF Extensions: {csrf_extensions}")
        
        if not secret_key_configured or not csrf_extensions:
            print("  NG: Basic CSRF setup incomplete")
            return False
        
        print("  OK: Basic CSRF setup detected")
        print()
        
        # 2. 実際のCSRFトークン生成テスト
        print("2. CSRF Token Generation Test")
        
        with app.test_client() as client:
            # セッション開始とCSRFトークン確認
            client.get('/start_exam/specialist_road', follow_redirects=True)
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"  GET /exam status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"  NG: Failed to get exam page - {response.status_code}")
                return False
            
            # CSRFトークンの存在確認
            if 'csrf_token' in response_text:
                print("  OK: CSRF token found in response")
                
                # トークン値の抽出
                import re
                token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                if token_match:
                    token_value = token_match.group(1)
                    print(f"  Token format: {token_value[:20]}...")
                    
                    # フォールバックトークンかチェック
                    if token_value.startswith('fast_token_'):
                        print("  NG: Fallback token detected (Flask-WTF incompatible)")
                        token_issue = True
                    else:
                        print("  OK: Proper CSRF token format")
                        token_issue = False
                else:
                    print("  NG: CSRF token value extraction failed")
                    token_issue = True
            else:
                print("  NG: No CSRF token found")
                token_issue = True
        
        print()
        
        # 3. CSRF検証テスト
        print("3. CSRF Token Validation Test")
        
        csrf_validation_passed = False
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得とCSRFトークン抽出
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            
            if token_match:
                csrf_token = token_match.group(1)
                print(f"  Extracted CSRF token: {csrf_token[:15]}...")
                
                # 正常なCSRFトークンでPOSTテスト
                post_data = {
                    'answer': 'A',
                    'qid': '1',
                    'csrf_token': csrf_token
                }
                
                post_response = client.post('/exam', data=post_data)
                print(f"  POST with CSRF token result: {post_response.status_code}")
                
                if post_response.status_code == 200:
                    print("  OK: CSRF token validation successful")
                    csrf_validation_passed = True
                elif post_response.status_code == 400:
                    print("  NG: CSRF token validation failed (400 Bad Request)")
                    csrf_validation_passed = False
                else:
                    print(f"  WARNING: Unexpected status - {post_response.status_code}")
                    csrf_validation_passed = False
                    
            else:
                print("  NG: Failed to extract CSRF token")
                csrf_validation_passed = False
        
        print()
        
        # 4. 修正が必要な場合の実行
        if token_issue or not csrf_validation_passed:
            print("4. CSRF Token Implementation Fix")
            print("Fix strategy: Replace fallback token with proper Flask-WTF CSRF token")
            
            # app.pyのCSRFトークン生成部分を修正
            try:
                app_py_path = 'rccm-quiz-app/app.py'
                with open(app_py_path, 'r', encoding='utf-8') as f:
                    app_content = f.read()
                
                # 問題のあるフォールバックトークン生成コードを特定
                fallback_code_start = app_content.find('def csrf_token():')
                if fallback_code_start == -1:
                    print("  NG: csrf_token() function not found")
                    return False
                
                # 次の関数定義またはデコレータまで見つける
                next_function_patterns = ['\ndef ', '\n@app.', '\n@']
                fallback_code_end = len(app_content)  # デフォルトはファイル末尾
                
                for pattern in next_function_patterns:
                    pos = app_content.find(pattern, fallback_code_start + 1)
                    if pos != -1:
                        fallback_code_end = pos
                        break
                
                # 現在の実装を確認
                current_implementation = app_content[fallback_code_start:fallback_code_end]
                print(f"  Current implementation (first 100 chars):")
                print(f"    {current_implementation[:100]}...")
                
                # 修正版CSRFトークン実装
                fixed_csrf_implementation = '''def csrf_token():
    """CSRFトークンをテンプレートで利用可能にする（Flask-WTF完全対応版）"""
    try:
        from flask_wtf.csrf import generate_csrf
        return generate_csrf()
    except Exception as e:
        logger.warning(f"CSRF token generation error: {e}")
        # Flask-WTF使用時はフォールバックを使用せず、エラーを適切に処理
        return ""

'''
                
                # 修正実行
                fixed_content = app_content[:fallback_code_start] + fixed_csrf_implementation + app_content[fallback_code_end:]
                
                # バックアップ作成
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f'rccm-quiz-app/app.py.backup_csrf_fix_{timestamp}'
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(app_content)
                print(f"  OK: Backup created - {backup_file}")
                
                # 修正版保存
                with open(app_py_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"  OK: CSRF token generation fix applied")
                
                return True
                
            except Exception as e:
                print(f"  ERROR: CSRF fix failed - {str(e)[:60]}...")
                return False
        else:
            print("4. CSRF Implementation Status")
            print("  OK: CSRF implementation is working correctly - no fix needed")
            return True
        
    except Exception as e:
        print(f"ERROR: CSRF diagnosis failed - {str(e)[:60]}...")
        return False

def validate_csrf_fix():
    """CSRF修正の検証"""
    print()
    print("5. CSRF Fix Validation")
    
    try:
        # モジュールをリロード
        import importlib
        import sys
        
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        
        with app.test_client() as client:
            print("  Testing fixed CSRF token generation...")
            
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"    GET /exam status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"    NG: Failed to get exam page - {response.status_code}")
                return False
            
            # CSRFトークン確認
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            
            if token_match:
                csrf_token = token_match.group(1)
                print(f"    New CSRF token: {csrf_token[:20]}...")
                
                # フォールバックトークンでないことを確認
                if not csrf_token.startswith('fast_token_'):
                    print("    OK: Proper CSRF token generation confirmed")
                    
                    # POST送信テスト
                    post_data = {
                        'answer': 'A',
                        'qid': '1',
                        'csrf_token': csrf_token
                    }
                    
                    post_response = client.post('/exam', data=post_data)
                    print(f"    POST submission result: {post_response.status_code}")
                    
                    if post_response.status_code == 200:
                        print("    OK: CSRF fix successful - POST processing normal")
                        return True
                    else:
                        print(f"    NG: POST processing failed - {post_response.status_code}")
                        return False
                else:
                    print("    NG: Still using fallback token")
                    return False
            else:
                print("    NG: CSRF token not found")
                return False
                
    except Exception as e:
        print(f"  ERROR: Validation failed - {str(e)[:60]}...")
        return False

if __name__ == "__main__":
    print("=== Ultra Sync Task 8-9: CSRF Token Problem Complete Fix ===")
    print("Execution purpose: Solve root cause of 400 Bad Request errors")
    print("Target: Fix Flask-WTF CSRFProtect and fallback token inconsistency")
    print("=" * 70)
    print()
    
    # CSRF診断・修正実行
    fix_success = fix_csrf_token_implementation()
    
    if fix_success:
        # 修正検証実行
        validation_success = validate_csrf_fix()
        
        if validation_success:
            print()
            print("=" * 70)
            print("=== Task 8-9 Execution Result Summary ===")
            print("=" * 70)
            print("CSRF fix applied: SUCCESS")
            print("CSRF fix validation: SUCCESS")
            print()
            print("SUCCESS: Task 8-9 completed - CSRF token problem fixed")
            print("OK: 400 Bad Request error root cause resolved")
            print("OK: POST /exam processing normalized")
            print(">>> Task 8-10 (post-fix test re-execution) ready for execution")
            print()
            print("IMPORTANT: Task 8-9 marked as COMPLETED - problem actually solved")
        else:
            print()
            print("NG: Task 8-9 failed - CSRF fix validation failed")
            print(">>> Additional fixes required")
    else:
        print()
        print("NG: Task 8-9 failed - CSRF diagnosis/fix failed")
        print(">>> System-level investigation required")