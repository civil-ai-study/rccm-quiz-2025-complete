#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データソースの比較
"""

from app import get_department_questions_ultrasync
import os
from config import DataConfig

def compare_data_sources():
    """2つのデータソースを比較"""
    print("=== データソース比較 ===")
    
    # データソース1: get_department_questions_ultrasync（quiz_departmentで使用）
    print("データソース1: get_department_questions_ultrasync")
    dept_questions = get_department_questions_ultrasync('道路', 10)
    print(f"  問題数: {len(dept_questions)}")
    if dept_questions:
        first_q1 = dept_questions[0]
        print(f"  最初の問題ID: {first_q1.get('id')}")
        print(f"  カテゴリ: {first_q1.get('category')}")
        print(f"  問題種別: {first_q1.get('question_type')}")
        print(f"  年度: {first_q1.get('year')}")
        print(f"  選択肢A長: {len(first_q1.get('option_a', ''))}")
    
    print()
    # データソース2: load_specialist_questions_only（examエンドポイントで使用）
    print("データソース2: load_specialist_questions_only")
    try:
        from utils import load_specialist_questions_only
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        specialist_questions = load_specialist_questions_only('道路', 2016, data_dir)
        print(f"  問題数: {len(specialist_questions)}")
        if specialist_questions:
            first_q2 = specialist_questions[0]
            print(f"  最初の問題ID: {first_q2.get('id')}")
            print(f"  カテゴリ: {first_q2.get('category')}")
            print(f"  問題種別: {first_q2.get('question_type')}")
            print(f"  年度: {first_q2.get('year')}")
            print(f"  選択肢A長: {len(first_q2.get('option_a', ''))}")
    except Exception as e:
        print(f"  ERROR: {str(e)}")
    
    print()
    print("=== 分析 ===")
    
    # ID形式の違いを分析
    if dept_questions and specialist_questions:
        dept_ids = [q.get('id') for q in dept_questions[:5]]
        spec_ids = [q.get('id') for q in specialist_questions[:5]]
        
        print(f"get_department_questions_ultrasync IDs: {dept_ids}")
        print(f"load_specialist_questions_only IDs: {spec_ids}")
        
        # ID変換の可能性を確認
        if dept_ids and spec_ids:
            dept_id_first = dept_ids[0]
            spec_id_first = spec_ids[0]
            
            if isinstance(dept_id_first, int) and isinstance(spec_id_first, int):
                if dept_id_first > 20000 and spec_id_first < 1000:
                    print(f"推定: get_department_questions_ultrasyncは20000+オフセット使用")
                    print(f"推定: load_specialist_questions_onlyは元ID使用")
                    
                    # 変換確認
                    converted_id = dept_id_first - 20000
                    print(f"変換テスト: {dept_id_first} - 20000 = {converted_id}")
                    if converted_id in spec_ids:
                        print("✅ ID変換で一致します")
                        return True
                    else:
                        print("❌ ID変換でも一致しません")
                        return False
    
    return False

if __name__ == "__main__":
    result = compare_data_sources()
    print(f"\n解決可能: {'YES' if result else 'NO'}")