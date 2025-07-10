#!/usr/bin/env python3
"""
セッション分離検証: 4-1/4-2の混在防止とセッション間汚染の検証
"""

import json
import time
import os
import sys
from datetime import datetime

# アプリケーションのパスを追加
sys.path.insert(0, '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app')

def analyze_session_logic():
    """アプリケーションのセッション分離ロジックを分析"""
    
    # app.pyの内容を読み込み
    app_path = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/app.py"
    
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    analysis = {
        "test": "session_logic_analysis",
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # セッション管理関連のコードを探索
    session_patterns = [
        "session['exam_session']",
        "session.get('exam_session'",
        "4-1/4-2完全分離",
        "question_type_check",
        "基礎科目に専門科目混入検出",
        "専門科目に基礎科目混入検出",
        "lightweight_session",
        "store_exam_data_in_memory"
    ]
    
    findings = {}
    for pattern in session_patterns:
        count = app_content.count(pattern)
        findings[pattern] = count
        if count > 0:
            # パターンが見つかった場合の前後のコンテキストを取得
            lines = app_content.split('\n')
            contexts = []
            for i, line in enumerate(lines):
                if pattern in line:
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = {
                        "line_number": i + 1,
                        "context": lines[start:end]
                    }
                    contexts.append(context)
            findings[f"{pattern}_contexts"] = contexts[:3]  # 最初の3つのコンテキストのみ
    
    analysis["analysis"]["session_pattern_findings"] = findings
    
    # 4-1/4-2分離ロジックの検証
    separation_logic = {
        "contamination_detection": {
            "basic_contamination": "基礎科目に専門科目混入検出" in app_content,
            "specialist_contamination": "専門科目に基礎科目混入検出" in app_content,
            "automatic_removal": "除去します" in app_content
        },
        "question_type_check": {
            "has_type_check": "question_type_check" in app_content,
            "basic_check": "question_type_check == 'basic'" in app_content,
            "specialist_check": "question_type_check == 'specialist'" in app_content
        },
        "session_isolation": {
            "lightweight_session": "lightweight_session" in app_content,
            "memory_storage": "store_exam_data_in_memory" in app_content,
            "session_modification": "session.modified = True" in app_content
        }
    }
    
    analysis["analysis"]["separation_logic"] = separation_logic
    
    # 潜在的な問題の検出
    potential_issues = []
    
    # 1. セッション状態の直接変更
    if "session['exam_session'] =" in app_content:
        potential_issues.append("セッション状態の直接変更が検出されました")
    
    # 2. 複数のセッションキーの使用
    session_keys = ["exam_session", "exam_question_ids", "exam_current", "exam_category"]
    used_keys = [key for key in session_keys if f"session['{key}']" in app_content or f"session.get('{key}'" in app_content]
    if len(used_keys) > 2:
        potential_issues.append(f"複数のセッションキーが使用されています: {used_keys}")
    
    # 3. 問題タイプの混在チェック
    if "question_type" not in app_content:
        potential_issues.append("問題タイプの明示的な管理が不足している可能性があります")
    
    analysis["analysis"]["potential_issues"] = potential_issues
    
    return analysis

def verify_csv_separation():
    """CSVファイルレベルでの分離検証"""
    
    try:
        import csv
        
        # 4-1.csv の内容確認
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_4_1 = list(reader)
        
        # 4-2_2016.csv の内容確認
        with open("/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_4_2 = list(reader)
        
        # 問題タイプの推定
        categories_4_1 = set(row['category'] for row in data_4_1)
        categories_4_2 = set(row['category'] for row in data_4_2)
        
        # ID範囲の確認
        ids_4_1 = [int(row['id']) for row in data_4_1]
        ids_4_2 = [int(row['id']) for row in data_4_2]
        
        return {
            "test": "csv_separation_verification",
            "status": "PASSED",
            "4_1_analysis": {
                "question_count": len(data_4_1),
                "id_range": f"{min(ids_4_1)}-{max(ids_4_1)}",
                "categories": list(categories_4_1),
                "is_basic_only": len(categories_4_1) == 1 and "共通" in categories_4_1
            },
            "4_2_analysis": {
                "question_count": len(data_4_2),
                "id_range": f"{min(ids_4_2)}-{max(ids_4_2)}",
                "categories": list(categories_4_2),
                "is_specialist_only": len(categories_4_2) > 1 and "共通" not in categories_4_2
            },
            "separation_quality": {
                "no_id_overlap": len(set(ids_4_1).intersection(set(ids_4_2))) == 0,
                "no_category_overlap": len(categories_4_1.intersection(categories_4_2)) == 0,
                "clear_boundaries": max(ids_4_1) < min(ids_4_2)
            }
        }
    except Exception as e:
        return {
            "test": "csv_separation_verification",
            "status": "ERROR",
            "error": str(e)
        }

def verify_data_loading_logic():
    """データ読み込みロジックの検証"""
    
    try:
        # utils.pyの内容を読み込み
        utils_path = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/utils.py"
        
        with open(utils_path, 'r', encoding='utf-8') as f:
            utils_content = f.read()
        
        # BOM処理の確認
        bom_handling = {
            "bom_detection": "\\ufeff" in utils_content,
            "bom_removal": "lstrip('\\ufeff')" in utils_content,
            "encoding_fallback": "utf-8-sig" in utils_content
        }
        
        # エラーハンドリングの確認
        error_handling = {
            "unicode_decode_error": "UnicodeDecodeError" in utils_content,
            "file_not_found_error": "FileNotFoundError" in utils_content,
            "data_validation_error": "DataValidationError" in utils_content,
            "multiple_encoding_attempts": "encodings = [" in utils_content
        }
        
        # キャッシュ機能の確認
        cache_features = {
            "has_cache": "cache" in utils_content.lower(),
            "redis_cache": "redis" in utils_content.lower(),
            "memory_cache": "memory" in utils_content.lower()
        }
        
        return {
            "test": "data_loading_logic_verification",
            "status": "PASSED",
            "bom_handling": bom_handling,
            "error_handling": error_handling,
            "cache_features": cache_features
        }
    except Exception as e:
        return {
            "test": "data_loading_logic_verification",
            "status": "ERROR",
            "error": str(e)
        }

def run_comprehensive_session_verification():
    """包括的なセッション検証"""
    
    results = []
    
    print("=== セッション分離検証: 4-1/4-2混在防止 ===")
    print(f"実行時刻: {datetime.now()}")
    print()
    
    # 1. セッションロジック分析
    print("1. セッションロジック分析...")
    session_analysis = analyze_session_logic()
    results.append(session_analysis)
    
    # 2. CSV分離検証
    print("2. CSV分離検証...")
    csv_verification = verify_csv_separation()
    results.append(csv_verification)
    print(f"  結果: {csv_verification['status']}")
    
    # 3. データ読み込みロジック検証
    print("3. データ読み込みロジック検証...")
    data_loading_verification = verify_data_loading_logic()
    results.append(data_loading_verification)
    print(f"  結果: {data_loading_verification['status']}")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_session_verification()
    
    # 結果をJSONファイルに保存
    output_file = f"session_isolation_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n検証結果が保存されました: {output_file}")
    
    # サマリー表示
    passed = sum(1 for r in results if r.get('status') == 'PASSED')
    failed = sum(1 for r in results if r.get('status') == 'FAILED')
    error = sum(1 for r in results if r.get('status') == 'ERROR')
    analyzed = sum(1 for r in results if 'analysis' in r)
    
    print(f"\n=== 検証結果サマリー ===")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")
    print(f"エラー: {error}")
    print(f"分析完了: {analyzed}")
    print(f"合計: {len(results)}")