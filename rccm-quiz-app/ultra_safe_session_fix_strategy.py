#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE セッション修正戦略
副作用ゼロでセッション問題の安全な修正方法を立案
"""

import os
import re
from datetime import datetime

def ultra_safe_session_analysis():
    """セッション問題の安全な分析と修正戦略"""
    print("🛡️ ULTRA SAFE セッション修正戦略")
    print("=" * 60)
    print(f"分析時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（読み取り専用＋修正戦略立案）")
    
    strategy = {
        'issues_found': [],
        'safe_fixes': [],
        'testing_plan': [],
        'rollback_plan': []
    }
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return
    
    print("\n🔍 セッション問題の詳細分析:")
    
    # 1. 重複するsession.pop呼び出しの特定
    print("\n1. 重複セッション操作の分析:")
    session_pop_lines = []
    for i, line in enumerate(lines):
        if "session.pop('exam_question_ids'" in line:
            session_pop_lines.append((i + 1, line.strip()))
    
    if len(session_pop_lines) > 3:
        strategy['issues_found'].append({
            'issue': 'セッション初期化の重複実行',
            'lines': session_pop_lines,
            'severity': 'HIGH',
            'description': f"{len(session_pop_lines)}箇所でsession.pop('exam_question_ids')が実行されている"
        })
        print(f"  🚨 session.pop('exam_question_ids'): {len(session_pop_lines)}箇所で重複")
        for line_no, line_content in session_pop_lines[:3]:
            print(f"    行{line_no}: {line_content}")
    
    # 2. セッション競合状態の特定
    print("\n2. セッション競合状態の分析:")
    
    # セッション読み取りと書き込みが近接している箇所を特定
    session_read_write_conflicts = []
    for i, line in enumerate(lines):
        if "session.get('exam_question_ids'" in line or "'exam_question_ids' in session" in line:
            # 前後5行でsession.popやsession.clearがあるかチェック
            start = max(0, i - 5)
            end = min(len(lines), i + 5)
            
            for j in range(start, end):
                if j != i and ("session.pop(" in lines[j] or "session.clear()" in lines[j]):
                    session_read_write_conflicts.append({
                        'read_line': i + 1,
                        'read_content': line.strip(),
                        'write_line': j + 1,
                        'write_content': lines[j].strip()
                    })
                    break
    
    if session_read_write_conflicts:
        strategy['issues_found'].append({
            'issue': 'セッション読み書き競合',
            'conflicts': session_read_write_conflicts,
            'severity': 'HIGH',
            'description': 'セッション読み取りと削除が近接している'
        })
        print(f"  🚨 セッション競合: {len(session_read_write_conflicts)}箇所")
    
    # 3. 安全な修正戦略の立案
    print("\n🛡️ 安全な修正戦略:")
    
    # 修正戦略1: セッション初期化の一元化
    strategy['safe_fixes'].append({
        'fix_name': 'セッション初期化一元化',
        'description': '複数箇所のsession.pop呼び出しを一つの関数に統合',
        'implementation': '''
def safe_exam_session_reset():
    """安全なセッション初期化"""
    keys_to_remove = ['exam_question_ids', 'exam_current', 'exam_category']
    for key in keys_to_remove:
        session.pop(key, None)
    session.modified = True
    logger.info("セッション安全リセット完了")
''',
        'risk_level': 'LOW',
        'testing_required': True
    })
    
    # 修正戦略2: セッション状態チェックの改善
    strategy['safe_fixes'].append({
        'fix_name': 'セッション状態チェック改善',
        'description': 'セッション存在チェックを修正前に実行',
        'implementation': '''
def safe_session_check():
    """安全なセッション状態チェック"""
    required_keys = ['exam_question_ids', 'exam_current']
    return all(key in session and session[key] is not None for key in required_keys)
''',
        'risk_level': 'LOW',
        'testing_required': True
    })
    
    # 修正戦略3: エラーハンドリング強化
    strategy['safe_fixes'].append({
        'fix_name': 'エラーハンドリング強化',
        'description': 'セッション操作時の例外処理を追加',
        'implementation': '''
try:
    # セッション操作
    if safe_session_check():
        # 正常処理
        pass
    else:
        # セッション初期化
        safe_exam_session_reset()
except Exception as e:
    logger.error(f"セッション操作エラー: {e}")
    # フォールバック処理
''',
        'risk_level': 'LOW',
        'testing_required': True
    })
    
    for i, fix in enumerate(strategy['safe_fixes'], 1):
        print(f"\n修正戦略{i}: {fix['fix_name']}")
        print(f"  説明: {fix['description']}")
        print(f"  リスク: {fix['risk_level']}")
        print(f"  テスト必要: {'はい' if fix['testing_required'] else 'いいえ'}")
    
    # 4. テスト計画
    print("\n🧪 ULTRA SAFEテスト計画:")
    test_scenarios = [
        "新規セッション開始テスト",
        "既存セッション継続テスト", 
        "セッション破損時の復旧テスト",
        "同時アクセス時の競合テスト",
        "エラー発生時のフォールバックテスト"
    ]
    
    strategy['testing_plan'] = test_scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"  {i}. {scenario}")
    
    # 5. ロールバック計画
    print("\n🔄 ロールバック計画:")
    rollback_steps = [
        "現在のapp.pyのバックアップ作成",
        "修正前の動作確認テスト実行", 
        "修正適用",
        "修正後テスト実行",
        "問題発生時は即座にバックアップから復旧"
    ]
    
    strategy['rollback_plan'] = rollback_steps
    for i, step in enumerate(rollback_steps, 1):
        print(f"  {i}. {step}")
    
    # 6. 実装優先順位
    print("\n📋 実装優先順位:")
    priorities = [
        "HIGH: セッション初期化一元化（最重要）",
        "HIGH: エラーハンドリング強化（安全性確保）",
        "MEDIUM: セッション状態チェック改善（品質向上）",
        "LOW: 性能最適化（余裕があれば）"
    ]
    
    for priority in priorities:
        print(f"  {priority}")
    
    # 7. 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    strategy_file = f"ultra_safe_session_strategy_{timestamp}.json"
    
    try:
        import json
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        print(f"\n💾 修正戦略保存: {strategy_file}")
    except Exception as e:
        print(f"\n❌ 戦略保存エラー: {e}")
    
    print(f"\n✅ ULTRA SAFE修正戦略完了")
    print("🛡️ 副作用: ゼロ（分析と戦略立案のみ）")
    print("🚀 次のステップ: 戦略に基づく安全な修正実行")
    
    return strategy

if __name__ == "__main__":
    ultra_safe_session_analysis()