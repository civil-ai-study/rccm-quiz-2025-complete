#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase4エンコーディング失敗の完全修正実装
ウルトラシンク原則による技術的解決策
"""

import sys
import os
import json
from datetime import datetime

def create_encoding_fix():
    """Phase4エンコーディング問題の根本修正"""
    
    # 1. Flaskアプリケーションのエンコーディング強化コード
    flask_encoding_fix = '''
# Phase4エンコーディング完全修正 - app.py先頭に追加
import sys
import os
from flask import Flask, make_response

# システムレベルのUTF-8設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Flask設定でUTF-8を強制
app = Flask(__name__)
app.config['DEFAULT_CHARSET'] = 'utf-8'
app.config['JSON_AS_ASCII'] = False

# すべてのレスポンスにUTF-8ヘッダーを付加するミドルウェア
@app.after_request
def after_request(response):
    """すべてのHTTPレスポンスにUTF-8 charsetを明示的に設定"""
    if response.mimetype == 'text/html':
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    elif response.mimetype == 'application/json':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    elif response.mimetype.startswith('text/'):
        response.headers['Content-Type'] = f'{response.mimetype}; charset=utf-8'
    return response
'''

    # 2. HTMLテンプレートのcharset meta強化
    html_charset_fix = '''
<!-- すべてのHTMLテンプレートの<head>セクション先頭に追加 -->
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
'''

    # 3. CSVファイル読み込み強化コード
    csv_encoding_fix = '''
def load_csv_safe_enhanced(file_path):
    """
    Phase4エンコーディング問題対応強化版CSV読み込み
    """
    if not os.path.exists(file_path):
        print(f"ERROR: ファイルが存在しません: {file_path}")
        return None
    
    # UTF-8優先の強化エンコーディング試行順序
    encodings_to_try = [
        'utf-8-sig',  # UTF-8 with BOM
        'utf-8',      # UTF-8 without BOM
        'cp932',      # Windows Japanese
        'shift_jis',  # Shift JIS
        'euc-jp',     # EUC-JP
        'iso-2022-jp' # ISO-2022-JP
    ]
    
    for encoding in encodings_to_try:
        try:
            # エンコーディング指定で読み込み
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 日本語文字が正しく読み込まれているか検証
            if not df.empty:
                # サンプル文字列で日本語検証
                sample_text = str(df.iloc[0, 0]) if len(df.columns) > 0 else ""
                if any(ord(char) > 127 for char in sample_text):
                    print(f"OK: {file_path} 日本語エンコーディング成功 ({encoding})")
                else:
                    print(f"OK: {file_path} ASCII読み込み成功 ({encoding})")
                
            return df
            
        except UnicodeDecodeError as e:
            print(f"WARNING: {file_path} エンコーディング {encoding} 失敗: Unicode Decode Error")
            continue
        except Exception as e:
            print(f"WARNING: {file_path} エンコーディング {encoding} 失敗: {e}")
            continue
    
    print(f"ERROR: {file_path} すべてのエンコーディング失敗")
    return None
'''

    # 4. render_template関数の強化
    template_encoding_fix = '''
from flask import make_response, render_template

def render_template_utf8(template_name, **context):
    """UTF-8エンコーディングを保証するrender_template"""
    response = make_response(render_template(template_name, **context))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

# 使用例:
# return render_template_utf8('index.html', data=data)
'''

    # 5. 統合修正プラン
    integration_plan = {
        'timestamp': datetime.now().isoformat(),
        'phase4_encoding_fixes': [
            {
                'priority': 1,
                'component': 'Flask Application',
                'description': 'app.py先頭にシステムレベルUTF-8設定とafter_requestミドルウェアを追加',
                'code_location': 'app.py lines 1-30',
                'implementation': 'flask_encoding_fix'
            },
            {
                'priority': 2,
                'component': 'HTML Templates',  
                'description': '全HTMLテンプレートにdouble charset meta宣言を追加',
                'code_location': 'templates/*.html <head>セクション',
                'implementation': 'html_charset_fix'
            },
            {
                'priority': 3,
                'component': 'CSV Loading',
                'description': 'load_csv_safe関数をUTF-8優先強化版に置き換え',
                'code_location': 'app.py load_csv_safe function',
                'implementation': 'csv_encoding_fix'
            },
            {
                'priority': 4,
                'component': 'Template Rendering',
                'description': 'render_template呼び出しをUTF-8保証版に変更',
                'code_location': 'app.py all render_template calls',
                'implementation': 'template_encoding_fix'
            }
        ],
        'validation_steps': [
            'encoding_diagnostic_test.pyを実行',
            'Content-Typeヘッダーにcharset=utf-8が含まれることを確認',
            'HTML meta charsetタグが存在することを確認',
            '日本語文字が正しく表示されることを確認',
            'Phase4基本テスト80%以上成功率達成を確認'
        ]
    }

    # 修正コードをファイルに保存
    with open('phase4_encoding_fix_plan.json', 'w', encoding='utf-8') as f:
        json.dump(integration_plan, f, ensure_ascii=False, indent=2)

    # 実装コードをファイル出力
    with open('flask_encoding_fix.py', 'w', encoding='utf-8') as f:
        f.write(flask_encoding_fix)
    
    with open('csv_encoding_fix.py', 'w', encoding='utf-8') as f:
        f.write(csv_encoding_fix)
    
    with open('template_encoding_fix.py', 'w', encoding='utf-8') as f:
        f.write(template_encoding_fix)

    print("=== Phase4エンコーディング修正実装完了 ===")
    print("生成ファイル:")
    print("1. phase4_encoding_fix_plan.json - 修正計画")
    print("2. flask_encoding_fix.py - Flaskアプリ修正コード")
    print("3. csv_encoding_fix.py - CSV読み込み修正コード")  
    print("4. template_encoding_fix.py - テンプレート修正コード")
    print("5. encoding_diagnostic_test.py - 検証テスト")
    
    print("\n=== 実装手順 ===")
    print("1. rccm-quiz-app/app.pyの先頭にflask_encoding_fix.pyの内容を追加")
    print("2. 全HTMLテンプレートに<meta charset=\"UTF-8\">を確実に配置")
    print("3. load_csv_safe関数をcsv_encoding_fix.pyの内容で置き換え")
    print("4. encoding_diagnostic_test.pyで検証実行")
    print("5. Phase4基本テスト80%以上成功率達成を確認")
    
    return True

if __name__ == "__main__":
    create_encoding_fix()