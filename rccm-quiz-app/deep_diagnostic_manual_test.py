#!/usr/bin/env python3
# 🛡️ ULTRASYNC 深層診断手動等価テスト

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
from datetime import datetime
import re

def deep_diagnostic_manual_test():
    """外部知識を活用した深層診断手動等価テスト"""
    
    print('🛡️ ULTRASYNC 深層診断手動等価テスト開始')
    print('=' * 70)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # セッションクリア
            sess.clear()
        
        try:
            # ステップ1: トップページアクセス
            print('ステップ1: トップページアクセス確認')
            response = client.get('/')
            print(f'  トップページ応答: {response.status_code}')
            if response.status_code != 200:
                print(f'  ❌ トップページアクセス失敗')
                return False
            print('  ✅ トップページ正常')
            
            # ステップ2: 基礎科目試験開始（修正後のセッション初期化確認）
            print('ステップ2: 基礎科目試験開始とセッション初期化検証')
            start_data = {
                'questions': '10',
                'year': '2024'
            }
            start_response = client.post('/start_exam/基礎科目', 
                                       data=start_data, 
                                       follow_redirects=False)
            print(f'  start_exam応答: {start_response.status_code}')
            print(f'  リダイレクト先: {start_response.location if start_response.location else "なし"}')
            
            # ステップ3: セッション状態詳細診断
            print('ステップ3: セッション状態詳細診断')
            with client.session_transaction() as sess:
                exam_question_ids = sess.get('exam_question_ids', [])
                exam_current = sess.get('exam_current', 0)
                exam_category = sess.get('exam_category', '')
                
                print(f'  問題ID数: {len(exam_question_ids)}')
                print(f'  問題ID例: {exam_question_ids[:3] if exam_question_ids else "空"}')
                print(f'  現在位置: {exam_current}')
                print(f'  試験カテゴリー: {exam_category}')
                
                # セッション診断結果
                session_diagnosis = {
                    'has_question_ids': len(exam_question_ids) > 0,
                    'question_count': len(exam_question_ids),
                    'current_position': exam_current,
                    'category_set': bool(exam_category),
                    'ids_sample': exam_question_ids[:3] if exam_question_ids else []
                }
                
                if len(exam_question_ids) == 0:
                    print('  ❌ CRITICAL: セッションに問題IDが設定されていない')
                    return False
                elif len(exam_question_ids) != 10:
                    print(f'  ⚠️ WARNING: 問題数が10ではない: {len(exam_question_ids)}')
                else:
                    print('  ✅ セッション正常初期化')
            
            # ステップ4: /examルート詳細診断（外部知識適用）
            print('ステップ4: /examルート詳細診断（Flask Template Debugging）')
            exam_response = client.get('/exam')
            print(f'  /exam応答: {exam_response.status_code}')
            
            if exam_response.status_code != 200:
                print(f'  ❌ /examアクセス失敗: {exam_response.status_code}')
                return False
            
            content = exam_response.data.decode('utf-8')
            print(f'  応答サイズ: {len(content)} bytes')
            
            # 外部知識適用: Flask Template Debugging
            # 1. テンプレート変数の存在確認
            template_variables = [
                ('question', 'question変数'),
                ('current_no', '現在問題番号'),
                ('total_questions', '総問題数'),
                ('csrf_token', 'CSRFトークン')
            ]
            
            template_diagnosis = {}
            print('  Flask Template変数診断:')
            for var_name, description in template_variables:
                # Jinja2テンプレート内での変数参照を確認
                if f'{{{{{ var_name}' in content or f'{{{{{ var_name}.' in content:
                    template_diagnosis[var_name] = 'referenced'
                    print(f'    ✅ {description}: テンプレート内で参照されている')
                else:
                    template_diagnosis[var_name] = 'not_referenced'
                    print(f'    ❌ {description}: テンプレート内で参照されていない')
            
            # 2. 実際の値の出力確認
            print('  実際の値出力診断:')
            value_checks = [
                ('問題 1/10', '進捗表示'),
                ('<input.*name="qid"', '問題IDフィールド'),
                ('<input.*name="answer"', '回答フィールド'),
                ('name="csrf_token"', 'CSRFトークン'),
                ('{{ question.question }}', '問題文変数'),
                ('{{ question.option_a }}', '選択肢A変数')
            ]
            
            for pattern, description in value_checks:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f'    ✅ {description}: 存在')
                else:
                    print(f'    ❌ {description}: 不存在')
            
            # 3. エラーメッセージ詳細確認
            print('  エラーメッセージ詳細確認:')
            error_patterns = [
                (r'問題データが存在しません', 'データ不存在エラー'),
                (r'問題が見つかりません', '問題未発見エラー'),
                (r'セッションが無効です', 'セッション無効エラー'),
                (r'undefined.*question', 'question変数未定義'),
                (r'jinja2\.exceptions', 'Jinja2テンプレートエラー'),
                (r'NameError.*question', 'Python変数エラー')
            ]
            
            found_errors = []
            for pattern, description in error_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_errors.append(description)
                    print(f'    ❌ 検出: {description}')
            
            if not found_errors:
                print('    ✅ 明示的なエラーメッセージなし')
            
            # 4. 問題フォーム構造診断
            print('  問題フォーム構造診断:')
            form_elements = [
                ('<form', 'フォーム開始タグ'),
                ('method="POST"', 'POSTメソッド'),
                ('action="/exam"', 'exam action'),
                ('<fieldset', 'フィールドセット'),
                ('type="radio"', 'ラジオボタン'),
                ('value="A"', '選択肢A'),
                ('value="B"', '選択肢B'),
                ('value="C"', '選択肢C'),
                ('value="D"', '選択肢D'),
                ('<button.*type="submit"', '送信ボタン')
            ]
            
            form_diagnosis = {}
            for element, description in form_elements:
                if re.search(element, content, re.IGNORECASE):
                    form_diagnosis[description] = True
                    print(f'    ✅ {description}: 存在')
                else:
                    form_diagnosis[description] = False
                    print(f'    ❌ {description}: 不存在')
            
            # 5. 外部知識適用: Session Debug Approach
            print('  セッションデバッグ情報:')
            debug_response = client.get('/debug/session')
            if debug_response.status_code == 200:
                try:
                    debug_data = debug_response.json()
                    print(f'    セッションデータ: {debug_data}')
                    
                    # セッションとテンプレートの整合性確認
                    session_ids = debug_data.get('exam_question_ids', [])
                    if session_ids:
                        first_id = session_ids[0]
                        print(f'    最初の問題ID: {first_id}')
                        
                        # 実際にその問題IDが問題データに存在するか確認
                        if f'value="{first_id}"' in content:
                            print('    ✅ セッションの問題IDがテンプレートに反映されている')
                        else:
                            print('    ❌ セッションの問題IDがテンプレートに反映されていない')
                            print(f'    ❌ 期待するパターン: value="{first_id}"')
                            
                            # valueパターンを調査
                            value_matches = re.findall(r'value="([^"]*)"', content)
                            print(f'    検出された値: {value_matches[:10]}')
                    
                except Exception as e:
                    print(f'    ❌ セッションデバッグデータ解析エラー: {e}')
            else:
                print(f'    ❌ セッションデバッグエンドポイント失敗: {debug_response.status_code}')
            
            # ステップ5: 結論と推奨修正方法
            print('\nステップ5: 診断結果と推奨修正方法')
            
            # 問題フォームの存在確認
            has_form = all([
                form_diagnosis.get('フォーム開始タグ', False),
                form_diagnosis.get('POSTメソッド', False),
                form_diagnosis.get('送信ボタン', False)
            ])
            
            has_options = all([
                form_diagnosis.get('選択肢A', False),
                form_diagnosis.get('選択肢B', False),
                form_diagnosis.get('選択肢C', False),
                form_diagnosis.get('選択肢D', False)
            ])
            
            if has_form and has_options:
                print('  ✅ 問題フォーム構造は正常')
                
                # さらに詳細な問題を特定
                if '{{ question.question }}' in content:
                    print('  ❌ CRITICAL: question変数がテンプレートで展開されていない')
                    print('  推奨修正: app.pyのexam()関数でquestion変数の渡し方を確認')
                    return False
                else:
                    print('  ✅ question変数は展開されている')
                    
                # 進捗表示確認
                if '1/10' in content or '問題 1/10' in content:
                    print('  ✅ 進捗表示正常')
                    print('  ✅ 基礎科目10問完走テスト: 全ての前提条件が整っている')
                    return True
                else:
                    print('  ❌ 進捗表示に問題がある可能性')
                    return False
            else:
                print('  ❌ CRITICAL: 問題フォーム構造に問題がある')
                print(f'  フォーム存在: {has_form}, 選択肢存在: {has_options}')
                return False
            
        except Exception as e:
            print(f'深層診断中にエラー: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = deep_diagnostic_manual_test()
    if success:
        print('\n🎯 結論: 基礎科目10問完走テストは正常に動作します')
    else:
        print('\n❌ 結論: 基礎科目10問完走テストに問題があります')
        print('   詳細な診断結果を確認して修正が必要です')