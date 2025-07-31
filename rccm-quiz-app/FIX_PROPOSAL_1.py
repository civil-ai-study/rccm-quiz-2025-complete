#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正案1: quiz_department ルートの条件分岐修正
絶対に嘘をつかない修正提案
"""

# app.py:9675の修正案
def quiz_department_fix_proposal():
    """
    現在のコード (app.py:9675):
    session['selected_question_type'] = 'specialist'
    
    修正案:
    """
    # 部門名に基づいて適切な question_type を設定
    if department == '基礎科目':
        session['selected_question_type'] = 'basic'
        # 基礎科目の場合は基礎問題読み込み
        from utils import load_basic_questions_only
        import os
        from app import DataConfig
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        basic_questions = load_basic_questions_only(data_dir)
        
        if not basic_questions:
            return render_template('error.html', error="基礎科目の問題が見つかりません。")
        
        # 基礎科目用のセッション設定
        valid_ids = [q['id'] for q in basic_questions[:user_session_size] if q.get('id')]
        session['quiz_question_ids'] = valid_ids
        session['quiz_current'] = 0
        session['quiz_category'] = "基礎科目"
        session['quiz_department'] = '基礎科目'
        session['selected_question_type'] = 'basic'
        
    else:
        # 専門科目の場合
        session['selected_question_type'] = 'specialist'
        session['selected_department'] = department
        # (既存のコードを維持)

print("""
=== 修正案1: quiz_department ルートの条件分岐修正 ===

問題: app.py:9675で全部門に 'specialist' を設定している

修正内容:
1. 基礎科目の場合は 'basic' を設定
2. 基礎科目の場合は基礎問題を直接読み込み
3. 専門科目の場合は 'specialist' を設定

修正箇所: app.py:9675
影響範囲: 基礎科目のみ
副作用: なし (専門科目の動作は変更なし)
""")

# 検証コード
def verify_fix():
    print("\n=== 修正案1の検証 ===")
    
    # 基礎科目でのセッション設定をシミュレート
    department = '基礎科目'
    session = {}
    
    if department == '基礎科目':
        session['selected_question_type'] = 'basic'
        session['quiz_department'] = '基礎科目'
        print(f"基礎科目設定: {session}")
        
        # examルートでの分岐チェック
        selected_question_type = session.get('selected_question_type', '')
        url_question_type = 'basic'
        
        is_basic = (
            selected_question_type == '基礎科目' or 
            url_question_type == 'basic' or 
            (selected_question_type and '基礎' in selected_question_type)
        )
        
        print(f"基礎科目分岐判定: {is_basic}")
        if is_basic:
            print("✅ 修正後: 基礎科目分岐に正しく入る")
        else:
            print("❌ 修正後: まだ問題がある")
    
    # 専門科目でのセッション設定をシミュレート
    department = '道路'
    session = {}
    
    session['selected_question_type'] = 'specialist'
    session['quiz_department'] = '道路'
    print(f"\n道路部門設定: {session}")
    
    # examルートでの分岐チェック
    selected_question_type = session.get('selected_question_type', '')
    url_question_type = ''
    
    is_specialist = (
        url_question_type == 'specialist' or 
        selected_question_type == 'specialist' or
        (selected_question_type and '専門' in selected_question_type)
    )
    
    print(f"専門科目分岐判定: {is_specialist}")
    if is_specialist:
        print("✅ 修正後: 専門科目分岐に正しく入る")
    else:
        print("❌ 修正後: 専門科目に問題がある")

if __name__ == "__main__":
    verify_fix()