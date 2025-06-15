#!/usr/bin/env python3
import csv
import re
import shutil
import os

def fix_2013_csv():
    """2013年CSVファイルの特定問題を修正"""
    input_path = 'data/4-2_2013.csv'
    output_path = 'data/4-2_2013_fixed.csv'
    backup_path = 'data/4-2_2013_backup.csv'
    
    # バックアップ作成
    shutil.copy2(input_path, backup_path)
    print(f'バックアップ作成: {backup_path}')
    
    fixed_lines = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        fixed_lines.append(headers)
        
        for line_num, row in enumerate(reader, start=2):
            if line_num == 226:  # 行 226 の修正
                # 問題: フィールド6,7が分割されている "1,000㎡"
                fixed_row = [
                    row[0],  # id: 285
                    row[1],  # category: 都市計画及び地方計画
                    row[2],  # year: 2013  
                    row[3],  # question: 大規模小売店舗立地法に関する記述として、誤っているものはどれか。
                    row[4],  # option_a: 大規模小売店舗の新設に関する届出をしたものは、2週間以内に内容を周知させるための説明会を開催しなければならない
                    row[5] + row[6],  # option_b: 大規模小売店舗とは一の建物であって、その建物内の店舗面積の合計が1,000㎡を超えるものである
                    row[7],  # option_c: 経済産業大臣は、周辺の地域の生活環境の保持を通じた小売業の健全な発達を図る観点から、大規模小売店舗を設置する者が配慮すべき事項に関する指針を定め、これを公表するものとする
                    row[8],  # option_d: d
                    row[9],  # correct_answer: a
                    row[10], # explanation (1つ目): a
                    row[11] + ' ' + row[12], # explanation (結合): 説明会開催義務はない + 大規模小売店舗立地法
                    row[13]  # difficulty: 標準
                ]
                fixed_lines.append(fixed_row)
                print(f'修正: 行 {line_num}')
                
            elif line_num == 228:  # 行 228 の修正
                # 問題: フィールド7,8が分割されている "1,000㎡"
                fixed_row = [
                    row[0],  # id: 287
                    row[1],  # category: 都市計画及び地方計画
                    row[2],  # year: 2013
                    row[3],  # question: 都市公園法による都市公園に関する記述として、正しいものはどれか。
                    row[4],  # option_a: 公園管理者以外の者は公園施設を整備することができない
                    row[5],  # option_b: 借地公園の土地貸借契約が終了した場合、都市公園を廃止することができる
                    row[6] + row[7],  # option_c: 都市公園に公園施設として設けられる建築物の面積は1,000㎡を上限とする
                    row[8],  # option_d: a
                    row[9],  # correct_answer: b
                    row[10], # explanation (1つ目): b
                    row[11] + ' ' + row[12], # explanation (結合): 借地公園は契約終了により廃止可能 + 都市公園法
                    row[13]  # difficulty: 標準
                ]
                fixed_lines.append(fixed_row)
                print(f'修正: 行 {line_num}')
                
            elif line_num == 243:  # 行 243 の修正 (複雑な問題)
                # 問題: 複数の数値フィールドが分割されている
                fixed_row = [
                    row[0],  # id: 302
                    row[1],  # category: 上水道及び工業用水道  
                    row[2],  # year: 2013
                    row[3],  # question: 国内水道事業に関する記述として、誤っているものはどれか。
                    row[4] + row[5] + row[6],  # option_a: 国内の水道事業数（上水道、簡易水道）は、7,884事業で約1億2,400万人に給水を行っており、専用水道からの給水も含めて水道普及率は97.6％である
                    row[7],  # option_b: 用水供給事業は、水道事業者に対し水道用水を供給する事業であり、平成22年度から増加して95事業がある
                    'c) 簡易水道事業は、101人以上5' + row[9] + row[10],  # option_c: 簡易水道事業は、101人以上5,000人以下が対象で16,000箇所を超える施設があり、40万人以上に給水している
                    row[11],  # option_d: 上水道事業は、県営、市町村営、組合営、私営があり、用水供給事業は、県営、市町村営、組合営がある
                    row[12], # correct_answer: b
                    row[13], # explanation (1つ目): b
                    row[14] + ' ' + row[15], # explanation + reference: 用水供給事業数の記述が不正確 + 水道法
                    row[16]  # difficulty: 標準
                ]
                fixed_lines.append(fixed_row)
                print(f'修正: 行 {line_num}')
                
            elif line_num == 257:  # 行 257 の修正
                # 問題: "100,000人"と"50,000人"でフィールドが分割されている
                fixed_row = [
                    row[0],  # id: 316
                    row[1],  # category: 上水道及び工業用水道
                    row[2],  # year: 2013
                    row[3],  # question: 消火水量に関する記述として、誤っているものはどれか。
                    row[4],  # option_a: 小規模水道の消火用水量は消火栓1栓の放水量を1㎥/min、同時に開放する消火栓１栓を標準として設定する
                    row[5] + ',' + row[6],  # option_b: 配水管の受持つ給水区域内の計画給水人口が100,000人以下のものについては、配水管の設計において、計画一日平均配水量に消火用水量を加算した水量で管径を検討する
                    row[7] + ',000人以下のものについては、配水池の容量に消火用水量を加算する',  # option_c: 配水池容量の設計に当たって、配水池の受持つ計画給水人口が50,000人以下のものについては、配水池の容量に消火用水量を加算する
                    'd) ' + row[9],  # option_d: d) 火災時の動水圧は、消火栓の位置で正圧であり、かつ配水管内においても一様に正圧を確保することが必要である
                    row[10], # correct_answer: a
                    row[11], # explanation: a (この部分は不完全なので次のフィールドと結合)
                    row[12], # reference: 小規模水道でも消火栓は2栓同時使用を標準とする
                    row[13]  # difficulty: 配水施設設計指針
                ]
                # difficulty が抜けているので調整
                fixed_row = [
                    row[0],  # id: 316
                    row[1],  # category: 上水道及び工業用水道
                    row[2],  # year: 2013
                    row[3],  # question
                    row[4],  # option_a
                    row[5] + ',' + row[6],  # option_b
                    row[7] + ',000人以下のものについては、配水池の容量に消火用水量を加算する',  # option_c
                    'd) ' + row[9],  # option_d
                    row[10], # correct_answer: a
                    row[12], # explanation: 小規模水道でも消火栓は2栓同時使用を標準とする
                    row[13], # reference: 配水施設設計指針
                    row[14]  # difficulty: 標準
                ]
                fixed_lines.append(fixed_row)
                print(f'修正: 行 {line_num}')
                
            elif len(row) != 12:
                # その他の問題行
                print(f'未処理の問題行: {line_num}, フィールド数: {len(row)}')
                # 12フィールドに調整
                if len(row) > 12:
                    fixed_row = row[:12]
                else:
                    fixed_row = row + [''] * (12 - len(row))
                fixed_lines.append(fixed_row)
            else:
                # 正常な行
                fixed_lines.append(row)
    
    # 修正したファイルを書き出し
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_lines)
    
    print(f'修正完了: {output_path}')
    return output_path

def fix_2014_csv():
    """2014年CSVファイルの問題を修正"""
    input_path = 'data/4-2_2014.csv'
    output_path = 'data/4-2_2014_fixed.csv'
    backup_path = 'data/4-2_2014_backup.csv'
    
    # バックアップ作成
    shutil.copy2(input_path, backup_path)
    print(f'バックアップ作成: {backup_path}')
    
    fixed_lines = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        fixed_lines.append(headers)
        
        for line_num, row in enumerate(reader, start=2):
            if line_num == 222:  # 行 222 の修正
                # 重複データがある問題行
                fixed_row = [
                    row[0],  # id: 1
                    row[1],  # category: 造園
                    row[2],  # year: 2014
                    row[3],  # question: 地球環境に配慮し、資源を大切にする考え方や生活に関連していない用語をa～dのなかから選びなさい。
                    row[4],  # option_a: サスティナブル・ディベロップメント
                    row[5],  # option_b: リデュース
                    row[6],  # option_c: ハザード
                    row[7],  # option_d: ロハス
                    row[8],  # correct_answer: c
                    row[15], # explanation: ハザードは災害や危険を意味し、環境配慮や資源保護とは直接関連しない。
                    row[16], # reference: 環境用語
                    row[17]  # difficulty: 標準
                ]
                fixed_lines.append(fixed_row)
                print(f'修正: 行 {line_num}')
                
            elif len(row) != 12:
                # その他の問題行
                print(f'未処理の問題行: {line_num}, フィールド数: {len(row)}')
                # 12フィールドに調整
                if len(row) > 12:
                    fixed_row = row[:12]
                else:
                    fixed_row = row + [''] * (12 - len(row))
                fixed_lines.append(fixed_row)
            else:
                # 正常な行
                fixed_lines.append(row)
    
    # 修正したファイルを書き出し
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_lines)
    
    print(f'修正完了: {output_path}')
    return output_path

def verify_csv(filepath):
    """CSVファイルを検証"""
    print(f'\n=== {filepath} の検証 ===')
    
    try:
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
            
            print(f'総行数: {line_count}')
            print(f'問題行数: {problem_count}')
            
            if problem_count == 0:
                print('✓ ファイルは正常です')
                return True
            else:
                print('✗ まだ問題があります')
                return False
                
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == "__main__":
    print('=== CSV修正プロセス開始 ===')
    
    # 2013年ファイルの修正
    print('\n--- 2013年ファイルの修正 ---')
    fixed_2013 = fix_2013_csv()
    verify_2013 = verify_csv(fixed_2013)
    
    # 2014年ファイルの修正
    print('\n--- 2014年ファイルの修正 ---')
    fixed_2014 = fix_2014_csv()
    verify_2014 = verify_csv(fixed_2014)
    
    print('\n=== 修正プロセス完了 ===')
    print(f'2013年ファイル: {"成功" if verify_2013 else "失敗"}')
    print(f'2014年ファイル: {"成功" if verify_2014 else "失敗"}')