#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部門指定テスト - 道路部門問題のみが出題されるかの確認
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def department_specific_test():
    """部門指定が正しく動作するかテスト"""
    print("=== 部門指定テスト開始 ===")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. 道路部門の種別選択ページにアクセス
            print("1. 道路部門種別選択ページアクセス")
            types_response = client.get('/departments/road/types')
            
            if types_response.status_code != 200:
                return f"FAILED: 道路部門種別選択失敗 {types_response.status_code}"
            
            print("SUCCESS: 道路部門種別選択ページアクセス成功")
            
            # 2. 道路部門専門科目開始（正しいルート使用）
            print("2. 道路部門専門科目開始")
            start_response = client.get('/exam?department=road&type=specialist')
            
            if start_response.status_code not in [200, 302]:
                return f"FAILED: 道路部門専門科目開始失敗 {start_response.status_code}"
            
            print("SUCCESS: 道路部門専門科目開始成功")
            
            # 3. exam画面で問題確認
            print("3. exam画面で問題確認")
            exam_response = client.get('/exam')
            
            if exam_response.status_code != 200:
                return f"FAILED: exam画面アクセス失敗 {exam_response.status_code}"
            
            html = exam_response.data.decode('utf-8', errors='ignore')
            
            # カテゴリ確認
            category_match = re.search(r'カテゴリ:\s*([^<\n]+)', html)
            if category_match:
                category = category_match.group(1).strip()
                print(f"出題カテゴリ: {category}")
                
                # 道路部門であるかチェック
                if category == "道路":
                    print("SUCCESS: 道路部門問題が出題されました")
                    return {
                        'status': 'SUCCESS',
                        'category': category,
                        'department_specified': True,
                        'correct_category': True
                    }
                else:
                    print(f"WARNING: 道路部門ではない問題が出題: {category}")
                    return {
                        'status': 'FIELD_MIXING_DETECTED',
                        'category': category,
                        'department_specified': False,
                        'correct_category': False
                    }
            else:
                return "FAILED: カテゴリ情報が見つかりません"

if __name__ == "__main__":
    result = department_specific_test()
    
    print("=" * 60)
    if isinstance(result, dict):
        if result['status'] == 'SUCCESS':
            print("✓ DEPARTMENT TEST SUCCESS")
            print(f"✓ 出題カテゴリ: {result['category']}")
            print("✓ 部門指定が正しく動作しています")
        elif result['status'] == 'FIELD_MIXING_DETECTED':
            print("✗ CRITICAL: 部門指定問題発見")
            print(f"✗ 期待: 道路, 実際: {result['category']}")
            print("✗ CLAUDE.mdの分野混在問題が未解決です")
        else:
            print(f"✗ UNKNOWN STATUS: {result}")
    else:
        print(f"✗ TEST FAILED: {result}")
    print("=" * 60)