#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク Task 8-9: CSRFトークン問題診断および修正
目的: 400 Bad Requestエラーの根本原因であるCSRFトークン問題を解決
診断結果: CSRFProtect有効だが、テンプレートでフォールバックトークン使用が原因
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def diagnose_csrf_token_implementation():
    """CSRF token実装状況の詳細診断"""
    print("=== Task 8-9: CSRF Token実装診断開始 ===")
    print("目的: 400 Bad RequestエラーのCSRF原因を特定し修正方針決定")
    print()
    
    # 1. Flask-WTF CSRFProtect初期化状況確認
    print("【1. Flask-WTF CSRFProtect初期化状況確認】")
    
    try:
        from app import app
        
        # CSRF_AVAILABLEフラグ確認
        csrf_available = app.config.get('CSRF_AVAILABLE', False)
        wtf_csrf_enabled = app.config.get('WTF_CSRF_ENABLED', True)
        
        print(f"  CSRF_AVAILABLE: {csrf_available}")
        print(f"  WTF_CSRF_ENABLED: {wtf_csrf_enabled}")
        
        # CSRFProtectが初期化されているか確認
        csrf_extensions = [ext for ext in app.extensions.keys() if 'csrf' in ext.lower()]
        print(f"  CSRF Extensions: {csrf_extensions}")
        
        # SECRET_KEY設定確認（CSRF必須）
        secret_key_configured = bool(app.config.get('SECRET_KEY'))
        print(f"  SECRET_KEY設定: {secret_key_configured}")
        
        if secret_key_configured:
            print("  ✅ SECRET_KEY正常設定")
        else:
            print("  ❌ SECRET_KEY未設定（CSRF機能不全の原因）")
            
    except Exception as e:
        print(f"  ERROR Flask app initialization: {str(e)[:60]}...")
    
    print()
    
    # 2. テンプレートのCSRFトークン実装確認
    print("【2. テンプレートCSRFトークン実装確認】")
    
    try:
        with open('rccm-quiz-app/templates/exam.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # CSRFトークン関連コードを検索
        csrf_patterns = [
            'csrf_token()',
            'name="csrf_token"',
            'CSRFProtect',
            'fast_token_'
        ]
        
        for pattern in csrf_patterns:
            if pattern in template_content:
                lines_with_pattern = []
                for i, line in enumerate(template_content.split('\n'), 1):
                    if pattern in line:
                        lines_with_pattern.append((i, line.strip()))
                
                print(f"  {pattern}使用箇所: {len(lines_with_pattern)}箇所")
                for line_no, line_content in lines_with_pattern[:2]:
                    print(f"    Line {line_no}: {line_content[:60]}...")
        
        # フォーム構造確認
        if 'method="POST"' in template_content:
            print("  ✅ POST method設定確認")
        else:
            print("  ❌ POST method未設定")
            
        if 'action="/exam"' in template_content:
            print("  ✅ action属性正常")
        else:
            print("  ❌ action属性問題")
            
    except Exception as e:
        print(f"  ERROR template analysis: {str(e)[:60]}...")
    
    print()
    
    # 3. 実際のCSRFトークン生成テスト
    print("【3. CSRFトークン生成テスト】")
    
    try:
        with app.test_client() as client:
            # 問題画面取得してCSRFトークン確認
            response = client.get('/exam?department=road&type=specialist')
            response_text = response.get_data(as_text=True)
            
            print(f"  GET /exam status: {response.status_code}")
            
            # CSRFトークンの存在確認
            if 'csrf_token' in response_text:
                print("  ✅ CSRFトークン存在確認")
                
                # トークン値の抽出
                import re
                token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                if token_match:
                    token_value = token_match.group(1)
                    print(f"  トークン形式: {token_value[:20]}...")
                    
                    # フォールバックトークンか確認
                    if token_value.startswith('fast_token_'):
                        print("  ❌ フォールバックトークン検出（Flask-WTF非互換）")
                        return 'fallback_token_issue'
                    else:
                        print("  ✅ 正規CSRFトークン形式")
                        return 'proper_csrf_token'
                else:
                    print("  ❌ CSRFトークン値抽出失敗")
                    return 'token_extraction_failure'
            else:
                print("  ❌ CSRFトークンが存在しません")
                return 'no_csrf_token'
                
    except Exception as e:
        print(f"  ERROR CSRF token test: {str(e)[:60]}...")
        return 'test_failure'
    
    print()

def test_csrf_token_validation():
    """CSRFトークン検証テスト"""
    print("【4. CSRFトークン検証テスト実行】")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            # CSRFトークン抽出
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            
            if token_match:
                csrf_token = token_match.group(1)
                print(f"  CSRFトークン抽出成功: {csrf_token[:15]}...")
                
                # 正常なCSRFトークンでPOSTテスト
                post_data = {
                    'answer': 'A',
                    'qid': '1',
                    'csrf_token': csrf_token
                }
                
                post_response = client.post('/exam', data=post_data)
                print(f"  正常CSRFトークンPOST結果: {post_response.status_code}")
                
                if post_response.status_code == 200:
                    print("  ✅ CSRFトークン検証成功")
                    return True
                elif post_response.status_code == 400:
                    print("  ❌ CSRFトークン検証失敗（400 Bad Request）")
                    
                    # レスポンス内容確認
                    error_content = post_response.get_data(as_text=True)
                    if 'CSRF' in error_content.upper():
                        print("    原因: CSRF検証エラー")
                    elif 'TOKEN' in error_content.upper():
                        print("    原因: トークン関連エラー")
                    else:
                        print(f"    原因: 不明 - {error_content[:50]}...")
                    
                    return False
                else:
                    print(f"  ⚠️ 予期しないステータス: {post_response.status_code}")
                    return False
                    
            else:
                print("  ❌ CSRFトークン抽出失敗")
                return False
                
    except Exception as e:
        print(f"  ERROR CSRF validation test: {str(e)[:60]}...")
        return False

def fix_csrf_token_implementation():
    """CSRFトークン実装修正"""
    print()
    print("【5. CSRFトークン実装修正実行】")
    
    # 修正方針の決定
    print("修正方針の決定:")
    print("  問題: フォールバックトークン（fast_token_）とFlask-WTF CSRFProtectの不整合")
    print("  解決: 正規のFlask-WTF CSRFトークン生成に修正")
    print()
    
    # app.pyのCSRFトークン生成部分を修正
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # 問題のあるフォールバックトークン生成コードを特定
        fallback_code_start = app_content.find('def csrf_token():')
        if fallback_code_start == -1:
            print("  ❌ csrf_token()関数が見つかりません")
            return False
        
        fallback_code_end = app_content.find('def ', fallback_code_start + 1)
        if fallback_code_end == -1:
            # ファイル末尾まで
            fallback_code_end = len(app_content)
        
        # 現在の実装を表示
        current_implementation = app_content[fallback_code_start:fallback_code_end]
        print(f"  現在の実装（最初の200文字）:")
        print(f"    {current_implementation[:200]}...")
        
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
        print(f"  ✅ バックアップ作成: {backup_file}")
        
        # 修正版保存
        with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✅ CSRFトークン生成修正完了")
        
        return True
        
    except Exception as e:
        print(f"  ERROR during CSRF fix: {str(e)[:60]}...")
        return False

def validate_csrf_fix():
    """CSRF修正の検証"""
    print()
    print("【6. CSRF修正検証】")
    
    try:
        # app.pyをリロードして修正を適用
        import importlib
        import sys
        
        # モジュールをリロード
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        
        with app.test_client() as client:
            print("  修正後のCSRFトークン生成テスト...")
            
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"    GET /exam status: {response.status_code}")
            
            # CSRFトークン確認
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            
            if token_match:
                csrf_token = token_match.group(1)
                print(f"    新CSRFトークン: {csrf_token[:20]}...")
                
                # フォールバックトークンでないことを確認
                if not csrf_token.startswith('fast_token_'):
                    print("    ✅ 正規CSRFトークン生成確認")
                    
                    # POST送信テスト
                    post_data = {
                        'answer': 'A',
                        'qid': '1',
                        'csrf_token': csrf_token
                    }
                    
                    post_response = client.post('/exam', data=post_data)
                    print(f"    POST送信結果: {post_response.status_code}")
                    
                    if post_response.status_code == 200:
                        print("    ✅ CSRF修正成功：POST処理正常")
                        return True
                    else:
                        print(f"    ❌ POST処理失敗: {post_response.status_code}")
                        return False
                else:
                    print("    ❌ まだフォールバックトークンが使用されています")
                    return False
            else:
                print("    ❌ CSRFトークンが見つかりません")
                return False
                
    except Exception as e:
        print(f"  ERROR during validation: {str(e)[:60]}...")
        return False

def run_csrf_diagnosis_and_fix():
    """CSRF診断および修正のメイン実行"""
    print("=== ウルトラシンク Task 8-9: CSRFトークン問題完全修正 ===")
    print("実行目的: 400 Bad Requestエラーの根本原因を解決")
    print("対象: Flask-WTF CSRFProtectとフォールバックトークンの不整合修正")
    print("=" * 70)
    
    results = {}
    
    # 段階1: CSRF実装診断
    csrf_issue_type = diagnose_csrf_token_implementation()
    results['diagnosis'] = csrf_issue_type
    
    # 段階2: CSRF検証テスト
    csrf_validation_success = test_csrf_token_validation()
    results['validation_test'] = csrf_validation_success
    
    # 段階3: 修正が必要な場合は実行
    if csrf_issue_type == 'fallback_token_issue' or not csrf_validation_success:
        print()
        print("🔧 CSRF問題確認済み - 修正実行")
        
        fix_success = fix_csrf_token_implementation()
        results['fix_applied'] = fix_success
        
        if fix_success:
            validation_success = validate_csrf_fix()
            results['fix_validation'] = validation_success
        else:
            results['fix_validation'] = False
    else:
        print()
        print("✅ CSRF実装正常 - 修正不要")
        results['fix_applied'] = 'not_needed'
        results['fix_validation'] = True
    
    # 結果サマリー
    print()
    print("=" * 70)
    print("=== Task 8-9 実行結果サマリー ===")
    print("=" * 70)
    
    print(f"CSRF診断結果: {results['diagnosis']}")
    print(f"CSRF検証テスト: {'成功' if results['validation_test'] else '失敗'}")
    print(f"修正適用: {results['fix_applied']}")
    print(f"修正検証: {'成功' if results['fix_validation'] else '失敗'}")
    
    # 最終判定
    if results['fix_validation']:
        print()
        print("🎉 Task 8-9 完了: CSRFトークン問題修正成功")
        print("✅ 400 Bad Requestエラーの根本原因解決")
        print("✅ POST /exam処理正常化")
        print(">>> Task 8-10（修正後テスト再実行）実行準備完了")
        return True
    else:
        print()
        print("❌ Task 8-9 失敗: CSRF問題未解決")
        print(">>> 追加修正が必要")
        return False

if __name__ == "__main__":
    success = run_csrf_diagnosis_and_fix()
    if success:
        print("\n✅ ウルトラシンク Task 8-9 成功")
    else:
        print("\n❌ ウルトラシンク Task 8-9 要追加修正")