#!/usr/bin/env python3
"""
ULTRATHIN区段階41: 修正済み問題表示検証
目的: 実際のHTMLリダイレクトチェーンに基づいた正確な問題表示確認
"""

import requests
import json
import time
from datetime import datetime

def verify_corrected_question_display():
    """修正済み問題表示検証 - 正確なリダイレクトチェーン対応"""
    
    print("🛡️ ULTRATHIN区段階41: 修正済み問題表示検証開始")
    print("=" * 80)
    print("📋 修正点: 実際のHTMLリダイレクトチェーン追跡")
    print("🎯 目標: /start_exam → /exam_question → /exam_simulator の流れ確認")
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
        "stage": "ULTRATHIN区段階41",
        "functionality": "修正済み問題表示",
        "department_results": {}
    }
    
    print("🔍 部門別修正済み検証開始")
    print("-" * 60)
    
    for dept in all_departments:
        print(f"\n📋 {dept}部門検証...")
        
        dept_result = verify_department_with_redirects(session, base_url, dept)
        verification_results["department_results"][dept] = dept_result
        
        # 結果表示
        if dept_result["final_status"]["has_simulator_content"]:
            print(f"  ✅ 問題シミュレーター到達: 成功")
        else:
            print(f"  ❌ 問題シミュレーター到達: 失敗")
            
        if dept_result["redirect_chain"]["complete_chain"]:
            print(f"  ✅ リダイレクトチェーン: 完全")
        else:
            print(f"  ❌ リダイレクトチェーン: 不完全")
        
        time.sleep(1)  # サーバー負荷軽減
    
    # 総合評価
    print("\n🔍 総合評価")
    print("-" * 60)
    
    simulator_success = []
    redirect_success = []
    failed_departments = []
    
    for dept, result in verification_results["department_results"].items():
        if result["final_status"]["has_simulator_content"]:
            simulator_success.append(dept)
        if result["redirect_chain"]["complete_chain"]:
            redirect_success.append(dept)
        if not result["final_status"]["access_successful"]:
            failed_departments.append(dept)
    
    overall_assessment = {
        "total_departments": len(all_departments),
        "simulator_success_count": len(simulator_success),
        "redirect_success_count": len(redirect_success),
        "failed_count": len(failed_departments),
        "simulator_success_rate": len(simulator_success) / len(all_departments) * 100,
        "redirect_success_rate": len(redirect_success) / len(all_departments) * 100,
        "system_status": "excellent" if len(simulator_success) == len(all_departments) else 
                        "good" if len(simulator_success) >= 10 else
                        "needs_improvement"
    }
    
    verification_results["overall_assessment"] = overall_assessment
    
    print(f"  📊 シミュレーター到達: {len(simulator_success)}/{len(all_departments)} ({overall_assessment['simulator_success_rate']:.1f}%)")
    print(f"  📊 リダイレクト成功: {len(redirect_success)}/{len(all_departments)} ({overall_assessment['redirect_success_rate']:.1f}%)")
    print(f"  📊 アクセス失敗: {len(failed_departments)}")
    print(f"  🎯 システム状況: {overall_assessment['system_status']}")
    
    if failed_departments:
        print(f"\n  ❌ 失敗部門:")
        for dept in failed_departments:
            print(f"    - {dept}")
    
    # 結果保存
    output_file = f"corrected_question_display_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verification_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果: {output_file}")
    
    if overall_assessment["system_status"] == "excellent":
        print("\n✅ 全部門で問題シミュレーターに正常到達しています")
    else:
        print(f"\n⚠️ {len(all_departments) - len(simulator_success)}部門で改善が必要です")
    
    return verification_results

def verify_department_with_redirects(session, base_url, department):
    """個別部門のリダイレクトチェーン追跡検証"""
    
    result = {
        "department": department,
        "redirect_chain": {
            "start_exam_response": {},
            "exam_question_response": {},
            "exam_simulator_response": {},
            "complete_chain": False
        },
        "final_status": {
            "access_successful": False,
            "has_simulator_content": False,
            "has_question_elements": False
        }
    }
    
    try:
        # Step 1: start_exam 呼び出し
        if department == "基礎科目":
            start_response = session.post(
                f"{base_url}/start_exam/{department}",
                data={"questions": "10"},
                allow_redirects=False,
                timeout=15
            )
        else:
            start_response = session.post(
                f"{base_url}/start_exam/{department}",
                data={"questions": "10", "year": "2016"},
                allow_redirects=False,
                timeout=15
            )
        
        result["redirect_chain"]["start_exam_response"] = {
            "status_code": start_response.status_code,
            "location": start_response.headers.get('Location', ''),
            "has_redirect": start_response.status_code in [301, 302]
        }
        
        # Step 2: exam_question 呼び出し（もしリダイレクトがあれば）
        if start_response.status_code in [301, 302]:
            location = start_response.headers.get('Location', '')
            if location:
                # 相対URLの場合は絶対URLに変換
                if location.startswith('/'):
                    exam_question_url = f"{base_url}{location}"
                else:
                    exam_question_url = location
                
                exam_question_response = session.get(
                    exam_question_url,
                    allow_redirects=False,
                    timeout=15
                )
                
                result["redirect_chain"]["exam_question_response"] = {
                    "status_code": exam_question_response.status_code,
                    "location": exam_question_response.headers.get('Location', ''),
                    "has_redirect": exam_question_response.status_code in [301, 302]
                }
                
                # Step 3: exam_simulator 呼び出し（さらにリダイレクトがあれば）
                if exam_question_response.status_code in [301, 302]:
                    simulator_location = exam_question_response.headers.get('Location', '')
                    if simulator_location:
                        if simulator_location.startswith('/'):
                            simulator_url = f"{base_url}{simulator_location}"
                        else:
                            simulator_url = simulator_location
                        
                        simulator_response = session.get(
                            simulator_url,
                            allow_redirects=True,
                            timeout=15
                        )
                        
                        result["redirect_chain"]["exam_simulator_response"] = {
                            "status_code": simulator_response.status_code,
                            "final_url": simulator_response.url,
                            "content_length": len(simulator_response.text)
                        }
                        
                        # 最終的なコンテンツ分析
                        if simulator_response.status_code == 200:
                            content = simulator_response.text
                            
                            # シミュレーターページの要素確認
                            simulator_indicators = [
                                "試験シミュレーター",
                                "exam_simulator",
                                "実際の試験",
                                "制限時間",
                                "問題数"
                            ]
                            
                            has_simulator = any(indicator in content for indicator in simulator_indicators)
                            
                            # 問題関連要素の確認
                            question_indicators = [
                                "問題",
                                "選択肢", 
                                "次の問題",
                                "前の問題",
                                "結果を見る",
                                "見直し"
                            ]
                            
                            has_questions = any(indicator in content for indicator in question_indicators)
                            
                            result["final_status"] = {
                                "access_successful": True,
                                "has_simulator_content": has_simulator,
                                "has_question_elements": has_questions
                            }
                            
                            # 完全なチェーンかどうか判定
                            result["redirect_chain"]["complete_chain"] = (
                                result["redirect_chain"]["start_exam_response"]["has_redirect"] and
                                result["redirect_chain"]["exam_question_response"]["has_redirect"] and
                                has_simulator
                            )
        
    except Exception as e:
        result["error"] = str(e)
        result["final_status"]["access_successful"] = False
    
    return result

if __name__ == "__main__":
    verify_corrected_question_display()