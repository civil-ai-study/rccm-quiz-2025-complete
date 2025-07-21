#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門get_mixed_questions関数の直接テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import load_questions, get_mixed_questions, normalize_department_name, get_department_category

def test_road_function():
    """道路部門関数テスト"""
    print("道路部門get_mixed_questions関数テスト開始")
    print("-" * 60)
    
    try:
        # データ読み込み
        all_questions = load_questions()
        print(f"総問題数: {len(all_questions)}")
        
        # 道路問題フィルタ
        road_questions = [q for q in all_questions if q.get('category') == '道路']
        print(f"道路カテゴリ問題数: {len(road_questions)}")
        
        # 部門名正規化テスト
        normalized = normalize_department_name("道路")
        print(f"正規化部門名: '{normalized}'")
        
        # カテゴリマッピングテスト
        target_category = get_department_category(normalized) if normalized else None
        print(f"マッピングされたカテゴリ: '{target_category}'")
        
        # 空のセッション作成
        mock_session = {
            'history': [],
            'session_size': 10
        }
        
        print("\n=== get_mixed_questions関数テスト ===")
        
        # テスト1: 道路部門、専門科目、年度なし
        try:
            print("テスト1開始: department='道路', question_type='specialist', year=None")
            result = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='全体',
                session_size=10,
                department='道路',
                question_type='specialist',
                year=None
            )
            print(f"テスト1結果: {len(result)}問取得")
            if result:
                print(f"  サンプル問題: ID={result[0].get('id')}, カテゴリ={result[0].get('category')}")
            else:
                print("  結果: 問題なし")
        except Exception as e:
            print(f"テスト1エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # テスト2: 道路部門、専門科目、2015年度
        try:
            print("テスト2開始: department='道路', question_type='specialist', year='2015'")
            result = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='全体',
                session_size=10,
                department='道路',
                question_type='specialist',
                year='2015'
            )
            print(f"テスト2結果: {len(result)}問取得")
            if result:
                print(f"  サンプル問題: ID={result[0].get('id')}, 年度={result[0].get('year')}")
            else:
                print("  結果: 問題なし")
        except Exception as e:
            print(f"テスト2エラー: {str(e)}")
            
        # テスト3: 道路部門、専門科目、空文字列年度
        try:
            print("テスト3開始: department='道路', question_type='specialist', year=''")
            result = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='全体',
                session_size=10,
                department='道路',
                question_type='specialist',
                year=''
            )
            print(f"テスト3結果: {len(result)}問取得")
            if result:
                print(f"  サンプル問題: ID={result[0].get('id')}, カテゴリ={result[0].get('category')}")
            else:
                print("  結果: 問題なし")
        except Exception as e:
            print(f"テスト3エラー: {str(e)}")
            
        # テスト4: 道路問題の年度分布確認
        print(f"\n=== 道路問題年度分布 ===")
        years = {}
        for q in road_questions:
            year = q.get('year')
            question_type = q.get('question_type')
            if year not in years:
                years[year] = {'specialist': 0, 'basic': 0}
            years[year][question_type] = years[year].get(question_type, 0) + 1
            
        for year in sorted(years.keys()):
            specialist_count = years[year].get('specialist', 0)
            print(f"  {year}年: 専門科目{specialist_count}問")
            
        print("\n" + "="*60)
        print("関数テスト完了")
        
    except Exception as e:
        print(f"テストエラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_road_function()