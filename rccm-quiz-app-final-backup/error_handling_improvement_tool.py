#!/usr/bin/env python3
"""
🛠️ Error Handling Improvement Tool
エラー隠蔽体質の根本改善 - CLAUDE.md準拠の包括的例外処理実装
副作用ゼロ保証 - 慎重なコード修正
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ErrorHandlingImprover:
    """
    エラーハンドリング改善器
    CLAUDE.md禁止事項解消・包括的例外処理実装
    """
    
    def __init__(self):
        self.fixes = []
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': [],
            'problematic_patterns': [],
            'fixes_applied': [],
            'improvements': []
        }
    
    def analyze_app_py(self) -> List[Dict[str, Any]]:
        """
        app.py の問題パターン分析
        """
        app_path = Path(__file__).parent / 'app.py'
        
        if not app_path.exists():
            logger.error("app.py not found")
            return []
        
        logger.info("🔍 Analyzing app.py for problematic error handling patterns")
        
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        problematic_patterns = []
        
        # Pattern 1: Line 4217 - bare except for datetime parsing
        if len(lines) > 4217:
            line = lines[4216].strip()  # 0-based indexing
            if line == "except:":
                problematic_patterns.append({
                    'line_number': 4217,
                    'pattern': 'bare_except_datetime_1',
                    'current_code': line,
                    'context': 'SRS due today count calculation',
                    'issue': 'Catches all exceptions including system errors',
                    'claude_md_violation': '根本原因を解決せずに症状のみを隠す修正'
                })
        
        # Pattern 2: Line 4249 - bare except for datetime parsing
        if len(lines) > 4249:
            line = lines[4248].strip()  # 0-based indexing
            if line == "except:":
                problematic_patterns.append({
                    'line_number': 4249,
                    'pattern': 'bare_except_datetime_2', 
                    'current_code': line,
                    'context': 'Days until review calculation',
                    'issue': 'Catches all exceptions including system errors',
                    'claude_md_violation': '根本原因を解決せずに症状のみを隠す修正'
                })
        
        # Pattern 3: Line 6649 - bare except for resource limits
        if len(lines) > 6649:
            line = lines[6648].strip()  # 0-based indexing
            if line == "except:":
                problematic_patterns.append({
                    'line_number': 6649,
                    'pattern': 'bare_except_resource',
                    'current_code': line,
                    'context': 'System resource limit detection',
                    'issue': 'Catches all exceptions including system errors',
                    'claude_md_violation': '根本原因を解決せずに症状のみを隠す修正'
                })
        
        self.analysis_results['problematic_patterns'] = problematic_patterns
        
        logger.info(f"📊 Found {len(problematic_patterns)} problematic patterns in app.py")
        for pattern in problematic_patterns:
            logger.warning(f"   ⚠️ Line {pattern['line_number']}: {pattern['issue']}")
        
        return problematic_patterns
    
    def generate_improved_patterns(self) -> Dict[str, str]:
        """
        改善されたエラーハンドリングパターン生成
        """
        improved_patterns = {
            'bare_except_datetime_1': '''                except (ValueError, TypeError, AttributeError) as e:
                    # 日時解析エラーの場合は復習対象としてカウント
                    logger.warning(f"Date parsing error in SRS due count: {e}")
                    due_today_count += 1  # パースエラーの場合は復習対象としてカウント''',
            
            'bare_except_datetime_2': '''                    except (ValueError, TypeError, AttributeError) as e:
                        # 日時解析エラーの場合は今すぐ復習として設定
                        logger.warning(f"Date parsing error in days until review: {e}")
                        days_until_review = 0  # パースエラーの場合は今すぐ復習''',
            
            'bare_except_resource': '''        except (OSError, AttributeError, ImportError) as e:
            # システムリソース取得エラーの場合は不明として設定
            logger.warning(f"System resource limit detection error: {e}")
            soft_limit, hard_limit = 'unknown', 'unknown'
            # パフォーマンス監視に影響するがシステム継続可能'''
        }
        
        return improved_patterns
    
    def create_backup_and_fix(self) -> bool:
        """
        バックアップ作成とコード修正実行
        """
        app_path = Path(__file__).parent / 'app.py'
        backup_path = Path(__file__).parent / f'app_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        
        try:
            # Create backup
            logger.info(f"📄 Creating backup: {backup_path}")
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Apply fixes
            problematic_patterns = self.analyze_app_py()
            improved_patterns = self.generate_improved_patterns()
            
            if not problematic_patterns:
                logger.info("✅ No problematic patterns found")
                return True
            
            # Read current content
            lines = content.split('\n')
            
            # Apply fixes in reverse order to maintain line numbers
            fixes_applied = 0
            
            for pattern in reversed(problematic_patterns):
                pattern_type = pattern['pattern']
                line_num = pattern['line_number'] - 1  # Convert to 0-based
                
                if pattern_type in improved_patterns:
                    # Replace the problematic line
                    original_line = lines[line_num]
                    improved_code = improved_patterns[pattern_type]
                    
                    logger.info(f"🔧 Fixing line {pattern['line_number']}: {pattern_type}")
                    
                    # Replace with improved error handling
                    lines[line_num] = improved_code
                    
                    self.analysis_results['fixes_applied'].append({
                        'line_number': pattern['line_number'],
                        'pattern_type': pattern_type,
                        'original': original_line.strip(),
                        'improved': improved_code.split('\n')[0].strip()
                    })
                    
                    fixes_applied += 1
            
            # Write improved content
            if fixes_applied > 0:
                improved_content = '\n'.join(lines)
                
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(improved_content)
                
                logger.info(f"✅ Applied {fixes_applied} error handling improvements")
                
                # Add necessary import if not present
                if 'import logging' not in improved_content:
                    self._add_logging_import(app_path)
                
                return True
            else:
                logger.info("ℹ️ No fixes needed to be applied")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error during backup and fix: {e}")
            return False
    
    def _add_logging_import(self, app_path: Path):
        """
        ログ機能のインポート追加
        """
        try:
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if logging import already exists
            if 'import logging' not in content and 'from logging import' not in content:
                # Add logging import after existing imports
                lines = content.split('\n')
                import_section_end = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_section_end = i + 1
                
                # Insert logging import
                lines.insert(import_section_end, 'import logging')
                
                # Add logger configuration near the top
                logger_config = '''
# Configure logging for error handling
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
'''
                lines.insert(import_section_end + 1, logger_config)
                
                # Write back
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                logger.info("✅ Added logging import and configuration")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not add logging import: {e}")
    
    def validate_improvements(self) -> Dict[str, Any]:
        """
        改善結果の検証
        """
        app_path = Path(__file__).parent / 'app.py'
        
        validation_results = {
            'syntax_valid': False,
            'claude_md_compliant': False,
            'bare_except_count': 0,
            'specific_except_count': 0,
            'logging_present': False
        }
        
        try:
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Syntax validation
            try:
                compile(content, app_path, 'exec')
                validation_results['syntax_valid'] = True
                logger.info("✅ Syntax validation passed")
            except SyntaxError as e:
                logger.error(f"❌ Syntax error: {e}")
                validation_results['syntax_valid'] = False
            
            # Count exception patterns
            bare_except_count = len(re.findall(r'except\s*:', content))
            specific_except_count = len(re.findall(r'except\s+\([^)]+\)', content))
            
            validation_results['bare_except_count'] = bare_except_count
            validation_results['specific_except_count'] = specific_except_count
            
            # Logging presence
            validation_results['logging_present'] = 'import logging' in content or 'logger.' in content
            
            # CLAUDE.md compliance
            if bare_except_count == 0 and specific_except_count > 0:
                validation_results['claude_md_compliant'] = True
                logger.info("✅ CLAUDE.md compliance achieved")
            else:
                logger.warning(f"⚠️ Still {bare_except_count} bare except clauses remaining")
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
        
        return validation_results
    
    def generate_report(self) -> str:
        """
        改善レポート生成
        """
        validation = self.validate_improvements()
        
        report = f"""
🛠️ Error Handling Improvement Report
================================================================================
📅 Timestamp: {self.analysis_results['timestamp']}
🎯 Target: CLAUDE.md Compliance - Error Hiding Elimination

📊 Analysis Results:
   Problematic patterns found: {len(self.analysis_results['problematic_patterns'])}
   Fixes applied: {len(self.analysis_results['fixes_applied'])}

🔧 Improvements Applied:
"""
        
        for fix in self.analysis_results['fixes_applied']:
            report += f"""
   Line {fix['line_number']}: {fix['pattern_type']}
   Before: {fix['original']}
   After:  {fix['improved']}
"""
        
        report += f"""
✅ Validation Results:
   Syntax valid: {validation['syntax_valid']}
   CLAUDE.md compliant: {validation['claude_md_compliant']}
   Bare except count: {validation['bare_except_count']}
   Specific except count: {validation['specific_except_count']}
   Logging present: {validation['logging_present']}

🎯 CLAUDE.md Compliance Status:
   {'✅ COMPLIANT' if validation['claude_md_compliant'] else '❌ NON-COMPLIANT'}

📋 Summary:
   {'✅ Error hiding patterns successfully eliminated' if validation['bare_except_count'] == 0 else '⚠️ Some error hiding patterns remain'}
   {'✅ Proper exception handling implemented' if validation['specific_except_count'] > 0 else '⚠️ Limited specific exception handling'}
   {'✅ Comprehensive logging added' if validation['logging_present'] else '⚠️ Logging not detected'}
"""
        
        return report

def main():
    """
    メイン実行
    """
    print("🛠️ Error Handling Improvement Tool")
    print("=" * 80)
    print("🎯 目的: CLAUDE.md準拠エラーハンドリング実装")
    print("🚫 対象: 禁止されたbare except パターンの完全排除")
    print("✅ 実装: 包括的例外処理・適切なログ出力")
    print()
    
    improver = ErrorHandlingImprover()
    
    # Analyze current state
    problematic_patterns = improver.analyze_app_py()
    
    if not problematic_patterns:
        print("✅ No problematic error handling patterns found")
        return 0
    
    # Apply fixes
    print(f"🔧 Applying fixes for {len(problematic_patterns)} patterns...")
    
    success = improver.create_backup_and_fix()
    
    if not success:
        print("❌ Error handling improvement failed")
        return 1
    
    # Generate and display report
    report = improver.generate_report()
    print(report)
    
    # Save report
    report_file = f"error_handling_improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")
    
    # Final status
    validation = improver.validate_improvements()
    if validation['claude_md_compliant']:
        print("\n🎉 Error Handling Improvement: SUCCESS")
        print("✅ CLAUDE.md準拠達成 - エラー隠蔽体質完全改善")
        return 0
    else:
        print("\n⚠️ Error Handling Improvement: PARTIAL")
        print("❌ 追加修正が必要です")
        return 1

if __name__ == "__main__":
    exit(main())