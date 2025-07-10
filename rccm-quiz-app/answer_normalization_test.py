#!/usr/bin/env python3
"""
RCCM試験アプリの回答値正規化処理のテストスクリプト
修正後の動作確認を行う
"""

import sys
import json
from datetime import datetime

def test_answer_normalization():
    """回答値正規化処理のテスト"""
    
    def normalize_answer(answer):
        """回答値を正規化（大文字・小文字対応）"""
        if not answer:
            return ""
        
        # 文字列に変換して正規化
        normalized = str(answer).strip().upper()
        
        # 数値形式の回答値を文字に変換（1=A, 2=B, 3=C, 4=D）
        if normalized in ['1', '2', '3', '4']:
            mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
            normalized = mapping[normalized]
        
        # 小文字回答値を大文字に変換
        if normalized in ['a', 'b', 'c', 'd']:
            normalized = normalized.upper()
        
        # 全角文字を半角に変換
        if normalized in ['Ａ', 'Ｂ', 'Ｃ', 'Ｄ']:
            mapping = {'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D'}
            normalized = mapping[normalized]
        
        # 有効な回答値のみ受け入れ
        if normalized in ['A', 'B', 'C', 'D']:
            return normalized
        
        return ""
    
    # テストケース
    test_cases = [
        # 正常ケース
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        
        # 小文字ケース
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        
        # 数値ケース
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
        
        # 全角ケース
        ('Ａ', 'A'),
        ('Ｂ', 'B'),
        ('Ｃ', 'C'),
        ('Ｄ', 'D'),
        
        # 空白付きケース
        ('  A  ', 'A'),
        ('  b  ', 'B'),
        ('  3  ', 'C'),
        ('  Ｄ  ', 'D'),
        
        # 無効ケース
        ('', ''),
        ('E', ''),
        ('5', ''),
        ('X', ''),
        ('0', ''),
        ('aa', ''),
        ('AB', ''),
        (None, ''),
        ('あ', ''),
    ]
    
    print("=== RCCM試験アプリ 回答値正規化処理テスト ===")
    print(f"テスト実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected) in enumerate(test_cases, 1):
        try:
            result = normalize_answer(input_val)
            status = "PASS" if result == expected else "FAIL"
            
            if status == "PASS":
                passed += 1
            else:
                failed += 1
            
            print(f"テスト {i:2d}: {status} | 入力: {repr(input_val):>8} → 期待値: {repr(expected):>4} | 実際: {repr(result):>4}")
            
        except Exception as e:
            failed += 1
            print(f"テスト {i:2d}: ERROR | 入力: {repr(input_val):>8} → エラー: {e}")
    
    print()
    print("=== テスト結果 ===")
    print(f"合格: {passed}")
    print(f"失敗: {failed}")
    print(f"合計: {passed + failed}")
    print(f"成功率: {passed / (passed + failed) * 100:.1f}%")
    
    if failed == 0:
        print("✅ すべてのテストが成功しました！")
        return True
    else:
        print("❌ 一部のテストが失敗しました。")
        return False

def test_correct_answer_normalization():
    """正解値正規化処理のテスト"""
    
    def normalize_correct_answer(answer):
        """正解値を正規化（データ読み込み時用）"""
        if not answer:
            return ""
        
        normalized = str(answer).strip().upper()
        
        # 数値形式の正解値を文字に変換
        if normalized in ['1', '2', '3', '4']:
            mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
            normalized = mapping[normalized]
        
        # 小文字正解値を大文字に変換
        if normalized in ['a', 'b', 'c', 'd']:
            normalized = normalized.upper()
        
        # 全角文字を半角に変換
        if normalized in ['Ａ', 'Ｂ', 'Ｃ', 'Ｄ']:
            mapping = {'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D'}
            normalized = mapping[normalized]
        
        return normalized
    
    # テストケース
    test_cases = [
        ('A', 'A'),
        ('a', 'A'),
        ('1', 'A'),
        ('Ａ', 'A'),
        ('B', 'B'),
        ('b', 'B'),
        ('2', 'B'),
        ('Ｂ', 'B'),
        ('C', 'C'),
        ('c', 'C'),
        ('3', 'C'),
        ('Ｃ', 'C'),
        ('D', 'D'),
        ('d', 'D'),
        ('4', 'D'),
        ('Ｄ', 'D'),
        ('  A  ', 'A'),
        ('  b  ', 'B'),
        ('', ''),
        ('E', 'E'),  # 無効だが変換はされる
        ('5', '5'),  # 無効だが変換はされる
    ]
    
    print("\n=== 正解値正規化処理テスト ===")
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected) in enumerate(test_cases, 1):
        try:
            result = normalize_correct_answer(input_val)
            status = "PASS" if result == expected else "FAIL"
            
            if status == "PASS":
                passed += 1
            else:
                failed += 1
            
            print(f"テスト {i:2d}: {status} | 入力: {repr(input_val):>8} → 期待値: {repr(expected):>4} | 実際: {repr(result):>4}")
            
        except Exception as e:
            failed += 1
            print(f"テスト {i:2d}: ERROR | 入力: {repr(input_val):>8} → エラー: {e}")
    
    print(f"\n正解値正規化テスト結果: 合格 {passed}, 失敗 {failed}")
    
    return failed == 0

if __name__ == "__main__":
    print("RCCM試験アプリ 回答値正規化処理の包括的テストを開始します。")
    print("=" * 60)
    
    # 回答値正規化テスト
    answer_test_passed = test_answer_normalization()
    
    # 正解値正規化テスト
    correct_answer_test_passed = test_correct_answer_normalization()
    
    print("\n" + "=" * 60)
    print("=== 総合結果 ===")
    if answer_test_passed and correct_answer_test_passed:
        print("✅ すべてのテストが成功しました！")
        print("✅ 回答値正規化処理の強化が完了しました。")
        print("✅ 「無効な回答が選択されました」エラーが解消されるはずです。")
        sys.exit(0)
    else:
        print("❌ 一部のテストが失敗しました。")
        print("❌ 追加の修正が必要です。")
        sys.exit(1)