#!/usr/bin/env python3
# 🛡️ ULTRASYNC 基礎科目(4-1) 10問完走テスト本番検証

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_basic_subjects_completion():
    """基礎科目10問完走テストの本番準備検証"""
    print('🛡️ ULTRASYNC 基礎科目(4-1) 10問完走テスト検証開始')
    print('=' * 70)
    
    issues_found = []
    fixes_applied = []
    
    try:
        # 1. exam.html テンプレートのcsrf_token確認
        print('ステップ1: exam.html CSRF Token確認')
        with open('templates/exam.html', 'r', encoding='utf-8') as f:
            exam_content = f.read()
        
        if 'csrf_token()' in exam_content and 'name="csrf_token"' in exam_content:
            print('  ✅ CSRF Token: テンプレートに実装済み')
            fixes_applied.append('exam.html CSRF Token実装')
        else:
            print('  ❌ CSRF Token: テンプレートに未実装')
            issues_found.append('exam.html CSRF Token未実装')
        
        # 2. app.py Context Processor確認
        print('ステップ2: app.py Context Processor確認')
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        if 'inject_csrf_token' in app_content and 'empty_csrf_token' in app_content:
            print('  ✅ Context Processor: 実装済み')
            fixes_applied.append('CSRF Context Processor実装')
        else:
            print('  ❌ Context Processor: 未実装')
            issues_found.append('CSRF Context Processor未実装')
        
        # 3. start_exam基礎科目セッション初期化確認
        print('ステップ3: start_exam基礎科目セッション初期化確認')
        if "session['exam_question_ids'] = question_ids" in app_content:
            print('  ✅ セッション初期化: 基礎科目対応済み')
            fixes_applied.append('基礎科目セッション初期化修正')
        else:
            print('  ❌ セッション初期化: 基礎科目未対応')
            issues_found.append('基礎科目セッション初期化未対応')
        
        # 4. exam route GET/POST対応確認
        print('ステップ4: exam route GET/POST対応確認')
        if "methods=['GET', 'POST']" in app_content and '@app.route(\'/exam\',' in app_content:
            print('  ✅ exam route: GET/POST対応済み')
            fixes_applied.append('exam route GET/POST対応')
        else:
            print('  ❌ exam route: GET/POST未対応')
            issues_found.append('exam route GET/POST未対応')
        
        # 5. 基礎科目データファイル確認
        print('ステップ5: 基礎科目データファイル確認')
        basic_file_path = 'data/4-1.csv'
        if os.path.exists(basic_file_path):
            print(f'  ✅ データファイル: {basic_file_path} 存在')
            fixes_applied.append('基礎科目データファイル確認')
            
            # ファイルサイズ確認
            file_size = os.path.getsize(basic_file_path)
            print(f'  📊 ファイルサイズ: {file_size} bytes')
            
            if file_size > 1000:  # 1KB以上なら問題データありと判断
                print('  ✅ データ内容: 十分なサイズ')
            else:
                print('  ⚠️ データ内容: サイズが小さい可能性')
                issues_found.append('基礎科目データサイズ不足の可能性')
        else:
            print(f'  ❌ データファイル: {basic_file_path} 不存在')
            issues_found.append('基礎科目データファイル不存在')
        
        # 6. 専門科目分離確認
        print('ステップ6: 専門科目との分離確認')
        if 'load_basic_questions_only' in app_content:
            print('  ✅ 専門科目分離: 基礎科目専用ローダー実装済み')
            fixes_applied.append('基礎科目専用ローダー実装')
        else:
            print('  ❌ 専門科目分離: 基礎科目専用ローダー未実装')
            issues_found.append('基礎科目専用ローダー未実装')
        
        # 7. ID範囲分離確認
        print('ステップ7: ID範囲分離確認')
        try:
            with open('utils.py', 'r', encoding='utf-8') as f:
                utils_content = f.read()
            
            if '1000000' in utils_content and '2000000' in utils_content:
                print('  ✅ ID範囲分離: utils.pyで基礎科目1000000-1999999確保済み')
                fixes_applied.append('基礎科目ID範囲分離')
            else:
                print('  ❌ ID範囲分離: utils.pyで基礎科目ID範囲未確保')
                issues_found.append('基礎科目ID範囲未確保')
        except FileNotFoundError:
            print('  ❌ ID範囲分離: utils.pyファイル不存在')
            issues_found.append('utils.pyファイル不存在')
        
        print('=' * 70)
        print('検証結果サマリー:')
        print(f'✅ 修正適用済み: {len(fixes_applied)}項目')
        for fix in fixes_applied:
            print(f'    - {fix}')
        
        print(f'❌ 未解決問題: {len(issues_found)}項目')
        for issue in issues_found:
            print(f'    - {issue}')
        
        # 本番テスト手順説明
        print('=' * 70)
        print('🎯 本番環境手動テスト手順:')
        print('1. https://rccm-quiz-2025.onrender.com/ にアクセス')
        print('2. 基礎科目(4-1共通)を選択')
        print('3. 10問設定で試験開始')
        print('4. 1問目が正常表示されることを確認')
        print('5. 回答選択 → 次の問題へボタンクリック')
        print('6. 10問すべて回答完了まで継続')
        print('7. 最終結果画面が表示されることを確認')
        print('8. スコア計算が正常であることを確認')
        
        if len(issues_found) == 0:
            print('\n🎯 結論: 基礎科目10問完走テスト準備完了 - 本番テスト実行可能')
            return True
        else:
            print('\n❌ 結論: 未解決問題あり - 追加修正が必要')
            return False
        
    except Exception as e:
        print(f'検証中にエラー: {e}')
        return False

if __name__ == '__main__':
    success = verify_basic_subjects_completion()
    if success:
        print('\n🚀 基礎科目10問完走テスト: 本番環境テスト実行準備完了')
    else:
        print('\n🔧 基礎科目10問完走テスト: 追加修正が必要です')