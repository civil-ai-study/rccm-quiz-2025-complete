#!/usr/bin/env python3
"""
厳重なテスト: 全修正事項の包括的検証
ユーザーの指摘事項120回以上の問題を含む全ての問題を検証
"""

from app import app, get_mixed_questions, load_questions
from flask import session
import random

def test_critical_data_mixing_comprehensive():
    """120回以上指摘された重要なバグの厳重テスト"""
    print("🚨 【厳重テスト】基礎・専門科目データ混在問題の包括検証")
    print("=" * 60)
    
    with app.app_context():
        with app.test_request_context():
            # 全問題データを読み込み
            all_questions = load_questions()
            print(f"✅ 総問題数: {len(all_questions)}問")
            
            # 基礎・専門問題の分類確認
            basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
            specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
            
            print(f"✅ 基礎科目問題: {len(basic_questions)}問")
            print(f"✅ 専門科目問題: {len(specialist_questions)}問")
            
            # 【厳重テスト1】基礎科目選択時の漏れ検証
            print("\n📋 テスト1: 基礎科目選択（厳重検証）")
            error_count = 0
            
            for test_run in range(10):  # 10回連続テスト
                mock_session = {}
                basic_selected = get_mixed_questions(mock_session, all_questions, '全体', 10, '', 'basic')
                
                print(f"  実行{test_run + 1}: {len(basic_selected)}問選択")
                
                for i, q in enumerate(basic_selected):
                    q_type = q.get('question_type')
                    q_year = q.get('year')
                    q_id = q.get('id')
                    
                    if q_type != 'basic':
                        print(f"    ❌ エラー発見: 基礎選択で{q_type}問題(ID:{q_id})が混入!")
                        error_count += 1
                    
                    if q_year is not None:
                        print(f"    ❌ エラー発見: 基礎問題(ID:{q_id})に年度{q_year}が設定!")
                        error_count += 1
            
            # 【厳重テスト2】専門科目選択時の漏れ検証
            print("\n📋 テスト2: 専門科目選択（厳重検証）")
            departments = ['road', 'civil_planning', 'tunnel', 'soil_foundation']
            
            for dept in departments:
                for test_run in range(5):  # 各部門5回テスト
                    mock_session = {}
                    specialist_selected = get_mixed_questions(mock_session, all_questions, '全体', 10, dept, 'specialist')
                    
                    print(f"  {dept}部門実行{test_run + 1}: {len(specialist_selected)}問選択")
                    
                    for i, q in enumerate(specialist_selected):
                        q_type = q.get('question_type')
                        q_year = q.get('year')
                        q_id = q.get('id')
                        
                        if q_type != 'specialist':
                            print(f"    ❌ エラー発見: 専門選択で{q_type}問題(ID:{q_id})が混入!")
                            error_count += 1
                        
                        if q_year is None:
                            print(f"    ❌ エラー発見: 専門問題(ID:{q_id})に年度が未設定!")
                            error_count += 1
            
            # 【厳重テスト3】セッション切り替え時の検証
            print("\n📋 テスト3: セッション切り替え時の検証（厳重）")
            
            # セッション状態をシミュレート
            test_session = {
                'exam_question_ids': [1, 2, 3],
                'selected_question_type': 'basic',
                'selected_department': ''
            }
            
            # 基礎→専門への切り替えテスト
            specialist_after_basic = get_mixed_questions(test_session, all_questions, '全体', 5, 'road', 'specialist')
            for q in specialist_after_basic:
                if q.get('question_type') != 'specialist':
                    print(f"    ❌ セッション切り替えエラー: 基礎→専門で{q.get('question_type')}問題混入!")
                    error_count += 1
            
            # 専門→基礎への切り替えテスト
            test_session['selected_question_type'] = 'specialist'
            test_session['selected_department'] = 'road'
            
            basic_after_specialist = get_mixed_questions(test_session, all_questions, '全体', 5, '', 'basic')
            for q in basic_after_specialist:
                if q.get('question_type') != 'basic':
                    print(f"    ❌ セッション切り替えエラー: 専門→基礎で{q.get('question_type')}問題混入!")
                    error_count += 1
            
            # 結果判定
            print(f"\n🎯 【厳重テスト結果】")
            if error_count == 0:
                print("✅ 全テストパス: データ混在問題は完全に解決されています")
                return True
            else:
                print(f"❌ {error_count}件のエラーが発見されました")
                return False

def test_ui_color_scheme():
    """UI色彩テーマの厳重検証"""
    print("\n🎨 【厳重テスト】モダン・プロフェッショナル色彩の検証")
    print("=" * 60)
    
    # base.htmlの色設定を確認
    with open('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/templates/base.html', 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    required_colors = [
        '--primary-color: #334155',
        '--secondary-color: #475569', 
        '--success-color: #059669',
        '--accent-color: #6366f1'
    ]
    
    missing_colors = []
    for color in required_colors:
        if color not in base_content:
            missing_colors.append(color)
    
    if missing_colors:
        print(f"❌ 欠落色設定: {missing_colors}")
        return False
    else:
        print("✅ 全ての専門色彩が正しく設定されています")
        return True

def test_question_text_removal():
    """不要テキスト削除の厳重検証"""
    print("\n🧹 【厳重テスト】不要「問題」テキスト削除の検証")
    print("=" * 60)
    
    # exam.htmlの内容確認
    with open('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/templates/exam.html', 'r', encoding='utf-8') as f:
        exam_content = f.read()
    
    # 問題表示エリアの不要テキストのみを確認（アプリ名は除外）
    # 具体的に問題となる箇所のみチェック
    lines = exam_content.split('\n')
    
    problematic_patterns = []
    for i, line in enumerate(lines):
        # アプリケーション名やナビゲーション以外で「問題」単体が使われているかチェック
        if ('問題文' in line and 'title' not in line and 'navbar' not in line):
            problematic_patterns.append(f"Line {i+1}: {line.strip()}")
        
        # 問題ヘッダーで「RCCM試験問題」が使われているかチェック
        if ('RCCM試験問題' in line and 'h1' in line):
            problematic_patterns.append(f"Line {i+1}: {line.strip()}")
    
    if problematic_patterns:
        print(f"❌ 問題表示エリアに不要テキストが残存:")
        for pattern in problematic_patterns:
            print(f"  {pattern}")
        return False
    else:
        print("✅ 問題表示エリアから不要な「問題」テキストが正しく削除されています")
        return True

def run_comprehensive_tests():
    """全ての厳重テストを実行"""
    print("🔬 RCCM試験問題集アプリ - 厳重テスト実行開始")
    print("=" * 80)
    
    test_results = []
    
    # テスト1: 最重要のデータ混在問題
    result1 = test_critical_data_mixing_comprehensive()
    test_results.append(("データ混在問題解決", result1))
    
    # テスト2: UI色彩テーマ
    result2 = test_ui_color_scheme()
    test_results.append(("プロフェッショナル色彩", result2))
    
    # テスト3: 不要テキスト削除
    result3 = test_question_text_removal()
    test_results.append(("不要テキスト削除", result3))
    
    # 総合判定
    print("\n" + "=" * 80)
    print("🎯 【最終厳重テスト結果】")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 【総合判定】全ての厳重テスト合格 - 全修正事項が正常に動作")
    else:
        print("🚨 【総合判定】一部テスト失敗 - 追加修正が必要")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_tests()