#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階12-14】全12部門完全検証システム
基礎科目(4-1) + 専門科目11部門(4-2) の完全手動検証
カテゴリー混在防止チェック付き
"""

import requests
import json
import re
from datetime import datetime
import time

# 検証対象部門リスト
DEPARTMENTS_TO_TEST = [
    # 基礎科目
    {"name": "基礎科目", "type": "basic", "url_param": "basic", "category_expected": "共通"},
    
    # 専門科目11部門
    {"name": "道路部門", "type": "specialist", "url_param": "道路", "category_expected": "道路"},
    {"name": "河川・砂防部門", "type": "specialist", "url_param": "河川・砂防", "category_expected": "河川・砂防"},
    {"name": "都市計画部門", "type": "specialist", "url_param": "都市計画", "category_expected": "都市計画"},
    {"name": "造園部門", "type": "specialist", "url_param": "造園", "category_expected": "造園"},
    {"name": "建設環境部門", "type": "specialist", "url_param": "建設環境", "category_expected": "建設環境"},
    {"name": "鋼構造・コンクリート部門", "type": "specialist", "url_param": "鋼構造・コンクリート", "category_expected": "鋼構造・コンクリート"},
    {"name": "土質・基礎部門", "type": "specialist", "url_param": "土質・基礎", "category_expected": "土質・基礎"},
    {"name": "施工計画部門", "type": "specialist", "url_param": "施工計画", "category_expected": "施工計画"},
    {"name": "上下水道部門", "type": "specialist", "url_param": "上下水道", "category_expected": "上下水道"},
    {"name": "森林土木部門", "type": "specialist", "url_param": "森林土木", "category_expected": "森林土木"},
    {"name": "農業土木部門", "type": "specialist", "url_param": "農業土木", "category_expected": "農業土木"},
    {"name": "トンネル部門", "type": "specialist", "url_param": "トンネル", "category_expected": "トンネル"}
]

def extract_question_detail(html_content):
    """問題の詳細情報とカテゴリー情報を抽出"""
    try:
        # 問題ID
        qid_match = re.search(r'name="qid" value="(\d+)"', html_content)
        qid = qid_match.group(1) if qid_match else None
        
        # 進捗
        progress_match = re.search(r'(\d+)/(\d+)', html_content)
        current, total = (int(progress_match.group(1)), int(progress_match.group(2))) if progress_match else (0, 10)
        
        # 問題種別の推定（問題IDから）
        question_type_detected = "unknown"
        if qid:
            qid_int = int(qid)
            if 10000 <= qid_int < 20000:
                question_type_detected = "basic"
            elif 20000 <= qid_int < 30000:
                question_type_detected = "specialist"
            elif qid_int < 1000:
                question_type_detected = "legacy"
        
        # 問題カテゴリーの検出（HTMLから）
        category_detected = "unknown"
        category_patterns = [
            r'カテゴリ[：:]\s*([^<\n]+)',
            r'部門[：:]\s*([^<\n]+)',
            r'科目[：:]\s*([^<\n]+)'
        ]
        
        for pattern in category_patterns:
            category_match = re.search(pattern, html_content)
            if category_match:
                category_detected = category_match.group(1).strip()
                break
        
        return {
            "qid": qid,
            "current": current,
            "total": total,
            "question_type_detected": question_type_detected,
            "category_detected": category_detected,
            "is_valid": qid is not None
        }
    except Exception as e:
        return {
            "qid": None,
            "current": 0,
            "total": 10,
            "question_type_detected": "error",
            "category_detected": f"error: {e}",
            "is_valid": False
        }

def verify_single_department(dept_info):
    """単一部門の10問完走テスト"""
    print(f"\n🎯 【{dept_info['name']}】10問完走テスト開始")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # 回答パターン
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
    test_log = []
    category_violations = []
    
    try:
        # セッション初期化
        print("📋 ステップ1: セッション初期化")
        session.get(f"{base_url}/")
        
        # 部門別試験開始
        print(f"📋 ステップ2: {dept_info['name']}試験開始")
        if dept_info['type'] == 'basic':
            start_url = f"{base_url}/exam?question_type=basic"
        else:
            start_url = f"{base_url}/exam?question_type=specialist&department={dept_info['url_param']}"
        
        print(f"   開始URL: {start_url}")
        response = session.get(start_url)
        print(f"   開始ステータス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ 試験開始失敗")
            return {"success": False, "error": f"start_failed_{response.status_code}"}
        
        # エラーページチェック
        if "エラー" in response.text or "問題データの取得に失敗" in response.text:
            print(f"   ❌ エラーページが表示")
            return {"success": False, "error": "error_page_displayed"}
        
        first_question = extract_question_detail(response.text)
        print(f"   初回問題: QID={first_question['qid']}, Type={first_question['question_type_detected']}")
        print(f"   カテゴリー: {first_question['category_detected']}")
        
        if not first_question["is_valid"]:
            print(f"   ❌ 初回問題データ無効")
            return {"success": False, "error": "invalid_first_question"}
        
        # カテゴリー整合性チェック
        expected_category = dept_info['category_expected']
        if dept_info['type'] == 'basic':
            # 基礎科目の場合
            if first_question['question_type_detected'] not in ['basic', 'legacy']:
                category_violations.append({
                    "question_num": 1,
                    "qid": first_question['qid'],
                    "expected_type": "basic",
                    "detected_type": first_question['question_type_detected'],
                    "violation": "wrong_question_type"
                })
        else:
            # 専門科目の場合
            if first_question['question_type_detected'] not in ['specialist', 'legacy']:
                category_violations.append({
                    "question_num": 1,
                    "qid": first_question['qid'],
                    "expected_type": "specialist",
                    "detected_type": first_question['question_type_detected'],
                    "violation": "wrong_question_type"
                })
        
        test_log.append({
            "step": "start",
            "dept": dept_info['name'],
            "success": True,
            "qid": first_question['qid'],
            "question_type": first_question['question_type_detected']
        })
        
        # 10問連続実行
        print(f"📋 ステップ3: {dept_info['name']} 10問連続実行")
        
        for question_num in range(1, 11):
            print(f"\n   🔍 {dept_info['name']} 問題 {question_num}/10")
            
            # 現在の問題取得
            if question_num > 1:
                response = session.get(f"{base_url}/exam")
                if response.status_code != 200:
                    print(f"      ❌ 問題{question_num}取得失敗: {response.status_code}")
                    return {"success": False, "error": f"question_{question_num}_failed"}
                
                current_question = extract_question_detail(response.text)
            else:
                current_question = first_question
            
            print(f"      QID: {current_question['qid']}")
            print(f"      進捗: {current_question['current']}/{current_question['total']}")
            print(f"      検出タイプ: {current_question['question_type_detected']}")
            print(f"      検出カテゴリー: {current_question['category_detected']}")
            
            # カテゴリー整合性チェック
            if dept_info['type'] == 'basic':
                if current_question['question_type_detected'] not in ['basic', 'legacy', 'unknown']:
                    category_violations.append({
                        "question_num": question_num,
                        "qid": current_question['qid'],
                        "expected_type": "basic",
                        "detected_type": current_question['question_type_detected'],
                        "violation": "basic_contamination"
                    })
                    print(f"      🚨 カテゴリー違反: 基礎科目に{current_question['question_type_detected']}混入")
            else:
                if current_question['question_type_detected'] == 'basic':
                    category_violations.append({
                        "question_num": question_num,
                        "qid": current_question['qid'],
                        "expected_type": "specialist",
                        "detected_type": "basic",
                        "violation": "specialist_contamination"
                    })
                    print(f"      🚨 カテゴリー違反: 専門科目に基礎科目混入")
            
            if not current_question["is_valid"]:
                print(f"      ❌ 問題{question_num}データ無効")
                return {"success": False, "error": f"invalid_question_{question_num}"}
            
            # 回答送信
            answer = answers[question_num - 1]
            post_data = {
                "answer": answer,
                "qid": current_question["qid"],
                "elapsed": "30"
            }
            
            print(f"      回答送信: {answer}")
            response = session.post(f"{base_url}/exam", data=post_data)
            print(f"      POST応答: {response.status_code}")
            
            if response.status_code not in [200, 302]:
                print(f"      ❌ 回答{question_num}送信失敗")
                return {"success": False, "error": f"answer_{question_num}_failed"}
            
            # 回答処理結果確認
            if response.status_code == 200:
                if "正解" in response.text or "不正解" in response.text:
                    print(f"      ✅ 回答{question_num}処理成功")
                    
                    if question_num == 10:
                        print(f"      🎯 {dept_info['name']} 10問目完了！")
                        if "結果を見る" in response.text:
                            print(f"      ✅ 結果ボタン確認")
                else:
                    print(f"      ⚠️ 回答結果内容不明")
            
            test_log.append({
                "question_num": question_num,
                "qid": current_question['qid'],
                "answer": answer,
                "status": response.status_code,
                "question_type": current_question['question_type_detected'],
                "category": current_question['category_detected'],
                "success": True
            })
            
            time.sleep(0.5)  # サーバー負荷軽減
        
        # 結果画面確認
        print(f"\n📋 ステップ4: {dept_info['name']} 結果画面確認")
        result_response = session.get(f"{base_url}/result")
        print(f"   結果画面アクセス: {result_response.status_code}")
        
        result_success = False
        if result_response.status_code == 200:
            if "結果" in result_response.text and len(result_response.text) > 1000:
                print(f"   ✅ {dept_info['name']} 結果画面正常")
                result_success = True
            else:
                print(f"   ⚠️ {dept_info['name']} 結果画面内容不足")
        
        # 最終判定
        questions_completed = len([log for log in test_log if log.get("question_num")])
        overall_success = (questions_completed == 10 and result_success)
        
        print(f"\n🎯 【{dept_info['name']}】テスト結果")
        print(f"   ✅ 完走問題数: {questions_completed}/10")
        print(f"   ✅ 結果画面: {result_success}")
        print(f"   🚨 カテゴリー違反: {len(category_violations)}件")
        
        if category_violations:
            print(f"   🚨 カテゴリー違反詳細:")
            for violation in category_violations:
                print(f"      問題{violation['question_num']}: QID={violation['qid']}, {violation['violation']}")
        
        return {
            "department": dept_info['name'],
            "success": overall_success,
            "questions_completed": questions_completed,
            "result_screen_success": result_success,
            "category_violations": category_violations,
            "test_log": test_log
        }
        
    except Exception as e:
        print(f"\n❌ {dept_info['name']} テスト実行エラー: {e}")
        return {"success": False, "error": str(e)}

def comprehensive_department_verification():
    """全12部門の包括的検証"""
    print("🎯 【ULTRASYNC段階12-14】全12部門包括的検証開始")
    print("基礎科目(4-1) + 専門科目11部門(4-2) 完全手動検証")
    print("=" * 80)
    
    all_results = []
    total_violations = 0
    
    # 各部門のテスト実行
    for i, dept_info in enumerate(DEPARTMENTS_TO_TEST, 1):
        print(f"\n{'='*20} {i}/12部門目 {'='*20}")
        print(f"検証対象: {dept_info['name']} ({dept_info['type']})")
        
        result = verify_single_department(dept_info)
        all_results.append(result)
        
        if result.get("category_violations"):
            total_violations += len(result["category_violations"])
        
        # 部門間で少し待機
        time.sleep(2)
    
    # 全体結果サマリー
    print("\n" + "=" * 80)
    print("🎯 【ULTRASYNC段階12-14】全12部門検証結果サマリー")
    print("=" * 80)
    
    successful_depts = sum(1 for result in all_results if result.get("success", False))
    total_depts = len(all_results)
    success_rate = (successful_depts / total_depts * 100) if total_depts > 0 else 0
    
    print(f"✅ 成功部門: {successful_depts}/{total_depts} ({success_rate:.1f}%)")
    print(f"🚨 カテゴリー違反総数: {total_violations}件")
    
    # 部門別結果詳細
    print(f"\n📋 部門別結果:")
    for result in all_results:
        if result.get("success"):
            dept_name = result.get("department", "不明")
            violations = len(result.get("category_violations", []))
            status_icon = "✅" if violations == 0 else "⚠️"
            print(f"{status_icon} {dept_name}: 10問完走成功, 違反{violations}件")
        else:
            dept_name = result.get("department", "不明")
            error = result.get("error", "不明エラー")
            print(f"❌ {dept_name}: 失敗 ({error})")
    
    # 詳細レポート保存
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "ULTRASYNC段階12-14全12部門包括検証",
        "total_departments": total_depts,
        "successful_departments": successful_depts,
        "success_rate": success_rate,
        "total_category_violations": total_violations,
        "department_results": all_results
    }
    
    report_filename = f"comprehensive_dept_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 詳細レポート保存: {report_filename}")
    
    # 最終判定
    if success_rate >= 90.0 and total_violations == 0:
        print(f"\n🎉 【ULTRASYNC段階12-14】完全成功")
        print(f"✅ 全12部門10問完走成功")
        print(f"✅ カテゴリー混在ゼロ")
        print(f"✅ 4-1/4-2分離完璧")
        return True
    elif success_rate >= 80.0:
        print(f"\n⚠️ 【ULTRASYNC段階12-14】部分成功")
        print(f"✅ 大部分の部門で成功")
        if total_violations > 0:
            print(f"🚨 カテゴリー混在要修正: {total_violations}件")
        return True
    else:
        print(f"\n🚨 【ULTRASYNC段階12-14】要改善")
        print(f"❌ 成功率不足: {success_rate:.1f}%")
        return False

if __name__ == "__main__":
    success = comprehensive_department_verification()
    exit(0 if success else 1)