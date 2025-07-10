#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRATHIN区Deep検証: 4-2専門問題CSVファイルのカテゴリー混入問題調査
副作用ゼロで調査し、問題があれば具体的な修正提案を行う
"""

import csv
import os
import glob
from collections import Counter, defaultdict
import re

def analyze_category_data():
    """4-2専門問題CSVファイルのカテゴリー混入問題を調査"""
    
    # 調査対象ディレクトリ
    data_dir = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/isolated_test_env/data"
    
    # 4-2のCSVファイルを取得
    csv_files = glob.glob(os.path.join(data_dir, "4-2_*.csv"))
    csv_files.sort()
    
    print("=" * 80)
    print("ULTRATHIN区Deep検証: 4-2専門問題CSVカテゴリー混入問題調査")
    print("=" * 80)
    
    all_categories = set()
    category_distribution = {}
    category_variations = defaultdict(set)
    problematic_files = []
    
    for csv_file in csv_files:
        year = os.path.basename(csv_file).replace("4-2_", "").replace(".csv", "")
        print(f"\n[{year}年度] {csv_file}")
        
        try:
            # CSVファイルを読み込み
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # カテゴリー列の確認
            if not rows or 'category' not in rows[0]:
                print("  ❌ エラー: 'category'列が見つかりません")
                problematic_files.append((csv_file, "category列なし"))
                continue
            
            # カテゴリー分布を集計
            categories = Counter()
            env_problems = []
            
            for row in rows:
                category = row.get('category', '').strip()
                if category:
                    categories[category] += 1
                    all_categories.add(category)
                    
                    # カテゴリー名の表記揺れをチェック
                    normalized = category.lower()
                    category_variations[normalized].add(category)
                    
                    # 建設環境カテゴリーの問題を収集
                    env_keywords = ["建設環境", "環境", "建設環境・建設技術"]
                    if any(keyword in category for keyword in env_keywords):
                        env_problems.append(row)
            
            category_distribution[year] = dict(categories)
            
            print(f"  📊 総問題数: {len(rows)}")
            print(f"  📂 カテゴリー数: {len(categories)}")
            
            # カテゴリー詳細表示
            for category, count in categories.most_common():
                print(f"    - {category}: {count}問")
            
            # 建設環境カテゴリーの他カテゴリー混入チェック
            if env_problems:
                print(f"  🌱 建設環境関連: {len(env_problems)}問")
                
                # 問題文の内容をチェック（他カテゴリーの混入確認）
                suspicious_patterns = [
                    (r'鋼構造|鋼材|溶接|鋼橋', '鋼構造'),
                    (r'コンクリート|RC|PC|プレストレス', 'コンクリート'),
                    (r'トンネル|坑道|NATM', 'トンネル'),
                    (r'基礎|杭|地盤改良', '基礎'),
                    (r'道路|舗装|アスファルト', '道路'),
                    (r'河川|砂防|ダム|堤防', '河川・砂防')
                ]
                
                for row in env_problems:
                    question = str(row.get('question', ''))
                    for pattern, category_name in suspicious_patterns:
                        if re.search(pattern, question, re.IGNORECASE):
                            print(f"    ⚠️  問題ID{row.get('id', 'N/A')}: {category_name}要素を含む可能性")
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")
            problematic_files.append((csv_file, str(e)))
    
    # 全体的な分析結果
    print("\n" + "=" * 80)
    print("📋 総合分析結果")
    print("=" * 80)
    
    print(f"\n🗂️  発見された全カテゴリー ({len(all_categories)}種類):")
    for category in sorted(all_categories):
        print(f"    - {category}")
    
    # カテゴリー名の表記揺れ検出
    print(f"\n📝 カテゴリー名の表記揺れ検出:")
    variations_found = False
    for normalized, variations in category_variations.items():
        if len(variations) > 1:
            variations_found = True
            print(f"    ⚠️  '{normalized}'の表記: {list(variations)}")
    
    if not variations_found:
        print("    ✅ 表記揺れは検出されませんでした")
    
    # 各年度のカテゴリー分布比較
    print(f"\n📊 年度別カテゴリー分布:")
    years = sorted(category_distribution.keys())
    all_cats = sorted(all_categories)
    
    # 分布表作成
    print(f"{'カテゴリー':<20}", end="")
    for year in years:
        print(f"{year:>8}", end="")
    print()
    print("-" * (20 + 8 * len(years)))
    
    for category in all_cats:
        print(f"{category:<20}", end="")
        for year in years:
            count = category_distribution.get(year, {}).get(category, 0)
            print(f"{count:>8}", end="")
        print()
    
    # 問題ファイルの報告
    if problematic_files:
        print(f"\n❌ 問題が発見されたファイル:")
        for file_path, error in problematic_files:
            print(f"    - {os.path.basename(file_path)}: {error}")
    else:
        print(f"\n✅ 全ファイルが正常に処理されました")
    
    # 修正提案
    print("\n" + "=" * 80)
    print("🔧 修正提案")
    print("=" * 80)
    
    if variations_found:
        print("\n1. カテゴリー名の表記統一:")
        for normalized, variations in category_variations.items():
            if len(variations) > 1:
                most_common = max(variations, key=lambda x: sum(
                    category_distribution[year].get(x, 0) 
                    for year in category_distribution
                ))
                print(f"   - '{normalized}'系: '{most_common}'に統一推奨")
    
    print("\n2. カテゴリー混入問題:")
    print("   - 建設環境カテゴリーで他分野要素を含む問題を上記で特定")
    print("   - 該当問題の再分類またはカテゴリー修正を推奨")
    
    print("\n3. データ品質改善:")
    print("   - 定期的なカテゴリー整合性チェックの実装")
    print("   - 問題登録時のカテゴリー検証ルールの強化")
    
    return category_distribution, all_categories, problematic_files

if __name__ == "__main__":
    analyze_category_data()