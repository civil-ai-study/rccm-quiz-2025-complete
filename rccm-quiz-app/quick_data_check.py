#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース内容クイックチェック
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# アプリケーション設定読み込み
from app import load_questions

def check_data():
    """データ内容チェック"""
    print("データベース内容チェック開始")
    print("-" * 50)
    
    try:
        all_questions = load_questions()
        print(f"総問題数: {len(all_questions)}")
        
        # 問題種別別統計
        basic_count = len([q for q in all_questions if q.get('question_type') == 'basic'])
        specialist_count = len([q for q in all_questions if q.get('question_type') == 'specialist'])
        
        print(f"基礎科目: {basic_count}問")
        print(f"専門科目: {specialist_count}問")
        
        # カテゴリ別統計
        categories = {}
        for question in all_questions:
            category = question.get('category', 'なし')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            
        print("\nカテゴリ別問題数:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}問")
            
        # 道路カテゴリの詳細
        road_questions = [q for q in all_questions if q.get('category') == '道路']
        print(f"\n道路カテゴリ詳細:")
        print(f"  道路問題総数: {len(road_questions)}問")
        
        if road_questions:
            # 年度別統計
            years = {}
            for q in road_questions:
                year = q.get('year', 'なし')
                if year not in years:
                    years[year] = 0
                years[year] += 1
                
            print("  年度別分布:")
            for year, count in sorted(years.items()):
                print(f"    {year}年: {count}問")
                
            # サンプル表示
            print(f"\n  道路問題サンプル:")
            for i, q in enumerate(road_questions[:3]):
                print(f"    [{i+1}] ID:{q.get('id')}, 年度:{q.get('year')}, タイプ:{q.get('question_type')}")
        
        print("\n" + "="*50)
        print("データチェック完了")
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    check_data()