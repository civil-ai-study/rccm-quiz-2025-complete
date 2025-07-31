#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: start_exam関数実行パス追跡
修正コードが実際に実行されているかを確認
"""

from app import app

def trace_start_exam():
    """start_exam関数の実行パスを追跡"""
    print("ULTRA SYNC: Tracing start_exam execution path")
    print("=" * 60)
    
    with app.app_context():
        with app.test_client() as client:
            # セッション初期化
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_name'] = 'trace_test'
            
            print("Testing: /start_exam/河川・砂防")
            
            # ログを有効にしてリクエスト送信
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            
            # POST request
            response = client.post('/start_exam/河川・砂防', data={'questions': '10'})
            
            print(f"Response status: {response.status_code}")
            print(f"Response length: {len(response.data)}")
            
            # レスポンス内容の一部を確認
            html = response.data.decode('utf-8', errors='ignore')
            if response.status_code == 200:
                if len(html) > 100:
                    print(f"Response preview: {html[:200]}...")
                else:
                    print(f"Full response: {html}")
            else:
                print("Non-200 response received")
            
            # セッション最終状態
            with client.session_transaction() as sess:
                print("\nFinal session state:")
                for key, value in sess.items():
                    if isinstance(value, list):
                        print(f"  {key}: list with {len(value)} items")
                    elif isinstance(value, dict):
                        print(f"  {key}: dict with {len(value)} keys")
                    else:
                        print(f"  {key}: {value}")

if __name__ == "__main__":
    trace_start_exam()