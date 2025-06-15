#!/usr/bin/env python3
import pandas as pd
import csv

def final_verification(filepath):
    print(f'=== {filepath} の最終検証 ===')
    try:
        # pandasで読み込み
        df = pd.read_csv(filepath)
        print(f'pandas読み込み成功: {len(df)}行, {len(df.columns)}列')
        print(f'列名: {list(df.columns)}')
        
        # csv.readerでも検証
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            line_count = 0
            problem_count = 0
            
            for line_num, row in enumerate(reader, start=2):
                line_count += 1
                if len(row) != 12:
                    problem_count += 1
                    print(f'問題行: {line_num}, フィールド数: {len(row)}')
            
            print(f'CSV reader検証: 総行数 {line_count}, 問題行数 {problem_count}')
            
            if problem_count == 0:
                print('✓ ファイルは完全に修正されました')
                return True
            else:
                print('✗ まだ問題があります')
                return False
                
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == "__main__":
    # 両ファイルの最終検証
    result_2013 = final_verification('data/4-2_2013.csv')
    result_2014 = final_verification('data/4-2_2014.csv')

    print(f'\n=== 最終結果 ===')
    print(f'2013年ファイル: {"成功" if result_2013 else "失敗"}')
    print(f'2014年ファイル: {"成功" if result_2014 else "失敗"}')
    print(f'全体: {"すべて成功" if result_2013 and result_2014 else "一部失敗"}')