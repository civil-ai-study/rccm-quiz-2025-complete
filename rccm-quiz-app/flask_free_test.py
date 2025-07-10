#!/usr/bin/env python3
"""
Flask依存関係なしで土質・基礎部門機能を直接テスト
"""

import sys
import os
import re
import json
from datetime import datetime

def extract_legacy_aliases():
    """app.pyからLEGACY_DEPARTMENT_ALIASESを抽出"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # LEGACY_DEPARTMENT_ALIASESの開始位置を見つける
        start_match = re.search(r'LEGACY_DEPARTMENT_ALIASES\s*=\s*\{', content)
        if not start_match:
            return None
        
        start_pos = start_match.end() - 1  # '{' の位置
        
        # 対応する '}' を見つける
        brace_count = 0
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = start_pos + i + 1
                    break
        
        # 辞書部分を抽出
        dict_text = content[start_pos:end_pos]
        
        # 各行を解析してマッピングを構築
        aliases = {}
        for line in dict_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 'key': 'value' パターンを探す
            match = re.match(r"'([^']+)':\s*'([^']+)'", line)
            if match:
                key, value = match.groups()
                aliases[key] = value
        
        return aliases
        
    except Exception as e:
        print(f"❌ エイリアス抽出エラー: {e}")
        return None

def extract_department_mapping():
    """DEPARTMENT_TO_CATEGORY_MAPPINGを抽出"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # DEPARTMENT_TO_CATEGORY_MAPPINGの開始位置を見つける
        start_match = re.search(r'DEPARTMENT_TO_CATEGORY_MAPPING\s*=\s*\{', content)
        if not start_match:
            return None
        
        start_pos = start_match.end() - 1  # '{' の位置
        
        # 対応する '}' を見つける
        brace_count = 0
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = start_pos + i + 1
                    break
        
        # 辞書部分を抽出
        dict_text = content[start_pos:end_pos]
        
        # 各行を解析してマッピングを構築
        mapping = {}
        for line in dict_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 'key': 'value' パターンを探す
            match = re.match(r"'([^']+)':\s*'([^']+)'", line)
            if match:
                key, value = match.groups()
                mapping[key] = value
        
        return mapping
        
    except Exception as e:
        print(f"❌ マッピング抽出エラー: {e}")
        return None

def simulate_normalize_department_name(department_name, aliases, mapping):
    """normalize_department_name関数をシミュレート"""
    if not department_name:
        return None
    
    # 既に正規化済みの場合
    if department_name in mapping:
        return department_name
    
    # エイリアスの場合は変換
    if department_name in aliases:
        return aliases[department_name]
    
    return department_name

def simulate_get_safe_category_name(department, aliases, mapping):
    """get_safe_category_name関数をシミュレート"""
    if department == "基礎科目":
        return "4-1"
    elif department == "専門科目":
        return "4-2"
    
    # 正規化された部門名を取得
    normalized = simulate_normalize_department_name(department, aliases, mapping)
    if normalized and normalized in mapping:
        return mapping[normalized]
    
    return None

def main():
    """メイン検証関数"""
    print("🔧 Flask依存関係なし土質・基礎部門機能テスト")
    print("=" * 60)
    
    # 1. エイリアス抽出
    print("1. LEGACY_DEPARTMENT_ALIASES抽出中...")
    aliases = extract_legacy_aliases()
    if aliases:
        print(f"   ✓ {len(aliases)}個のエイリアスを抽出")
    else:
        print("   ✗ エイリアス抽出失敗")
        return
    
    # 2. マッピング抽出
    print("\n2. DEPARTMENT_TO_CATEGORY_MAPPING抽出中...")
    mapping = extract_department_mapping()
    if mapping:
        print(f"   ✓ {len(mapping)}個のマッピングを抽出")
    else:
        print("   ✗ マッピング抽出失敗")
        return
    
    # 3. 土質・基礎部門関連の検証
    print("\n3. 土質・基礎部門関連検証:")
    target_departments = ['土質・基礎', '都市計画', '鋼構造・コンクリート', '施工計画', '上下水道']
    
    for dept in target_departments:
        # エイリアス確認
        if dept in aliases:
            print(f"   ✓ エイリアス: {dept} → {aliases[dept]}")
        else:
            print(f"   ✗ エイリアス: {dept} が見つかりません")
        
        # 正規化機能テスト
        normalized = simulate_normalize_department_name(dept, aliases, mapping)
        category = simulate_get_safe_category_name(dept, aliases, mapping)
        print(f"     正規化: {dept} → {normalized}")
        print(f"     カテゴリ: {dept} → {category}")
    
    # 4. 英語名からの逆引きテスト
    print("\n4. 英語名からの逆引きテスト:")
    english_names = ['soil_foundation', 'urban_planning', 'steel_concrete', 'construction_planning', 'water_supply']
    
    for eng_name in english_names:
        # 正規化機能テスト
        normalized = simulate_normalize_department_name(eng_name, aliases, mapping)
        category = simulate_get_safe_category_name(eng_name, aliases, mapping)
        print(f"   {eng_name} → 正規化: {normalized}, カテゴリ: {category}")
    
    # 5. 短縮形テスト
    print("\n5. 短縮形テスト:")
    short_names = ['soil', 'foundation', 'urban', 'planning']
    
    for short_name in short_names:
        # 正規化機能テスト
        normalized = simulate_normalize_department_name(short_name, aliases, mapping)
        category = simulate_get_safe_category_name(short_name, aliases, mapping)
        print(f"   {short_name} → 正規化: {normalized}, カテゴリ: {category}")
    
    # 6. 結果サマリー
    print("\n" + "=" * 60)
    print("📊 検証結果サマリー")
    print("=" * 60)
    
    # 必要なマッピングが存在するかチェック
    required_aliases = ['土質・基礎', '都市計画', '鋼構造・コンクリート', '施工計画', '上下水道']
    missing_aliases = [dept for dept in required_aliases if dept not in aliases]
    
    if not missing_aliases:
        print("✓ すべての必要なエイリアスが存在します")
    else:
        print(f"✗ 不足エイリアス: {missing_aliases}")
    
    # 英語名マッピングの確認
    required_english = ['soil_foundation', 'urban_planning', 'steel_concrete', 'construction_planning', 'water_supply']
    missing_english = [eng for eng in required_english if eng not in mapping]
    
    if not missing_english:
        print("✓ すべての必要な英語名マッピングが存在します")
    else:
        print(f"✗ 不足英語名マッピング: {missing_english}")
    
    # 検証結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"flask_free_test_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'aliases_count': len(aliases),
            'mapping_count': len(mapping),
            'required_aliases': required_aliases,
            'missing_aliases': missing_aliases,
            'required_english': required_english,
            'missing_english': missing_english,
            'success': len(missing_aliases) == 0 and len(missing_english) == 0
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 検証結果を {result_file} に保存しました。")
    
    if len(missing_aliases) == 0 and len(missing_english) == 0:
        print("\n🎉 すべての検証が成功しました！")
        print("土質・基礎部門の修正が正しく適用されています。")
    else:
        print("\n❌ 一部の検証が失敗しました。")
        print("app.pyの修正内容を確認してください。")

if __name__ == '__main__':
    main()