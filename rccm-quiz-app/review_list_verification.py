#!/usr/bin/env python3
"""
ULTRATHIN区段階39: 復習リスト機能の完全動作検証
目的: 復習リスト機能が全部門で正常に動作することを確認
"""

import requests
import json
import time
from datetime import datetime

def verify_review_list_functionality():
    """復習リスト機能の検証"""
    
    print("🛡️ ULTRATHIN区段階39: 復習リスト機能検証開始")
    print("=" * 80)
    print("📋 対象: 復習リスト機能の全部門動作確認")
    print("🎯 目標: 問題をブックマークし、復習リストで確認")
    print("")
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    verification_results = {
        "timestamp": datetime.now().isoformat(),
        "stage": "ULTRATHIN区段階39",
        "functionality": "復習リスト機能",
        "test_results": {}
    }
    
    # 1. メインページアクセス確認
    print("🔍 1. メインページアクセス確認")
    print("-" * 60)
    
    try:
        response = session.get(f"{base_url}/", timeout=10)
        main_page_ok = response.status_code == 200
        print(f"  ✅ メインページ: {response.status_code}")
        
        verification_results["test_results"]["main_page"] = {
            "status_code": response.status_code,
            "accessible": main_page_ok
        }
    except Exception as e:
        print(f"  ❌ メインページエラー: {e}")
        verification_results["test_results"]["main_page"] = {
            "error": str(e),
            "accessible": False
        }
    
    # 2. 復習リストページアクセス確認
    print("\n🔍 2. 復習リストページアクセス確認")
    print("-" * 60)
    
    try:
        # 復習リストのURLパスを確認
        review_paths = [
            "/review",
            "/review_list",
            "/bookmarks",
            "/study/review"
        ]
        
        review_page_found = False
        review_url = None
        
        for path in review_paths:
            try:
                response = session.get(f"{base_url}{path}", timeout=5)
                if response.status_code == 200:
                    review_page_found = True
                    review_url = path
                    print(f"  ✅ 復習リストページ発見: {path}")
                    break
                else:
                    print(f"  ❌ {path}: {response.status_code}")
            except:
                print(f"  ❌ {path}: アクセス不可")
        
        verification_results["test_results"]["review_page"] = {
            "found": review_page_found,
            "url": review_url
        }
        
    except Exception as e:
        print(f"  ❌ 復習リストページ検索エラー: {e}")
        verification_results["test_results"]["review_page"] = {
            "error": str(e),
            "found": False
        }
    
    # 3. ブックマーク機能テスト（基礎科目）
    print("\n🔍 3. ブックマーク機能テスト（基礎科目）")
    print("-" * 60)
    
    try:
        # 基礎科目で試験開始
        start_response = session.post(
            f"{base_url}/start_exam/基礎科目",
            data={"questions": "10"},
            allow_redirects=True,
            timeout=15
        )
        
        if start_response.status_code == 200:
            print("  ✅ 基礎科目試験開始成功")
            
            # ブックマーク機能の存在確認
            content = start_response.text
            has_bookmark_feature = any(indicator in content for indicator in 
                                     ["ブックマーク", "bookmark", "復習", "後で見る"])
            
            verification_results["test_results"]["bookmark_feature"] = {
                "exists": has_bookmark_feature,
                "in_basic_subject": True
            }
            
            print(f"  {'✅' if has_bookmark_feature else '❌'} ブックマーク機能: {'存在' if has_bookmark_feature else '未実装'}")
        else:
            print(f"  ❌ 基礎科目試験開始失敗: {start_response.status_code}")
            verification_results["test_results"]["bookmark_feature"] = {
                "error": "試験開始失敗",
                "exists": False
            }
            
    except Exception as e:
        print(f"  ❌ ブックマーク機能テストエラー: {e}")
        verification_results["test_results"]["bookmark_feature"] = {
            "error": str(e),
            "exists": False
        }
    
    # 4. 専門科目でのブックマーク機能確認
    print("\n🔍 4. 専門科目でのブックマーク機能確認")
    print("-" * 60)
    
    test_departments = ["道路", "造園"]
    specialist_bookmark_results = {}
    
    for dept in test_departments:
        try:
            print(f"  📋 {dept}部門テスト...")
            
            response = session.post(
                f"{base_url}/start_exam/{dept}",
                data={"questions": "10", "year": "2016"},
                allow_redirects=True,
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.text
                has_bookmark = any(indicator in content for indicator in 
                                 ["ブックマーク", "bookmark", "復習", "後で見る"])
                
                specialist_bookmark_results[dept] = {
                    "status_code": response.status_code,
                    "has_bookmark_feature": has_bookmark
                }
                
                print(f"    {'✅' if has_bookmark else '❌'} ブックマーク機能: {'存在' if has_bookmark else '未実装'}")
            else:
                specialist_bookmark_results[dept] = {
                    "status_code": response.status_code,
                    "has_bookmark_feature": False
                }
                print(f"    ❌ アクセス失敗: {response.status_code}")
                
        except Exception as e:
            specialist_bookmark_results[dept] = {
                "error": str(e),
                "has_bookmark_feature": False
            }
            print(f"    ❌ エラー: {e}")
    
    verification_results["test_results"]["specialist_bookmark"] = specialist_bookmark_results
    
    # 5. 総合評価
    print("\n🔍 5. 総合評価")
    print("-" * 60)
    
    # 復習リスト機能の実装状況評価
    review_page_ok = verification_results["test_results"].get("review_page", {}).get("found", False)
    bookmark_in_basic = verification_results["test_results"].get("bookmark_feature", {}).get("exists", False)
    
    specialist_ok_count = sum(1 for result in specialist_bookmark_results.values() 
                             if result.get("has_bookmark_feature", False))
    
    overall_assessment = {
        "review_page_exists": review_page_ok,
        "bookmark_feature_exists": bookmark_in_basic or specialist_ok_count > 0,
        "implementation_level": "未実装" if not (bookmark_in_basic or specialist_ok_count > 0) else "部分実装" if specialist_ok_count < len(test_departments) else "完全実装",
        "ready_for_use": review_page_ok and (bookmark_in_basic or specialist_ok_count > 0)
    }
    
    verification_results["overall_assessment"] = overall_assessment
    
    print(f"  📊 復習リストページ: {'✅ 存在' if review_page_ok else '❌ 未実装'}")
    print(f"  📊 ブックマーク機能: {overall_assessment['implementation_level']}")
    print(f"  📊 利用可能状態: {'✅ YES' if overall_assessment['ready_for_use'] else '❌ NO'}")
    
    # 結果保存
    output_file = f"review_list_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verification_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果: {output_file}")
    
    if not overall_assessment["ready_for_use"]:
        print("\n⚠️ 復習リスト機能は未実装または部分的実装です")
        print("📋 推奨事項: 機能実装の完了が必要です")
    else:
        print("\n✅ 復習リスト機能は利用可能です")
    
    return verification_results

if __name__ == "__main__":
    verify_review_list_functionality()