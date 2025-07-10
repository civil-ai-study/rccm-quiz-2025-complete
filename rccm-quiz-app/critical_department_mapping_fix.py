#!/usr/bin/env python3
"""
緊急修正: 専門科目部門マッピング問題の完全解決
"""

import csv
import os

def analyze_department_mapping_problem():
    """部門マッピング問題の分析"""
    
    print("🚨 部門マッピング問題の緊急分析")
    print("=" * 60)
    
    # アプリで使用されている部門名
    app_departments = [
        "道路", 
        "河川、砂防及び海岸・海洋",
        "都市計画",
        "造園",
        "建設環境", 
        "鋼構造・コンクリート",
        "土質・基礎",
        "施工計画",
        "上下水道",
        "森林土木",
        "農業土木",
        "トンネル"
    ]
    
    # データファイルの部門名を確認
    data_file = 'data/4-2_2016.csv'
    
    if os.path.exists(data_file):
        print(f"📋 データファイル分析: {data_file}")
        
        with open(data_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            file_departments = set()
            
            for row in reader:
                category = row.get('category', '').strip()
                if category:
                    file_departments.add(category)
        
        print(f"📊 ファイル内部門: {len(file_departments)}部門")
        for dept in sorted(file_departments):
            print(f"  - {dept}")
        
        print(f"\n📊 アプリ期待部門: {len(app_departments)}部門")
        for dept in app_departments:
            print(f"  - {dept}")
        
        print("\n🔍 マッチング分析:")
        
        matched = []
        unmatched_app = []
        unmatched_file = []
        
        for app_dept in app_departments:
            if app_dept in file_departments:
                matched.append(app_dept)
            else:
                unmatched_app.append(app_dept)
        
        for file_dept in file_departments:
            if file_dept not in app_departments:
                unmatched_file.append(file_dept)
        
        print(f"✅ マッチ: {len(matched)}部門")
        for dept in matched:
            print(f"  - {dept}")
        
        print(f"\n❌ アプリ側不一致: {len(unmatched_app)}部門")
        for dept in unmatched_app:
            print(f"  - {dept}")
        
        print(f"\n❌ ファイル側余剰: {len(unmatched_file)}部門")  
        for dept in unmatched_file:
            print(f"  - {dept}")
        
        # 修正提案
        print("\n🔧 修正提案:")
        
        if unmatched_app:
            print("アプリ側部門名を以下に修正:")
            for i, app_dept in enumerate(unmatched_app):
                # 類似する部門を探す
                for file_dept in file_departments:
                    if any(word in file_dept for word in app_dept.split('・')):
                        print(f"  '{app_dept}' → '{file_dept}'")
                        break
    
    else:
        print(f"❌ データファイルが見つかりません: {data_file}")

if __name__ == "__main__":
    analyze_department_mapping_problem()