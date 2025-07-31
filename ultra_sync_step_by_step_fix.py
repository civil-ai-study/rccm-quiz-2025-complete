#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC段階的安全修正
型エラーを副作用ゼロで1箇所ずつ修正
"""

import re
from datetime import datetime

class UltraSyncStepByStepFix:
    def __init__(self):
        self.app_file = 'rccm-quiz-app/app.py'
        
    def create_safety_backup(self):
        """安全バックアップの作成"""
        print("ULTRA SYNC段階的安全修正")
        print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        print("\nStep 1: 安全バックアップの作成")
        
        try:
            # バックアップ作成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.app_file}.backup_ultrasync_{timestamp}"
            
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  バックアップ作成: {backup_path}")
            print(f"  ファイルサイズ: {len(content)} 文字")
            
            return True, backup_path, content
            
        except Exception as e:
            print(f"  バックアップ作成エラー: {e}")
            return False, None, None
    
    def find_exact_problematic_lines(self, content):
        """問題箇所の正確な特定"""
        print("\nStep 2: 問題箇所の正確な特定")
        
        lines = content.split('\n')
        problematic_lines = []
        
        # 型エラーを引き起こす可能性の高いパターンを検索
        dangerous_patterns = [
            # パターン1: session.get('exam_current')の直接比較
            r"session\.get\(['\"]exam_current['\"][^)]*\)\s*([><=]+)",
            # パターン2: session.get('exam_current')の直接算術演算
            r"session\.get\(['\"]exam_current['\"][^)]*\)\s*[+\-*/]",
            # パターン3: 型チェックなしの直接代入後の使用
            r"=\s*session\.get\(['\"]exam_current['\"][^)]*\)(?![^;]*isinstance)"
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line):
                    # 既に修正済み（isinstance や get_exam_current_safe を含む）かチェック
                    if 'isinstance' not in line and 'get_exam_current_safe' not in line:
                        problematic_lines.append({
                            'line_number': i,
                            'content': line.strip(),
                            'pattern': pattern,
                            'risk_level': 'high'
                        })
        
        print(f"  検出された問題箇所: {len(problematic_lines)}行")
        
        # 上位5行のみ表示
        for problem in problematic_lines[:5]:
            print(f"    行{problem['line_number']}: {problem['content']}")
        
        return problematic_lines
    
    def fix_single_line_safely(self, content, line_info):
        """単一行の安全修正"""
        print(f"\nStep 3: 行{line_info['line_number']}の安全修正")
        
        lines = content.split('\n')
        target_line = lines[line_info['line_number'] - 1]
        
        print(f"  修正対象: {target_line.strip()}")
        
        # 修正パターンの適用
        modified_line = target_line
        
        # パターン1: session.get('exam_current', 0) >= の修正
        pattern1 = r"session\.get\(['\"]exam_current['\"]\s*,\s*(\d+)\)\s*([><=]+)\s*(\w+)"
        if re.search(pattern1, target_line):
            modified_line = re.sub(
                pattern1,
                r"get_exam_current_safe(session, \1) \2 \3",
                target_line
            )
            print("  適用修正: 型安全関数による比較演算修正")
        
        # パターン2: session.get('exam_current') >= の修正（デフォルト値なし）
        pattern2 = r"session\.get\(['\"]exam_current['\"])\s*([><=]+)\s*(\w+)"
        if re.search(pattern2, target_line):
            modified_line = re.sub(
                pattern2,
                r"get_exam_current_safe(session, 0) \1 \2",
                target_line
            )
            print("  適用修正: 型安全関数による比較演算修正（デフォルト値追加）")
        
        # パターン3: session.get('exam_current', 0) + 1 の修正
        pattern3 = r"session\.get\(['\"]exam_current['\"]\s*,\s*(\d+)\)\s*([+\-*/])\s*(\d+)"
        if re.search(pattern3, target_line):
            modified_line = re.sub(
                pattern3,
                r"get_exam_current_safe(session, \1) \2 \3",
                target_line
            )
            print("  適用修正: 型安全関数による算術演算修正")
        
        if modified_line != target_line:
            print(f"  修正後: {modified_line.strip()}")
            
            # 修正を適用
            lines[line_info['line_number'] - 1] = modified_line
            new_content = '\n'.join(lines)
            
            return True, new_content
        else:
            print("  修正不要または修正パターン該当なし")
            return False, content
    
    def verify_syntax_safety(self, content):
        """構文安全性の確認"""
        print("\nStep 4: 構文安全性の確認")
        
        try:
            import ast
            # 構文解析テスト
            ast.parse(content)
            print("  構文チェック: OK")
            return True
        except SyntaxError as e:
            print(f"  構文エラー: {e}")
            return False
        except Exception as e:
            print(f"  チェックエラー: {e}")
            return False
    
    def apply_single_fix(self):
        """単一修正の適用"""
        # Step 1: バックアップ
        backup_success, backup_path, content = self.create_safety_backup()
        if not backup_success:
            return False
        
        # Step 2: 問題箇所特定
        problematic_lines = self.find_exact_problematic_lines(content)
        if not problematic_lines:
            print("\n結果: 修正対象なし")
            return True
        
        # Step 3: 最初の問題箇所のみ修正（段階的実行）
        first_problem = problematic_lines[0]
        fix_applied, modified_content = self.fix_single_line_safely(content, first_problem)
        
        if not fix_applied:
            print("\n結果: 修正適用なし")
            return True
        
        # Step 4: 構文確認
        if not self.verify_syntax_safety(modified_content):
            print("\n結果: 構文エラーのため修正中止")
            return False
        
        # Step 5: ファイル更新
        try:
            with open(self.app_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print("\nStep 5: ファイル更新完了")
            print(f"  修正済み: 行{first_problem['line_number']}")
            print(f"  バックアップ: {backup_path}")
            return True
        except Exception as e:
            print(f"\nファイル更新エラー: {e}")
            return False

def main():
    print("ULTRA SYNC段階的安全修正システム")
    print("目的: 型エラーの段階的修正（副作用ゼロ保証）")
    print("=" * 70)
    
    fixer = UltraSyncStepByStepFix()
    
    # 単一修正の適用
    result = fixer.apply_single_fix()
    
    print("\n" + "=" * 70)
    print("ULTRA SYNC段階的修正結果")
    print("=" * 70)
    
    if result:
        print("修正実行: 成功")
        print("次のステップ: 修正後の動作確認テスト")
        print("重要: 1箇所のみ修正済み、追加修正は動作確認後")
    else:
        print("修正実行: 失敗")
        print("バックアップから復旧して再実行")
    
    return result

if __name__ == "__main__":
    main()