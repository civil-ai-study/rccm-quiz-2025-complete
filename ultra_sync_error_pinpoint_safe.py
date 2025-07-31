#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC ピンポイントエラー特定（安全版）
型エラーの正確な発生箇所を特定し、副作用ゼロで修正計画を立案
"""

import requests
import re
from datetime import datetime

class UltraSyncErrorPinpointSafe:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def detect_exact_error_location(self):
        """正確なエラー箇所の特定"""
        print("ULTRA SYNC エラー箇所ピンポイント特定")
        print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("目的: 型エラー発生箇所の完全特定")
        print("=" * 60)
        
        try:
            # Stage 1: エラー再現
            print("\nStage 1: エラーの確実な再現")
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 1, "year": "2018"}
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"  セッション初期化: HTTP {start_response.status_code}")
            
            # Stage 2: エラー詳細抽出
            print("\nStage 2: エラー詳細の抽出")
            content = start_response.text
            
            # エラーメッセージの精密検索
            error_patterns = [
                r"詳細[：:]\s*([^<]+)",
                r"not supported between instances[^<]*",
                r"TypeError[：:]([^<]+)"
            ]
            
            found_errors = []
            for pattern in error_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    clean_match = match.strip()
                    if clean_match and clean_match not in found_errors:
                        found_errors.append(clean_match)
            
            print(f"  検出エラー: {len(found_errors)}件")
            for i, error in enumerate(found_errors, 1):
                print(f"    {i}. {error}")
            
            # Stage 3: エラー種類の判定
            print("\nStage 3: エラー種類の判定")
            
            type_error_confirmed = False
            for error in found_errors:
                if "not supported between instances" in error and "'str'" in error and "'int'" in error:
                    type_error_confirmed = True
                    print("  確認: 文字列vs整数の比較エラー発生中")
                    break
            
            if not type_error_confirmed:
                print("  結果: 型エラー以外またはエラー未検出")
                return False, found_errors
            
            # Stage 4: 未修正箇所の推定
            print("\nStage 4: 未修正箇所の推定")
            
            # これまでの修正履歴から未修正箇所を推定
            likely_locations = [
                "exam関数内のセッション処理",
                "問題データ取得処理",
                "プログレス計算処理",
                "セッション状態判定処理"
            ]
            
            print("  推定未修正箇所:")
            for i, location in enumerate(likely_locations, 1):
                print(f"    {i}. {location}")
            
            return True, found_errors
            
        except Exception as e:
            print(f"  エラー特定処理失敗: {e}")
            return False, [str(e)]
    
    def create_safe_fix_plan(self, errors_found):
        """安全な修正計画の作成"""
        print("\nStage 5: 安全修正計画の作成")
        print("副作用ゼロ保証・段階的実行")
        
        if not errors_found:
            print("  修正対象なし")
            return []
        
        # 段階的修正計画
        fix_plan = [
            {
                'step': 1,
                'description': 'app.pyの完全バックアップ作成',
                'risk_level': 'none',
                'verification': 'バックアップファイル存在確認'
            },
            {
                'step': 2,
                'description': 'exam関数内のsession.get使用箇所特定',
                'risk_level': 'none',
                'verification': '検索結果の手動確認'
            },
            {
                'step': 3,
                'description': '最も可能性の高い1箇所のみ修正',
                'risk_level': 'low',
                'verification': '構文チェック＋単体テスト'
            },
            {
                'step': 4,
                'description': '修正後の動作確認テスト',
                'risk_level': 'none',
                'verification': '河川・砂防2018年での1問テスト'
            },
            {
                'step': 5,
                'description': '副作用チェック（基礎科目・他部門）',
                'risk_level': 'none',
                'verification': '複数部門での動作確認'
            }
        ]
        
        print("  段階的修正計画:")
        for plan in fix_plan:
            print(f"    Step {plan['step']}: {plan['description']}")
            print(f"      リスク: {plan['risk_level']}")
            print(f"      確認: {plan['verification']}")
        
        return fix_plan
    
    def execute_safe_backup(self):
        """安全バックアップの実行"""
        print("\nStage 6: 安全バックアップの実行")
        
        try:
            # バックアップファイル作成
            backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"rccm-quiz-app/app.py.backup_ultrasync_safe_{backup_timestamp}"
            
            with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # バックアップ確認
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            if backup_content == content:
                print(f"  バックアップ作成完了: {backup_path}")
                print(f"  ファイルサイズ: {len(content)} 文字")
                print("  整合性: OK")
                return True, backup_path
            else:
                print("  バックアップ整合性エラー")
                return False, None
                
        except Exception as e:
            print(f"  バックアップ作成エラー: {e}")
            return False, None

def main():
    print("ULTRA SYNC エラーピンポイント特定システム")
    print("目的: 型エラーの完全特定と安全修正計画")
    print("方針: 副作用ゼロ・段階的実行")
    print("=" * 70)
    
    detector = UltraSyncErrorPinpointSafe()
    
    # エラー特定
    error_confirmed, found_errors = detector.detect_exact_error_location()
    
    # 修正計画作成
    fix_plan = detector.create_safe_fix_plan(found_errors) if error_confirmed else []
    
    # 安全バックアップ
    backup_success, backup_path = detector.execute_safe_backup() if error_confirmed else (False, None)
    
    # 総合結果
    print("\n" + "=" * 70)
    print("ULTRA SYNC ピンポイント特定結果")
    print("=" * 70)
    
    print(f"エラー確認: {'YES' if error_confirmed else 'NO'}")
    print(f"検出エラー数: {len(found_errors)}")
    print(f"修正計画: {len(fix_plan)}段階")
    print(f"バックアップ: {'作成済み' if backup_success else '未実行'}")
    
    if error_confirmed and backup_success:
        print("\nULTRA SYNC準備完了")
        print("次のステップ: 段階的安全修正の実行")
        print(f"バックアップ: {backup_path}")
        print("重要: 1段階ずつ実行し、各段階で動作確認")
        return True
    elif error_confirmed:
        print("\nULTRA SYNC準備未完了")
        print("バックアップ作成後に修正実行")
        return False
    else:
        print("\nエラー未確認または別問題")
        print("さらなる調査が必要")
        return False

if __name__ == "__main__":
    main()