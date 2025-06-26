#!/usr/bin/env python3
"""
Critical-5: 部門数不一致問題の分析スクリプト
CLAUDE.md準拠の根本原因調査
"""

from utils import load_rccm_data_files
from config import RCCMConfig

def analyze_department_count_issue():
    """部門数不一致問題の詳細分析"""
    print('🔍 Critical-5: 部門数不一致問題分析開始')
    
    # 実際のデータから部門を抽出
    questions = load_rccm_data_files('data')
    specialist_questions = [q for q in questions if q.get('question_type') == 'specialist']
    
    actual_categories = set()
    for q in specialist_questions:
        cat = q.get('category', '不明')
        actual_categories.add(cat)
    
    print(f'✅ 実際の専門科目部門数: {len(actual_categories)}部門')
    print('📋 実際の部門リスト:')
    for i, cat in enumerate(sorted(actual_categories), 1):
        print(f'  {i:2d}. {cat}')
    
    # システム設定の期待値確認
    expected_departments = getattr(RCCMConfig, 'DEPARTMENTS', [])
    print(f'\n⚙️ システム期待部門数: {len(expected_departments)}部門')
    
    if expected_departments:
        print('📋 システム期待部門リスト:')
        for i, dept in enumerate(expected_departments, 1):
            print(f'  {i:2d}. {dept}')
    
    # 不一致の確認
    actual_count = len(actual_categories)
    expected_count = len(expected_departments)
    
    if actual_count != expected_count:
        print(f'\n❌ Critical-5確認: 部門数不一致')
        print(f'   実際: {actual_count}部門')
        print(f'   期待: {expected_count}部門')
        print(f'   差分: {actual_count - expected_count}部門')
        
        # 不一致の根本原因分析
        print('\n🔍 根本原因分析:')
        
        if expected_count == 0:
            print('   - システム設定に部門リストが定義されていない')
        elif actual_count > expected_count:
            print('   - 実際のデータに想定外の部門が含まれている')
        else:
            print('   - 実際のデータで部門が不足している')
        
        return False
    else:
        print(f'\n✅ 部門数は一致: {actual_count}部門')
        return True

if __name__ == '__main__':
    analyze_department_count_issue()