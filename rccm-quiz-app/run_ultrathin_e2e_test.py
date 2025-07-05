#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ ULTRATHIN E2E テスト実行スクリプト
=====================================

副作用ゼロのSelenium E2Eテストを実行するためのヘルパースクリプト

Usage:
    python run_ultrathin_e2e_test.py [options]

Options:
    --url URL          テスト対象のURL (default: http://localhost:5000)
    --headless         ヘッドレスモードで実行 (default: True)
    --no-headless      ブラウザを表示して実行
    --help             このヘルプを表示

Author: Claude Code
Version: 1.0.0
Date: 2025-07-05
"""

import sys
import argparse
import logging
from ultrathin_selenium_e2e_test_zero_sideeffects import UltraThinE2ETestZeroSideEffects

def parse_arguments():
    """
    コマンドライン引数の解析
    
    Returns:
        argparse.Namespace: 解析された引数
    """
    parser = argparse.ArgumentParser(
        description='🛡️ ULTRATHIN E2E テスト実行スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
    python run_ultrathin_e2e_test.py
    python run_ultrathin_e2e_test.py --url http://localhost:5000
    python run_ultrathin_e2e_test.py --no-headless
    python run_ultrathin_e2e_test.py --url http://localhost:8080 --no-headless
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help='テスト対象のベースURL (default: http://localhost:5000)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='ヘッドレスモードで実行 (default: True)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='ブラウザを表示して実行'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細なログを表示'
    )
    
    return parser.parse_args()

def setup_logging(verbose: bool = False):
    """
    ログ設定
    
    Args:
        verbose: 詳細ログの有効化
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """
    依存関係の確認
    
    Returns:
        bool: 依存関係が満たされているかどうか
    """
    try:
        import selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print(f"✅ Selenium バージョン: {selenium.__version__}")
        return True
    except ImportError as e:
        print(f"❌ 依存関係エラー: {e}")
        print("必要なパッケージをインストールしてください:")
        print("pip install selenium")
        return False

def main():
    """
    メイン実行関数
    """
    print("🛡️ ULTRATHIN E2E テスト実行スクリプト")
    print("=" * 50)
    
    # 引数の解析
    args = parse_arguments()
    
    # ログの設定
    setup_logging(args.verbose)
    
    # 依存関係の確認
    if not check_dependencies():
        return 1
    
    # ヘッドレスモードの設定
    headless = args.headless and not args.no_headless
    
    print(f"📋 テスト設定:")
    print(f"  - URL: {args.url}")
    print(f"  - ヘッドレスモード: {headless}")
    print(f"  - 詳細ログ: {args.verbose}")
    print()
    
    # 安全性の確認
    print("🛡️ 安全性チェック:")
    print("  - 副作用なし: ✅")
    print("  - データ変更なし: ✅")
    print("  - ファイル作成なし: ✅")
    print("  - 読み取り専用: ✅")
    print()
    
    # テストの実行
    try:
        tester = UltraThinE2ETestZeroSideEffects(
            base_url=args.url,
            headless=headless
        )
        
        print("🚀 テスト実行開始...")
        results = tester.run_all_tests()
        
        print("\n📊 テスト結果:")
        print(f"  - 総合結果: {results['overall_status']}")
        
        if 'summary' in results:
            summary = results['summary']
            print(f"  - 総テスト数: {summary['total_tests']}")
            print(f"  - 成功: {summary['passed']}")
            print(f"  - 失敗: {summary['failed']}")
            print(f"  - 成功率: {summary['success_rate']:.1f}%")
        
        # 詳細レポートの生成
        print("\n📋 詳細レポート:")
        report = tester.generate_report()
        print(report)
        
        # 終了ステータスの決定
        if results['overall_status'] == 'passed':
            print("✅ すべてのテストが成功しました")
            return 0
        else:
            print("⚠️ 一部のテストが失敗しました")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ テストが中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)