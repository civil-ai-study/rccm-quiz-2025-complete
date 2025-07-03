#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - CSVカテゴリー名詳細チェック
全CSVファイルのカテゴリー名の表記揺れ・不統一を徹底検証
"""

import csv
import os
import json
from datetime import datetime
from collections import defaultdict, Counter

# 正式な12分野のカテゴリー名
OFFICIAL_CATEGORIES = {
    'road': '道路',
    'tunnel': 'トンネル', 
    'civil_planning': '河川、砂防及び海岸・海洋',
    'urban_planning': '都市計画及び地方計画',
    'landscape': '造園',
    'construction_env': '建設環境',
    'steel_concrete': '鋼構造及びコンクリート',
    'soil_foundation': '土質及び基礎',
    'construction_planning': '施工計画、施工設備及び積算',
    'water_supply': '上水道及び工業用水道',
    'forestry': '森林土木',
    'agriculture': '農業土木',
    'common': '共通'
}

def analyze_csv_categories():
    """全CSVファイルのカテゴリー名を詳細分析"""
    print("=== CSV カテゴリー名詳細チェック ===")
    print(f"検証開始時刻: {datetime.now()}")
    print()
    
    data_dir = 'data'
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"対象CSVファイル: {len(csv_files)}個")
    for f in sorted(csv_files):
        print(f"  - {f}")
    print()
    
    results = {}
    all_categories = defaultdict(list)  # カテゴリー名 -> ファイルリスト
    category_variations = defaultdict(set)  # ベース名 -> バリエーション集合
    
    for csv_file in sorted(csv_files):
        file_path = os.path.join(data_dir, csv_file)
        print(f"\n=== {csv_file} の分析 ===")
        
        file_categories = []
        category_counts = Counter()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                total_rows = 0
                
                for row in reader:
                    total_rows += 1
                    category = row.get('category', '').strip()
                    
                    if category:
                        file_categories.append(category)
                        category_counts[category] += 1
                        all_categories[category].append(csv_file)
        
        except Exception as e:
            print(f"❌ エラー: {e}")
            continue
        
        # ファイル内のユニークカテゴリー
        unique_categories = list(set(file_categories))
        print(f"総行数: {total_rows}")
        print(f"ユニークカテゴリー数: {len(unique_categories)}")
        print(f"ユニークカテゴリー:")
        
        for cat in sorted(unique_categories):
            count = category_counts[cat]
            # 表記チェック
            issues = []
            
            # スペース・文字チェック
            if cat != cat.strip():
                issues.append("前後スペース")
            if '　' in cat:  # 全角スペース
                issues.append("全角スペース")
            if cat != cat.replace('\u3000', ''):  # 全角スペース
                issues.append("全角文字")
            
            # 公式カテゴリーとの一致チェック
            official_match = cat in OFFICIAL_CATEGORIES.values()
            status = "✅" if official_match else "❌"
            
            issue_str = f" [{', '.join(issues)}]" if issues else ""
            print(f"  {status} '{cat}' ({count}問){issue_str}")
            
            if not official_match:
                print(f"      -> 非公式カテゴリー名")
        
        results[csv_file] = {
            'total_rows': total_rows,
            'unique_categories': unique_categories,
            'category_counts': dict(category_counts),
            'issues_count': len([c for c in unique_categories if c not in OFFICIAL_CATEGORIES.values()])
        }
    
    print(f"\n" + "="*70)
    print("=== 全体統計 ===")
    
    # 全カテゴリー名の統計
    all_unique_categories = set(all_categories.keys())
    official_categories_found = set(OFFICIAL_CATEGORIES.values()) & all_unique_categories
    unofficial_categories = all_unique_categories - set(OFFICIAL_CATEGORIES.values())
    
    print(f"発見された全カテゴリー数: {len(all_unique_categories)}")
    print(f"公式カテゴリーとの一致: {len(official_categories_found)}/13")
    print(f"非公式・問題のあるカテゴリー: {len(unofficial_categories)}")
    
    if unofficial_categories:
        print(f"\n❌ 問題のあるカテゴリー名:")
        for cat in sorted(unofficial_categories):
            files = all_categories[cat]
            print(f"  '{cat}' -> 使用ファイル: {files}")
            
            # 類似する公式カテゴリーを探す
            similar_officials = []
            for official in OFFICIAL_CATEGORIES.values():
                if any(word in cat for word in official.split('、')):
                    similar_officials.append(official)
            
            if similar_officials:
                print(f"      類似公式名: {similar_officials}")
    
    print(f"\n=== 公式カテゴリー使用状況 ===")
    for dept_id, official_name in OFFICIAL_CATEGORIES.items():
        if official_name in all_categories:
            files = sorted(set(all_categories[official_name]))
            print(f"✅ '{official_name}' -> {len(files)}ファイル: {files}")
        else:
            print(f"❌ '{official_name}' -> 使用ファイルなし")
    
    # 詳細レポート保存
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_csv_files': len(csv_files),
            'total_categories_found': len(all_unique_categories),
            'official_categories_found': len(official_categories_found),
            'unofficial_categories_count': len(unofficial_categories)
        },
        'official_categories': OFFICIAL_CATEGORIES,
        'found_categories_by_file': results,
        'category_usage': {cat: sorted(set(files)) for cat, files in all_categories.items()},
        'unofficial_categories': list(unofficial_categories),
        'category_variations': {k: list(v) for k, v in category_variations.items()}
    }
    
    report_filename = f"csv_category_detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細レポート保存: {report_filename}")
    
    return results, unofficial_categories

def check_specific_inconsistencies():
    """特定の不整合パターンをチェック"""
    print(f"\n=== 特定不整合パターンチェック ===")
    
    data_dir = 'data'
    inconsistencies = []
    
    # よくある表記揺れパターン
    variation_patterns = {
        '道路': ['道路', '道路 ', ' 道路'],
        'トンネル': ['トンネル', 'トンネル ', ' トンネル'],
        '河川、砂防及び海岸・海洋': [
            '河川、砂防及び海岸・海洋',
            '河川砂防及び海岸・海洋',
            '河川、砂防及び海岸海洋',
            '河川，砂防及び海岸・海洋'
        ],
        '都市計画及び地方計画': [
            '都市計画及び地方計画',
            '都市計画・地方計画',
            '都市計画及地方計画'
        ],
        '鋼構造及びコンクリート': [
            '鋼構造及びコンクリート',
            '鋼構造・コンクリート',
            '鋼構造及コンクリート'
        ],
        '施工計画、施工設備及び積算': [
            '施工計画、施工設備及び積算',
            '施工計画・施工設備及び積算',
            '施工計画施工設備及び積算'
        ],
        '上水道及び工業用水道': [
            '上水道及び工業用水道',
            '上水道・工業用水道',
            '上水道及工業用水道'
        ]
    }
    
    for csv_file in os.listdir(data_dir):
        if not csv_file.endswith('.csv'):
            continue
            
        file_path = os.path.join(data_dir, csv_file)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    category = row.get('category', '')
                    
                    # パターンマッチング
                    for official, variations in variation_patterns.items():
                        if category in variations and category != official:
                            inconsistencies.append({
                                'file': csv_file,
                                'row': row_num,
                                'found': category,
                                'should_be': official,
                                'id': row.get('id', 'unknown')
                            })
        
        except Exception as e:
            print(f"エラー {csv_file}: {e}")
    
    if inconsistencies:
        print(f"❌ 発見された不整合: {len(inconsistencies)}件")
        for issue in inconsistencies[:10]:  # 最初の10件表示
            print(f"  {issue['file']}:{issue['row']} ID:{issue['id']} '{issue['found']}' -> '{issue['should_be']}'")
        if len(inconsistencies) > 10:
            print(f"  ... 他{len(inconsistencies) - 10}件")
    else:
        print("✅ 特定パターンでの不整合なし")
    
    return inconsistencies

def generate_fix_script(unofficial_categories, inconsistencies):
    """修正スクリプトを生成"""
    print(f"\n=== 修正スクリプト生成 ===")
    
    if not unofficial_categories and not inconsistencies:
        print("✅ 修正が必要な問題は見つかりませんでした")
        return
    
    fix_script = f'''#!/usr/bin/env python3
"""
自動生成されたCSVカテゴリー名修正スクリプト
生成日時: {datetime.now()}
"""

import csv
import os
import shutil
from datetime import datetime

def fix_csv_categories():
    """CSVファイルのカテゴリー名を修正"""
    
    # 修正マッピング
    category_fixes = {{
'''
    
    # 修正マッピングを生成
    fixes = {}
    
    # 不整合から修正マッピングを作成
    for issue in inconsistencies:
        fixes[issue['found']] = issue['should_be']
    
    # 非公式カテゴリーの推定修正
    for unofficial in unofficial_categories:
        # 類似性ベースの推定
        for official in OFFICIAL_CATEGORIES.values():
            if any(word in unofficial for word in official.split('、')):
                fixes[unofficial] = official
                break
    
    for wrong, correct in fixes.items():
        fix_script += f'        "{wrong}": "{correct}",\n'
    
    fix_script += '''    }
    
    data_dir = 'data'
    backup_dir = f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # バックアップ作成
    print(f"バックアップ作成: {backup_dir}")
    shutil.copytree(data_dir, backup_dir)
    
    fixed_count = 0
    
    for csv_file in os.listdir(data_dir):
        if not csv_file.endswith('.csv'):
            continue
            
        file_path = os.path.join(data_dir, csv_file)
        temp_path = file_path + '.tmp'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as infile, \\
                 open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                file_fixes = 0
                for row in reader:
                    original_category = row.get('category', '')
                    if original_category in category_fixes:
                        row['category'] = category_fixes[original_category]
                        file_fixes += 1
                    writer.writerow(row)
                
                if file_fixes > 0:
                    print(f"{csv_file}: {file_fixes}件修正")
                    fixed_count += file_fixes
            
            # 元ファイルを置換
            if file_fixes > 0:
                os.replace(temp_path, file_path)
            else:
                os.remove(temp_path)
                
        except Exception as e:
            print(f"エラー {csv_file}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    print(f"修正完了: 総計{fixed_count}件")

if __name__ == "__main__":
    fix_csv_categories()
'''
    
    script_filename = f"fix_csv_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print(f"修正スクリプト生成: {script_filename}")
    print(f"実行方法: python3 {script_filename}")

if __name__ == "__main__":
    # メイン分析実行
    results, unofficial_categories = analyze_csv_categories()
    
    # 特定パターンチェック
    inconsistencies = check_specific_inconsistencies()
    
    # 修正スクリプト生成
    if unofficial_categories or inconsistencies:
        generate_fix_script(unofficial_categories, inconsistencies)
    
    print(f"\n=== CSV カテゴリー名チェック完了 ===")
    
    if unofficial_categories or inconsistencies:
        print(f"❌ 問題発見: カテゴリー名の不統一があります")
        print(f"   非公式カテゴリー: {len(unofficial_categories)}個")
        print(f"   表記不整合: {len(inconsistencies)}件")
        print(f"   修正が必要です")
    else:
        print(f"✅ 全CSVファイルのカテゴリー名は統一されています")