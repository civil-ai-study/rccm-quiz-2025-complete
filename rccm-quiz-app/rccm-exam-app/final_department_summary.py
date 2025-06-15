#!/usr/bin/env python3
"""
最終的な部門データ要約レポート
"""
import csv
import os
import re
from collections import defaultdict
from config import RCCMConfig

def normalize_department(dept):
    """部門名を正規化"""
    normalization_rules = {
        '上水道工業用水道': '上水道及び工業用水道',
        '都市計画地方計画': '都市計画及び地方計画',
        '鋼構造コンクリート': '鋼構造及びコンクリート',
        '河川砂防海岸海洋': '河川、砂防及び海岸・海洋',
        '河川砂防海岸': '河川、砂防及び海岸・海洋',
        '河川砂防': '河川、砂防及び海岸・海洋',
        '河川・砂防及び海岸・海洋': '河川、砂防及び海岸・海洋',
        '河川、砂防及び海岸･海洋': '河川、砂防及び海岸・海洋',
        '河川砂防及び海岸・海洋': '河川、砂防及び海岸・海洋',
        '施工計画施工設備積算': '施工計画、施工設備及び積算',
        '施工計画・施工設備及び積算': '施工計画、施工設備及び積算',
        '施工計画積算': '施工計画、施工設備及び積算',
    }
    return normalization_rules.get(dept, dept)

def determine_question_type(filename):
    """ファイル名から問題種別を判定"""
    if '4-1' in filename:
        return 'basic'  # 4-1 必須科目
    elif '4-2' in filename:
        return 'specialist'  # 4-2 選択科目
    else:
        return 'legacy'  # レガシーデータ

def main():
    data_dir = '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    
    # データ収集
    department_stats = defaultdict(lambda: {'basic': 0, 'specialist': 0, 'legacy': 0, 'total': 0})
    file_analysis = {}
    total_questions = 0
    
    # CSVファイルを分析
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv') or 'backup' in filename:
            continue
            
        filepath = os.path.join(data_dir, filename)
        question_type = determine_question_type(filename)
        file_questions = 0
        file_departments = set()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        dept = normalize_department(row['category'])
                        department_stats[dept][question_type] += 1
                        department_stats[dept]['total'] += 1
                        file_questions += 1
                        file_departments.add(dept)
                        total_questions += 1
        except Exception as e:
            print(f"エラー処理中 {filename}: {e}")
            continue
        
        file_analysis[filename] = {
            'questions': file_questions,
            'departments': sorted(list(file_departments)),
            'type': question_type
        }
    
    # CSVからconfig.pyへのマッピング
    csv_to_config = {
        '道路': 'road',
        '河川、砂防及び海岸・海洋': 'civil_planning',
        '建設環境': 'construction_env', 
        '都市計画及び地方計画': 'urban_planning',
        '森林土木': 'forestry',
        '農業土木': 'agriculture',
        '鋼構造及びコンクリート': 'construction_mgmt',
        '土質及び基礎': 'construction_mgmt',
        '施工計画、施工設備及び積算': 'construction_mgmt',
        '施工計画': 'construction_mgmt',
        '上水道及び工業用水道': 'civil_planning',
        'トンネル': 'road',
        '造園': 'urban_planning',
        '共通': 'basic_common',
        '未分類': 'uncategorized',
        'レガシーデータ': 'legacy'
    }
    
    print("=" * 80)
    print("RCCM Quiz App - 部門データ完全分析レポート")
    print("=" * 80)
    
    print(f"\n【1. 全体統計】")
    print(f"総問題数: {total_questions:,}問")
    print(f"CSVファイル数: {len(file_analysis)}ファイル")
    print(f"実際の部門数: {len([d for d in department_stats.keys() if d not in ['共通', '未分類', 'レガシーデータ']])}部門")
    
    print(f"\n【2. 問題種別統計】")
    basic_total = sum(stats['basic'] for stats in department_stats.values())
    specialist_total = sum(stats['specialist'] for stats in department_stats.values())
    legacy_total = sum(stats['legacy'] for stats in department_stats.values())
    
    print(f"4-1 基礎問題: {basic_total:,}問 ({basic_total/total_questions*100:.1f}%)")
    print(f"4-2 専門問題: {specialist_total:,}問 ({specialist_total/total_questions*100:.1f}%)")
    print(f"レガシーデータ: {legacy_total:,}問 ({legacy_total/total_questions*100:.1f}%)")
    
    print(f"\n【3. 部門別詳細統計】")
    print(f"{'部門名':30s} {'基礎':>6s} {'専門':>6s} {'合計':>6s} {'config.py ID':>20s}")
    print("-" * 80)
    
    # 部門をタイプ別にソート
    main_departments = []
    special_categories = []
    
    for dept, stats in department_stats.items():
        if dept in ['共通', '未分類', 'レガシーデータ']:
            special_categories.append((dept, stats))
        else:
            main_departments.append((dept, stats))
    
    # メイン部門を問題数順でソート
    main_departments.sort(key=lambda x: x[1]['total'], reverse=True)
    
    for dept, stats in main_departments:
        config_id = csv_to_config.get(dept, '未マッピング')
        print(f"{dept:30s} {stats['basic']:>6d} {stats['specialist']:>6d} {stats['total']:>6d} {config_id:>20s}")
    
    print("-" * 80)
    for dept, stats in special_categories:
        config_id = csv_to_config.get(dept, '未マッピング')
        print(f"{dept:30s} {stats['basic']:>6d} {stats['specialist']:>6d} {stats['total']:>6d} {config_id:>20s}")
    
    print(f"\n【4. 実際に利用可能な部門（config.pyマッピング済み）】")
    config_mapped_departments = {}
    for csv_dept, config_id in csv_to_config.items():
        if config_id in RCCMConfig.DEPARTMENTS and csv_dept not in ['共通', '未分類', 'レガシーデータ']:
            if config_id not in config_mapped_departments:
                config_mapped_departments[config_id] = {'csv_categories': [], 'total_questions': 0}
            config_mapped_departments[config_id]['csv_categories'].append(csv_dept)
            config_mapped_departments[config_id]['total_questions'] += department_stats[csv_dept]['total']
    
    for config_id in sorted(config_mapped_departments.keys()):
        info = config_mapped_departments[config_id]
        config_name = RCCMConfig.DEPARTMENTS[config_id]['name']
        print(f"\n{config_id} ({config_name}): {info['total_questions']}問")
        for csv_cat in info['csv_categories']:
            stats = department_stats[csv_cat]
            print(f"  └ {csv_cat}: 基礎{stats['basic']}問 + 専門{stats['specialist']}問 = {stats['total']}問")
    
    print(f"\n【5. config.pyで定義されているが問題データがない部門】")
    unused_configs = []
    for config_id, config_info in RCCMConfig.DEPARTMENTS.items():
        if config_id not in config_mapped_departments:
            unused_configs.append(f"  - {config_id}: {config_info['name']}")
    
    if unused_configs:
        for item in unused_configs:
            print(item)
    else:
        print("  なし（全ての設定済み部門に問題データが存在）")
    
    print(f"\n【6. 推奨事項】")
    print("1. 以下の部門は十分な問題数があり、実際の学習に利用可能：")
    for config_id, info in sorted(config_mapped_departments.items(), key=lambda x: x[1]['total_questions'], reverse=True):
        if info['total_questions'] >= 100:  # 100問以上
            config_name = RCCMConfig.DEPARTMENTS[config_id]['name']
            print(f"   ✓ {config_name} ({info['total_questions']}問)")
    
    print("\n2. 問題データが不足している部門：")
    for config_id, info in config_mapped_departments.items():
        if info['total_questions'] < 100:
            config_name = RCCMConfig.DEPARTMENTS[config_id]['name']
            print(f"   ⚠ {config_name} ({info['total_questions']}問) - 追加データ推奨")
    
    print("\n3. 追加可能な部門（現在データなし）：")
    for item in unused_configs[:3]:  # 上位3つのみ表示
        print(f"   💡{item}")

if __name__ == "__main__":
    main()