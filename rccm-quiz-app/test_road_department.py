#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from app import app
import threading
import time

def test_road_department():
    """道路部門のアクセステスト"""
    print("=== 道路部門アクセステスト ===")
    
    # Flaskアプリケーションをテストモードで起動
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # 1. ホームページにアクセス
        print("1. ホームページアクセス")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        
        # 2. 道路部門にアクセス
        print("2. 道路部門アクセス")
        response = client.get('/department_study/道路')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   OK 道路部門アクセス成功")
            # レスポンスの内容を確認
            html_content = response.get_data(as_text=True)
            if "問題を開始" in html_content:
                print("   OK '問題を開始'ボタンが表示されています")
            else:
                print("   NG '問題を開始'ボタンが見つかりません")
                print(f"   Response: {html_content[:200]}...")
        else:
            print(f"   NG 道路部門アクセス失敗: {response.status_code}")
            print(f"   Response: {response.get_data(as_text=True)}")
        
        # 3. 専門問題開始をテスト
        print("3. 専門問題開始テスト")
        response = client.post('/start_exam/specialist', data={'department': '道路'})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   OK 専門問題開始成功")
            html_content = response.get_data(as_text=True)
            if "問題1" in html_content or "1問目" in html_content or "問題 1" in html_content:
                print("   OK 1問目が表示されています")
            else:
                print("   NG 1問目が見つかりません")
                print(f"   Response: {html_content[:500]}...")
        else:
            print(f"   NG 専門問題開始失敗: {response.status_code}")
            print(f"   Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_road_department()