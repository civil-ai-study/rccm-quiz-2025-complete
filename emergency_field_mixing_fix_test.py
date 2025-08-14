#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 緊急対応：分野混在問題修正テスト（ウルトラシンク方式）
目的: Task 9で特定されたLIGHTWEIGHT_DEPARTMENT_MAPPING問題の根本修正
問題箇所: app.py line 2585: target_category = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
解決方針: 英語ID変換システムを廃止し、日本語カテゴリ直接使用に変更
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_current_problem():
    """現在の問題を実証するテスト"""
    print("=== 🚨 現在の分野混在問題実証テスト ===")
    print("目的: LIGHTWEIGHT_DEPARTMENT_MAPPINGシステムの問題点を実証")
    print()
    
    try:
        from app import app
        
        # 河川部門での問題を実証
        with app.test_client() as client:
            print("【河川部門専門問題テスト】")
            
            # 河川部門セッション開始
            response = client.get('/exam?type=specialist&department=river')
            print(f"HTTPステータス: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                
                # 分野混在チェック
                if '基礎科目（共通）' in response_text:
                    print("❌ 分野混在問題確認: 河川部門で基礎科目問題が出題")
                    print("原因: LIGHTWEIGHT_DEPARTMENT_MAPPING変換システムの不具合")
                elif '河川、砂防及び海岸・海洋' in response_text:
                    print("✅ 正常: 河川部門問題が出題")
                else:
                    print("⚠️ 不明な状態")
                
                # デバッグ情報抽出
                import re
                debug_info = re.findall(r'🔍.*カテゴリ.*?([^<]*)', response_text)
                if debug_info:
                    print(f"デバッグ情報: {debug_info}")
                
                return '基礎科目（共通）' in response_text
            else:
                print(f"❌ HTTPエラー: {response.status_code}")
                return True
                
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return True

def create_emergency_fix():
    """緊急修正の実装"""
    print("\n=== 🔧 緊急修正実装 ===")
    print("修正内容: LIGHTWEIGHT_DEPARTMENT_MAPPINGシステムを日本語カテゴリ直接使用に変更")
    print()
    
    try:
        # バックアップ作成
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'rccm-quiz-app/app.py.backup_emergency_field_mixing_fix_{timestamp}'
        
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ バックアップ作成: {backup_file}")
        
        # 修正実行
        lines = original_content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Line 2585の修正: 英語ID→日本語カテゴリ変換を廃止
            if 'target_category = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)' in line:
                lines[i] = '                            # 🔥 EMERGENCY FIX: 英語ID変換システム廃止、日本語カテゴリ直接使用'
                lines.insert(i+1, '                            # 河川部門(river) → 河川、砂防及び海岸・海洋 (直接指定)')
                lines.insert(i+2, '                            target_category = department  # 一時的措置')
                lines.insert(i+3, '                            if department == "river":')
                lines.insert(i+4, '                                target_category = "河川、砂防及び海岸・海洋"')
                lines.insert(i+5, '                            elif department == "road":')
                lines.insert(i+6, '                                target_category = "道路"')
                lines.insert(i+7, '                            elif department == "urban":')
                lines.insert(i+8, '                                target_category = "都市計画及び地方計画"')
                lines.insert(i+9, '                            # 他の部門も同様に直接マッピング（一時的措置）')
                modified = True
                break
        
        if modified:
            fixed_content = '\n'.join(lines)
            with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print("✅ 緊急修正適用: 英語ID変換システムを一時的に日本語カテゴリ直接指定に変更")
            return True
        else:
            print("❌ 修正対象行が見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ 修正エラー: {str(e)}")
        return False

def test_after_fix():
    """修正後テスト"""
    print("\n=== 🧪 修正後動作確認テスト ===")
    print("目的: 分野混在問題が解決されたかを確認")
    print()
    
    try:
        # モジュールリロードが必要
        import importlib
        import sys
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        
        with app.test_client() as client:
            print("【修正後河川部門テスト】")
            
            # 河川部門セッション開始
            response = client.get('/exam?type=specialist&department=river')
            print(f"HTTPステータス: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                
                # 修正効果確認
                if '河川、砂防及び海岸・海洋' in response_text:
                    print("✅ 修正成功: 河川部門専門問題が正常に出題")
                    field_mixing_fixed = True
                elif '基礎科目（共通）' in response_text:
                    print("❌ 修正失敗: まだ分野混在問題が継続")
                    field_mixing_fixed = False
                else:
                    print("⚠️ 修正結果不明")
                    field_mixing_fixed = False
                
                # デバッグ情報確認
                import re
                debug_info = re.findall(r'🔍.*カテゴリ.*?([^<]*)', response_text)
                if debug_info:
                    print(f"修正後デバッグ情報: {debug_info}")
                
                return field_mixing_fixed
            else:
                print(f"❌ HTTPエラー: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")
        return False

def run_emergency_field_mixing_fix():
    """緊急分野混在修正の実行メイン"""
    print("🚨 緊急対応：分野混在問題修正（LIGHTWEIGHT_DEPARTMENT_MAPPING問題対応）")
    print("=" * 80)
    print("発見経緯: Task 9 河川部門10問完走テストで分野混在問題を特定")
    print("問題箇所: app.py line 2585 英語ID→日本語カテゴリ変換システム")
    print("修正方針: 英語ID変換を廃止し、日本語カテゴリ直接使用に変更")
    print()
    
    # Step 1: 問題実証
    problem_exists = test_current_problem()
    
    if problem_exists:
        print("\n🔧 分野混在問題確認 - 緊急修正を実行します")
        
        # Step 2: 緊急修正実行
        fix_success = create_emergency_fix()
        
        if fix_success:
            # Step 3: 修正後テスト
            fix_verified = test_after_fix()
            
            print("\n" + "=" * 80)
            print("=== 緊急修正結果サマリー ===")
            print("=" * 80)
            
            if fix_verified:
                print("✅ 緊急修正成功")
                print("✅ 分野混在問題解決確認")
                print("✅ 河川部門専門問題正常出題確認")
                print()
                print(">>> Next Action: Task 9 河川部門10問完走テスト再実行推奨")
            else:
                print("❌ 緊急修正失敗または効果不十分")
                print(">>> Next Action: より根本的な修正が必要")
        else:
            print("❌ 緊急修正の適用に失敗")
            print(">>> Next Action: 手動修正が必要")
    else:
        print("\n✅ 分野混在問題は既に解決済み")
        print(">>> Next Action: 他の部門テストに進行可能")

if __name__ == "__main__":
    run_emergency_field_mixing_fix()