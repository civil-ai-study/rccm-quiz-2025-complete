#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失敗パターンの再現テスト
"""

from app import app

def reproduce_failure_pattern():
    """失敗パターンを確実に再現"""
    print("=== 失敗パターン再現テスト ===")
    
    # 建設環境部門で失敗が多いため、これを対象とする
    target_dept = '建設環境'
    
    with app.test_client() as client:
        # 複数回テストして一貫性を確認
        results = []
        
        for i in range(5):
            print(f"\nテスト {i+1}/5: {target_dept}")
            
            # 確実なセッション初期化
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_name'] = f'test_{i}'
                sess.modified = True
            
            try:
                # Step 1: quiz_departmentアクセス
                resp1 = client.get(f'/quiz_department/{target_dept}')
                print(f"  quiz_department: {resp1.status_code}")
                
                if resp1.status_code == 302:
                    # Step 2: examアクセス
                    location = resp1.headers.get('Location', '')
                    resp2 = client.get(location)
                    print(f"  exam: {resp2.status_code}")
                    
                    if resp2.status_code == 200:
                        html = resp2.data.decode('utf-8', errors='ignore')
                        
                        # 詳細分析
                        has_value_a = 'value="A"' in html
                        has_value_b = 'value="B"' in html
                        has_value_c = 'value="C"' in html
                        has_value_d = 'value="D"' in html
                        
                        radio_count = html.count('type="radio"')
                        question_text = html.count('question-text')
                        option_text = html.count('option-text')
                        html_size = len(html)
                        
                        success = has_value_a and has_value_b and has_value_c and has_value_d
                        
                        result = {
                            'success': success,
                            'values': {
                                'A': has_value_a,
                                'B': has_value_b, 
                                'C': has_value_c,
                                'D': has_value_d
                            },
                            'counts': {
                                'radio': radio_count,
                                'question_text': question_text,
                                'option_text': option_text,
                                'html_size': html_size
                            }
                        }
                        
                        results.append(result)
                        
                        print(f"  結果: {'SUCCESS' if success else 'FAILED'}")
                        print(f"  values: A={has_value_a}, B={has_value_b}, C={has_value_c}, D={has_value_d}")
                        print(f"  counts: radio={radio_count}, q_text={question_text}, html_size={html_size}")
                        
                        # 失敗の場合、HTMLの一部を確認
                        if not success:
                            print("  HTML抜粋:")
                            # form要素周辺を探す
                            form_start = html.find('<form')
                            if form_start != -1:
                                form_end = html.find('</form>', form_start) + 7
                                form_html = html[form_start:form_end]
                                print(f"    Form長: {len(form_html)}文字")
                                
                                # radioボタンの有無を確認
                                if 'type="radio"' in form_html:
                                    print("    ✅ Form内にradioボタンあり")
                                else:
                                    print("    ❌ Form内にradioボタンなし")
                            else:
                                print("    ❌ Form要素が見つかりません")
                    else:
                        results.append({'success': False, 'error': f'exam_status_{resp2.status_code}'})
                        print(f"  ERROR: exam status {resp2.status_code}")
                else:
                    results.append({'success': False, 'error': f'dept_status_{resp1.status_code}'})
                    print(f"  ERROR: dept status {resp1.status_code}")
                    
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
                print(f"  EXCEPTION: {str(e)[:50]}")
    
    # 結果分析
    print(f"\n=== 結果分析 ===")
    success_count = sum(1 for r in results if r.get('success', False))
    print(f"成功率: {success_count}/5 ({success_count*20}%)")
    
    if success_count > 0 and success_count < 5:
        print("⚠️ 不安定性確認: 成功と失敗が混在")
        return 'unstable'
    elif success_count == 0:
        print("❌ 一貫した失敗")
        return 'consistent_failure'
    else:
        print("✅ 一貫した成功")
        return 'consistent_success'

if __name__ == "__main__":
    pattern = reproduce_failure_pattern()
    print(f"\nパターン: {pattern}")