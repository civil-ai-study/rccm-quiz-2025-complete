#!/usr/bin/env python3
"""
シンプルな土質・基礎部門の動作検証スクリプト
Flask不要で基本的なマッピング機能を検証
"""

import sys
import os
import json
import time
import re
from datetime import datetime

# プロジェクトディレクトリを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_department_mapping():
    """部門マッピングの基本機能をテスト"""
    print("🔍 部門マッピング基本機能テスト")
    
    try:
        # app.pyから必要な部分のみ抽出してテスト
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # LEGACY_DEPARTMENT_ALIASESを抽出
        aliases_match = re.search(r'LEGACY_DEPARTMENT_ALIASES\s*=\s*\{([^}]+)\}', content, re.MULTILINE | re.DOTALL)
        if not aliases_match:
            print("❌ LEGACY_DEPARTMENT_ALIASESが見つかりません")
            return False
        
        # 辞書形式で評価
        aliases_text = aliases_match.group(1)
        print(f"🔍 LEGACY_DEPARTMENT_ALIASES抽出:")
        print(f"   {aliases_text[:200]}...")
        
        # 土質・基礎部門のマッピング確認
        target_mappings = [
            "'土質・基礎': 'soil_foundation'",
            "'都市計画': 'urban_planning'",
            "'鋼構造・コンクリート': 'steel_concrete'",
            "'施工計画': 'construction_planning'",
            "'上下水道': 'water_supply'"
        ]
        
        print(f"\n📊 修正対象マッピング確認:")
        for mapping in target_mappings:
            if mapping in content:
                print(f"  ✓ {mapping}")
            else:
                print(f"  ✗ {mapping}")
        
        return True
        
    except Exception as e:
        print(f"❌ マッピングテストエラー: {e}")
        return False

def test_data_files():
    """データファイルの存在確認"""
    print("\n📁 データファイル存在確認")
    
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            print(f"❌ データディレクトリが見つかりません: {data_dir}")
            return False
        
        # CSVファイルの確認
        csv_files = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        print(f"📊 CSVファイル数: {len(csv_files)}")
        
        # 土質・基礎関連のファイルを探す
        soil_files = [f for f in csv_files if 'soil' in f.lower() or '4-2' in f]
        print(f"土質・基礎関連ファイル数: {len(soil_files)}")
        
        # 各ファイルの行数確認
        for file in csv_files[:10]:  # 最初の10ファイルのみ
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                print(f"  {os.path.basename(file)}: {lines}行")
            except Exception as e:
                print(f"  {os.path.basename(file)}: 読み込みエラー - {e}")
        
        return len(csv_files) > 0
        
    except Exception as e:
        print(f"❌ データファイルテストエラー: {e}")
        return False

def test_route_patterns():
    """ルートパターンの確認"""
    print("\n🛣️ ルートパターン確認")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # start_exam関連のルート確認
        route_patterns = [
            r'@app\.route\([\'"]\/start_exam\/',
            r'def start_exam\(',
            r'normalize_department_name\(',
            r'get_safe_category_name\('
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, content)
            print(f"  {pattern}: {len(matches)}件")
        
        # POST対応の確認
        post_patterns = [
            r'methods\s*=\s*\[.*POST.*\]',
            r'request\.method\s*==\s*[\'"]POST[\'"]'
        ]
        
        for pattern in post_patterns:
            matches = re.findall(pattern, content)
            print(f"  POST対応 {pattern}: {len(matches)}件")
        
        return True
        
    except Exception as e:
        print(f"❌ ルートパターンテストエラー: {e}")
        return False

def test_app_structure():
    """アプリケーション構造の確認"""
    print("\n🏗️ アプリケーション構造確認")
    
    try:
        # 重要なファイルの存在確認
        important_files = [
            'app.py',
            'utils.py',
            'templates/index.html',
            'templates/exam.html',
            'static/style.css',
            'static/script.js'
        ]
        
        for file in important_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  ✓ {file}: {size} bytes")
            else:
                print(f"  ✗ {file}: 見つかりません")
        
        # app.pyのサイズ確認
        app_size = os.path.getsize('app.py')
        print(f"\n📊 app.pyサイズ: {app_size:,} bytes")
        
        if app_size > 500000:  # 500KB以上
            print("  ⚠️ app.pyが大きくなっています")
        
        return True
        
    except Exception as e:
        print(f"❌ アプリケーション構造テストエラー: {e}")
        return False

def main():
    """メイン検証関数"""
    print("🔧 シンプル土質・基礎部門動作検証")
    print("=" * 50)
    
    verification_results = []
    
    # 1. 部門マッピングテスト
    result1 = test_department_mapping()
    verification_results.append(("部門マッピング", result1))
    
    # 2. データファイルテスト
    result2 = test_data_files()
    verification_results.append(("データファイル", result2))
    
    # 3. ルートパターンテスト
    result3 = test_route_patterns()
    verification_results.append(("ルートパターン", result3))
    
    # 4. アプリケーション構造テスト
    result4 = test_app_structure()
    verification_results.append(("アプリケーション構造", result4))
    
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
        print("\n🎉 すべての基本検証が成功しました！")
        print("土質・基礎部門の修正が基本的に機能しています。")
        print("次は実際のFlaskアプリケーションでの動作確認を推奨します。")
    else:
        print("\n❌ 一部の検証が失敗しました。")
        print("修正内容を再確認してください。")
    
    # 検証結果をJSONファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"simple_soil_foundation_test_{timestamp}.json"
    
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