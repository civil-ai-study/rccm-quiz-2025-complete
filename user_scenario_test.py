#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 ユーザー状況再現テスト
森林土木部門で上下水道問題が表示される問題の再現
"""

import os
import sys
import requests
import time
from datetime import datetime

def user_scenario_test():
    """ユーザーが報告した状況の再現テスト"""
    
    print("🚨 ユーザー状況再現テスト開始")
    print("=" * 60)
    print("再現シナリオ: 森林土木部門PRACTICE モード 問題 1/7 で上下水道問題が表示")
    
    # アプリケーションが動作しているかチェック
    base_url = "http://localhost:5005"
    
    try:
        # 1. ホームページアクセス
        print(f"\n1. ホームページアクセス: {base_url}")
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ ホームページアクセス失敗: {response.status_code}")
            return False
        
        print(f"✅ ホームページアクセス成功: {response.status_code}")
        
        # 2. 森林土木部門の問題開始
        print(f"\n2. 森林土木部門試験開始")
        exam_url = f"{base_url}/start_exam/森林土木"
        
        # セッション維持のためcookiesを使用
        session = requests.Session()
        
        # まずホームページでセッション開始
        session.get(base_url)
        
        # 森林土木部門を選択（POSTリクエスト）
        exam_data = {
            'questions_count': 7  # 7問に設定
        }
        
        print(f"アクセス URL: {exam_url}")
        print(f"送信データ: {exam_data}")
        
        exam_response = session.post(exam_url, data=exam_data, timeout=10)
        
        print(f"レスポンス: {exam_response.status_code}")
        
        if exam_response.status_code == 200:
            print("✅ 試験開始成功")
            
            # レスポンス内容から問題情報を抽出
            content = exam_response.text
            
            # 問題のカテゴリ情報を探す
            if "上水道及び工業用水道" in content:
                print("🚨 問題混在発見！上下水道問題が含まれています")
                print("問題箇所:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "上水道及び工業用水道" in line:
                        context_start = max(0, i-2)
                        context_end = min(len(lines), i+3)
                        for j in range(context_start, context_end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}{j+1:4d}: {lines[j]}")
                        break
                return False
            
            elif "森林土木" in content:
                print("✅ 正常: 森林土木問題が表示されています")
                return True
            
            else:
                print("⚠️ 問題カテゴリが特定できません")
                # HTMLから問題情報を抽出を試行
                if "<h3" in content and "question-text" in content:
                    print("問題内容が存在しますが、カテゴリ情報が見つかりません")
                return None
                
        elif exam_response.status_code == 302:
            print("リダイレクト発生 - リダイレクト先を確認")
            redirect_url = exam_response.headers.get('Location', '')
            print(f"リダイレクト先: {redirect_url}")
            
            if redirect_url:
                final_response = session.get(base_url + redirect_url, timeout=10)
                print(f"最終レスポンス: {final_response.status_code}")
                
                if final_response.status_code == 200:
                    content = final_response.text
                    if "上水道及び工業用水道" in content:
                        print("🚨 リダイレクト後に問題混在発見！")
                        return False
                    elif "森林土木" in content:
                        print("✅ リダイレクト後正常: 森林土木問題表示")
                        return True
            
            return None
            
        else:
            print(f"❌ 試験開始失敗: {exam_response.status_code}")
            print(f"エラー内容: {exam_response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ アプリケーションが起動していません")
        print("以下のコマンドでアプリケーションを起動してください:")
        print("cd rccm-quiz-app && python app.py")
        return False
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False

def check_application_status():
    """アプリケーション起動状況確認"""
    base_url = "http://localhost:5005"
    
    try:
        response = requests.get(base_url, timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("ユーザー状況再現テスト")
    print("=" * 60)
    
    # アプリケーション起動チェック
    if not check_application_status():
        print("⚠️ アプリケーションが起動していません")
        print("手動でアプリケーションを起動してからテストを実行してください:")
        print("cd rccm-quiz-app && python app.py")
        exit(1)
    
    # テスト実行
    result = user_scenario_test()
    
    print(f"\n{'='*60}")
    if result is True:
        print("✅ テスト結果: 正常 - 森林土木問題のみ表示")
    elif result is False:
        print("❌ テスト結果: 問題混在あり - 修正が必要")
    else:
        print("⚠️ テスト結果: 判定不可 - 詳細調査が必要")