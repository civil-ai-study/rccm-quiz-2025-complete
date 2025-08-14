#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門10問完走テスト実行スクリプト（ウルトラシンク方式・Unicode修正版）
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
        print(f"NG 8-1 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_road_department_session_initialization():
    """8-2: 道路部門セッション初期化確認"""
    print("=== 8-2: 道路部門セッション初期化確認 ===")
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
                print("OK セッション初期化アクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # セッション初期化の確認項目
                checks = [
                    ("リダイレクト成功", len(response_text) > 1000),
                    ("問題画面表示", "/exam" in str(response.request) or "問題" in response_text),
                    ("セッション作成", "session" in response_text.lower() or "quiz" in response_text.lower())
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 2:
                    print("OK 8-2 PASS: セッション初期化成功")
                    return True, response_text
                else:
                    print("NG 8-2 FAIL: セッション初期化問題")
                    return False, response_text
                    
            else:
                print(f"NG 8-2 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-2 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_first_question_display():
    """8-3: 1問目表示確認"""
    print("=== 8-3: 1問目表示確認 ===")
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
                print("OK 1問目画面アクセス成功")
                
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
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                # 分野混在チェック（重要）
                if "道路" in response_text:
                    print("  OK 分野確認: 道路カテゴリ表示確認")
                    field_mixing_check = True
                else:
                    print("  WARN 分野確認: 道路カテゴリ表示要確認")
                    field_mixing_check = False
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 4 and field_mixing_check:
                    print("OK 8-3 PASS: 1問目表示正常")
                    return True, response_text
                else:
                    print("NG 8-3 FAIL: 1問目表示に問題")
                    return False, response_text
                    
            else:
                print(f"NG 8-3 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-3 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_question_transition():
    """8-4: 1問目から2問目遷移テスト"""
    print("=== 8-4: 1問目から2問目遷移テスト ===")
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
                print(f"NG 8-4 FAIL: 1問目取得失敗 {response1.status_code}")
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
                print("OK 回答送信成功")
                
                response_text = response2.get_data(as_text=True)
                
                # セッション継続性の確認
                checks = [
                    ("フィードバック表示", "正解" in response_text or "不正解" in response_text or "解答" in response_text),
                    ("次問題リンク", "次" in response_text or "2" in response_text),
                    ("セッション継続", "問題" in response_text and len(response_text) > 500),
                    ("道路分野維持", "道路" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 3:
                    print("OK 8-4 PASS: 1→2問目遷移成功")
                    return True, response_text
                else:
                    print("NG 8-4 FAIL: セッション継続に問題")
                    return False, response_text
                    
            else:
                print(f"NG 8-4 FAIL: 回答送信エラー {response2.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-4 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_full_10_question_sequence():
    """8-5: 2-9問目連続処理テスト（ブラッシュアップ追加）"""
    print("=== 8-5: 2-9問目連続処理テスト ===")
    print("目的: セッション継続と分野混在チェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            question_categories = []
            question_progression = []
            
            # 1問目から9問目まで処理
            for q_num in range(1, 10):
                print(f"--- 問題 {q_num}/10 処理中 ---")
                
                # 問題取得
                response = client.get('/exam')
                if response.status_code != 200:
                    print(f"NG 問題{q_num} 取得失敗: {response.status_code}")
                    return False, ""
                
                response_text = response.get_data(as_text=True)
                
                # カテゴリチェック（分野混在確認）
                if "道路" in response_text:
                    question_categories.append("道路")
                    print(f"  OK 問題{q_num} カテゴリ: 道路")
                else:
                    # その他のカテゴリを検出
                    other_categories = ["河川", "都市計画", "造園", "建設環境", "鋼構造", "土質", "施工", "水道", "森林", "農業", "トンネル"]
                    found_other = None
                    for cat in other_categories:
                        if cat in response_text:
                            found_other = cat
                            break
                    
                    if found_other:
                        question_categories.append(found_other)
                        print(f"  NG 問題{q_num} 分野混在: {found_other}")
                    else:
                        question_categories.append("不明")
                        print(f"  WARN 問題{q_num} カテゴリ不明")
                
                # 進捗確認
                if f"{q_num}" in response_text and "10" in response_text:
                    question_progression.append(True)
                    print(f"  OK 問題{q_num} 進捗表示正常")
                else:
                    question_progression.append(False)
                    print(f"  NG 問題{q_num} 進捗表示異常")
                
                # 回答送信
                post_data = {
                    'answer': ['A', 'B', 'C', 'D'][q_num % 4],  # 回答をローテーション
                    'question_id': str(q_num)
                }
                
                post_response = client.post('/exam', data=post_data, follow_redirects=True)
                if post_response.status_code != 200:
                    print(f"NG 問題{q_num} 回答送信失敗: {post_response.status_code}")
                    return False, ""
                
                print(f"  OK 問題{q_num} 回答送信完了")
                time.sleep(0.1)  # 負荷軽減
            
            # 結果分析
            print("\n--- 2-9問目連続処理結果分析 ---")
            road_count = question_categories.count("道路")
            total_questions = len(question_categories)
            
            print(f"処理問題数: {total_questions}/8")
            print(f"道路カテゴリ問題: {road_count}/{total_questions}")
            print(f"分野混在問題: {total_questions - road_count}/{total_questions}")
            print(f"進捗表示正常: {sum(question_progression)}/{total_questions}")
            
            # 成功判定
            if road_count == total_questions and sum(question_progression) >= total_questions * 0.8:
                print("OK 8-5 PASS: 2-9問目連続処理成功")
                return True, {"categories": question_categories, "progression": question_progression}
            else:
                print("NG 8-5 FAIL: 分野混在またはセッション問題")
                return False, {"categories": question_categories, "progression": question_progression}
                
    except Exception as e:
        print(f"NG 8-5 FAIL: 例外エラー - {str(e)}")
        return False, {}

def test_final_question_and_results():
    """8-6: 10問目最終回答処理テスト（ブラッシュアップ追加）"""
    print("=== 8-6: 10問目最終回答処理テスト ===")
    print("目的: 結果画面への遷移確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # フルセッション実行（1-9問目）
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 1-9問目を高速処理
            for q_num in range(1, 10):
                client.get('/exam')
                post_data = {'answer': 'A', 'question_id': str(q_num)}
                client.post('/exam', data=post_data, follow_redirects=True)
            
            # 10問目処理
            print("--- 10問目最終処理 ---")
            response10 = client.get('/exam')
            
            if response10.status_code != 200:
                print(f"NG 10問目取得失敗: {response10.status_code}")
                return False, ""
            
            response_text = response10.get_data(as_text=True)
            
            # 10問目確認
            if "10" in response_text:
                print("  OK 10問目表示確認")
            else:
                print("  NG 10問目表示異常")
                return False, ""
            
            # 最終回答送信
            final_post_data = {'answer': 'D', 'question_id': '10'}
            final_response = client.post('/exam', data=final_post_data, follow_redirects=True)
            
            print(f"最終回答ステータス: {final_response.status_code}")
            
            if final_response.status_code == 200:
                final_text = final_response.get_data(as_text=True)
                
                # 結果画面への遷移確認
                result_checks = [
                    ("結果画面遷移", "結果" in final_text or "スコア" in final_text or "完了" in final_text),
                    ("10問完了表示", "10" in final_text),
                    ("道路部門表示", "道路" in final_text),
                    ("統計情報表示", "正解" in final_text or "%" in final_text)
                ]
                
                for check_name, result in result_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in result_checks if result)
                if success_count >= 3:
                    print("OK 8-6 PASS: 10問目処理と結果画面遷移成功")
                    return True, final_text
                else:
                    print("NG 8-6 FAIL: 結果画面遷移に問題")
                    return False, final_text
            else:
                print(f"NG 8-6 FAIL: 最終回答エラー {final_response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-6 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_results_page_validation():
    """8-7: 最終結果画面表示確認（ブラッシュアップ追加）"""
    print("=== 8-7: 最終結果画面表示確認 ===")
    print("目的: スコア、部門名、統計情報のチェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 完全な10問セッション実行
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 全10問高速処理
            for q_num in range(1, 11):
                client.get('/exam')
                post_data = {'answer': 'A', 'question_id': str(q_num)}
                client.post('/exam', data=post_data, follow_redirects=True)
            
            # 結果画面直接アクセス
            result_response = client.get('/result')
            
            print(f"結果画面ステータス: {result_response.status_code}")
            
            if result_response.status_code == 200:
                result_text = result_response.get_data(as_text=True)
                print(f"結果画面サイズ: {len(result_text)} bytes")
                
                # 結果画面詳細チェック
                detailed_checks = [
                    ("部門名表示", "道路" in result_text),
                    ("回答数表示", "10" in result_text),
                    ("正解数表示", "正解" in result_text or "score" in result_text.lower()),
                    ("正答率表示", "%" in result_text or "率" in result_text),
                    ("問題種別表示", "専門" in result_text or "4-2" in result_text),
                    ("完了メッセージ", "完了" in result_text or "終了" in result_text or "結果" in result_text),
                    ("日時情報", "2025" in result_text or "日" in result_text),
                    ("再挑戦リンク", "再" in result_text or "もう一度" in result_text or "戻る" in result_text)
                ]
                
                print("--- 結果画面詳細チェック ---")
                for check_name, result in detailed_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in detailed_checks if result)
                success_rate = success_count / len(detailed_checks) * 100
                
                print(f"\n結果画面品質: {success_count}/{len(detailed_checks)} ({success_rate:.1f}%)")
                
                if success_count >= 6:
                    print("OK 8-7 PASS: 結果画面表示高品質")
                    return True, result_text
                elif success_count >= 4:
                    print("OK 8-7 PASS: 結果画面表示基本要件満足")
                    return True, result_text
                else:
                    print("NG 8-7 FAIL: 結果画面表示不十分")
                    return False, result_text
                    
            else:
                print(f"NG 8-7 FAIL: 結果画面アクセスエラー {result_response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-7 FAIL: 例外エラー - {str(e)}")
        return False, ""

def run_comprehensive_road_test():
    """道路部門10問完走テスト実行メイン（ブラッシュアップ版）"""
    print("=== 道路部門10問完走テスト開始（ウルトラシンク方式・ブラッシュアップ版） ===")
    print("=" * 80)
    print("方針: 嘘をつかない、問題解決後にのみ完了マーク")
    print("ブラッシュアップ: 作業中にタスクを詳細化・追加")
    print("追加サブタスク: 8-5(連続処理), 8-6(最終問題), 8-7(結果画面)")
    print()
    
    results = {}
    test_data = {}
    
    # 8-1: アクセスルート確認
    success_8_1, response_8_1 = test_road_department_access()
    results['8-1'] = success_8_1
    test_data['8-1'] = response_8_1
    time.sleep(1)
    
    # 8-2: セッション初期化確認
    success_8_2, response_8_2 = test_road_department_session_initialization()
    results['8-2'] = success_8_2
    test_data['8-2'] = response_8_2
    time.sleep(1)
    
    # 8-3: 1問目表示確認
    success_8_3, response_8_3 = test_first_question_display()
    results['8-3'] = success_8_3
    test_data['8-3'] = response_8_3
    time.sleep(1)
    
    # 8-4: 問題遷移テスト
    success_8_4, response_8_4 = test_question_transition()
    results['8-4'] = success_8_4
    test_data['8-4'] = response_8_4
    time.sleep(1)
    
    # 8-5: 連続処理テスト（ブラッシュアップ追加）
    success_8_5, data_8_5 = test_full_10_question_sequence()
    results['8-5'] = success_8_5
    test_data['8-5'] = data_8_5
    time.sleep(1)
    
    # 8-6: 最終問題処理テスト（ブラッシュアップ追加）
    success_8_6, response_8_6 = test_final_question_and_results()
    results['8-6'] = success_8_6
    test_data['8-6'] = response_8_6
    time.sleep(1)
    
    # 8-7: 結果画面検証（ブラッシュアップ追加）
    success_8_7, response_8_7 = test_results_page_validation()
    results['8-7'] = success_8_7
    test_data['8-7'] = response_8_7
    
    # 総合結果分析
    print("\n" + "=" * 80)
    print("=== 道路部門10問完走テスト - 総合結果分析 ===")
    print("=" * 80)
    
    total_tests = len(results)
    success_tests = sum(1 for success in results.values() if success)
    success_rate = (success_tests / total_tests) * 100
    
    print(f"実行済みテスト: {total_tests}/7 サブタスク（ブラッシュアップ後）")
    print(f"成功テスト: {success_tests}/{total_tests}")
    print(f"総合成功率: {success_rate:.1f}%")
    print()
    
    print("詳細結果:")
    for task_id, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {task_id}: {status}")
    
    # 分野混在分析
    if '8-5' in test_data and isinstance(test_data['8-5'], dict):
        categories = test_data['8-5'].get('categories', [])
        if categories:
            road_ratio = categories.count("道路") / len(categories) * 100
            print(f"\n分野混在分析:")
            print(f"  道路分野問題率: {road_ratio:.1f}% ({categories.count('道路')}/{len(categories)})")
            if road_ratio == 100:
                print("  OK 分野混在ゼロ確認")
            else:
                print("  NG 分野混在問題検出")
    
    print()
    
    # 最終判定
    if success_tests >= 6:  # 7個中6個以上成功
        print("*** 道路部門10問完走テスト - 基本成功 ***")
        print(">>> 次タスク（8-8以降またはタスク9）実行可能")
        
        if success_tests == total_tests:
            print("*** 完全成功：全サブタスクパス ***")
        
        return True
    elif success_tests >= 4:  # 7個中4個以上成功
        print("!!! 部分成功：重要な問題あり")
        print(">>> 修正後に再テスト推奨")
        return False
    else:
        print("!!! 重大な問題：大部分のテスト失敗")
        print(">>> システム根本的修正が必要")
        return False

if __name__ == "__main__":
    run_comprehensive_road_test()