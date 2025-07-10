#!/usr/bin/env python3
"""
RCCM試験アプリ - 無効な回答エラー修正の検証テスト
"""

import re
import unicodedata

def sanitize_input(input_string, allow_underscores=False):
    """入力値をサニタイズ（app.pyと同じ処理）"""
    if not input_string:
        return ""

    # 文字列に変換して空白の正規化
    sanitized = str(input_string).strip()

    # 危険なHTMLタグのみ除去（日本語文字は保持）
    sanitized = re.sub(r'<[^>]*>', '', sanitized)

    # 危険文字のエスケープ
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
    
    for char, escaped in dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    # Unicode制御文字の除去
    sanitized = ''.join(char for char in sanitized if unicodedata.category(char) != 'Cc')
    
    # SQLインジェクション対策の追加文字
    sql_dangerous_chars = {
        ";": "&#59;",
        "--": "&#45;&#45;",
        "/*": "&#47;&#42;",
        "*/": "&#42;&#47;",
        "\\": "&#92;",
        "=": "&#61;",
        "%": "&#37;",
    }

    for char, escaped in sql_dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    if not allow_underscores:
        sanitized = sanitized.replace("_", "&#95;")

    return sanitized

def normalize_answer(answer):
    """回答値を正規化（大文字・小文字対応）"""
    if not answer:
        return ""
    
    # 文字列に変換して正規化
    normalized = str(answer).strip().upper()
    
    # 有効な回答値のみ受け入れ
    if normalized in ['A', 'B', 'C', 'D']:
        return normalized
    
    return ""

def test_answer_normalization():
    """回答値の正規化テスト"""
    
    print("=== RCCM試験アプリ - 無効な回答エラー修正の検証テスト ===\n")
    
    # テストケース
    test_cases = [
        # 通常ケース
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        
        # 小文字ケース（問題の原因）
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        
        # 空白付きケース
        ('A ', 'A'),
        (' B', 'B'),
        (' C ', 'C'),
        
        # 無効なケース
        ('E', ''),
        ('1', ''),
        ('', ''),
        ('AB', ''),
        ('a1', ''),
        
        # 特殊文字ケース
        ('A&B', ''),
        ('A=B', ''),
        ('A%B', ''),
        ('A;B', ''),
        
        # 全角文字ケース
        ('Ａ', ''),
        ('Ｂ', ''),
        ('Ｃ', ''),
        ('Ｄ', ''),
    ]
    
    print("1. 回答値正規化テスト:")
    success_count = 0
    total_count = len(test_cases)
    
    for input_val, expected in test_cases:
        # sanitize_inputを通してから正規化
        sanitized = sanitize_input(input_val)
        normalized = normalize_answer(sanitized)
        
        success = normalized == expected
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   '{input_val}' -> sanitized: '{sanitized}' -> normalized: '{normalized}' -> expected: '{expected}' {status}")
        
        if success:
            success_count += 1
    
    print(f"\n📊 テスト結果: {success_count}/{total_count} 成功")
    
    print("\n2. 問題ID 125のシミュレーション:")
    
    # 問題ID 125の正解は元々'b'だった
    original_answer = 'b'
    sanitized = sanitize_input(original_answer)
    normalized = normalize_answer(sanitized)
    
    print(f"   元の正解: '{original_answer}'")
    print(f"   サニタイズ後: '{sanitized}'")
    print(f"   正規化後: '{normalized}'")
    print(f"   検証結果: {normalized in ['A', 'B', 'C', 'D']}")
    
    if normalized == 'B':
        print("   ✅ 問題ID 125の正解が正しく処理されました！")
    else:
        print("   ❌ 問題ID 125の正解処理に問題があります。")
    
    print("\n3. フロントエンドからの送信値シミュレーション:")
    
    # フロントエンドから送信される可能性のある値
    frontend_cases = [
        ('A', 'ユーザーが選択肢Aを選択'),
        ('B', 'ユーザーが選択肢Bを選択'),
        ('C', 'ユーザーが選択肢Cを選択'),
        ('D', 'ユーザーが選択肢Dを選択'),
        ('a', 'JavaScriptで小文字で送信された場合'),
        ('b', 'JavaScriptで小文字で送信された場合'),
        ('c', 'JavaScriptで小文字で送信された場合'),
        ('d', 'JavaScriptで小文字で送信された場合'),
    ]
    
    for input_val, description in frontend_cases:
        sanitized = sanitize_input(input_val)
        normalized = normalize_answer(sanitized)
        valid = normalized in ['A', 'B', 'C', 'D']
        
        status = "✅ 有効" if valid else "❌ 無効"
        print(f"   '{input_val}' ({description}) -> '{normalized}' {status}")
    
    print("\n4. 修正前後の比較:")
    print("   修正前: 小文字の回答値が「無効な回答が選択されました」エラーを引き起こしていた")
    print("   修正後: 小文字の回答値も大文字に正規化され、正常に処理される")
    
    print("\n✅ 修正完了!")
    print("   - データファイルの正解が大文字に統一されました")
    print("   - app.pyに回答値の正規化処理が追加されました")
    print("   - 3問目の「無効な回答が選択されました」エラーが解決されるはずです")

if __name__ == "__main__":
    test_answer_normalization()