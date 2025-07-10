#!/usr/bin/env python3
"""
本番環境で基礎科目10問設定での完走テスト
"""

import requests
import json
import time
from datetime import datetime

def test_basic_10_questions():
    """基礎科目10問の完走テスト"""
    base_url = "http://157.7.139.212"
    session = requests.Session()
    
    results = {
        "test_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "基礎科目10問完走テスト",
        "questions": [],
        "errors": [],
        "success": True
    }
    
    print("=== 基礎科目10問完走テスト開始 ===")
    print(f"開始時刻: {results['test_start']}")
    print(f"ベースURL: {base_url}")
    print()
    
    try:
        # Step 1: トップページアクセス
        print("Step 1: トップページアクセス")
        response = session.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print()
        
        # Step 2: 試験開始
        print("Step 2: 基礎科目10問の試験を開始")
        start_data = {
            "exam_type": "basic",
            "num_questions": "10"
        }
        
        response = session.post(f"{base_url}/start_exam", data=start_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            results["errors"].append({
                "step": "start_exam",
                "status_code": response.status_code,
                "error": "試験開始に失敗"
            })
            results["success"] = False
            return results
        
        print("試験開始成功")
        print()
        
        # Step 3: 各問題に回答
        for i in range(1, 11):
            print(f"Step 3-{i}: 第{i}問目に回答")
            
            # 問題ページを取得
            response = session.get(f"{base_url}/question/{i}")
            print(f"問題取得 - Status: {response.status_code}")
            
            question_info = {
                "question_number": i,
                "get_status": response.status_code,
                "post_status": None,
                "error": None
            }
            
            if response.status_code != 200:
                question_info["error"] = f"問題取得失敗 (Status: {response.status_code})"
                results["questions"].append(question_info)
                results["errors"].append({
                    "step": f"question_{i}_get",
                    "status_code": response.status_code,
                    "error": question_info["error"]
                })
                results["success"] = False
                continue
            
            # 回答を送信（選択肢Aを選択）
            answer_data = {
                "answer": "A",
                "question_number": str(i)
            }
            
            response = session.post(f"{base_url}/submit_answer", data=answer_data)
            print(f"回答送信 - Status: {response.status_code}")
            question_info["post_status"] = response.status_code
            
            if response.status_code == 302:
                # リダイレクトの場合は次の問題へ
                print(f"第{i}問目回答成功（リダイレクト）")
            elif response.status_code == 200:
                print(f"第{i}問目回答成功")
            else:
                question_info["error"] = f"回答送信失敗 (Status: {response.status_code})"
                results["errors"].append({
                    "step": f"question_{i}_post",
                    "status_code": response.status_code,
                    "error": question_info["error"]
                })
                results["success"] = False
            
            results["questions"].append(question_info)
            print()
            
            # 短い待機時間
            time.sleep(0.5)
        
        # Step 4: 結果ページ確認
        print("Step 4: 結果ページ確認")
        response = session.get(f"{base_url}/result")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("結果ページ取得成功")
            # 結果の内容を簡単に確認
            if "あなたのスコア" in response.text or "点" in response.text:
                print("結果が正常に表示されています")
            else:
                print("警告: 結果ページの内容が予期したものと異なる可能性があります")
        else:
            results["errors"].append({
                "step": "result",
                "status_code": response.status_code,
                "error": "結果ページ取得失敗"
            })
            results["success"] = False
        
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        results["errors"].append({
            "step": "exception",
            "error": str(e)
        })
        results["success"] = False
    
    results["test_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 結果サマリー
    print("\n=== テスト結果サマリー ===")
    print(f"終了時刻: {results['test_end']}")
    print(f"成功: {results['success']}")
    print(f"回答した問題数: {len(results['questions'])}")
    print(f"エラー数: {len(results['errors'])}")
    
    if results['errors']:
        print("\nエラー詳細:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # 結果をJSONファイルに保存
    output_file = f"basic_10_questions_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細な結果を {output_file} に保存しました")
    
    return results

if __name__ == "__main__":
    test_basic_10_questions()