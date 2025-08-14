#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ultra Simple Deep Search: データ不整合問題の根本原因特定テスト
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
from utils import load_rccm_data_files

def debug_data_mismatch():
    """データ不整合問題の根本原因を特定"""
    print("=== Ultra Simple Deep Search: データ不整合問題調査 ===")
    
    with app.app_context():
        # 1. all_questionsの読み込み
        data_dir = os.path.join('rccm-quiz-app', 'data')
        all_questions = load_rccm_data_files(data_dir)
        
        print(f"1. all_questions読み込み: {len(all_questions)}問")
        
        # 2. all_questionsのIDレンジ確認
        if all_questions:
            all_ids = [int(q.get('id', 0)) for q in all_questions if q.get('id')]
            all_ids.sort()
            
            print(f"2. IDレンジ確認:")
            print(f"   最小ID: {min(all_ids)}")
            print(f"   最大ID: {max(all_ids)}")
            print(f"   最初の10件: {all_ids[:10]}")
            print(f"   最後の10件: {all_ids[-10:]}")
            
            # 3. IDの分布確認
            basic_ids = [id for id in all_ids if 1000000 <= id <= 1999999]
            specialist_ids = [id for id in all_ids if 2000000 <= id <= 2999999]
            other_ids = [id for id in all_ids if id < 1000000 or id >= 3000000]
            
            print(f"3. ID分布:")
            print(f"   基礎科目(1000000-1999999): {len(basic_ids)}件")
            print(f"   専門科目(2000000-2999999): {len(specialist_ids)}件")
            print(f"   その他: {len(other_ids)}件")
            
            if other_ids:
                print(f"   その他のID例: {other_ids[:20]}")
        
        # 4. extract_department_questions_from_csvテスト
        from app import extract_department_questions_from_csv
        
        print(f"\n4. extract_department_questions_from_csvテスト:")
        road_questions = extract_department_questions_from_csv('道路', 10)
        
        if road_questions:
            print(f"   道路部門抽出: {len(road_questions)}問")
            road_ids = [int(q.get('id', 0)) for q in road_questions if q.get('id')]
            print(f"   抽出されたID例: {road_ids[:10]}")
            
            # 5. 重要: all_questionsとの照合
            print(f"\n5. 重要: all_questionsとの照合")
            missing_ids = []
            for road_id in road_ids[:5]:  # 最初の5個をチェック
                found = any(int(q.get('id', 0)) == road_id for q in all_questions)
                if not found:
                    missing_ids.append(road_id)
                print(f"   ID {road_id}: {'✅ 存在' if found else '❌ 不存在'}")
            
            if missing_ids:
                print(f"   ❌ 見つからないID: {missing_ids}")
                print("   🚨 根本原因: extract_department_questions_from_csvとall_questionsの不整合")
            else:
                print("   ✅ ID照合: すべて存在確認")
        else:
            print("   ❌ 道路部門問題抽出失敗")
        
        # 6. 基礎科目の確認
        print(f"\n6. 基礎科目確認:")
        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
        if basic_questions:
            print(f"   基礎科目: {len(basic_questions)}問")
            basic_sample_ids = [int(q.get('id', 0)) for q in basic_questions[:5]]
            print(f"   基礎科目ID例: {basic_sample_ids}")
        
        print("\n=== 調査完了 ===")

if __name__ == "__main__":
    debug_data_mismatch()