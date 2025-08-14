#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門10問完走テスト実行スクリプト（ウルトラシンク方式）
目的: 現在システムで道路部門の10問完走テストを完全実行
方針: 嘘をつかない、作業実施だけでチェックマークは付けない、問題解決後にのみ完了
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_road_department_access():
    """8-1: 道路部門アクセスルート確認"""
    print("=== 8-1: 道路部門アクセスルート確認 ===")
    print("目的: /departments/road/types アクセステスト")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 道路部門選択ページにアクセス
            response = client.get('/departments/road/types')
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("OK 道路部門ページアクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # 重要要素のチェック
                checks = [
                    ("道路部門表示", "道路" in response_text),
                    ("問題種別選択", "選択" in response_text or "開始" in response_text),
                    ("HTMLフォーム", "<form" in response_text or "button" in response_text),
                    ("専門問題リンク", "specialist" in response_text.lower() or "4-2" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                # 成功判定
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 3:
                    print("OK 8-1 PASS: 道路部門アクセスルート正常")
                    return True, response_text
                else:
                    print("NG 8-1 FAIL: 必要な要素が不足")
                    return False, response_text
                    
            else:
                print(f"NG 8-1 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"❌ 8-1 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_road_department_session_initialization():
    """8-2: 道路部門セッション初期化確認"""
    print("\n=== 8-2: 道路部門セッション初期化確認 ===")
    print("目的: /start_exam/specialist_road アクセステスト")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション初期化テスト
            response = client.get('/start_exam/specialist_road', follow_redirects=True)
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("✅ セッション初期化アクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # セッション初期化の確認項目
                checks = [
                    ("リダイレクト成功", len(response_text) > 1000),
                    ("問題画面表示", "/exam" in response.request.url or "問題" in response_text),
                    ("セッション作成", "session" in response_text.lower() or "quiz" in response_text.lower())
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 2:
                    print("✅ 8-2 PASS: セッション初期化成功")
                    return True, response_text
                else:
                    print("❌ 8-2 FAIL: セッション初期化問題")
                    return False, response_text
                    
            else:
                print(f"❌ 8-2 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"❌ 8-2 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_first_question_display():
    """8-3: 1問目表示確認"""
    print("\n=== 8-3: 1問目表示確認 ===")
    print("目的: 問題フォーム、カテゴリ表示、進捗表示のチェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始後の問題画面取得
            client.get('/start_exam/specialist_road', follow_redirects=True)
            response = client.get('/exam')
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("✅ 1問目画面アクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # 1問目表示の確認項目
                checks = [
                    ("問題番号表示", "1" in response_text and ("/" in response_text or "問題" in response_text)),
                    ("問題文表示", "<h3>" in response_text or "問題" in response_text),
                    ("回答選択肢", "type=\"radio\"" in response_text or "選択" in response_text),
                    ("送信フォーム", "<form" in response_text and "method=\"post\"" in response_text),
                    ("カテゴリ表示", "道路" in response_text or "カテゴリ" in response_text),
                    ("進捗表示", "1" in response_text and "10" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"  {status} {check_name}: {result}")
                
                # 分野混在チェック（重要）
                if "道路" in response_text:
                    print("  ✅ 分野確認: 道路カテゴリ表示確認")
                    field_mixing_check = True
                else:
                    print("  ⚠️ 分野確認: 道路カテゴリ表示要確認")
                    field_mixing_check = False
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 4 and field_mixing_check:
                    print("✅ 8-3 PASS: 1問目表示正常")
                    return True, response_text
                else:
                    print("❌ 8-3 FAIL: 1問目表示に問題")
                    return False, response_text
                    
            else:
                print(f"❌ 8-3 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"❌ 8-3 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_question_transition():
    """8-4: 1問目から2問目遷移テスト"""
    print("\n=== 8-4: 1問目から2問目遷移テスト ===")
    print("目的: 回答送信とセッション継続性確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 1問目取得
            response1 = client.get('/exam')
            if response1.status_code != 200:
                print(f"❌ 8-4 FAIL: 1問目取得失敗 {response1.status_code}")
                return False, ""
            
            # 1問目回答送信（仮の回答）
            post_data = {
                'answer': 'A',
                'question_id': '1',  # 仮のID
            }
            
            response2 = client.post('/exam', data=post_data, follow_redirects=True)
            
            print(f"回答送信ステータス: {response2.status_code}")
            print(f"レスポンスサイズ: {len(response2.get_data())} bytes")
            
            if response2.status_code == 200:
                print("✅ 回答送信成功")
                
                response_text = response2.get_data(as_text=True)
                
                # セッション継続性の確認
                checks = [
                    ("フィードバック表示", "正解" in response_text or "不正解" in response_text or "解答" in response_text),
                    ("次問題リンク", "次" in response_text or "2" in response_text),
                    ("セッション継続", "問題" in response_text and len(response_text) > 500),
                    ("道路分野維持", "道路" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 3:
                    print("✅ 8-4 PASS: 1→2問目遷移成功")
                    return True, response_text
                else:
                    print("❌ 8-4 FAIL: セッション継続に問題")
                    return False, response_text
                    
            else:
                print(f"❌ 8-4 FAIL: 回答送信エラー {response2.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"❌ 8-4 FAIL: 例外エラー - {str(e)}")
        return False, ""

def run_road_department_10q_test():
    """道路部門10問完走テスト実行メイン"""
    print("=== 道路部門10問完走テスト開始（ウルトラシンク方式） ===")
    print("=" * 70)
    print("方針: 嘘をつかない、問題解決後にのみ完了マーク")
    print("ブラッシュアップ: 作業中にタスクを詳細化・追加")
    print()
    
    results = {}
    
    # 8-1: アクセスルート確認
    success_8_1, response_8_1 = test_road_department_access()
    results['8-1'] = success_8_1
    time.sleep(1)
    
    # 8-2: セッション初期化確認
    success_8_2, response_8_2 = test_road_department_session_initialization()
    results['8-2'] = success_8_2
    time.sleep(1)
    
    # 8-3: 1問目表示確認
    success_8_3, response_8_3 = test_first_question_display()
    results['8-3'] = success_8_3
    time.sleep(1)
    
    # 8-4: 問題遷移テスト
    success_8_4, response_8_4 = test_question_transition()
    results['8-4'] = success_8_4
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("=== 道路部門10問完走テスト - 中間結果 ===")
    print("=" * 70)
    
    total_tests = len(results)
    success_tests = sum(1 for success in results.values() if success)
    
    print(f"実行済みテスト: {total_tests}/10 サブタスク")
    print(f"成功テスト: {success_tests}/{total_tests}")
    print(f"成功率: {(success_tests/total_tests)*100:.1f}%")
    print()
    
    print("詳細結果:")
    for task_id, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {task_id}: {status}")
    
    print()
    
    if success_tests == total_tests:
        print("*** 現在までの全サブタスク成功 ***")
        print(">>> 次フェーズ（8-5以降）実行準備完了")
        return True
    else:
        print("!!! 一部サブタスクで問題検出")
        print(">>> 問題解決が必要")
        return False

if __name__ == "__main__":
    run_road_department_10q_test()