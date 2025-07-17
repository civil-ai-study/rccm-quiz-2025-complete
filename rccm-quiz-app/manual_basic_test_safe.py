#!/usr/bin/env python3
"""
🛡️ ULTRA SYNC 基礎科目手動テスト（副作用ゼロ保証版）
CLAUDE.md準拠の安全なテスト実行
"""

import sys
import os

# 🛡️ 安全なパス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 🛡️ 基本機能のインポートテスト
    print("🔍 ULTRA SYNC: モジュール読み込みテスト開始")
    
    from app import app, load_questions
    from config import RCCMConfig
    import utils
    
    print("✅ 基本モジュール読み込み成功")
    
    # 🛡️ データ読み込みテスト
    print("🔍 ULTRA SYNC: データ読み込みテスト開始")
    
    questions = load_questions()
    print(f"✅ 問題データ読み込み成功: {len(questions)}問")
    
    # 🛡️ 基礎科目データ確認
    basic_questions = [q for q in questions if q.get('question_type') == 'basic']
    print(f"✅ 基礎科目データ確認: {len(basic_questions)}問")
    
    if len(basic_questions) >= 10:
        print("✅ 基礎科目10問テスト可能")
        
        # 最初の10問を確認
        for i in range(min(10, len(basic_questions))):
            q = basic_questions[i]
            print(f"  問題{i+1}: ID={q.get('id')}, カテゴリ={q.get('category')}")
    else:
        print(f"⚠️ 基礎科目データ不足: {len(basic_questions)}問のみ")
    
    # 🛡️ 専門科目データ確認
    specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
    print(f"✅ 専門科目データ確認: {len(specialist_questions)}問")
    
    # カテゴリ別集計
    categories = {}
    for q in specialist_questions:
        cat = q.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("✅ 専門科目カテゴリ別問題数:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}問")
    
    print("\n🛡️ ULTRA SYNC: 基本データ読み込みテスト完了")
    print("✅ 副作用なし: 読み込みテストのみ実行")
    
except Exception as e:
    print(f"❌ テストエラー: {e}")
    import traceback
    print(f"詳細: {traceback.format_exc()}")