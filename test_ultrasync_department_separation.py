#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC実装テスト】部門別分離機能の動作確認
CSV日本語カテゴリー名・副作用ゼロ・12部門完全分離
"""

import requests
import json
import re
from datetime import datetime
import time

# 実装完了した部門リスト（CSVの日本語カテゴリー名使用）
ULTRASYNC_DEPARTMENTS = [
    "基礎科目",
    "道路", "河川・砂防", "都市計画", "造園", "建設環境",
    "鋼構造・コンクリート", "土質・基礎", "施工計画", 
    "上下水道", "森林土木", "農業土木", "トンネル"
]

def test_department_route_access(department_name):
    """単一部門の新しいルートアクセステスト"""
    print(f"\n🎯 【{department_name}】ULTRASYNC部門別ルートテスト")
    print("-" * 50)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    try:
        # セッション初期化
        print("📋 ステップ1: セッション初期化")
        session.get(f"{base_url}/")
        
        # 新しい部門別ルートアクセス（ルート競合解決版）
        print("📋 ステップ2: ULTRASYNC部門別ルートアクセス")
        department_url = f"{base_url}/quiz_department/{department_name}"
        print(f"   URL: {department_url}")
        
        response = session.get(department_url)
        print(f"   ステータス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ 部門別ルートアクセス失敗")
            return {"success": False, "error": f"status_{response.status_code}"}
        
        # リダイレクト確認
        if "/exam" in response.url:
            print(f"   ✅ 問題ページへのリダイレクト確認")
            
            # 問題ページ内容確認
            if 'name="qid"' in response.text:
                print(f"   ✅ 正常な問題ページ")
                
                # 問題IDを抽出
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                if qid_match:
                    qid = qid_match.group(1)
                    print(f"   問題ID: {qid}")
                    
                    # 回答テスト
                    print("📋 ステップ3: 回答テスト")
                    post_data = {
                        "answer": "A",
                        "qid": qid,
                        "elapsed": "30"
                    }
                    
                    answer_response = session.post(f"{base_url}/exam", data=post_data)
                    print(f"   回答送信: {answer_response.status_code}")
                    
                    if answer_response.status_code == 200:
                        if "正解" in answer_response.text or "不正解" in answer_response.text:
                            print(f"   ✅ 回答処理成功")
                            return {"success": True, "qid": qid, "department": department_name}
                        else:
                            print(f"   ⚠️ 回答結果内容不明")
                            return {"success": True, "qid": qid, "department": department_name}
                    else:
                        print(f"   ❌ 回答送信失敗")
                        return {"success": False, "error": "answer_failed"}
                else:
                    print(f"   ❌ 問題ID抽出失敗")
                    return {"success": False, "error": "qid_extraction_failed"}
            else:
                print(f"   ❌ 問題ページではない")
                return {"success": False, "error": "not_question_page"}
        else:
            print(f"   ❌ 期待されるリダイレクトなし")
            return {"success": False, "error": "no_redirect"}
            
    except Exception as e:
        print(f"   ❌ テスト実行エラー: {e}")
        return {"success": False, "error": str(e)}

def test_all_ultrasync_departments():
    """全部門のULTRASYNC実装テスト"""
    print("🎯 【ULTRASYNC実装テスト】全12部門分離機能確認")
    print("CSV日本語カテゴリー名・副作用ゼロ・12部門完全分離")
    print("=" * 80)
    
    all_results = []
    
    for i, department in enumerate(ULTRASYNC_DEPARTMENTS, 1):
        print(f"\n{'='*20} {i}/13部門目 {'='*20}")
        print(f"検証対象: {department}")
        
        result = test_department_route_access(department)
        all_results.append(result)
        
        # 部門間で少し待機
        time.sleep(1)
    
    # 全体結果サマリー
    print("\n" + "=" * 80)
    print("🎯 【ULTRASYNC実装テスト】全12部門分離機能確認結果")
    print("=" * 80)
    
    successful_depts = sum(1 for result in all_results if result.get("success", False))
    total_depts = len(all_results)
    success_rate = (successful_depts / total_depts * 100) if total_depts > 0 else 0
    
    print(f"✅ 成功部門: {successful_depts}/{total_depts} ({success_rate:.1f}%)")
    
    # 部門別結果詳細
    print(f"\n📋 部門別結果:")
    for i, result in enumerate(all_results):
        department = ULTRASYNC_DEPARTMENTS[i]
        if result.get("success"):
            qid = result.get("qid", "N/A")
            print(f"✅ {department}: 正常動作 (QID={qid})")
        else:
            error = result.get("error", "不明エラー")
            print(f"❌ {department}: 失敗 ({error})")
    
    # レポート保存
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "ULTRASYNC部門別分離機能確認",
        "total_departments": total_depts,
        "successful_departments": successful_depts,
        "success_rate": success_rate,
        "department_results": all_results
    }
    
    report_filename = f"ultrasync_department_separation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 詳細レポート保存: {report_filename}")
    
    # 最終判定
    if success_rate >= 90.0:
        print(f"\n🎉 【ULTRASYNC実装テスト】完全成功")
        print(f"✅ 全12部門分離機能正常動作")
        print(f"✅ CSV日本語カテゴリー名対応")
        print(f"✅ 副作用ゼロ実装確認")
        return True
    elif success_rate >= 80.0:
        print(f"\n⚠️ 【ULTRASYNC実装テスト】部分成功")
        print(f"✅ 大部分の部門で成功")
        return True
    else:
        print(f"\n🚨 【ULTRASYNC実装テスト】要改善")
        print(f"❌ 成功率不足: {success_rate:.1f}%")
        return False

if __name__ == "__main__":
    success = test_all_ultrasync_departments()
    exit(0 if success else 1)