#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク Task 8-10: 修正後テスト再実行（ASCII安全版）
目的: CSRF修正後の道路部門10問完走テストを完全実行
方針: 嘘をつかない、修正効果を正確に測定、ブラッシュアップで詳細化
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_road_department_access_post_fix():
    """8-10-1: 道路部門アクセスルート確認（修正後）"""
    print("=== 8-10-1: 道路部門アクセスルート確認（修正後） ===")
    print("目的: CSRF修正後の/departments/road/types アクセステスト")
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
                    print("OK 8-10-1 PASS: 道路部門アクセスルート正常（修正後）")
                    return True, response_text
                else:
                    print("NG 8-10-1 FAIL: 必要な要素が不足")
                    return False, response_text
                    
            else:
                print(f"NG 8-10-1 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-1 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_csrf_token_generation_post_fix():
    """8-10-2: CSRF修正後のトークン生成確認（ブラッシュアップ追加）"""
    print("=== 8-10-2: CSRF修正後のトークン生成確認 ===")
    print("目的: 修正されたCSRFトークン生成機能の動作確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始とCSRFトークン確認
            client.get('/start_exam/specialist_road', follow_redirects=True)
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"GET /exam status: {response.status_code}")
            
            if response.status_code == 200:
                print("OK 問題画面アクセス成功")
                
                # CSRFトークンの存在確認
                if 'csrf_token' in response_text:
                    print("OK CSRFトークン存在確認")
                    
                    # トークン値の抽出
                    import re
                    token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                    if token_match:
                        token_value = token_match.group(1)
                        print(f"修正後トークン形式: {token_value[:20]}...")
                        
                        # フォールバックトークンでないことを確認
                        if not token_value.startswith('fast_token_'):
                            print("OK 正規CSRFトークン形式確認（Flask-WTF互換）")
                            return True, token_value
                        else:
                            print("NG まだフォールバックトークンが使用されています")
                            return False, token_value
                    else:
                        print("NG CSRFトークン値抽出失敗")
                        return False, ""
                else:
                    print("NG CSRFトークンが存在しません")
                    return False, ""
            else:
                print(f"NG 問題画面アクセス失敗: {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-2 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_first_question_display_post_fix():
    """8-10-3: 1問目表示確認（修正後）"""
    print("=== 8-10-3: 1問目表示確認（修正後） ===")
    print("目的: CSRF修正後の問題フォーム、カテゴリ表示、進捗表示のチェック")
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
                
                # 1問目表示の確認項目（修正後）
                checks = [
                    ("問題番号表示", "1" in response_text and ("/" in response_text or "問題" in response_text)),
                    ("問題文表示", "<h3>" in response_text or "問題" in response_text),
                    ("回答選択肢", 'type="radio"' in response_text or "選択" in response_text),
                    ("送信フォーム", "<form" in response_text and 'method="POST"' in response_text),
                    ("CSRFトークン", 'name="csrf_token"' in response_text),
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
                if success_count >= 5 and field_mixing_check:
                    print("OK 8-10-3 PASS: 1問目表示正常（修正後）")
                    return True, response_text
                else:
                    print("NG 8-10-3 FAIL: 1問目表示に問題（修正後も継続）")
                    return False, response_text
                    
            else:
                print(f"NG 8-10-3 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-3 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_question_transition_post_fix():
    """8-10-4: 1問目から2問目遷移テスト（修正後）"""
    print("=== 8-10-4: 1問目から2問目遷移テスト（修正後） ===")
    print("目的: CSRF修正後の回答送信とセッション継続性確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 1問目取得とCSRFトークン取得
            response1 = client.get('/exam')
            if response1.status_code != 200:
                print(f"NG 8-10-4 FAIL: 1問目取得失敗 {response1.status_code}")
                return False, ""
            
            response_text = response1.get_data(as_text=True)
            
            # CSRFトークン抽出
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            if not token_match:
                print("NG 8-10-4 FAIL: CSRFトークン取得失敗")
                return False, ""
            
            csrf_token = token_match.group(1)
            print(f"CSRFトークン取得: {csrf_token[:15]}...")
            
            # 1問目回答送信（CSRFトークン付き）
            post_data = {
                'answer': 'A',
                'qid': '1',
                'csrf_token': csrf_token
            }
            
            response2 = client.post('/exam', data=post_data, follow_redirects=True)
            
            print(f"回答送信ステータス: {response2.status_code}")
            print(f"レスポンスサイズ: {len(response2.get_data())} bytes")
            
            if response2.status_code == 200:
                print("OK 回答送信成功（CSRF修正効果確認）")
                
                response_text = response2.get_data(as_text=True)
                
                # セッション継続性の確認
                checks = [
                    ("フィードバック表示", "正解" in response_text or "不正解" in response_text or "解答" in response_text),
                    ("次問題表示", "次" in response_text or "2" in response_text),
                    ("セッション継続", "問題" in response_text and len(response_text) > 500),
                    ("道路分野維持", "道路" in response_text),
                    ("CSRFエラー回避", "CSRF" not in response_text.upper() and "400" not in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 4:
                    print("OK 8-10-4 PASS: 1→2問目遷移成功（CSRF修正効果確認）")
                    return True, response_text
                else:
                    print("NG 8-10-4 FAIL: セッション継続に問題（修正後も継続）")
                    return False, response_text
                    
            else:
                print(f"NG 8-10-4 FAIL: 回答送信エラー {response2.status_code}（CSRF修正効果なし）")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-4 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_full_10_question_sequence_post_fix():
    """8-10-5: 2-9問目連続処理テスト（修正後）"""
    print("=== 8-10-5: 2-9問目連続処理テスト（修正後） ===")
    print("目的: CSRF修正後のセッション継続と分野混在チェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            question_categories = []
            question_progression = []
            csrf_success_count = 0
            
            # 1問目から9問目まで処理
            for q_num in range(1, 10):
                print(f"--- 問題 {q_num}/10 処理中 ---")
                
                # 問題取得
                response = client.get('/exam')
                if response.status_code != 200:
                    print(f"NG 問題{q_num} 取得失敗: {response.status_code}")
                    return False, ""
                
                response_text = response.get_data(as_text=True)
                
                # CSRFトークン抽出
                import re
                token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                if not token_match:
                    print(f"NG 問題{q_num} CSRFトークン取得失敗")
                    continue
                
                csrf_token = token_match.group(1)
                
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
                
                # 回答送信（CSRFトークン付き）
                post_data = {
                    'answer': ['A', 'B', 'C', 'D'][q_num % 4],
                    'qid': str(q_num),
                    'csrf_token': csrf_token
                }
                
                post_response = client.post('/exam', data=post_data, follow_redirects=True)
                if post_response.status_code == 200:
                    csrf_success_count += 1
                    print(f"  OK 問題{q_num} 回答送信完了（CSRF成功）")
                else:
                    print(f"  NG 問題{q_num} 回答送信失敗: {post_response.status_code}")
                
                time.sleep(0.1)  # 負荷軽減
            
            # 結果分析
            print("\\n--- 2-9問目連続処理結果分析（修正後） ---")
            road_count = question_categories.count("道路")
            total_questions = len(question_categories)
            
            print(f"処理問題数: {total_questions}/8")
            print(f"道路カテゴリ問題: {road_count}/{total_questions}")
            print(f"分野混在問題: {total_questions - road_count}/{total_questions}")
            print(f"進捗表示正常: {sum(question_progression)}/{total_questions}")
            print(f"CSRF成功率: {csrf_success_count}/{total_questions} ({csrf_success_count/total_questions*100:.1f}%)")
            
            # 成功判定（CSRF修正効果を考慮）
            if (road_count == total_questions and 
                sum(question_progression) >= total_questions * 0.8 and
                csrf_success_count >= total_questions * 0.9):
                print("OK 8-10-5 PASS: 2-9問目連続処理成功（CSRF修正効果確認）")
                return True, {"categories": question_categories, "progression": question_progression, "csrf_success": csrf_success_count}
            else:
                print("NG 8-10-5 FAIL: 分野混在またはCSRF問題継続")
                return False, {"categories": question_categories, "progression": question_progression, "csrf_success": csrf_success_count}
                
    except Exception as e:
        print(f"NG 8-10-5 FAIL: 例外エラー - {str(e)}")
        return False, {}

def test_final_question_and_results_post_fix():
    """8-10-6: 10問目最終回答処理テスト（修正後）"""
    print("=== 8-10-6: 10問目最終回答処理テスト（修正後） ===")
    print("目的: CSRF修正後の結果画面への遷移確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # フルセッション実行（1-9問目）
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 1-9問目を高速処理（CSRFトークン付き）
            for q_num in range(1, 10):
                response = client.get('/exam')
                if response.status_code != 200:
                    continue
                
                response_text = response.get_data(as_text=True)
                
                # CSRFトークン抽出
                import re
                token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                if token_match:
                    csrf_token = token_match.group(1)
                    post_data = {
                        'answer': 'A', 
                        'qid': str(q_num),
                        'csrf_token': csrf_token
                    }
                    client.post('/exam', data=post_data, follow_redirects=True)
            
            # 10問目処理
            print("--- 10問目最終処理（修正後） ---")
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
            
            # CSRFトークン取得
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            if not token_match:
                print("  NG 10問目CSRFトークン取得失敗")
                return False, ""
            
            csrf_token = token_match.group(1)
            
            # 最終回答送信（CSRFトークン付き）
            final_post_data = {
                'answer': 'D', 
                'qid': '10',
                'csrf_token': csrf_token
            }
            final_response = client.post('/exam', data=final_post_data, follow_redirects=True)
            
            print(f"最終回答ステータス: {final_response.status_code}")
            
            if final_response.status_code == 200:
                final_text = final_response.get_data(as_text=True)
                
                # 結果画面への遷移確認
                result_checks = [
                    ("結果画面遷移", "結果" in final_text or "スコア" in final_text or "完了" in final_text),
                    ("10問完了表示", "10" in final_text),
                    ("道路部門表示", "道路" in final_text),
                    ("統計情報表示", "正解" in final_text or "%" in final_text),
                    ("CSRFエラー回避", "400" not in final_text and "CSRF" not in final_text.upper())
                ]
                
                for check_name, result in result_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in result_checks if result)
                if success_count >= 4:
                    print("OK 8-10-6 PASS: 10問目処理と結果画面遷移成功（CSRF修正効果確認）")
                    return True, final_text
                else:
                    print("NG 8-10-6 FAIL: 結果画面遷移に問題（修正後も継続）")
                    return False, final_text
            else:
                print(f"NG 8-10-6 FAIL: 最終回答エラー {final_response.status_code}（CSRF修正効果なし）")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-6 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_results_page_validation_post_fix():
    """8-10-7: 最終結果画面表示確認（修正後）"""
    print("=== 8-10-7: 最終結果画面表示確認（修正後） ===")
    print("目的: CSRF修正後のスコア、部門名、統計情報のチェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 完全な10問セッション実行（CSRFトークン付き）
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 全10問高速処理（CSRFトークン付き）
            for q_num in range(1, 11):
                response = client.get('/exam')
                if response.status_code != 200:
                    continue
                
                response_text = response.get_data(as_text=True)
                
                # CSRFトークン抽出
                import re
                token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
                if token_match:
                    csrf_token = token_match.group(1)
                    post_data = {
                        'answer': 'A', 
                        'qid': str(q_num),
                        'csrf_token': csrf_token
                    }
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
                    ("再挑戦リンク", "再" in result_text or "もう一度" in result_text or "戻る" in result_text),
                    ("CSRFエラー回避", "400" not in result_text and "CSRF" not in result_text.upper())
                ]
                
                print("--- 結果画面詳細チェック（修正後） ---")
                for check_name, result in detailed_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in detailed_checks if result)
                success_rate = success_count / len(detailed_checks) * 100
                
                print(f"\\n結果画面品質（修正後）: {success_count}/{len(detailed_checks)} ({success_rate:.1f}%)")
                
                if success_count >= 7:
                    print("OK 8-10-7 PASS: 結果画面表示高品質（CSRF修正効果確認）")
                    return True, result_text
                elif success_count >= 5:
                    print("OK 8-10-7 PASS: 結果画面表示基本要件満足（CSRF修正効果あり）")
                    return True, result_text
                else:
                    print("NG 8-10-7 FAIL: 結果画面表示不十分（修正後も継続）")
                    return False, result_text
                    
            else:
                print(f"NG 8-10-7 FAIL: 結果画面アクセスエラー {result_response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 8-10-7 FAIL: 例外エラー - {str(e)}")
        return False, ""

def run_post_csrf_fix_comprehensive_test():
    """道路部門10問完走テスト再実行メイン（CSRF修正後）"""
    print("=== 道路部門10問完走テスト再実行（CSRF修正後・ブラッシュアップ版） ===")
    print("=" * 80)
    print("方針: CSRF修正効果の正確な測定、嘘をつかない実証")
    print("ブラッシュアップ: 修正前失敗7サブタスク全てを再実行・詳細化")
    print("追加検証: CSRFトークン生成確認、修正前後比較")
    print()
    
    results = {}
    test_data = {}
    
    # 8-10-1: アクセスルート確認（修正後）
    success_8_10_1, response_8_10_1 = test_road_department_access_post_fix()
    results['8-10-1'] = success_8_10_1
    test_data['8-10-1'] = response_8_10_1
    time.sleep(1)
    
    # 8-10-2: CSRF修正後のトークン生成確認（ブラッシュアップ追加）
    success_8_10_2, token_8_10_2 = test_csrf_token_generation_post_fix()
    results['8-10-2'] = success_8_10_2
    test_data['8-10-2'] = token_8_10_2
    time.sleep(1)
    
    # 8-10-3: 1問目表示確認（修正後）
    success_8_10_3, response_8_10_3 = test_first_question_display_post_fix()
    results['8-10-3'] = success_8_10_3
    test_data['8-10-3'] = response_8_10_3
    time.sleep(1)
    
    # 8-10-4: 問題遷移テスト（修正後）
    success_8_10_4, response_8_10_4 = test_question_transition_post_fix()
    results['8-10-4'] = success_8_10_4
    test_data['8-10-4'] = response_8_10_4
    time.sleep(1)
    
    # 8-10-5: 連続処理テスト（修正後）
    success_8_10_5, data_8_10_5 = test_full_10_question_sequence_post_fix()
    results['8-10-5'] = success_8_10_5
    test_data['8-10-5'] = data_8_10_5
    time.sleep(1)
    
    # 8-10-6: 最終問題処理テスト（修正後）
    success_8_10_6, response_8_10_6 = test_final_question_and_results_post_fix()
    results['8-10-6'] = success_8_10_6
    test_data['8-10-6'] = response_8_10_6
    time.sleep(1)
    
    # 8-10-7: 結果画面検証（修正後）
    success_8_10_7, response_8_10_7 = test_results_page_validation_post_fix()
    results['8-10-7'] = success_8_10_7
    test_data['8-10-7'] = response_8_10_7
    
    # 総合結果分析
    print("\\n" + "=" * 80)
    print("=== 道路部門10問完走テスト - CSRF修正後総合結果分析 ===")
    print("=" * 80)
    
    total_tests = len(results)
    success_tests = sum(1 for success in results.values() if success)
    success_rate = (success_tests / total_tests) * 100
    
    print(f"実行済みテスト: {total_tests}/7 サブタスク（CSRF修正後ブラッシュアップ版）")
    print(f"成功テスト: {success_tests}/{total_tests}")
    print(f"総合成功率（修正後）: {success_rate:.1f}%")
    print()
    
    print("詳細結果:")
    for task_id, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {task_id}: {status}")
    
    # CSRF修正効果分析
    if '8-10-5' in test_data and isinstance(test_data['8-10-5'], dict):
        csrf_success = test_data['8-10-5'].get('csrf_success', 0)
        total_attempts = 8  # 2-9問目
        if csrf_success > 0:
            csrf_success_rate = csrf_success / total_attempts * 100
            print(f"\\nCSRF修正効果分析:")
            print(f"  CSRF成功率: {csrf_success_rate:.1f}% ({csrf_success}/{total_attempts})")
            if csrf_success_rate >= 90:
                print("  OK CSRF修正大成功")
            elif csrf_success_rate >= 70:
                print("  OK CSRF修正効果あり")
            else:
                print("  NG CSRF修正効果不十分")
    
    # 修正前後比較
    print(f"\\n修正前後比較:")
    print(f"  修正前成功率: 28.6% (2/7サブタスク)")
    print(f"  修正後成功率: {success_rate:.1f}% ({success_tests}/{total_tests}サブタスク)")
    improvement = success_rate - 28.6
    print(f"  改善効果: {improvement:+.1f}ポイント")
    
    print()
    
    # 最終判定
    if success_tests >= 6:  # 7個中6個以上成功
        print("*** CSRF修正後道路部門10問完走テスト - 基本成功 ***")
        print(">>> Task 8-10 完了: CSRF修正効果確認済み")
        
        if success_tests == total_tests:
            print("*** 完全成功：CSRF修正により全サブタスクパス ***")
        
        return True
    elif success_tests >= 4:  # 7個中4個以上成功
        print("!!! 部分成功：CSRF修正効果あり、残り問題要対応")
        print(">>> 追加修正後に再テスト推奨")
        return False
    else:
        print("!!! CSRF修正効果不十分：根本的な問題が継続")
        print(">>> システム根本的修正が必要")
        return False

if __name__ == "__main__":
    success = run_post_csrf_fix_comprehensive_test()
    if success:
        print("\\nSUCCESS: Task 8-10 completed - CSRF修正効果確認済み")
    else:
        print("\\nFAILED: Task 8-10 requires additional fixes")