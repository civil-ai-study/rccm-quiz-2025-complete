#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急対応-13: 造園部門CSRFトークン問題詳細診断
Ultra Sync Emergency Fix 13 - Garden Department CSRF Token Problem Diagnosis

Purpose: 造園部門のCSRFトークン問題と10問目識別エラーの根本原因を特定し修正
- CSRFトークン取得・送信プロセスの詳細分析
- セッション継続システムの診断
- 10問目識別システムの問題点特定
- 完全な修正方針の策定
"""

import sys
import os
import re

# Set path to access app module
if 'rccm-quiz-app' not in sys.path:
    sys.path.insert(0, os.path.join(os.getcwd(), 'rccm-quiz-app'))

# Ensure working directory is correct
if not os.path.exists('app.py'):
    os.chdir('rccm-quiz-app')

def run_csrf_token_diagnosis():
    """CSRFトークン問題の詳細診断"""
    print("=== 緊急対応-13: CSRFトークン問題詳細診断 ===")
    print("Purpose: 造園部門のCSRFトークン取得・送信プロセス分析")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. 造園部門セッション開始テスト...")
            
            # セッション開始
            start_response = client.get('/start_exam/specialist_garden')
            print(f"   セッション開始ステータス: {start_response.status_code}")
            
            if start_response.status_code in [200, 302]:
                print("   ✅ セッション開始成功")
                
                print()
                print("2. 1問目画面でのCSRFトークン詳細分析...")
                
                # 1問目画面取得
                exam_response = client.get('/exam')
                print(f"   1問目画面ステータス: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    html_content = exam_response.get_data(as_text=True)
                    print(f"   HTML内容長: {len(html_content)} 文字")
                    
                    # CSRFトークン詳細確認
                    csrf_patterns = [
                        'name="csrf_token"',
                        'value=',
                        'type="hidden"',
                        'csrf_token'
                    ]
                    
                    print("   CSRFトークン要素確認:")
                    for pattern in csrf_patterns:
                        if pattern in html_content:
                            print(f"     ✅ {pattern}: 存在")
                        else:
                            print(f"     ❌ {pattern}: 不存在")
                    
                    # CSRFトークン値抽出テスト
                    import re
                    csrf_pattern = r'name="csrf_token"[^>]*value="([^"]*)"'
                    csrf_match = re.search(csrf_pattern, html_content)
                    
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        print(f"   ✅ CSRFトークン抽出成功: {csrf_token[:20]}...")
                        print(f"   CSRFトークン長: {len(csrf_token)} 文字")
                        
                        print()
                        print("3. CSRFトークン送信テスト...")
                        
                        # 正常なCSRFトークンでPOST送信
                        answer_response = client.post('/exam', data={
                            'answer': 'A',
                            'csrf_token': csrf_token
                        })
                        
                        print(f"   回答送信ステータス: {answer_response.status_code}")
                        
                        if answer_response.status_code == 200:
                            print("   ✅ CSRF送信成功 - 200番台レスポンス")
                            
                            # レスポンス内容確認
                            response_html = answer_response.get_data(as_text=True)
                            print(f"   回答後HTML長: {len(response_html)} 文字")
                            
                            # 2問目遷移確認
                            if '2/10' in response_html or '問題 2' in response_html:
                                print("   ✅ 2問目遷移正常 - セッション継続確認")
                                return True
                            else:
                                print("   ❌ 2問目遷移失敗 - セッション継続問題")
                                print("   詳細分析が必要:")
                                print(f"     レスポンス内容(最初200文字): {response_html[:200]}")
                                return False
                                
                        elif answer_response.status_code == 302:
                            print("   ⚠️ CSRF送信でリダイレクト発生")
                            redirect_location = answer_response.headers.get('Location', 'unknown')
                            print(f"   リダイレクト先: {redirect_location}")
                            return None
                            
                        else:
                            print(f"   ❌ CSRF送信エラー - ステータス {answer_response.status_code}")
                            return False
                            
                    else:
                        print("   ❌ CSRFトークン抽出失敗")
                        print("   HTML内容(CSRFトークン周辺):")
                        csrf_context = re.search(r'.{0,100}csrf.{0,100}', html_content, re.IGNORECASE)
                        if csrf_context:
                            print(f"     {csrf_context.group()}")
                        return False
                        
                else:
                    print(f"   ❌ 1問目画面取得失敗 - ステータス {exam_response.status_code}")
                    return False
                    
            else:
                print(f"   ❌ セッション開始失敗 - ステータス {start_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: CSRF診断中にエラー発生: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tenth_question_diagnosis():
    """10問目識別問題の詳細診断"""
    print()
    print("=== 10問目識別システム詳細診断 ===")
    print("Purpose: 10問目識別エラーの根本原因特定")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. 造園部門完全セッション実行...")
            
            # セッション開始
            client.get('/start_exam/specialist_garden')
            
            # 1-9問目高速実行
            for i in range(1, 10):
                print(f"   問題{i}処理中...", end="")
                
                # 問題画面取得
                exam_response = client.get('/exam')
                if exam_response.status_code != 200:
                    print(f"ERROR: 問題{i}画面取得失敗")
                    return False
                
                # CSRFトークン取得・回答送信
                html_content = exam_response.get_data(as_text=True)
                csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', html_content)
                
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    answer_response = client.post('/exam', data={
                        'answer': ['A', 'B', 'C', 'D'][i % 4],
                        'csrf_token': csrf_token
                    })
                    
                    if answer_response.status_code in [200, 302]:
                        print("OK", end="")
                    else:
                        print(f"ERROR({answer_response.status_code})", end="")
                        return False
                else:
                    print("CSRF_ERROR", end="")
                    return False
                    
                print(f"({i}/9)")
            
            print("   1-9問目完了")
            
            print()
            print("2. 10問目詳細分析...")
            
            # 10問目画面取得
            tenth_response = client.get('/exam')
            print(f"   10問目画面ステータス: {tenth_response.status_code}")
            
            if tenth_response.status_code == 200:
                tenth_html = tenth_response.get_data(as_text=True)
                print(f"   10問目HTML長: {len(tenth_html)} 文字")
                
                # 問題番号識別パターン確認
                identification_patterns = [
                    ('10/10', '10/10パターン'),
                    ('問題 10', '問題 10パターン'),
                    ('問題10', '問題10パターン'),
                    ('10問目', '10問目パターン'),
                    ('最終問題', '最終問題パターン')
                ]
                
                print("   10問目識別パターン確認:")
                found_patterns = []
                for pattern, description in identification_patterns:
                    if pattern in tenth_html:
                        print(f"     ✅ {description}: 検出")
                        found_patterns.append(pattern)
                    else:
                        print(f"     ❌ {description}: 未検出")
                
                if found_patterns:
                    print(f"   ✅ 識別成功: {len(found_patterns)}個のパターンで10問目確認")
                    
                    # セッション状態確認
                    with client.session_transaction() as sess:
                        print("   セッション状態確認:")
                        if 'questions' in sess:
                            questions = sess['questions']
                            current_index = sess.get('quiz_current', 0)
                            print(f"     セッション問題数: {len(questions)}")
                            print(f"     現在のインデックス: {current_index}")
                            print(f"     期待される問題番号: {current_index + 1}")
                            
                            if current_index == 9:  # 0-based index
                                print("     ✅ セッション状態正常 - 10問目(index 9)")
                                return True
                            else:
                                print(f"     ❌ セッション状態異常 - index {current_index}")
                                return False
                        else:
                            print("     ❌ セッションに問題データなし")
                            return False
                else:
                    print("   ❌ 10問目識別完全失敗")
                    print("   HTML内容(最初500文字):")
                    print(f"     {tenth_html[:500]}")
                    return False
                    
            else:
                print(f"   ❌ 10問目画面取得失敗 - ステータス {tenth_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: 10問目診断中にエラー発生: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_session_state_diagnosis():
    """セッション状態管理システム診断"""
    print()
    print("=== セッション状態管理システム診断 ===")
    print("Purpose: セッション継続・状態管理の詳細分析")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. セッション初期化確認...")
            
            # セッション開始
            client.get('/start_exam/specialist_garden')
            
            with client.session_transaction() as sess:
                print("   初期セッション状態:")
                session_keys = list(sess.keys())
                print(f"     セッションキー: {session_keys}")
                
                if 'questions' in sess:
                    questions = sess['questions']
                    print(f"     問題数: {len(questions)}")
                    print(f"     現在位置: {sess.get('quiz_current', '未設定')}")
                    print(f"     セッションID: {sess.get('exam_id', '未設定')}")
                    
                    # 造園部門問題であることを確認
                    if questions:
                        sample_question = questions[0]
                        category = sample_question.get('category', 'unknown')
                        print(f"     カテゴリ確認: {category}")
                        
                        if category == '造園':
                            print("     ✅ 造園部門問題確認")
                        else:
                            print(f"     ❌ 分野混在エラー: {category}")
                            return False
                    
                    print()
                    print("2. セッション継続テスト...")
                    
                    # 3問連続でセッション状態を確認
                    for i in range(1, 4):
                        print(f"   問題{i}でのセッション状態:")
                        
                        # 問題画面取得
                        exam_response = client.get('/exam')
                        
                        with client.session_transaction() as sess:
                            current_index = sess.get('quiz_current', -1)
                            expected_index = i - 1  # 0-based
                            print(f"     現在index: {current_index}, 期待index: {expected_index}")
                            
                            if current_index == expected_index:
                                print(f"     ✅ 問題{i}: セッション状態正常")
                            else:
                                print(f"     ❌ 問題{i}: セッション状態異常")
                                return False
                        
                        # 回答送信でセッション状態更新
                        html_content = exam_response.get_data(as_text=True)
                        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', html_content)
                        
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            client.post('/exam', data={
                                'answer': 'A',
                                'csrf_token': csrf_token
                            })
                    
                    print("   ✅ セッション継続テスト完了")
                    return True
                    
                else:
                    print("     ❌ セッションに問題データが設定されていない")
                    return False
                    
    except Exception as e:
        print(f"ERROR: セッション診断中にエラー発生: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("緊急対応-13: 造園部門CSRFトークン問題と10問完走テスト詳細診断")
    print("=" * 80)
    print("Background: 造園部門で10問目識別エラーとCSRFトークン問題が発生")
    print("Purpose: 根本原因特定と完全修正方針策定")
    print()
    
    # 診断結果収集
    diagnosis_results = {}
    
    # Task 13-1: CSRFトークン問題診断
    print(">>> Task 13-1 Starting: CSRFトークン問題詳細診断")
    diagnosis_results['csrf'] = run_csrf_token_diagnosis()
    
    # Task 13-2: 10問目識別問題診断
    print(">>> Task 13-2 Starting: 10問目識別システム詳細診断")
    diagnosis_results['tenth_question'] = run_tenth_question_diagnosis()
    
    # Task 13-3: セッション状態管理診断
    print(">>> Task 13-3 Starting: セッション状態管理システム診断")
    diagnosis_results['session_state'] = run_session_state_diagnosis()
    
    print()
    print("=" * 80)
    print("緊急対応-13 詳細診断結果:")
    
    # 結果分析
    success_count = 0
    total_tests = len(diagnosis_results)
    
    for test_name, result in diagnosis_results.items():
        if result is True:
            print(f"✅ {test_name}: 正常動作確認")
            success_count += 1
        elif result is False:
            print(f"❌ {test_name}: 問題確認 - 修正必要")
        else:
            print(f"⚠️ {test_name}: 部分的問題 - 調査継続")
    
    print()
    print(f"診断結果サマリー: {success_count}/{total_tests} 項目で正常動作")
    
    if success_count == total_tests:
        print()
        print("🎉 緊急対応-13 診断完了: 造園部門システム正常動作確認")
        print("- CSRFトークンシステム: 正常")
        print("- 10問目識別システム: 正常")
        print("- セッション状態管理: 正常")
        print("- 次ステップ: 完全10問完走テスト実行")
        return True
    elif success_count >= 2:
        print()
        print("⚠️ 緊急対応-13 診断: 部分的問題確認")
        print("- 大部分のシステムは正常動作")
        print("- 特定箇所の修正が必要")
        print("- 次ステップ: 問題箇所の根本修正適用")
        return None
    else:
        print()
        print("❌ 緊急対応-13 診断: 重大な問題確認")
        print("- 複数のシステムで問題発生")
        print("- 包括的な修正が必要")
        print("- 次ステップ: 緊急修正システム適用")
        return False

if __name__ == "__main__":
    # Fix encoding issues for Windows console
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    
    success = main()
    sys.exit(0 if success else 1)