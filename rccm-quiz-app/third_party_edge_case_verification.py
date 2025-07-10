#!/usr/bin/env python3
"""
第三者検証: 4-1/4-2分離実装の重要なエッジケースと品質問題を深掘り分析
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime

# アプリケーションのパスを追加
sys.path.insert(0, '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app')

try:
    from utils import load_questions_improved, DataLoadError, DataValidationError
    from app import app
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def test_file_not_found_error():
    """ファイルが存在しない場合のエラーハンドリング検証"""
    try:
        # 存在しないファイルパスを指定
        fake_path = "/nonexistent/path/fake.csv"
        result = load_questions_improved(fake_path)
        return {
            "test": "file_not_found",
            "status": "FAILED",
            "message": "FileNotFoundError が発生すべきでした",
            "result": result
        }
    except FileNotFoundError as e:
        return {
            "test": "file_not_found",
            "status": "PASSED",
            "message": "FileNotFoundError が正常に発生",
            "error": str(e)
        }
    except Exception as e:
        return {
            "test": "file_not_found",
            "status": "FAILED",
            "message": "予期しないエラー",
            "error": str(e)
        }

def test_invalid_csv_format():
    """不正なCSVフォーマットの場合のエラーハンドリング検証"""
    try:
        # 一時的に不正なCSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            # 不正なCSVデータ（必須列が不足）
            f.write("invalid,header,format\n")
            f.write("1,2,3\n")
            temp_path = f.name
        
        try:
            result = load_questions_improved(temp_path)
            return {
                "test": "invalid_csv_format",
                "status": "FAILED",
                "message": "DataValidationError が発生すべきでした",
                "result": result
            }
        except (DataValidationError, DataLoadError) as e:
            return {
                "test": "invalid_csv_format",
                "status": "PASSED",
                "message": "DataValidationError が正常に発生",
                "error": str(e)
            }
        except Exception as e:
            return {
                "test": "invalid_csv_format",
                "status": "FAILED",
                "message": "予期しないエラー",
                "error": str(e)
            }
        finally:
            # 一時ファイルを削除
            os.unlink(temp_path)
    except Exception as e:
        return {
            "test": "invalid_csv_format",
            "status": "FAILED",
            "message": "テストセットアップエラー",
            "error": str(e)
        }

def test_bom_handling():
    """BOM付きCSVファイルの処理検証"""
    try:
        # BOM付きCSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            # UTF-8 BOM + 正常なCSVデータ
            bom_data = b'\xef\xbb\xbf'  # UTF-8 BOM
            csv_data = b'id,category,year,question,option_a,option_b,option_c,option_d,correct_answer,explanation,reference,difficulty\n'
            csv_data += b'1,test,2024,test question,a,b,c,d,a,test explanation,test reference,standard\n'
            f.write(bom_data + csv_data)
            temp_path = f.name
        
        try:
            result = load_questions_improved(temp_path)
            
            # BOMが正しく処理されているか確認
            if result and len(result) > 0:
                first_question = result[0]
                # idフィールドが正しく認識されているか確認
                if 'id' in first_question and first_question['id'] == '1':
                    return {
                        "test": "bom_handling",
                        "status": "PASSED",
                        "message": "BOMが正しく処理されました",
                        "questions_count": len(result),
                        "first_question_id": first_question['id']
                    }
                else:
                    return {
                        "test": "bom_handling",
                        "status": "FAILED",
                        "message": "BOM処理に問題があります",
                        "first_question_keys": list(first_question.keys()),
                        "first_question": first_question
                    }
            else:
                return {
                    "test": "bom_handling",
                    "status": "FAILED",
                    "message": "データが読み込まれませんでした",
                    "result": result
                }
        finally:
            # 一時ファイルを削除
            os.unlink(temp_path)
    except Exception as e:
        return {
            "test": "bom_handling",
            "status": "FAILED",
            "message": "テスト実行エラー",
            "error": str(e)
        }

def test_id_uniqueness():
    """ID重複チェック"""
    try:
        # 4-1.csv のIDをチェック
        csv_4_1_path = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv"
        questions_4_1 = load_questions_improved(csv_4_1_path)
        
        # 4-2_2016.csv のIDをチェック
        csv_4_2_path = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2016.csv"
        questions_4_2 = load_questions_improved(csv_4_2_path)
        
        # IDを抽出
        ids_4_1 = set(q['id'] for q in questions_4_1)
        ids_4_2 = set(q['id'] for q in questions_4_2)
        
        # 重複チェック
        duplicate_ids = ids_4_1.intersection(ids_4_2)
        
        # ID範囲チェック
        min_id_4_1 = min(int(q['id']) for q in questions_4_1)
        max_id_4_1 = max(int(q['id']) for q in questions_4_1)
        min_id_4_2 = min(int(q['id']) for q in questions_4_2)
        max_id_4_2 = max(int(q['id']) for q in questions_4_2)
        
        return {
            "test": "id_uniqueness",
            "status": "PASSED" if len(duplicate_ids) == 0 else "FAILED",
            "message": "ID重複チェック完了",
            "duplicate_count": len(duplicate_ids),
            "duplicate_ids": list(duplicate_ids),
            "4_1_range": f"{min_id_4_1}-{max_id_4_1}",
            "4_2_range": f"{min_id_4_2}-{max_id_4_2}",
            "4_1_count": len(questions_4_1),
            "4_2_count": len(questions_4_2)
        }
    except Exception as e:
        return {
            "test": "id_uniqueness",
            "status": "FAILED",
            "message": "ID重複チェックエラー",
            "error": str(e)
        }

def test_session_isolation():
    """セッション分離テスト"""
    try:
        with app.test_client() as client:
            # 4-1試験開始
            response_4_1 = client.post('/start_exam/基礎科目', 
                                     data={'questions': '5', 'year': '2024'})
            
            # 4-2試験開始（別セッション）
            response_4_2 = client.post('/start_exam/専門科目', 
                                     data={'questions': '5', 'year': '2016'})
            
            # レスポンスチェック
            status_4_1 = response_4_1.status_code
            status_4_2 = response_4_2.status_code
            
            return {
                "test": "session_isolation",
                "status": "PASSED" if status_4_1 == 200 and status_4_2 == 200 else "FAILED",
                "message": "セッション分離テスト完了",
                "4_1_status": status_4_1,
                "4_2_status": status_4_2,
                "4_1_response_length": len(response_4_1.data),
                "4_2_response_length": len(response_4_2.data)
            }
    except Exception as e:
        return {
            "test": "session_isolation",
            "status": "FAILED",
            "message": "セッション分離テストエラー",
            "error": str(e)
        }

def run_all_tests():
    """すべてのテストを実行"""
    results = []
    
    print("=== 第三者検証: 4-1/4-2分離実装 エッジケース検証 ===")
    print(f"実行時刻: {datetime.now()}")
    print()
    
    tests = [
        test_file_not_found_error,
        test_invalid_csv_format,
        test_bom_handling,
        test_id_uniqueness,
        test_session_isolation
    ]
    
    for test_func in tests:
        print(f"実行中: {test_func.__name__}")
        try:
            result = test_func()
            results.append(result)
            status = result.get('status', 'UNKNOWN')
            message = result.get('message', 'No message')
            print(f"  結果: {status} - {message}")
        except Exception as e:
            error_result = {
                "test": test_func.__name__,
                "status": "ERROR",
                "message": "テスト実行中にエラーが発生",
                "error": str(e)
            }
            results.append(error_result)
            print(f"  結果: ERROR - {str(e)}")
        print()
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # 結果をJSONファイルに保存
    output_file = f"third_party_edge_case_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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