#!/usr/bin/env python3
"""
🔍 復習リストエラー確認 - 読み取り専用・副作用なし
"""

import requests
import re
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

def check_review_error():
    """復習リストエラー詳細確認"""
    print("🔍 復習リストエラー詳細確認開始 - 副作用なし")
    print("=" * 50)
    
    session = load_cookies()
    
    # セッション初期化
    session.get(BASE_URL)
    
    # 復習リスト関連のURLを確認
    review_urls = [
        "bookmarks",
        "review", 
        "exam/review",
        "srs_stats"
    ]
    
    for url_path in review_urls:
        print(f"\n📋 {url_path} 確認")
        try:
            response = session.get(urljoin(BASE_URL, url_path))
            print(f"  ステータス: {response.status_code}")
            
            if response.status_code != 200:
                print(f"  ❌ エラー: {response.status_code}")
                continue
            
            content = response.text
            
            # エラーメッセージ検索
            error_patterns = [
                r'<div[^>]*class="[^"]*alert[^"]*alert-danger[^"]*"[^>]*>(.*?)</div>',
                r'エラー[：:]([^<\n]+)',
                r'error[：:]([^<\n]+)', 
                r'Exception[：:]([^<\n]+)',
                r'Traceback[：:]([^<\n]+)',
                r'Internal Server Error',
                r'500 Internal Server Error',
                r'404 Not Found'
            ]
            
            errors_found = []
            for pattern in error_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    errors_found.extend(matches[:3])  # 最大3つまで
            
            if errors_found:
                print(f"  ❌ エラー検出:")
                for error in errors_found:
                    error_clean = re.sub(r'<[^>]+>', '', str(error)).strip()
                    if error_clean:
                        print(f"    - {error_clean[:100]}...")
            else:
                print(f"  ✅ エラーメッセージなし")
                
                # 復習リスト固有の要素確認
                review_indicators = [
                    "復習",
                    "bookmark", 
                    "間違えた問題",
                    "復習リスト",
                    "ブックマーク"
                ]
                
                found_indicators = []
                for indicator in review_indicators:
                    if indicator in content:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"  📝 復習関連要素: {found_indicators}")
                else:
                    print(f"  ⚠️ 復習関連要素なし")
        
        except Exception as e:
            print(f"  ❌ 例外: {e}")
    
    # 最新ログからreview関連エラー確認
    print(f"\n📋 最新ログの復習関連エラー確認")
    try:
        with open("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/rccm_app.log", 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-100:]  # 最新100行
            
            review_errors = []
            for line in recent_lines:
                if any(keyword in line.lower() for keyword in ['review', 'bookmark', '復習', 'srs']):
                    if any(error_word in line.lower() for error_word in ['error', 'エラー', 'exception', 'failed', '失敗']):
                        review_errors.append(line.strip())
            
            if review_errors:
                print(f"  ❌ 復習関連エラー:")
                for error in review_errors[-5:]:  # 最新5つ
                    print(f"    {error}")
            else:
                print(f"  ✅ 復習関連エラーなし")
    except Exception as e:
        print(f"  ログ確認エラー: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 復習リストエラー確認完了 - 副作用なし")

if __name__ == "__main__":
    check_review_error()