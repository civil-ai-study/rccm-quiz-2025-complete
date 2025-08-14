#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急対応-13: 造園部門CSRFトークン問題緊急修正システム
Ultra Sync Emergency Fix 13 - Garden Department CSRF Token Problem Complete Fix

Purpose: 造園部門で発見されたCSRFトークン完全欠如問題の緊急修正
- HTMLテンプレートにCSRFトークンフィールド追加
- セッション状態管理システム修正
- 10問完走テスト実行環境構築

Critical Issues Identified:
1. CSRFトークンが全くHTML内に存在しない
2. セッション内に問題データが設定されていない
3. フォーム送信処理でCSRF検証が正常動作しない
"""

import sys
import os
import shutil
import time
import re

# Ensure correct path and directory
if not os.path.exists('app.py'):
    if os.path.exists('rccm-quiz-app'):
        os.chdir('rccm-quiz-app')
    else:
        print("ERROR: Cannot find app.py or rccm-quiz-app directory")
        sys.exit(1)

def diagnose_csrf_template_system():
    """CSRFトークンテンプレートシステムの診断"""
    print("=== CSRFトークンテンプレートシステム診断 ===")
    print("Purpose: HTMLテンプレート内のCSRFトークン実装状況確認")
    print()
    
    # exam.htmlテンプレートを確認
    exam_template_path = 'templates/exam.html'
    
    if os.path.exists(exam_template_path):
        print("1. exam.htmlテンプレート確認...")
        
        with open(exam_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        print(f"   テンプレート長: {len(template_content)} 文字")
        
        # CSRFトークン関連要素を検索
        csrf_patterns = [
            ('csrf_token()', 'Flask-WTF CSRFトークン関数'),
            ('{{ csrf_token() }}', 'CSRFトークン出力'),
            ('name="csrf_token"', 'CSRFトークンフィールド名'),
            ('<input type="hidden"', 'Hidden inputフィールド'),
            ('csrf', '任意のCSRF関連記述'),
        ]
        
        csrf_found = False
        print("   CSRFトークン要素検索:")
        for pattern, description in csrf_patterns:
            if pattern in template_content:
                print(f"     SUCCESS {description}: 発見")
                csrf_found = True
            else:
                print(f"     MISSING {description}: 不存在")
        
        if not csrf_found:
            print("   CRITICAL: CSRFトークンが全くテンプレートに実装されていない")
            print("   詳細: フォーム内容確認")
            
            # フォーム要素を探す
            form_match = re.search(r'<form[^>]*>(.*?)</form>', template_content, re.DOTALL)
            if form_match:
                form_content = form_match.group(1)
                print(f"     フォーム内容長: {len(form_content)} 文字")
                print("     フォーム内容(最初200文字):")
                print(f"     {form_content[:200]}...")
            else:
                print("     ERROR: フォーム要素が見つかりません")
        
        return csrf_found
    else:
        print(f"   ERROR: テンプレートファイルが見つかりません: {exam_template_path}")
        return False

def apply_csrf_template_fix():
    """CSRFトークンテンプレート修正の適用"""
    print()
    print("=== CSRFトークンテンプレート修正適用 ===")
    
    exam_template_path = 'templates/exam.html'
    
    if not os.path.exists(exam_template_path):
        print("ERROR: exam.htmlテンプレートが見つかりません")
        return False
    
    try:
        # バックアップ作成
        backup_path = f'{exam_template_path}.emergency_csrf_backup_{int(time.time())}'
        shutil.copy(exam_template_path, backup_path)
        print(f"1. バックアップ作成: {backup_path}")
        
        # 現在のテンプレート内容を読み込み
        with open(exam_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        print("2. CSRFトークンフィールド追加...")
        
        # フォーム内にCSRFトークンを追加
        csrf_field = '        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'
        
        # フォーム開始タグの直後にCSRFトークンを挿入
        form_pattern = r'(<form[^>]*>\s*)'
        if re.search(form_pattern, template_content):
            updated_content = re.sub(
                form_pattern,
                r'\1\n' + csrf_field + '\n',
                template_content
            )
            
            print("   SUCCESS: フォーム開始直後にCSRFトークンフィールド追加")
        else:
            print("   ERROR フォーム開始タグが見つかりませんでした")
            return False
        
        # 修正されたテンプレートを保存
        with open(exam_template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("3. 修正内容確認...")
        
        # 修正が適用されたか確認
        with open(exam_template_path, 'r', encoding='utf-8') as f:
            updated_template = f.read()
        
        if 'csrf_token()' in updated_template and 'name="csrf_token"' in updated_template:
            print("   SUCCESS CSRFトークンフィールドが正常に追加されました")
            return True
        else:
            print("   ERROR CSRFトークンフィールドの追加に失敗しました")
            # バックアップを復元
            shutil.copy(backup_path, exam_template_path)
            print(f"   バックアップを復元: {backup_path}")
            return False
            
    except Exception as e:
        print(f"ERROR: テンプレート修正中にエラー: {e}")
        return False

def apply_session_management_fix():
    """セッション状態管理システム修正の適用"""
    print()
    print("=== セッション状態管理システム修正適用 ===")
    
    try:
        # app.pyを読み込み
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        print("1. セッション初期化処理確認...")
        
        # start_examルートの処理を確認
        start_exam_pattern = r'@app\.route\(["\']\/start_exam\/<path:exam_type>["\'].*?\ndef\s+start_exam.*?return'
        start_exam_match = re.search(start_exam_pattern, app_content, re.DOTALL)
        
        if start_exam_match:
            start_exam_function = start_exam_match.group(0)
            print(f"   start_exam関数確認: {len(start_exam_function)} 文字")
            
            # セッション設定処理を確認
            if 'session[' in start_exam_function:
                print("   SUCCESS セッション設定処理が存在します")
                
                # questionsセッション設定を確認
                if "session['questions']" in start_exam_function:
                    print("   SUCCESS questionsセッション設定が存在します")
                    return True
                else:
                    print("   ERROR questionsセッション設定が不足しています")
                    print("   修正が必要: questionsをセッションに設定する処理を追加")
                    
                    # セッション設定の修正
                    questions_session_fix = """
        # EMERGENCY FIX 13: Ensure questions are properly stored in session
        session['questions'] = selected_questions
        session['quiz_current'] = 0
        session['quiz_total'] = len(selected_questions)
        logger.info(f"EMERGENCY FIX 13: Session questions set: {len(selected_questions)}")
        """
                    
                    # redirect前にセッション設定を追加
                    redirect_pattern = r'(return redirect\([^)]+\))'
                    if re.search(redirect_pattern, start_exam_function):
                        updated_function = re.sub(
                            redirect_pattern,
                            questions_session_fix + r'\n        \1',
                            start_exam_function
                        )
                        
                        # app.py全体を更新
                        updated_app_content = app_content.replace(start_exam_function, updated_function)
                        
                        # バックアップ作成
                        backup_path = f'app.py.emergency_session_fix_{int(time.time())}'
                        shutil.copy('app.py', backup_path)
                        print(f"   バックアップ作成: {backup_path}")
                        
                        # 修正を適用
                        with open('app.py', 'w', encoding='utf-8') as f:
                            f.write(updated_app_content)
                        
                        print("   SUCCESS セッション設定修正を適用しました")
                        return True
                    else:
                        print("   ERROR redirect処理が見つかりません")
                        return False
            else:
                print("   ERROR セッション設定処理が存在しません")
                return False
        else:
            print("   ERROR start_exam関数が見つかりません")
            return False
            
    except Exception as e:
        print(f"ERROR: セッション管理修正中にエラー: {e}")
        return False

def test_garden_department_after_fix():
    """造園部門修正後テスト"""
    print()
    print("=== 造園部門修正後動作テスト ===")
    
    try:
        # アプリケーションインポート
        from app import app
        
        with app.test_client() as client:
            print("1. セッション開始テスト...")
            
            # 造園部門セッション開始
            start_response = client.get('/start_exam/specialist_garden')
            print(f"   セッション開始ステータス: {start_response.status_code}")
            
            if start_response.status_code in [200, 302]:
                print("   SUCCESS セッション開始成功")
                
                print("2. 1問目CSRFトークン確認...")
                
                # 1問目画面取得
                exam_response = client.get('/exam')
                print(f"   1問目画面ステータス: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    html_content = exam_response.get_data(as_text=True)
                    
                    # CSRFトークン確認
                    if 'name="csrf_token"' in html_content and 'value=' in html_content:
                        print("   SUCCESS CSRFトークンフィールド確認")
                        
                        # CSRFトークン値抽出
                        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', html_content)
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            print(f"   CSRFトークン値: {csrf_token[:20]}...")
                            
                            print("3. CSRF付き回答送信テスト...")
                            
                            # CSRF付きPOST送信
                            answer_response = client.post('/exam', data={
                                'answer': 'A',
                                'csrf_token': csrf_token
                            })
                            
                            print(f"   回答送信ステータス: {answer_response.status_code}")
                            
                            if answer_response.status_code in [200, 302]:
                                print("   SUCCESS CSRF付き回答送信成功")
                                return True
                            else:
                                print("   ERROR CSRF付き回答送信失敗")
                                return False
                        else:
                            print("   ERROR CSRFトークン値抽出失敗")
                            return False
                    else:
                        print("   ERROR CSRFトークンフィールド未確認")
                        return False
                else:
                    print("   ERROR 1問目画面取得失敗")
                    return False
            else:
                print("   ERROR セッション開始失敗")
                return False
                
    except Exception as e:
        print(f"ERROR: テスト実行中にエラー: {e}")
        return False

def main():
    print("緊急対応-13: 造園部門CSRFトークン問題緊急修正システム")
    print("=" * 70)
    print("Purpose: CSRFトークン完全欠如問題の包括的修正")
    print("Background: 造園部門診断で3つの重大問題を特定")
    print()
    
    # 診断結果
    diagnosis_results = {}
    
    # Task 13-A: CSRFテンプレートシステム診断
    print(">>> Task 13-A: CSRFテンプレートシステム診断")
    diagnosis_results['csrf_template'] = diagnose_csrf_template_system()
    
    # Task 13-B: CSRFテンプレート修正適用
    print(">>> Task 13-B: CSRFテンプレート修正適用")
    diagnosis_results['csrf_fix'] = apply_csrf_template_fix()
    
    # Task 13-C: セッション管理修正適用
    print(">>> Task 13-C: セッション管理修正適用")
    diagnosis_results['session_fix'] = apply_session_management_fix()
    
    # Task 13-D: 修正後テスト実行
    print(">>> Task 13-D: 造園部門修正後動作テスト")
    diagnosis_results['final_test'] = test_garden_department_after_fix()
    
    print()
    print("=" * 70)
    print("緊急対応-13 修正システム結果:")
    
    # 結果分析
    success_count = sum(1 for result in diagnosis_results.values() if result is True)
    total_tasks = len(diagnosis_results)
    
    for task_name, result in diagnosis_results.items():
        if result is True:
            print(f"SUCCESS {task_name}: 修正成功")
        elif result is False:
            print(f"ERROR {task_name}: 修正失敗")
        else:
            print(f"WARNING {task_name}: 部分的成功")
    
    print()
    print(f"修正結果サマリー: {success_count}/{total_tasks} タスクで修正成功")
    
    if success_count == total_tasks:
        print()
        print("CELEBRATION 緊急対応-13 修正システム完全成功")
        print("- CSRFトークンシステム: 修正完了")
        print("- セッション状態管理: 修正完了")
        print("- 造園部門動作テスト: 成功")
        print("- 次ステップ: 造園部門10問完走テスト実行")
        return True
    elif success_count >= 3:
        print()
        print("WARNING 緊急対応-13 部分的修正成功")
        print("- 主要な修正は完了")
        print("- 一部の項目で追加作業が必要")
        return None
    else:
        print()
        print("ERROR 緊急対応-13 修正システム失敗")
        print("- 複数の修正で問題発生")
        print("- 追加の緊急対応が必要")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)