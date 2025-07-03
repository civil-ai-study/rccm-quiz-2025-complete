#!/usr/bin/env python3
"""
RCCM試験問題集アプリ専門分野混在問題の根本原因分析レポート
詳細なコード解析とデータフロー図による包括的調査
"""

def analyze_root_cause():
    """
    専門分野12分野選択時の他分野問題混在問題の根本原因分析
    """
    
    analysis = {
        "問題の概要": {
            "現象": "専門分野（例：道路）を選択しても他分野（土質、鋼構造等）の問題が混在して出題される",
            "影響": "学習効率の低下、試験対策の効果減少、ユーザビリティの著しい悪化",
            "重要度": "極めて高い（アプリの基本機能に関わる致命的バグ）"
        },
        
        "根本原因分析": {
            "1. なぜ混在したのか（プログラミングロジックの問題点）": {
                "主要原因": "部門IDと日本語カテゴリ名の不適切なマッピング処理",
                "詳細説明": [
                    "英語部門ID（'road', 'tunnel'等）と日本語カテゴリ名（'道路', 'トンネル'等）の変換処理が不完全",
                    "get_mixed_questions関数内の専門科目フィルタリング条件が曖昧",
                    "カテゴリマッチングロジックでの完全一致判定の失敗",
                    "部門指定時のフォールバック処理が他分野問題を含んでしまう"
                ],
                "技術的要因": [
                    "DEPARTMENT_TO_CATEGORY_MAPPINGの部分的な適用",
                    "question_type='specialist'での部門フィルタが条件分岐内でのみ実行",
                    "URLパラメータから渡される部門情報の型不整合（英語ID vs 日本語名）"
                ]
            },
            
            "2. 具体的なコード箇所と処理フロー": {
                "主要問題箇所": [
                    {
                        "ファイル": "app.py",
                        "関数": "get_mixed_questions",
                        "行数": "1112-1143",
                        "問題": "専門科目の部門フィルタリングが条件分岐内でのみ実行される",
                        "コード例": """
if question_type == 'specialist' and department:
    # 部門フィルタが専門科目かつ部門指定がある場合のみ実行
    target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(department, department)
    dept_match_questions = [q for q in available_questions
                           if q.get('category') == target_category]
    if dept_match_questions:
        available_questions = dept_match_questions  # ここで正常にフィルタされる
    else:
        # フィルタ失敗時に他分野問題が混在する原因
        logger.warning(f"部門マッチング失敗")
                        """
                    },
                    {
                        "ファイル": "app.py", 
                        "関数": "exam (GET処理)",
                        "行数": "2306-2317",
                        "問題": "URLパラメータの部門情報処理で型変換が不適切",
                        "コード例": """
if requested_category != '共通':
    requested_question_type = 'specialist'
    if not requested_department:
        # departmentが未設定時にカテゴリを部門として使用
        requested_department = requested_category  # 日本語名が設定される
                        """
                    }
                ],
                
                "問題のあるデータフロー": """
1. ユーザーが「道路」専門分野を選択
2. /exam?question_type=specialist&department=road でリクエスト
3. get_mixed_questions内で部門フィルタリング実行
4. DEPARTMENT_TO_CATEGORY_MAPPING['road'] = '道路' でカテゴリ変換
5. available_questions を category='道路' でフィルタ
6. マッチング成功時は道路問題のみ選択
7. マッチング失敗時（カテゴリ名不一致等）は全問題から選択
8. 結果として他分野問題が混在
                """
            },
            
            "3. 共通問題（4-1基礎問題）の動作確認": {
                "動作状況": "正常に動作している",
                "理由": [
                    "4-1.csvの全問題でcategory='共通'に統一されている",
                    "question_type='basic'の判定が確実に機能", 
                    "年度指定なし（year=None）の条件が正確に処理される",
                    "部門フィルタリングが基礎科目では実行されない"
                ],
                "CSVデータ確認": "4-1.csv: 全問題がcategory='共通', question_type='basic'に統一"
            },
            
            "4. 修正前と修正後の動作の違い": {
                "修正前の問題動作": [
                    "専門分野選択後、他分野問題が混在して出題",
                    "カテゴリマッチング失敗時のフォールバック処理で全問題対象化",
                    "部門フィルタリング条件の不適切な分岐",
                    "ログには警告が出力されるが実際の問題選択は混在状態"
                ],
                "修正後の期待動作": [
                    "専門分野選択時は該当分野の問題のみ厳格に出題",
                    "カテゴリマッチング失敗時は問題不足エラーを適切に表示", 
                    "部門フィルタリングを専門科目では必須条件として実行",
                    "ログで正確な問題選択状況を追跡可能"
                ]
            },
            
            "5. 類似問題の発生可能性": {
                "高リスク箇所": [
                    "年度指定時の問題フィルタリング（4-2_2019.csvの年度別選択）",
                    "復習問題選択時の部門別フィルタリング",
                    "カテゴリ別統計表示での集計処理",
                    "SRS（間隔反復学習）システムでの部門別復習問題選択"
                ],
                "予防策": [
                    "フィルタリング処理の統一化",
                    "型安全なマッピング処理の実装",
                    "テストケースの充実化",
                    "ログ出力による動作検証の強化"
                ]
            }
        },
        
        "データ構造分析": {
            "CSV構造": {
                "4-1.csv（基礎科目）": {
                    "問題数": "約200問",
                    "category": "全て'共通'",
                    "question_type": "basic（自動設定）",
                    "year": "None（年度不問）"
                },
                "4-2_2019.csv（専門科目）": {
                    "問題数": "357問",
                    "category分布": {
                        "道路": "29問",
                        "トンネル": "29問", 
                        "河川、砂防及び海岸・海洋": "29問",
                        "鋼構造及びコンクリート": "31問",
                        "土質及び基礎": "30問",
                        "その他": "各30問前後"
                    },
                    "question_type": "specialist（自動設定）",
                    "year": "2019"
                }
            },
            
            "マッピング定数": {
                "DEPARTMENT_TO_CATEGORY_MAPPING": {
                    "'road'": "'道路'",
                    "'tunnel'": "'トンネル'", 
                    "'civil_planning'": "'河川、砂防及び海岸・海洋'",
                    "'steel_concrete'": "'鋼構造及びコンクリート'",
                    "'soil_foundation'": "'土質及び基礎'",
                    "その他": "12分野分の完全マッピング"
                },
                "使用箇所": "utils.py（行482-541）, app.py（行101-117）で定義・使用"
            }
        },
        
        "エラー再現手順": {
            "手順1": "アプリケーション起動",
            "手順2": "部門選択画面で「道路」を選択", 
            "手順3": "専門科目（4-2）を選択",
            "手順4": "問題開始後、出題される問題を確認",
            "期待結果": "道路分野の問題のみ出題される",
            "実際の結果": "道路以外の問題（土質、鋼構造等）も混在して出題される",
            "再現率": "ほぼ100%（条件が揃えば必ず発生）"
        },
        
        "修正案": {
            "緊急修正": [
                "get_mixed_questions関数内の専門科目フィルタリング条件を必須化",
                "部門マッチング失敗時のフォールバック処理を削除または制限",
                "カテゴリマッチングの完全一致判定を厳格化"
            ],
            "根本対策": [
                "部門IDとカテゴリ名の型安全なマッピングシステム構築",
                "問題選択フローの単純化・統一化", 
                "包括的なテストスイートの実装",
                "エラーハンドリングの改善"
            ]
        }
    }
    
    return analysis

if __name__ == "__main__":
    analysis_result = analyze_root_cause()
    
    print("=" * 80)
    print("RCCM試験問題集アプリ専門分野混在問題 - 根本原因分析レポート")
    print("=" * 80)
    
    for section, content in analysis_result.items():
        print(f"\n【{section}】")
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"\n  ◆ {key}")
                if isinstance(value, list):
                    for item in value:
                        print(f"    - {item}")
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        print(f"    • {sub_key}: {sub_value}")
                else:
                    print(f"    {value}")
        else:
            print(f"  {content}")
    
    print("\n" + "=" * 80)
    print("分析完了: 専門分野混在問題の根本原因を特定しました")
    print("対策: get_mixed_questions関数の専門科目フィルタリング条件の修正が必要")
    print("=" * 80)