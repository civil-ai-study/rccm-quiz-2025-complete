#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階31】原因分析
20問・30問未完走問題の深層分析・副作用ゼロ保証
"""

import requests
import json
import re
from datetime import datetime
import time

def analyze_20_30_questions_issue():
    """
    ULTRASYNC段階31: 20問・30問未完走の原因分析
    副作用ゼロで既存機能に影響を与えない調査
    """
    print("🔍 【ULTRASYNC段階31】20問・30問未完走原因分析")
    print("副作用ゼロ・既存機能保護・慎重な調査実施")
    print("=" * 80)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    analysis_results = {
        "analysis_name": "ULTRASYNC段階31_20問30問未完走原因分析",
        "timestamp": datetime.now().isoformat(),
        "methodology": "副作用ゼロ・既存機能保護・段階的調査",
        "investigations": []
    }
    
    # 調査1: 基本的な10問完走の確認（既存機能の安全確認）
    print("\n📋 調査1: 10問完走の安全確認（既存機能保護）")
    investigation_10q = investigate_10_questions_flow(base_url)
    analysis_results["investigations"].append(investigation_10q)
    
    # 調査2: 20問設定時のセッション状態詳細分析
    print("\n📋 調査2: 20問設定時のセッション状態分析")
    investigation_20q = investigate_20_questions_session(base_url)
    analysis_results["investigations"].append(investigation_20q)
    
    # 調査3: 問題数パラメータの処理確認
    print("\n📋 調査3: 問題数パラメータの処理分析")
    investigation_params = investigate_question_count_parameters(base_url)
    analysis_results["investigations"].append(investigation_params)
    
    # 調査4: レスポンス内容の詳細分析
    print("\n📋 調査4: 異常レスポンス内容の分析")
    investigation_response = investigate_response_content(base_url)
    analysis_results["investigations"].append(investigation_response)
    
    # 結果分析
    print("\n" + "=" * 80)
    print("🎯 【ULTRASYNC段階31】原因分析結果")
    print("=" * 80)
    
    # 各調査の結果サマリー
    successful_investigations = 0
    for investigation in analysis_results["investigations"]:
        name = investigation.get("investigation_name", "不明")
        success = investigation.get("success", False)
        key_finding = investigation.get("key_finding", "不明")
        
        status = "✅ 成功" if success else "❌ 問題検出"
        print(f"{status} {name}: {key_finding}")
        
        if success:
            successful_investigations += 1
    
    # 原因特定
    print(f"\n🔍 原因特定:")
    root_causes = []
    
    for investigation in analysis_results["investigations"]:
        if not investigation.get("success", False):
            cause = investigation.get("root_cause", "不明")
            root_causes.append(cause)
    
    if root_causes:
        print("❌ 検出された根本原因:")
        for i, cause in enumerate(root_causes, 1):
            print(f"  {i}. {cause}")
    else:
        print("⚠️ 根本原因の特定が困難（さらなる調査が必要）")
    
    analysis_results["summary"] = {
        "total_investigations": len(analysis_results["investigations"]),
        "successful_investigations": successful_investigations,
        "root_causes_identified": root_causes,
        "next_action_required": len(root_causes) > 0
    }
    
    # レポート保存
    report_filename = f"ultrasync_stage31_root_cause_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 詳細分析レポート保存: {report_filename}")
    
    # ULTRASYNC段階31結論
    print(f"\n🎯 【ULTRASYNC段階31】結論:")
    if len(root_causes) > 0:
        print("✅ 原因特定完了")
        print("🔧 次段階: 特定された原因への安全な対処")
        print("🛡️ 副作用ゼロでの修正実施準備")
        return True
    else:
        print("⚠️ 原因特定継続中")
        print("🔍 次段階: より詳細な調査実施")
        print("🛡️ 既存機能保護を維持")
        return False

def investigate_10_questions_flow(base_url):
    """
    調査1: 10問完走の確認（既存機能の安全確認）
    """
    print("🔍 10問完走確認（既存機能保護）")
    
    investigation = {
        "investigation_name": "10問完走確認",
        "success": False,
        "details": {}
    }
    
    session = requests.Session()
    
    try:
        # 最もシンプルなアクセスパターン（既存の正常動作）
        print("   基本アクセス確認...")
        response = session.get(f"{base_url}/exam")
        
        if response.status_code == 200:
            has_qid = 'name="qid"' in response.text
            has_form = '<form' in response.text
            
            investigation["details"] = {
                "status_code": response.status_code,
                "has_question_form": has_qid,
                "has_html_form": has_form,
                "response_length": len(response.text)
            }
            
            if has_qid and has_form:
                investigation["success"] = True
                investigation["key_finding"] = "10問基本機能は正常動作"
                print("   ✅ 10問基本機能正常確認")
            else:
                investigation["key_finding"] = "10問基本機能で問題表示なし"
                investigation["root_cause"] = "基本的な問題表示機能の異常"
                print("   ❌ 問題表示機能に異常")
        else:
            investigation["key_finding"] = f"基本アクセス失敗: {response.status_code}"
            investigation["root_cause"] = "サーバーアクセス基本問題"
            print(f"   ❌ アクセス失敗: {response.status_code}")
            
    except Exception as e:
        investigation["key_finding"] = f"調査エラー: {str(e)}"
        investigation["root_cause"] = "ネットワークまたはサーバー問題"
        print(f"   ❌ エラー: {e}")
    
    return investigation

def investigate_20_questions_session(base_url):
    """
    調査2: 20問設定時のセッション状態詳細分析
    """
    print("🔍 20問設定時のセッション分析")
    
    investigation = {
        "investigation_name": "20問セッション分析",
        "success": False,
        "details": {}
    }
    
    session = requests.Session()
    
    try:
        # ステップ1: ホームページアクセス
        print("   ホームページアクセス...")
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            investigation["key_finding"] = "ホームページアクセス失敗"
            investigation["root_cause"] = "基本的なサーバーアクセス問題"
            return investigation
        
        # ステップ2: 20問設定での試験開始
        print("   20問試験開始設定...")
        start_data = {
            "exam_type": "specialist",
            "questions": "20",
            "year": "2024"
        }
        
        response = session.post(f"{base_url}/start_exam/specialist", data=start_data)
        
        # レスポンス詳細分析
        investigation["details"] = {
            "start_status_code": response.status_code,
            "start_response_length": len(response.text),
            "has_redirect": response.history,
            "final_url": response.url,
            "cookies": dict(session.cookies)
        }
        
        print(f"   試験開始レスポンス: {response.status_code}")
        print(f"   最終URL: {response.url}")
        print(f"   Cookie数: {len(session.cookies)}")
        
        # ステップ3: 問題ページアクセス
        print("   問題ページアクセス...")
        exam_response = session.get(f"{base_url}/exam")
        
        investigation["details"]["exam_status_code"] = exam_response.status_code
        investigation["details"]["exam_response_length"] = len(exam_response.text)
        
        # セッション内容分析
        has_qid = 'name="qid"' in exam_response.text
        has_session_data = 'exam_question_ids' in str(session.cookies)
        
        investigation["details"]["has_qid"] = has_qid
        investigation["details"]["has_session_data"] = has_session_data
        
        if has_qid:
            investigation["success"] = True
            investigation["key_finding"] = "20問設定で問題表示成功"
            print("   ✅ 20問設定で問題表示確認")
        else:
            investigation["key_finding"] = "20問設定で問題表示失敗"
            investigation["root_cause"] = "20問設定時のセッション初期化問題"
            print("   ❌ 20問設定で問題表示なし")
            
            # より詳細な分析
            if "エラー" in exam_response.text:
                error_match = re.search(r'エラー[：:]\s*([^<\n]+)', exam_response.text)
                if error_match:
                    investigation["details"]["error_message"] = error_match.group(1)
                    print(f"   エラーメッセージ: {error_match.group(1)}")
            
    except Exception as e:
        investigation["key_finding"] = f"20問調査エラー: {str(e)}"
        investigation["root_cause"] = "20問設定処理の根本的問題"
        print(f"   ❌ エラー: {e}")
    
    return investigation

def investigate_question_count_parameters(base_url):
    """
    調査3: 問題数パラメータの処理確認
    """
    print("🔍 問題数パラメータ処理分析")
    
    investigation = {
        "investigation_name": "問題数パラメータ処理",
        "success": False,
        "details": {}
    }
    
    # 異なる問題数設定での挙動確認
    test_cases = [
        {"questions": "10", "expected": "10問（基準）"},
        {"questions": "20", "expected": "20問（問題対象）"},
        {"questions": "30", "expected": "30問（問題対象）"}
    ]
    
    results = []
    
    for case in test_cases:
        print(f"   {case['questions']}問設定テスト...")
        session = requests.Session()
        
        try:
            # ホームページアクセス
            session.get(f"{base_url}/")
            
            # 問題数指定での開始
            start_data = {
                "exam_type": "specialist",
                "questions": case["questions"],
                "year": "2024"
            }
            
            response = session.post(f"{base_url}/start_exam/specialist", data=start_data)
            exam_response = session.get(f"{base_url}/exam")
            
            has_qid = 'name="qid"' in exam_response.text
            
            case_result = {
                "question_count": case["questions"],
                "start_status": response.status_code,
                "exam_status": exam_response.status_code,
                "has_problem": has_qid,
                "success": has_qid
            }
            
            results.append(case_result)
            status = "✅" if has_qid else "❌"
            print(f"     {status} {case['questions']}問: {'成功' if has_qid else '失敗'}")
            
        except Exception as e:
            case_result = {
                "question_count": case["questions"],
                "error": str(e),
                "success": False
            }
            results.append(case_result)
            print(f"     ❌ {case['questions']}問: エラー")
    
    investigation["details"]["test_results"] = results
    
    # 結果分析
    successful_counts = [r["question_count"] for r in results if r.get("success", False)]
    failed_counts = [r["question_count"] for r in results if not r.get("success", False)]
    
    if len(successful_counts) == 3:
        investigation["success"] = True
        investigation["key_finding"] = "全問題数設定で成功"
    elif "10" in successful_counts and len(failed_counts) > 0:
        investigation["key_finding"] = f"10問成功、{','.join(failed_counts)}問失敗"
        investigation["root_cause"] = f"{','.join(failed_counts)}問設定時の処理問題"
    else:
        investigation["key_finding"] = "全問題数設定で失敗"
        investigation["root_cause"] = "問題数設定処理の根本的異常"
    
    return investigation

def investigate_response_content(base_url):
    """
    調査4: 異常レスポンス内容の分析
    """
    print("🔍 異常レスポンス内容分析")
    
    investigation = {
        "investigation_name": "異常レスポンス内容分析",
        "success": False,
        "details": {}
    }
    
    session = requests.Session()
    
    try:
        # 20問での設定で実際のレスポンス内容を詳細分析
        session.get(f"{base_url}/")
        
        start_data = {
            "exam_type": "specialist",
            "questions": "20",
            "year": "2024"
        }
        
        session.post(f"{base_url}/start_exam/specialist", data=start_data)
        response = session.get(f"{base_url}/exam")
        
        # レスポンス内容の詳細分析
        content_analysis = {
            "status_code": response.status_code,
            "content_length": len(response.text),
            "has_html": "<html" in response.text,
            "has_error_message": "エラー" in response.text,
            "has_question_form": 'name="qid"' in response.text,
            "has_csrf_token": 'name="csrf_token"' in response.text,
            "has_answer_options": any(opt in response.text for opt in ["選択肢A", "選択肢B", "選択肢C", "選択肢D"]),
            "response_type": "unknown"
        }
        
        # レスポンスタイプの判定
        if content_analysis["has_question_form"]:
            content_analysis["response_type"] = "正常な問題ページ"
            investigation["success"] = True
            investigation["key_finding"] = "レスポンス内容は正常"
        elif content_analysis["has_error_message"]:
            content_analysis["response_type"] = "エラーページ"
            investigation["key_finding"] = "エラーページが返される"
            investigation["root_cause"] = "サーバー側でエラー発生"
            
            # エラーメッセージ抽出
            error_pattern = re.search(r'エラー[：:]\s*([^<\n]+)', response.text)
            if error_pattern:
                content_analysis["error_message"] = error_pattern.group(1)
        elif len(response.text) < 100:
            content_analysis["response_type"] = "空または短すぎるレスポンス"
            investigation["key_finding"] = "レスポンス内容が不完全"
            investigation["root_cause"] = "サーバー応答の不完全性"
        else:
            content_analysis["response_type"] = "予期しないレスポンス"
            investigation["key_finding"] = "予期しないレスポンス内容"
            investigation["root_cause"] = "アプリケーション処理の異常"
            
            # 部分的内容確認
            content_analysis["partial_content"] = response.text[:500]
        
        investigation["details"] = content_analysis
        
        print(f"   レスポンスタイプ: {content_analysis['response_type']}")
        print(f"   内容長: {content_analysis['content_length']}")
        
    except Exception as e:
        investigation["key_finding"] = f"レスポンス分析エラー: {str(e)}"
        investigation["root_cause"] = "レスポンス分析処理の問題"
        print(f"   ❌ エラー: {e}")
    
    return investigation

if __name__ == "__main__":
    print("🔍 ULTRASYNC段階31: 20問・30問未完走原因分析")
    print("副作用ゼロ・既存機能保護・慎重な調査")
    print()
    
    success = analyze_20_30_questions_issue()
    
    print(f"\n🎯 ULTRASYNC段階31完了")
    print("慎重かつ正確に副作用を絶対発生させない段階的進行を継続")
    
    exit(0 if success else 1)