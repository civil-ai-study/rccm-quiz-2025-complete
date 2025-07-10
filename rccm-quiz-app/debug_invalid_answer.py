#!/usr/bin/env python3
"""
RCCM試験アプリ - 3問目「無効な回答が選択されました」エラー調査ツール
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

def debug_answer_validation():
    """回答値の検証プロセスをデバッグ"""
    
    print("=== RCCM試験アプリ - 3問目「無効な回答が選択されました」エラー調査 ===\n")
    
    # 通常の回答値のテスト
    valid_answers = ['A', 'B', 'C', 'D']
    print("1. 通常の回答値テスト:")
    for answer in valid_answers:
        sanitized = sanitize_input(answer)
        is_valid = sanitized in ['A', 'B', 'C', 'D']
        print(f"   '{answer}' -> sanitized: '{sanitized}' -> valid: {is_valid}")
    
    print("\n2. 問題のある回答値テスト:")
    
    # 潜在的な問題のあるケース
    problematic_cases = [
        'a',  # 小文字
        'b',  # 小文字
        'c',  # 小文字
        'd',  # 小文字
        'A ',  # 末尾にスペース
        ' B',  # 先頭にスペース
        'A\n',  # 改行文字
        'B\r',  # キャリッジリターン
        'C\t',  # タブ文字
        'A&B',  # 特殊文字
        'A=B',  # 等号
        'A%B',  # パーセント
        'A;B',  # セミコロン
        'A--B',  # SQLコメント
        'A/*B',  # SQLコメント開始
        'A*/B',  # SQLコメント終了
        'A\\B',  # バックスラッシュ
        'A"B',  # ダブルクォート
        "A'B",  # シングルクォート
        'A<B',  # 小なり
        'A>B',  # 大なり
        'A_B',  # アンダースコア
        'Ａ',  # 全角A
        'Ｂ',  # 全角B
        'Ｃ',  # 全角C
        'Ｄ',  # 全角D
        '',    # 空文字
        None,  # None
    ]
    
    for case in problematic_cases:
        try:
            sanitized = sanitize_input(case)
            is_valid = sanitized in ['A', 'B', 'C', 'D']
            print(f"   '{case}' -> sanitized: '{sanitized}' -> valid: {is_valid}")
        except Exception as e:
            print(f"   '{case}' -> ERROR: {e}")
    
    print("\n3. 問題ID 125のデータ確認:")
    
    # 問題ID 125の情報
    question_125_data = "125,共通,,濃度の分からない食塩水が200gある。これに10％の食塩水を300g混ぜたら8％の食塩水になった。はじめの食塩水の濃度として正しいものをa～dのなかから選びなさい。,4%,5%,6%,7%,b,水理学の基本原理に基づいて、流体の運動と静止状態を解析します。ベルヌーイの定理と連続の式が基本となります。,河川砂防技術基準,標準"
    
    fields = question_125_data.split(',')
    print(f"   問題ID: {fields[0]}")
    print(f"   部門: {fields[1]}")
    print(f"   年度: {fields[2]}")
    print(f"   問題文: {fields[3]}")
    print(f"   選択肢A: {fields[4]}")
    print(f"   選択肢B: {fields[5]}")
    print(f"   選択肢C: {fields[6]}")
    print(f"   選択肢D: {fields[7]}")
    print(f"   正解: {fields[8]}")
    
    # 正解が小文字の'b'になっている問題
    correct_answer = fields[8]
    print(f"\n   ⚠️  正解が小文字: '{correct_answer}'")
    print(f"   サニタイズ後: '{sanitize_input(correct_answer)}'")
    print(f"   検証結果: {sanitize_input(correct_answer) in ['A', 'B', 'C', 'D']}")
    
    print("\n4. 考えられる根本原因:")
    print("   - 問題データの正解が小文字（'b'）になっている")
    print("   - フロントエンドから小文字で送信されている可能性")
    print("   - sanitize_input関数が文字を変換している可能性")
    print("   - 3問目特有のセッション状態の問題")
    
    print("\n5. 推奨される修正策:")
    print("   A. 回答値の正規化処理を追加（小文字を大文字に変換）")
    print("   B. データファイルの正解を大文字に統一")
    print("   C. フロントエンドの送信値を大文字に変換")
    print("   D. 検証ロジックで大文字・小文字を区別しない")

if __name__ == "__main__":
    debug_answer_validation()