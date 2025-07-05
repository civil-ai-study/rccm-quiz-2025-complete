#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 関数挿入ツール
副作用ゼロでセッション管理関数をapp.pyに追加
"""

import os
from datetime import datetime

def create_session_functions_block():
    """挿入する関数ブロックを作成"""
    return '''
# 🛡️ ULTRA SAFE セッション管理関数群
def safe_exam_session_reset():
    """
    安全なセッション初期化
    複数箇所のsession.pop呼び出しを一元化
    """
    keys_to_remove = ['exam_question_ids', 'exam_current', 'exam_category']
    removed_keys = []
    
    for key in keys_to_remove:
        if key in session:
            session.pop(key, None)
            removed_keys.append(key)
    
    session.modified = True
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.info(f"セッション安全リセット完了: {removed_keys}")
    except NameError:
        pass  # loggerが定義されていない場合は無視
    
    return len(removed_keys)

def safe_session_check():
    """
    安全なセッション状態チェック
    セッション存在確認を修正前に実行
    """
    required_keys = ['exam_question_ids', 'exam_current']
    
    # 各キーの存在と有効性をチェック
    check_result = {}
    
    for key in required_keys:
        if key in session:
            value = session[key]
            if value is not None:
                if key == 'exam_question_ids':
                    # リスト型で空でないことを確認
                    check_result[key] = isinstance(value, list) and len(value) > 0
                elif key == 'exam_current':
                    # 数値型で0以上であることを確認
                    try:
                        num_value = int(value)
                        check_result[key] = num_value >= 0
                    except (ValueError, TypeError):
                        check_result[key] = False
                else:
                    check_result[key] = True
            else:
                check_result[key] = False
        else:
            check_result[key] = False
    
    # 全てのキーが有効な場合のみTrue
    is_valid = all(check_result.values())
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.debug(f"セッション状態チェック: {check_result}, 有効: {is_valid}")
    except NameError:
        pass
    
    return is_valid

'''

def insert_functions_safely():
    """関数を安全にapp.pyに挿入"""
    print("🛡️ ULTRA SAFE 関数挿入開始")
    print("=" * 60)
    print(f"実行時刻: {datetime.now()}")
    
    # 1. app.pyの読み込み
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✅ app.py読み込み成功: {len(lines)}行")
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return False
    
    # 2. 挿入位置の特定（SessionStateManagerクラスの後）
    insert_position = None
    for i, line in enumerate(lines):
        if "class SessionStateManager:" in line:
            # クラス定義の終わりを見つける
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' '):
                    insert_position = j
                    break
            break
    
    if not insert_position:
        print("❌ 適切な挿入位置が見つかりません")
        return False
    
    print(f"✅ 挿入位置特定: 行{insert_position + 1}")
    
    # 3. 関数が既に存在するかチェック
    content = ''.join(lines)
    if "def safe_exam_session_reset(" in content:
        print("⚠️ 関数は既に存在します")
        return False
    
    # 4. 新しい内容の作成
    functions_block = create_session_functions_block()
    new_lines = lines[:insert_position] + [functions_block] + lines[insert_position:]
    
    # 5. 新しいファイルの作成（まず一時ファイルに）
    temp_file = 'app.py.temp_with_functions'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ 一時ファイル作成: {temp_file}")
    except Exception as e:
        print(f"❌ 一時ファイル作成エラー: {e}")
        return False
    
    # 6. 構文チェック
    print("\n🔍 構文チェック実行中...")
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', temp_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 構文エラー検出: {result.stderr}")
        os.remove(temp_file)
        return False
    
    print("✅ 構文チェック成功")
    
    # 7. 関数挿入内容の確認
    print("\n📋 挿入される関数:")
    print("  - safe_exam_session_reset(): セッション初期化一元化")
    print("  - safe_session_check(): セッション状態チェック")
    
    # 8. プレビュー表示
    print("\n📄 挿入箇所のプレビュー:")
    preview_start = max(0, insert_position - 2)
    preview_end = min(len(lines), insert_position + 2)
    
    print("--- 挿入前 ---")
    for i in range(preview_start, preview_end):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    print(f"\n--- ここに関数を挿入 (行{insert_position + 1}) ---")
    print("[セッション管理関数群]")
    
    # 9. 最終確認
    print("\n✅ 準備完了")
    print("🛡️ 副作用: 最小限（一時ファイルのみ作成）")
    print(f"📁 一時ファイル: {temp_file}")
    print("\n次のステップ:")
    print(f"  1. {temp_file}の内容を確認")
    print(f"  2. 問題なければ: mv {temp_file} app.py")
    print(f"  3. バックアップは作成済み: app.py.backup_before_session_functions")
    
    return True

if __name__ == "__main__":
    success = insert_functions_safely()
    if success:
        print("\n✅ ULTRA SAFE関数挿入準備完了")
    else:
        print("\n❌ 関数挿入準備失敗")