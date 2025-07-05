#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 一問目エラー分析ツール
副作用ゼロで根本原因を特定
"""

import os
import sys
import json
from datetime import datetime

def safe_analyze_first_question_error():
    """一問目エラーの根本原因を安全に分析"""
    print("🛡️ ULTRA SAFE 一問目エラー分析開始")
    print("=" * 60)
    print(f"分析時刻: {datetime.now()}")
    print(f"副作用: ゼロ（読み取り専用分析）")
    
    analysis_results = {
        'session_initialization_issues': [],
        'route_problems': [],
        'template_errors': [],
        'data_loading_issues': [],
        'critical_findings': []
    }
    
    # 1. セッション初期化問題の分析
    print("\n🔍 セッション初期化問題分析:")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 危険なセッション初期化パターンを検索
        dangerous_patterns = [
            "session.pop('exam_question_ids'",
            "session.clear()",
            "del session[",
            "'exam_question_ids' not in session",
            "session['exam_question_ids'] = []"
        ]
        
        for pattern in dangerous_patterns:
            count = content.count(pattern)
            if count > 0:
                analysis_results['session_initialization_issues'].append({
                    'pattern': pattern,
                    'occurrences': count,
                    'risk_level': 'HIGH' if count > 5 else 'MEDIUM'
                })
                print(f"  🚨 {pattern}: {count}箇所")
            else:
                print(f"  ✅ {pattern}: 0箇所")
                
    except Exception as e:
        print(f"  ❌ 分析エラー: {e}")
    
    # 2. /exam ルートの問題分析
    print("\n🔍 /exam ルート問題分析:")
    try:
        # /exam ルートの開始行を特定
        lines = content.split('\n')
        exam_route_start = None
        for i, line in enumerate(lines):
            if "@app.route('/exam'" in line:
                exam_route_start = i
                break
        
        if exam_route_start:
            print(f"  ✅ /exam ルート発見: 行 {exam_route_start + 1}")
            
            # 最初の100行を分析
            exam_function_lines = lines[exam_route_start:exam_route_start + 200]
            
            # 問題のあるパターンを検索
            problematic_patterns = [
                ("return render_template('error.html'", "エラーページへの早期リダイレクト"),
                ("if not", "条件チェック失敗"),
                ("KeyError", "キーエラー例外"),
                ("session.get('exam_question_ids')", "セッション取得"),
                ("exam_question_ids = []", "空リスト初期化")
            ]
            
            for pattern, description in problematic_patterns:
                matches = [i for i, line in enumerate(exam_function_lines) if pattern in line]
                if matches:
                    analysis_results['route_problems'].append({
                        'pattern': pattern,
                        'description': description,
                        'line_numbers': [exam_route_start + m + 1 for m in matches[:3]]
                    })
                    print(f"  🔍 {description}: {len(matches)}箇所 (例: 行{exam_route_start + matches[0] + 1})")
        else:
            print("  ❌ /exam ルートが見つかりません")
            analysis_results['route_problems'].append({
                'pattern': '@app.route(\'/exam\')',
                'description': 'ルート定義が見つからない',
                'line_numbers': []
            })
            
    except Exception as e:
        print(f"  ❌ ルート分析エラー: {e}")
    
    # 3. テンプレート問題分析
    print("\n🔍 テンプレート問題分析:")
    try:
        template_files = [
            'templates/exam.html',
            'templates/exam_feedback.html',
            'templates/error.html'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # 問題のあるテンプレートパターン
                template_issues = [
                    ("{{ question.id }}", "問題ID参照"),
                    ("{% if question %}", "問題存在チェック"),
                    ("{% if not question %}", "問題不存在チェック"),
                    ("{{ current_no }}", "現在問題番号"),
                    ("{{ error }}", "エラー表示")
                ]
                
                file_issues = []
                for pattern, description in template_issues:
                    if pattern in template_content:
                        file_issues.append(f"{description}: あり")
                    
                if file_issues:
                    analysis_results['template_errors'].append({
                        'file': template_file,
                        'issues': file_issues
                    })
                    print(f"  📄 {template_file}: {len(file_issues)}項目")
                else:
                    print(f"  ✅ {template_file}: 問題なし")
            else:
                print(f"  ❌ {template_file}: ファイル不存在")
                
    except Exception as e:
        print(f"  ❌ テンプレート分析エラー: {e}")
    
    # 4. データロード問題分析
    print("\n🔍 データロード問題分析:")
    try:
        data_files = [
            'data/questions_fixed.csv',
            'data/questions.csv'
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                file_size = os.path.getsize(data_file)
                print(f"  ✅ {data_file}: {file_size} bytes")
                
                # CSVファイルの基本チェック
                with open(data_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        print(f"    📋 ヘッダー: {first_line[:50]}...")
                        
                        # 行数カウント
                        f.seek(0)
                        line_count = sum(1 for line in f) - 1  # ヘッダーを除く
                        print(f"    📊 データ行数: {line_count}")
                        
                        if line_count == 0:
                            analysis_results['data_loading_issues'].append({
                                'file': data_file,
                                'issue': 'データ行なし',
                                'severity': 'CRITICAL'
                            })
                    else:
                        analysis_results['data_loading_issues'].append({
                            'file': data_file,
                            'issue': '空ファイル',
                            'severity': 'CRITICAL'
                        })
            else:
                print(f"  ❌ {data_file}: ファイル不存在")
                analysis_results['data_loading_issues'].append({
                    'file': data_file,
                    'issue': 'ファイル不存在',
                    'severity': 'CRITICAL'
                })
                
    except Exception as e:
        print(f"  ❌ データロード分析エラー: {e}")
    
    # 5. 根本原因推定
    print("\n🎯 根本原因推定:")
    
    # セッション初期化問題が多い場合
    session_issues = len(analysis_results['session_initialization_issues'])
    if session_issues > 3:
        analysis_results['critical_findings'].append(
            "セッション初期化に複数の問題あり - 一問目で初期化失敗の可能性"
        )
        print("  🚨 セッション初期化問題: 高リスク")
    
    # データロード問題がある場合
    data_issues = len(analysis_results['data_loading_issues'])
    if data_issues > 0:
        analysis_results['critical_findings'].append(
            "データロードに問題あり - 問題データ取得失敗の可能性"
        )
        print("  🚨 データロード問題: 高リスク")
    
    # ルート問題がある場合
    route_issues = len(analysis_results['route_problems'])
    if route_issues > 2:
        analysis_results['critical_findings'].append(
            "/exam ルートに複数の問題あり - リクエスト処理失敗の可能性"
        )
        print("  🚨 ルート処理問題: 高リスク")
    
    if not analysis_results['critical_findings']:
        analysis_results['critical_findings'].append(
            "明確な問題は検出されず - 実行時の動的エラーの可能性"
        )
        print("  ✅ 静的分析では明確な問題検出されず")
    
    # 6. 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"ultra_safe_first_question_analysis_{timestamp}.json"
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 分析結果保存: {result_file}")
    except Exception as e:
        print(f"\n❌ 結果保存エラー: {e}")
    
    # 7. 推奨対応策
    print("\n📋 推奨対応策:")
    print("1. セッション初期化ロジックの最適化")
    print("2. エラーハンドリングの強化")
    print("3. データロード処理の改善")
    print("4. デバッグログの追加")
    
    print("\n✅ ULTRA SAFE分析完了")
    print("🛡️ 副作用: ゼロ（読み取り専用分析のみ実行）")
    
    return analysis_results

if __name__ == "__main__":
    safe_analyze_first_question_error()