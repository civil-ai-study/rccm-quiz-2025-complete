#!/usr/bin/env python3
"""
簡易版第三者検証: 4-1/4-2分離実装の重要なエッジケースと品質問題を深掘り分析
Flask依存性を排除した基本検証
"""

import os
import sys
import json
import tempfile
import csv
from datetime import datetime

def test_file_existence():
    """CSVファイルの物理的存在確認"""
    files_to_check = [
        "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv",
        "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv"
    ]
    
    results = []
    for file_path in files_to_check:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            results.append({
                "file": os.path.basename(file_path),
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        else:
            results.append({
                "file": os.path.basename(file_path),
                "exists": False
            })
    
    return {
        "test": "file_existence",
        "status": "PASSED" if all(r["exists"] for r in results) else "FAILED",
        "results": results
    }

def test_csv_structure():
    """CSVファイルの構造とBOM問題の検証"""
    files_to_check = [
        "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv",
        "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv"
    ]
    
    results = []
    for file_path in files_to_check:
        try:
            # BOM検出
            with open(file_path, 'rb') as f:
                first_bytes = f.read(3)
                has_bom = first_bytes == b'\xef\xbb\xbf'
            
            # CSV構造チェック
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                row_count = sum(1 for _ in reader)
            
            results.append({
                "file": os.path.basename(file_path),
                "has_bom": has_bom,
                "headers": headers,
                "row_count": row_count,
                "status": "OK"
            })
        except Exception as e:
            results.append({
                "file": os.path.basename(file_path),
                "status": "ERROR",
                "error": str(e)
            })
    
    return {
        "test": "csv_structure",
        "status": "PASSED" if all(r["status"] == "OK" for r in results) else "FAILED",
        "results": results
    }

def test_id_ranges_and_duplicates():
    """ID範囲と重複の検証"""
    try:
        # 4-1.csv のID範囲チェック
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            ids_4_1 = [int(row['id']) for row in reader]
        
        # 4-2_2016.csv のID範囲チェック
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            ids_4_2 = [int(row['id']) for row in reader]
        
        # 重複チェック
        set_4_1 = set(ids_4_1)
        set_4_2 = set(ids_4_2)
        duplicates = set_4_1.intersection(set_4_2)
        
        # 内部重複チェック
        internal_duplicates_4_1 = len(ids_4_1) - len(set_4_1)
        internal_duplicates_4_2 = len(ids_4_2) - len(set_4_2)
        
        return {
            "test": "id_ranges_and_duplicates",
            "status": "PASSED" if len(duplicates) == 0 and internal_duplicates_4_1 == 0 and internal_duplicates_4_2 == 0 else "FAILED",
            "4_1_range": f"{min(ids_4_1)}-{max(ids_4_1)}",
            "4_2_range": f"{min(ids_4_2)}-{max(ids_4_2)}",
            "4_1_count": len(ids_4_1),
            "4_2_count": len(ids_4_2),
            "cross_duplicates": len(duplicates),
            "internal_duplicates_4_1": internal_duplicates_4_1,
            "internal_duplicates_4_2": internal_duplicates_4_2,
            "duplicate_ids": list(duplicates)
        }
    except Exception as e:
        return {
            "test": "id_ranges_and_duplicates",
            "status": "ERROR",
            "error": str(e)
        }

def test_content_integrity():
    """データ内容の整合性チェック"""
    try:
        # 4-1.csv の内容チェック
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_4_1 = list(reader)
        
        # 4-2_2016.csv の内容チェック
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_4_2 = list(reader)
        
        # カテゴリー分析
        categories_4_1 = set(row['category'] for row in data_4_1)
        categories_4_2 = set(row['category'] for row in data_4_2)
        
        # 年度分析
        years_4_1 = set(row['year'] for row in data_4_1 if row['year'])
        years_4_2 = set(row['year'] for row in data_4_2 if row['year'])
        
        # 必須フィールドチェック
        required_fields = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        missing_fields_4_1 = []
        missing_fields_4_2 = []
        
        for row in data_4_1:
            for field in required_fields:
                if field not in row or not row[field]:
                    missing_fields_4_1.append(f"ID {row.get('id', 'unknown')}: {field}")
        
        for row in data_4_2:
            for field in required_fields:
                if field not in row or not row[field]:
                    missing_fields_4_2.append(f"ID {row.get('id', 'unknown')}: {field}")
        
        return {
            "test": "content_integrity",
            "status": "PASSED" if len(missing_fields_4_1) == 0 and len(missing_fields_4_2) == 0 else "FAILED",
            "4_1_categories": list(categories_4_1),
            "4_2_categories": list(categories_4_2),
            "4_1_years": list(years_4_1),
            "4_2_years": list(years_4_2),
            "4_1_missing_fields": missing_fields_4_1[:10],  # 最初の10件のみ
            "4_2_missing_fields": missing_fields_4_2[:10],  # 最初の10件のみ
            "4_1_total_missing": len(missing_fields_4_1),
            "4_2_total_missing": len(missing_fields_4_2)
        }
    except Exception as e:
        return {
            "test": "content_integrity",
            "status": "ERROR",
            "error": str(e)
        }

def test_category_separation():
    """カテゴリー分離の検証"""
    try:
        # 4-1.csv のカテゴリー
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            categories_4_1 = set(row['category'] for row in reader)
        
        # 4-2_2016.csv のカテゴリー
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            categories_4_2 = set(row['category'] for row in reader)
        
        # カテゴリー重複チェック
        overlapping_categories = categories_4_1.intersection(categories_4_2)
        
        # 期待される分離状態
        expected_4_1_categories = {'共通'}  # 4-1は共通科目
        expected_4_2_categories = {'道路', '河川・砂防・海岸', '港湾・空港', '電力土木', '造園', '廃棄物・資源循環', '建設環境', '上下水道', '農業土木', '森林土木', '水産土木', '機械', '電気電子', '建設情報', '応用理学', '施工計画・施工設備・積算', '建設マネジメント', '構造', '地盤・土質', '鋼構造コンクリート', 'トンネル', '施工管理', '建設環境', '機械設計'}
        
        return {
            "test": "category_separation",
            "status": "PASSED" if len(overlapping_categories) == 0 else "FAILED",
            "4_1_categories": list(categories_4_1),
            "4_2_categories": list(categories_4_2),
            "overlapping_categories": list(overlapping_categories),
            "4_1_is_basic_only": categories_4_1 == expected_4_1_categories,
            "4_2_has_specialties": len(categories_4_2) > 1
        }
    except Exception as e:
        return {
            "test": "category_separation",
            "status": "ERROR",
            "error": str(e)
        }

def run_all_tests():
    """すべてのテストを実行"""
    results = []
    
    print("=== 簡易版第三者検証: 4-1/4-2分離実装 ===")
    print(f"実行時刻: {datetime.now()}")
    print()
    
    tests = [
        test_file_existence,
        test_csv_structure,
        test_id_ranges_and_duplicates,
        test_content_integrity,
        test_category_separation
    ]
    
    for test_func in tests:
        print(f"実行中: {test_func.__name__}")
        try:
            result = test_func()
            results.append(result)
            status = result.get('status', 'UNKNOWN')
            print(f"  結果: {status}")
        except Exception as e:
            error_result = {
                "test": test_func.__name__,
                "status": "ERROR",
                "error": str(e)
            }
            results.append(error_result)
            print(f"  結果: ERROR - {str(e)}")
        print()
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # 結果をJSONファイルに保存
    output_file = f"simplified_edge_case_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"検証結果が保存されました: {output_file}")
    
    # サマリー
    passed = sum(1 for r in results if r.get('status') == 'PASSED')
    failed = sum(1 for r in results if r.get('status') == 'FAILED')
    error = sum(1 for r in results if r.get('status') == 'ERROR')
    
    print(f"\n=== 検証結果サマリー ===")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")
    print(f"エラー: {error}")
    print(f"合計: {len(results)}")
    
    # 詳細結果表示
    print(f"\n=== 詳細結果 ===")
    for result in results:
        print(f"テスト: {result['test']}")
        print(f"ステータス: {result['status']}")
        if result['status'] == 'FAILED':
            print(f"  - 失敗理由: {result.get('error', '詳細は出力ファイルを参照')}")
        elif result['status'] == 'ERROR':
            print(f"  - エラー: {result.get('error', 'Unknown error')}")
        print()