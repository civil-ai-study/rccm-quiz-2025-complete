#!/usr/bin/env python3
"""
建設環境部門で発生する「無効な回答が選択されました」エラーの詳細デバッグ
"""

import re
import unicodedata
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def sanitize_input(input_string, allow_underscores=False):
    """app.pyのsanitize_input関数をそのまま再現"""
    if not input_string:
        return ""

    # 文字列に変換して空白の正規化
    sanitized = str(input_string).strip()

    # 危険なHTMLタグのみ除去（日本語文字は保持）
    sanitized = re.sub(r'<[^>]*>', '', sanitized)

    # 🔥 ULTRA SYNC SECURITY FIX: 包括的なXSS対策（日本語対応）
    # すべての危険文字を適切にエスケープ
    dangerous_chars = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        "'": "&#39;",
        '"': "&quot;",
        "\n": "&#10;",
        "\r": "&#13;",
        "\t": "&#9;"
    }
    
    # 日本語文字も含めて一律エスケープ処理
    for char, escaped in dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    # Unicode制御文字の除去
    sanitized = ''.join(char for char in sanitized if unicodedata.category(char) != 'Cc')
    
    # SQLインジェクション対策の追加文字
    sql_dangerous_chars = {
        ";": "&#59;",      # セミコロン
        "--": "&#45;&#45;",  # SQLコメント
        "/*": "&#47;&#42;",  # SQLコメント開始
        "*/": "&#42;&#47;",  # SQLコメント終了
        "\\": "&#92;",     # バックスラッシュ
        "=": "&#61;",      # 等号（WHERE句攻撃対策）
        "%": "&#37;",      # パーセント（LIKE句攻撃対策）
    }

    # SQLインジェクション対策の適用
    for char, escaped in sql_dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    return sanitized


def normalize_answer(answer):
    """app.pyのnormalize_answer関数を再現"""
    if not answer:
        return ""
    
    # 文字列に変換して正規化
    normalized = str(answer).strip().upper()
    
    # 数値形式の回答値を文字に変換（1=A, 2=B, 3=C, 4=D）
    if normalized in ['1', '2', '3', '4']:
        mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        normalized = mapping[normalized]
        logger.info(f"数値回答値を文字に変換: {answer} → {normalized}")
    
    # 小文字回答値を大文字に変換
    if normalized in ['a', 'b', 'c', 'd']:
        normalized = normalized.upper()
        logger.info(f"小文字回答値を大文字に変換: {answer} → {normalized}")
    
    # 全角文字を半角に変換
    if normalized in ['Ａ', 'Ｂ', 'Ｃ', 'Ｄ']:
        mapping = {'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D'}
        normalized = mapping[normalized]
        logger.info(f"全角回答値を半角に変換: {answer} → {normalized}")
    
    # 有効な回答値のみ受け入れ
    if normalized in ['A', 'B', 'C', 'D']:
        return normalized
    
    # 無効な回答値の詳細ログ
    logger.warning(f"無効な回答値: '{answer}' (正規化後: '{normalized}')")
    return ""


def test_answer_validation():
    """回答値検証処理をテスト"""
    print("=== 回答値検証デバッグ ===\n")
    
    # テストケース
    test_cases = [
        # 正常なケース
        "A", "B", "C", "D",
        "a", "b", "c", "d",
        "1", "2", "3", "4",
        "Ａ", "Ｂ", "Ｃ", "Ｄ",
        # エッジケース
        " A ", " b ", "  C  ", "   d   ",
        "A\n", "B\r", "C\t", "D ",
        # 異常なケース
        "E", "F", "5", "0",
        "AA", "BB", "abc", "選択肢A",
        "<script>alert('A')</script>",
        "A; DROP TABLE questions;",
        "A' OR '1'='1",
        "",
        None,
    ]
    
    for test_input in test_cases:
        print(f"\n入力値: {repr(test_input)}")
        
        # まずsanitize_inputを通す
        if test_input is not None:
            sanitized = sanitize_input(test_input)
            print(f"  → sanitize後: {repr(sanitized)}")
            
            # 次にnormalize_answerを通す
            normalized = normalize_answer(sanitized)
            print(f"  → normalize後: {repr(normalized)}")
            
            # 最終的な判定
            if normalized:
                print(f"  ✅ 有効な回答値として受け入れられます: {normalized}")
            else:
                print(f"  ❌ 無効な回答値として拒否されます")
        else:
            print(f"  ❌ Noneは無効な入力です")


def test_problematic_answers():
    """問題が発生する可能性のある回答値を重点的にテスト"""
    print("\n\n=== 問題発生パターンの分析 ===\n")
    
    # HTMLフォームから送信される可能性のある値
    form_values = [
        "A",      # 正常
        "B",      # 正常
        "C",      # 正常  
        "D",      # 正常
        "option_a",  # ラジオボタンのvalue属性が間違っている場合
        "option_b",
        "option_c", 
        "option_d",
        "A ",     # 末尾に空白
        " A",     # 先頭に空白
        "=A",     # 等号が含まれる（sanitizeで変換される）
        "%A",     # パーセントが含まれる（sanitizeで変換される）
    ]
    
    for value in form_values:
        print(f"\nフォーム送信値: {repr(value)}")
        
        # sanitize処理
        sanitized = sanitize_input(value)
        print(f"  sanitize後: {repr(sanitized)}")
        
        # normalize処理
        normalized = normalize_answer(sanitized)
        print(f"  normalize後: {repr(normalized)}")
        
        # 判定結果
        if normalized:
            print(f"  → ✅ 有効")
        else:
            print(f"  → ❌ 無効（エラー発生）")
            
            # エラー原因の分析
            if "&#" in sanitized:
                print(f"     原因: sanitize_inputでエスケープされた文字が含まれている")
            elif len(sanitized) > 1:
                print(f"     原因: 1文字を超える文字列")
            else:
                print(f"     原因: 予期しない文字")


if __name__ == "__main__":
    test_answer_validation()
    test_problematic_answers()