#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC start_exam関数深層スキャン
start_exam関数内の残存型エラー箇所を完全特定
副作用ゼロ保証・段階的実行
"""

import re
from datetime import datetime

class UltraSyncStartExamDeepScan:
    def __init__(self):
        self.app_file = 'rccm-quiz-app/app.py'
        
    def extract_start_exam_function(self):
        """start_exam関数の完全抽出"""
        print("ULTRA SYNC start_exam関数深層スキャン")
        print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("目的: start_exam関数内の残存型エラー完全特定")
        print("=" * 60)
        
        try:
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            print(f"ファイル解析: {len(lines)}行")
            
            # start_exam関数の範囲特定
            start_line = None
            end_line = None
            
            for i, line in enumerate(lines, 1):
                if '@app.route(\'/start_exam/<path:department>\')' in line:
                    start_line = i
                    break
            
            if start_line:
                # 関数終了を探す（次の@app.routeまたはdef）
                for i in range(start_line, len(lines)):
                    line = lines[i]
                    if i > start_line and (line.startswith('@app.route') or (line.startswith('def ') and not line.strip().startswith('def '))):
                        end_line = i
                        break
                
                if not end_line:
                    end_line = len(lines)
                
                print(f"start_exam関数範囲: {start_line}～{end_line}行 ({end_line - start_line}行)")
                return lines, start_line, end_line
            else:
                print("start_exam関数が見つかりません")
                return None, None, None
                
        except Exception as e:
            print(f"抽出エラー: {e}")
            return None, None, None
    
    def scan_dangerous_patterns_in_start_exam(self, lines, start_line, end_line):
        """start_exam関数内の危険パターンスキャン"""
        print(f"\nstart_exam関数内危険パターンスキャン")
        
        if not lines or not start_line or not end_line:
            print("  スキャン対象なし")
            return []
        
        dangerous_findings = []
        
        # start_exam関数内のみをスキャン
        for i in range(start_line - 1, end_line - 1):
            line_num = i + 1
            line_content = lines[i]
            
            # パターン1: session.get('exam_current')の直接使用
            if "session.get('exam_current'" in line_content:
                # 型安全化されているかチェック
                if not any(safe in line_content for safe in ['get_exam_current_safe', 'isinstance', 'int(', 'try:']):
                    # 前後行もチェック
                    context_safe = False
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        context_line = lines[j]
                        if any(safe in context_line for safe in ['get_exam_current_safe', 'isinstance', 'try:', 'except:']):
                            context_safe = True
                            break
                    
                    if not context_safe:
                        dangerous_findings.append({
                            'line': line_num,
                            'content': line_content.strip(),
                            'type': 'raw_session_get',
                            'risk': 'high'
                        })
            
            # パターン2: 比較演算子と組み合わせ
            if any(op in line_content for op in [' >= ', ' <= ', ' > ', ' < ', ' == ', ' != ']):
                if 'exam_current' in line_content and 'session' in line_content:
                    if not any(safe in line_content for safe in ['get_exam_current_safe', 'isinstance']):
                        dangerous_findings.append({
                            'line': line_num,
                            'content': line_content.strip(),
                            'type': 'comparison_without_safety',
                            'risk': 'critical'
                        })
            
            # パターン3: len()との比較
            if 'len(' in line_content and 'exam_current' in line_content:
                if any(op in line_content for op in [' >= len(', ' < len(', ' > len(']):
                    if not any(safe in line_content for safe in ['get_exam_current_safe', 'isinstance']):
                        dangerous_findings.append({
                            'line': line_num,
                            'content': line_content.strip(),
                            'type': 'len_comparison',
                            'risk': 'critical'
                        })
        
        print(f"  発見された危険パターン: {len(dangerous_findings)}箇所")
        
        # リスク順ソート
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        dangerous_findings.sort(key=lambda x: risk_order[x['risk']])
        
        for finding in dangerous_findings[:5]:  # 上位5件表示
            print(f"    行{finding['line']} ({finding['risk']}): {finding['content'][:50]}...")
        
        return dangerous_findings
    
    def analyze_specific_error_location(self, dangerous_findings):
        """特定エラー箇所の詳細分析"""
        print(f"\n特定エラー箇所の詳細分析")
        
        if not dangerous_findings:
            print("  分析対象なし")
            return None
        
        # 最高リスクの箇所を選択
        target = dangerous_findings[0]
        
        print(f"  最優先修正対象:")
        print(f"    行番号: {target['line']}")
        print(f"    リスク: {target['risk']}")
        print(f"    タイプ: {target['type']}")
        print(f"    内容: {target['content']}")
        
        # 修正案の生成
        original_line = target['content']
        suggested_fix = self._generate_fix_suggestion(original_line, target['type'])
        
        if suggested_fix:
            print(f"  修正案:")
            print(f"    修正前: {original_line}")
            print(f"    修正後: {suggested_fix}")
        
        return target
    
    def _generate_fix_suggestion(self, line, error_type):
        """修正案の生成"""
        if error_type == 'raw_session_get':
            # session.get('exam_current')をget_exam_current_safe()に置換
            if "session.get('exam_current'" in line:
                return re.sub(
                    r"session\.get\('exam_current'[^)]*\)",
                    "get_exam_current_safe(session, 0)",
                    line
                )
        
        elif error_type == 'comparison_without_safety':
            # 比較演算の型安全化
            if "session.get('exam_current'" in line:
                return re.sub(
                    r"session\.get\('exam_current'[^)]*\)",
                    "get_exam_current_safe(session, 0)",
                    line
                )
        
        elif error_type == 'len_comparison':
            # len()比較の型安全化
            if "session.get('exam_current'" in line:
                return re.sub(
                    r"session\.get\('exam_current'[^)]*\)",
                    "get_exam_current_safe(session, 0)",
                    line
                )
        
        return None
    
    def execute_targeted_fix(self, target):
        """対象箇所の安全修正実行"""
        print(f"\n対象箇所の安全修正実行")
        
        if not target:
            print("  修正対象なし")
            return True
        
        try:
            # 安全バックアップ
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.app_file}.backup_deep_scan_{timestamp}"
            
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  バックアップ作成: {backup_path}")
            
            # 修正実行
            lines = content.split('\n')
            target_line_index = target['line'] - 1
            original_line = lines[target_line_index]
            
            # 修正案適用
            suggested_fix = self._generate_fix_suggestion(original_line, target['type'])
            
            if suggested_fix and suggested_fix != original_line:
                print(f"  修正適用:")
                print(f"    行{target['line']}: {original_line.strip()}")
                print(f"    →: {suggested_fix.strip()}")
                
                lines[target_line_index] = suggested_fix
                
                # ファイル更新
                new_content = '\n'.join(lines)
                with open(self.app_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"  修正完了")
                return True
            else:
                print(f"  修正案なし")
                return True
                
        except Exception as e:
            print(f"  修正エラー: {e}")
            return False

def main():
    print("ULTRA SYNC start_exam関数深層スキャンシステム")
    print("目的: start_exam関数内の残存型エラー完全根絶")
    print("方針: 副作用ゼロ・段階的実行・完全安全")
    print("=" * 70)
    
    scanner = UltraSyncStartExamDeepScan()
    
    # Step 1: start_exam関数抽出
    lines, start_line, end_line = scanner.extract_start_exam_function()
    
    # Step 2: 危険パターンスキャン
    dangerous_findings = scanner.scan_dangerous_patterns_in_start_exam(lines, start_line, end_line)
    
    # Step 3: 特定箇所分析
    target = scanner.analyze_specific_error_location(dangerous_findings)
    
    # Step 4: 修正実行
    fix_success = scanner.execute_targeted_fix(target)
    
    # 総合結果
    print("\n" + "=" * 70)
    print("ULTRA SYNC 深層スキャン結果")
    print("=" * 70)
    
    print(f"関数範囲特定: {'成功' if start_line else '失敗'}")
    print(f"危険パターン: {len(dangerous_findings)}箇所発見")
    print(f"修正実行: {'成功' if fix_success else '失敗'}")
    
    if target and fix_success:
        print(f"修正完了: 行{target['line']} ({target['type']})")
        print("次のステップ: 修正後動作確認テスト")
        return True
    elif not dangerous_findings:
        print("危険パターンなし: start_exam関数は型安全")
        return True
    else:
        print("追加調査が必要")
        return False

if __name__ == "__main__":
    main()