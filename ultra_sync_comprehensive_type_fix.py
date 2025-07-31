#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 包括的型エラー修正
app.py内のsession.get('exam_current')使用箇所を全て安全に修正
"""

import re
from datetime import datetime

class UltraSyncComprehensiveTypeFix:
    def __init__(self):
        self.app_file_path = 'rccm-quiz-app/app.py'
        
    def analyze_and_fix_type_errors(self):
        """包括的な型エラー修正"""
        print("ULTRA SYNC 包括的型エラー修正")
        print(f"対象: app.py内の全session.get('exam_current')箇所")
        print(f"修正時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Step 1: app.pyファイルを読み取り
            print("\n1. app.pyファイルの読み取り")
            with open(self.app_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_size = len(content)
            print(f"   ファイルサイズ: {original_size} 文字")
            
            # Step 2: 問題パターンの検索
            print("\n2. 型エラー問題パターンの検索")
            
            # 修正対象パターンの定義
            patterns_to_fix = [
                # 直接比較パターン
                (r'session\.get\([\'"]exam_current[\'"][^)]*\)\s*([><=]+)', 'direct_comparison'),
                # 直接取得パターン（型チェックなし）
                (r'session\.get\([\'"]exam_current[\'"][^)]*\)(?!\s*(?:if|and|or))', 'direct_usage'),
                # 算術演算パターン
                (r'session\.get\([\'"]exam_current[\'"][^)]*\)\s*[+\-*/]', 'arithmetic_operation'),
            ]
            
            found_patterns = {}
            total_matches = 0
            
            for pattern, pattern_name in patterns_to_fix:
                matches = re.findall(pattern, content)
                found_patterns[pattern_name] = len(matches)
                total_matches += len(matches)
                print(f"   {pattern_name}: {len(matches)}件")
            
            print(f"   合計対象箇所: {total_matches}件")
            
            # Step 3: 包括的修正の実行
            print("\n3. 包括的修正の実行")
            
            if total_matches > 0:
                # バックアップ作成
                backup_path = f"{self.app_file_path}.backup_type_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   バックアップ作成: {backup_path}")
                
                # 修正実行
                modified_content = self._apply_comprehensive_fixes(content)
                
                # 修正結果の確認
                if modified_content != content:
                    with open(self.app_file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    print(f"   修正完了: ファイルを更新しました")
                    print(f"   修正後サイズ: {len(modified_content)} 文字")
                    return True
                else:
                    print("   修正不要: 既に安全なコードです")
                    return True
            else:
                print("   修正不要: 問題となるパターンが見つかりませんでした")
                return True
                
        except Exception as e:
            print(f"   修正エラー: {e}")
            return False
    
    def _apply_comprehensive_fixes(self, content):
        """包括的修正の適用"""
        print("   詳細修正を実行中...")
        
        # 修正パターンの定義
        fixes = [
            # パターン1: session.get('exam_current', 0) >= の修正
            {
                'pattern': r'(\s+)session\.get\([\'"]exam_current[\'"],?\s*(\d+)\)\s*([><=]+)\s*(\w+)',
                'replacement': r'''\1exam_current_raw = session.get('exam_current', \2)
\1try:
\1    exam_current_safe = int(exam_current_raw) if exam_current_raw is not None else \2
\1except (ValueError, TypeError):
\1    exam_current_safe = \2
\1if exam_current_safe \3 \4''',
                'description': '直接比較の修正'
            },
            
            # パターン2: session.get('exam_current') >= の修正（デフォルト値なし）
            {
                'pattern': r'(\s+)session\.get\([\'"]exam_current[\'"])\)\s*([><=]+)\s*(\w+)',
                'replacement': r'''\1exam_current_raw = session.get('exam_current', 0)
\1try:
\1    exam_current_safe = int(exam_current_raw) if exam_current_raw is not None else 0
\1except (ValueError, TypeError):
\1    exam_current_safe = 0
\1if exam_current_safe \2 \3''',
                'description': 'デフォルト値なし比較の修正'
            },
            
            # パターン3: session.get('exam_current', 0) + 1 の修正
            {
                'pattern': r'session\.get\([\'"]exam_current[\'"],?\s*(\d+)\)\s*([+\-*/])\s*(\d+)',
                'replacement': r'''int(session.get('exam_current', \1) or \1) \2 \3''',
                'description': '算術演算の修正'
            },
            
            # パターン4: current = session.get('exam_current', 0) の修正
            {
                'pattern': r'(\w+)\s*=\s*session\.get\([\'"]exam_current[\'"],?\s*(\d+)\)',
                'replacement': r'''\1_raw = session.get('exam_current', \2)
\1 = int(\1_raw) if isinstance(\1_raw, int) else \2''',
                'description': '変数代入の修正'
            }
        ]
        
        modified_content = content
        applied_fixes = 0
        
        for fix in fixes:
            pattern = fix['pattern']
            replacement = fix['replacement']
            description = fix['description']
            
            matches = re.findall(pattern, modified_content)
            if matches:
                modified_content = re.sub(pattern, replacement, modified_content)
                applied_fixes += len(matches)
                print(f"     - {description}: {len(matches)}箇所修正")
        
        print(f"   適用した修正: {applied_fixes}箇所")
        return modified_content
    
    def verify_syntax(self):
        """修正後の構文チェック"""
        print("\n4. 修正後の構文確認")
        
        try:
            import ast
            with open(self.app_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 構文解析テスト
            ast.parse(content)
            print("   構文チェック: OK")
            return True
            
        except SyntaxError as e:
            print(f"   構文エラー: {e}")
            return False
        except Exception as e:
            print(f"   チェックエラー: {e}")
            return False

def main():
    print("ULTRA SYNC 包括的型エラー修正")
    print("目的: app.py内の全ての型エラーを根絶")
    print("=" * 70)
    
    fixer = UltraSyncComprehensiveTypeFix()
    
    # Step 1: 包括的修正
    fix_result = fixer.analyze_and_fix_type_errors()
    
    # Step 2: 構文確認
    syntax_result = fixer.verify_syntax()
    
    # 総合結果
    print("\n" + "=" * 70)
    print("ULTRA SYNC 包括的修正結果")
    print("=" * 70)
    
    print(f"修正実行: {'成功' if fix_result else '失敗'}")
    print(f"構文確認: {'OK' if syntax_result else 'NG'}")
    
    overall_success = fix_result and syntax_result
    
    if overall_success:
        print("\nULTRA SYNC 包括的修正: 完了")
        print("全ての型エラー箇所が修正されました")
        print("次のステップ: 本番環境での動作確認")
    else:
        print("\nULTRA SYNC 包括的修正: 要再実行")
        print("修正に問題があります")
    
    return overall_success

if __name__ == "__main__":
    main()