# -*- coding: utf-8 -*-
"""
ULTRA SYNC [基本機能確保-004] セッション直接アクセス段階的安全化
副作用なし・読み取り専用での詳細分析と安全な修正計画策定
"""

import re
import os
from collections import defaultdict

def analyze_session_access_patterns():
    """セッション直接アクセスパターンの詳細分析"""
    print('ULTRA SYNC [基本機能確保-004] セッション直接アクセス段階的安全化')
    print('=' * 80)
    print('副作用防止・機能アップ禁止・読み取り専用分析モード')
    print('=' * 80)
    
    app_py_path = 'rccm-quiz-app/app.py'
    
    if not os.path.exists(app_py_path):
        print('ERROR: app.py が見つかりません')
        return
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 危険パターンの検出
    risk_patterns = [
        {
            'pattern': r"session\['([^']+)'\](?!\s*=)",  # 読み取り専用アクセス
            'type': 'READ_ACCESS',
            'risk_level': 'HIGH',
            'description': 'KeyError発生の可能性'
        },
        {
            'pattern': r"session\['([^']+)'\]\['([^']+)'\]",  # ネストアクセス
            'type': 'NESTED_ACCESS', 
            'risk_level': 'CRITICAL',
            'description': '二重KeyError発生の可能性'
        },
        {
            'pattern': r"session\['([^']+)'\]\[(\w+)\]",  # 動的キーアクセス
            'type': 'DYNAMIC_ACCESS',
            'risk_level': 'CRITICAL', 
            'description': '予測不可能なKeyError'
        }
    ]
    
    # 安全パターンの確認
    safe_patterns = [
        r"session\.get\(",
        r"'[^']+'\s+in\s+session",
        r"if\s+session\s*\.",
        r"try:\s*.*session\[",
        r"except\s+KeyError"
    ]
    
    findings = []
    safe_usages = []
    
    print('\n=== セッションアクセスパターン分析 ===')
    
    for line_no, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # 危険パターンの検出
        for pattern_info in risk_patterns:
            matches = re.finditer(pattern_info['pattern'], line_content)
            for match in matches:
                # 同じ行に安全チェックがあるかを確認
                has_safe_check = any(re.search(safe_pattern, line_content) for safe_pattern in safe_patterns)
                
                finding = {
                    'line_no': line_no,
                    'line': line_content,
                    'pattern_type': pattern_info['type'],
                    'risk_level': pattern_info['risk_level'] if not has_safe_check else 'LOW',
                    'session_key': match.group(1) if match.groups() else 'unknown',
                    'has_safe_check': has_safe_check,
                    'description': pattern_info['description']
                }
                findings.append(finding)
        
        # 安全な使用パターンの検出
        for safe_pattern in safe_patterns:
            if re.search(safe_pattern, line_content):
                safe_usages.append({
                    'line_no': line_no,
                    'line': line_content,
                    'pattern': safe_pattern
                })
    
    # 結果の分析
    critical_findings = [f for f in findings if f['risk_level'] == 'CRITICAL']
    high_risk_findings = [f for f in findings if f['risk_level'] == 'HIGH']
    low_risk_findings = [f for f in findings if f['risk_level'] == 'LOW']
    
    print(f'総検出箇所: {len(findings)}')
    print(f'緊急対応必要: {len(critical_findings)}')
    print(f'高リスク: {len(high_risk_findings)}')
    print(f'低リスク: {len(low_risk_findings)}')
    print(f'安全な使用: {len(safe_usages)}')
    
    # セッションキー別の使用頻度分析
    key_usage = defaultdict(lambda: {'total': 0, 'critical': 0, 'high': 0, 'safe': 0})
    
    for finding in findings:
        key = finding['session_key']
        key_usage[key]['total'] += 1
        if finding['risk_level'] == 'CRITICAL':
            key_usage[key]['critical'] += 1
        elif finding['risk_level'] == 'HIGH':
            key_usage[key]['high'] += 1
        elif finding['has_safe_check']:
            key_usage[key]['safe'] += 1
    
    # 修正優先度順にソート
    sorted_keys = sorted(key_usage.items(), 
                        key=lambda x: (x[1]['critical'], x[1]['high']), 
                        reverse=True)
    
    print('\n=== 緊急対応必要箇所（CRITICAL）===')
    critical_count = 0
    for finding in critical_findings[:10]:  # 上位10件
        critical_count += 1
        print(f'{critical_count}. 行{finding["line_no"]}: {finding["pattern_type"]}')
        print(f'   キー: {finding["session_key"]}')
        print(f'   コード: {finding["line"][:80]}...')
        print()
    
    print('\n=== セッションキー使用頻度（リスク順）===')
    for key, usage in sorted_keys[:15]:  # 上位15キー
        total = usage['total']
        critical = usage['critical']
        high = usage['high']
        safe = usage['safe']
        
        if critical > 0 or high > 0:
            print(f'{key}: 総{total}回 (緊急{critical}, 高{high}, 安全{safe})')
    
    # 段階的修正計画の策定
    print('\n=== ULTRA SYNC 段階的修正計画 ===')
    
    # Phase 1: 緊急対応（CRITICAL）
    phase1_keys = [key for key, usage in sorted_keys if usage['critical'] > 0][:5]
    phase1_lines = [f['line_no'] for f in critical_findings[:20]]
    
    print('Phase 1: 緊急対応（副作用リスク最小化）')
    print(f'   対象キー: {len(phase1_keys)}個')
    print(f'   対象行数: {len(phase1_lines)}行')
    for key in phase1_keys[:3]:
        print(f'   - {key} ({key_usage[key]["critical"]}箇所)')
    
    # Phase 2: 高リスク対応
    phase2_keys = [key for key, usage in sorted_keys if usage['high'] >= 3 and usage['critical'] == 0][:5]
    phase2_lines = [f['line_no'] for f in high_risk_findings[:30]]
    
    print('\nPhase 2: 高リスク対応（段階的安全化）')
    print(f'   対象キー: {len(phase2_keys)}個')
    print(f'   対象行数: {len(phase2_lines)}行')
    
    # Phase 3: 残り低リスク対応
    remaining_count = len(findings) - len(critical_findings) - len(high_risk_findings)
    
    print('\nPhase 3: 残り低リスク対応（将来対応）')
    print(f'   対象箇所: {remaining_count}箇所')
    
    # 修正テンプレートの提示
    print('\n=== 安全な修正テンプレート ===')
    print('1. 基本読み取り:')
    print('   session["key"] → session.get("key", default_value)')
    print()
    print('2. ネストアクセス:')
    print('   session["key"]["nested"] → session.get("key", {}).get("nested", default)')
    print()
    print('3. 条件チェック付き:')
    print('   if "key" in session and session["key"]:')
    print('       value = session["key"]')
    
    return {
        'total_findings': len(findings),
        'critical_count': len(critical_findings),
        'high_risk_count': len(high_risk_findings),
        'phase1_keys': phase1_keys,
        'phase1_lines': phase1_lines[:10],  # 最初の10行
        'phase2_keys': phase2_keys,
        'phase2_lines': phase2_lines[:15],  # 最初の15行
        'safe_usage_count': len(safe_usages)
    }

def generate_phase1_fix_plan(analysis_result):
    """Phase 1の緊急修正計画生成"""
    print('\n' + '=' * 80)
    print('ULTRA SYNC Phase 1 緊急修正計画（副作用ゼロ保証）')
    print('=' * 80)
    
    phase1_lines = analysis_result['phase1_lines']
    phase1_keys = analysis_result['phase1_keys']
    
    print('修正対象:')
    print(f'  緊急対応行: {len(phase1_lines)}行')
    print(f'  主要キー: {len(phase1_keys)}個')
    
    print('\n修正方針:')
    print('1. 最小限の変更で最大の安全性向上')
    print('2. 既存ロジックの完全保持')
    print('3. デフォルト値の慎重な選択')
    print('4. 修正前後のテスト実行')
    
    print('\n実行手順:')
    print('1. バックアップ作成')
    print('2. Phase 1対象箇所の個別修正')
    print('3. 各修正後の動作確認')
    print('4. 全修正完了後の総合テスト')
    
    return True

if __name__ == '__main__':
    try:
        os.chdir('C:/Users/ABC/Desktop/rccm-quiz-app')
        
        print('ULTRA SYNC セッション安全化分析開始')
        analysis_result = analyze_session_access_patterns()
        
        if analysis_result:
            generate_phase1_fix_plan(analysis_result)
            
            print(f'\n分析完了:')
            print(f'  総検出: {analysis_result["total_findings"]}箇所')
            print(f'  緊急対応: {analysis_result["critical_count"]}箇所')
            print(f'  高リスク: {analysis_result["high_risk_count"]}箇所')
            print(f'  安全使用: {analysis_result["safe_usage_count"]}箇所')
            
            print('\n次のステップ: Phase 1緊急修正の実行準備完了')
    
    except Exception as e:
        print(f'分析エラー: {e}')