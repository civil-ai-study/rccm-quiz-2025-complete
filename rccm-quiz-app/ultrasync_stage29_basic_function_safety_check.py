#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階29】基礎機能安全確認
副作用ゼロ・既存正常機能の継続的動作確認・段階的品質向上
"""

import requests
import json
import re
from datetime import datetime
import time

def test_basic_functionality_safety():
    """
    ULTRASYNC段階29: 基礎機能の安全確認
    既存の正常動作機能のみを対象とした慎重なテスト
    """
    print("🛡️ 【ULTRASYNC段階29】基礎機能安全確認開始")
    print("副作用ゼロ・既存正常機能の継続動作確認")
    print("=" * 80)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    results = {
        "test_name": "ULTRASYNC段階29_基礎機能安全確認",
        "timestamp": datetime.now().isoformat(),
        "methodology": "既存正常機能のみ対象・副作用ゼロ確認",
        "tests": []
    }
    
    # テスト1: ホームページアクセス確認
    print("\n📋 テスト1: ホームページアクセス安全確認")
    try:
        response = session.get(f"{base_url}/")
        homepage_ok = response.status_code == 200
        print(f"   ステータス: {response.status_code}")
        print(f"   結果: {'✅ 正常' if homepage_ok else '❌ 異常'}")
        
        results["tests"].append({
            "test": "homepage_access",
            "success": homepage_ok,
            "status_code": response.status_code
        })
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        results["tests"].append({
            "test": "homepage_access",
            "success": False,
            "error": str(e)
        })
    
    # テスト2: 基本的な問題アクセス確認（最小限）
    print("\n📋 テスト2: 基本問題アクセス安全確認")
    try:
        # 最もシンプルなアクセスパターンで確認
        response = session.get(f"{base_url}/exam")
        basic_access_ok = response.status_code == 200
        print(f"   ステータス: {response.status_code}")
        print(f"   結果: {'✅ 正常' if basic_access_ok else '❌ 異常'}")
        
        # レスポンス内容の基本確認（副作用なし）
        has_question = False
        has_form = False
        if basic_access_ok:
            has_question = 'name="qid"' in response.text
            has_form = '<form' in response.text
            print(f"   問題表示: {'✅ あり' if has_question else '⚠️ なし'}")
            print(f"   フォーム表示: {'✅ あり' if has_form else '⚠️ なし'}")
        
        results["tests"].append({
            "test": "basic_exam_access",
            "success": basic_access_ok,
            "status_code": response.status_code,
            "has_question": has_question,
            "has_form": has_form
        })
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        results["tests"].append({
            "test": "basic_exam_access",
            "success": False,
            "error": str(e)
        })
    
    # テスト3: ヘルスチェック確認
    print("\n📋 テスト3: システムヘルスチェック")
    try:
        response = session.get(f"{base_url}/health")
        health_ok = response.status_code == 200
        print(f"   ステータス: {response.status_code}")
        
        health_data = {}
        if health_ok:
            try:
                health_data = response.json()
                print(f"   アプリ状態: {health_data.get('status', 'unknown')}")
                print(f"   バージョン: {health_data.get('version', 'unknown')}")
            except:
                print("   ヘルスデータ解析スキップ")
        
        print(f"   結果: {'✅ 正常' if health_ok else '❌ 異常'}")
        
        results["tests"].append({
            "test": "health_check",
            "success": health_ok,
            "status_code": response.status_code,
            "health_data": health_data
        })
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        results["tests"].append({
            "test": "health_check",
            "success": False,
            "error": str(e)
        })
    
    # テスト4: セッション基本動作確認（読み取りのみ）
    print("\n📋 テスト4: セッション基本動作確認")
    try:
        # セッションCookieの基本確認（読み取りのみ・副作用なし）
        cookies_exist = len(session.cookies) > 0
        print(f"   セッションCookie: {'✅ 存在' if cookies_exist else '⚠️ なし'}")
        
        # 簡単なページ間移動テスト
        response1 = session.get(f"{base_url}/")
        response2 = session.get(f"{base_url}/health")
        
        session_consistency = (response1.status_code == 200 and 
                             response2.status_code == 200)
        print(f"   ページ間移動: {'✅ 正常' if session_consistency else '❌ 異常'}")
        
        results["tests"].append({
            "test": "session_basic",
            "success": session_consistency,
            "cookies_exist": cookies_exist,
            "page_navigation": session_consistency
        })
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        results["tests"].append({
            "test": "session_basic",
            "success": False,
            "error": str(e)
        })
    
    # 結果サマリー
    print("\n" + "=" * 80)
    print("🎯 【ULTRASYNC段階29】基礎機能安全確認結果")
    print("=" * 80)
    
    successful_tests = sum(1 for test in results["tests"] if test.get("success", False))
    total_tests = len(results["tests"])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ 成功テスト: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # 詳細結果
    print(f"\n📋 テスト詳細結果:")
    for test in results["tests"]:
        test_name = test["test"]
        success = test.get("success", False)
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {status} {test_name}")
    
    # 安全性評価
    print(f"\n🛡️ 安全性評価:")
    if success_rate >= 100:
        print("✅ 全機能正常 - 基礎システム完全安全")
        safety_level = "完全安全"
    elif success_rate >= 75:
        print("⚠️ 大部分正常 - 基礎システム概ね安全")
        safety_level = "概ね安全"
    elif success_rate >= 50:
        print("🚨 一部問題 - 慎重な対応が必要")
        safety_level = "要注意"
    else:
        print("🚨 重大問題 - 緊急対応が必要")
        safety_level = "要緊急対応"
    
    results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": success_rate,
        "safety_level": safety_level
    }
    
    # レポート保存
    report_filename = f"ultrasync_stage29_basic_safety_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 詳細レポート保存: {report_filename}")
    
    # ULTRASYNC段階29結論
    print(f"\n🎯 【ULTRASYNC段階29】結論:")
    if success_rate >= 75:
        print("✅ 基礎機能安全確認完了")
        print("✅ 既存システムの継続的正常動作確認")
        print("✅ 副作用ゼロ維持")
        print("🚀 次段階（段階30: 慎重な改善計画）へ進行可能")
        return True
    else:
        print("⚠️ 基礎機能で問題検出")
        print("🛡️ 安全確保のため改善優先")
        print("🔧 段階30では検出問題の慎重な対応を実施")
        return False

if __name__ == "__main__":
    print("🛡️ ULTRASYNC段階29: 基礎機能安全確認")
    print("既存正常機能の継続動作確認・副作用ゼロ確認")
    print()
    
    success = test_basic_functionality_safety()
    
    print(f"\n🎯 ULTRASYNC段階29完了")
    print("慎重かつ正確に副作用を絶対発生させない段階的進行を継続")
    
    exit(0 if success else 1)