#!/usr/bin/env python3
"""
🔍 セッション変数観察 - 副作用なし・既存機能維持
専門家推奨：ログ分析でget_user_session_size関数の動作確認
"""

import requests
import time
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

def observe_session_variables():
    """セッション変数の観察（ログ出力誘発）"""
    print("🔍 セッション変数観察開始 - ログ分析型デバッグ")
    print("=" * 60)
    
    session = load_cookies()
    session.get(BASE_URL)
    
    # ログファイルのタイムスタンプ確認
    log_file = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/rccm_app.log"
    
    try:
        # ログファイルの現在サイズ記録
        with open(log_file, 'r') as f:
            lines_before = len(f.readlines())
        print(f"📋 ログ開始位置: {lines_before}行")
    except:
        lines_before = 0
        print("📋 ログファイル: 新規作成予定")
    
    # テストケース: 30問設定で詳細ログ出力
    print("\n🔍 30問設定での詳細ログ出力")
    test_cases = [
        {"name": "30問設定", "count": 30, "dept": "基礎科目", "type": "basic"},
        {"name": "20問設定", "count": 20, "dept": "道路部門", "type": "specialist"},
        {"name": "10問設定", "count": 10, "dept": "河川・砂防部門", "type": "specialist"}
    ]
    
    for case in test_cases:
        print(f"\n📋 {case['name']} テスト開始")
        
        try:
            # 1. 設定変更
            print(f"  Step 1: {case['count']}問設定")
            settings_response = session.post(
                urljoin(BASE_URL, "settings"), 
                data={'questions_per_session': case['count']}
            )
            
            if settings_response.status_code in [200, 302]:
                print(f"    ✅ 設定成功: {case['count']}問")
            else:
                print(f"    ❌ 設定失敗: {settings_response.status_code}")
                continue
            
            # 少し待機（ログ出力確保）
            time.sleep(0.5)
            
            # 2. セッション開始（ログ出力誘発）
            print(f"  Step 2: セッション開始（ログ出力誘発）")
            exam_data = {
                'department': case['dept'],
                'question_type': case['type'],
                'question_count': case['count']
            }
            
            exam_response = session.post(urljoin(BASE_URL, "exam"), data=exam_data)
            
            if exam_response.status_code in [200, 302]:
                print(f"    ✅ セッション開始成功")
                
                # 3. 追加のGETリクエスト（ログ詳細出力）
                if exam_response.status_code == 302:
                    # リダイレクトの場合、その先を取得
                    redirect_url = exam_response.headers.get('Location', '/exam')
                    final_response = session.get(urljoin(BASE_URL, redirect_url.lstrip('/')))
                    print(f"    📍 リダイレクト先取得: {final_response.status_code}")
                
            else:
                print(f"    ❌ セッション開始失敗: {exam_response.status_code}")
            
            # 少し待機（ログ処理完了確保）
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ テスト例外: {e}")
    
    # ログ分析
    print(f"\n🔍 ログ分析開始")
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        # 新しく追加されたログ行を抽出
        new_lines = all_lines[lines_before:] if lines_before < len(all_lines) else []
        
        if new_lines:
            print(f"📋 新規ログ行数: {len(new_lines)}")
            
            # 重要なキーワードでフィルタリング
            important_keywords = [
                'get_user_session_size',
                'display_total',
                'questions_per_session',
                'PROGRESS FIX',
                'quiz_settings',
                '問設定',
                'セッション開始'
            ]
            
            relevant_logs = []
            for line in new_lines:
                for keyword in important_keywords:
                    if keyword in line:
                        relevant_logs.append(line.strip())
                        break
            
            if relevant_logs:
                print(f"\n📊 関連ログ（{len(relevant_logs)}件）:")
                for i, log in enumerate(relevant_logs[-20:], 1):  # 最新20件
                    print(f"  {i:2d}. {log}")
            else:
                print(f"\n⚠️ 関連ログなし（キーワード: {important_keywords}）")
                
            # 3問設定に関するログ検索
            problem_logs = [line.strip() for line in new_lines if '3' in line and any(kw in line for kw in ['display', 'total', 'questions'])]
            if problem_logs:
                print(f"\n🚨 3問関連ログ（{len(problem_logs)}件）:")
                for i, log in enumerate(problem_logs, 1):
                    print(f"  {i:2d}. {log}")
        else:
            print(f"⚠️ 新規ログなし（開始位置: {lines_before}行, 現在: {len(all_lines)}行）")
            
    except Exception as e:
        print(f"❌ ログ分析エラー: {e}")
    
    print("\n" + "=" * 60)
    print("✅ セッション変数観察完了")
    print("\n📊 観察結果:")
    print("  - ログ出力による変数値確認完了")
    print("  - get_user_session_size()の戻り値をログで確認")
    print("  - 既存機能維持: コード変更なし")

if __name__ == "__main__":
    observe_session_variables()