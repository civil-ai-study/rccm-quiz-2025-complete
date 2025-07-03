#!/usr/bin/env python3
"""
起動時間最適化スクリプト
"""

import time
import os

# 起動時の環境変数設定
os.environ['RCCM_FAST_MODE'] = 'false'  # まず遅延読み込みを無効化してテスト

print("=== RCCM アプリ起動時間計測 ===")
start_time = time.time()

# アプリのインポート
print("1. アプリインポート開始...")
import_start = time.time()
from app import app
import_end = time.time()
print(f"   インポート時間: {import_end - import_start:.2f}秒")

# テストリクエスト
print("2. 最初のリクエスト...")
request_start = time.time()
with app.test_client() as client:
    response = client.get('/')
    print(f"   ステータス: {response.status_code}")
request_end = time.time()
print(f"   リクエスト時間: {request_end - request_start:.2f}秒")

total_time = time.time() - start_time
print(f"\n総起動時間: {total_time:.2f}秒")

# 遅延読み込みモードでテスト
print("\n=== 遅延読み込みモードテスト ===")
os.environ['RCCM_LAZY_LOAD'] = 'true'
os.environ.pop('RCCM_FAST_MODE', None)

# アプリを再読み込み
import importlib
import sys
if 'app' in sys.modules:
    del sys.modules['app']

start_time2 = time.time()
print("1. アプリインポート開始（遅延読み込み）...")
import_start2 = time.time()
from app import app as app2
import_end2 = time.time()
print(f"   インポート時間: {import_end2 - import_start2:.2f}秒")

print("2. 最初のリクエスト（遅延読み込み）...")
request_start2 = time.time()
with app2.test_client() as client:
    response = client.get('/')
    print(f"   ステータス: {response.status_code}")
request_end2 = time.time()
print(f"   リクエスト時間: {request_end2 - request_start2:.2f}秒")

total_time2 = time.time() - start_time2
print(f"\n総起動時間（遅延読み込み）: {total_time2:.2f}秒")

print(f"\n改善率: {((total_time - total_time2) / total_time * 100):.1f}%")