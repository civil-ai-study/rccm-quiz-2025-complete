#!/usr/bin/env python3
"""
🔍 シンプルHTML確認 - 専門家推奨観察手法
既存機能肯定→HTML内容直接確認→問題の正確な特定
"""

import subprocess
import time
import requests
import re
import os

BASE_URL = "http://localhost:5005/"

def simple_html_check():
    """シンプルHTML内容確認"""
    print("🔍 シンプルHTML内容確認開始")
    print("=" * 50)
    
    # アプリ起動
    os.chdir("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app")
    app_process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(3)
    
    try:
        session = requests.Session()
        
        # 30問設定でテスト
        print("\n📋 30問設定テスト")
        
        # 設定
        settings_resp = session.post(f"{BASE_URL}settings", 
                                   data={'questions_per_session': 30})
        print(f"設定: {settings_resp.status_code}")
        
        # 試験開始
        exam_resp = session.post(f"{BASE_URL}exam", 
                               data={'department': '基礎科目', 'question_type': 'basic'})
        print(f"試験: {exam_resp.status_code}")
        
        if exam_resp.status_code == 200:
            html = exam_resp.text
            
            # 進捗表示検索
            print(f"\n📊 HTML進捗検索:")
            
            # パターン1: badge要素
            badge_pattern = r'<span[^>]*class="[^"]*badge[^"]*bg-primary[^"]*"[^>]*>([^<]*)</span>'
            badge_matches = re.findall(badge_pattern, html)
            print(f"  Badge要素: {badge_matches}")
            
            # パターン2: 数値パターン
            number_pattern = r'(\d+/\d+)'
            number_matches = re.findall(number_pattern, html)
            print(f"  数値パターン: {number_matches}")
            
            # パターン3: 変数検索
            if 'current_no' in html:
                print(f"  current_no: 存在")
            else:
                print(f"  current_no: なし")
                
            if 'total_questions' in html:
                print(f"  total_questions: 存在") 
            else:
                print(f"  total_questions: なし")
            
            # 期待値確認
            if "1/30" in html:
                print(f"  ✅ 期待値発見: 1/30")
            elif "1/3" in html:
                print(f"  ❌ 異常値発見: 1/3") 
            else:
                print(f"  ⚠️ 進捗表示なし")
                
            # HTMLサンプル出力（進捗部分）
            print(f"\n📝 HTML進捗部分抜粋:")
            lines = html.split('\n')
            for i, line in enumerate(lines):
                if 'badge' in line and 'bg-primary' in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        print(f"  {marker}{lines[j].strip()}")
                    break
            else:
                print(f"  進捗badge要素が見つかりません")
        
        print(f"\n✅ HTML確認完了")
        
    finally:
        # アプリ停止
        app_process.terminate()
        try:
            app_process.wait(timeout=3)
        except:
            app_process.kill()
        print(f"🛑 アプリ停止")

if __name__ == "__main__":
    simple_html_check()