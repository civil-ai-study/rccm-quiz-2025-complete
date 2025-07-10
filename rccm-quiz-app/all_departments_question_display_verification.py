#!/usr/bin/env python3
"""
ULTRATHIN区段階40: 全部門での問題表示確認
目的: 全13部門で問題が正しく表示されることを確認
"""

import requests
import json
import time
from datetime import datetime
import re

def verify_all_departments_question_display():
    """全部門での問題表示検証"""
    
    print("🛡️ ULTRATHIN区段階40: 全部門問題表示検証開始")
    print("=" * 80)
    print("📋 対象: 全13部門での問題表示品質確認")
    print("🎯 目標: 各部門で問題文・選択肢が正しく表示")
    print("")
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # 全13部門定義
    all_departments = [
        "基礎科目",
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
    
    verification_results = {
        "timestamp": datetime.now().isoformat(),
        "stage": "ULTRATHIN区段階40",
        "functionality": "全部門問題表示",
        "department_results": {}
    }
    
    print("🔍 部門別問題表示検証開始")
    print("-" * 60)
    
    for dept in all_departments:
        print(f"\n📋 {dept}部門検証...")
        
        dept_result = verify_department_question_display(session, base_url, dept)
        verification_results["department_results"][dept] = dept_result
        
        # 結果表示
        if dept_result["display_quality"]["all_elements_present"]:
            print(f"  ✅ 問題表示: 完全")
        else:
            print(f"  ❌ 問題表示: 不完全")
            missing = []
            if not dept_result["display_quality"]["has_question_text"]:
                missing.append("問題文")
            if not dept_result["display_quality"]["has_all_options"]:
                missing.append("選択肢")
            if not dept_result["display_quality"]["has_navigation"]:
                missing.append("ナビゲーション")
            print(f"    不足要素: {', '.join(missing)}")
        
        time.sleep(1)  # サーバー負荷軽減
    
    # 総合評価
    print("\n🔍 総合評価")
    print("-" * 60)
    
    perfect_departments = []
    imperfect_departments = []
    failed_departments = []
    
    for dept, result in verification_results["department_results"].items():
        if result["display_quality"]["all_elements_present"]:
            perfect_departments.append(dept)
        elif result["access_successful"]:
            imperfect_departments.append(dept)
        else:
            failed_departments.append(dept)
    
    overall_assessment = {
        "total_departments": len(all_departments),
        "perfect_display_count": len(perfect_departments),
        "imperfect_display_count": len(imperfect_departments),
        "failed_access_count": len(failed_departments),
        "perfect_display_rate": len(perfect_departments) / len(all_departments) * 100,
        "system_quality": "excellent" if len(perfect_departments) == len(all_departments) else 
                         "good" if len(perfect_departments) >= 10 else
                         "needs_improvement",
        "perfect_departments": perfect_departments,
        "imperfect_departments": imperfect_departments,
        "failed_departments": failed_departments
    }
    
    verification_results["overall_assessment"] = overall_assessment
    
    print(f"  📊 完全表示部門: {len(perfect_departments)}/{len(all_departments)} ({overall_assessment['perfect_display_rate']:.1f}%)")
    print(f"  📊 部分表示部門: {len(imperfect_departments)}")
    print(f"  📊 アクセス失敗: {len(failed_departments)}")
    print(f"  🎯 システム品質: {overall_assessment['system_quality']}")
    
    if imperfect_departments:
        print(f"\n  ⚠️ 部分表示部門:")
        for dept in imperfect_departments[:5]:
            print(f"    - {dept}")
    
    if failed_departments:
        print(f"\n  ❌ アクセス失敗部門:")
        for dept in failed_departments:
            print(f"    - {dept}")
    
    # 結果保存
    output_file = f"all_departments_question_display_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verification_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果: {output_file}")
    
    if overall_assessment["system_quality"] == "excellent":
        print("\n✅ 全部門で問題表示が完全に機能しています")
    else:
        print(f"\n⚠️ {len(imperfect_departments + failed_departments)}部門で改善が必要です")
    
    return verification_results

def verify_department_question_display(session, base_url, department):
    """個別部門の問題表示検証"""
    
    result = {
        "department": department,
        "access_successful": False,
        "response_details": {},
        "display_quality": {
            "has_question_text": False,
            "has_all_options": False,
            "has_navigation": False,
            "has_progress_indicator": False,
            "all_elements_present": False
        },
        "sample_content": {}
    }
    
    try:
        # 部門別試験開始
        if department == "基礎科目":
            response = session.post(
                f"{base_url}/start_exam/{department}",
                data={"questions": "10"},
                allow_redirects=True,
                timeout=15
            )
        else:
            response = session.post(
                f"{base_url}/start_exam/{department}",
                data={"questions": "10", "year": "2016"},
                allow_redirects=True,
                timeout=15
            )
        
        result["access_successful"] = response.status_code == 200
        result["response_details"] = {
            "status_code": response.status_code,
            "final_url": response.url,
            "content_length": len(response.text)
        }
        
        if response.status_code == 200:
            content = response.text
            
            # 問題文の存在確認
            question_patterns = [
                r'<div[^>]*class="[^"]*question[^"]*"[^>]*>([^<]+)',
                r'問題\d+[：:]([^<]+)',
                r'<p[^>]*>.*?次のうち.*?</p>',
                r'Q\d+[\.:]([^<]+)'
            ]
            
            for pattern in question_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    result["display_quality"]["has_question_text"] = True
                    result["sample_content"]["question_sample"] = match.group(0)[:100] + "..."
                    break
            
            # 選択肢の存在確認
            option_patterns = [
                r'<input[^>]*type="radio"[^>]*>',
                r'option_[a-d]',
                r'選択肢[A-D]',
                r'<label[^>]*for="[^"]*option'
            ]
            
            option_count = 0
            for pattern in option_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                option_count += len(matches)
            
            result["display_quality"]["has_all_options"] = option_count >= 4
            result["sample_content"]["option_count"] = option_count
            
            # ナビゲーション要素の確認
            nav_patterns = [
                r'次の問題',
                r'前の問題',
                r'<button[^>]*>.*?(次|前|Next|Previous)',
                r'href="[^"]*\?next=',
                r'結果を見る'
            ]
            
            for pattern in nav_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result["display_quality"]["has_navigation"] = True
                    break
            
            # 進捗表示の確認
            progress_patterns = [
                r'問題\s*\d+/\d+',
                r'第\s*\d+\s*問',
                r'progress',
                r'\d+/\d+問'
            ]
            
            for pattern in progress_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result["display_quality"]["has_progress_indicator"] = True
                    break
            
            # 全要素の存在判定
            result["display_quality"]["all_elements_present"] = (
                result["display_quality"]["has_question_text"] and
                result["display_quality"]["has_all_options"] and
                result["display_quality"]["has_navigation"]
            )
            
    except Exception as e:
        result["error"] = str(e)
        result["access_successful"] = False
    
    return result

if __name__ == "__main__":
    verify_all_departments_question_display()