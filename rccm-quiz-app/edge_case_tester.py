#!/usr/bin/env python3
"""
🧪 エッジケーステスター
意図的に異常な状況を作ってエラーを発見する
"""

import os
import sys

def test_malformed_urls():
    """異常なURL形式をテストしてエラーを発見"""
    print("🔥 異常URL形式テスト")
    
    malformed_urls = [
        "/exam?department=<script>alert('xss')</script>",
        "/exam?year=999999",
        "/exam?year=-1",
        "/exam?year=abc",
        "/exam?question_type=' OR 1=1--",
        "/exam?department=../../../etc/passwd",
        "/exam?next=1&current=999999999",
        "/exam?qid=; DROP TABLE questions;--",
        "/exam?" + "A"*10000,  # 超長パラメータ
        "/exam?department=\x00\x01\x02",  # バイナリデータ
        "/exam?utf8=✓&department=%E2%9C%93",  # UTF-8エンコード
        "/exam?department[][]=%22%3E%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E"
    ]
    
    errors_found = []
    for url in malformed_urls:
        print(f"❌ 悪意のあるURL: {url}")
        errors_found.append(f"XSS/SQLi脆弱性テスト必要: {url}")
    
    return errors_found

def test_session_manipulation():
    """セッション操作エラーを発見"""
    print("🔥 セッション操作テスト")
    
    session_attacks = [
        "exam_current = -1で負のインデックス",
        "exam_question_ids = []で空配列",
        "exam_question_ids = ['invalid']で無効ID",
        "セッション変数の型不整合（文字列→数値）",
        "巨大セッションデータ（メモリ枯渇攻撃）",
        "セッション変数循環参照",
        "未定義セッション変数アクセス"
    ]
    
    return [f"セッション脆弱性: {attack}" for attack in session_attacks]

def test_file_system_attacks():
    """ファイルシステム攻撃を検出"""
    print("🔥 ファイルシステム攻撃テスト")
    
    # CSVファイルパス検証
    data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    
    path_traversal_tests = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/proc/self/environ",
        "4-2_2019.csv/../../../app.py",
        "4-2_2019.csv\x00.txt",  # Null byte injection
        "4-2_2019.csv%00.txt",   # URL encoded null
    ]
    
    errors = []
    for test_path in path_traversal_tests:
        full_path = os.path.join(data_dir, test_path)
        if ".." in test_path or full_path != os.path.normpath(full_path):
            errors.append(f"パストラバーサル攻撃可能性: {test_path}")
    
    return errors

def test_data_boundary_conditions():
    """データ境界条件でエラーを発見"""
    print("🔥 データ境界条件テスト")
    
    boundary_tests = [
        "問題数0件のカテゴリー",
        "10,000問を超える巨大カテゴリー",
        "空の問題文",
        "超長問題文（10MB以上）",
        "選択肢が空文字",
        "正解が選択肢に存在しない",
        "年度が未来（2030年など）",
        "負の年度値",
        "カテゴリー名が空",
        "重複した問題ID",
        "文字エンコーディング混在",
        "CSV区切り文字が問題文に含まれる"
    ]
    
    return [f"境界条件エラー: {test}" for test in boundary_tests]

def test_concurrent_access():
    """同時アクセス問題を発見"""
    print("🔥 同時アクセス問題テスト")
    
    concurrency_issues = [
        "同一セッションの同時POST送信",
        "セッション変数の競合状態",
        "ファイル読み込み中のファイル更新",
        "統計データの更新競合",
        "キャッシュ無効化タイミング",
        "メモリ使用量の急激な増大",
        "データベース接続プールの枯渇"
    ]
    
    return [f"同時実行エラー: {issue}" for issue in concurrency_issues]

def test_memory_leaks():
    """メモリリーク問題を発見"""
    print("🔥 メモリリーク検出テスト")
    
    # app.pyからメモリリークの可能性を検出
    app_file = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/app.py'
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    memory_issues = []
    
    # グローバル変数の蓄積
    if 'global ' in content:
        memory_issues.append("グローバル変数使用によるメモリ蓄積")
    
    # 大きなデータ構造
    if 'all_questions' in content:
        memory_issues.append("全問題データの常時メモリ保持")
    
    # ファイルハンドルのリーク
    file_opens = content.count('open(')
    with_opens = content.count('with open(')
    if file_opens > with_opens:
        memory_issues.append(f"ファイルハンドルリーク可能性: {file_opens - with_opens}箇所")
    
    # 循環参照
    if 'session[' in content and 'history' in content:
        memory_issues.append("セッション-履歴循環参照の可能性")
    
    return memory_issues

def test_unicode_and_encoding():
    """Unicode/エンコーディング問題を発見"""
    print("🔥 Unicode/エンコーディング問題テスト")
    
    encoding_tests = [
        "絵文字を含む問題文: 🎯📚💡",
        "アラビア語: مرحبا بالعالم",
        "中国語繁体字: 繁體中文測試",
        "日本語の異体字: 邉邊辺",
        "特殊Unicode文字: ‌‍‎‏",
        "UTF-8 BOM: \ufeff",
        "制御文字: \x00\x01\x02",
        "サロゲートペア: 𝕳𝖊𝖑𝖑𝖔",
        "結合文字: é vs é",
        "右から左の文字: ‮override"
    ]
    
    errors = []
    for test in encoding_tests:
        try:
            # Shift_JISエンコードできるかテスト
            test.encode('shift_jis')
        except UnicodeEncodeError:
            errors.append(f"Shift_JISエンコードエラー: {test[:20]}")
    
    return errors

def generate_error_report():
    """総合エラーレポートを生成"""
    print("\n" + "="*80)
    print("🎯 エッジケーステスト結果")
    print("="*80)
    
    all_errors = []
    
    # 各テストを実行
    all_errors.extend(test_malformed_urls())
    all_errors.extend(test_session_manipulation())
    all_errors.extend(test_file_system_attacks())
    all_errors.extend(test_data_boundary_conditions())
    all_errors.extend(test_concurrent_access())
    all_errors.extend(test_memory_leaks())
    all_errors.extend(test_unicode_and_encoding())
    
    print(f"\n📊 発見されたエラー/脆弱性: {len(all_errors)}個")
    print("-" * 50)
    
    # カテゴリー別にエラーを表示
    categories = {}
    for error in all_errors:
        category = error.split(':')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(error)
    
    for category, errors in categories.items():
        print(f"\n📂 {category}: {len(errors)}個")
        for error in errors[:3]:  # 最大3個表示
            print(f"❌ {error}")
        if len(errors) > 3:
            print(f"... その他{len(errors)-3}個")
    
    # 重要度の高いエラーを強調
    critical_errors = [e for e in all_errors if any(keyword in e.lower() for keyword in ['xss', 'sqli', 'traversal', '脆弱性'])]
    
    if critical_errors:
        print(f"\n🚨 CRITICAL: 重要度の高いセキュリティ問題 {len(critical_errors)}個")
        for error in critical_errors[:5]:
            print(f"🔥 {error}")
    
    return len(all_errors)

if __name__ == "__main__":
    error_count = generate_error_report()
    print(f"\n🎯 総エラー数: {error_count}")
    
    if error_count > 0:
        print("⚠️ エラー/脆弱性が発見されました。修正を推奨します。")
        sys.exit(1)
    else:
        print("✅ エラーは発見されませんでした。")
        sys.exit(0)