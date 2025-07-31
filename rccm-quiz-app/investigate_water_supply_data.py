#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下水道部門の問題データ詳細調査
"""

from app import app, get_department_questions_ultrasync

def investigate_water_supply_data():
    """上下水道部門の問題データを詳細調査"""
    print("=== 上下水道部門データ詳細調査 ===")
    
    try:
        # Get water supply questions
        print("1. 上下水道部門の問題データ取得...")
        questions = get_department_questions_ultrasync('上下水道')
        print(f"   取得問題数: {len(questions)}")
        
        if len(questions) == 0:
            print("   ERROR: 上下水道部門の問題が0件")
            return False
        
        # Check first few questions structure
        print("2. 問題データ構造確認...")
        for i, q in enumerate(questions[:3]):
            print(f"   問題{i+1}:")
            print(f"     ID: {q.get('id', 'NO_ID')}")
            print(f"     問題文: {q.get('question', 'NO_QUESTION')[:50]}...")
            print(f"     選択肢A: {q.get('option_a', 'NO_OPTION_A')[:30]}...")
            print(f"     選択肢B: {q.get('option_b', 'NO_OPTION_B')[:30]}...")
            print(f"     選択肢C: {q.get('option_c', 'NO_OPTION_C')[:30]}...")
            print(f"     選択肢D: {q.get('option_d', 'NO_OPTION_D')[:30]}...")
            print(f"     正解: {q.get('correct_answer', 'NO_ANSWER')}")
            print(f"     部門: {q.get('department', 'NO_DEPARTMENT')}")
            print(f"     年度: {q.get('year', 'NO_YEAR')}")
            print()
        
        # Check for data integrity issues
        print("3. データ整合性チェック...")
        issues = []
        
        for i, q in enumerate(questions):
            qid = q.get('id', f'NO_ID_{i}')
            
            # Check required fields
            if not q.get('question'):
                issues.append(f"問題{qid}: 問題文なし")
            if not q.get('option_a'):
                issues.append(f"問題{qid}: 選択肢Aなし")
            if not q.get('option_b'):
                issues.append(f"問題{qid}: 選択肢Bなし")
            if not q.get('option_c'):
                issues.append(f"問題{qid}: 選択肢Cなし")
            if not q.get('option_d'):
                issues.append(f"問題{qid}: 選択肢Dなし")
            if not q.get('correct_answer'):
                issues.append(f"問題{qid}: 正解なし")
        
        if issues:
            print(f"   データ問題発見: {len(issues)}件")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"     {issue}")
            if len(issues) > 10:
                print(f"     ... その他{len(issues) - 10}件")
        else:
            print("   データ整合性OK")
            
        return True
        
    except Exception as e:
        print(f"ERROR: 調査中にエラー発生: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_water_supply_session():
    """上下水道部門でのセッション動作テスト"""
    print("\n=== 上下水道部門セッション動作テスト ===")
    
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Session initialization
        with client.session_transaction() as sess:
            sess.clear()
            sess['user_name'] = 'water_supply_session_test'
            sess.modified = True
        
        try:
            # Department selection
            print("1. 部門選択...")
            resp_dept = client.get('/quiz_department/上下水道')
            print(f"   ステータス: {resp_dept.status_code}")
            
            if resp_dept.status_code != 302:
                print(f"   ERROR: 部門選択失敗")
                return False
            
            # Get first question
            print("2. 最初の問題取得...")
            resp_first = client.get('/exam')
            print(f"   ステータス: {resp_first.status_code}")
            
            if resp_first.status_code != 200:
                print(f"   ERROR: 問題取得失敗")
                if hasattr(resp_first, 'data'):
                    content = resp_first.data.decode('utf-8', errors='ignore')
                    if 'エラー' in content or 'error' in content.lower():
                        print(f"   エラー内容検出: {content[:200]}...")
                return False
            
            # Try to answer first question
            print("3. 最初の問題回答...")
            resp_answer = client.post('/exam', data={'answer': 'A'})
            print(f"   ステータス: {resp_answer.status_code}")
            
            if resp_answer.status_code == 302:
                location = resp_answer.headers.get('Location', '')
                print(f"   リダイレクト先: {location}")
                
                # Get second question
                print("4. 次の問題取得...")
                resp_second = client.get('/exam')
                print(f"   ステータス: {resp_second.status_code}")
                
                if resp_second.status_code == 200:
                    print("   SUCCESS: 上下水道部門の基本動作確認完了")
                    return True
                else:
                    print(f"   ERROR: 次の問題取得失敗")
                    return False
            else:
                print(f"   ERROR: 回答処理失敗")
                return False
                
        except Exception as e:
            print(f"   EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    data_ok = investigate_water_supply_data()
    session_ok = test_water_supply_session()
    
    print(f"\n=== 最終結果 ===")
    print(f"データ調査: {'SUCCESS' if data_ok else 'FAILURE'}")
    print(f"セッションテスト: {'SUCCESS' if session_ok else 'FAILURE'}")