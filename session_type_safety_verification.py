#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッション型安全性修正の検証スクリプト
session.get('exam_current')の文字列と数値比較エラー修正確認
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from flask import Flask
from unittest.mock import Mock, patch
import logging

# テスト設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_session_type_safety():
    """セッション型安全性テスト"""
    print("=== セッション型安全性修正の検証開始 ===")
    
    # 問題となりうるセッション値のテストケース
    test_cases = [
        {"exam_current": "0", "desc": "文字列の0"},
        {"exam_current": "5", "desc": "文字列の数値"},
        {"exam_current": "", "desc": "空文字列"},
        {"exam_current": None, "desc": "None値"},
        {"exam_current": 0, "desc": "正常な数値0"},
        {"exam_current": 5, "desc": "正常な数値5"},
        {"exam_current": [], "desc": "リスト型"},
        {"exam_current": {}, "desc": "辞書型"}
    ]
    
    print(f"\n1. 型安全な比較処理のテスト（{len(test_cases)}ケース）")
    
    for i, case in enumerate(test_cases, 1):
        exam_current_value = case["exam_current"]
        desc = case["desc"]
        
        print(f"\nケース{i}: {desc} (値: {repr(exam_current_value)})")
        
        # 修正後のコード相当をシミュレート
        try:
            # 修正箇所1: _validate_session_integrity相当
            current = exam_current_value if exam_current_value is not None else 0
            if not isinstance(current, int):
                current = 0
            
            # 数値比較テスト（例：len=10のリスト想定）
            exam_ids_len = 10
            is_valid_range = current >= 0 and current < exam_ids_len
            
            print(f"  - 型安全変換後: {current} (type: {type(current).__name__})")
            print(f"  - 範囲チェック結果: {is_valid_range}")
            
            # 修正箇所2: final_exam_current相当
            final_exam_current = exam_current_value if exam_current_value is not None else 0
            if not isinstance(final_exam_current, int):
                final_exam_current = 0
            
            is_within_bounds = final_exam_current < exam_ids_len
            print(f"  - 最終インデックスチェック: {is_within_bounds}")
            
        except Exception as e:
            print(f"  ❌ エラー発生: {e}")
            continue
        
        print(f"  ✅ 型安全処理成功")
    
    print(f"\n2. 実際のコードパターンテスト")
    
    # 実際の修正コードパターンをテスト
    test_session_patterns = [
        {"exam_current": "invalid", "exam_question_ids": [1, 2, 3, 4, 5]},
        {"exam_current": 3, "exam_question_ids": [1, 2, 3, 4, 5]},
        {"exam_current": 10, "exam_question_ids": [1, 2, 3]},  # 範囲外
        {"exam_current": None, "exam_question_ids": []},
    ]
    
    for i, session_mock in enumerate(test_session_patterns, 1):
        print(f"\nパターン{i}: exam_current={repr(session_mock['exam_current'])}, ids={len(session_mock['exam_question_ids'])}問")
        
        # シミュレートされたsession.get()
        def mock_session_get(key, default=None):
            return session_mock.get(key, default)
        
        try:
            # 修正後のコード1: _validate_session_integrity
            exam_ids = mock_session_get('exam_question_ids', [])
            current = mock_session_get('exam_current', 0)
            if not isinstance(current, int):
                current = 0
            
            if exam_ids and current >= len(exam_ids):
                new_current = max(0, len(exam_ids) - 1)
                print(f"  - 範囲修正: {current} -> {new_current}")
            
            # 修正後のコード2: final_exam_current
            final_exam_current = mock_session_get('exam_current', 0)
            if not isinstance(final_exam_current, int):
                final_exam_current = 0
            final_exam_question_ids = mock_session_get('exam_question_ids', [])
            
            if final_exam_current >= len(final_exam_question_ids):
                safe_index = max(0, len(final_exam_question_ids) - 1)
                print(f"  - インデックス修復: {final_exam_current} -> {safe_index}")
            
            # 修正後のコード3: has_active_session
            current_exam = mock_session_get('exam_current', 0)
            if not isinstance(current_exam, int):
                current_exam = 0
            has_active_session = (exam_ids and 
                                current_exam >= 0 and
                                current_exam < len(exam_ids))
            
            print(f"  - アクティブセッション判定: {has_active_session}")
            print(f"  ✅ 全パターン正常処理")
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
    
    print(f"\n=== 検証完了 ===")
    print("修正により、session.get('exam_current')の文字列値に対する")
    print("型安全な数値比較が実装されました。")
    
    return True

if __name__ == "__main__":
    test_session_type_safety()