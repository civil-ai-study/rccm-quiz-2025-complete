#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験システム 13部門完全調査スクリプト
- データファイル構造分析
- 部門マッピング検証
- 問題数・年度範囲調査
- データ品質チェック
"""

import os
import csv
import json
import re
from collections import defaultdict, Counter
from datetime import datetime

def analyze_rccm_system():
    """RCCM試験システム完全分析"""
    base_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app"
    data_dir = os.path.join(base_dir, "data")
    
    # 結果格納用
    analysis_result = {
        "analysis_date": datetime.now().isoformat(),
        "basic_subjects": {},
        "specialist_subjects": {},
        "department_mapping": {},
        "data_quality": {},
        "summary": {}
    }
    
    print("RCCM試験システム 13部門完全調査開始")
    print("=" * 60)
    
    # 1. 基礎科目（4-1.csv）分析
    print("1. 基礎科目データ分析")
    basic_file = os.path.join(data_dir, "4-1.csv")
    if os.path.exists(basic_file):
        basic_analysis = analyze_basic_subjects(basic_file)
        analysis_result["basic_subjects"] = basic_analysis
        print(f"   基礎科目: {basic_analysis['total_questions']}問")
        print(f"   カテゴリ: {list(basic_analysis['categories'].keys())}")
    else:
        print("   基礎科目ファイルが見つかりません")
    
    # 2. 専門科目（4-2_YYYY.csv）分析
    print("\n2. 専門科目データ分析")
    specialist_files = [f for f in os.listdir(data_dir) 
                       if f.startswith("4-2_") and f.endswith(".csv") 
                       and not f.endswith(".backup")]
    
    specialist_analysis = analyze_specialist_subjects(data_dir, specialist_files)
    analysis_result["specialist_subjects"] = specialist_analysis
    
    print(f"   年度ファイル数: {len(specialist_files)}")
    print(f"   年度範囲: {specialist_analysis['year_range']}")
    print(f"   総問題数: {specialist_analysis['total_questions']}")
    
    # 3. 部門マッピング分析
    print("\n3. 部門マッピング分析")
    mapping_analysis = analyze_department_mapping(base_dir)
    analysis_result["department_mapping"] = mapping_analysis
    
    # 4. データ品質チェック
    print("\n4. データ品質チェック")
    quality_analysis = check_data_quality(specialist_analysis)
    analysis_result["data_quality"] = quality_analysis
    
    # 5. 13部門リスト生成
    print("\n5. 13部門完全リスト")
    all_departments = generate_complete_department_list(specialist_analysis)
    analysis_result["complete_departments"] = all_departments
    
    # 結果サマリー
    analysis_result["summary"] = {
        "total_departments": len(all_departments),
        "total_years": len(specialist_analysis["by_year"]),
        "total_questions": (analysis_result["basic_subjects"].get("total_questions", 0) + 
                          specialist_analysis["total_questions"]),
        "data_coverage": calculate_data_coverage(specialist_analysis)
    }
    
    # 結果保存
    output_file = os.path.join(base_dir, f"rccm_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    # 詳細レポート生成
    generate_detailed_report(analysis_result)
    
    print(f"\n分析完了！結果を保存: {output_file}")
    return analysis_result

def analyze_basic_subjects(file_path):
    """基礎科目データ分析"""
    analysis = {
        "file_path": file_path,
        "total_questions": 0,
        "categories": defaultdict(int),
        "encoding_issues": [],
        "missing_fields": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                analysis["total_questions"] += 1
                
                # カテゴリ分析
                category = row.get('category', '').strip()
                if category:
                    analysis["categories"][category] += 1
                
                # データ品質チェック
                for field in ['id', 'question', 'correct_answer']:
                    if not row.get(field, '').strip():
                        analysis["missing_fields"].append(f"行{row_num}: {field}")
                
                # エンコーディング問題チェック
                for field, value in row.items():
                    if value and any(ord(c) > 127 for c in value):
                        try:
                            value.encode('utf-8')
                        except UnicodeEncodeError:
                            analysis["encoding_issues"].append(f"行{row_num}: {field}")
    
    except Exception as e:
        analysis["error"] = str(e)
    
    return analysis

def analyze_specialist_subjects(data_dir, files):
    """専門科目データ分析"""
    analysis = {
        "files": files,
        "total_questions": 0,
        "by_year": {},
        "by_category": defaultdict(lambda: defaultdict(int)),
        "year_range": [],
        "categories": set(),
        "encoding_issues": [],
        "missing_fields": []
    }
    
    for file_name in sorted(files):
        # 年度抽出
        year_match = re.search(r'4-2_(\d{4})\.csv', file_name)
        if not year_match:
            continue
        
        year = int(year_match.group(1))
        analysis["year_range"].append(year)
        analysis["by_year"][year] = {
            "file": file_name,
            "questions": 0,
            "categories": defaultdict(int)
        }
        
        file_path = os.path.join(data_dir, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 1):
                    analysis["total_questions"] += 1
                    analysis["by_year"][year]["questions"] += 1
                    
                    # カテゴリ分析
                    category = row.get('category', '').strip()
                    if category:
                        analysis["categories"].add(category)
                        analysis["by_category"][category][year] += 1
                        analysis["by_year"][year]["categories"][category] += 1
                    
                    # データ品質チェック
                    for field in ['id', 'question', 'correct_answer']:
                        if not row.get(field, '').strip():
                            analysis["missing_fields"].append(f"{file_name} 行{row_num}: {field}")
        
        except Exception as e:
            analysis["by_year"][year]["error"] = str(e)
    
    # 年度範囲のソート
    analysis["year_range"] = sorted(analysis["year_range"]) if analysis["year_range"] else []
    analysis["categories"] = sorted(list(analysis["categories"]))
    
    return analysis

def analyze_department_mapping(base_dir):
    """部門マッピング分析"""
    app_file = os.path.join(base_dir, "app.py")
    mapping_analysis = {
        "csv_japanese_categories": {},
        "department_to_category_mapping": {},
        "legacy_aliases": {},
        "inconsistencies": []
    }
    
    if not os.path.exists(app_file):
        mapping_analysis["error"] = "app.pyファイルが見つかりません"
        return mapping_analysis
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # CSV_JAPANESE_CATEGORIES抽出
        csv_match = re.search(r'CSV_JAPANESE_CATEGORIES\s*=\s*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
        if csv_match:
            csv_content = csv_match.group(1)
            # 簡易パースing（実際のPython辞書パースは複雑なので簡略化）
            lines = csv_content.split('\n')
            for line in lines:
                if ':' in line and '"' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip().strip('"').strip("'")
                        value = parts[1].strip().strip(',').strip('"').strip("'")
                        if key and value:
                            mapping_analysis["csv_japanese_categories"][key] = value
        
        # DEPARTMENT_TO_CATEGORY_MAPPING抽出
        dept_match = re.search(r'DEPARTMENT_TO_CATEGORY_MAPPING\s*=\s*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
        if dept_match:
            dept_content = dept_match.group(1)
            lines = dept_content.split('\n')
            for line in lines:
                if ':' in line and "'" in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip().strip('"').strip("'")
                        value = parts[1].strip().strip(',').strip('"').strip("'")
                        if key and value:
                            mapping_analysis["department_to_category_mapping"][key] = value
    
    except Exception as e:
        mapping_analysis["error"] = str(e)
    
    return mapping_analysis

def check_data_quality(specialist_analysis):
    """データ品質チェック"""
    quality = {
        "year_gaps": [],
        "category_inconsistencies": [],
        "question_count_variations": {},
        "encoding_issues_count": len(specialist_analysis.get("encoding_issues", [])),
        "missing_fields_count": len(specialist_analysis.get("missing_fields", []))
    }
    
    # 年度ギャップチェック
    years = specialist_analysis.get("year_range", [])
    if years:
        for i in range(len(years) - 1):
            if years[i+1] - years[i] > 1:
                quality["year_gaps"].append(f"{years[i]}-{years[i+1]}")
    
    # カテゴリ別問題数のばらつき
    by_category = specialist_analysis.get("by_category", {})
    for category, year_data in by_category.items():
        counts = list(year_data.values())
        if counts:
            min_count = min(counts)
            max_count = max(counts)
            avg_count = sum(counts) / len(counts)
            quality["question_count_variations"][category] = {
                "min": min_count,
                "max": max_count,
                "avg": round(avg_count, 1),
                "variation_ratio": round(max_count / min_count if min_count > 0 else 0, 2)
            }
    
    return quality

def generate_complete_department_list(specialist_analysis):
    """13部門完全リスト生成"""
    departments = []
    
    # 基礎科目
    departments.append({
        "id": "basic",
        "name": "基礎科目（共通）",
        "csv_category": "共通",
        "type": "basic",
        "file": "4-1.csv"
    })
    
    # 専門科目部門
    categories = specialist_analysis.get("categories", [])
    department_mapping = {
        "道路": {"id": "road", "name": "道路"},
        "河川、砂防及び海岸・海洋": {"id": "river_sabo", "name": "河川・砂防"},
        "都市計画及び地方計画": {"id": "urban_planning", "name": "都市計画"},
        "造園": {"id": "landscape", "name": "造園"},
        "建設環境": {"id": "construction_environment", "name": "建設環境"},
        "鋼構造及びコンクリート": {"id": "steel_concrete", "name": "鋼構造・コンクリート"},
        "土質及び基礎": {"id": "soil_foundation", "name": "土質・基礎"},
        "施工計画、施工設備及び積算": {"id": "construction_planning", "name": "施工計画"},
        "上水道及び工業用水道": {"id": "water_supply", "name": "上下水道"},
        "森林土木": {"id": "forest_engineering", "name": "森林土木"},
        "農業土木": {"id": "agricultural_engineering", "name": "農業土木"},
        "トンネル": {"id": "tunnel", "name": "トンネル"}
    }
    
    for category in categories:
        if category in department_mapping:
            dept_info = department_mapping[category]
            
            # 年度・問題数情報追加
            by_category = specialist_analysis.get("by_category", {})
            category_data = by_category.get(category, {})
            
            departments.append({
                "id": dept_info["id"],
                "name": dept_info["name"],
                "csv_category": category,
                "type": "specialist",
                "years": sorted(category_data.keys()),
                "total_questions": sum(category_data.values()),
                "questions_per_year": dict(category_data)
            })
    
    return departments

def calculate_data_coverage(specialist_analysis):
    """データ網羅率計算"""
    by_category = specialist_analysis.get("by_category", {})
    years = specialist_analysis.get("year_range", [])
    
    if not years or not by_category:
        return 0
    
    total_possible = len(by_category) * len(years)
    actual_coverage = 0
    
    for category, year_data in by_category.items():
        actual_coverage += len([y for y in years if y in year_data and year_data[y] > 0])
    
    return round((actual_coverage / total_possible) * 100, 1) if total_possible > 0 else 0

def generate_detailed_report(analysis_result):
    """詳細レポート生成"""
    print("\n" + "=" * 80)
    print("RCCM試験システム 13部門完全調査レポート")
    print("=" * 80)
    
    # 基礎科目情報
    basic = analysis_result.get("basic_subjects", {})
    print(f"\n基礎科目（共通）")
    print(f"   問題数: {basic.get('total_questions', 0)}問")
    print(f"   ファイル: 4-1.csv")
    
    # 専門科目情報
    specialist = analysis_result.get("specialist_subjects", {})
    print(f"\n専門科目")
    print(f"   総問題数: {specialist.get('total_questions', 0)}問")
    print(f"   年度範囲: {specialist.get('year_range', [])}")
    print(f"   年度ファイル数: {len(specialist.get('by_year', {}))}")
    
    # 部門別詳細
    departments = analysis_result.get("complete_departments", [])
    print(f"\n全13部門詳細")
    for i, dept in enumerate(departments, 1):
        print(f"   {i:2d}. {dept['name']} ({dept['id']})")
        if dept['type'] == 'specialist':
            print(f"       問題数: {dept.get('total_questions', 0)}問")
            print(f"       対象年度: {len(dept.get('years', []))}年分")
    
    # データ品質情報
    quality = analysis_result.get("data_quality", {})
    print(f"\nデータ品質")
    print(f"   年度ギャップ: {quality.get('year_gaps', [])}")
    print(f"   エンコーディング問題: {quality.get('encoding_issues_count', 0)}件")
    print(f"   欠損フィールド: {quality.get('missing_fields_count', 0)}件")
    
    # サマリー
    summary = analysis_result.get("summary", {})
    print(f"\n総合サマリー")
    print(f"   総部門数: {summary.get('total_departments', 0)}部門")
    print(f"   総年度数: {summary.get('total_years', 0)}年")
    print(f"   総問題数: {summary.get('total_questions', 0)}問")
    print(f"   データ網羅率: {summary.get('data_coverage', 0)}%")

if __name__ == "__main__":
    try:
        result = analyze_rccm_system()
        print("\n調査完了！")
    except Exception as e:
        print(f"\nエラー発生: {e}")
        import traceback
        traceback.print_exc()