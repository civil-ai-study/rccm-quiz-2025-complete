#!/usr/bin/env python3
"""
🔍 ルート実行観察 - 専門家推奨手法
Flask専門家推奨：既存機能肯定→実際の実行ルート確認→問題特定
"""

import subprocess
import time
import requests
import os

BASE_URL = "http://localhost:5005/"

def observe_route_execution():
    """実際のルート実行観察"""
    print("🔍 ルート実行観察開始")
    print("専門家推奨：既存機能肯定→実行ルート確認→問題特定")
    print("=" * 70)
    
    # アプリ起動
    print("🚀 観察用アプリ起動...")
    os.chdir("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app")
    
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
            print(f"📋 ログ開始位置: {start_line_count}行")
        except:
            start_line_count = 0
            print("📋 ログファイル: 新規作成")
        
        session = requests.Session()
        
        # テストケース：30問設定で詳細追跡
        print(f"\n🔍 30問設定での詳細ルート追跡")
        print("-" * 50)
        
        # 1. 設定変更
        print(f"  Step 1: 30問設定")
        settings_resp = session.post(f"{BASE_URL}settings", 
                                   data={'questions_per_session': 30})
        print(f"    設定レスポンス: {settings_resp.status_code}")
        
        time.sleep(0.5)  # ログ出力確保
        
        # 2. 試験開始（詳細追跡）
        print(f"  Step 2: 試験開始（ルート追跡）")
        exam_data = {
            'department': '基礎科目',
            'question_type': 'basic'
        }
        
        print(f"    POSTデータ: {exam_data}")
        exam_resp = session.post(f"{BASE_URL}exam", data=exam_data)
        print(f"    レスポンス: {exam_resp.status_code}")
        print(f"    Content-Type: {exam_resp.headers.get('Content-Type', 'N/A')}")
        print(f"    Content-Length: {len(exam_resp.text)}")
        
        if exam_resp.status_code == 302:
            redirect_url = exam_resp.headers.get('Location', '')
            print(f"    リダイレクト先: {redirect_url}")
        
        time.sleep(1)  # ログ処理完了確保
        
        # 3. ログ分析：実際の実行ルート確認
        print(f"  Step 3: 実行ルート分析")
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
            
            # 新しく追加されたログ抽出
            new_lines = all_lines[start_line_count:] if start_line_count < len(all_lines) else []
            
            if new_lines:
                print(f"    📝 新規ログ行数: {len(new_lines)}")
                
                # ルート実行関連ログ検索
                route_keywords = [
                    'POST /exam',
                    'GET /exam', 
                    'テンプレート変数最終',
                    'render_template',
                    'exam.html',
                    '=== PROGRESS FIX',
                    'display_current',
                    'display_total'
                ]
                
                route_logs = []
                for line in new_lines:
                    for keyword in route_keywords:
                        if keyword in line:
                            route_logs.append(line.strip())
                            break
                
                if route_logs:
                    print(f"    📊 ルート実行ログ({len(route_logs)}件):")
                    for i, log in enumerate(route_logs[-20:], 1):  # 最新20件
                        print(f"      {i:2d}. {log}")
                        
                    # 特に重要：テンプレート変数最終ログ
                    template_logs = [log for log in route_logs if 'テンプレート変数最終' in log]
                    if template_logs:
                        print(f"\n    🎯 テンプレート変数最終ログ:")
                        for template_log in template_logs:
                            print(f"      {template_log}")
                    else:
                        print(f"\n    ⚠️ テンプレート変数最終ログなし - 別ルート実行の可能性")
                        
                    # POST/GET ルート確認
                    method_logs = [log for log in route_logs if '/exam' in log and ('POST' in log or 'GET' in log)]
                    if method_logs:
                        print(f"\n    📍 実行されたルート:")
                        for method_log in method_logs:
                            print(f"      {method_log}")
                else:
                    print(f"    ⚠️ ルート実行ログなし")
            else:
                print(f"    ⚠️ 新規ログなし")
                
        except Exception as e:
            print(f"    ❌ ログ分析エラー: {e}")
        
        # 4. 追加テスト：GETルート直接確認
        print(f"\n🔍 GETルート直接確認")
        print("-" * 30)
        
        try:
            # /exam に直接GETアクセス
            get_resp = session.get(f"{BASE_URL}exam")
            print(f"  GET /exam: {get_resp.status_code}")
            print(f"  Content-Length: {len(get_resp.text)}")
            
            if get_resp.status_code == 200:
                # HTMLに進捗があるか確認
                if 'badge' in get_resp.text and 'bg-primary' in get_resp.text:
                    print(f"  ✅ Badge要素存在")
                    
                    # 実際のHTML抜粋
                    import re
                    badge_pattern = r'<span[^>]*class="[^"]*badge[^"]*bg-primary[^"]*"[^>]*>([^<]*)</span>'
                    badge_matches = re.findall(badge_pattern, get_resp.text)
                    if badge_matches:
                        print(f"  🔍 Badge内容: {badge_matches}")
                    else:
                        print(f"  ⚠️ Badge要素はあるが内容なし")
                else:
                    print(f"  ❌ Badge要素なし")
            
            time.sleep(0.5)
            
            # ログ確認
            with open(log_file, 'r') as f:
                final_lines = f.readlines()
            
            final_new_lines = final_lines[len(all_lines):] if len(all_lines) < len(final_lines) else []
            if final_new_lines:
                get_logs = []
                for line in final_new_lines:
                    if any(kw in line for kw in ['GET /exam', 'テンプレート変数最終', 'display_current']):
                        get_logs.append(line.strip())
                
                if get_logs:
                    print(f"  📊 GETルートログ:")
                    for get_log in get_logs:
                        print(f"    {get_log}")
                else:
                    print(f"  ⚠️ GETルートログなし")
            
        except Exception as e:
            print(f"  ❌ GET確認エラー: {e}")
    
    finally:
        # アプリ停止
        try:
            app_process.terminate()
            app_process.wait(timeout=3)
            print(f"\n🛑 観察用アプリ停止")
        except:
            app_process.kill()
            print(f"\n🛑 観察用アプリ強制停止")
    
    print(f"\n" + "=" * 70)
    print("✅ ルート実行観察完了")
    print("\n📊 観察結果:")
    print("  - 既存機能: 完全肯定・維持")
    print("  - 実行ルート: ログ分析による精密確認")
    print("  - 問題特定: 実際の実行パス確認")

if __name__ == "__main__":
    observe_route_execution()