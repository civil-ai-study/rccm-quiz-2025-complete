#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 残り箇所分析
残り4箇所の詳細分析と最適な置換順序の決定
"""

import os
from datetime import datetime

def ultra_safe_remaining_analysis():
    """残り箇所の詳細分析"""
    print("🛡️ ULTRA SAFE 残り箇所分析")
    print("=" * 60)
    print(f"分析時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（分析のみ）")
    
    # 1. 現在の状態確認
    print("\n📊 現在の状態確認:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ ファイル読み込み: {len(lines)}行")
    
    # 2. 残存session.pop箇所の完全マッピング
    print("\n🔍 残存session.pop箇所の完全マッピング:")
    
    session_pop_groups = []
    i = 0
    
    while i < len(lines) - 2:
        # 3行連続のsession.popパターンを探す
        if (i + 2 < len(lines) and
            "session.pop('exam_question_ids', None)" in lines[i] and
            "session.pop('exam_current', None)" in lines[i + 1] and
            "session.pop('exam_category', None)" in lines[i + 2]):
            
            # 前後のコンテキストを詳細に分析
            context_before = []
            context_after = []
            
            # 前5行のコンテキスト
            for j in range(max(0, i-5), i):
                context_before.append((j + 1, lines[j].strip()))
            
            # 後5行のコンテキスト
            for j in range(i + 3, min(len(lines), i + 8)):
                context_after.append((j + 1, lines[j].strip()))
            
            session_pop_groups.append({
                'id': len(session_pop_groups) + 1,
                'start_line': i + 1,  # 1-based
                'end_line': i + 3,    # 1-based
                'lines': [
                    lines[i].strip(),
                    lines[i + 1].strip(),
                    lines[i + 2].strip()
                ],
                'context_before': context_before,
                'context_after': context_after,
                'indent_level': len(lines[i]) - len(lines[i].lstrip()),
                'function_context': None,  # 後で設定
                'safety_score': 0  # 後で計算
            })
            i += 3  # スキップ
        else:
            i += 1
    
    print(f"発見された残存箇所: {len(session_pop_groups)}箇所")
    
    if len(session_pop_groups) == 0:
        print("✅ 全て置換完了")
        return True
    
    # 3. 各箇所の詳細分析
    print("\n📋 各箇所の詳細分析:")
    
    for group in session_pop_groups:
        print(f"\n--- 箇所 {group['id']} ---")
        print(f"位置: 行{group['start_line']}-{group['end_line']}")
        print(f"インデント: {group['indent_level']}文字")
        
        # 関数コンテキストの特定
        function_name = "不明"
        for line_no, line_content in group['context_before']:
            if 'def ' in line_content and '(' in line_content:
                function_name = line_content.split('def ')[1].split('(')[0].strip()
                break
        
        group['function_context'] = function_name
        print(f"関数コンテキスト: {function_name}")
        
        # 前後コンテキストの表示
        print("前のコンテキスト:")
        for line_no, line_content in group['context_before'][-2:]:  # 直前2行
            print(f"  行{line_no}: {line_content}")
        
        print("対象行:")
        for i, line in enumerate(group['lines']):
            print(f"  行{group['start_line'] + i}: {line}")
        
        print("後のコンテキスト:")
        for line_no, line_content in group['context_after'][:2]:  # 直後2行
            print(f"  行{line_no}: {line_content}")
    
    # 4. 安全性スコアの計算
    print("\n🔒 安全性スコア計算:")
    
    for group in session_pop_groups:
        score = 100  # 基本スコア
        
        # 危険要因の減点
        safety_factors = []
        
        # インデントレベルが深い（複雑な処理内）
        if group['indent_level'] > 20:
            score -= 10
            safety_factors.append("深いインデント")
        
        # 前後に危険なキーワード
        all_context = [line for _, line in group['context_before'] + group['context_after']]
        dangerous_keywords = ['import', 'global', 'exec', 'eval', 'compile']
        
        for keyword in dangerous_keywords:
            if any(keyword in line for line in all_context):
                score -= 20
                safety_factors.append(f"危険キーワード: {keyword}")
        
        # 例外処理内
        if any('except' in line or 'try:' in line for _, line in group['context_before']):
            score -= 5
            safety_factors.append("例外処理内")
        
        # ループ内
        if any('for ' in line or 'while ' in line for _, line in group['context_before']):
            score -= 5
            safety_factors.append("ループ内")
        
        group['safety_score'] = max(0, score)
        group['safety_factors'] = safety_factors
        
        print(f"箇所 {group['id']}: スコア {group['safety_score']}/100")
        if safety_factors:
            print(f"  減点要因: {', '.join(safety_factors)}")
        else:
            print("  減点要因: なし")
    
    # 5. 推奨置換順序の決定
    print("\n🎯 推奨置換順序:")
    
    # 安全性スコア順でソート
    sorted_groups = sorted(session_pop_groups, key=lambda x: (-x['safety_score'], x['start_line']))
    
    for i, group in enumerate(sorted_groups, 1):
        risk_level = "低リスク" if group['safety_score'] >= 90 else \
                    "中リスク" if group['safety_score'] >= 70 else "高リスク"
        
        print(f"{i}. 箇所{group['id']} (行{group['start_line']}-{group['end_line']})")
        print(f"   安全性: {group['safety_score']}/100 ({risk_level})")
        print(f"   関数: {group['function_context']}")
        print(f"   推奨: {'即座に置換可' if group['safety_score'] >= 90 else '慎重に置換' if group['safety_score'] >= 70 else '最後に置換'}")
    
    # 6. 次の置換対象の推奨
    print("\n🚀 次の置換対象推奨:")
    
    next_target = sorted_groups[0]
    print(f"推奨: 箇所{next_target['id']} (行{next_target['start_line']}-{next_target['end_line']})")
    print(f"理由: 最高安全性スコア {next_target['safety_score']}/100")
    print(f"関数: {next_target['function_context']}")
    
    # 7. 全体戦略
    print("\n📋 全体戦略:")
    
    high_safety = [g for g in session_pop_groups if g['safety_score'] >= 90]
    medium_safety = [g for g in session_pop_groups if 70 <= g['safety_score'] < 90]
    low_safety = [g for g in session_pop_groups if g['safety_score'] < 70]
    
    print(f"高安全性 (90+): {len(high_safety)}箇所 - 優先置換")
    print(f"中安全性 (70-89): {len(medium_safety)}箇所 - 慎重に置換")
    print(f"低安全性 (70未満): {len(low_safety)}箇所 - 最後に置換")
    
    # 8. リスク分析
    print("\n⚠️ リスク分析:")
    
    total_risk_factors = []
    for group in session_pop_groups:
        total_risk_factors.extend(group['safety_factors'])
    
    if not total_risk_factors:
        print("✅ 特別なリスク要因なし - 安全に進行可能")
        risk_level = "LOW"
    elif len(total_risk_factors) <= 2:
        print("⚠️ 軽微なリスク要因あり - 慎重に進行")
        risk_level = "MEDIUM"
    else:
        print("🚨 複数のリスク要因あり - 特に慎重に進行")
        risk_level = "HIGH"
    
    unique_risks = list(set(total_risk_factors))
    for risk in unique_risks:
        count = total_risk_factors.count(risk)
        print(f"  {risk}: {count}箇所")
    
    print(f"\n✅ 残り箇所分析完了")
    print(f"📊 総合リスクレベル: {risk_level}")
    print(f"🎯 次の推奨: 箇所{next_target['id']}の第3段階置換")
    
    return {
        'remaining_groups': session_pop_groups,
        'next_target': next_target,
        'risk_level': risk_level,
        'total_remaining': len(session_pop_groups)
    }

if __name__ == "__main__":
    result = ultra_safe_remaining_analysis()
    if result and isinstance(result, dict):
        print(f"\n分析結果: {result['total_remaining']}箇所残存")
        print(f"リスクレベル: {result['risk_level']}")
    else:
        print(f"\n完了または分析失敗")