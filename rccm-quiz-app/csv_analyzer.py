#!/usr/bin/env python3
import csv
import re

def analyze_csv_file(filepath):
    """CSVファイルの問題行を詳細に分析する"""
    print(f'=== {filepath} の調査 ===')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print(f'ヘッダー: {headers}')
            print(f'ヘッダー数: {len(headers)}')
            
            problem_lines = []
            all_lines = []
            
            for i, row in enumerate(reader, start=2):
                all_lines.append((i, row))
                if len(row) != 12:
                    problem_lines.append((i, len(row), row))
                    if len(problem_lines) <= 10:
                        print(f'行 {i}: フィールド数 {len(row)}')
            
            print(f'総行数: {len(all_lines)}')
            print(f'問題行の総数: {len(problem_lines)}')
            
            # 問題行の詳細分析
            if problem_lines:
                print('\n=== 問題行の詳細分析 ===')
                for line_num, field_count, row in problem_lines[:3]:
                    print(f'\n行 {line_num} (フィールド数: {field_count}):')
                    for j, field in enumerate(row):
                        print(f'  フィールド {j+1}: {repr(field[:100])}{"..." if len(field) > 100 else ""}')
            
            return problem_lines, all_lines
                    
    except Exception as e:
        print(f'エラー: {e}')
        return [], []

def fix_csv_problems(filepath, problem_lines, all_lines):
    """CSVの問題を修正する"""
    print(f'\n=== {filepath} の修正開始 ===')
    
    fixed_lines = []
    
    for line_num, row in all_lines:
        if len(row) == 12:
            # 正常な行はそのまま
            fixed_lines.append(row)
        else:
            # 問題行を修正
            print(f'修正中: 行 {line_num} (フィールド数: {len(row)})')
            fixed_row = fix_row(row, line_num)
            fixed_lines.append(fixed_row)
    
    return fixed_lines

def fix_row(row, line_num):
    """個別の行を修正する"""
    # 全フィールドを結合して再分割
    full_text = ','.join(row)
    
    # カンマやその他の問題文字を修正
    full_text = full_text.replace('\n', ' ').replace('\r', ' ')
    full_text = re.sub(r'\s+', ' ', full_text)  # 複数スペースを単一スペースに
    
    # 12フィールドに分割を試行
    # パターン1: 基本的な分割
    parts = full_text.split(',')
    
    if len(parts) > 12:
        # フィールドが多すぎる場合、説明文や選択肢内のカンマを処理
        # 最初の6フィールド（ID、年、分野、問題番号、問題文、図面）は固定
        fixed_parts = parts[:6]
        
        # 残りを4つの選択肢（A、B、C、D）と正解、解説に分割
        remaining = ','.join(parts[6:])
        
        # 選択肢を識別（A)、B)、C)、D) パターン）
        choice_pattern = r'([ABCD]\))'
        matches = list(re.finditer(choice_pattern, remaining))
        
        if len(matches) >= 4:
            choices = []
            for i in range(4):
                start = matches[i].start()
                end = matches[i+1].start() if i < 3 else len(remaining)
                choice_text = remaining[start:end].strip()
                if choice_text.endswith(','):
                    choice_text = choice_text[:-1]
                choices.append(choice_text)
            
            # 残りの部分（正解と解説）
            after_choices = remaining[matches[3].end():].strip()
            if after_choices.startswith(','):
                after_choices = after_choices[1:]
            
            remaining_parts = after_choices.split(',', 1)  # 正解と解説に分割
            
            fixed_parts.extend(choices)
            fixed_parts.extend(remaining_parts)
        else:
            # パターンマッチングが失敗した場合、末尾から逆算
            fixed_parts.extend(parts[6:])
    
    elif len(parts) < 12:
        # フィールドが少ない場合、空フィールドで補完
        fixed_parts = parts + [''] * (12 - len(parts))
    else:
        fixed_parts = parts
    
    # 12フィールドに調整
    if len(fixed_parts) > 12:
        fixed_parts = fixed_parts[:12]
    elif len(fixed_parts) < 12:
        fixed_parts.extend([''] * (12 - len(fixed_parts)))
    
    return fixed_parts

if __name__ == "__main__":
    # 2013年ファイルの分析
    problem_lines_2013, all_lines_2013 = analyze_csv_file('data/4-2_2013.csv')
    
    # 2014年ファイルの分析
    problem_lines_2014, all_lines_2014 = analyze_csv_file('data/4-2_2014.csv')