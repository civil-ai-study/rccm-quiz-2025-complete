#!/usr/bin/env python3
import csv
import glob
from collections import defaultdict

def analyze_categories():
    # 年度別カテゴリー収集
    year_categories = defaultdict(set)
    category_variations = defaultdict(set)
    
    # 全CSVファイルを分析
    csv_files = sorted(glob.glob("4-2_*.csv"))
    
    for csv_file in csv_files:
        if "backup" in csv_file or "fixed" in csv_file:
            continue
            
        year = csv_file.split("_")[1].split(".")[0]
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        category = row['category'].strip()
                        year_categories[year].add(category)
                        category_variations[category].add(year)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    # カテゴリー名のバリエーション分析
    print("=== カテゴリー名の年度別バリエーション ===\n")
    
    # 類似カテゴリーをグループ化
    category_groups = {
        "河川・砂防": [],
        "鋼構造及びコンクリート": [],
        "都市計画": [],
        "施工計画": [],
        "上水道": [],
        "土質及び基礎": [],
        "道路": [],
        "トンネル": [],
        "造園": [],
        "農業土木": [],
        "森林土木": [],
        "建設環境": [],
        "その他": []
    }
    
    # カテゴリーを分類
    for category in sorted(category_variations.keys()):
        years = sorted(category_variations[category])
        
        if "河川" in category or "砂防" in category or "海岸" in category:
            category_groups["河川・砂防"].append((category, years))
        elif "鋼構造" in category or "コンクリート" in category:
            category_groups["鋼構造及びコンクリート"].append((category, years))
        elif "都市計画" in category or "地方計画" in category:
            category_groups["都市計画"].append((category, years))
        elif "施工計画" in category or "施工設備" in category or "積算" in category:
            category_groups["施工計画"].append((category, years))
        elif "上水道" in category or "工業用水道" in category:
            category_groups["上水道"].append((category, years))
        elif "土質" in category and "基礎" in category:
            category_groups["土質及び基礎"].append((category, years))
        elif category == "道路":
            category_groups["道路"].append((category, years))
        elif category == "トンネル":
            category_groups["トンネル"].append((category, years))
        elif category == "造園":
            category_groups["造園"].append((category, years))
        elif category == "農業土木":
            category_groups["農業土木"].append((category, years))
        elif category == "森林土木":
            category_groups["森林土木"].append((category, years))
        elif category == "建設環境":
            category_groups["建設環境"].append((category, years))
        else:
            category_groups["その他"].append((category, years))
    
    # 結果出力
    for group_name, categories in category_groups.items():
        if categories:
            print(f"【{group_name}】")
            for category, years in categories:
                years_str = ", ".join(years)
                print(f"  「{category}」 - {years_str}")
            
            # 推奨統一名を提示
            if len(categories) > 1:
                print(f"  → 推奨統一名: ", end="")
                if group_name == "河川・砂防":
                    print("「河川、砂防及び海岸・海洋」")
                elif group_name == "鋼構造及びコンクリート":
                    print("「鋼構造及びコンクリート」")
                elif group_name == "都市計画":
                    print("「都市計画及び地方計画」")
                elif group_name == "施工計画":
                    print("「施工計画、施工設備及び積算」")
                elif group_name == "上水道":
                    print("「上水道及び工業用水道」")
            print()
    
    # 年度別サマリー
    print("\n=== 年度別カテゴリー数 ===")
    for year in sorted(year_categories.keys()):
        categories = year_categories[year]
        print(f"{year}年: {len(categories)}カテゴリー")
        if "未分類" in categories:
            print(f"  ※ 「未分類」が含まれています")

if __name__ == "__main__":
    analyze_categories()