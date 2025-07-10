#!/usr/bin/env python3
"""
RCCM試験アプリ - 「無効な回答が選択されました」エラー修正ツール
"""

import os
import csv
import re
from datetime import datetime

def fix_csv_answer_case(csv_file_path):
    """CSVファイルの回答列を大文字に修正"""
    
    backup_path = f"{csv_file_path}.backup_answer_case_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # バックアップを作成
    with open(csv_file_path, 'r', encoding='utf-8') as src:
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    print(f"バックアップ作成: {backup_path}")
    
    # CSVファイルを読み込み、修正
    fixed_rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 9:  # 最低9列必要
                # 9列目（インデックス8）が正解列
                if row[8] in ['a', 'b', 'c', 'd']:
                    row[8] = row[8].upper()
                    print(f"修正: ID {row[0]} - 正解 '{row[8].lower()}' -> '{row[8]}'")
            fixed_rows.append(row)
    
    # 修正したデータを書き戻し
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_rows)
    
    return len([row for row in fixed_rows if len(row) >= 9 and row[8] in ['A', 'B', 'C', 'D']])

def generate_app_py_fix():
    """app.pyの修正コードを生成"""
    
    fix_code = '''
# 回答値の正規化処理を追加（大文字・小文字対応）
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

# 既存の回答検証ロジックを以下に置き換える：
# if answer not in ['A', 'B', 'C', 'D']:
#     logger.warning(f"🚨 無効な回答値: {answer} (元: {raw_answer})")
#     return render_template('error.html',
#                            error="無効な回答が選択されました。",
#                            error_type="invalid_input")

# 修正後の回答検証ロジック：
answer = sanitize_input(raw_answer)
normalized_answer = normalize_answer(answer)

if not normalized_answer:
    logger.warning(f"🚨 無効な回答値: {answer} (元: {raw_answer})")
    return render_template('error.html',
                           error="無効な回答が選択されました。",
                           error_type="invalid_input")

# 正規化された回答値を使用
answer = normalized_answer
'''
    
    return fix_code

def main():
    """メイン実行関数"""
    
    print("=== RCCM試験アプリ - 無効な回答エラー修正ツール ===\n")
    
    # データディレクトリのパス
    data_dir = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data"
    
    if not os.path.exists(data_dir):
        print(f"❌ データディレクトリが見つかりません: {data_dir}")
        return
    
    # CSVファイル一覧を取得
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"📁 CSVファイル数: {len(csv_files)}")
    
    total_fixed = 0
    
    # 各CSVファイルの正解列を修正
    for csv_file in csv_files:
        csv_path = os.path.join(data_dir, csv_file)
        print(f"\n🔧 修正中: {csv_file}")
        
        try:
            fixed_count = fix_csv_answer_case(csv_path)
            total_fixed += fixed_count
            print(f"✅ 修正完了: {csv_file} ({fixed_count}件)")
        except Exception as e:
            print(f"❌ 修正失敗: {csv_file} - {e}")
    
    print(f"\n📊 修正サマリー:")
    print(f"   - 処理ファイル数: {len(csv_files)}")
    print(f"   - 修正された問題数: {total_fixed}")
    
    # app.pyの修正コードを出力
    print(f"\n🛠️  app.py修正コード:")
    print(generate_app_py_fix())
    
    print(f"\n✅ 修正完了!")
    print(f"   次の手順:")
    print(f"   1. 生成されたコードをapp.pyに適用")
    print(f"   2. アプリケーションを再起動")
    print(f"   3. 3問目で「無効な回答が選択されました」エラーが解決されることを確認")

if __name__ == "__main__":
    main()