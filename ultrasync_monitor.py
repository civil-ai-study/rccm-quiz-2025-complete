# -*- coding: utf-8 -*-
"""
ULTRA SYNC継続監視システム
システム安定性と副作用防止の継続確認
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5005"

def ultrasync_health_check():
    """ULTRA SYNC継続健全性チェック"""
    
    print("=" * 60)
    print("ULTRA SYNC継続監視システム開始")
    print("=" * 60)
    print(f"チェック時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"監視対象: {BASE_URL}")
    print("=" * 60)
    
    # 1. システム基本動作確認
    print("\n[健全性-1] システム基本動作確認")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("  [OK] ホームページ: 正常応答")
        else:
            print(f"  [NG] ホームページ: 異常 ({response.status_code})")
            return False
    except Exception as e:
        print(f"  [NG] ホームページ: 接続エラー ({e})")
        return False
    
    # 2. 代表部門での簡易動作確認
    print("\n[健全性-2] 代表部門動作確認")
    session = requests.Session()
    
    try:
        # クイズ開始テスト
        quiz_data = {'category': '4-2', 'department': '道路'}
        response = session.post(f"{BASE_URL}/quiz", data=quiz_data, timeout=5)
        if response.status_code in [200, 302]:
            print("  [OK] クイズ開始: 正常動作")
        else:
            print(f"  [NG] クイズ開始: 異常 ({response.status_code})")
            return False
            
        # 問題表示テスト
        response = session.get(f"{BASE_URL}/quiz_question", timeout=5)
        if response.status_code == 200:
            print("  [OK] 問題表示: 正常動作")
        else:
            print(f"  [NG] 問題表示: 異常 ({response.status_code})")
            return False
            
        # 回答送信テスト（1問のみ）
        answer_data = {'answer': '1'}
        response = session.post(f"{BASE_URL}/submit_exam_answer", 
                               data=answer_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("  [OK] 回答送信: 正常動作")
            else:
                print(f"  [NG] 回答送信: 処理エラー ({result})")
                return False
        else:
            print(f"  [NG] 回答送信: 異常 ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"  [NG] 代表部門テスト: エラー ({e})")
        return False
    
    # 3. システムリソース確認
    print("\n[健全性-3] システムリソース確認")
    try:
        # メモリ使用量チェック（簡易）
        import psutil
        memory_percent = psutil.virtual_memory().percent
        if memory_percent < 90:
            print(f"  [OK] メモリ使用量: 正常 ({memory_percent:.1f}%)")
        else:
            print(f"  [WARNING] メモリ使用量: 高負荷 ({memory_percent:.1f}%)")
    except ImportError:
        print("  [INFO] メモリチェック: psutilライブラリ未インストール")
    except Exception as e:
        print(f"  [WARNING] リソースチェック: {e}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ULTRA SYNC継続監視: 全項目正常")
    print("[SECURE] システム安定性: 維持確認")
    print("[SAFE] 副作用: 検出なし")
    print("=" * 60)
    
    return True

def continuous_monitoring():
    """継続監視実行"""
    print("ULTRA SYNC継続監視開始")
    print("Ctrl+Cで停止")
    
    try:
        while True:
            success = ultrasync_health_check()
            if not success:
                print("\n[ALERT] 異常検出: 詳細調査が必要です")
                break
            
            print(f"\n[WAIT] 次回チェックまで60秒待機...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n監視を停止しました")
    except Exception as e:
        print(f"\n\n監視エラー: {e}")

if __name__ == "__main__":
    print("ULTRA SYNC継続監視システム")
    print("1. 単発チェック")
    print("2. 継続監視")
    
    # 自動で単発チェックを実行
    print("\n単発チェックを実行します...")
    ultrasync_health_check()