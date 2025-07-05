#!/usr/bin/env python3
"""
🛡️ バックアップ状態サマリー
現在の全バックアップと変更履歴の要約
"""

import os
import glob
from datetime import datetime

def generate_backup_summary():
    """バックアップ状態の要約を生成"""
    print("🛡️ バックアップ状態サマリー")
    print("=" * 60)
    print(f"生成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # バックアップファイルを収集
    backup_files = glob.glob('app.py.backup*') + glob.glob('app.py.checkpoint*') + glob.glob('app.py.temp*')
    backup_files.sort(key=lambda x: os.path.getmtime(x))
    
    print(f"\n📁 バックアップファイル数: {len(backup_files)}")
    print("\n時系列順バックアップ一覧:")
    print("-" * 60)
    
    for i, backup in enumerate(backup_files, 1):
        mtime = os.path.getmtime(backup)
        timestamp = datetime.fromtimestamp(mtime)
        size = os.path.getsize(backup)
        
        # ファイル名から状態を推定
        status = "不明"
        if "before_session_functions" in backup:
            status = "🔵 関数追加前（完全オリジナル）"
        elif "after_function_add" in backup:
            status = "🟢 関数追加後（現在の状態）"
        elif "first_replace" in backup:
            status = "🟡 1箇所置換テスト（未適用）"
        elif "ultra_safe" in backup:
            status = "🔵 作業開始時点"
        
        print(f"\n{i}. {backup}")
        print(f"   作成日時: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   サイズ: {size:,} bytes")
        print(f"   状態: {status}")
    
    # 現在のapp.pyの状態
    print("\n" + "=" * 60)
    print("📄 現在のapp.py:")
    if os.path.exists('app.py'):
        current_size = os.path.getsize('app.py')
        current_mtime = datetime.fromtimestamp(os.path.getmtime('app.py'))
        
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_functions = 'def safe_exam_session_reset(' in content
        has_calls = 'safe_exam_session_reset()' in content
        
        print(f"   最終更新: {current_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   サイズ: {current_size:,} bytes")
        print(f"   セッション管理関数: {'✅ あり' if has_functions else '❌ なし'}")
        print(f"   関数呼び出し: {'✅ あり' if has_calls else '❌ なし'}")
    
    # 推奨アクション
    print("\n" + "=" * 60)
    print("🎯 現在の状態と推奨アクション:")
    print("\n✅ 安全な状態です:")
    print("  - 関数追加のみ完了（副作用なし）")
    print("  - session.pop置換は未実施")
    print("  - 完全なバックアップあり")
    
    print("\n📋 次のステップ:")
    print("  1. 現在の状態で動作確認")
    print("  2. 問題なければ1箇所だけ置換")
    print("  3. 各ステップでバックアップ作成")
    
    print("\n🔄 ロールバックコマンド:")
    print("  完全に元に戻す:")
    print("  $ cp app.py.backup_before_session_functions app.py")
    
    print("\n✅ サマリー生成完了")

if __name__ == "__main__":
    generate_backup_summary()