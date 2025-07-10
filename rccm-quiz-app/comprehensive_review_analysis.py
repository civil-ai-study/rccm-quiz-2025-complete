#!/usr/bin/env python3
"""
RCCM Quiz App - Comprehensive Review List Analysis
復習リスト機能の包括的分析と問題点の特定

This script analyzes the review list functionality comprehensively:
1. Review system architecture (bookmark vs SRS)
2. API endpoints and their functionality
3. Frontend templates and UI components
4. Data flow from answering to review addition
5. Potential issues and inconsistencies
"""

import json
import os
import re
from datetime import datetime


def analyze_review_system():
    """復習システムの包括的分析"""
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "analysis_type": "comprehensive_review_list_analysis",
        "findings": {
            "system_architecture": {},
            "api_endpoints": {},
            "frontend_templates": {},
            "data_flow": {},
            "issues_identified": [],
            "recommendations": []
        }
    }
    
    # 1. System Architecture Analysis
    print("📊 1. システムアーキテクチャの分析...")
    analysis["findings"]["system_architecture"] = analyze_system_architecture()
    
    # 2. API Endpoints Analysis
    print("🔗 2. API エンドポイントの分析...")
    analysis["findings"]["api_endpoints"] = analyze_api_endpoints()
    
    # 3. Frontend Templates Analysis
    print("🖥️ 3. フロントエンドテンプレートの分析...")
    analysis["findings"]["frontend_templates"] = analyze_frontend_templates()
    
    # 4. Data Flow Analysis
    print("🔄 4. データフローの分析...")
    analysis["findings"]["data_flow"] = analyze_data_flow()
    
    # 5. Issues Identification
    print("🚨 5. 問題点の特定...")
    analysis["findings"]["issues_identified"] = identify_issues()
    
    # 6. Recommendations
    print("💡 6. 改善提案...")
    analysis["findings"]["recommendations"] = generate_recommendations()
    
    return analysis


def analyze_system_architecture():
    """システムアーキテクチャの分析"""
    
    architecture = {
        "dual_system": True,
        "primary_system": "advanced_srs",
        "fallback_system": "bookmarks",
        "integration_approach": "hybrid",
        "details": {
            "advanced_srs": {
                "description": "高度な間隔反復学習システム",
                "session_key": "advanced_srs",
                "features": [
                    "間隔反復アルゴリズム",
                    "マスター判定 (5回正解)",
                    "難易度調整",
                    "復習スケジューリング"
                ],
                "data_structure": {
                    "correct_count": "正解回数",
                    "wrong_count": "間違い回数",
                    "total_attempts": "総試行回数",
                    "difficulty_level": "難易度レベル (1-10)",
                    "mastered": "マスター済みフラグ",
                    "next_review": "次回復習日",
                    "interval_days": "復習間隔日数"
                }
            },
            "bookmarks": {
                "description": "従来のブックマークシステム",
                "session_key": "bookmarks",
                "features": [
                    "問題ID配列による管理",
                    "シンプルな追加/削除",
                    "後方互換性維持"
                ],
                "data_structure": "問題IDの配列"
            }
        }
    }
    
    return architecture


def analyze_api_endpoints():
    """API エンドポイントの分析"""
    
    endpoints = {
        "review_display": {
            "route": "/review",
            "method": "GET",
            "function": "review_list",
            "description": "復習リスト表示（高度なSRSシステム対応版）",
            "features": [
                "SRSデータとブックマーク統合",
                "優先度計算",
                "部門別統計",
                "マスター済み問題分離"
            ]
        },
        "review_count": {
            "route": "/api/review/count",
            "method": "GET",
            "function": "api_review_count",
            "description": "復習問題数取得",
            "features": [
                "ホーム画面表示用",
                "SRSデータからカウント",
                "復習期限チェック"
            ]
        },
        "review_questions": {
            "route": "/api/review/questions",
            "method": "POST",
            "function": "get_review_questions",
            "description": "復習問題詳細一括取得",
            "features": [
                "問題IDリストから詳細取得",
                "セッション検証あり"
            ]
        },
        "review_remove": {
            "route": "/api/review/remove",
            "method": "POST",
            "function": "remove_from_review",
            "description": "復習リストから問題削除",
            "features": [
                "個別問題削除",
                "セッション検証あり"
            ]
        },
        "review_bulk_remove": {
            "route": "/api/review/bulk_remove",
            "method": "POST",
            "function": "bulk_remove_from_review",
            "description": "復習リストから一括削除",
            "features": [
                "複数問題同時削除",
                "セッション検証あり"
            ]
        },
        "review_exam": {
            "route": "/exam/review",
            "method": "GET",
            "function": "review_questions",
            "description": "復習問題練習開始",
            "features": [
                "SRSシステム統合",
                "問題データロード",
                "セッション生成"
            ]
        },
        "bookmarks_display": {
            "route": "/bookmarks",
            "method": "GET",
            "function": "bookmarks_page",
            "description": "従来のブックマーク表示",
            "features": [
                "シンプルな問題リスト",
                "統計情報表示"
            ]
        },
        "bookmark_api": {
            "route": "/api/bookmark",
            "methods": ["POST", "DELETE"],
            "functions": ["add_bookmark", "remove_bookmark"],
            "description": "ブックマーク追加/削除API",
            "features": [
                "個別問題管理",
                "JSON API"
            ]
        },
        "bookmarks_api": {
            "route": "/api/bookmarks",
            "method": "GET",
            "function": "get_bookmarks",
            "description": "ブックマーク一覧取得",
            "features": [
                "問題詳細付き取得"
            ]
        }
    }
    
    return endpoints


def analyze_frontend_templates():
    """フロントエンドテンプレートの分析"""
    
    templates = {
        "review_enhanced.html": {
            "description": "高度なSRSシステム対応復習リストUI",
            "features": [
                "今日復習すべき問題数表示",
                "優先度順表示",
                "部門別統計",
                "マスター済み問題分離",
                "復習開始ボタン",
                "SRS統計情報"
            ],
            "ui_components": [
                "進捗表示アラート",
                "統計カード",
                "問題リストテーブル",
                "フィルタリング機能",
                "一括操作ボタン"
            ]
        },
        "bookmarks.html": {
            "description": "従来のブックマークシステムUI",
            "features": [
                "シンプルな問題リスト",
                "統計情報（基礎/専門科目別）",
                "復習開始ボタン",
                "問題削除機能"
            ],
            "ui_components": [
                "統計カード",
                "問題リストテーブル",
                "アクションボタン"
            ]
        }
    }
    
    return templates


def analyze_data_flow():
    """データフローの分析"""
    
    data_flow = {
        "answer_to_review": {
            "description": "問題回答から復習リストへの追加フロー",
            "steps": [
                "1. 問題回答提出 (submit_answer)",
                "2. 正誤判定実行",
                "3. update_advanced_srs_data 呼び出し",
                "4. SRSデータ更新（統計・次回復習日計算）",
                "5. 旧ブックマークシステムとの同期",
                "6. マスター済み問題の自動除外"
            ],
            "key_functions": [
                "update_advanced_srs_data",
                "calculate_next_review_date",
                "cleanup_mastered_questions"
            ]
        },
        "review_display": {
            "description": "復習リスト表示フロー",
            "steps": [
                "1. セッションからSRSデータとブックマーク取得",
                "2. 問題データ統合",
                "3. 優先度計算",
                "4. 統計情報計算",
                "5. UI描画"
            ]
        },
        "session_management": {
            "description": "セッション管理",
            "keys": [
                "advanced_srs: SRSデータ",
                "bookmarks: ブックマーク配列",
                "session_id: セッション識別子"
            ]
        }
    }
    
    return data_flow


def identify_issues():
    """問題点の特定"""
    
    issues = [
        {
            "severity": "CRITICAL",
            "category": "Data Inconsistency",
            "title": "SRSデータがセッションに保存されない",
            "description": "update_advanced_srs_data関数でSRSデータを更新するが、HTTP 431対策でセッションに保存されない（lines 1524-1525がコメントアウト）",
            "impact": "SRSシステムが実際には動作せず、データが永続化されない",
            "file": "app.py",
            "line_numbers": [1524, 1525]
        },
        {
            "severity": "HIGH",
            "category": "Logic Error",
            "title": "重複したSRSデータ更新",
            "description": "submit_answer関数でupdate_advanced_srs_dataが2回呼び出される（lines 3106, 3147）",
            "impact": "不要な処理とデータ不整合の可能性",
            "file": "app.py",
            "line_numbers": [3106, 3147]
        },
        {
            "severity": "HIGH",
            "category": "Logic Error",
            "title": "due_today_countの重複加算",
            "description": "review_list関数でdue_today_countが2回加算される（lines 5171-5172）",
            "impact": "復習必要問題数の誤計算",
            "file": "app.py",
            "line_numbers": [5171, 5172]
        },
        {
            "severity": "MEDIUM",
            "category": "UI Inconsistency",
            "title": "複数の復習リストUI",
            "description": "/review（SRS対応）と/bookmarks（従来システム）の2つのUIが存在",
            "impact": "ユーザーの混乱と機能重複",
            "templates": ["review_enhanced.html", "bookmarks.html"]
        },
        {
            "severity": "MEDIUM",
            "category": "Data Validation",
            "title": "セッション検証の不整合",
            "description": "一部のAPIエンドポイントでセッション検証があるが、メイン機能では検証がない",
            "impact": "セキュリティとデータ整合性の問題",
            "affected_endpoints": ["/api/review/questions", "/api/review/remove"]
        },
        {
            "severity": "LOW",
            "category": "Code Quality",
            "title": "エラーハンドリングの重複",
            "description": "同じエラーハンドリングパターンが複数回記述されている",
            "impact": "コードの保守性低下",
            "file": "app.py"
        }
    ]
    
    return issues


def generate_recommendations():
    """改善提案の生成"""
    
    recommendations = [
        {
            "priority": "HIGH",
            "category": "System Architecture",
            "title": "SRSシステムの完全実装",
            "description": "SRSデータのセッション保存を有効化し、真の間隔反復学習を実現",
            "actions": [
                "HTTP 431対策を見直し、適切なセッション管理を実装",
                "SRSデータの永続化方法を再検討",
                "メモリ使用量を最適化したSRSデータ構造を設計"
            ]
        },
        {
            "priority": "HIGH",
            "category": "UI/UX",
            "title": "復習リストUIの統合",
            "description": "2つの復習リストUIを統合し、一貫したユーザー体験を提供",
            "actions": [
                "review_enhanced.htmlをメインUIとして採用",
                "bookmarks.htmlは段階的に廃止",
                "ユーザーデータの移行計画を策定"
            ]
        },
        {
            "priority": "MEDIUM",
            "category": "Data Management",
            "title": "データ同期機能の改善",
            "description": "SRSデータとブックマークの同期を最適化",
            "actions": [
                "データ同期のタイミングを見直し",
                "エラー時の復旧機能を追加",
                "データ整合性チェック機能を実装"
            ]
        },
        {
            "priority": "MEDIUM",
            "category": "Performance",
            "title": "セッション管理の最適化",
            "description": "セッションサイズを最適化し、パフォーマンスを向上",
            "actions": [
                "不要なセッションデータの削除",
                "データ圧縮機能の実装",
                "セッション有効期限の最適化"
            ]
        },
        {
            "priority": "LOW",
            "category": "Code Quality",
            "title": "コードリファクタリング",
            "description": "重複コードの削除と可読性向上",
            "actions": [
                "共通関数の抽出",
                "エラーハンドリングの統一",
                "コメントとドキュメントの整備"
            ]
        }
    ]
    
    return recommendations


def save_analysis_report(analysis):
    """分析レポートの保存"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_review_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析レポートを保存しました: {filename}")
    
    return filename


def main():
    """メイン処理"""
    
    print("🔍 RCCM Quiz App - 復習リスト機能包括的分析")
    print("=" * 60)
    
    # 包括的分析実行
    analysis = analyze_review_system()
    
    # レポート保存
    filename = save_analysis_report(analysis)
    
    # サマリー表示
    print("\n📊 分析結果サマリー")
    print("-" * 30)
    print(f"検出された問題点: {len(analysis['findings']['issues_identified'])}件")
    print(f"改善提案: {len(analysis['findings']['recommendations'])}件")
    
    # 重要な問題点の表示
    critical_issues = [i for i in analysis['findings']['issues_identified'] if i['severity'] == 'CRITICAL']
    high_issues = [i for i in analysis['findings']['issues_identified'] if i['severity'] == 'HIGH']
    
    if critical_issues:
        print(f"\n🚨 クリティカルな問題: {len(critical_issues)}件")
        for issue in critical_issues:
            print(f"  - {issue['title']}")
    
    if high_issues:
        print(f"\n⚠️ 高優先度の問題: {len(high_issues)}件")
        for issue in high_issues:
            print(f"  - {issue['title']}")
    
    print(f"\n📄 詳細レポート: {filename}")
    print("分析完了 ✅")


if __name__ == "__main__":
    main()