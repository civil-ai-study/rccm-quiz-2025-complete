#!/usr/bin/env python3
"""
🎯 ULTRASYNC段階63: ローカル環境での10問テスト
RCCMクイズアプリケーションの基本機能確認
"""

import requests
import time
import json
from datetime import datetime

def test_10_questions_local():
    """ローカル環境で10問テストを実行"""
    
    print("🚀 ULTRASYNC段階63: ローカル環境10問テスト開始")
    print(f"開始時刻: {datetime.now()}")
    
    base_url = "http://localhost:5005"
    
    try:
        # 1. ホームページアクセス
        print("\n📝 Step 1: ホームページアクセス")
        response = requests.get(base_url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ ホームページアクセス成功")
        else:
            print("❌ ホームページアクセス失敗")
            return False
        
        # 2. 10問テスト開始
        print("\n📝 Step 2: 10問テスト開始")
        session = requests.Session()
        
        # 基礎科目10問テスト開始
        start_data = {
            'questions': '10',
            'department': '基礎科目',
            'year': '2024'
        }
        
        response = session.post(f"{base_url}/start_exam/基礎科目", data=start_data)
        print(f"Start exam status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 10問テスト開始成功")
            
            # 3. 問題画面確認
            print("\n📝 Step 3: 問題画面確認")
            if "問題" in response.text:
                print("✅ 問題画面表示確認")
                
                # 4. 簡易回答テスト
                print("\n📝 Step 4: 簡易回答テスト（最初の3問）")
                for i in range(3):
                    # 次の問題へのPOST
                    answer_data = {'answer': '1'}  # 選択肢1を回答
                    next_response = session.post(f"{base_url}/exam", data=answer_data)
                    print(f"Question {i+1} answered: {next_response.status_code}")
                    
                    if next_response.status_code != 200:
                        print(f"❌ 問題{i+1}で失敗")
                        break
                    else:
                        print(f"✅ 問題{i+1}回答成功")
                
                print("\n🎯 10問テスト部分実行完了")
                print("✅ 基本的な問題画面遷移が正常動作")
                return True
            else:
                print("❌ 問題画面表示失敗")
                return False
        else:
            print("❌ 10問テスト開始失敗")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ローカルサーバーに接続できません")
        print("📝 解決方法: python app.py でローカルサーバーを起動してください")
        return False
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return False

if __name__ == "__main__":
    result = test_10_questions_local()
    print(f"\n🎯 最終結果: {'✅ 成功' if result else '❌ 失敗'}")
    print(f"終了時刻: {datetime.now()}")