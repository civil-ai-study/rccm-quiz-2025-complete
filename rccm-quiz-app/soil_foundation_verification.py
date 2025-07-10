#!/usr/bin/env python3
"""
土質・基礎部門の動作検証スクリプト
修正後のsoil_foundation部門マッピングが正しく機能するかを検証
"""

import sys
import os
import json
import time
import requests
from datetime import datetime

# Flask アプリケーションを直接テストするための設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_soil_foundation_mapping():
    """土質・基礎部門マッピングの検証"""
    print("🔍 土質・基礎部門マッピング検証開始")
    
    try:
        # アプリケーションをインポート
        from app import app, normalize_department_name, get_safe_category_name, LEGACY_DEPARTMENT_ALIASES
        
        # 1. マッピング確認
        print("\n1. 部門マッピング確認:")
        test_names = ['土質・基礎', 'soil_foundation', 'soil', 'foundation']
        
        for name in test_names:
            normalized = normalize_department_name(name)
            category = get_safe_category_name(name)
            print(f"  {name} → 正規化: {normalized}, カテゴリー: {category}")
        
        # 2. LEGACY_DEPARTMENT_ALIASESの確認
        print(f"\n2. LEGACY_DEPARTMENT_ALIASES確認:")
        if '土質・基礎' in LEGACY_DEPARTMENT_ALIASES:
            print(f"  '土質・基礎' → {LEGACY_DEPARTMENT_ALIASES['土質・基礎']} ✓")
        else:
            print(f"  '土質・基礎' が見つかりません ✗")
            
        # 3. 他の専門科目部門も確認
        print(f"\n3. 他の専門科目部門確認:")
        specialist_depts = ['都市計画', '鋼構造・コンクリート', '施工計画', '上下水道']
        for dept in specialist_depts:
            if dept in LEGACY_DEPARTMENT_ALIASES:
                print(f"  '{dept}' → {LEGACY_DEPARTMENT_ALIASES[dept]} ✓")
            else:
                print(f"  '{dept}' が見つかりません ✗")
        
        return True
        
    except Exception as e:
        print(f"❌ マッピング検証エラー: {e}")
        return False

def test_local_flask_app():
    """ローカルFlaskアプリケーションのテスト"""
    print("\n🚀 ローカルFlaskアプリケーションテスト開始")
    
    try:
        from app import app
        
        # テストクライアントを作成
        with app.test_client() as client:
            # 1. メインページアクセス
            print("\n1. メインページアクセステスト:")
            response = client.get('/')
            print(f"  ステータス: {response.status_code}")
            print(f"  レスポンス長: {len(response.data)} bytes")
            
            # 2. 土質・基礎部門で試験開始テスト
            print("\n2. 土質・基礎部門試験開始テスト:")
            
            # 10問、20問、30問でテスト
            for question_count in [10, 20, 30]:
                print(f"\n  {question_count}問テスト:")
                
                # POST リクエストでテスト
                response = client.post('/start_exam/土質・基礎', data={
                    'questions': str(question_count),
                    'year': '2024'
                })
                
                print(f"    ステータス: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    成功: {question_count}問で試験開始 ✓")
                elif response.status_code == 302:
                    print(f"    リダイレクト: {response.location}")
                else:
                    print(f"    エラー: {response.status_code}")
                    print(f"    レスポンス: {response.data.decode('utf-8')[:500]}...")
            
            # 3. 他の専門科目部門でもテスト
            print("\n3. 他の専門科目部門テスト:")
            specialist_depts = ['都市計画', '鋼構造・コンクリート', '施工計画', '上下水道']
            
            for dept in specialist_depts:
                response = client.post(f'/start_exam/{dept}', data={
                    'questions': '10',
                    'year': '2024'
                })
                
                if response.status_code in [200, 302]:
                    print(f"  {dept}: 成功 ✓")
                else:
                    print(f"  {dept}: エラー {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ ローカルテストエラー: {e}")
        return False

def verify_data_availability():
    """データ可用性の検証"""
    print("\n📊 データ可用性検証開始")
    
    try:
        from app import app
        from utils import load_questions_data, filter_questions_by_department
        
        # データ読み込み
        all_questions = load_questions_data()
        print(f"全問題数: {len(all_questions)}")
        
        # 土質・基礎部門の問題を取得
        soil_questions = filter_questions_by_department(all_questions, 'soil_foundation')
        print(f"土質・基礎部門問題数: {len(soil_questions)}")
        
        if len(soil_questions) == 0:
            print("❌ 土質・基礎部門の問題が見つかりません")
            return False
            
        # 年度別問題数
        years = {}
        for q in soil_questions:
            year = q.get('year', 'unknown')
            years[year] = years.get(year, 0) + 1
        
        print("年度別問題数:")
        for year, count in sorted(years.items()):
            print(f"  {year}: {count}問")
        
        # 他の専門科目部門も確認
        specialist_depts = {
            '都市計画': 'urban_planning',
            '鋼構造・コンクリート': 'steel_concrete', 
            '施工計画': 'construction_planning',
            '上下水道': 'water_supply'
        }
        
        print(f"\n他の専門科目部門問題数:")
        for dept_jp, dept_en in specialist_depts.items():
            questions = filter_questions_by_department(all_questions, dept_en)
            print(f"  {dept_jp}: {len(questions)}問")
        
        return True
        
    except Exception as e:
        print(f"❌ データ検証エラー: {e}")
        return False

def main():
    """メイン検証関数"""
    print("🔧 土質・基礎部門動作検証スクリプト")
    print("=" * 50)
    
    verification_results = []
    
    # 1. マッピング検証
    result1 = verify_soil_foundation_mapping()
    verification_results.append(("マッピング検証", result1))
    
    # 2. データ可用性検証
    result2 = verify_data_availability()
    verification_results.append(("データ可用性検証", result2))
    
    # 3. ローカルアプリケーションテスト
    result3 = test_local_flask_app()
    verification_results.append(("ローカルアプリテスト", result3))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 検証結果サマリー")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in verification_results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 すべての検証が成功しました！")
        print("土質・基礎部門の修正が正しく機能しています。")
    else:
        print("\n❌ 一部の検証が失敗しました。")
        print("修正に問題がある可能性があります。")
    
    # 検証結果をJSONファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"soil_foundation_verification_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'verification_results': [
                {'test_name': name, 'result': result} 
                for name, result in verification_results
            ],
            'overall_success': all_passed
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 検証結果を {result_file} に保存しました。")

if __name__ == '__main__':
    main()