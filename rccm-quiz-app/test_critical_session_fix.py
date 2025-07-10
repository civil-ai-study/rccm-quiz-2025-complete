#!/usr/bin/env python3
"""
🔥 CRITICAL SESSION FIX 検証テスト
根本修正後の基礎科目試験開始動作確認

修正内容:
1. start_exam関数のlightweight_session変数定義問題修正
2. exam_simulator_page関数のセッション読み取り処理追加
3. exam_question -> exam へのリダイレクト修正
4. exam関数での基礎科目/専門科目完全分離データ読み込み
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime

# プロジェクトパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_subject_exam_start():
    """基礎科目試験開始の完全テスト"""
    
    try:
        from app import app
        
        print("🔥 CRITICAL SESSION FIX 検証テスト開始")
        print("=" * 60)
        
        test_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_name": "critical_session_fix_verification",
            "修正内容": [
                "lightweight_session変数定義問題修正",
                "exam_simulator_pageセッション読み取り処理追加", 
                "exam_question->examリダイレクト修正",
                "基礎科目/専門科目データ読み込み分離"
            ],
            "tests": []
        }
        
        with app.test_client() as client:
            
            # テスト1: 基礎科目試験開始（GET）
            print("\n🧪 テスト1: 基礎科目試験開始 GET リクエスト")
            try:
                response = client.get('/start_exam/基礎科目?questions=10')
                print(f"   ステータス: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"   リダイレクト先: {response.location}")
                    test_results["tests"].append({
                        "test": "基礎科目試験開始GET",
                        "status": "PASS",
                        "response_code": response.status_code,
                        "redirect_location": response.location
                    })
                else:
                    print(f"   レスポンス内容（先頭100文字）: {response.get_data(as_text=True)[:100]}")
                    test_results["tests"].append({
                        "test": "基礎科目試験開始GET", 
                        "status": "FAIL",
                        "response_code": response.status_code,
                        "error": "Expected redirect but got different response"
                    })
                    
            except Exception as e:
                print(f"   ❌ エラー: {e}")
                test_results["tests"].append({
                    "test": "基礎科目試験開始GET",
                    "status": "ERROR", 
                    "error": str(e)
                })
            
            # テスト2: 基礎科目試験開始（POST）
            print("\n🧪 テスト2: 基礎科目試験開始 POST リクエスト")
            try:
                response = client.post('/start_exam/基礎科目', data={
                    'questions': '10',
                    'category': '基礎科目'
                })
                print(f"   ステータス: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"   リダイレクト先: {response.location}")
                    test_results["tests"].append({
                        "test": "基礎科目試験開始POST",
                        "status": "PASS",
                        "response_code": response.status_code,
                        "redirect_location": response.location
                    })
                else:
                    print(f"   レスポンス内容（先頭100文字）: {response.get_data(as_text=True)[:100]}")
                    test_results["tests"].append({
                        "test": "基礎科目試験開始POST",
                        "status": "FAIL", 
                        "response_code": response.status_code,
                        "error": "Expected redirect but got different response"
                    })
                    
            except Exception as e:
                print(f"   ❌ エラー: {e}")
                test_results["tests"].append({
                    "test": "基礎科目試験開始POST",
                    "status": "ERROR",
                    "error": str(e)
                })
            
            # テスト3: exam エンドポイントアクセス
            print("\n🧪 テスト3: /exam エンドポイント直接アクセス")
            try:
                # セッションコンテキストでテスト
                with client.session_transaction() as sess:
                    sess['exam_session'] = {
                        'exam_id': 'test_001',
                        'exam_type': '基礎科目',
                        'q_count': 10,
                        'current': 0,
                        'status': 'in_progress'
                    }
                    sess['exam_question_ids'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    sess['exam_current'] = 0
                
                response = client.get('/exam')
                print(f"   ステータス: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    if '問題' in content or 'question' in content.lower():
                        print("   ✅ 問題画面が正常に表示")
                        test_results["tests"].append({
                            "test": "exam画面表示",
                            "status": "PASS",
                            "response_code": response.status_code
                        })
                    else:
                        print("   ⚠️ 問題画面の内容が不完全")
                        test_results["tests"].append({
                            "test": "exam画面表示", 
                            "status": "PARTIAL",
                            "response_code": response.status_code,
                            "note": "画面表示はされるが問題内容が不完全"
                        })
                else:
                    print(f"   ❌ 期待されるステータス200でない: {response.status_code}")
                    test_results["tests"].append({
                        "test": "exam画面表示",
                        "status": "FAIL",
                        "response_code": response.status_code
                    })
                    
            except Exception as e:
                print(f"   ❌ エラー: {e}")
                test_results["tests"].append({
                    "test": "exam画面表示",
                    "status": "ERROR",
                    "error": str(e)
                })
            
            # テスト4: exam_simulator エンドポイントアクセス
            print("\n🧪 テスト4: /exam_simulator エンドポイント（修正後）")
            try:
                # セッションコンテキストでテスト
                with client.session_transaction() as sess:
                    sess['exam_session'] = {
                        'exam_id': 'test_002',
                        'exam_type': '基礎科目',
                        'q_count': 10,
                        'current': 0,
                        'status': 'in_progress'
                    }
                
                # メモリデータも設定
                from app import store_exam_data_in_memory
                store_exam_data_in_memory('test_002', {
                    'questions': [{'id': i, 'question': f'テスト問題{i}'} for i in range(1, 11)],
                    'current_question': 0,
                    'answers': {},
                    'flagged_ids': []
                })
                
                response = client.get('/exam_simulator')
                print(f"   ステータス: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    print("   ✅ exam_simulator画面が正常に表示")
                    test_results["tests"].append({
                        "test": "exam_simulator画面表示（修正後）",
                        "status": "PASS",
                        "response_code": response.status_code
                    })
                elif response.status_code == 302:
                    print(f"   ⚠️ リダイレクト発生: {response.location}")
                    test_results["tests"].append({
                        "test": "exam_simulator画面表示（修正後）",
                        "status": "REDIRECT",
                        "response_code": response.status_code,
                        "redirect_location": response.location
                    })
                else:
                    print(f"   ❌ 期待されるステータス200でない: {response.status_code}")
                    test_results["tests"].append({
                        "test": "exam_simulator画面表示（修正後）",
                        "status": "FAIL",
                        "response_code": response.status_code
                    })
                    
            except Exception as e:
                print(f"   ❌ エラー: {e}")
                test_results["tests"].append({
                    "test": "exam_simulator画面表示（修正後）",
                    "status": "ERROR",
                    "error": str(e)
                })
        
        # 結果集計
        total_tests = len(test_results["tests"])
        passed_tests = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
        failed_tests = sum(1 for t in test_results["tests"] if t["status"] in ["FAIL", "ERROR"])
        
        print("\n" + "=" * 60)
        print("🏁 テスト結果サマリー")
        print(f"   総テスト数: {total_tests}")
        print(f"   成功: {passed_tests}")
        print(f"   失敗: {failed_tests}")
        print(f"   成功率: {(passed_tests / total_tests * 100):.1f}%")
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": round(passed_tests / total_tests * 100, 1)
        }
        
        # 結果をJSONファイルに保存
        output_file = f"critical_session_fix_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細結果: {output_file}")
        
        if passed_tests == total_tests:
            print("\n🎉 全てのテストが成功！CRITICAL SESSION FIX は正常に動作しています。")
        elif passed_tests > failed_tests:
            print("\n✅ 大部分のテストが成功。一部の問題は継続調査が必要です。")
        else:
            print("\n⚠️ 重要な問題が残っています。追加の修正が必要です。")
        
        return test_results
        
    except Exception as e:
        print(f"\n💥 テスト実行中に致命的エラー: {e}")
        print(f"詳細: {traceback.format_exc()}")
        return {"error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    test_basic_subject_exam_start()