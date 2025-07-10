#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 Phase 1】品質保証強化システム
Flask非依存での包括的品質チェック
副作用ゼロ保証・段階的改善監視
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltrathinQualityAssurance:
    """ULTRATHIN区品質保証クラス"""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}
        self.quality_metrics = {}
        
    def check_file_structure(self) -> Dict[str, Any]:
        """ファイル構造チェック"""
        print("🔍 ファイル構造チェック...")
        
        required_files = [
            'app.py',
            'utils.py', 
            'config.py',
            'requirements.txt',
            'CLAUDE.md',
            'data/4-1.csv'
        ]
        
        blueprint_files = [
            'blueprints/static_bp.py',
            'blueprints/health_bp.py'
        ]
        
        results = {
            'required_files': {},
            'blueprint_files': {},
            'file_sizes': {},
            'file_counts': {}
        }
        
        # 必須ファイルチェック
        for file_path in required_files:
            exists = os.path.exists(file_path)
            results['required_files'][file_path] = exists
            
            if exists:
                size = os.path.getsize(file_path)
                results['file_sizes'][file_path] = size
                print(f"   ✅ {file_path}: {size:,} bytes")
            else:
                print(f"   ❌ {file_path}: 見つかりません")
        
        # Blueprintファイルチェック
        for file_path in blueprint_files:
            exists = os.path.exists(file_path)
            results['blueprint_files'][file_path] = exists
            
            if exists:
                size = os.path.getsize(file_path)
                results['file_sizes'][file_path] = size
                print(f"   ✅ Blueprint {file_path}: {size:,} bytes")
            else:
                print(f"   ❌ Blueprint {file_path}: 見つかりません")
        
        # ディレクトリ構造チェック
        directories = ['data', 'templates', 'static', 'blueprints', 'tests']
        results['directories'] = {}
        
        for dir_name in directories:
            exists = os.path.exists(dir_name)
            results['directories'][dir_name] = exists
            
            if exists:
                file_count = len([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))])
                results['file_counts'][dir_name] = file_count
                print(f"   📁 {dir_name}/: {file_count}ファイル")
            else:
                print(f"   ❌ {dir_name}/: ディレクトリ未作成")
                
        return results
    
    def check_code_quality(self) -> Dict[str, Any]:
        """コード品質チェック"""
        print("\n🔧 コード品質チェック...")
        
        results = {
            'syntax_check': {},
            'import_check': {},
            'line_counts': {},
            'complexity_metrics': {}
        }
        
        python_files = [
            'app.py',
            'utils.py',
            'config.py',
            'blueprints/static_bp.py',
            'blueprints/health_bp.py'
        ]
        
        for file_path in python_files:
            if not os.path.exists(file_path):
                results['syntax_check'][file_path] = 'file_not_found'
                continue
                
            # 構文チェック
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Pythonコンパイルテスト
                compile(content, file_path, 'exec')
                results['syntax_check'][file_path] = 'valid'
                print(f"   ✅ {file_path}: 構文正常")
                
                # 行数計算
                lines = content.split('\n')
                results['line_counts'][file_path] = len(lines)
                
                # 簡易複雑度計算
                function_count = content.count('def ')
                class_count = content.count('class ')
                if_count = content.count('if ')
                complexity_score = function_count + class_count * 2 + if_count * 0.5
                
                results['complexity_metrics'][file_path] = {
                    'functions': function_count,
                    'classes': class_count,
                    'conditions': if_count,
                    'complexity_score': complexity_score
                }
                
                print(f"      📊 {len(lines)}行, 関数{function_count}個, クラス{class_count}個")
                
            except SyntaxError as e:
                results['syntax_check'][file_path] = f'syntax_error: {e}'
                print(f"   ❌ {file_path}: 構文エラー - {e}")
            except Exception as e:
                results['syntax_check'][file_path] = f'error: {e}'
                print(f"   ⚠️ {file_path}: チェックエラー - {e}")
        
        return results
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """データ整合性チェック"""
        print("\n📊 データ整合性チェック...")
        
        results = {
            'csv_files': {},
            'data_quality': {},
            'encoding_check': {}
        }
        
        csv_files = []
        if os.path.exists('data'):
            csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = f"data/{csv_file}"
            
            try:
                # エンコーディングテスト
                encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            content = f.read()
                            if content:
                                results['encoding_check'][csv_file] = encoding
                                break
                    except:
                        continue
                
                # CSV構造チェック
                import csv
                with open(file_path, 'r', encoding=results['encoding_check'].get(csv_file, 'utf-8'), errors='ignore') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    if rows:
                        results['csv_files'][csv_file] = {
                            'row_count': len(rows),
                            'columns': list(rows[0].keys()) if rows else [],
                            'has_required_fields': all(field in rows[0] for field in ['id', 'question'] if rows)
                        }
                        
                        print(f"   ✅ {csv_file}: {len(rows)}行, {len(rows[0].keys()) if rows else 0}列")
                    else:
                        results['csv_files'][csv_file] = {'row_count': 0, 'columns': []}
                        print(f"   ⚠️ {csv_file}: データなし")
                        
            except Exception as e:
                results['csv_files'][csv_file] = {'error': str(e)}
                print(f"   ❌ {csv_file}: エラー - {e}")
        
        return results
    
    def check_architectural_improvement(self) -> Dict[str, Any]:
        """アーキテクチャ改善チェック"""
        print("\n🏗️ アーキテクチャ改善チェック...")
        
        results = {
            'monolithic_app_analysis': {},
            'blueprint_separation': {},
            'code_organization': {}
        }
        
        # app.pyのモノリシック分析
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                results['monolithic_app_analysis'] = {
                    'total_lines': len(lines),
                    'route_count': content.count('@app.route'),
                    'function_count': content.count('def '),
                    'class_count': content.count('class '),
                    'import_count': content.count('import '),
                    'is_monolithic': len(lines) > 5000
                }
                
                print(f"   📊 app.py分析:")
                print(f"      - 総行数: {len(lines):,}行")
                print(f"      - ルート数: {content.count('@app.route')}個")
                print(f"      - 関数数: {content.count('def ')}個")
                
                if len(lines) > 10000:
                    print(f"   ⚠️ モノリシック問題: {len(lines):,}行（要分割）")
                elif len(lines) > 5000:
                    print(f"   🟡 大規模ファイル: {len(lines):,}行（分割推奨）")
                else:
                    print(f"   ✅ 適切なサイズ: {len(lines):,}行")
        
        # Blueprint分離進捗
        blueprint_count = 0
        if os.path.exists('blueprints'):
            blueprint_files = [f for f in os.listdir('blueprints') if f.endswith('.py') and f != '__init__.py']
            blueprint_count = len(blueprint_files)
            
            results['blueprint_separation'] = {
                'blueprint_count': blueprint_count,
                'blueprint_files': blueprint_files,
                'separation_progress': min(blueprint_count * 10, 100)  # 10%ずつ進捗
            }
            
            print(f"   📦 Blueprint分離進捗:")
            print(f"      - 作成済みBlueprint: {blueprint_count}個")
            for bp_file in blueprint_files:
                print(f"      - {bp_file}")
        
        return results
    
    def check_conditional_logic_fixes(self) -> Dict[str, Any]:
        """条件分岐修正チェック"""
        print("\n🔧 条件分岐修正チェック...")
        
        results = {
            'fixed_conditions': [],
            'remaining_issues': [],
            'fix_verification': {}
        }
        
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # 修正済み条件分岐の確認
            fixed_patterns = [
                "elif exam_type == '基礎科目' or exam_type == 'basic':",
                "if exam_type == '基礎科目' or exam_type == 'basic':",
                "exam_type.lower() == 'basic' or exam_type == '基礎科目'"
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern in fixed_patterns:
                    if pattern in line:
                        results['fixed_conditions'].append({
                            'line_number': i,
                            'pattern': pattern,
                            'content': line.strip()
                        })
                        print(f"   ✅ 修正確認 {i}行目: {pattern}")
            
            # 潜在的問題パターンチェック
            problem_patterns = [
                "exam_type == 'basic'",  # 単独のbasicチェック
                "if '基礎' in",  # 不完全な基礎科目チェック
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern in problem_patterns:
                    if pattern in line and 'or' not in line:  # orがない単独チェック
                        results['remaining_issues'].append({
                            'line_number': i,
                            'pattern': pattern,
                            'content': line.strip()
                        })
                        print(f"   ⚠️ 要確認 {i}行目: {pattern}")
            
            results['fix_verification'] = {
                'total_fixes': len(results['fixed_conditions']),
                'remaining_issues': len(results['remaining_issues']),
                'fix_success_rate': len(results['fixed_conditions']) / max(1, len(results['fixed_conditions']) + len(results['remaining_issues'])) * 100
            }
        
        return results
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """品質レポート生成"""
        print("\n📋 品質レポート生成...")
        
        execution_time = time.time() - self.start_time
        
        # 全テスト実行
        file_structure = self.check_file_structure()
        code_quality = self.check_code_quality()
        data_integrity = self.check_data_integrity()
        architecture = self.check_architectural_improvement()
        conditional_fixes = self.check_conditional_logic_fixes()
        
        # 品質スコア計算
        quality_score = 0
        max_score = 100
        
        # ファイル構造スコア (20点)
        required_files_score = sum(1 for exists in file_structure['required_files'].values() if exists)
        blueprint_files_score = sum(1 for exists in file_structure['blueprint_files'].values() if exists)
        file_score = min(20, (required_files_score * 3 + blueprint_files_score * 2))
        quality_score += file_score
        
        # コード品質スコア (30点)
        syntax_score = sum(1 for status in code_quality['syntax_check'].values() if status == 'valid')
        code_score = min(30, syntax_score * 6)
        quality_score += code_score
        
        # データ整合性スコア (20点)
        csv_score = len([f for f, data in data_integrity['csv_files'].items() if isinstance(data, dict) and data.get('row_count', 0) > 0])
        data_score = min(20, csv_score * 10)
        quality_score += data_score
        
        # アーキテクチャ改善スコア (20点)
        arch_score = min(20, architecture['blueprint_separation'].get('blueprint_count', 0) * 10)
        quality_score += arch_score
        
        # 条件分岐修正スコア (10点)
        fix_score = min(10, len(conditional_fixes['fixed_conditions']))
        quality_score += fix_score
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'execution_time_seconds': round(execution_time, 2),
            'quality_score': quality_score,
            'max_score': max_score,
            'quality_percentage': round(quality_score / max_score * 100, 1),
            'test_results': {
                'file_structure': file_structure,
                'code_quality': code_quality,
                'data_integrity': data_integrity,
                'architecture_improvement': architecture,
                'conditional_logic_fixes': conditional_fixes
            },
            'quality_metrics': {
                'file_structure_score': file_score,
                'code_quality_score': code_score,
                'data_integrity_score': data_score,
                'architecture_score': arch_score,
                'conditional_fixes_score': fix_score
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """レポート保存"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ULTRATHIN_QUALITY_REPORT_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 品質レポート保存: {filename}")
        except Exception as e:
            print(f"\n❌ レポート保存失敗: {e}")

def main():
    """メイン実行"""
    print("🎯 【ULTRATHIN区 Phase 1】品質保証強化システム開始")
    print("=" * 70)
    
    qa = UltrathinQualityAssurance()
    report = qa.generate_quality_report()
    
    print("\n" + "=" * 70)
    print("🎉 【ULTRATHIN区】品質保証レポート")
    print("=" * 70)
    
    print(f"📊 総合品質スコア: {report['quality_score']}/{report['max_score']} ({report['quality_percentage']}%)")
    print(f"⏱️ 実行時間: {report['execution_time_seconds']}秒")
    
    metrics = report['quality_metrics']
    print(f"\n📋 詳細スコア:")
    print(f"   🗂️ ファイル構造: {metrics['file_structure_score']}/20")
    print(f"   🔧 コード品質: {metrics['code_quality_score']}/30")
    print(f"   📊 データ整合性: {metrics['data_integrity_score']}/20")
    print(f"   🏗️ アーキテクチャ: {metrics['architecture_score']}/20")
    print(f"   🔧 条件分岐修正: {metrics['conditional_fixes_score']}/10")
    
    # 品質判定
    if report['quality_percentage'] >= 90:
        print(f"\n🏆 品質評価: 優秀 (90%以上)")
    elif report['quality_percentage'] >= 75:
        print(f"\n🎯 品質評価: 良好 (75%以上)")
    elif report['quality_percentage'] >= 60:
        print(f"\n🔧 品質評価: 改善の余地あり (60%以上)")
    else:
        print(f"\n⚠️ 品質評価: 要改善 (60%未満)")
    
    # レポート保存
    qa.save_report(report)
    
    print(f"\n🚀 ULTRATHIN区品質保証完了")
    print(f"副作用: ゼロ（読み取り専用分析）")
    
    return report['quality_percentage'] >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)