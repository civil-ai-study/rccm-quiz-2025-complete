#!/usr/bin/env python3
"""
🔍 読み取り専用 - 現状確認スクリプト
絶対に副作用を起こしません - 観察のみ実行
"""

import requests
import re
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:5005/"
COOKIE_FILE = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/cookies.txt"

def load_cookies():
    """セッションクッキー読み込み"""
    session = requests.Session()
    try:
        with open(COOKIE_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('#HttpOnly_localhost') and 'rccm_session' in line:
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        cookie_value = parts[6]
                        session.cookies.set('rccm_session', cookie_value)
                        return session
    except Exception:
        pass
    return session

def check_current_status():
    """現状確認 - 読み取り専用"""
    print("🔍 現状確認開始 - 副作用なし・読み取り専用")
    print("=" * 50)
    
    session = load_cookies()
    
    # 1. サーバー接続確認
    try:
        home_response = session.get(BASE_URL, timeout=5)
        print(f"✅ サーバー接続: {home_response.status_code}")
    except Exception as e:
        print(f"❌ サーバー接続失敗: {e}")
        return
    
    # 2. 設定画面の現在値確認
    print("\n📋 設定画面の現在値確認")
    try:
        settings_response = session.get(urljoin(BASE_URL, "settings"))
        if settings_response.status_code == 200:
            settings_content = settings_response.text
            
            # 現在の問題数設定を確認
            select_patterns = [
                r'<select[^>]*name="questions_per_session"[^>]*>.*?</select>',
                r'value="(\d+)"[^>]*selected',
                r'questions_per_session["\']?\s*[:=]\s*["\']?(\d+)'
            ]
            
            for pattern in select_patterns:
                matches = re.findall(pattern, settings_content, re.DOTALL | re.IGNORECASE)
                if matches:
                    print(f"   設定画面パターン {pattern[:20]}...: {matches}")
        else:
            print(f"   設定画面アクセス失敗: {settings_response.status_code}")
    except Exception as e:
        print(f"   設定画面エラー: {e}")
    
    # 3. 部門画面確認
    print("\n🏛️ 部門画面確認")
    try:
        dept_response = session.get(urljoin(BASE_URL, "departments"))
        if dept_response.status_code == 200:
            print(f"   部門画面: 正常アクセス可能")
            
            # 利用可能な部門確認
            dept_content = dept_response.text
            departments = re.findall(r'department["\']?\s*[:=]\s*["\']([^"\']+)', dept_content)
            if departments:
                print(f"   検出された部門: {departments[:5]}...")  # 最初の5つのみ表示
        else:
            print(f"   部門画面アクセス失敗: {dept_response.status_code}")
    except Exception as e:
        print(f"   部門画面エラー: {e}")
    
    # 4. 試験画面の現在の動作確認（読み取り専用）
    print("\n📝 試験画面の現在動作確認")
    try:
        # 基礎科目での確認
        exam_response = session.get(urljoin(BASE_URL, "exam?department=基礎&question_type=4-1&year=2019"))
        if exam_response.status_code == 200:
            exam_content = exam_response.text
            
            # 進捗表示確認
            progress_match = re.search(r'aria-label="進捗">([^<]+)</span>', exam_content)
            if progress_match:
                current_progress = progress_match.group(1).strip()
                print(f"   現在の進捗表示: {current_progress}")
            else:
                print(f"   進捗表示: 検出されず")
            
            # 問題ID確認
            qid_match = re.search(r'name="qid" value="([^"]+)"', exam_content)
            if qid_match:
                current_qid = qid_match.group(1)
                print(f"   現在の問題ID: {current_qid}")
            
            # 問題カテゴリ確認
            category_indicators = ["基礎", "共通", "道路", "河川", "トンネル"]
            detected_categories = []
            for indicator in category_indicators:
                if indicator in exam_content:
                    detected_categories.append(indicator)
            
            if detected_categories:
                print(f"   検出されたカテゴリ: {detected_categories}")
            else:
                print(f"   カテゴリ: 検出されず")
        else:
            print(f"   試験画面アクセス失敗: {exam_response.status_code}")
    except Exception as e:
        print(f"   試験画面エラー: {e}")
    
    # 5. ログファイルの最新エラー確認
    print("\n📋 最新ログ確認")
    try:
        with open("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/rccm_app.log", 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-10:]  # 最新10行
            
            error_lines = []
            for line in recent_lines:
                if any(keyword in line.lower() for keyword in ['error', 'エラー', 'failed', '失敗', 'warning', '警告']):
                    error_lines.append(line.strip())
            
            if error_lines:
                print("   最新のエラー/警告:")
                for error_line in error_lines[-3:]:  # 最新3つのみ
                    print(f"     {error_line}")
            else:
                print("   最新ログにエラー/警告なし")
    except Exception as e:
        print(f"   ログ確認エラー: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 現状確認完了 - 副作用なし")
    print("📋 報告: 上記情報は現在のシステム状態の読み取り結果です")

if __name__ == "__main__":
    check_current_status()