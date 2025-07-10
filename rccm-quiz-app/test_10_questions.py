#!/usr/bin/env python3
"""
🛡️ ULTRATHIN段階79: 10問完走テスト自動実行
基礎科目10問を確実に完走する
"""

import requests
import time
import re

def test_10_questions():
    """基礎科目10問完走テスト"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("🛡️ ULTRATHIN段階79: 10問完走テスト開始")
    print("=" * 60)
    
    # 1. 試験開始
    print("\n📝 試験開始...")
    response = session.post(
        f"{base_url}/start_exam/basic",
        data={"questions": "10", "year": "2024"}
    )
    print(f"開始レスポンス: {response.status_code}")
    
    # 2. 10問回答
    for i in range(1, 11):
        print(f"\n📝 問題 {i}/10:")
        
        # 問題取得
        if i == 1:
            response = session.get(f"{base_url}/exam")
        else:
            response = session.get(f"{base_url}/exam/next")
            
        # qid抽出
        match = re.search(r'name="qid"\s+value="(\d+)"', response.text)
        if match:
            qid = match.group(1)
            print(f"   問題ID: {qid}")
            
            # 回答送信
            response = session.post(
                f"{base_url}/exam",
                data={"answer": "A", "qid": qid}
            )
            print(f"   回答送信: {response.status_code}")
            
            # エラーチェック
            if "エラー" in response.text or response.status_code != 200:
                print(f"   ❌ エラー発生!")
                error_match = re.search(r'<strong>(.*?)</strong>', response.text)
                if error_match:
                    print(f"   エラー内容: {error_match.group(1)}")
                return False
        else:
            print(f"   ❌ 問題IDが見つかりません")
            return False
        
        time.sleep(0.5)  # サーバー負荷軽減
    
    print("\n✅ 10問完走成功!")
    return True

if __name__ == "__main__":
    success = test_10_questions()
    print(f"\n最終結果: {'成功' if success else '失敗'}")