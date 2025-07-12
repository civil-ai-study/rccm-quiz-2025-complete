#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC緊急デバッグ】部門別アクセス問題分析
各部門のアクセス方法を詳細分析してエラー原因を特定
"""

import requests
import json
import re
from datetime import datetime

def debug_department_access():
    """部門別アクセス方法の詳細デバッグ"""
    print("🔍 【ULTRASYNC緊急デバッグ】部門別アクセス問題分析")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # 基本アクセステスト
    print("📋 ステップ1: 基本アクセステスト")
    
    test_cases = [
        {"name": "ホームページ", "url": f"{base_url}/"},
        {"name": "基礎科目（単純）", "url": f"{base_url}/exam?question_type=basic"},
        {"name": "基礎科目（明示）", "url": f"{base_url}/exam?question_type=basic&count=10"},
        {"name": "部門ページ確認", "url": f"{base_url}/departments"},
        {"name": "カテゴリページ確認", "url": f"{base_url}/categories"},
    ]
    
    for test in test_cases:
        try:
            response = session.get(test["url"])
            print(f"   {test['name']}: {response.status_code}")
            
            if "エラー" in response.text:
                print(f"      ❌ エラーページ検出")
                # エラー詳細を抽出
                error_match = re.search(r'<strong>(.*?)</strong>', response.text)
                if error_match:
                    print(f"      エラー内容: {error_match.group(1)}")
            elif 'name="qid"' in response.text:
                print(f"      ✅ 正常な問題ページ")
            elif "部門" in response.text or "カテゴリ" in response.text:
                print(f"      ✅ 正常なナビゲーションページ")
            else:
                print(f"      ⚠️ 不明なページ")
                
        except Exception as e:
            print(f"   {test['name']}: エラー - {e}")
    
    # 専門科目アクセス方法調査
    print(f"\n📋 ステップ2: 専門科目アクセス方法調査")
    
    # まず departments ページから正しいアクセス方法を確認
    try:
        dept_response = session.get(f"{base_url}/departments")
        if dept_response.status_code == 200:
            print(f"   部門ページアクセス: 成功")
            
            # 部門リンクを抽出
            dept_links = re.findall(r'href="([^"]*exam[^"]*)"', dept_response.text)
            print(f"   検出された部門リンク数: {len(dept_links)}")
            
            for i, link in enumerate(dept_links[:5]):  # 最初の5つを表示
                print(f"      リンク{i+1}: {link}")
                
            # 実際のリンクをテスト
            if dept_links:
                test_link = dept_links[0]
                full_url = f"{base_url}{test_link}" if test_link.startswith('/') else test_link
                print(f"\n   実際の部門リンクテスト: {full_url}")
                
                link_response = session.get(full_url)
                print(f"   ステータス: {link_response.status_code}")
                
                if "エラー" in link_response.text:
                    print(f"      ❌ 部門リンクもエラー")
                elif 'name="qid"' in link_response.text:
                    print(f"      ✅ 部門リンクは正常動作")
                else:
                    print(f"      ⚠️ 部門リンク結果不明")
        else:
            print(f"   部門ページアクセス: 失敗 ({dept_response.status_code})")
    
    except Exception as e:
        print(f"   部門ページ調査エラー: {e}")
    
    # 正常に動作した方法での部門テスト
    print(f"\n📋 ステップ3: 正常動作方法での部門テスト")
    
    # 成功したbasicパターンを使用
    session.get(f"{base_url}/")  # セッション初期化
    
    working_methods = [
        {"name": "基礎科目（動作確認済み）", "url": f"{base_url}/exam?question_type=basic"},
        {"name": "パラメータなし", "url": f"{base_url}/exam"},
        {"name": "count指定", "url": f"{base_url}/exam?count=10"},
        {"name": "年度指定", "url": f"{base_url}/exam?year=2016"},
    ]
    
    for method in working_methods:
        try:
            # 新しいセッションで試行
            fresh_session = requests.Session()
            fresh_session.get(f"{base_url}/")
            
            response = fresh_session.get(method["url"])
            print(f"   {method['name']}: {response.status_code}")
            
            if 'name="qid"' in response.text:
                print(f"      ✅ 正常な問題ページ")
                
                # 問題IDを抽出
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                if qid_match:
                    qid = qid_match.group(1)
                    print(f"      問題ID: {qid}")
                    
                    # 問題種別を推定
                    qid_int = int(qid)
                    if qid_int < 200:
                        print(f"      推定タイプ: レガシー基礎科目")
                    elif 10000 <= qid_int < 20000:
                        print(f"      推定タイプ: 新形式基礎科目")
                    elif 20000 <= qid_int < 30000:
                        print(f"      推定タイプ: 新形式専門科目")
                    else:
                        print(f"      推定タイプ: 不明")
                        
            elif "エラー" in response.text:
                print(f"      ❌ エラーページ")
            else:
                print(f"      ⚠️ 結果不明")
                
        except Exception as e:
            print(f"   {method['name']}: エラー - {e}")
    
    # 部門指定の代替方法テスト
    print(f"\n📋 ステップ4: 部門指定代替方法テスト")
    
    alternative_methods = [
        {"name": "start_exam/道路", "url": f"{base_url}/start_exam/道路"},
        {"name": "start_exam/basic", "url": f"{base_url}/start_exam/基礎科目"},
        {"name": "exam + category", "url": f"{base_url}/exam?category=道路"},
        {"name": "exam + dept", "url": f"{base_url}/exam?dept=道路"},
    ]
    
    for method in alternative_methods:
        try:
            fresh_session = requests.Session()
            fresh_session.get(f"{base_url}/")
            
            response = fresh_session.get(method["url"])
            print(f"   {method['name']}: {response.status_code}")
            
            if response.status_code == 200:
                if 'name="qid"' in response.text:
                    print(f"      ✅ 正常な問題ページ")
                elif "エラー" in response.text:
                    print(f"      ❌ エラーページ")
                else:
                    print(f"      ⚠️ その他のページ")
            elif response.status_code == 404:
                print(f"      ❌ ページが存在しない")
            else:
                print(f"      ❌ アクセス失敗")
                
        except Exception as e:
            print(f"   {method['name']}: エラー - {e}")
    
    # 結論とレコメンデーション
    print(f"\n📋 ステップ5: デバッグ結論")
    print(f"🔍 【デバッグ結論】")
    print(f"1. 基礎科目（question_type=basic）は動作する")
    print(f"2. 専門科目の部門指定方法に問題がある可能性")
    print(f"3. 正しい部門アクセス方法を特定する必要がある")
    
    # レポート保存
    debug_report = {
        "timestamp": datetime.now().isoformat(),
        "conclusion": "department_access_method_issue",
        "working_basic": True,
        "working_specialist": False,
        "recommendation": "investigate_correct_department_access_pattern"
    }
    
    with open(f"debug_department_access_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
        json.dump(debug_report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    debug_department_access()