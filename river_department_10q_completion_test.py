#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク Task 9: 河川部門10問完走テスト実行（CSRF対応版）
目的: 河川、砂防及び海岸・海洋部門での10問完走テストを完全実行
方針: 道路部門で実証されたCSRF修正効果を河川部門でも確認
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_river_department_access():
    """9-1: 河川部門アクセスルート確認"""
    print("=== 9-1: 河川部門アクセスルート確認 ===")
    print("目的: /departments/river/types アクセステスト")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 河川部門選択ページにアクセス
            response = client.get('/departments/river/types')
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("OK 河川部門ページアクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # 重要要素のチェック
                checks = [
                    ("河川部門表示", "河川" in response_text or "砂防" in response_text or "海岸" in response_text),
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
                    print("OK 9-1 PASS: 河川部門アクセスルート正常")
                    return True, response_text
                else:
                    print("NG 9-1 FAIL: 必要な要素が不足")
                    return False, response_text
                    
            else:
                print(f"NG 9-1 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-1 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_river_department_session_initialization():
    """9-2: 河川部門セッション初期化確認"""
    print("=== 9-2: 河川部門セッション初期化確認 ===")
    print("目的: /start_exam/specialist_river アクセステスト")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション初期化テスト
            response = client.get('/start_exam/specialist_river', follow_redirects=True)
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("OK セッション初期化アクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # セッション初期化の確認項目
                checks = [
                    ("リダイレクト成功", len(response_text) > 1000),
                    ("問題画面表示", "/exam" in str(response.request) or "問題" in response_text),
                    ("セッション作成", "session" in response_text.lower() or "quiz" in response_text.lower()),
                    ("河川分野表示", "河川" in response_text or "砂防" in response_text or "海岸" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 3:
                    print("OK 9-2 PASS: 河川部門セッション初期化成功")
                    return True, response_text
                else:
                    print("NG 9-2 FAIL: セッション初期化問題")
                    return False, response_text
                    
            else:
                print(f"NG 9-2 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-2 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_river_first_question_display():
    """9-3: 河川部門1問目表示確認（CSRF対応）"""
    print("=== 9-3: 河川部門1問目表示確認（CSRF対応） ===")
    print("目的: 問題フォーム、カテゴリ表示、進捗表示、CSRFトークンのチェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始後の問題画面取得
            client.get('/start_exam/specialist_river', follow_redirects=True)
            response = client.get('/exam')
            
            print(f"HTTPステータス: {response.status_code}")
            print(f"レスポンスサイズ: {len(response.get_data())} bytes")
            
            if response.status_code == 200:
                print("OK 1問目画面アクセス成功")
                
                response_text = response.get_data(as_text=True)
                
                # 1問目表示の確認項目（CSRF対応版）
                checks = [
                    ("問題番号表示", "1" in response_text and ("/" in response_text or "問題" in response_text)),
                    ("問題文表示", "<h3>" in response_text or "問題" in response_text),
                    ("回答選択肢", 'type="radio"' in response_text or "選択" in response_text),
                    ("送信フォーム", "<form" in response_text and 'method="POST"' in response_text),
                    ("CSRFトークン", 'name="csrf_token"' in response_text),
                    ("河川分野表示", "河川" in response_text or "砂防" in response_text or "海岸" in response_text),
                    ("進捗表示", "1" in response_text and "10" in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                # 分野混在チェック（重要）
                river_categories = ["河川", "砂防", "海岸", "海洋"]
                field_mixing_check = any(cat in response_text for cat in river_categories)
                
                if field_mixing_check:
                    print("  OK 分野確認: 河川・砂防・海岸海洋分野表示確認")
                else:
                    print("  WARN 分野確認: 河川分野表示要確認")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 5 and field_mixing_check:
                    print("OK 9-3 PASS: 1問目表示正常（CSRF対応）")
                    return True, response_text
                else:
                    print("NG 9-3 FAIL: 1問目表示に問題")
                    return False, response_text
                    
            else:
                print(f"NG 9-3 FAIL: HTTPエラー {response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-3 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_river_question_transition():
    """9-4: 河川部門1問目から2問目遷移テスト（CSRF対応）"""
    print("=== 9-4: 河川部門1問目から2問目遷移テスト（CSRF対応） ===")
    print("目的: CSRF対応済み回答送信とセッション継続性確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_river', follow_redirects=True)
            
            # 1問目取得とCSRFトークン取得
            response1 = client.get('/exam')
            if response1.status_code != 200:
                print(f"NG 9-4 FAIL: 1問目取得失敗 {response1.status_code}")
                return False, ""
            
            response_text = response1.get_data(as_text=True)
            
            # CSRFトークン抽出
            import re
            token_match = re.search(r'name="csrf_token"\s+value="([^"]*)"', response_text)
            if not token_match:
                print("NG 9-4 FAIL: CSRFトークン取得失敗")
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
                print("OK 回答送信成功（CSRF対応効果確認）")
                
                response_text = response2.get_data(as_text=True)
                
                # セッション継続性の確認
                checks = [
                    ("フィードバック表示", "正解" in response_text or "不正解" in response_text or "解答" in response_text),
                    ("次問題表示", "次" in response_text or "2" in response_text),
                    ("セッション継続", "問題" in response_text and len(response_text) > 500),
                    ("河川分野維持", any(cat in response_text for cat in ["河川", "砂防", "海岸", "海洋"])),
                    ("CSRFエラー回避", "CSRF" not in response_text.upper() and "400" not in response_text)
                ]
                
                for check_name, result in checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in checks if result)
                if success_count >= 4:
                    print("OK 9-4 PASS: 1→2問目遷移成功（CSRF対応効果確認）")
                    return True, response_text
                else:
                    print("NG 9-4 FAIL: セッション継続に問題")
                    return False, response_text
                    
            else:
                print(f"NG 9-4 FAIL: 回答送信エラー {response2.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-4 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_river_full_10_question_sequence():
    """9-5: 河川部門2-9問目連続処理テスト（CSRF対応・分野混在チェック）"""
    print("=== 9-5: 河川部門2-9問目連続処理テスト（CSRF対応） ===")
    print("目的: CSRF対応でのセッション継続と河川分野混在チェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_river', follow_redirects=True)
            
            question_categories = []
            question_progression = []
            csrf_success_count = 0
            river_categories = ["河川", "砂防", "海岸", "海洋"]
            
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
                found_river_category = None
                for cat in river_categories:
                    if cat in response_text:
                        found_river_category = cat
                        break
                
                if found_river_category:
                    question_categories.append(found_river_category)
                    print(f"  OK 問題{q_num} カテゴリ: {found_river_category}")
                else:
                    # その他のカテゴリを検出
                    other_categories = ["道路", "都市計画", "造園", "建設環境", "鋼構造", "土質", "施工", "水道", "森林", "農業", "トンネル"]
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
            print("\\n--- 2-9問目連続処理結果分析（河川部門） ---")
            river_count = sum(1 for cat in question_categories if cat in river_categories)
            total_questions = len(question_categories)
            
            print(f"処理問題数: {total_questions}/8")
            print(f"河川関連カテゴリ問題: {river_count}/{total_questions}")
            print(f"分野混在問題: {total_questions - river_count}/{total_questions}")
            print(f"進捗表示正常: {sum(question_progression)}/{total_questions}")
            print(f"CSRF成功率: {csrf_success_count}/{total_questions} ({csrf_success_count/total_questions*100:.1f}%)")
            
            # 成功判定（河川分野対応・CSRF修正効果を考慮）
            if (river_count == total_questions and 
                sum(question_progression) >= total_questions * 0.8 and
                csrf_success_count >= total_questions * 0.9):
                print("OK 9-5 PASS: 2-9問目連続処理成功（河川部門・CSRF対応）")
                return True, {"categories": question_categories, "progression": question_progression, "csrf_success": csrf_success_count}
            else:
                print("NG 9-5 FAIL: 分野混在またはCSRF問題継続")
                return False, {"categories": question_categories, "progression": question_progression, "csrf_success": csrf_success_count}
                
    except Exception as e:
        print(f"NG 9-5 FAIL: 例外エラー - {str(e)}")
        return False, {}

def test_river_final_question_and_results():
    """9-6: 河川部門10問目最終回答処理テスト（CSRF対応）"""
    print("=== 9-6: 河川部門10問目最終回答処理テスト（CSRF対応） ===")
    print("目的: CSRF対応での結果画面への遷移確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # フルセッション実行（1-9問目）
            client.get('/start_exam/specialist_river', follow_redirects=True)
            
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
            print("--- 10問目最終処理（河川部門・CSRF対応） ---")
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
                river_categories = ["河川", "砂防", "海岸", "海洋"]
                result_checks = [
                    ("結果画面遷移", "結果" in final_text or "スコア" in final_text or "完了" in final_text),
                    ("10問完了表示", "10" in final_text),
                    ("河川部門表示", any(cat in final_text for cat in river_categories)),
                    ("統計情報表示", "正解" in final_text or "%" in final_text),
                    ("CSRFエラー回避", "400" not in final_text and "CSRF" not in final_text.upper())
                ]
                
                for check_name, result in result_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in result_checks if result)
                if success_count >= 4:
                    print("OK 9-6 PASS: 10問目処理と結果画面遷移成功（河川部門・CSRF対応）")
                    return True, final_text
                else:
                    print("NG 9-6 FAIL: 結果画面遷移に問題")
                    return False, final_text
            else:
                print(f"NG 9-6 FAIL: 最終回答エラー {final_response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-6 FAIL: 例外エラー - {str(e)}")
        return False, ""

def test_river_results_page_validation():
    """9-7: 河川部門最終結果画面表示確認（CSRF対応）"""
    print("=== 9-7: 河川部門最終結果画面表示確認（CSRF対応） ===")
    print("目的: CSRF対応でのスコア、部門名、統計情報のチェック")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 完全な10問セッション実行（CSRFトークン付き）
            client.get('/start_exam/specialist_river', follow_redirects=True)
            
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
                river_categories = ["河川", "砂防", "海岸", "海洋"]
                detailed_checks = [
                    ("河川部門名表示", any(cat in result_text for cat in river_categories)),
                    ("回答数表示", "10" in result_text),
                    ("正解数表示", "正解" in result_text or "score" in result_text.lower()),
                    ("正答率表示", "%" in result_text or "率" in result_text),
                    ("問題種別表示", "専門" in result_text or "4-2" in result_text),
                    ("完了メッセージ", "完了" in result_text or "終了" in result_text or "結果" in result_text),
                    ("日時情報", "2025" in result_text or "日" in result_text),
                    ("再挑戦リンク", "再" in result_text or "もう一度" in result_text or "戻る" in result_text),
                    ("CSRFエラー回避", "400" not in result_text and "CSRF" not in result_text.upper())
                ]
                
                print("--- 河川部門結果画面詳細チェック（CSRF対応） ---")
                for check_name, result in detailed_checks:
                    status = "OK" if result else "NG"
                    print(f"  {status} {check_name}: {result}")
                
                success_count = sum(1 for _, result in detailed_checks if result)
                success_rate = success_count / len(detailed_checks) * 100
                
                print(f"\\n結果画面品質（河川部門・CSRF対応）: {success_count}/{len(detailed_checks)} ({success_rate:.1f}%)")
                
                if success_count >= 7:
                    print("OK 9-7 PASS: 河川部門結果画面表示高品質（CSRF対応効果確認）")
                    return True, result_text
                elif success_count >= 5:
                    print("OK 9-7 PASS: 河川部門結果画面表示基本要件満足（CSRF対応効果あり）")
                    return True, result_text
                else:
                    print("NG 9-7 FAIL: 河川部門結果画面表示不十分")
                    return False, result_text
                    
            else:
                print(f"NG 9-7 FAIL: 結果画面アクセスエラー {result_response.status_code}")
                return False, ""
                
    except Exception as e:
        print(f"NG 9-7 FAIL: 例外エラー - {str(e)}")
        return False, ""

def run_comprehensive_river_test():
    """河川部門10問完走テスト実行メイン（CSRF対応・ブラッシュアップ版）"""
    print("=== 河川部門10問完走テスト開始（CSRF対応・ブラッシュアップ版） ===")
    print("=" * 80)
    print("方針: 道路部門で確認済みのCSRF修正効果を河川部門で検証")
    print("ブラッシュアップ: 河川・砂防・海岸・海洋分野の専門特化テスト")
    print("追加検証: CSRFトークン対応、分野混在ゼロ達成確認")
    print()
    
    results = {}
    test_data = {}
    
    # 9-1: アクセスルート確認
    success_9_1, response_9_1 = test_river_department_access()
    results['9-1'] = success_9_1
    test_data['9-1'] = response_9_1
    time.sleep(1)
    
    # 9-2: セッション初期化確認
    success_9_2, response_9_2 = test_river_department_session_initialization()
    results['9-2'] = success_9_2
    test_data['9-2'] = response_9_2
    time.sleep(1)
    
    # 9-3: 1問目表示確認（CSRF対応）
    success_9_3, response_9_3 = test_river_first_question_display()
    results['9-3'] = success_9_3
    test_data['9-3'] = response_9_3
    time.sleep(1)
    
    # 9-4: 問題遷移テスト（CSRF対応）
    success_9_4, response_9_4 = test_river_question_transition()
    results['9-4'] = success_9_4
    test_data['9-4'] = response_9_4
    time.sleep(1)
    
    # 9-5: 連続処理テスト（CSRF対応）
    success_9_5, data_9_5 = test_river_full_10_question_sequence()
    results['9-5'] = success_9_5
    test_data['9-5'] = data_9_5
    time.sleep(1)
    
    # 9-6: 最終問題処理テスト（CSRF対応）
    success_9_6, response_9_6 = test_river_final_question_and_results()
    results['9-6'] = success_9_6
    test_data['9-6'] = response_9_6
    time.sleep(1)
    
    # 9-7: 結果画面検証（CSRF対応）
    success_9_7, response_9_7 = test_river_results_page_validation()
    results['9-7'] = success_9_7
    test_data['9-7'] = response_9_7
    
    # 総合結果分析
    print("\\n" + "=" * 80)
    print("=== 河川部門10問完走テスト - CSRF対応総合結果分析 ===")
    print("=" * 80)
    
    total_tests = len(results)
    success_tests = sum(1 for success in results.values() if success)
    success_rate = (success_tests / total_tests) * 100
    
    print(f"実行済みテスト: {total_tests}/7 サブタスク（河川部門CSRF対応ブラッシュアップ版）")
    print(f"成功テスト: {success_tests}/{total_tests}")
    print(f"総合成功率（河川部門）: {success_rate:.1f}%")
    print()
    
    print("詳細結果:")
    for task_id, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {task_id}: {status}")
    
    # CSRF効果と分野混在分析
    if '9-5' in test_data and isinstance(test_data['9-5'], dict):
        csrf_success = test_data['9-5'].get('csrf_success', 0)
        categories = test_data['9-5'].get('categories', [])
        total_attempts = 8  # 2-9問目
        
        if csrf_success > 0:
            csrf_success_rate = csrf_success / total_attempts * 100
            print(f"\\nCSRF対応効果分析（河川部門）:")
            print(f"  CSRF成功率: {csrf_success_rate:.1f}% ({csrf_success}/{total_attempts})")
            if csrf_success_rate >= 90:
                print("  OK CSRF対応大成功（河川部門）")
            elif csrf_success_rate >= 70:
                print("  OK CSRF対応効果あり（河川部門）")
            else:
                print("  NG CSRF対応効果不十分（河川部門）")
        
        # 分野混在分析
        if categories:
            river_categories = ["河川", "砂防", "海岸", "海洋"]
            river_ratio = sum(1 for cat in categories if cat in river_categories) / len(categories) * 100
            print(f"\\n分野混在分析（河川部門）:")
            print(f"  河川関連問題率: {river_ratio:.1f}% ({sum(1 for cat in categories if cat in river_categories)}/{len(categories)})")
            if river_ratio == 100:
                print("  OK 分野混在ゼロ確認（河川部門）")
            else:
                print("  NG 分野混在問題検出（河川部門）")
    
    # 道路部門との比較
    print(f"\\n道路部門（Task 8-10）との比較:")
    print(f"  道路部門成功率: 42.9% (3/7サブタスク) - CSRF修正後")
    print(f"  河川部門成功率: {success_rate:.1f}% ({success_tests}/{total_tests}サブタスク) - CSRF対応済み")
    comparison = success_rate - 42.9
    print(f"  部門間比較: {comparison:+.1f}ポイント差")
    
    print()
    
    # 最終判定
    if success_tests >= 6:  # 7個中6個以上成功
        print("*** 河川部門10問完走テスト - 基本成功 ***")
        print(">>> Task 9 完了: 河川部門CSRF対応効果確認済み")
        
        if success_tests == total_tests:
            print("*** 完全成功：河川部門全サブタスクパス ***")
        
        return True
    elif success_tests >= 4:  # 7個中4個以上成功
        print("!!! 部分成功：河川部門でCSRF対応効果あり、残り問題要対応")
        print(">>> 追加修正後に再テスト推奨")
        return False
    else:
        print("!!! 河川部門でCSRF対応効果不十分：根本的な問題が継続")
        print(">>> システム根本的修正が必要")
        return False

if __name__ == "__main__":
    success = run_comprehensive_river_test()
    if success:
        print("\\nSUCCESS: Task 9 completed - 河川部門CSRF対応効果確認済み")
    else:
        print("\\nFAILED: Task 9 requires additional fixes")