#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 Phase 1】Blueprint簡易テスト
依存関係なしでの品質保証
"""

import sys
import os
import json

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

def test_blueprint_isolation():
    """Blueprint分離・独立性テスト"""
    try:
        from blueprints.static_bp import static_bp
        from blueprints.health_bp import health_bp
        
        # Blueprintの独立性確認
        assert static_bp.name != health_bp.name
        assert static_bp.url_prefix != health_bp.url_prefix
        
        print("✅ Blueprint分離・独立性テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint分離・独立性テスト失敗: {e}")
        return False

def run_blueprint_tests():
    """全Blueprint テスト実行"""
    print("🧪 【ULTRATHIN区 Phase 1】Blueprint テスト開始")
    print("=" * 60)
    
    tests = [
        test_static_blueprint_creation,
        test_health_blueprint_creation,
        test_blueprint_isolation
    ]
    
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
    success = run_blueprint_tests()
    exit(0 if success else 1)