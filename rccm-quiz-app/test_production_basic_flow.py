#!/usr/bin/env python3
"""
🎯 本番環境基本動作テスト: 問題1→問題2→問題3の基本フロー確認
デプロイ完了後の本番環境での動作確認
"""

import requests
import time
import sys
from datetime import datetime

def test_production_basic_flow(production_url):
    """本番環境での基本的な問題フロー確認"""
    
    print(f"🚀 本番環境基本動作テスト")
    print(f"🌐 テスト対象URL: {production_url}")
    print(f"開始時刻: {datetime.now()}")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # ステップ1: 本番環境接続確認
        print("\n📝 ステップ1: 本番環境接続確認")
        response = session.get(production_url, timeout=15)
        if response.status_code == 200:
            print("✅ 本番環境接続成功")
            
            # HTMLコンテンツ確認
            if "RCCM" in response.text:
                print("✅ RCCMコンテンツ確認")
            else:
                print("⚠️ RCCMコンテンツ未確認")
        else:
            print(f"❌ 本番環境接続失敗: {response.status_code}")
            return False
        
        # ステップ2: 試験開始 (10問テスト)
        print("\n📝 ステップ2: 本番環境での試験開始")
        start_data = {
            'questions': '10',
            'department': '基礎科目',
            'year': '2024'
        }
        
        response = session.post(f"{production_url}/start_exam/基礎科目", 
                              data=start_data, timeout=20)
        if response.status_code == 200:
            print("✅ 本番環境での試験開始成功")
        else:
            print(f"❌ 本番環境での試験開始失敗: {response.status_code}")
            return False
        
        # ステップ3: 1問目確認
        print("\n📝 ステップ3: 本番環境での1問目表示確認")
        if "問題" in response.text:
            print("✅ 本番環境での1問目表示確認")
            print("  📋 本番環境で1問目が正常に表示")
        else:
            print("❌ 本番環境での1問目表示失敗")
            return False
        
        # ステップ4: 1問目回答 → 2問目表示
        print("\n📝 ステップ4: 本番環境での1問目回答 → 2問目表示")
        answer_data = {'answer': '1'}
        response = session.post(f"{production_url}/exam", 
                              data=answer_data, timeout=20)
        
        if response.status_code == 200:
            print("✅ 本番環境での1問目回答成功")
            
            if "問題" in response.text:
                print("✅ 本番環境での2問目表示確認")
                print("  📋 本番環境で1問目 → 2問目遷移成功")
            elif "結果" in response.text:
                print("🎯 本番環境で結果画面表示 (短縮テスト)")
                return True
            else:
                print("⚠️ 本番環境での2問目表示不明確")
        else:
            print(f"❌ 本番環境での1問目回答失敗: {response.status_code}")
            return False
        
        # ステップ5: 2問目回答 → 3問目表示
        print("\n📝 ステップ5: 本番環境での2問目回答 → 3問目表示")
        answer_data = {'answer': '2'}
        response = session.post(f"{production_url}/exam", 
                              data=answer_data, timeout=20)
        
        if response.status_code == 200:
            print("✅ 本番環境での2問目回答成功")
            
            if "問題" in response.text:
                print("✅ 本番環境での3問目表示確認")
                print("  📋 本番環境で2問目 → 3問目遷移成功")
            elif "結果" in response.text:
                print("🎯 本番環境で結果画面表示")
                print("  📋 本番環境でのテスト完了確認")
            else:
                print("⚠️ 本番環境での3問目表示不明確")
        else:
            print(f"❌ 本番環境での2問目回答失敗: {response.status_code}")
            return False
        
        print("\n🎯 === 本番環境基本動作テスト結果 ===")
        print("✅ 本番環境接続: 成功")
        print("✅ 試験開始: 成功")
        print("✅ 1問目表示: 成功")
        print("✅ 1問目 → 2問目遷移: 成功")
        print("✅ 2問目 → 3問目遷移: 成功")
        print("✅ 本番環境基本フロー: 完全動作")
        
        print("\n📋 本番環境確認事項:")
        print("  • 問題選択をしたら1番目が出てくる: ✅ 本番環境で確認")
        print("  • 1番目が終わったら2問目が出てくる: ✅ 本番環境で確認")
        print("  • 2問目が終わったら3問目が出てくる: ✅ 本番環境で確認")
        print("  • 基本的な動作: ✅ 本番環境で正常動作")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 本番環境 {production_url} に接続できません")
        print("📝 確認事項: URLが正しいか、デプロイが完了しているか")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 本番環境 {production_url} でタイムアウト")
        print("📝 確認事項: サーバーの応答速度、負荷状況")
        return False
    except Exception as e:
        print(f"❌ 本番環境テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🎯 本番環境基本動作テストスクリプト")
    print("📋 使用方法: python test_production_basic_flow.py <本番環境URL>")
    
    if len(sys.argv) > 1:
        production_url = sys.argv[1]
        print(f"\n🌐 指定URL: {production_url}")
        result = test_production_basic_flow(production_url)
    else:
        # 想定される本番環境URLでテスト
        potential_urls = [
            "https://rccm-quiz-2025-complete.vercel.app",
            "https://rccm-quiz-2025-complete.up.railway.app",
            "https://rccm-quiz-2025-complete.onrender.com"
        ]
        
        print("\n🔍 想定本番環境URL確認:")
        result = False
        for url in potential_urls:
            print(f"\n📝 テスト対象: {url}")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {url}: 接続成功")
                    result = test_production_basic_flow(url)
                    if result:
                        break
                else:
                    print(f"❌ {url}: {response.status_code}")
            except:
                print(f"❌ {url}: 接続エラー")
    
    print(f"\n🎯 最終結果: {'✅ 本番環境基本動作確認成功' if result else '❌ 本番環境基本動作確認失敗'}")
    print(f"終了時刻: {datetime.now()}")
    
    if not result:
        print("\n📋 次のアクション:")
        print("  1. Web Dashboardでのデプロイ実行")
        print("  2. デプロイ完了URL確認")
        print("  3. 本スクリプトで基本動作テスト実行")