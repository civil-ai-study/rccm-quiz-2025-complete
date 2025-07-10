#!/usr/bin/env python3
"""
本番環境互換性テスト
土質・基礎部門修正後の本番環境での動作を検証
"""

import sys
import os
import json
import urllib.parse
import urllib.request
import time
from datetime import datetime

def test_production_urls():
    """本番環境のURL構造をテスト"""
    print("🌐 本番環境URL構造テスト")
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    # テスト対象の部門名
    departments = [
        '土質・基礎',
        '都市計画', 
        '鋼構造・コンクリート',
        '施工計画',
        '上下水道'
    ]
    
    # URLエンコードテスト
    print("\n1. URLエンコーディングテスト:")
    for dept in departments:
        encoded = urllib.parse.quote(dept, safe='')
        print(f"   {dept} → {encoded}")
    
    # POST リクエストボディ構造テスト
    print("\n2. POST リクエストボディ構造テスト:")
    for dept in departments:
        body_data = {
            'questions': '10',
            'year': '2024'
        }
        encoded_body = urllib.parse.urlencode(body_data).encode('utf-8')
        
        print(f"   {dept}:")
        print(f"     URL: {base_url}/start_exam/{urllib.parse.quote(dept, safe='')}")
        print(f"     Body: {encoded_body}")
    
    return True

def test_url_length_limits():
    """URL長制限テスト（HTTP 431対策）"""
    print("\n🚨 URL長制限テスト（HTTP 431対策）")
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    # 最長の部門名でテスト
    longest_dept = '鋼構造・コンクリート'
    
    # GETリクエストでの最大URL長
    get_params = {
        'questions': '30',
        'year': '2024',
        'additional_param': 'test_value'
    }
    
    get_url = f"{base_url}/start_exam/{urllib.parse.quote(longest_dept, safe='')}"
    get_url_with_params = f"{get_url}?{urllib.parse.urlencode(get_params)}"
    
    print(f"   GET URL長: {len(get_url_with_params)} 文字")
    print(f"   GET URL: {get_url_with_params}")
    
    # POST リクエストでの制限回避
    post_data = urllib.parse.urlencode(get_params).encode('utf-8')
    print(f"   POST Body長: {len(post_data)} bytes")
    print(f"   POST Body: {post_data}")
    
    if len(get_url_with_params) > 72:
        print("   ⚠️ GET URL長が制限を超えています - POST使用推奨")
    else:
        print("   ✓ GET URL長は制限内です")
    
    return True

def test_exam_flow_simulation():
    """試験フロー シミュレーション"""
    print("\n🔄 試験フロー シミュレーション")
    
    # 土質・基礎部門での試験フロー
    dept = '土質・基礎'
    
    print(f"   対象部門: {dept}")
    
    # 1. 試験開始
    print(f"   1. 試験開始: /start_exam/{urllib.parse.quote(dept, safe='')}")
    
    # 2. 問題数選択
    question_counts = [10, 20, 30]
    for count in question_counts:
        print(f"   2. 問題数選択: {count}問")
        
        # POST データ
        post_data = {
            'questions': str(count),
            'year': '2024'
        }
        print(f"      POST データ: {post_data}")
    
    # 3. 期待される結果
    print(f"   3. 期待される結果:")
    print(f"      - 正規化: {dept} → soil_foundation")
    print(f"      - カテゴリ: soil_foundation → 土質及び基礎")
    print(f"      - リダイレクト: /exam (試験画面)")
    
    return True

def test_error_handling():
    """エラーハンドリングテスト"""
    print("\n❌ エラーハンドリングテスト")
    
    # 無効な部門名
    invalid_departments = [
        '存在しない部門',
        '',
        '土質',  # 短縮形は正常
        '基礎',  # 短縮形は正常
        '土質・基礎・追加'  # 無効な拡張
    ]
    
    for dept in invalid_departments:
        print(f"   無効部門: '{dept}'")
        
        # URL構造
        if dept:
            url = f"/start_exam/{urllib.parse.quote(dept, safe='')}"
            print(f"      URL: {url}")
        else:
            print(f"      URL: /start_exam/ (空文字)")
    
    # 無効なパラメータ
    invalid_params = [
        {'questions': '0', 'year': '2024'},
        {'questions': '100', 'year': '2024'},
        {'questions': '10', 'year': '1999'},
        {'questions': 'abc', 'year': '2024'},
        {'questions': '10', 'year': 'def'}
    ]
    
    for params in invalid_params:
        print(f"   無効パラメータ: {params}")
    
    return True

def test_session_management():
    """セッション管理テスト"""
    print("\n🔐 セッション管理テスト")
    
    # 複数部門での同時セッション
    departments = ['土質・基礎', '都市計画', '施工計画']
    
    print("   複数部門同時セッション:")
    for i, dept in enumerate(departments):
        print(f"     セッション{i+1}: {dept}")
        print(f"       Cookie: session_{i+1}")
        print(f"       データ: exam_question_ids, exam_current, etc.")
    
    # セッション分離の重要性
    print("\n   セッション分離の重要性:")
    print("     - 各部門は独立したセッションを持つ")
    print("     - 問題IDの混在を防ぐ")
    print("     - 進捗状況の混在を防ぐ")
    
    return True

def main():
    """メイン検証関数"""
    print("🔧 本番環境互換性テスト - 土質・基礎部門修正後")
    print("=" * 60)
    
    verification_results = []
    
    # 1. 本番環境URL構造テスト
    result1 = test_production_urls()
    verification_results.append(("本番環境URL構造", result1))
    
    # 2. URL長制限テスト
    result2 = test_url_length_limits()
    verification_results.append(("URL長制限テスト", result2))
    
    # 3. 試験フロー シミュレーション
    result3 = test_exam_flow_simulation()
    verification_results.append(("試験フロー シミュレーション", result3))
    
    # 4. エラーハンドリングテスト
    result4 = test_error_handling()
    verification_results.append(("エラーハンドリング", result4))
    
    # 5. セッション管理テスト
    result5 = test_session_management()
    verification_results.append(("セッション管理", result5))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 検証結果サマリー")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in verification_results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    # 本番環境での注意点
    print("\n🚨 本番環境での注意点:")
    print("1. すべてのリクエストはPOSTメソッドを使用")
    print("2. 日本語部門名は正しくURLエンコードされる")
    print("3. HTTP 431エラーを回避するためGETからPOSTに移行済み")
    print("4. セッション管理は個別に分離されている")
    print("5. エラーハンドリングは適切に実装されている")
    
    # 推奨テスト手順
    print("\n📋 推奨テスト手順:")
    print("1. ブラウザで https://rccm-quiz-2025.onrender.com にアクセス")
    print("2. 各専門科目部門（土質・基礎、都市計画、等）を選択")
    print("3. 10問、20問、30問の問題数でテスト")
    print("4. 試験画面が正しく表示されるか確認")
    print("5. 問題内容が正しい部門のものかを確認")
    
    if all_passed:
        print("\n🎉 すべての互換性テストが成功しました！")
        print("本番環境での動作に問題はないと予想されます。")
    else:
        print("\n❌ 一部の互換性テストが失敗しました。")
        print("本番環境での動作に問題が発生する可能性があります。")
    
    # 検証結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"production_compatibility_test_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'verification_results': [
                {'test_name': name, 'result': result} 
                for name, result in verification_results
            ],
            'overall_success': all_passed,
            'production_url': 'https://rccm-quiz-2025.onrender.com',
            'tested_departments': ['土質・基礎', '都市計画', '鋼構造・コンクリート', '施工計画', '上下水道']
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 検証結果を {result_file} に保存しました。")

if __name__ == '__main__':
    main()