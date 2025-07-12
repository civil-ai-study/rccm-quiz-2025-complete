#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番環境直接テスト - 実際の動作確認
"""

import requests
import time

def test_production_direct():
    """本番環境直接テスト"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("🔍 本番環境直接テスト開始")
    print(f"対象: {base_url}")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # 1. ホームページアクセス
        print("1. ホームページアクセス...")
        home_response = session.get(base_url, timeout=30)
        print(f"   ステータス: {home_response.status_code}")
        print(f"   応答時間: {round(time.time(), 2)}秒")
        
        if home_response.status_code == 200:
            print("   ✅ ホームページ正常")
        else:
            print("   ❌ ホームページ異常")
            return False
        
        # 2. 基礎科目アクセステスト
        print("\n2. 基礎科目アクセステスト...")
        
        # まず/examにアクセス
        exam_response = session.get(f"{base_url}/exam", timeout=30)
        print(f"   /exam ステータス: {exam_response.status_code}")
        
        if exam_response.status_code == 200:
            # HTMLの内容確認
            content = exam_response.text
            if "基礎科目" in content or "部門" in content:
                print("   ✅ 試験ページ正常表示")
            else:
                print("   ⚠️ 試験ページ内容要確認")
        
        # 3. 基礎科目選択のPOSTテスト
        print("\n3. 基礎科目選択テスト...")
        
        # 基礎科目を選択するPOSTリクエスト
        post_data = {
            'exam_type': '基礎科目',
            'questions_count': '10'
        }
        
        start_response = session.post(f"{base_url}/start_exam", data=post_data, timeout=30)
        print(f"   選択POSTステータス: {start_response.status_code}")
        
        if start_response.status_code in [200, 302]:  # 302はリダイレクト
            print("   ✅ 基礎科目選択成功")
            
            # リダイレクト先を追跡
            if start_response.status_code == 302:
                redirect_url = start_response.headers.get('Location', '')
                print(f"   リダイレクト先: {redirect_url}")
                
                if redirect_url:
                    # リダイレクト先にアクセス
                    quiz_response = session.get(f"{base_url}{redirect_url}", timeout=30)
                    print(f"   問題ページステータス: {quiz_response.status_code}")
                    
                    if quiz_response.status_code == 200:
                        quiz_content = quiz_response.text
                        if "問題" in quiz_content or "選択" in quiz_content:
                            print("   ✅ 問題ページ正常表示")
                            return True
                        else:
                            print("   ⚠️ 問題ページ内容要確認")
                            print(f"   内容サンプル: {quiz_content[:200]}...")
        
        # 4. 直接クイズアクセス
        print("\n4. 直接クイズアクセステスト...")
        quiz_direct_response = session.get(f"{base_url}/quiz", timeout=30)
        print(f"   /quiz ステータス: {quiz_direct_response.status_code}")
        
        if quiz_direct_response.status_code == 200:
            print("   ✅ クイズページアクセス成功")
            return True
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_production_direct()
    print(f"\n🏁 本番環境テスト結果: {'成功' if success else '失敗'}")
    exit(0 if success else 1)