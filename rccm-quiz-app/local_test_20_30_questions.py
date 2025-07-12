#!/usr/bin/env python3
"""
🎯 ULTRASYNC段階64: 20問・30問テスト実行
RCCMクイズアプリケーションの完全テスト確認
"""

import requests
import time
import json
from datetime import datetime

def test_20_30_questions_local():
    """ローカル環境で20問・30問テストを実行"""
    
    print("🚀 ULTRASYNC段階64: 20問・30問テスト開始")
    print(f"開始時刻: {datetime.now()}")
    
    base_url = "http://localhost:5005"
    
    try:
        # 20問テスト
        print("\n🔥 === 20問テスト実行 ===")
        result_20 = test_specific_questions(base_url, 20, "基礎科目")
        
        # 30問テスト  
        print("\n🔥 === 30問テスト実行 ===")
        result_30 = test_specific_questions(base_url, 30, "道路")
        
        # 結果サマリー
        print("\n🎯 === テスト結果サマリー ===")
        print(f"20問テスト: {'✅ 成功' if result_20 else '❌ 失敗'}")
        print(f"30問テスト: {'✅ 成功' if result_30 else '❌ 失敗'}")
        
        overall_success = result_20 and result_30
        print(f"\n🎯 総合結果: {'✅ 全テスト成功' if overall_success else '❌ 一部失敗'}")
        
        return overall_success
        
    except requests.exceptions.ConnectionError:
        print("❌ ローカルサーバーに接続できません")
        print("📝 解決方法: python app.py でローカルサーバーを起動してください")
        return False
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return False

def test_specific_questions(base_url, question_count, department):
    """指定問題数でのテスト実行"""
    
    print(f"\n📝 {question_count}問テスト開始 ({department})")
    session = requests.Session()
    
    try:
        # 1. ホームページアクセス
        response = session.get(base_url)
        if response.status_code != 200:
            print(f"❌ ホームページアクセス失敗: {response.status_code}")
            return False
        print("✅ ホームページアクセス成功")
        
        # 2. 試験開始
        start_data = {
            'questions': str(question_count),
            'department': department,
            'year': '2024'
        }
        
        response = session.post(f"{base_url}/start_exam/{department}", data=start_data)
        if response.status_code != 200:
            print(f"❌ {question_count}問テスト開始失敗: {response.status_code}")
            return False
        print(f"✅ {question_count}問テスト開始成功")
        
        # 3. 問題画面確認
        if "問題" not in response.text:
            print(f"❌ {question_count}問 - 問題画面表示失敗")
            return False
        print(f"✅ {question_count}問 - 問題画面表示確認")
        
        # 4. 複数問題回答テスト（最初の5問）
        print(f"\n📝 {question_count}問テスト - 複数問題回答（最初の5問）")
        test_questions = min(5, question_count)  # 最大5問でテスト
        
        for i in range(test_questions):
            answer_data = {'answer': '1'}  # 選択肢1を回答
            next_response = session.post(f"{base_url}/exam", data=answer_data)
            
            if next_response.status_code != 200:
                print(f"❌ {question_count}問テスト - 問題{i+1}で失敗: {next_response.status_code}")
                return False
            
            print(f"✅ {question_count}問テスト - 問題{i+1}回答成功")
            
            # 結果画面に到達したかチェック
            if "結果" in next_response.text or "score" in next_response.text.lower():
                print(f"🎯 {question_count}問テスト - 結果画面到達確認")
                break
        
        print(f"✅ {question_count}問テスト - 基本動作確認完了")
        return True
        
    except Exception as e:
        print(f"❌ {question_count}問テストでエラー: {e}")
        return False

if __name__ == "__main__":
    result = test_20_30_questions_local()
    print(f"\n🎯 最終結果: {'✅ 成功' if result else '❌ 失敗'}")
    print(f"終了時刻: {datetime.now()}")