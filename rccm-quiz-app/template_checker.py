#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jinja2
import os
import sys

def check_html_syntax(file_path):
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # HTMLエスケープのチェック
        if '<script>' in content and '{{' in content:
            warnings.append(f'JavaScript内でJinja変数が使用されている可能性があります')
        
        # 基本的なHTMLタグの対応チェック
        tags_to_check = ['div', 'span', 'form', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5']
        for tag in tags_to_check:
            open_count = content.count(f'<{tag}')
            close_count = content.count(f'</{tag}>')
            if open_count != close_count:
                errors.append(f'<{tag}> タグの開閉が一致しません (開始: {open_count}, 終了: {close_count})')
        
        # 基本的なJinja構文チェック
        if '{% extends' in content and not content.strip().startswith('{% extends'):
            warnings.append('extends構文がファイルの先頭にありません')
        
        # blockの対応チェック
        block_starts = content.count('{% block')
        block_ends = content.count('{% endblock')
        if block_starts != block_ends:
            errors.append(f'block構文の開閉が一致しません (開始: {block_starts}, 終了: {block_ends})')
        
        # forループのチェック
        for_starts = content.count('{% for')
        endfor_count = content.count('{% endfor')
        if for_starts != endfor_count:
            errors.append(f'for構文の開閉が一致しません (開始: {for_starts}, 終了: {endfor_count})')
        
        # ifのチェック
        if_starts = content.count('{% if')
        endif_count = content.count('{% endif')
        if if_starts != endif_count:
            errors.append(f'if構文の開閉が一致しません (開始: {if_starts}, 終了: {endif_count})')
        
        return errors, warnings
        
    except Exception as e:
        return [f'ファイル読み込みエラー: {str(e)}'], []

def check_jinja_syntax(file_path):
    try:
        env = jinja2.Environment()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Jinja2テンプレートとして解析
        env.parse(content)
        return True, None
    except jinja2.exceptions.TemplateSyntaxError as e:
        return False, f'行{e.lineno}: {e.message}'
    except Exception as e:
        return False, str(e)

def main():
    template_dir = 'templates'
    html_files = []

    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f'テンプレート構文チェック開始 - 対象ファイル数: {len(html_files)}')
    print('=' * 80)

    html_ok = 0
    jinja_ok = 0
    total_files = len(html_files)
    all_errors = []
    all_warnings = []

    for file_path in sorted(html_files):
        print(f'チェック中: {file_path}')
        
        # HTMLとJinja構文の基本チェック
        errors, warnings = check_html_syntax(file_path)
        
        if not errors:
            html_ok += 1
            print('  HTML構文: OK')
        else:
            print('  HTML構文: エラーあり')
            for error in errors:
                print(f'    ERROR: {error}')
                all_errors.append(f'{file_path}: {error}')
        
        if warnings:
            for warning in warnings:
                print(f'    WARNING: {warning}')
                all_warnings.append(f'{file_path}: {warning}')
        
        # Jinja構文チェック
        jinja_ok_flag, jinja_error = check_jinja_syntax(file_path)
        if jinja_ok_flag:
            jinja_ok += 1
            print('  Jinja構文: OK')
        else:
            print('  Jinja構文: エラーあり')
            print(f'    JINJA ERROR: {jinja_error}')
            all_errors.append(f'{file_path}: {jinja_error}')
        
        print()

    print('=' * 80)
    print('チェック結果サマリー:')
    print(f'  総ファイル数: {total_files}')
    print(f'  HTML構文OK: {html_ok}/{total_files}')
    print(f'  Jinja構文OK: {jinja_ok}/{total_files}')
    print(f'  成功率: {(min(html_ok, jinja_ok) / total_files * 100):.1f}%')
    
    if all_errors:
        print('\nエラー一覧:')
        for error in all_errors:
            print(f'  • {error}')
    
    if all_warnings:
        print('\n警告一覧:')
        for warning in all_warnings:
            print(f'  • {warning}')
    
    if not all_errors:
        print('\n✅ 重大なエラーは検出されませんでした。')
    else:
        print(f'\n❌ {len(all_errors)}個のエラーが検出されました。')
    
    return len(all_errors) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)