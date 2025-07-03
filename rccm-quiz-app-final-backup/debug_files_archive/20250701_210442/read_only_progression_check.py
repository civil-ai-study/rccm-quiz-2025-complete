#!/usr/bin/env python3
"""
🔍 読み取り専用 - 進捗表示の実際の動作確認
絶対に副作用を起こしません - 観察のみ
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

def check_progression_display():
    """進捗表示の実際の動作確認 - 読み取り専用"""
    print("🔍 進捗表示動作確認開始 - 副作用なし・読み取り専用")
    print("=" * 60)
    
    session = load_cookies()
    
    # セッション初期化（読み取り専用操作）
    session.get(BASE_URL)
    session.get(urljoin(BASE_URL, "departments"))
    
    # 現在の設定画面の内容を確認
    print("1️⃣ 設定画面の詳細確認")
    try:
        settings_response = session.get(urljoin(BASE_URL, "settings"))
        if settings_response.status_code == 200:
            settings_content = settings_response.text
            
            # selectボックスの詳細分析
            select_match = re.search(r'<select[^>]*name="questions_per_session"[^>]*>(.*?)</select>', settings_content, re.DOTALL)
            if select_match:
                select_content = select_match.group(1)
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', select_content)
                print(f"   利用可能な問題数設定:")
                for value, text in options:
                    selected = "selected" in select_content
                    print(f"     {value}問 - {text.strip()} {'(選択中)' if selected else ''}")
            
            # 現在選択されている値を確認
            selected_match = re.search(r'value="(\d+)"[^>]*selected', settings_content)
            if selected_match:
                current_setting = selected_match.group(1)
                print(f"   現在選択: {current_setting}問")
            else:
                print(f"   現在選択: 検出されず")
        else:
            print(f"   設定画面エラー: {settings_response.status_code}")
    except Exception as e:
        print(f"   設定画面例外: {e}")
    
    # 複数の部門で試験画面確認
    test_departments = [
        {"name": "基礎", "type": "4-1", "year": "2019"},
        {"name": "道路", "type": "4-2", "year": "2019"},
        {"name": "河川、砂防及び海岸・海洋", "type": "4-2", "year": "2019"}
    ]
    
    print("\n2️⃣ 各部門での試験画面確認")
    for dept in test_departments:
        print(f"\n   📝 {dept['name']}部門 ({dept['type']}) 確認")
        try:
            # 試験画面アクセス
            exam_url = f"{BASE_URL}exam?department={dept['name']}&question_type={dept['type']}&year={dept['year']}"
            exam_response = session.get(exam_url)
            
            if exam_response.status_code == 200:
                exam_content = exam_response.text
                
                # 進捗表示の詳細分析
                progress_patterns = [
                    r'aria-label="進捗">([^<]+)</span>',
                    r'class="badge[^"]*"[^>]*>([^<]*\d+/\d+[^<]*)</[^>]*>',
                    r'>(\d+/\d+)<',
                    r'進捗[：:]\s*(\d+/\d+)'
                ]
                
                progress_found = False
                for i, pattern in enumerate(progress_patterns):
                    matches = re.findall(pattern, exam_content)
                    if matches:
                        print(f"     パターン{i+1}で進捗検出: {matches}")
                        progress_found = True
                
                if not progress_found:
                    print(f"     ❌ 進捗表示が見つかりません")
                    
                    # HTMLの一部を確認（デバッグ用）
                    badge_matches = re.findall(r'<span[^>]*badge[^>]*>([^<]+)</span>', exam_content)
                    if badge_matches:
                        print(f"     バッジ要素: {badge_matches}")
                
                # 問題IDとカテゴリ確認
                qid_match = re.search(r'name="qid" value="([^"]+)"', exam_content)
                if qid_match:
                    print(f"     問題ID: {qid_match.group(1)}")
                
                # 問題内容の部門確認
                dept_indicators = [dept['name'], "基礎", "共通", "道路", "河川", "トンネル", "都市計画"]
                found_indicators = []
                for indicator in dept_indicators:
                    if indicator in exam_content:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"     内容に含まれる部門キーワード: {found_indicators}")
                
            else:
                print(f"     ❌ アクセス失敗: {exam_response.status_code}")
                
        except Exception as e:
            print(f"     例外: {e}")
    
    # セッションデバッグ情報確認
    print("\n3️⃣ セッションデバッグ情報確認")
    try:
        debug_response = session.get(urljoin(BASE_URL, "debug_session"))
        if debug_response.status_code == 200:
            debug_content = debug_response.text
            
            # セッション情報の抽出
            session_patterns = [
                r'quiz_settings[\'"]?\s*[:=]\s*([^,\}]+)',
                r'questions_per_session[\'"]?\s*[:=]\s*(\d+)',
                r'exam_question_ids[\'"]?\s*[:=]\s*\[([^\]]*)\]',
                r'total_questions[\'"]?\s*[:=]\s*(\d+)'
            ]
            
            for pattern in session_patterns:
                matches = re.findall(pattern, debug_content)
                if matches:
                    print(f"   {pattern[:20]}...: {matches}")
        else:
            print(f"   デバッグセッション: アクセス不可 ({debug_response.status_code})")
    except Exception as e:
        print(f"   デバッグセッション例外: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 進捗表示確認完了 - 副作用なし")

if __name__ == "__main__":
    check_progression_display()