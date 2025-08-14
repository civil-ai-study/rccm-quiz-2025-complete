#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク Task 8-8: 重大なシステム問題の緊急診断
目的: 道路部門10問完走テスト失敗の根本原因を特定し、緊急修正が必要な箇所を明確化
判明した問題: 分野混在（基礎科目が道路部門に混入）+ 400 Bad Request（フォーム送信問題）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def diagnose_field_mixing_issue():
    """分野混在問題の詳細診断"""
    print("=== 緊急診断1: 分野混在問題詳細分析 ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 道路部門セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"HTTPステータス: {response.status_code}")
            
            # 分野混在の詳細確認
            category_matches = []
            department_matches = []
            
            if "カテゴリ: 共通" in response_text:
                category_matches.append("基礎科目問題が混入")
                print("NG 重大問題: 基礎科目問題が道路部門に混入している")
            
            if "カテゴリ: 道路" in response_text:
                category_matches.append("道路問題正常")
                print("OK 道路問題確認")
            
            # 問題文から分野を推測
            if "測量" in response_text or "縮尺" in response_text or "座標" in response_text:
                department_matches.append("基礎科目系問題文")
                print("NG 問題文内容: 基礎科目系問題文検出")
            
            if "道路" in response_text or "舗装" in response_text or "交通" in response_text:
                department_matches.append("道路系問題文")
                print("OK 問題文内容: 道路系問題文検出")
            
            print(f"\n分野混在診断結果:")
            print(f"  カテゴリ表示問題: {len(category_matches)}件")
            print(f"  問題文内容問題: {len(department_matches)}件")
            
            return len(category_matches) == 1 and category_matches[0] == "基礎科目問題が混入"
            
    except Exception as e:
        print(f"分野混在診断エラー: {str(e)}")
        return False

def diagnose_form_submission_issue():
    """フォーム送信問題の詳細診断"""
    print("\n=== 緊急診断2: フォーム送信問題詳細分析 ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # セッション開始
            client.get('/start_exam/specialist_road', follow_redirects=True)
            
            # 問題画面取得
            response = client.get('/exam')
            response_text = response.get_data(as_text=True)
            
            print(f"HTMLフォーム詳細診断:")
            
            # フォーム要素の存在確認
            form_elements = []
            
            if '<form' in response_text:
                form_elements.append("form_tag_exists")
                print("OK <form>タグ存在")
            else:
                print("NG <form>タグ不存在")
            
            if 'method="post"' in response_text or "method='post'" in response_text:
                form_elements.append("post_method_exists")
                print("OK POST method設定")
            else:
                print("NG POST method未設定")
            
            if 'action="/exam"' in response_text or "action='/exam'" in response_text:
                form_elements.append("action_correct")
                print("OK action属性正常")
            else:
                print("NG action属性問題")
            
            if 'type="radio"' in response_text:
                form_elements.append("radio_buttons_exist")
                print("OK ラジオボタン存在")
            else:
                print("NG ラジオボタン不存在")
            
            if 'name="answer"' in response_text:
                form_elements.append("answer_name_exists")
                print("OK name=\"answer\"存在")
            else:
                print("NG name=\"answer\"不存在")
            
            if 'type="submit"' in response_text or 'input.*submit' in response_text or '<button' in response_text:
                form_elements.append("submit_button_exists")
                print("OK 送信ボタン存在")
            else:
                print("NG 送信ボタン不存在")
            
            # CSRFトークンチェック
            if 'csrf_token' in response_text or 'name="csrf"' in response_text:
                form_elements.append("csrf_token_exists")
                print("OK CSRFトークン存在")
            else:
                print("WARN CSRFトークン未確認")
            
            print(f"\nフォーム送信診断結果:")
            print(f"  フォーム要素数: {len(form_elements)}/7")
            print(f"  要素詳細: {form_elements}")
            
            # 実際のPOST送信テスト
            print("\n実際のPOST送信テスト:")
            post_data = {
                'answer': 'A',
                'question_id': '1'
            }
            
            post_response = client.post('/exam', data=post_data, follow_redirects=True)
            print(f"POST結果: {post_response.status_code}")
            
            if post_response.status_code == 400:
                print("NG 400 Bad Request継続")
                error_text = post_response.get_data(as_text=True)
                if "CSRF" in error_text.upper():
                    print("原因: CSRF問題の可能性")
                elif "Missing" in error_text or "required" in error_text.lower():
                    print("原因: 必須パラメータ不足")
                else:
                    print(f"原因: 不明 - {error_text[:100]}...")
            else:
                print(f"OK POST成功: {post_response.status_code}")
            
            return len(form_elements) >= 5, post_response.status_code == 400
            
    except Exception as e:
        print(f"フォーム送信診断エラー: {str(e)}")
        return False, True

def diagnose_system_integration_issue():
    """システム統合問題の診断"""
    print("\n=== 緊急診断3: LIGHTWEIGHT_DEPARTMENT_MAPPING問題分析 ===")
    
    try:
        # app.pyファイル読み込み
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # LIGHTWEIGHT_DEPARTMENT_MAPPINGの使用状況確認
        lightweight_usage_count = app_content.count('LIGHTWEIGHT_DEPARTMENT_MAPPING')
        print(f"LIGHTWEIGHT_DEPARTMENT_MAPPING使用箇所: {lightweight_usage_count}箇所")
        
        # start_examルーティング確認
        if 'start_exam/specialist_road' in app_content:
            print("OK start_exam/specialist_roadルート存在")
        else:
            print("NG start_exam/specialist_roadルート不存在")
        
        # 部門フィルタリング処理確認
        if 'road' in app_content and 'specialist' in app_content:
            print("OK road/specialist関連処理存在")
        else:
            print("NG road/specialist関連処理問題")
        
        # 問題フィルタリング処理の確認
        filter_patterns = [
            'category =',
            'department =',
            'filter',
            'questions = ['
        ]
        
        filter_count = 0
        for pattern in filter_patterns:
            if pattern in app_content:
                filter_count += 1
        
        print(f"フィルタリング処理要素: {filter_count}/4")
        
        if lightweight_usage_count > 50:
            print("判定: LIGHTWEIGHT_DEPARTMENT_MAPPING過剰使用 - システム統合問題")
            return True
        else:
            print("判定: LIGHTWEIGHT_DEPARTMENT_MAPPING使用量正常")
            return False
            
    except Exception as e:
        print(f"システム統合診断エラー: {str(e)}")
        return False

def run_critical_system_diagnosis():
    """重大システム問題の総合診断実行"""
    print("=== ウルトラシンク緊急システム診断開始 ===")
    print("対象: 道路部門10問完走テスト失敗の根本原因")
    print("問題: 28.6%成功率、5つのサブタスク失敗")
    print("=" * 70)
    
    # 診断1: 分野混在問題
    field_mixing_problem = diagnose_field_mixing_issue()
    
    # 診断2: フォーム送信問題  
    form_ok, form_400_error = diagnose_form_submission_issue()
    
    # 診断3: システム統合問題
    integration_problem = diagnose_system_integration_issue()
    
    print("\n" + "=" * 70)
    print("=== 緊急システム診断結果サマリー ===")
    print("=" * 70)
    
    critical_issues = []
    
    if field_mixing_problem:
        critical_issues.append("分野混在問題")
        print("NG 重大問題1: 分野混在問題確認 - 基礎科目が道路部門に混入")
    
    if form_400_error:
        critical_issues.append("フォーム送信400エラー")
        print("NG 重大問題2: フォーム送信400エラー確認 - POST処理失敗")
    
    if integration_problem:
        critical_issues.append("システム統合問題")
        print("NG 重大問題3: LIGHTWEIGHT_DEPARTMENT_MAPPING統合問題")
    
    print(f"\n検出された重大問題数: {len(critical_issues)}")
    print(f"重大問題リスト: {critical_issues}")
    
    # 修正優先順位の決定
    print(f"\n=== 緊急修正優先順位 ===")
    if field_mixing_problem:
        print("優先度1: 分野混在問題の修正（最重要）")
        print("  -> LIGHTWEIGHT_DEPARTMENT_MAPPINGの問題フィルタリング修正")
    
    if form_400_error:
        print("優先度2: フォーム送信400エラーの修正")
        print("  -> CSRFトークン問題またはフォーム構造修正")
    
    if integration_problem:
        print("優先度3: システム統合問題の修正")
        print("  -> LIGHTWEIGHT_DEPARTMENT_MAPPING過剰使用の削減")
    
    # 緊急アクション判定
    if len(critical_issues) >= 2:
        print(f"\n!!! 緊急アクション必要 !!!")
        print(f"複数の重大問題が検出されました。システム根本修正が必要です。")
        return False
    elif len(critical_issues) == 1:
        print(f"\n!!! 部分的修正が必要 !!!")
        print(f"1つの重大問題が検出されました。修正後にテスト再実行してください。")
        return False
    else:
        print(f"\nシステム診断: 大きな問題は検出されませんでした")
        return True

if __name__ == "__main__":
    system_healthy = run_critical_system_diagnosis()
    
    if not system_healthy:
        print("\n" + "=" * 70)
        print("!!! ウルトラシンク Task 8-8 結論 !!!")
        print("重大なシステム問題が確認されました。")
        print("Task 8-9（緊急システム修正）の実行が必要です。")
        print("=" * 70)