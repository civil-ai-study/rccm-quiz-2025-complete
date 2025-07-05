#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 統合計画
副作用ゼロでセッション管理関数をapp.pyに統合する計画
"""

import re
from datetime import datetime

def create_ultra_safe_integration_plan():
    """超安全な統合計画の作成"""
    print("🛡️ ULTRA SAFE 統合計画")
    print("=" * 60)
    print(f"計画作成時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（計画立案のみ）")
    
    plan = {
        'target_replacements': [],
        'safety_checks': [],
        'rollback_points': [],
        'test_scenarios': []
    }
    
    # app.pyの読み込み
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return None
    
    print("\n📍 置換対象の特定:")
    
    # 1. session.pop('exam_question_ids' の箇所を特定
    session_pop_patterns = [
        (r"session\.pop\('exam_question_ids', None\)", "safe_exam_session_reset()"),
        (r"session\.pop\('exam_current', None\)", "# Handled by safe_exam_session_reset()"),
        (r"session\.pop\('exam_category', None\)", "# Handled by safe_exam_session_reset()"),
    ]
    
    for pattern, replacement in session_pop_patterns:
        matches = []
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                matches.append({
                    'line_no': i + 1,
                    'original': line.strip(),
                    'replacement': replacement,
                    'context': lines[max(0, i-2):min(len(lines), i+3)]
                })
        
        if matches:
            plan['target_replacements'].append({
                'pattern': pattern,
                'replacement': replacement,
                'occurrences': len(matches),
                'locations': matches
            })
            print(f"\n  パターン: {pattern}")
            print(f"  置換先: {replacement}")
            print(f"  発見箇所: {len(matches)}箇所")
            for match in matches[:2]:  # 最初の2つを表示
                print(f"    行{match['line_no']}: {match['original']}")
    
    # 2. 関数追加位置の特定
    print("\n📍 関数追加位置の特定:")
    
    # SessionStateManagerクラスの後に追加する
    insert_position = None
    for i, line in enumerate(lines):
        if "class SessionStateManager:" in line:
            # クラス定義の終わりを見つける
            indent_level = len(line) - len(line.lstrip())
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' '):
                    insert_position = j
                    break
            break
    
    if insert_position:
        print(f"  ✅ 関数追加位置: 行{insert_position} (SessionStateManagerクラスの後)")
        plan['insert_position'] = insert_position
    else:
        print("  ❌ 適切な挿入位置が見つかりません")
        # フォールバック: インポート文の後
        for i, line in enumerate(lines):
            if "from config import" in line:
                insert_position = i + 2
                print(f"  ✅ フォールバック位置: 行{insert_position} (インポート文の後)")
                plan['insert_position'] = insert_position
                break
    
    # 3. 安全性チェック項目
    print("\n🔒 安全性チェック項目:")
    safety_checks = [
        "バックアップファイルの存在確認",
        "構文エラーチェック（python -m py_compile）",
        "インポートテスト",
        "関数定義の重複チェック",
        "インデントレベルの一貫性"
    ]
    
    plan['safety_checks'] = safety_checks
    for i, check in enumerate(safety_checks, 1):
        print(f"  {i}. {check}")
    
    # 4. ロールバックポイント
    print("\n🔄 ロールバックポイント:")
    rollback_points = [
        {
            'stage': '関数追加前',
            'action': 'app.pyのバックアップ作成',
            'file': 'app.py.backup_before_session_functions'
        },
        {
            'stage': '関数追加後',
            'action': '構文チェック実行',
            'file': 'app.py.backup_after_functions'
        },
        {
            'stage': '置換実行後',
            'action': '全体テスト実行',
            'file': 'app.py.backup_after_replacements'
        }
    ]
    
    plan['rollback_points'] = rollback_points
    for point in rollback_points:
        print(f"  {point['stage']}: {point['action']}")
    
    # 5. テストシナリオ
    print("\n🧪 テストシナリオ:")
    test_scenarios = [
        "セッション初期化テスト（新規開始）",
        "セッション継続テスト（既存セッション）",
        "エラー回復テスト（破損セッション）",
        "並行アクセステスト",
        "メモリリークテスト"
    ]
    
    plan['test_scenarios'] = test_scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"  {i}. {scenario}")
    
    # 6. 実装手順
    print("\n📋 ULTRA SAFE実装手順:")
    implementation_steps = [
        "1. app.pyのバックアップ作成",
        "2. セッション管理関数の追加（safe_exam_session_reset等）",
        "3. 構文チェック実行",
        "4. 最初の1箇所のみ置換（テスト）",
        "5. 動作確認",
        "6. 残りの箇所を段階的に置換",
        "7. 各段階で動作確認",
        "8. 最終テスト実行"
    ]
    
    for step in implementation_steps:
        print(f"  {step}")
    
    # 計画の保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = f"ultra_safe_integration_plan_{timestamp}.json"
    
    try:
        import json
        with open(plan_file, 'w', encoding='utf-8') as f:
            # JSONシリアライズ可能な形式に変換
            serializable_plan = {
                'timestamp': timestamp,
                'target_replacements': len(plan['target_replacements']),
                'insert_position': plan.get('insert_position', 0),
                'safety_checks': plan['safety_checks'],
                'rollback_points': plan['rollback_points'],
                'test_scenarios': plan['test_scenarios']
            }
            json.dump(serializable_plan, f, ensure_ascii=False, indent=2)
        print(f"\n💾 統合計画保存: {plan_file}")
    except Exception as e:
        print(f"\n❌ 計画保存エラー: {e}")
    
    print("\n✅ ULTRA SAFE統合計画完了")
    print("🛡️ 副作用: ゼロ（計画立案のみ）")
    print("🚀 次のステップ: 計画に基づく段階的実装")
    
    return plan

if __name__ == "__main__":
    create_ultra_safe_integration_plan()