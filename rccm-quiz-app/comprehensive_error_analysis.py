#!/usr/bin/env python3
"""
建設環境部門とその他の部門で発生する「無効な回答が選択されました」エラーの包括的分析
"""

import os
import csv
import logging
from collections import defaultdict, Counter

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def analyze_csv_data():
    """すべてのCSVファイルの正解値を分析"""
    print("=== CSVファイルの正解値分析 ===\n")
    
    # データディレクトリのCSVファイル一覧
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f.startswith('4-')]
    
    department_answer_stats = defaultdict(Counter)
    invalid_answers = []
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    department = row.get('category', 'Unknown')
                    correct_answer = row.get('correct_answer', '').strip()
                    question_id = row.get('id', '')
                    
                    # 正解値を大文字に変換して統計を取る
                    normalized_answer = correct_answer.upper()
                    department_answer_stats[department][normalized_answer] += 1
                    
                    # 無効な正解値をチェック
                    if normalized_answer not in ['A', 'B', 'C', 'D']:
                        invalid_answers.append({
                            'file': csv_file,
                            'row': row_num,
                            'id': question_id,
                            'department': department,
                            'answer': correct_answer,
                            'normalized': normalized_answer
                        })
                        
        except Exception as e:
            logger.error(f"ファイル読み込みエラー {csv_file}: {e}")
    
    # 部門別の正解値分布を表示
    print("部門別正解値分布:")
    for dept, answer_counts in sorted(department_answer_stats.items()):
        print(f"\n{dept}:")
        total = sum(answer_counts.values())
        for answer, count in sorted(answer_counts.items()):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {answer}: {count} ({percentage:.1f}%)")
    
    # 無効な正解値を表示
    if invalid_answers:
        print("\n\n=== 無効な正解値が見つかりました ===")
        for item in invalid_answers[:20]:  # 最初の20件
            print(f"\nファイル: {item['file']}")
            print(f"  行番号: {item['row']}")
            print(f"  問題ID: {item['id']}")
            print(f"  部門: {item['department']}")
            print(f"  正解値: '{item['answer']}' → '{item['normalized']}'")
        
        if len(invalid_answers) > 20:
            print(f"\n... 他 {len(invalid_answers) - 20} 件の無効な正解値")
    else:
        print("\n✅ すべての正解値は有効です (A, B, C, D)")


def check_specific_questions():
    """問題が報告されている特定の問題をチェック"""
    print("\n\n=== 特定問題の詳細チェック ===\n")
    
    # 建設環境部門の問題を重点的にチェック
    construction_env_questions = []
    
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f.startswith('4-2')]
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('category', '') == '建設環境':
                        construction_env_questions.append({
                            'file': csv_file,
                            'id': row.get('id', ''),
                            'question': row.get('question', '')[:50] + '...',
                            'correct_answer': row.get('correct_answer', ''),
                            'option_a': row.get('option_a', '')[:30],
                            'option_b': row.get('option_b', '')[:30],
                            'option_c': row.get('option_c', '')[:30],
                            'option_d': row.get('option_d', '')[:30]
                        })
        except Exception as e:
            logger.error(f"ファイル読み込みエラー {csv_file}: {e}")
    
    # 建設環境部門の問題を表示
    print(f"建設環境部門の問題数: {len(construction_env_questions)}")
    
    # ID 122周辺の問題を詳しく見る
    for q in construction_env_questions[:10]:
        print(f"\n問題ID: {q['id']} ({q['file']})")
        print(f"  正解: {q['correct_answer']}")
        print(f"  A: {q['option_a']}")
        print(f"  B: {q['option_b']}")
        print(f"  C: {q['option_c']}")
        print(f"  D: {q['option_d']}")


def analyze_potential_causes():
    """エラーの潜在的原因を分析"""
    print("\n\n=== エラーの潜在的原因分析 ===\n")
    
    causes = [
        {
            "原因": "CSVファイルの正解値に特殊文字が含まれている",
            "チェック方法": "correct_answer列に空白、改行、特殊文字がないか確認",
            "解決策": "CSVファイルの正解値を修正"
        },
        {
            "原因": "HTMLフォームのvalue属性が誤っている",
            "チェック方法": "テンプレートファイルのradioボタンのvalue属性を確認",
            "解決策": "value属性を'A', 'B', 'C', 'D'に統一"
        },
        {
            "原因": "JavaScriptが回答値を変更している",
            "チェック方法": "submitイベントで送信される値をconsole.logで確認",
            "解決策": "JavaScriptコードを修正"
        },
        {
            "原因": "sanitize_input関数が過剰にエスケープしている",
            "チェック方法": "ログでsanitize前後の値を確認",
            "解決策": "回答値には特別な処理を適用しない"
        },
        {
            "原因": "セッション管理の問題で異なる問題の回答が混在",
            "チェック方法": "セッションの問題IDと回答の問題IDが一致するか確認",
            "解決策": "セッション管理の見直し"
        }
    ]
    
    for i, cause in enumerate(causes, 1):
        print(f"\n{i}. {cause['原因']}")
        print(f"   チェック方法: {cause['チェック方法']}")
        print(f"   解決策: {cause['解決策']}")


def suggest_fix():
    """修正案の提案"""
    print("\n\n=== 推奨される修正案 ===\n")
    
    print("1. app.pyのsanitize_input関数の修正:")
    print("""
def sanitize_answer_value(answer):
    \"\"\"回答値専用のサニタイズ（最小限の処理）\"\"\"
    if not answer:
        return ""
    
    # 文字列に変換して前後の空白を削除
    return str(answer).strip()
""")
    
    print("\n2. submit_answer関数での回答値処理の修正:")
    print("""
# 回答値は特別扱い（過剰なサニタイズを避ける）
raw_answer = request.form.get('answer')
if raw_answer:
    # 回答値専用の軽量サニタイズ
    answer = sanitize_answer_value(raw_answer)
else:
    answer = ""
""")
    
    print("\n3. デバッグログの追加:")
    print("""
logger.info(f"回答値デバッグ - Raw: {repr(raw_answer)}, Sanitized: {repr(answer)}, Normalized: {repr(normalized_answer)}")
""")


if __name__ == "__main__":
    analyze_csv_data()
    check_specific_questions()
    analyze_potential_causes()
    suggest_fix()