#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ ULTRA SYNC 残存エラー狩り
まだ修正されていない型エラー箇所を完全特定
副作用ゼロ保証・段階的実行
"""

import re
from datetime import datetime

class UltraSyncRemainingErrorHunt:
    def __init__(self):
        self.app_file = 'rccm-quiz-app/app.py'
        
    def hunt_remaining_dangerous_patterns(self):
        """残存する危険パターンの完全捕獲"""
        print("🛡️ ULTRA SYNC 残存エラー完全捕獲")
        print(f"⏰ 実行時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("🎯 目的: 未修正の型エラー箇所を完全特定")
        print("=" * 60)
        
        try:
            # Step 1: ファイル読み取り
            print("\nStep 1: app.pyファイルの解析")
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            print(f"  総行数: {len(lines)}")
            
            # Step 2: 危険パターンの精密検索
            print("\nStep 2: 危険パターンの精密検索")
            
            dangerous_patterns = [
                {
                    'name': '直接比較（型チェックなし）',
                    'pattern': r"session\.get\(['\"]exam_current['\"][^)]*\)\s*([><=!]+)\s*\w+",
                    'exclude': ['isinstance', 'get_exam_current_safe', 'int(', 'try:', 'except:']
                },
                {
                    'name': '直接算術演算（型チェックなし）',
                    'pattern': r"session\.get\(['\"]exam_current['\"][^)]*\)\s*[+\-*/]\s*\d+",
                    'exclude': ['isinstance', 'get_exam_current_safe', 'int(']
                },
                {
                    'name': '型チェックなし変数代入後の危険使用',
                    'pattern': r"(\w+)\s*=\s*session\.get\(['\"]exam_current['\"][^)]*\).*\n.*\1\s*[><=!+\-*/]",
                    'exclude': ['isinstance', 'get_exam_current_safe']
                }
            ]
            
            found_patterns = []
            
            for pattern_info in dangerous_patterns:
                pattern = pattern_info['pattern']
                excludes = pattern_info['exclude']
                name = pattern_info['name']
                
                print(f"\n  🔍 検索: {name}")
                
                matches = []
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # 除外条件チェック
                        line_safe = any(exclude in line for exclude in excludes)
                        
                        # 前後3行もチェック（コンテキスト確認）
                        context_lines = []
                        for j in range(max(0, i-3), min(len(lines), i+3)):
                            context_lines.append(lines[j])
                        context = '\n'.join(context_lines)
                        context_safe = any(exclude in context for exclude in excludes)
                        
                        if not (line_safe or context_safe):
                            matches.append({
                                'line': i,
                                'content': line.strip(),
                                'pattern': name,
                                'context': context
                            })
                
                print(f"    発見: {len(matches)}箇所")
                for match in matches[:3]:  # 上位3件表示
                    print(f"      行{match['line']}: {match['content'][:60]}...")
                
                found_patterns.extend(matches)
            
            return found_patterns
            
        except Exception as e:
            print(f"  🚨 捕獲エラー: {e}")
            return []
    
    def prioritize_fixes(self, patterns):
        """修正優先度の決定"""
        print(f"\nStep 3: 修正優先度の決定")
        
        if not patterns:
            print("  ✅ 修正対象なし")
            return []
        
        # 優先度付け
        for pattern in patterns:
            content = pattern['content'].lower()
            line = pattern['line']
            
            # 優先度決定ロジック
            if any(op in content for op in ['>= len(', '< len(', '== len(']):
                pattern['priority'] = 'critical'
                pattern['risk'] = 'very_high'
            elif any(op in content for op in ['>=', '<=', '>', '<']):
                pattern['priority'] = 'high' 
                pattern['risk'] = 'high'
            elif any(op in content for op in ['==', '!=']):
                pattern['priority'] = 'medium'
                pattern['risk'] = 'medium'
            else:
                pattern['priority'] = 'low'
                pattern['risk'] = 'low'
            
            # exam関数内は最優先
            if 4000 <= line <= 6500:  # exam関数の推定範囲
                if pattern['priority'] == 'high':
                    pattern['priority'] = 'critical'
                elif pattern['priority'] == 'medium':
                    pattern['priority'] = 'high'
        
        # 優先度順ソート
        patterns.sort(key=lambda x: {
            'critical': 0, 'high': 1, 'medium': 2, 'low': 3
        }[x['priority']])
        
        print(f"  📊 優先度付け完了:")
        priority_counts = {}
        for p in patterns:
            priority_counts[p['priority']] = priority_counts.get(p['priority'], 0) + 1
        
        for priority, count in priority_counts.items():
            print(f"    {priority}: {count}箇所")
        
        return patterns
    
    def create_next_fix_plan(self, prioritized_patterns):
        """次の修正計画の作成"""
        print(f"\nStep 4: 次修正計画の作成")
        
        if not prioritized_patterns:
            print("  ✅ 修正計画なし（修正対象なし）")
            return None
        
        # 最優先の1箇所のみ選択
        next_target = prioritized_patterns[0]
        
        fix_plan = {
            'target_line': next_target['line'],
            'target_content': next_target['content'],
            'priority': next_target['priority'],
            'risk_level': next_target['risk'],
            'safety_measures': [
                '修正前バックアップ作成',
                '単一行のみ修正',
                '構文チェック実行',
                '動作確認テスト',
                '副作用チェック'
            ],
            'rollback_plan': 'バックアップからの即座復旧'
        }
        
        print(f"  🎯 次修正対象:")
        print(f"    行番号: {fix_plan['target_line']}")
        print(f"    優先度: {fix_plan['priority']}")
        print(f"    リスク: {fix_plan['risk_level']}")
        print(f"    内容: {fix_plan['target_content'][:50]}...")
        
        return fix_plan
    
    def execute_safe_backup_for_next_fix(self):
        """次修正用安全バックアップ"""
        print(f"\nStep 5: 次修正用安全バックアップ")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.app_file}.backup_hunt_{timestamp}"
            
            with open(self.app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ バックアップ作成: {backup_path}")
            print(f"  📊 ファイルサイズ: {len(content)} 文字")
            
            return True, backup_path
            
        except Exception as e:
            print(f"  🚨 バックアップエラー: {e}")
            return False, None

def main():
    print("🛡️ ULTRA SYNC 残存エラー完全捕獲システム")
    print("🎯 目的: 型エラー箇所の完全特定と次修正計画")
    print("⚡ 方針: 副作用ゼロ・段階的実行・完全安全")
    print("=" * 70)
    
    hunter = UltraSyncRemainingErrorHunt()
    
    # Step 1-2: 残存パターン捕獲
    remaining_patterns = hunter.hunt_remaining_dangerous_patterns()
    
    # Step 3: 優先度付け
    prioritized = hunter.prioritize_fixes(remaining_patterns)
    
    # Step 4: 次修正計画
    fix_plan = hunter.create_next_fix_plan(prioritized)
    
    # Step 5: バックアップ作成
    backup_success, backup_path = hunter.execute_safe_backup_for_next_fix() if fix_plan else (False, None)
    
    # 総合結果
    print("\n" + "=" * 70)
    print("🛡️ ULTRA SYNC 残存エラー捕獲結果")
    print("=" * 70)
    
    print(f"🔍 発見パターン: {len(remaining_patterns)}箇所")
    print(f"📊 優先度付け: {'完了' if prioritized else '未実行'}")
    print(f"🎯 次修正計画: {'作成済み' if fix_plan else '対象なし'}")
    print(f"🛡️ バックアップ: {'作成済み' if backup_success else '未作成'}")
    
    if fix_plan and backup_success:
        print(f"\n🚀 ULTRA SYNC 次修正準備完了")
        print(f"🎯 対象: 行{fix_plan['target_line']} ({fix_plan['priority']}優先度)")
        print(f"🛡️ バックアップ: {backup_path}")
        print(f"⚠️  重要: 単一箇所修正→テスト→確認のサイクル厳守")
        return True, fix_plan
    elif not remaining_patterns:
        print(f"\n✅ ULTRA SYNC 捕獲完了")
        print(f"🎉 修正対象なし - 型エラー根絶完了の可能性")
        return True, None
    else:
        print(f"\n⚠️  ULTRA SYNC 準備未完了")
        print(f"📋 バックアップ作成後に次修正実行")
        return False, fix_plan

if __name__ == "__main__":
    main()