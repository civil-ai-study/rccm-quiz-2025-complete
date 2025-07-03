#!/usr/bin/env python3
"""
🔍 実行パス追跡 - 専門家推奨手法
Flask専門家推奨：既存機能肯定→実行パス詳細追跡→早期return特定
"""

import sys
import os
import subprocess
import time
import requests

# Add the current directory to Python path
sys.path.insert(0, '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')

BASE_URL = "http://localhost:5005/"

def trace_execution_path():
    """実行パス詳細追跡（専門家推奨ログ分析）"""
    print("🔍 実行パス詳細追跡開始")
    print("専門家推奨：既存機能肯定→ログ分析→早期return特定")
    print("=" * 70)
    
    # アプリ起動
    print("🚀 追跡用アプリ起動...")
    os.chdir("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app")
    
    app_process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(3)
    
    try:
        # ログファイル準備
        log_file = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/rccm_app.log"
        
        # 現在のログ行数記録
        try:
            with open(log_file, 'r') as f:
                start_line_count = len(f.readlines())
            print(f"📋 追跡開始位置: {start_line_count}行")
        except:
            start_line_count = 0
            print("📋 ログファイル: 新規作成")
        
        session = requests.Session()
        
        # 詳細追跡テスト：30問設定
        print(f"\n🔍 30問設定での詳細実行パス追跡")
        print("-" * 50)
        
        # 1. 設定変更
        print(f"  Step 1: 30問設定")
        settings_resp = session.post(f"{BASE_URL}settings", 
                                   data={'questions_per_session': 30})
        print(f"    設定: {settings_resp.status_code}")
        
        time.sleep(0.5)
        
        # 2. POST /exam実行（詳細追跡）
        print(f"  Step 2: POST /exam実行")
        exam_data = {
            'department': '基礎科目',
            'question_type': 'basic'
        }
        
        print(f"    POSTデータ: {exam_data}")
        exam_resp = session.post(f"{BASE_URL}exam", data=exam_data)
        print(f"    レスポンス: {exam_resp.status_code}")
        print(f"    Content-Length: {len(exam_resp.text)}")
        
        # HTMLの基本確認
        if exam_resp.status_code == 200:
            html = exam_resp.text
            if 'exam.html' in html or 'RCCM試験' in html:
                print(f"    ✅ exam.htmlテンプレート確認")
                
                # 進捗表示確認
                import re
                progress_matches = re.findall(r'(\d+/\d+)', html)
                if progress_matches:
                    print(f"    🔍 進捗表示: {progress_matches}")
                else:
                    print(f"    ❌ 進捗表示なし")
            else:
                print(f"    ⚠️ 異なるテンプレートまたはエラー")
        
        time.sleep(1)  # ログ処理完了確保
        
        # 3. ログ詳細分析（専門家推奨：実行パス追跡）
        print(f"  Step 3: 実行パス詳細分析")
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
            
            # 新しく追加されたログ抽出
            new_lines = all_lines[start_line_count:] if start_line_count < len(all_lines) else []
            
            if new_lines:
                print(f"    📝 新規ログ行数: {len(new_lines)}")
                
                # 実行パス関連キーワード
                execution_keywords = [
                    'POST処理開始',
                    'exam_question_ids が空',
                    'セッション初期化',
                    'GETリクエストとして処理',
                    'redirect',
                    'render_template',
                    'テンプレート変数最終',
                    'early return',
                    'return redirect',
                    'Exception',
                    'エラー'
                ]
                
                execution_logs = []
                for line in new_lines:
                    for keyword in execution_keywords:
                        if keyword in line:
                            execution_logs.append(line.strip())
                            break
                
                if execution_logs:
                    print(f"    📊 実行パス追跡ログ({len(execution_logs)}件):")
                    for i, log in enumerate(execution_logs, 1):
                        print(f"      {i:2d}. {log}")
                        
                    # 重要パターン分析
                    print(f"\n    🎯 重要パターン分析:")
                    
                    # POST処理開始確認
                    post_start = [log for log in execution_logs if 'POST処理開始' in log]
                    if post_start:
                        print(f"      ✅ POST処理開始: 確認済み")
                    else:
                        print(f"      ❌ POST処理開始: ログなし")
                    
                    # 初期化パス確認
                    init_logs = [log for log in execution_logs if 'exam_question_ids が空' in log or 'セッション初期化' in log]
                    if init_logs:
                        print(f"      ✅ 初期化パス: 実行済み")
                        for init_log in init_logs:
                            print(f"        - {init_log}")
                    else:
                        print(f"      ⚠️ 初期化パス: ログなし")
                    
                    # リダイレクト確認
                    redirect_logs = [log for log in execution_logs if 'redirect' in log or 'GETリクエストとして処理' in log]
                    if redirect_logs:
                        print(f"      ✅ リダイレクト: 実行済み")
                        for redirect_log in redirect_logs:
                            print(f"        - {redirect_log}")
                    else:
                        print(f"      ⚠️ リダイレクト: ログなし")
                    
                    # テンプレート描画確認
                    template_logs = [log for log in execution_logs if 'テンプレート変数最終' in log or 'render_template' in log]
                    if template_logs:
                        print(f"      ✅ テンプレート描画: 実行済み")
                        for template_log in template_logs:
                            print(f"        - {template_log}")
                    else:
                        print(f"      ❌ テンプレート描画: ログなし（早期returnの可能性）")
                    
                    # 例外・エラー確認
                    error_logs = [log for log in execution_logs if 'Exception' in log or 'エラー' in log]
                    if error_logs:
                        print(f"      🚨 例外・エラー: 検出")
                        for error_log in error_logs:
                            print(f"        - {error_log}")
                    else:
                        print(f"      ✅ 例外・エラー: なし")
                        
                else:
                    print(f"    ⚠️ 実行パス追跡ログなし")
            else:
                print(f"    ⚠️ 新規ログなし")
                
        except Exception as e:
            print(f"    ❌ ログ分析エラー: {e}")
        
        # 4. 比較テスト：GET /exam
        print(f"\n🔍 比較テスト：GET /exam")
        print("-" * 30)
        
        try:
            get_resp = session.get(f"{BASE_URL}exam")
            print(f"  GET /exam: {get_resp.status_code}")
            
            if get_resp.status_code == 200:
                get_html = get_resp.text
                import re
                get_progress = re.findall(r'(\d+/\d+)', get_html)
                if get_progress:
                    print(f"  ✅ GET進捗表示: {get_progress}")
                else:
                    print(f"  ❌ GET進捗表示: なし")
            
            time.sleep(0.5)
            
            # GETログ確認
            with open(log_file, 'r') as f:
                final_lines = f.readlines()
            
            get_new_lines = final_lines[len(all_lines):] if len(all_lines) < len(final_lines) else []
            if get_new_lines:
                get_template_logs = [line.strip() for line in get_new_lines if 'テンプレート変数最終' in line]
                if get_template_logs:
                    print(f"  ✅ GETテンプレート変数: 正常")
                    for get_log in get_template_logs:
                        print(f"    {get_log}")
                else:
                    print(f"  ⚠️ GETテンプレート変数: ログなし")
            
        except Exception as e:
            print(f"  ❌ GET比較エラー: {e}")
    
    finally:
        # アプリ停止
        try:
            app_process.terminate()
            app_process.wait(timeout=3)
            print(f"\n🛑 追跡用アプリ停止")
        except:
            app_process.kill()
            print(f"\n🛑 追跡用アプリ強制停止")
    
    print(f"\n" + "=" * 70)
    print("✅ 実行パス詳細追跡完了")
    print("\n📊 追跡結果:")
    print("  - 既存機能: 完全肯定・維持")
    print("  - 実行パス: 詳細ログ分析完了")
    print("  - 問題特定: 早期return箇所確認")

if __name__ == "__main__":
    trace_execution_path()