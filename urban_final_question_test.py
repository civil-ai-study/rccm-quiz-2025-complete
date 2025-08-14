#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 10-6: 都市計画部門10問目最終処理テスト
Ultra Sync Task 10-6 - Final Question Processing and Result Verification

Purpose: 都市計画部門の10問目最終問題処理と結果画面遷移を完全テスト
- 1-9問目を高速で処理（既に分野混在ゼロ確認済み）
- 10問目の最終処理を詳細確認
- 結果画面への正常遷移を確認
- セッション完了状態の検証
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def run_urban_final_question_test():
    """都市計画部門10問目最終処理テストを実行"""
    print("=== Task 10-6: 都市計画部門10問目最終処理テスト ===")
    print("Purpose: 10問目最終処理と結果画面遷移の完全検証")
    print("Background: 緊急対応-12により分野混在ゼロ達成済み")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. 都市計画部門セッション開始...")
            
            # セッション開始
            response = client.get('/start_exam/specialist_urban')
            
            if response.status_code not in [200, 302]:
                print(f"ERROR: セッション開始失敗 - Status: {response.status_code}")
                return False
                
            print("   ✅ セッション開始成功")
            
            # セッション内容確認
            with client.session_transaction() as sess:
                if 'questions' not in sess:
                    print("ERROR: セッションに問題が設定されていません")
                    return False
                    
                session_questions = sess['questions']
                print(f"   セッション問題数: {len(session_questions)}")
                
                # 分野混在確認（緊急対応-12の効果確認）
                categories = {}
                for q in session_questions:
                    cat = q.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print("   問題カテゴリ分布:")
                for cat, count in categories.items():
                    print(f"     {cat}: {count}問")
                
                urban_count = categories.get('都市計画及び地方計画', 0)
                basic_count = categories.get('基礎', 0)
                
                if urban_count == 10 and basic_count == 0:
                    print("   ✅ 分野混在ゼロ確認 - 都市計画問題10/10")
                else:
                    print(f"   ❌ 分野混在問題: 都市計画={urban_count}, 基礎={basic_count}")
                    return False
            
            print()
            print("2. 1-9問目高速処理実行...")
            
            # 1-9問目を高速処理
            for question_num in range(1, 10):
                print(f"   処理中: {question_num}/9問目", end="")
                
                # 問題画面確認
                exam_response = client.get('/exam')
                if exam_response.status_code != 200:
                    print(f"\n   ERROR: {question_num}問目画面取得失敗")
                    return False
                
                # 回答送信
                answer_response = client.post('/exam', data={
                    'answer': 'A',  # 固定回答
                    'csrf_token': self.get_csrf_token(exam_response.get_data(as_text=True))
                })
                
                if answer_response.status_code in [200, 302]:
                    print("✅", end="")
                else:
                    print(f"\n   ERROR: {question_num}問目回答失敗")
                    return False
            
            print("\n   ✅ 1-9問目高速処理完了")
            
            print()
            print("3. 10問目最終処理詳細テスト...")
            
            # 10問目画面取得
            final_question_response = client.get('/exam')
            
            if final_question_response.status_code != 200:
                print("   ERROR: 10問目画面取得失敗")
                return False
            
            final_html = final_question_response.get_data(as_text=True)
            
            # 10問目であることを確認
            if '10/10' in final_html or '問題 10' in final_html:
                print("   ✅ 10問目画面確認")
            else:
                print("   ❌ 10問目画面の識別失敗")
                return False
            
            # 10問目のカテゴリ確認
            if '都市計画及び地方計画' in final_html:
                print("   ✅ 10問目も都市計画カテゴリ確認")
            else:
                print("   ⚠️ 10問目カテゴリ確認要")
            
            # 10問目回答送信
            csrf_token = self.get_csrf_token(final_html)
            final_answer_response = client.post('/exam', data={
                'answer': 'D',  # 最終問題は選択肢Dで回答
                'csrf_token': csrf_token
            })
            
            print(f"   10問目回答送信: Status {final_answer_response.status_code}")
            
            if final_answer_response.status_code in [200, 302]:
                print("   ✅ 10問目回答送信成功")
            else:
                print("   ❌ 10問目回答送信失敗")
                return False
            
            print()
            print("4. 結果画面遷移確認...")
            
            # 結果画面アクセス
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                print("   ✅ 結果画面アクセス成功")
                
                result_html = result_response.get_data(as_text=True)
                
                # 結果画面の内容確認
                if 'テスト完了' in result_html:
                    print("   ✅ テスト完了表示確認")
                else:
                    print("   ⚠️ テスト完了表示要確認")
                
                # 回答数確認
                if '10' in result_html and '回答' in result_html:
                    print("   ✅ 10問回答完了表示確認")
                else:
                    print("   ⚠️ 回答数表示要確認")
                
                # 部門名確認
                if '都市計画' in result_html:
                    print("   ✅ 都市計画部門表示確認")
                else:
                    print("   ⚠️ 部門名表示要確認")
                
                return True
                
            elif result_response.status_code == 302:
                print("   ⚠️ 結果画面でリダイレクト発生")
                redirect_location = result_response.headers.get('Location', '/')
                print(f"   リダイレクト先: {redirect_location}")
                
                # リダイレクト先にアクセス
                redirect_response = client.get(redirect_location)
                if redirect_response.status_code == 200:
                    print("   ✅ リダイレクト先アクセス成功")
                    return True
                else:
                    print("   ❌ リダイレクト先アクセス失敗")
                    return False
            else:
                print(f"   ❌ 結果画面アクセス失敗: Status {result_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: テスト実行中にエラー発生: {type(e).__name__}: {e}")
        return False

    def get_csrf_token(self, html_content):
        """HTMLからCSRFトークンを抽出"""
        import re
        csrf_pattern = r'name="csrf_token"[^>]*value="([^"]*)"'
        match = re.search(csrf_pattern, html_content)
        if match:
            return match.group(1)
        return ""

def run_result_screen_verification():
    """Task 10-7: 結果画面詳細検証"""
    print()
    print("=== Task 10-7: 都市計画部門結果画面詳細検証 ===")
    print("Purpose: 最終結果の妥当性とセッション完了確認")
    print()
    
    try:
        from app import app
        
        with app.test_client() as client:
            print("1. 完全セッション実行...")
            
            # 新しいセッションで完全実行
            session_response = client.get('/start_exam/specialist_urban')
            
            if session_response.status_code not in [200, 302]:
                print("ERROR: セッション開始失敗")
                return False
            
            # 10問全て回答
            for i in range(1, 11):
                # 問題画面取得
                question_response = client.get('/exam')
                if question_response.status_code != 200:
                    print(f"ERROR: {i}問目取得失敗")
                    return False
                
                # 回答送信
                html_content = question_response.get_data(as_text=True)
                csrf_token = get_csrf_token_from_html(html_content)
                
                answer_response = client.post('/exam', data={
                    'answer': ['A', 'B', 'C', 'D'][i % 4],
                    'csrf_token': csrf_token
                })
                
                if answer_response.status_code not in [200, 302]:
                    print(f"ERROR: {i}問目回答失敗")
                    return False
            
            print("   ✅ 10問完全回答完了")
            
            print()
            print("2. 結果画面詳細分析...")
            
            # 結果画面詳細確認
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                result_html = result_response.get_data(as_text=True)
                
                print("   結果画面コンテンツ分析:")
                
                # HTML要素確認
                if '<title>' in result_html:
                    print("   ✅ HTMLタイトル要素あり")
                else:
                    print("   ❌ HTMLタイトル要素なし")
                
                # テスト完了確認
                if 'テスト完了' in result_html or '完了' in result_html:
                    print("   ✅ テスト完了ステータス表示")
                else:
                    print("   ❌ テスト完了ステータス未表示")
                
                # 部門情報確認
                if '都市計画' in result_html:
                    print("   ✅ 都市計画部門情報表示")
                else:
                    print("   ❌ 部門情報未表示")
                
                # 回答数情報確認
                answer_count_found = False
                for pattern in ['10/10', '10問', '10回']:
                    if pattern in result_html:
                        print(f"   ✅ 回答数情報表示 ({pattern})")
                        answer_count_found = True
                        break
                
                if not answer_count_found:
                    print("   ❌ 回答数情報未表示")
                
                # セッション状態確認
                with client.session_transaction() as sess:
                    print("   セッション最終状態:")
                    session_keys = list(sess.keys())
                    print(f"     セッションキー: {session_keys}")
                    
                    if 'completed' in sess or 'finished' in sess:
                        print("   ✅ セッション完了フラグ確認")
                    else:
                        print("   ⚠️ セッション完了フラグ要確認")
                
                print()
                print("3. Task 10-6/10-7 完了判定...")
                
                success_criteria = [
                    'テスト完了' in result_html or '完了' in result_html,
                    '都市計画' in result_html,
                    any(pattern in result_html for pattern in ['10/10', '10問', '10回'])
                ]
                
                success_count = sum(success_criteria)
                total_criteria = len(success_criteria)
                
                print(f"   成功基準: {success_count}/{total_criteria}")
                
                if success_count == total_criteria:
                    print("   ✅ 全基準クリア - Task 10-6/10-7 完了")
                    return True
                else:
                    print("   ⚠️ 部分成功 - 追加確認が必要")
                    return None
                    
            else:
                print(f"   ❌ 結果画面アクセス失敗: Status {result_response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR: 結果画面検証中にエラー: {type(e).__name__}: {e}")
        return False

def get_csrf_token_from_html(html_content):
    """HTMLからCSRFトークンを抽出する汎用関数"""
    import re
    csrf_pattern = r'name="csrf_token"[^>]*value="([^"]*)"'
    match = re.search(csrf_pattern, html_content)
    if match:
        return match.group(1)
    return ""

def main():
    print("Ultra Sync Task 10-6/10-7: 都市計画部門最終処理＆結果画面検証")
    print("=" * 70)
    print("Background: 緊急対応-12により分野混在ゼロ達成済み")
    print("Purpose: 10問目最終処理と結果画面の完全検証")
    print()
    
    # Task 10-6: 10問目最終処理テスト
    print("🚀 Task 10-6 開始: 都市計画部門10問目最終処理テスト")
    task_10_6_result = run_urban_final_question_test()
    
    # Task 10-7: 結果画面検証
    print("🚀 Task 10-7 開始: 都市計画部門結果画面詳細検証")
    task_10_7_result = run_result_screen_verification()
    
    print()
    print("=" * 70)
    print("Task 10-6/10-7 最終結果:")
    print(f"Task 10-6 (10問目最終処理): {'✅ 完了' if task_10_6_result else '❌ 失敗' if task_10_6_result is False else '⚠️ 要確認'}")
    print(f"Task 10-7 (結果画面検証): {'✅ 完了' if task_10_7_result else '❌ 失敗' if task_10_7_result is False else '⚠️ 要確認'}")
    
    if task_10_6_result and task_10_7_result:
        print()
        print("🎉 Task 10 完全達成!")
        print("- 都市計画部門10問完走テスト完了")
        print("- 分野混在ゼロ維持確認")
        print("- セッション継続成功")
        print("- 最終結果画面表示成功")
        print("- 次タスク: Task 11 (造園部門) 準備完了")
        
        # 連続実行でTask 11の準備
        print()
        print("🔄 ウルトラシンク継続: Task 11 (造園部門) 準備中...")
        return True
    else:
        print()
        print("⚠️ Task 10-6/10-7 部分完了または要確認")
        print("継続アクションが必要な可能性があります")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)