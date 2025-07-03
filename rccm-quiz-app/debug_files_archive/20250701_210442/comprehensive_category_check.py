#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験問題集アプリ - 全12分野カテゴリ名統一性検証ツール

詳細検証項目：
1. 全12分野の各年度CSVファイルでのカテゴリ名表記統一性
2. 微妙な表記揺れ（句読点、スペース、表記違い）の検出
3. app.pyのDEPARTMENT_TO_CATEGORY_MAPPINGとCSVデータの整合性
4. 各分野で年度によってカテゴリ名が変わっていないか
"""

import os
import csv
import pandas as pd
from collections import defaultdict, Counter
import re
import json
from datetime import datetime

class ComprehensiveCategoryChecker:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.all_categories = defaultdict(list)  # 分野別カテゴリリスト
        self.category_variations = defaultdict(set)  # カテゴリの表記揺れ
        self.year_analysis = defaultdict(dict)  # 年度別分析
        self.inconsistencies = []  # 不整合リスト
        
        # app.pyから取得した12分野の正式マッピング
        self.official_mapping = {
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
            'agriculture': '農業土木'
        }
        
        # 12分野の正式カテゴリ名
        self.official_categories = set(self.official_mapping.values())
        
        print("🔍 全12分野カテゴリ名統一性検証開始")
        print(f"対象分野: {len(self.official_categories)}分野")
        for dept_id, category in self.official_mapping.items():
            print(f"  - {dept_id}: {category}")

    def extract_categories_from_csv(self, file_path):
        """CSVファイルからカテゴリ名を抽出"""
        categories = set()
        try:
            # 複数のエンコーディングを試す
            encodings = ['utf-8', 'utf-8-sig', 'shift_jis', 'cp932']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"❌ エンコーディングエラー: {file_path}")
                return categories
            
            # カテゴリ列を探す
            category_columns = ['カテゴリ', 'category', 'Category', '分野', '部門']
            category_column = None
            
            for col in category_columns:
                if col in df.columns:
                    category_column = col
                    break
            
            if category_column:
                # カテゴリ名を抽出（NaN値を除外）
                unique_categories = df[category_column].dropna().unique()
                categories = set(str(cat).strip() for cat in unique_categories if str(cat).strip())
            else:
                print(f"⚠️  カテゴリ列が見つからない: {file_path}")
                print(f"   利用可能な列: {list(df.columns)}")
                
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー {file_path}: {e}")
        
        return categories

    def analyze_csv_files(self):
        """全CSVファイルを分析"""
        print("\n📊 CSVファイル分析開始...")
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        print(f"発見したCSVファイル数: {len(csv_files)}")
        
        # 年度パターンを抽出
        year_pattern = re.compile(r'(\d{4})')
        
        for csv_file in sorted(csv_files):
            file_path = os.path.join(self.data_dir, csv_file)
            print(f"\n🔍 分析中: {csv_file}")
            
            # 年度を抽出
            year_match = year_pattern.search(csv_file)
            year = year_match.group(1) if year_match else "不明"
            
            # カテゴリを抽出
            categories = self.extract_categories_from_csv(file_path)
            
            if categories:
                print(f"   発見カテゴリ数: {len(categories)}")
                for category in sorted(categories):
                    print(f"     - {category}")
                    
                    # 全カテゴリに追加
                    self.all_categories[csv_file].extend(categories)
                    
                    # 年度別分析に追加
                    if year not in self.year_analysis:
                        self.year_analysis[year] = defaultdict(list)
                    
                    for cat in categories:
                        if 'categories' not in self.year_analysis[year]:
                            self.year_analysis[year]['categories'] = []
                        if cat not in self.year_analysis[year]['categories']:
                            self.year_analysis[year]['categories'].append(cat)
                        
                        # 表記揺れチェック
                        normalized = self.normalize_category_name(cat)
                        self.category_variations[normalized].add(cat)
            else:
                print(f"   ⚠️  カテゴリが見つからない")

    def normalize_category_name(self, category):
        """カテゴリ名を正規化（表記揺れ検出用）"""
        # 空白、句読点、特殊文字を除去して正規化
        normalized = re.sub(r'[\s\u3000、。，．・]', '', str(category))
        normalized = normalized.replace('及び', '')
        normalized = normalized.replace('および', '')
        return normalized.lower()

    def check_consistency_with_official_mapping(self):
        """公式マッピングとの整合性チェック"""
        print("\n🔍 公式マッピングとの整合性チェック...")
        
        # 発見されたすべてのカテゴリ
        all_found_categories = set()
        for categories_list in self.all_categories.values():
            all_found_categories.update(categories_list)
        
        print(f"発見された総カテゴリ数: {len(all_found_categories)}")
        
        # 公式カテゴリとの比較
        official_set = self.official_categories
        found_set = all_found_categories
        
        # 公式にあるがCSVにない
        missing_in_csv = official_set - found_set
        if missing_in_csv:
            print(f"\n❌ 公式マッピングにあるがCSVにないカテゴリ: {len(missing_in_csv)}")
            for cat in sorted(missing_in_csv):
                print(f"   - {cat}")
                self.inconsistencies.append({
                    'type': 'missing_in_csv',
                    'category': cat,
                    'description': '公式マッピングに定義されているがCSVデータに存在しない'
                })
        
        # CSVにあるが公式にない
        extra_in_csv = found_set - official_set
        if extra_in_csv:
            print(f"\n⚠️  CSVにあるが公式マッピングにないカテゴリ: {len(extra_in_csv)}")
            for cat in sorted(extra_in_csv):
                print(f"   - {cat}")
                self.inconsistencies.append({
                    'type': 'extra_in_csv',
                    'category': cat,
                    'description': 'CSVデータに存在するが公式マッピングに定義されていない'
                })
        
        # 完全一致
        exact_matches = official_set & found_set
        print(f"\n✅ 完全一致カテゴリ: {len(exact_matches)}")
        for cat in sorted(exact_matches):
            print(f"   - {cat}")

    def detect_category_variations(self):
        """カテゴリ名の表記揺れ検出"""
        print("\n🔍 表記揺れ検出...")
        
        variations_found = False
        for normalized, variations in self.category_variations.items():
            if len(variations) > 1:
                variations_found = True
                print(f"\n⚠️  表記揺れ発見: {normalized}")
                for var in sorted(variations):
                    print(f"   - {var}")
                
                self.inconsistencies.append({
                    'type': 'category_variation',
                    'normalized': normalized,
                    'variations': list(variations),
                    'description': f'同一カテゴリの表記揺れ: {len(variations)}種類'
                })
        
        if not variations_found:
            print("✅ 表記揺れは検出されませんでした")

    def analyze_yearly_consistency(self):
        """年度別一貫性分析"""
        print("\n🔍 年度別一貫性分析...")
        
        # 年度ごとのカテゴリを比較
        all_years = sorted(self.year_analysis.keys())
        print(f"分析対象年度: {all_years}")
        
        # 各カテゴリが全年度で一貫しているかチェック
        all_categories_by_year = {}
        for year in all_years:
            if 'categories' in self.year_analysis[year]:
                all_categories_by_year[year] = set(self.year_analysis[year]['categories'])
        
        if len(all_categories_by_year) > 1:
            # 年度間でのカテゴリ差異をチェック
            base_year = all_years[0]
            base_categories = all_categories_by_year.get(base_year, set())
            
            for year in all_years[1:]:
                year_categories = all_categories_by_year.get(year, set())
                
                # 増加したカテゴリ
                added = year_categories - base_categories
                if added:
                    print(f"\n📈 {year}年に追加されたカテゴリ:")
                    for cat in sorted(added):
                        print(f"   + {cat}")
                
                # 削除されたカテゴリ
                removed = base_categories - year_categories
                if removed:
                    print(f"\n📉 {year}年に削除されたカテゴリ:")
                    for cat in sorted(removed):
                        print(f"   - {cat}")
        else:
            print("年度データが不十分のため、年度別比較をスキップします")

    def generate_detailed_report(self):
        """詳細レポート生成"""
        print("\n📋 詳細レポート生成...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_csv_files': len(self.all_categories),
                'total_categories_found': len(set().union(*[cats for cats in self.all_categories.values()])),
                'official_categories_count': len(self.official_categories),
                'inconsistencies_count': len(self.inconsistencies)
            },
            'official_mapping': self.official_mapping,
            'found_categories_by_file': dict(self.all_categories),
            'category_variations': {k: list(v) for k, v in self.category_variations.items()},
            'yearly_analysis': dict(self.year_analysis),
            'inconsistencies': self.inconsistencies
        }
        
        # レポートファイルに保存
        report_file = f"category_consistency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 詳細レポートを保存: {report_file}")
        
        return report

    def suggest_fixes(self):
        """修正案の提示"""
        print("\n💡 修正案の提示...")
        
        fixes = []
        
        # 表記揺れの修正案
        for inconsistency in self.inconsistencies:
            if inconsistency['type'] == 'category_variation':
                variations = inconsistency['variations']
                # 最も長い（詳細な）表記を標準とする
                standard = max(variations, key=len)
                
                fix = {
                    'type': 'standardize_variations',
                    'standard_name': standard,
                    'variations_to_fix': [v for v in variations if v != standard],
                    'action': f'すべての表記を「{standard}」に統一'
                }
                fixes.append(fix)
                print(f"📝 表記統一案: 「{standard}」に統一")
                for var in fix['variations_to_fix']:
                    print(f"   {var} → {standard}")
        
        # 公式マッピングとの不整合修正案
        for inconsistency in self.inconsistencies:
            if inconsistency['type'] == 'extra_in_csv':
                category = inconsistency['category']
                
                # 類似の公式カテゴリを検索
                best_match = self.find_best_match(category, self.official_categories)
                if best_match:
                    fix = {
                        'type': 'map_to_official',
                        'csv_category': category,
                        'suggested_official': best_match,
                        'action': f'「{category}」を「{best_match}」にマッピング'
                    }
                    fixes.append(fix)
                    print(f"📝 マッピング提案: {category} → {best_match}")
        
        return fixes

    def find_best_match(self, target, candidates):
        """最適なマッチングを見つける"""
        target_normalized = self.normalize_category_name(target)
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            candidate_normalized = self.normalize_category_name(candidate)
            
            # 簡単な類似度計算（共通文字数）
            common_chars = len(set(target_normalized) & set(candidate_normalized))
            total_chars = len(set(target_normalized) | set(candidate_normalized))
            
            if total_chars > 0:
                score = common_chars / total_chars
                if score > best_score and score > 0.3:  # 30%以上の類似度
                    best_score = score
                    best_match = candidate
        
        return best_match

    def run_comprehensive_check(self):
        """包括的チェック実行"""
        print("🚀 RCCM試験問題集アプリ - 全12分野カテゴリ名統一性検証")
        print("=" * 80)
        
        # 1. CSVファイル分析
        self.analyze_csv_files()
        
        # 2. 公式マッピングとの整合性チェック
        self.check_consistency_with_official_mapping()
        
        # 3. 表記揺れ検出
        self.detect_category_variations()
        
        # 4. 年度別一貫性分析
        self.analyze_yearly_consistency()
        
        # 5. 修正案提示
        fixes = self.suggest_fixes()
        
        # 6. 詳細レポート生成
        report = self.generate_detailed_report()
        
        # 7. サマリー表示
        print("\n" + "=" * 80)
        print("📊 検証結果サマリー")
        print("=" * 80)
        print(f"✅ 分析済みCSVファイル数: {report['summary']['total_csv_files']}")
        print(f"✅ 発見カテゴリ総数: {report['summary']['total_categories_found']}")
        print(f"✅ 公式カテゴリ数: {report['summary']['official_categories_count']}")
        print(f"⚠️  不整合検出数: {report['summary']['inconsistencies_count']}")
        print(f"💡 修正案数: {len(fixes)}")
        
        if report['summary']['inconsistencies_count'] == 0:
            print("\n🎉 おめでとうございます！カテゴリ名は完全に統一されています！")
        else:
            print(f"\n⚠️  {report['summary']['inconsistencies_count']}件の不整合が見つかりました。修正をお勧めします。")
        
        return report, fixes

def main():
    """メイン実行関数"""
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print(f"❌ データディレクトリが見つかりません: {data_dir}")
        return
    
    checker = ComprehensiveCategoryChecker(data_dir)
    report, fixes = checker.run_comprehensive_check()
    
    return report, fixes

if __name__ == "__main__":
    main()