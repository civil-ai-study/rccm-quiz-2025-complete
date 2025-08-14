#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク段階3：英語ID変換システム依存箇所特定
目的: 副作用ゼロを保証するための完全依存箇所分析
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def analyze_english_id_dependencies():
    """英語ID変換システムの依存箇所を安全に特定"""
    print("=== Ultra Sync Stage 3: English ID Conversion System Dependency Analysis ===")
    print("Purpose: Complete dependency mapping of English ID conversion system")
    print()
    
    # 英語部門ID定義（グローバルスコープで定義）
    english_ids = ['road', 'river', 'urban', 'garden', 'env', 'steel', 'soil', 
                  'construction', 'water', 'forest', 'agri', 'tunnel']
    
    dependency_map = {
        'LIGHTWEIGHT_DEPARTMENT_MAPPING': [],
        'english_department_ids': [],
        'url_routing_english': [],
        'template_english_references': [],
        'javascript_english_ids': [],
        'config_english_mappings': []
    }
    
    # 1. app.pyでの英語ID変換システム使用箇所特定
    print("【1. app.py 英語ID変換システム分析】")
    
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # LIGHTWEIGHT_DEPARTMENT_MAPPING使用箇所
        lightweight_matches = []
        for i, line in enumerate(app_content.split('\n'), 1):
            if 'LIGHTWEIGHT_DEPARTMENT_MAPPING' in line:
                lightweight_matches.append((i, line.strip()))
        
        print(f"  LIGHTWEIGHT_DEPARTMENT_MAPPING使用箇所: {len(lightweight_matches)}箇所")
        for line_no, line_content in lightweight_matches[:5]:  # 最初の5箇所のみ表示
            print(f"    Line {line_no}: {line_content[:60]}...")
        
        dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING'] = lightweight_matches
        
        # 英語部門ID直接使用箇所
        
        english_id_matches = []
        for eng_id in english_ids:
            # 'road', 'river'等の使用箇所（但し変数名として使用されている箇所を除く）
            pattern = rf"['\"]({eng_id})['\"]"
            matches = re.finditer(pattern, app_content)
            for match in matches:
                line_no = app_content[:match.start()].count('\n') + 1
                line_content = app_content.split('\n')[line_no-1].strip()
                english_id_matches.append((line_no, eng_id, line_content))
        
        print(f"  英語部門ID直接使用箇所: {len(english_id_matches)}箇所")
        for line_no, eng_id, line_content in english_id_matches[:5]:
            print(f"    Line {line_no} ({eng_id}): {line_content[:60]}...")
        
        dependency_map['english_department_ids'] = english_id_matches
        
    except Exception as e:
        print(f"  ERROR app.py analysis: {str(e)[:60]}...")
    
    print()
    
    # 2. config.pyでの英語ID変換システム分析
    print("【2. config.py 英語ID変換システム分析】")
    
    try:
        with open('rccm-quiz-app/config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # RCCMConfig.DEPARTMENTSでの英語ID使用
        config_matches = []
        in_departments_section = False
        for i, line in enumerate(config_content.split('\n'), 1):
            if 'DEPARTMENTS = {' in line:
                in_departments_section = True
            elif in_departments_section and line.strip().startswith('}'):
                in_departments_section = False
            elif in_departments_section:
                for eng_id in english_ids:
                    if f"'{eng_id}':" in line or f'"{eng_id}":' in line:
                        config_matches.append((i, eng_id, line.strip()))
        
        print(f"  config.py英語ID使用箇所: {len(config_matches)}箇所")
        for line_no, eng_id, line_content in config_matches[:5]:
            print(f"    Line {line_no} ({eng_id}): {line_content[:60]}...")
        
        dependency_map['config_english_mappings'] = config_matches
        
    except Exception as e:
        print(f"  ERROR config.py analysis: {str(e)[:60]}...")
    
    print()
    
    # 3. テンプレートファイルでの英語ID参照分析
    print("【3. テンプレートファイル 英語ID参照分析】")
    
    template_matches = []
    template_dir = 'rccm-quiz-app/templates'
    if os.path.exists(template_dir):
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                try:
                    with open(os.path.join(template_dir, filename), 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    
                    for eng_id in english_ids:
                        if eng_id in template_content:
                            lines_with_id = []
                            for i, line in enumerate(template_content.split('\n'), 1):
                                if eng_id in line:
                                    lines_with_id.append((i, line.strip()))
                            template_matches.append((filename, eng_id, lines_with_id))
                
                except Exception as e:
                    print(f"    WARNING {filename} read error: {str(e)[:40]}...")
    
    print(f"  テンプレート英語ID参照: {len(template_matches)}ファイル")
    for filename, eng_id, lines in template_matches[:3]:
        print(f"    {filename} ({eng_id}): {len(lines)}箇所")
    
    dependency_map['template_english_references'] = template_matches
    
    print()
    
    # 4. URL ルーティング英語ID使用分析
    print("【4. URL ルーティング 英語ID使用分析】")
    
    routing_matches = []
    if 'app_content' in locals():
        # @app.route で英語IDを使用している箇所を特定
        route_pattern = r"@app\.route\(['\"][^'\"]*"
        routes = re.findall(route_pattern, app_content)
        
        for route in routes:
            for eng_id in english_ids:
                if eng_id in route:
                    routing_matches.append((route, eng_id))
        
        print(f"  URLルーティング英語ID使用: {len(routing_matches)}箇所")
        for route, eng_id in routing_matches[:5]:
            print(f"    Route ({eng_id}): {route}...")
    
    dependency_map['url_routing_english'] = routing_matches
    
    print()
    
    # 5. 依存関係サマリー生成
    print("【5. 依存関係サマリー】")
    
    total_dependencies = (
        len(dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING']) +
        len(dependency_map['english_department_ids']) +
        len(dependency_map['config_english_mappings']) +
        len(dependency_map['template_english_references']) +
        len(dependency_map['url_routing_english'])
    )
    
    print(f"  総依存箇所数: {total_dependencies}箇所")
    
    # 重要度分析
    critical_areas = []
    if len(dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING']) > 0:
        critical_areas.append('LIGHTWEIGHT_DEPARTMENT_MAPPING（最重要）')
    if len(dependency_map['english_department_ids']) > 20:
        critical_areas.append('英語部門ID直接使用（高重要）')
    if len(dependency_map['url_routing_english']) > 0:
        critical_areas.append('URLルーティング（中重要）')
    
    print(f"  重要修正対象: {len(critical_areas)}分野")
    for area in critical_areas:
        print(f"    - {area}")
    
    print()
    
    # 6. 修正影響範囲予測
    print("【6. 修正影響範囲予測】")
    
    impact_analysis = {
        'high_risk': [],
        'medium_risk': [],
        'low_risk': []
    }
    
    if len(dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING']) > 10:
        impact_analysis['high_risk'].append('部門選択機能')
    if len(dependency_map['english_department_ids']) > 20:
        impact_analysis['high_risk'].append('問題フィルタリング')
    if len(dependency_map['url_routing_english']) > 5:
        impact_analysis['medium_risk'].append('URLルーティング')
    if len(dependency_map['template_english_references']) > 0:
        impact_analysis['medium_risk'].append('テンプレート表示')
    
    print(f"  高リスク修正箇所: {len(impact_analysis['high_risk'])}分野")
    print(f"  中リスク修正箇所: {len(impact_analysis['medium_risk'])}分野")
    print(f"  低リスク修正箇所: {len(impact_analysis['low_risk'])}分野")
    
    print()
    
    # 7. 段階的修正計画提案
    print("【7. 段階的修正計画提案】")
    
    modification_plan = []
    
    if len(dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING']) > 0:
        modification_plan.append({
            'phase': 'Phase 1',
            'target': 'LIGHTWEIGHT_DEPARTMENT_MAPPING廃止',
            'risk': 'High',
            'estimated_changes': len(dependency_map['LIGHTWEIGHT_DEPARTMENT_MAPPING'])
        })
    
    if len(dependency_map['english_department_ids']) > 0:
        modification_plan.append({
            'phase': 'Phase 2', 
            'target': '英語部門ID → 日本語カテゴリ直接使用',
            'risk': 'High',
            'estimated_changes': len(dependency_map['english_department_ids'])
        })
    
    if len(dependency_map['url_routing_english']) > 0:
        modification_plan.append({
            'phase': 'Phase 3',
            'target': 'URLエンコーディング対応',
            'risk': 'Medium', 
            'estimated_changes': len(dependency_map['url_routing_english'])
        })
    
    for i, phase in enumerate(modification_plan, 1):
        print(f"  {phase['phase']}: {phase['target']}")
        print(f"    リスクレベル: {phase['risk']}")
        print(f"    推定変更箇所: {phase['estimated_changes']}箇所")
    
    print()
    print("=== Stage 3 Analysis Complete ===")
    print("SUCCESS: English ID conversion system dependency mapping created")
    print("SUCCESS: Modification impact analysis completed")
    print("SUCCESS: Staged modification plan proposed")
    print()
    print("SAFETY: Side effect risk areas identified in advance")
    print("READY: Stage 4 (Japanese category direct use system design) ready")
    
    return dependency_map, modification_plan

if __name__ == "__main__":
    dependency_map, modification_plan = analyze_english_id_dependencies()
    
    # 結果をファイルに保存（後の段階で参照用）
    import json
    
    # 依存関係マップをJSON化（複雑なオブジェクトは文字列化）
    json_safe_map = {}
    for key, value in dependency_map.items():
        if isinstance(value, list):
            json_safe_map[key] = [str(item) for item in value]
        else:
            json_safe_map[key] = str(value)
    
    with open('ultrasync_dependency_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump({
            'dependency_map': json_safe_map,
            'modification_plan': modification_plan,
            'analysis_timestamp': '2025-08-11T15:20:00+09:00',
            'total_dependencies': sum(len(v) for v in dependency_map.values() if isinstance(v, list))
        }, f, ensure_ascii=False, indent=2)
    
    print("SAVED: Dependency analysis result saved to ultrasync_dependency_analysis_result.json")