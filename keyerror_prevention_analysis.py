# -*- coding: utf-8 -*-
"""
ULTRA SYNC KeyError防止分析レポート生成
副作用なし・読み取り専用での詳細分析
"""

import re
import os

def analyze_keyerror_risks():
    """KeyErrorリスク箇所の詳細分析"""
    print('ULTRA SYNC KeyError防止分析開始')
    print('=' * 60)
    
    app_py_path = 'rccm-quiz-app/app.py'
    
    if not os.path.exists(app_py_path):
        print('エラー: app.py が見つかりません')
        return
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 危険パターンの分析
    high_risk_patterns = [
        (r"session\['([^']+)'\](?!\s*=)", "直接参照"),
        (r"session\['([^']+)'\]\['([^']+)'\]", "ネストアクセス"),
        (r"session\['([^']+)'\]\[(\w+)\]", "動的キーアクセス"),
    ]
    
    risk_findings = []
    
    for line_no, line in enumerate(lines, 1):
        line = line.strip()
        
        for pattern, risk_type in high_risk_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                # 安全なチェックが同じ行にあるかを確認
                safe_checks = [
                    'in session',
                    'session.get(',
                    'if session',
                    'try:',
                    'except KeyError',
                    'except Exception'
                ]
                
                is_safe = any(check in line for check in safe_checks)
                
                risk_findings.append({
                    'line_no': line_no,
                    'line': line,
                    'risk_type': risk_type,
                    'session_key': match.group(1) if match.groups() else 'unknown',
                    'is_safe': is_safe,
                    'severity': 'LOW' if is_safe else 'HIGH'
                })
    
    # 重要度別に分類
    high_risk = [f for f in risk_findings if f['severity'] == 'HIGH']
    low_risk = [f for f in risk_findings if f['severity'] == 'LOW']
    
    print(f'総検出箇所: {len(risk_findings)}')
    print(f'高リスク: {len(high_risk)}')
    print(f'低リスク: {len(low_risk)}')
    
    print('\n=== 高リスク箇所（修正必要）===')
    for i, finding in enumerate(high_risk[:20]):  # 上位20件
        print(f'{i+1}. 行{finding["line_no"]}: {finding["risk_type"]}')
        print(f'   キー: {finding["session_key"]}')
        print(f'   コード: {finding["line"][:80]}...')
        print()
    
    # セッションキー別の使用頻度分析
    key_usage = {}
    for finding in risk_findings:
        key = finding['session_key']
        if key not in key_usage:
            key_usage[key] = {'total': 0, 'high_risk': 0}
        key_usage[key]['total'] += 1
        if finding['severity'] == 'HIGH':
            key_usage[key]['high_risk'] += 1
    
    print('\n=== セッションキー使用頻度（リスク順）===')
    sorted_keys = sorted(key_usage.items(), 
                        key=lambda x: x[1]['high_risk'], 
                        reverse=True)
    
    for key, usage in sorted_keys[:15]:  # 上位15キー
        print(f'{key}: 総使用{usage["total"]}回 (高リスク{usage["high_risk"]}回)')
    
    # 修正優先度付けのための推奨事項
    print('\n=== ULTRA SYNC 修正推奨事項 ===')
    print('1. 最優先修正箇所:')
    
    critical_keys = [key for key, usage in sorted_keys 
                    if usage['high_risk'] >= 3][:5]
    
    for key in critical_keys:
        print(f'   - session[\'{key}\'] (高リスク{key_usage[key]["high_risk"]}箇所)')
    
    print('\n2. 推奨修正パターン:')
    print('   session[\'key\'] → session.get(\'key\', default_value)')
    print('   session[\'key\'][\'nested\'] → session.get(\'key\', {}).get(\'nested\', default)')
    
    print('\n3. 段階的修正計画:')
    print('   段階1: 最も使用頻度の高いキー（5個）')
    print('   段階2: 中頻度キー（10個）')
    print('   段階3: 残りの低頻度キー')
    
    return {
        'total_findings': len(risk_findings),
        'high_risk_count': len(high_risk),
        'critical_keys': critical_keys,
        'high_risk_lines': [f['line_no'] for f in high_risk[:20]]
    }

if __name__ == '__main__':
    try:
        os.chdir('C:/Users/ABC/Desktop/rccm-quiz-app')
        result = analyze_keyerror_risks()
        print(f'\n分析完了: {result["total_findings"]}箇所検出')
        print(f'修正必要: {result["high_risk_count"]}箇所')
    except Exception as e:
        print(f'分析エラー: {e}')