#!/usr/bin/env python3
"""
🔍 最終検証テスト - 副作用完全除去確認
専門家推奨：既存機能維持で10/20/30問完走テスト
"""

import subprocess
import time
import requests
import signal
import os
from urllib.parse import urljoin

BASE_URL = "http://localhost:5005/"

def simple_progress_test():
    """シンプルな進捗確認テスト"""
    print("🔍 進捗表示確認テスト - 副作用なし")
    print("=" * 50)
    
    # Start Flask in background
    print("🚀 Flask アプリ起動...")
    os.chdir("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app")
    
    app_process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(4)  # アプリ起動待機
    
    try:
        session = requests.Session()
        
        # Test cases
        test_cases = [
            {"name": "10問", "count": 10, "dept": "基礎科目", "type": "basic"},
            {"name": "20問", "count": 20, "dept": "道路部門", "type": "specialist"},
            {"name": "30問", "count": 30, "dept": "河川・砂防部門", "type": "specialist"}
        ]
        
        results = []
        
        for case in test_cases:
            print(f"\n📋 {case['name']}テスト")
            
            try:
                # 設定
                settings_resp = session.post(f"{BASE_URL}settings", 
                                           data={'questions_per_session': case['count']})
                print(f"  設定: {settings_resp.status_code}")
                
                # セッション開始
                exam_resp = session.post(f"{BASE_URL}exam", 
                                       data={'department': case['dept'], 
                                             'question_type': case['type']})
                
                if exam_resp.status_code == 200:
                    content = exam_resp.text
                elif exam_resp.status_code == 302:
                    redirect = exam_resp.headers.get('Location', '/exam')
                    final_resp = session.get(f"{BASE_URL}{redirect.lstrip('/')}")
                    content = final_resp.text
                else:
                    print(f"  ❌ エラー: {exam_resp.status_code}")
                    results.append(False)
                    continue
                
                # 進捗確認
                expected = f"1/{case['count']}"
                if expected in content:
                    print(f"  ✅ 進捗正常: {expected}")
                    results.append(True)
                elif "1/3" in content:
                    print(f"  ❌ 進捗異常: 1/3")
                    results.append(False)
                else:
                    print(f"  ⚠️ 進捗検出不可")
                    results.append(False)
                    
            except Exception as e:
                print(f"  ❌ 例外: {e}")
                results.append(False)
        
        # 結果
        success = sum(results)
        total = len(results)
        print(f"\n📊 結果: {success}/{total} ({success/total*100:.1f}%)")
        
        if success == total:
            print("✅ 副作用除去成功")
        else:
            print("❌ 副作用除去未完了")
            
    finally:
        # アプリ停止
        try:
            app_process.terminate()
            app_process.wait(timeout=3)
        except:
            app_process.kill()
        print("🛑 Flask アプリ停止")

if __name__ == "__main__":
    simple_progress_test()