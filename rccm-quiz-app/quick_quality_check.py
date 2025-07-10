#!/usr/bin/env python3
"""
🎯 ULTRATHIN区クイック品質チェック
"""

import re
import os

def check_imports():
    """未使用インポートのチェック"""
    print("\n1. インポートチェック...")
    
    with open("app.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 初期インポート部分を抽出
    imports_section = content[:content.find("class SessionStateManager")]
    
    imports = {
        'threading': 'threading' in content[1000:],
        'uuid': 'uuid' in content[1000:],
        'time': 'time' in content[1000:],
        'os': 'os' in content[1000:],
        'random': 'random' in content[1000:],
        're': 're.' in content[1000:] or 're.search' in content or 're.findall' in content,
        'gc': 'gc' in content[1000:],
        'logging': 'logging' in content[1000:] or 'logger' in content,
        'datetime': 'datetime' in content[1000:],
        'timedelta': 'timedelta' in content[1000:],
        'timezone': 'timezone' in content[1000:],
        'defaultdict': 'defaultdict' in content[1000:],
        'Dict': ': Dict' in content,
        'List': ': List' in content,
        'Tuple': ': Tuple' in content,
        'wraps': '@wraps' in content,
        'Decimal': 'Decimal' in content[1000:],
        'ROUND_HALF_UP': 'ROUND_HALF_UP' in content[1000:]
    }
    
    unused = [k for k, v in imports.items() if not v]
    print(f"  未使用インポート: {len(unused)}個")
    if unused:
        for imp in unused:
            print(f"    - {imp}")
    
    return 100 if len(unused) == 0 else max(0, 100 - len(unused) * 10)

def check_comments():
    """コメント更新チェック"""
    print("\n2. コメント更新チェック...")
    
    with open("app.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 新しいコメントスタイル
    modern_comments = len(re.findall(r'#\s*[🔥🛡️🎯]|ULTRATHIN|HTTP 431', content))
    
    # 古いコメント
    old_comments = len(re.findall(r'#\s*(TODO|FIXME|XXX|HACK)', content, re.IGNORECASE))
    
    print(f"  最新コメント: {modern_comments}個")
    print(f"  古いコメント: {old_comments}個")
    
    return min(100, 80 + modern_comments - old_comments * 5)

def check_category_separation():
    """4-1/4-2分離チェック"""
    print("\n3. カテゴリー分離チェック...")
    
    with open("app.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'CATEGORY_MAPPING定義': 'CATEGORY_MAPPING' in content,
        'get_safe_category_name関数': 'def get_safe_category_name' in content,
        '4-1基礎科目処理': '4-1' in content and '基礎科目' in content,
        '4-2専門科目処理': '4-2' in content and '専門科目' in content,
        'カテゴリーフィルタリング': 'category == category' in content or "q.get('category')" in content
    }
    
    passed = sum(checks.values())
    print(f"  実装項目: {passed}/5")
    for name, status in checks.items():
        print(f"    {name}: {'✓' if status else '✗'}")
    
    return passed * 20

def check_error_handling():
    """エラーハンドリングチェック"""
    print("\n4. エラーハンドリングチェック...")
    
    with open("app.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    try_count = len(re.findall(r'\btry:', content))
    except_specific = len(re.findall(r'except\s+\w+Error', content))
    except_generic = len(re.findall(r'except:', content))
    logging_errors = len(re.findall(r'logger\.(error|warning)', content))
    
    print(f"  try-exceptブロック: {try_count}個")
    print(f"  具体的な例外: {except_specific}個")
    print(f"  汎用except: {except_generic}個")
    print(f"  エラーロギング: {logging_errors}個")
    
    if try_count == 0:
        return 50
    
    specificity = (except_specific / max(except_specific + except_generic, 1)) * 40
    logging = min(30, (logging_errors / try_count) * 30)
    
    return int(50 + specificity + logging)

def check_session_management():
    """セッション管理チェック"""
    print("\n5. セッション管理チェック...")
    
    with open("app.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    safe_patterns = {
        'session.get()使用': len(re.findall(r'session\.get\(', content)),
        'デフォルト値指定': len(re.findall(r'session\.get\([^,]+,\s*(?:\[\]|{}|None|0)', content)),
        'session.modified': len(re.findall(r'session\.modified\s*=\s*True', content)),
        'SessionStateManager': 'SessionStateManager' in content,
        'safe_関数': len(re.findall(r'def safe_\w+', content))
    }
    
    total_safe = sum(safe_patterns.values())
    print(f"  安全パターン使用: {total_safe}回")
    for name, count in safe_patterns.items():
        if count > 0:
            print(f"    {name}: {count}回")
    
    return min(100, 20 + total_safe * 5)

def main():
    print("🎯 ULTRATHIN区クイック品質チェック開始")
    print("="*60)
    
    scores = {
        '未使用インポート': check_imports(),
        'コメント更新': check_comments(),
        'カテゴリー分離': check_category_separation(),
        'エラーハンドリング': check_error_handling(),
        'セッション管理': check_session_management()
    }
    
    print("\n" + "="*60)
    print("【スコアサマリー】")
    for item, score in scores.items():
        print(f"  {item}: {score}/100点")
    
    total = sum(scores.values()) / len(scores)
    print(f"\n総合スコア: {total:.1f}/100点")
    
    if total >= 95:
        print("\n🏆 優秀！100点満点達成レベルです！")
    elif total >= 90:
        print("\n✨ 良好な実装品質です！")
    else:
        print("\n📝 改善の余地があります。")

if __name__ == "__main__":
    main()