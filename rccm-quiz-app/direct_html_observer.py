#!/usr/bin/env python3
"""
🔍 直接HTML観察デバッグ - 専門家推奨最終手法
既存機能肯定→直接HTML内容確認→問題箇所完全特定
"""

import subprocess
import time
import requests
import re
import os

BASE_URL = "http://localhost:5005/"

def start_observation_app():
    """観察専用アプリ起動"""
    print("🚀 観察専用アプリ起動...")
    
    os.chdir("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app")
    
    process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(3)
    return process

def extract_progress_from_html(html_content):
    """HTML から進捗表示を抽出"""
    # 複数のパターンで検索
    patterns = [
        r'<span[^>]*class="[^"]*badge[^"]*bg-primary[^"]*"[^>]*>([^<]*)</span>',  # badge要素
        r'>(\d+/\d+)<',  # 単純な数値パターン
        r'current_no["\']?\s*:\s*(\d+)',  # JavaScript変数
        r'total_questions["\']?\s*:\s*(\d+)',  # JavaScript変数
    ]
    
    found_data = {}
    
    for i, pattern in enumerate(patterns):
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            found_data[f'pattern_{i+1}'] = matches
    
    return found_data

def direct_html_observation():
    """直接HTML観察による問題特定"""
    print("🔍 直接HTML観察デバッグ開始")
    print("専門家推奨：既存機能肯定→HTML直接確認→完全特定")
    print("=" * 70)
    
    app_process = start_observation_app()
    
    try:
        session = requests.Session()
        
        # テストケース
        test_cases = [
            {"name": "30問テスト", "count": 30, "dept": "基礎科目", "type": "basic"},
            {"name": "20問テスト", "count": 20, "dept": "道路部門", "type": "specialist"},
            {"name": "10問テスト", "count": 10, "dept": "河川・砂防部門", "type": "specialist"}
        ]
        
        all_results = []
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n🔍 {case['name']} - 直接HTML確認")
            print("-" * 50)
            
            try:
                # 1. 設定確認
                print(f"  Step 1: {case['count']}問設定")
                settings_resp = session.post(f"{BASE_URL}settings", 
                                           data={'questions_per_session': case['count']})
                
                if settings_resp.status_code == 200:
                    print(f"    ✅ 設定成功: {case['count']}問")
                else:
                    print(f"    ❌ 設定失敗: {settings_resp.status_code}")
                    continue
                
                # 2. 試験開始
                print(f"  Step 2: 試験開始")
                exam_data = {
                    'department': case['dept'],
                    'question_type': case['type']
                }
                
                exam_resp = session.post(f"{BASE_URL}exam", data=exam_data)
                
                print(f"    レスポンス: {exam_resp.status_code}")
                
                if exam_resp.status_code == 200:
                    html_content = exam_resp.text
                elif exam_resp.status_code == 302:
                    redirect_url = exam_resp.headers.get('Location', '/exam')
                    print(f"    リダイレクト: {redirect_url}")
                    
                    final_resp = session.get(f"{BASE_URL}{redirect_url.lstrip('/')}")
                    html_content = final_resp.text
                    print(f"    最終レスポンス: {final_resp.status_code}")
                else:
                    print(f"    ❌ エラー: {exam_resp.status_code}")
                    continue
                
                # 3. HTML詳細分析
                print(f"  Step 3: HTML進捗表示分析")
                
                # 進捗データ抽出
                progress_data = extract_progress_from_html(html_content)
                
                if progress_data:
                    print(f"    📊 検出されたパターン:")
                    for pattern_name, matches in progress_data.items():
                        print(f"      {pattern_name}: {matches}")
                        
                    # 期待値チェック
                    expected_progress = f"1/{case['count']}"
                    
                    # 全パターンから期待値検索
                    found_expected = False
                    found_wrong = False
                    
                    for pattern_name, matches in progress_data.items():
                        for match in matches:
                            if expected_progress in str(match):
                                print(f"    ✅ 期待進捗発見: {match} (パターン: {pattern_name})")
                                found_expected = True
                            elif "1/3" in str(match):
                                print(f"    ❌ 異常進捗発見: {match} (パターン: {pattern_name})")
                                found_wrong = True
                    
                    if not found_expected and not found_wrong:
                        print(f"    ⚠️ 期待進捗なし、異常進捗もなし")
                        
                        # 最も可能性の高いバッジ要素確認
                        badge_matches = progress_data.get('pattern_1', [])
                        if badge_matches:
                            print(f"    🔍 バッジ要素の内容: {badge_matches}")
                            
                else:
                    print(f"    ⚠️ 進捗パターン検出なし")
                    
                    # HTMLサイズ確認
                    print(f"    📏 HTMLサイズ: {len(html_content)}文字")
                    
                    # exam.htmlが含まれているか確認
                    if 'RCCM試験' in html_content:
                        print(f"    ✅ exam.htmlテンプレート確認")
                    else:
                        print(f"    ❌ exam.htmlテンプレートではない")
                
                # 結果記録
                result_summary = {
                    'case': case['name'],
                    'expected': expected_progress,
                    'found_data': progress_data,
                    'success': found_expected if 'found_expected' in locals() else False
                }
                all_results.append(result_summary)
                
            except Exception as e:
                print(f"  ❌ テスト例外: {e}")
                all_results.append({
                    'case': case['name'],
                    'error': str(e),
                    'success': False
                })
        
        # 総合結果分析
        print(f"\n📊 総合結果分析")
        print("=" * 50)
        
        success_count = sum(1 for result in all_results if result.get('success', False))
        total_count = len(all_results)
        
        print(f"成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        for result in all_results:
            case_name = result['case']
            if result.get('success'):
                print(f"  ✅ {case_name}: 正常")
            elif 'error' in result:
                print(f"  ❌ {case_name}: エラー - {result['error']}")
            else:
                print(f"  ⚠️ {case_name}: 進捗表示問題")
        
        if success_count == 0:
            print(f"\n🚨 全テスト失敗：根本的な問題が存在")
            print("  - 可能性1: テンプレート描画問題")
            print("  - 可能性2: セッション初期化問題")
            print("  - 可能性3: ルーティング問題")
        elif success_count < total_count:
            print(f"\n⚠️ 部分的問題：特定条件での失敗")
        else:
            print(f"\n✅ 全テスト成功：問題解決確認")
    
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
    print("✅ 直接HTML観察デバッグ完了")
    print("\n📊 最終観察結果:")
    print("  - 既存機能: 完全肯定・維持")
    print("  - 問題特定: HTML直接確認による精密分析")
    print("  - 次ステップ: 特定された問題箇所の修正")

if __name__ == "__main__":
    direct_html_observation()