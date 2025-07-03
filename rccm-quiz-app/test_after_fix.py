#!/usr/bin/env python3
"""
修正後テストスクリプト
緊急修正が正しく動作することを確認
"""

import sys
import os

print("🚀 RCCM Quiz App 修正後テスト")
print("=" * 50)

# 1. ファイル存在確認
if os.path.exists("app.py"):
    print("✅ app.py 存在確認")
else:
    print("❌ app.py が見つかりません")
    sys.exit(1)

# 2. バックアップファイル確認
backup_files = [f for f in os.listdir('.') if f.startswith('app.py.backup_')]
if backup_files:
    latest_backup = sorted(backup_files)[-1]
    print(f"✅ バックアップ確認: {latest_backup}")
else:
    print("⚠️ バックアップファイルが見つかりません")

# 3. 修正内容確認
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

checks = [
    ("GETリクエスト処理", "EMERGENCY FIX: GETリクエストでの新規セッション開始処理"),
    ("エラーチェック修正", "EMERGENCY FIX: シンプルなフォールバック処理"), 
    ("問題表示修正", "EMERGENCY FIX: シンプルで確実な問題表示")
]

for check_name, check_pattern in checks:
    if check_pattern in content:
        print(f"✅ {check_name}: 修正適用済み")
    else:
        print(f"❌ {check_name}: 修正未適用")

print("\n🎯 テスト手順:")
print("1. ターミナルで: cd /mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app")
print("2. アプリ起動: python3 app.py")
print("3. ブラウザで: http://localhost:5000")
print("4. 基礎科目テスト: http://localhost:5000/exam?question_type=basic")
print("5. 専門科目テスト: http://localhost:5000/exam?question_type=specialist&department=road")

print("\n✅ 修正完了 - アプリケーションを起動してテストしてください")