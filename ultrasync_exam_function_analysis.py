# -*- coding: utf-8 -*-
"""
ULTRA SYNC [基本機能確保-005] exam()関数3000行分割リファクタリング計画策定
副作用なし・読み取り専用での詳細分析と安全な分割計画
"""

import re
import os
from collections import defaultdict

def analyze_exam_function_structure():
    """exam()関数の詳細構造分析"""
    print('ULTRA SYNC [基本機能確保-005] exam()関数分割リファクタリング計画策定')
    print('=' * 80)
    print('副作用防止・機能アップ禁止・読み取り専用分析モード')
    print('=' * 80)
    
    app_py_path = 'rccm-quiz-app/app.py'
    
    if not os.path.exists(app_py_path):
        print('ERROR: app.py が見つかりません')
        return
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # exam()関数の開始・終了を特定
    exam_start = None
    exam_end = None
    indent_level = 0
    
    print('=== exam()関数の位置特定 ===')
    
    for line_no, line in enumerate(lines, 1):
        if re.match(r'^def exam\(\)', line.strip()):
            exam_start = line_no
            print(f'exam()関数開始: 行{exam_start}')
            break
    
    if not exam_start:
        print('ERROR: exam()関数が見つかりません')
        return
    
    # 関数の終了位置を特定
    for line_no in range(exam_start, len(lines)):
        line = lines[line_no]
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if line_no > exam_start:  # 次の関数定義
                exam_end = line_no
                break
    
    if not exam_end:
        exam_end = len(lines)
    
    exam_lines = lines[exam_start-1:exam_end-1]
    exam_line_count = len(exam_lines)
    
    print(f'exam()関数終了: 行{exam_end-1}')
    print(f'exam()関数総行数: {exam_line_count}行')
    
    # 機能ブロックの分析
    print('\n=== 機能ブロック分析 ===')
    
    functional_blocks = analyze_functional_blocks(exam_lines, exam_start)
    
    # 複雑度分析
    print('\n=== 複雑度分析 ===')
    complexity_analysis = analyze_complexity(exam_lines)
    
    # 分割計画の策定
    print('\n=== 安全な分割計画策定 ===')
    refactoring_plan = create_safe_refactoring_plan(functional_blocks, complexity_analysis)
    
    return {
        'exam_start': exam_start,
        'exam_end': exam_end,
        'total_lines': exam_line_count,
        'functional_blocks': functional_blocks,
        'complexity': complexity_analysis,
        'refactoring_plan': refactoring_plan
    }

def analyze_functional_blocks(exam_lines, start_line):
    """exam()関数内の機能ブロック分析"""
    blocks = []
    current_block = None
    
    # 機能パターンの定義
    patterns = [
        {'name': 'request_processing', 'pattern': r'request\.(method|form|args)', 'description': 'リクエスト処理'},
        {'name': 'session_management', 'pattern': r'session\[|session\.get', 'description': 'セッション管理'},
        {'name': 'question_loading', 'pattern': r'load_.*questions|csv|questions_data', 'description': '問題データロード'},
        {'name': 'department_handling', 'pattern': r'department|専門科目|4-2', 'description': '部門処理'},
        {'name': 'progress_tracking', 'pattern': r'current|progress|quiz_current', 'description': '進捗管理'},
        {'name': 'answer_processing', 'pattern': r'answer|correct|is_correct', 'description': '回答処理'},
        {'name': 'navigation_logic', 'pattern': r'next|redirect|url_for', 'description': 'ナビゲーション'},
        {'name': 'template_rendering', 'pattern': r'render_template|return.*html', 'description': 'テンプレート描画'},
        {'name': 'error_handling', 'pattern': r'try:|except|error|logger', 'description': 'エラーハンドリング'},
        {'name': 'security_checks', 'pattern': r'csrf|token|validate', 'description': 'セキュリティチェック'}
    ]
    
    # ブロック検出
    for line_no, line in enumerate(exam_lines, start_line):
        line_content = line.strip()
        
        if not line_content or line_content.startswith('#'):
            continue
        
        # パターンマッチング
        for pattern_info in patterns:
            if re.search(pattern_info['pattern'], line_content, re.IGNORECASE):
                if current_block and current_block['type'] != pattern_info['name']:
                    # 新しいブロック開始
                    blocks.append(current_block)
                    current_block = None
                
                if not current_block:
                    current_block = {
                        'type': pattern_info['name'],
                        'description': pattern_info['description'],
                        'start_line': line_no,
                        'end_line': line_no,
                        'lines': [],
                        'complexity': 0
                    }
                
                current_block['end_line'] = line_no
                current_block['lines'].append(line_content)
                
                # 複雑度カウント
                if re.search(r'if|for|while|try|except', line_content):
                    current_block['complexity'] += 1
                
                break
    
    if current_block:
        blocks.append(current_block)
    
    # ブロック統計
    print('検出された機能ブロック:')
    for i, block in enumerate(blocks, 1):
        line_count = len(block['lines'])
        print(f'{i:2}. {block["description"]}: {line_count}行 (複雑度{block["complexity"]}) '
              f'[行{block["start_line"]}-{block["end_line"]}]')
    
    return blocks

def analyze_complexity(exam_lines):
    """複雑度分析"""
    complexity_metrics = {
        'cyclomatic_complexity': 0,
        'nesting_levels': [],
        'condition_count': 0,
        'loop_count': 0,
        'exception_blocks': 0,
        'function_calls': 0
    }
    
    current_nesting = 0
    max_nesting = 0
    
    for line in exam_lines:
        line_content = line.strip()
        
        # ネストレベル計算
        if re.search(r'if|for|while|try|with|def|class', line_content):
            current_nesting += 1
            max_nesting = max(max_nesting, current_nesting)
            complexity_metrics['cyclomatic_complexity'] += 1
        
        if re.search(r'^\s*(elif|else|except|finally)', line):
            complexity_metrics['cyclomatic_complexity'] += 1
        
        # 他の複雑度指標
        if re.search(r'if|elif', line_content):
            complexity_metrics['condition_count'] += 1
        
        if re.search(r'for|while', line_content):
            complexity_metrics['loop_count'] += 1
        
        if re.search(r'try|except', line_content):
            complexity_metrics['exception_blocks'] += 1
        
        # 関数呼び出し
        function_calls = len(re.findall(r'\w+\(', line_content))
        complexity_metrics['function_calls'] += function_calls
        
        # ネストの減少
        if line_content and not line.startswith(' ') and not line.startswith('\t'):
            current_nesting = 0
    
    complexity_metrics['max_nesting_level'] = max_nesting
    
    print(f'サイクロマティック複雑度: {complexity_metrics["cyclomatic_complexity"]}')
    print(f'最大ネストレベル: {complexity_metrics["max_nesting_level"]}')
    print(f'条件分岐数: {complexity_metrics["condition_count"]}')
    print(f'ループ数: {complexity_metrics["loop_count"]}')
    print(f'例外処理ブロック数: {complexity_metrics["exception_blocks"]}')
    print(f'関数呼び出し数: {complexity_metrics["function_calls"]}')
    
    return complexity_metrics

def create_safe_refactoring_plan(functional_blocks, complexity_analysis):
    """安全なリファクタリング計画策定"""
    
    # 分割優先度の決定
    refactoring_phases = {
        'phase1_safe_extraction': {
            'description': 'Phase 1: 安全な独立機能抽出',
            'targets': [],
            'risk_level': 'LOW',
            'estimated_effort': 'Small'
        },
        'phase2_data_processing': {
            'description': 'Phase 2: データ処理ロジック分離',
            'targets': [],
            'risk_level': 'MEDIUM',
            'estimated_effort': 'Medium'
        },
        'phase3_core_logic': {
            'description': 'Phase 3: コアロジック分割（慎重実行）',
            'targets': [],
            'risk_level': 'HIGH',
            'estimated_effort': 'Large'
        }
    }
    
    # ブロックの分類
    for block in functional_blocks:
        block_type = block['type']
        complexity = block['complexity']
        line_count = len(block['lines'])
        
        if block_type in ['template_rendering', 'error_handling'] and complexity <= 3:
            # 安全に抽出可能
            refactoring_phases['phase1_safe_extraction']['targets'].append(block)
        elif block_type in ['question_loading', 'department_handling'] and complexity <= 8:
            # 中程度のリスクで分離可能
            refactoring_phases['phase2_data_processing']['targets'].append(block)
        else:
            # 慎重な分割が必要
            refactoring_phases['phase3_core_logic']['targets'].append(block)
    
    # 計画の詳細化
    for phase_key, phase in refactoring_phases.items():
        target_blocks = phase['targets']
        total_lines = sum(len(block['lines']) for block in target_blocks)
        total_complexity = sum(block['complexity'] for block in target_blocks)
        
        print(f'\n{phase["description"]}:')
        print(f'  対象ブロック数: {len(target_blocks)}')
        print(f'  総行数: {total_lines}行')
        print(f'  総複雑度: {total_complexity}')
        print(f'  リスクレベル: {phase["risk_level"]}')
        
        for block in target_blocks:
            print(f'    - {block["description"]}: {len(block["lines"])}行')
    
    # 安全性確保のための提案
    print('\n=== 安全性確保提案 ===')
    print('1. 副作用ゼロ原則:')
    print('   - 各Phase実行前にバックアップ作成')
    print('   - 抽出後の関数テスト実行')
    print('   - 元関数との完全な動作一致確認')
    
    print('\n2. 段階的実行:')
    print('   - Phase 1完了後、本番環境動作確認')
    print('   - Phase 2実行前、総合テスト実行')
    print('   - Phase 3は最終段階として慎重実行')
    
    print('\n3. 回帰テスト必須:')
    print('   - 13部門×3問題数テスト実行')
    print('   - 基本フロー動作確認')
    print('   - セッション管理整合性確認')
    
    return refactoring_phases

if __name__ == '__main__':
    try:
        os.chdir('C:/Users/ABC/Desktop/rccm-quiz-app')
        
        analysis_result = analyze_exam_function_structure()
        
        if analysis_result:
            print(f'\n分析完了:')
            print(f'  exam()関数: {analysis_result["total_lines"]}行')
            print(f'  機能ブロック: {len(analysis_result["functional_blocks"])}個')
            print(f'  複雑度: {analysis_result["complexity"]["cyclomatic_complexity"]}')
            
            print('\n次のステップ: Phase 1安全抽出の実行準備完了')
            print('リファクタリング実行前に必ず本番環境バックアップを取得してください')
    
    except Exception as e:
        print(f'分析エラー: {e}')