#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 Phase 1】Blueprint単体テスト
副作用ゼロでの新Blueprint機能テスト
品質保証強化第一段階
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のBlueprint import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_static_blueprint_creation():
    """静的コンテンツBlueprint作成テスト"""
    try:
        from blueprints.static_bp import static_bp, get_static_blueprint_info
        
        # Blueprint基本属性確認
        assert static_bp.name == 'static_content'
        assert static_bp.url_prefix == ''
        
        # Blueprint情報取得テスト
        info = get_static_blueprint_info()
        assert info['name'] == 'static_content'
        assert info['risk_level'] == 'zero'
        assert len(info['routes']) == 6
        
        print("✅ 静的コンテンツBlueprint作成テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 静的コンテンツBlueprint作成テスト失敗: {e}")
        return False

def test_health_blueprint_creation():
    """ヘルスチェックBlueprint作成テスト"""
    try:
        from blueprints.health_bp import health_bp, get_health_blueprint_info
        
        # Blueprint基本属性確認
        assert health_bp.name == 'health_check'
        assert health_bp.url_prefix == '/health'
        
        # Blueprint情報取得テスト
        info = get_health_blueprint_info()
        assert info['name'] == 'health_check'
        assert info['risk_level'] == 'zero'
        assert len(info['routes']) == 6
        
        print("✅ ヘルスチェックBlueprint作成テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ ヘルスチェックBlueprint作成テスト失敗: {e}")
        return False

@pytest.fixture
def mock_flask_app():
    """Flask アプリケーションモック"""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def test_static_blueprint_routes(mock_flask_app):
    """静的コンテンツBlueprint ルートテスト"""
    try:
        from blueprints.static_bp import static_bp
        
        # Blueprint登録
        mock_flask_app.register_blueprint(static_bp)
        
        with mock_flask_app.test_client() as client:
            # favicon.icoテスト
            response = client.get('/favicon.ico')
            assert response.status_code in [200, 404]  # ファイル存在に依存
            
            # manifest.jsonテスト
            response = client.get('/manifest.json')
            assert response.status_code == 200
            
            # レスポンスがJSONかチェック
            if response.content_type == 'application/json':
                data = json.loads(response.data)
                assert 'name' in data
                assert 'RCCM' in data['name']
            
            # Service Workerテスト
            response = client.get('/sw.js')
            assert response.status_code == 200
            assert 'javascript' in response.content_type
        
        print("✅ 静的コンテンツBlueprint ルートテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 静的コンテンツBlueprint ルートテスト失敗: {e}")
        return False

def test_health_blueprint_routes(mock_flask_app):
    """ヘルスチェックBlueprint ルートテスト"""
    try:
        from blueprints.health_bp import health_bp
        
        # Blueprint登録
        mock_flask_app.register_blueprint(health_bp)
        
        with mock_flask_app.test_client() as client:
            # シンプルヘルスチェック
            response = client.get('/health/simple')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert 'timestamp' in data
            
            # 詳細ヘルスチェック
            response = client.get('/health/')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'system' in data
            assert 'process' in data
            assert 'filesystem' in data
            
            # ライブネスチェック
            response = client.get('/health/live')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['alive'] == True
            assert data['test_passed'] == True
        
        print("✅ ヘルスチェックBlueprint ルートテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ ヘルスチェックBlueprint ルートテスト失敗: {e}")
        return False

def test_blueprint_isolation():
    """Blueprint分離・独立性テスト"""
    try:
        from blueprints.static_bp import static_bp
        from blueprints.health_bp import health_bp
        
        # Blueprintの独立性確認
        assert static_bp.name != health_bp.name
        assert static_bp.url_prefix != health_bp.url_prefix
        
        # Blueprintにapp特有の依存関係がないことを確認
        assert not hasattr(static_bp, 'app')
        assert not hasattr(health_bp, 'app')
        
        print("✅ Blueprint分離・独立性テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint分離・独立性テスト失敗: {e}")
        return False

def test_error_handling():
    """Blueprint エラーハンドリングテスト"""
    try:
        from flask import Flask
        from blueprints.health_bp import health_bp
        
        app = Flask(__name__)
        app.register_blueprint(health_bp)
        
        with app.test_client() as client:
            # 存在しないルートへのアクセス
            response = client.get('/health/nonexistent')
            assert response.status_code == 404
            
            # ヘルスチェック機能は正常動作
            response = client.get('/health/simple')
            assert response.status_code == 200
        
        print("✅ Blueprint エラーハンドリングテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint エラーハンドリングテスト失敗: {e}")
        return False

def run_all_blueprint_tests():
    """全Blueprint テスト実行"""
    print("🧪 【ULTRATHIN区 Phase 1】Blueprint テスト開始")
    print("=" * 60)
    
    tests = [
        test_static_blueprint_creation,
        test_health_blueprint_creation,
        test_blueprint_isolation,
        test_error_handling
    ]
    
    # Flaskアプリが必要なテスト
    try:
        from flask import Flask
        mock_app = Flask(__name__)
        mock_app.config['TESTING'] = True
        
        flask_tests = [
            lambda: test_static_blueprint_routes(mock_app),
            lambda: test_health_blueprint_routes(mock_app)
        ]
        tests.extend(flask_tests)
    except ImportError:
        print("⚠️ Flask未利用環境: Flask依存テストをスキップ")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Blueprint テスト結果:")
    print(f"   ✅ 成功: {passed}件")
    print(f"   ❌ 失敗: {failed}件")
    print(f"   📊 成功率: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 全Blueprint テスト成功！副作用ゼロでの実装完了")
    else:
        print("⚠️ 一部テスト失敗: 修正が必要")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_blueprint_tests()
    exit(0 if success else 1)