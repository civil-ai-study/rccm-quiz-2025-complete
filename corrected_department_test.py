#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正版部門指定テスト - 道路部門問題のみが出題されるかの確認
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def corrected_department_test():
    """修正版部門指定テスト - 正しいルート使用"""
    print("=== 修正版部門指定テスト開始 ===")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. 道路部門の種別選択ページにアクセス
            print("1. 道路部門種別選択ページアクセス")
            types_response = client.get('/departments/road/types')
            
            if types_response.status_code != 200:
                return f"FAILED: 道路部門種別選択失敗 {types_response.status_code}"
            
            print("SUCCESS: 道路部門種別選択ページアクセス成功")
            
            # 2. 道路部門専門科目開始（正しいルート）
            print("2. 道路部門専門科目開始")
            start_response = client.get('/exam?department=road&type=specialist')
            
            if start_response.status_code != 200:
                return f"FAILED: 道路部門専門科目開始失敗 {start_response.status_code}"
            
            print("SUCCESS: 道路部門専門科目開始成功")
            
            # 3. 問題画面で内容確認
            print("3. 問題画面で内容確認")
            
            html = start_response.data.decode('utf-8', errors='ignore')
            
            # カテゴリ確認
            category_match = re.search(r'カテゴリ:\s*([^<\n]+)', html)
            if category_match:
                category = category_match.group(1).strip()
                print(f"出題カテゴリ: {category}")
                
                # 道路部門であるかチェック
                if category == "道路":
                    print("SUCCESS: 道路部門問題が出題されました")
                    
                    # 問題番号確認
                    progress_match = re.search(r'(\d+)/(\d+)', html)
                    if progress_match:
                        current_num = progress_match.group(1)
                        total_num = progress_match.group(2)
                        print(f"進捗表示: {current_num}/{total_num}")
                        
                        return {
                            'status': 'COMPLETE_SUCCESS',
                            'category': category,
                            'progress': f"{current_num}/{total_num}",
                            'department_specified': True,
                            'correct_category': True,
                            'routing_fixed': True
                        }
                    else:
                        print("WARNING: 進捗表示が見つかりません")
                        return {
                            'status': 'PARTIAL_SUCCESS',
                            'category': category,
                            'department_specified': True,
                            'correct_category': True,
                            'routing_fixed': True,
                            'progress_issue': True
                        }
                else:
                    print(f"FIELD_MIXING_DETECTED: 道路部門以外の問題が出題: {category}")
                    return {
                        'status': 'FIELD_MIXING_DETECTED',
                        'category': category,
                        'expected_category': '道路',
                        'department_specified': False,
                        'correct_category': False,
                        'routing_fixed': True
                    }
            else:
                return "FAILED: カテゴリ情報が見つかりません"

if __name__ == "__main__":
    result = corrected_department_test()
    
    print("=" * 60)
    if isinstance(result, dict):
        if result['status'] == 'COMPLETE_SUCCESS':
            print("SUCCESS: 部門指定テスト完全成功")
            print(f"出題カテゴリ: {result['category']}")
            print(f"進捗表示: {result['progress']}")
            print("部門指定ルート修正: 成功")
            print("部門指定が正しく動作しています")
        elif result['status'] == 'PARTIAL_SUCCESS':
            print("PARTIAL SUCCESS: 部門指定は成功、進捗表示に問題")
            print(f"出題カテゴリ: {result['category']}")
            print("部門指定ルート修正: 成功")
        elif result['status'] == 'FIELD_MIXING_DETECTED':
            print("CRITICAL: 分野混在問題発見")
            print(f"期待: {result['expected_category']}, 実際: {result['category']}")
            print("CLAUDE.mdの分野混在問題が未解決です")
        else:
            print(f"UNKNOWN STATUS: {result}")
    else:
        print(f"TEST FAILED: {result}")
    print("=" * 60)