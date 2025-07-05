#!/usr/bin/env python3
"""
🚨 包括的システム診断ツール
根幹システムの完全分析とエラー特定
"""

import os
import sys
import traceback
from datetime import datetime

def comprehensive_error_analysis():
    """包括的エラー分析"""
    print("🚨 包括的システム診断開始")
    print("=" * 60)
    print(f"診断時刻: {datetime.now()}")
    print(f"Python版本: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    # 1. 基本ファイル存在確認
    print("\n📁 基本ファイル存在確認:")
    critical_files = [
        'app.py',
        'templates/exam_feedback.html', 
        'templates/exam.html',
        'data/questions_fixed.csv',
        'utils.py',
        'config.py'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size} bytes)")
        else:
            print(f"  ❌ {file_path} - 見つかりません")
    
    # 2. app.py の基本構文チェック
    print("\n🔍 app.py 構文チェック:")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # 基本的な構文チェック
        compile(app_content, 'app.py', 'exec')
        print("  ✅ 構文エラーなし")
    except SyntaxError as e:
        print(f"  ❌ 構文エラー: {e}")
        print(f"  行番号: {e.lineno}")
        print(f"  詳細: {e.text}")
    except Exception as e:
        print(f"  ❌ 読み込みエラー: {e}")
    
    # 3. 重要な関数・ルートの存在確認
    print("\n🔧 重要機能の存在確認:")
    if 'app_content' in locals():
        critical_functions = [
            '@app.route(\'/exam\')',
            'def exam(',
            'exam_feedback.html',
            'session[\'exam_question_ids\']',
            'load_questions(',
        ]
        
        for func in critical_functions:
            if func in app_content:
                print(f"  ✅ {func}")
            else:
                print(f"  ❌ {func} - 見つかりません")
    
    # 4. データベース/CSVファイルチェック
    print("\n📊 データファイルチェック:")
    try:
        import csv
        with open('data/questions_fixed.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            questions = list(reader)
            print(f"  ✅ CSV読み込み成功: {len(questions)}問")
            
            if questions:
                sample = questions[0]
                print(f"  📋 サンプル問題ID: {sample.get('ID', 'N/A')}")
                print(f"  📋 カテゴリ: {sample.get('Category', 'N/A')}")
    except Exception as e:
        print(f"  ❌ CSV読み込みエラー: {e}")
    
    return True

def session_flow_analysis():
    """セッション管理フローの分析"""
    print("\n🔄 セッション管理フロー分析:")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # セッション関連の重要パターンを検索
        session_patterns = [
            "session['exam_question_ids']",
            "session['exam_current']", 
            "session.get('exam_current'",
            "session.modified = True",
            "safe_session_update",
        ]
        
        for pattern in session_patterns:
            count = content.count(pattern)
            print(f"  📊 {pattern}: {count}箇所")
        
        # 危険なパターンをチェック
        dangerous_patterns = [
            "session.clear()",
            "session.pop(",
            "del session[",
        ]
        
        print("\n⚠️ 危険なセッション操作:")
        for pattern in dangerous_patterns:
            count = content.count(pattern)
            if count > 0:
                print(f"  🚨 {pattern}: {count}箇所")
            else:
                print(f"  ✅ {pattern}: 安全")
                
    except Exception as e:
        print(f"  ❌ 分析エラー: {e}")

def error_prone_areas_analysis():
    """エラー発生しやすい箇所の特定"""
    print("\n🎯 エラー発生しやすい箇所:")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        problematic_patterns = [
            ('KeyError', 'session['),
            ('IndexError', '['),
            ('AttributeError', '.get('),
            ('TypeError', 'int('),
            ('ValueError', 'int('),
        ]
        
        for error_type, pattern in problematic_patterns:
            count = 0
            for i, line in enumerate(lines, 1):
                if pattern in line and 'try:' not in line and 'except' not in line:
                    count += 1
            print(f"  🔍 {error_type}のリスク: {count}箇所")
            
    except Exception as e:
        print(f"  ❌ 分析エラー: {e}")

if __name__ == "__main__":
    print("🚨 根幹システム完全診断")
    print("基本的な機能の動作確認を実行します")
    print("=" * 60)
    
    try:
        comprehensive_error_analysis()
        session_flow_analysis() 
        error_prone_areas_analysis()
        
        print("\n✅ 診断完了")
        print("🔧 次のステップ: 特定された問題の修正")
        
    except Exception as e:
        print(f"\n❌ 診断中にエラー: {e}")
        traceback.print_exc()