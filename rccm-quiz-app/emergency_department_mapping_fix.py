#!/usr/bin/env python3
"""
ULTRATHIN区段階42: 緊急部門名マッピング修正
目的: 失敗している5部門の部門名マッピング問題を完全修正
"""

import requests
import json
import time
from datetime import datetime

def test_department_mapping_fix():
    """部門名マッピング修正のテスト"""
    
    print("🛡️ ULTRATHIN区段階42: 緊急部門名マッピング修正")
    print("=" * 80)
    print("📋 対象: 失敗中の5部門の部門名マッピング修正")
    print("🎯 目標: 全13部門でリダイレクトチェーン成功")
    print("")
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # 失敗している5部門とその正しいマッピング
    failed_departments = {
        "都市計画": "都市計画及び地方計画",
        "鋼構造・コンクリート": "鋼構造及びコンクリート", 
        "土質・基礎": "土質及び基礎",
        "施工計画": "施工計画、施工設備及び積算",
        "上下水道": "上水道及び工業用水道"
    }
    
    # 成功している部門（参考）
    working_departments = [
        "基礎科目", "道路", "河川、砂防及び海岸・海洋", "造園", 
        "建設環境", "森林土木", "農業土木", "トンネル"
    ]
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "stage": "ULTRATHIN区段階42",
        "functionality": "部門名マッピング修正",
        "failed_departments_test": {},
        "working_departments_test": {},
        "mapping_analysis": {}
    }
    
    print("🔍 失敗部門テスト開始")
    print("-" * 60)
    
    # 失敗部門のテスト
    for dept_url, dept_data in failed_departments.items():
        print(f"\n📋 {dept_url} → {dept_data} テスト...")
        
        result = test_department_mapping(session, base_url, dept_url, dept_data)
        test_results["failed_departments_test"][dept_url] = result
        
        if result["redirect_successful"]:
            print(f"  ✅ リダイレクト: 成功")
        else:
            print(f"  ❌ リダイレクト: 失敗 ({result['status_code']})")
            print(f"    エラー詳細: {result.get('error_content', 'N/A')[:100]}...")
    
    print("\n🔍 正常部門確認テスト")
    print("-" * 60)
    
    # 正常部門の確認テスト（サンプル）
    for dept in working_departments[:3]:  # 最初の3部門のみテスト
        print(f"\n📋 {dept} 確認テスト...")
        
        result = test_department_mapping(session, base_url, dept, dept)
        test_results["working_departments_test"][dept] = result
        
        if result["redirect_successful"]:
            print(f"  ✅ リダイレクト: 正常")
        else:
            print(f"  ⚠️ リダイレクト: 異常")
    
    # 総合分析
    print("\n🔍 マッピング問題分析")
    print("-" * 60)
    
    failed_fixed = sum(1 for result in test_results["failed_departments_test"].values() 
                      if result["redirect_successful"])
    
    working_stable = sum(1 for result in test_results["working_departments_test"].values() 
                        if result["redirect_successful"])
    
    analysis = {
        "failed_departments_count": len(failed_departments),
        "failed_fixed_count": failed_fixed,
        "working_departments_tested": len(test_results["working_departments_test"]),
        "working_stable_count": working_stable,
        "fix_success_rate": failed_fixed / len(failed_departments) * 100,
        "mapping_issue_identified": failed_fixed < len(failed_departments),
        "requires_code_fix": failed_fixed < len(failed_departments)
    }
    
    test_results["mapping_analysis"] = analysis
    
    print(f"  📊 失敗部門修正: {failed_fixed}/{len(failed_departments)} ({analysis['fix_success_rate']:.1f}%)")
    print(f"  📊 正常部門安定: {working_stable}/{len(test_results['working_departments_test'])}")
    print(f"  🔍 マッピング問題: {'特定済み' if analysis['mapping_issue_identified'] else '解決済み'}")
    print(f"  ⚡ コード修正必要: {'YES' if analysis['requires_code_fix'] else 'NO'}")
    
    # 結果保存
    output_file = f"emergency_department_mapping_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果: {output_file}")
    
    if analysis["requires_code_fix"]:
        print("\n⚠️ コード修正が必要です")
        print("📋 修正対象: 部門名マッピング機能の改善")
        print("🎯 目標: 全13部門でのリダイレクトチェーン成功")
    else:
        print("\n✅ 部門名マッピング修正完了")
    
    return test_results

def test_department_mapping(session, base_url, dept_url, dept_data):
    """個別部門のマッピングテスト"""
    
    result = {
        "department_url": dept_url,
        "department_data": dept_data,
        "redirect_successful": False,
        "status_code": None,
        "response_details": {}
    }
    
    try:
        if dept_url == "基礎科目":
            response = session.post(
                f"{base_url}/start_exam/{dept_url}",
                data={"questions": "10"},
                allow_redirects=False,
                timeout=15
            )
        else:
            response = session.post(
                f"{base_url}/start_exam/{dept_url}",
                data={"questions": "10", "year": "2016"},
                allow_redirects=False,
                timeout=15
            )
        
        result["status_code"] = response.status_code
        result["redirect_successful"] = response.status_code in [301, 302]
        
        result["response_details"] = {
            "location": response.headers.get('Location', ''),
            "content_length": len(response.text),
            "has_redirect_header": 'Location' in response.headers
        }
        
        # エラー内容の分析
        if response.status_code == 200:
            content = response.text
            if "エラー" in content or "error" in content.lower():
                # エラーページの場合
                error_indicators = [
                    "該当する部門が見つかりません",
                    "部門名が正しくありません", 
                    "利用できません",
                    "not found",
                    "無効な部門"
                ]
                
                for indicator in error_indicators:
                    if indicator in content:
                        result["error_content"] = indicator
                        break
                else:
                    result["error_content"] = "不明なエラー"
            else:
                result["error_content"] = "部門選択ページ（リダイレクト失敗）"
        
    except Exception as e:
        result["error"] = str(e)
        result["redirect_successful"] = False
    
    return result

if __name__ == "__main__":
    test_department_mapping_fix()