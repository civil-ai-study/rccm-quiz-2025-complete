#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小限Flask環境セットアップ・Blueprint動作確認システム
既存環境に影響を与えずFlask環境を構築してBlueprint検証
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

class MinimalFlaskSetup:
    """最小限Flask環境セットアップ"""
    
    def __init__(self):
        self.temp_dir = None
        self.venv_path = None
        self.setup_complete = False
        self.verification_results = {}
    
    def create_isolated_environment(self):
        """分離された環境を作成"""
        try:
            # 一時ディレクトリ作成
            self.temp_dir = tempfile.mkdtemp(prefix="flask_test_")
            self.venv_path = os.path.join(self.temp_dir, "venv")
            
            print(f"🔧 一時環境作成: {self.temp_dir}")
            
            # 仮想環境作成
            subprocess.run([
                sys.executable, "-m", "venv", self.venv_path
            ], check=True)
            
            # 仮想環境のPythonパス
            if os.name == 'nt':  # Windows
                python_path = os.path.join(self.venv_path, "Scripts", "python.exe")
                pip_path = os.path.join(self.venv_path, "Scripts", "pip.exe")
            else:  # Unix-like
                python_path = os.path.join(self.venv_path, "bin", "python")
                pip_path = os.path.join(self.venv_path, "bin", "pip")
            
            # Flask最小限インストール
            subprocess.run([
                pip_path, "install", "flask==3.0.0", "psutil==5.9.8"
            ], check=True)
            
            print("✅ 仮想環境セットアップ完了")
            self.setup_complete = True
            
            return python_path, pip_path
            
        except Exception as e:
            print(f"❌ 環境セットアップエラー: {e}")
            return None, None
    
    def copy_blueprints(self):
        """Blueprintファイルをテスト環境にコピー"""
        try:
            # blueprintsディレクトリ作成
            blueprints_dir = os.path.join(self.temp_dir, "blueprints")
            os.makedirs(blueprints_dir, exist_ok=True)
            
            # 既存Blueprintファイルをコピー
            source_blueprints = [
                '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/blueprints/static_bp.py',
                '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/blueprints/health_bp.py'
            ]
            
            copied_files = []
            for src in source_blueprints:
                if os.path.exists(src):
                    dst = os.path.join(blueprints_dir, os.path.basename(src))
                    shutil.copy2(src, dst)
                    copied_files.append(dst)
                    print(f"📁 コピー: {os.path.basename(src)}")
            
            return copied_files
            
        except Exception as e:
            print(f"❌ ファイルコピーエラー: {e}")
            return []
    
    def create_test_app(self):
        """テスト用Flaskアプリケーション作成"""
        test_app_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blueprint動作確認テスト用Flaskアプリケーション
"""

import os
import sys
from flask import Flask

# Blueprintインポート
try:
    from blueprints.static_bp import static_bp, get_static_blueprint_info
    static_bp_available = True
except ImportError as e:
    print(f"static_bp import error: {e}")
    static_bp_available = False

try:
    from blueprints.health_bp import health_bp, get_health_blueprint_info
    health_bp_available = True
except ImportError as e:
    print(f"health_bp import error: {e}")
    health_bp_available = False

def create_test_app():
    """テスト用Flaskアプリケーション作成"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Blueprint登録
    if static_bp_available:
        app.register_blueprint(static_bp)
        print("✅ static_bp登録完了")
    
    if health_bp_available:
        app.register_blueprint(health_bp)
        print("✅ health_bp登録完了")
    
    @app.route('/')
    def test_home():
        return "Blueprint Test App - Working!"
    
    @app.route('/test/blueprints')
    def test_blueprints():
        results = {
            'static_bp_available': static_bp_available,
            'health_bp_available': health_bp_available,
            'registered_blueprints': [bp.name for bp in app.blueprints.values()]
        }
        
        if static_bp_available:
            results['static_bp_info'] = get_static_blueprint_info()
        
        if health_bp_available:
            results['health_bp_info'] = get_health_blueprint_info()
        
        from flask import jsonify
        return jsonify(results)
    
    return app

def run_tests():
    """Blueprint動作テスト実行"""
    app = create_test_app()
    
    # テストクライアント作成
    with app.test_client() as client:
        print("\\n🧪 Blueprint動作テスト開始")
        
        # 基本テスト
        response = client.get('/')
        print(f"  ・基本ルート: {response.status_code} - {response.get_data(as_text=True)[:50]}")
        
        # Blueprint情報テスト
        response = client.get('/test/blueprints')
        print(f"  ・Blueprint情報: {response.status_code}")
        
        # static_bpテスト
        if static_bp_available:
            tests = [
                '/favicon.ico',
                '/manifest.json',
                '/robots.txt',
                '/sitemap.xml'
            ]
            
            for test_path in tests:
                response = client.get(test_path)
                print(f"  ・{test_path}: {response.status_code}")
        
        # health_bpテスト
        if health_bp_available:
            tests = [
                '/health/simple',
                '/health/status',
                '/health/check',
                '/health/ready',
                '/health/live'
            ]
            
            for test_path in tests:
                try:
                    response = client.get(test_path)
                    print(f"  ・{test_path}: {response.status_code}")
                except Exception as e:
                    print(f"  ・{test_path}: ERROR - {e}")
        
        print("\\n✅ Blueprint動作テスト完了")

if __name__ == "__main__":
    run_tests()
'''
        
        # テスト用アプリケーションファイル作成
        test_app_path = os.path.join(self.temp_dir, "test_app.py")
        with open(test_app_path, 'w', encoding='utf-8') as f:
            f.write(test_app_code)
        
        return test_app_path
    
    def run_blueprint_tests(self, python_path):
        """Blueprint動作テスト実行"""
        try:
            # テストアプリケーション作成
            test_app_path = self.create_test_app()
            
            # テスト実行
            print("\n🧪 Blueprint動作テスト実行中...")
            
            result = subprocess.run([
                python_path, test_app_path
            ], cwd=self.temp_dir, capture_output=True, text=True)
            
            self.verification_results = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            print("📋 テスト結果:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️  エラー出力:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            return False
    
    def cleanup(self):
        """環境クリーンアップ"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 クリーンアップ完了: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️  クリーンアップエラー: {e}")
    
    def get_setup_instructions(self):
        """セットアップ手順説明"""
        return """
🔧 最小限Flask環境セットアップ手順

1. 仮想環境作成:
   python3 -m venv flask_test_env
   source flask_test_env/bin/activate  # Linux/Mac
   # または
   flask_test_env\\Scripts\\activate  # Windows

2. 必要パッケージインストール:
   pip install flask==3.0.0 psutil==5.9.8

3. Blueprintテスト実行:
   python minimal_flask_setup.py

4. 手動テスト:
   python test_app.py
   # 別ターミナルで:
   curl http://localhost:5000/health/simple
   curl http://localhost:5000/favicon.ico

5. 環境削除:
   deactivate
   rm -rf flask_test_env
"""

def main():
    """メイン処理"""
    print("🚀 最小限Flask環境セットアップ開始")
    
    setup = MinimalFlaskSetup()
    
    try:
        # 分離環境作成
        python_path, pip_path = setup.create_isolated_environment()
        
        if not setup.setup_complete:
            print("❌ 環境セットアップ失敗")
            return
        
        # Blueprintコピー
        copied_files = setup.copy_blueprints()
        print(f"📁 Blueprint準備完了: {len(copied_files)}個")
        
        # テスト実行
        success = setup.run_blueprint_tests(python_path)
        
        if success:
            print("✅ すべてのBlueprint動作テストが成功しました")
        else:
            print("❌ Blueprint動作テストで問題が発生しました")
        
        # 手順説明
        print("\n📖 手動セットアップ手順:")
        print(setup.get_setup_instructions())
        
    finally:
        # クリーンアップ
        setup.cleanup()

if __name__ == "__main__":
    main()