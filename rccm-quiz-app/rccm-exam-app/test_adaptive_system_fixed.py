"""
RCCM部門別適応学習システムの実使用シナリオテスト（修正版）
"""

import os
import sys
import time
import json
import psutil
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import random

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adaptive_learning import AdaptiveLearningEngine
from ai_analyzer import AILearningAnalyzer
from data_manager import DataManager
from utils import load_questions_improved, load_rccm_data_files
from config import RCCMConfig

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdaptiveSystemTesterFixed:
    """部門別適応学習システムのテスター（修正版）"""
    
    def __init__(self):
        self.adaptive_engine = AdaptiveLearningEngine()
        self.ai_analyzer = AILearningAnalyzer()
        self.data_manager = DataManager()
        self.test_results = {
            'data_integrity_test': {},
            'performance_test': {},
            'edge_case_test': {},
            'functional_test': {},
            'errors': []
        }
        
    def run_all_tests(self):
        """全テストを実行"""
        logger.info("="*80)
        logger.info("RCCM部門別適応学習システム 実使用シナリオテスト開始（修正版）")
        logger.info("="*80)
        
        # 1. データ整合性テスト
        self.test_data_integrity()
        
        # 2. 機能テスト
        self.test_functional()
        
        # 3. パフォーマンステスト
        self.test_performance()
        
        # 4. エッジケーステスト
        self.test_edge_cases()
        
        # 結果レポート生成
        self.generate_report()
        
    def test_data_integrity(self):
        """データ整合性テスト"""
        logger.info("\n1. データ整合性テスト開始")
        test_results = {}
        
        try:
            # 問題データ読み込み
            data_dir = '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data'
            questions = load_rccm_data_files(data_dir)
            
            test_results['total_questions'] = len(questions)
            logger.info(f"総問題数: {test_results['total_questions']}")
            
            # 部門別カウント
            department_counts = {}
            missing_department = 0
            
            for q in questions:
                if 'department' in q and q['department']:
                    dept = q['department']
                    department_counts[dept] = department_counts.get(dept, 0) + 1
                else:
                    missing_department += 1
                    
            test_results['department_distribution'] = department_counts
            test_results['missing_department'] = missing_department
            
            logger.info(f"部門別問題数: {department_counts}")
            logger.info(f"部門情報欠落: {missing_department}問")
            
            # 各部門でのフィルタリングテスト（手動実装）
            for dept in RCCMConfig.DEPARTMENTS.keys():
                filtered = [q for q in questions if q.get('department') == dept]
                test_results[f'filtered_{dept}'] = len(filtered)
                logger.info(f"{dept}部門フィルタ後: {len(filtered)}問")
                
            # カテゴリ分布確認
            category_counts = {}
            for q in questions:
                cat = q.get('category', 'unknown')
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
            test_results['category_distribution'] = category_counts
            logger.info(f"カテゴリ数: {len(category_counts)}")
            
            # 問題種別分布確認
            question_type_counts = {}
            for q in questions:
                qtype = q.get('question_type', 'unknown')
                question_type_counts[qtype] = question_type_counts.get(qtype, 0) + 1
                
            test_results['question_type_distribution'] = question_type_counts
            logger.info(f"問題種別分布: {question_type_counts}")
            
        except Exception as e:
            logger.error(f"データ整合性テストエラー: {e}")
            self.test_results['errors'].append(f"データ整合性テスト: {str(e)}")
            test_results['error'] = str(e)
            
        self.test_results['data_integrity_test'] = test_results
        
    def test_functional(self):
        """機能テスト"""
        logger.info("\n2. 機能テスト開始")
        test_results = {}
        
        try:
            questions = load_rccm_data_files('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data')[:100]  # 100問で高速テスト
            
            # モックユーザーデータとAI分析データ作成
            mock_user_session = {
                'statistics': {
                    'category_accuracy': {
                        'コンクリート': 0.6,
                        '土質': 0.4,
                        '河川': 0.8
                    },
                    'total_questions': 100,
                    'correct_answers': 60
                },
                'srs_data': {},
                'answered_questions': []
            }
            
            mock_ai_analysis = {
                'weak_areas': {
                    '土質': {'priority': 0.8, 'weakness_score': 0.7},
                    'コンクリート': {'priority': 0.6, 'weakness_score': 0.5}
                },
                'recommendations': {
                    'department': 'road',
                    'focus_areas': ['基礎理論'],
                    'learning_priorities': ['構造力学', '土質工学']
                }
            }
            
            # 各学習モードでの問題選択テスト
            learning_modes = ['balanced', 'foundation', 'specialist_focused']
            departments = ['road', 'civil_planning', 'agriculture']
            
            for mode in learning_modes:
                for dept in departments:
                    try:
                        selected = self.adaptive_engine.get_adaptive_questions(
                            user_session=mock_user_session,
                            all_questions=questions,
                            ai_analysis=mock_ai_analysis,
                            session_size=10,
                            learning_mode=mode,
                            department=dept
                        )
                        
                        test_results[f'{mode}_{dept}'] = {
                            'success': True,
                            'selected_count': len(selected),
                            'selected_departments': [q.get('department') for q in selected]
                        }
                        logger.info(f"{mode}モード {dept}部門: {len(selected)}問選択")
                        
                    except Exception as e:
                        test_results[f'{mode}_{dept}'] = {
                            'success': False,
                            'error': str(e)
                        }
                        logger.error(f"{mode}モード {dept}部門エラー: {e}")
                        
            # AI分析テスト
            try:
                analysis = self.ai_analyzer.analyze_weak_areas(
                    mock_user_session,
                    'road'
                )
                test_results['ai_analysis'] = {
                    'success': True,
                    'result_keys': list(analysis.keys()) if isinstance(analysis, dict) else 'non_dict'
                }
                logger.info("AI分析テスト: 成功")
            except Exception as e:
                test_results['ai_analysis'] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"AI分析テストエラー: {e}")
                
        except Exception as e:
            logger.error(f"機能テストエラー: {e}")
            self.test_results['errors'].append(f"機能テスト: {str(e)}")
            test_results['error'] = str(e)
            
        self.test_results['functional_test'] = test_results
        
    def test_performance(self):
        """パフォーマンステスト"""
        logger.info("\n3. パフォーマンステスト開始")
        test_results = {}
        
        try:
            # メモリ使用量（開始時）
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 大量データでの問題選択テスト
            questions = load_rccm_data_files('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data')
            
            # モックユーザーデータ作成
            mock_user_session = {
                'statistics': {
                    'category_accuracy': {cat: random.uniform(0.3, 0.9) for cat in ['土質', 'コンクリート', '河川']},
                    'total_questions': 1000,
                    'correct_answers': 750,
                },
                'srs_data': {
                    str(i): {
                        'review_count': random.randint(0, 5),
                        'last_review': '2025-01-01',
                        'difficulty_rating': random.uniform(1, 5)
                    } for i in range(100)
                },
                'answered_questions': []
            }
            
            mock_ai_analysis = {
                'weak_areas': {
                    '土質': {'priority': 0.8, 'weakness_score': 0.7},
                    'コンクリート': {'priority': 0.6, 'weakness_score': 0.5}
                },
                'recommendations': {
                    'department': 'road',
                    'focus_areas': ['基礎理論']
                }
            }
            
            # 各学習モードでの処理時間測定
            for mode in ['balanced', 'foundation', 'specialist_focused']:
                start_time = time.time()
                
                # 適応的問題選択（10回実行）
                for _ in range(10):
                    selected = self.adaptive_engine.get_adaptive_questions(
                        user_session=mock_user_session,
                        all_questions=questions[:1000],  # 1000問でテスト
                        ai_analysis=mock_ai_analysis,
                        session_size=20,
                        learning_mode=mode,
                        department='road'
                    )
                    
                elapsed = time.time() - start_time
                test_results[f'mode_{mode}_time'] = elapsed
                logger.info(f"{mode}モード処理時間（10回）: {elapsed:.3f}秒")
                
            # データ読み込み時間測定
            start_time = time.time()
            for _ in range(5):
                questions = load_rccm_data_files('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data')
            elapsed = time.time() - start_time
            test_results['data_load_time'] = elapsed
            logger.info(f"データ読み込み時間（5回）: {elapsed:.3f}秒")
            
            # メモリ使用量（終了時）
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            test_results['memory_usage'] = {
                'start': start_memory,
                'end': end_memory,
                'increase': end_memory - start_memory
            }
            logger.info(f"メモリ使用量: 開始時 {start_memory:.1f}MB → 終了時 {end_memory:.1f}MB")
            
        except Exception as e:
            logger.error(f"パフォーマンステストエラー: {e}")
            self.test_results['errors'].append(f"パフォーマンステスト: {str(e)}")
            test_results['error'] = str(e)
            
        self.test_results['performance_test'] = test_results
        
    def test_edge_cases(self):
        """エッジケーステスト"""
        logger.info("\n4. エッジケーステスト開始")
        test_results = {}
        
        try:
            questions = load_rccm_data_files('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data')[:100]
            
            # テスト1: 履歴データが少ない場合
            logger.info("テスト1: 履歴データが少ない場合")
            minimal_user_session = {
                'statistics': {
                    'category_accuracy': {},
                    'total_questions': 5,
                    'correct_answers': 3,
                },
                'srs_data': {},
                'answered_questions': []
            }
            
            minimal_ai_analysis = {
                'weak_areas': {},
                'recommendations': {
                    'department': 'road',
                    'focus_areas': []
                }
            }
            
            selected = self.adaptive_engine.get_adaptive_questions(
                user_session=minimal_user_session,
                all_questions=questions,
                ai_analysis=minimal_ai_analysis,
                session_size=10,
                learning_mode='foundation',
                department='road'
            )
            test_results['minimal_history'] = {
                'selected_count': len(selected),
                'success': len(selected) > 0
            }
            logger.info(f"選択された問題数: {len(selected)}")
            
            # テスト2: 特定部門のデータが全くない場合
            logger.info("\nテスト2: 部門データ不十分の場合")
            # フィルタしても問題が少ない部門
            road_questions = [q for q in questions if q.get('department') == 'comprehensive'][:2]  # 2問のみ
            
            selected = self.adaptive_engine.get_adaptive_questions(
                user_session=minimal_user_session,
                all_questions=road_questions,
                ai_analysis=minimal_ai_analysis,
                session_size=10,
                learning_mode='balanced',
                department='comprehensive'
            )
            test_results['insufficient_dept_data'] = {
                'selected_count': len(selected),
                'success': True  # エラーが出ないことを確認
            }
            logger.info(f"不十分な部門データでの選択: {len(selected)}問")
            
            # テスト3: 同じ部門で複数の学習モードを切り替えた場合
            logger.info("\nテスト3: モード切り替えテスト")
            mode_results = {}
            
            for mode in ['foundation', 'balanced', 'specialist_focused']:
                selected = self.adaptive_engine.get_adaptive_questions(
                    user_session=minimal_user_session,
                    all_questions=questions,
                    ai_analysis=minimal_ai_analysis,
                    session_size=10,
                    learning_mode=mode,
                    department='road'
                )
                
                # 選択された問題の特性を分析
                departments = [q.get('department') for q in selected]
                mode_results[mode] = {
                    'count': len(selected),
                    'departments': departments
                }
                logger.info(f"{mode}モード: {len(selected)}問選択")
                
            test_results['mode_switching'] = mode_results
            
            # テスト4: 大量リクエスト処理
            logger.info("\nテスト4: 大量リクエスト処理")
            start_time = time.time()
            
            for i in range(20):  # 20回に削減
                dept = random.choice(['road', 'civil_planning', 'agriculture'])
                selected = self.adaptive_engine.get_adaptive_questions(
                    user_session=minimal_user_session,
                    all_questions=questions,
                    ai_analysis=minimal_ai_analysis,
                    session_size=5,
                    learning_mode='balanced',
                    department=dept
                )
                
            elapsed = time.time() - start_time
            test_results['bulk_requests'] = {
                'requests': 20,
                'total_time': elapsed,
                'avg_time': elapsed / 20
            }
            logger.info(f"20リクエスト処理時間: {elapsed:.3f}秒 (平均: {elapsed/20:.3f}秒)")
            
            # テスト5: AIAnalyzer のエッジケーステスト
            logger.info("\nテスト5: AI分析のエッジケース")
            try:
                # 空のユーザーセッションを作成
                empty_user_session = {'history': []}
                analysis = self.ai_analyzer.analyze_weak_areas(empty_user_session, 'road')
                test_results['ai_empty_data'] = {
                    'success': True,
                    'has_result': analysis is not None
                }
                logger.info("AI分析（空データ）: 成功")
            except Exception as e:
                test_results['ai_empty_data'] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"AI分析（空データ）エラー: {e}")
                
        except Exception as e:
            logger.error(f"エッジケーステストエラー: {e}")
            self.test_results['errors'].append(f"エッジケーステスト: {str(e)}")
            test_results['error'] = str(e)
            
        self.test_results['edge_case_test'] = test_results
        
    def generate_report(self):
        """テスト結果レポート生成"""
        logger.info("\n" + "="*80)
        logger.info("テスト結果サマリー")
        logger.info("="*80)
        
        # 1. データ整合性テスト結果
        logger.info("\n【データ整合性テスト】")
        data_test = self.test_results['data_integrity_test']
        if 'error' not in data_test:
            logger.info(f"総問題数: {data_test.get('total_questions', 0)}")
            logger.info(f"部門情報欠落: {data_test.get('missing_department', 0)}問")
            if 'department_distribution' in data_test:
                logger.info("部門別分布:")
                for dept, count in data_test['department_distribution'].items():
                    logger.info(f"  {dept}: {count}問")
            if 'question_type_distribution' in data_test:
                logger.info(f"問題種別分布: {data_test['question_type_distribution']}")
        else:
            logger.error(f"データ整合性テスト失敗: {data_test['error']}")
            
        # 2. 機能テスト結果
        logger.info("\n【機能テスト】")
        func_test = self.test_results['functional_test']
        if 'error' not in func_test:
            success_count = sum(1 for k, v in func_test.items() 
                              if isinstance(v, dict) and v.get('success', False))
            total_count = sum(1 for k, v in func_test.items() 
                            if isinstance(v, dict) and 'success' in v)
            logger.info(f"機能テスト成功率: {success_count}/{total_count}")
            
            # 失敗したテストを表示
            for key, value in func_test.items():
                if isinstance(value, dict) and not value.get('success', True):
                    logger.error(f"  失敗: {key} - {value.get('error', 'unknown')}")
        else:
            logger.error(f"機能テスト失敗: {func_test['error']}")
            
        # 3. パフォーマンステスト結果
        logger.info("\n【パフォーマンステスト】")
        perf_test = self.test_results['performance_test']
        if 'error' not in perf_test:
            for key, value in perf_test.items():
                if key.endswith('_time'):
                    logger.info(f"{key}: {value:.3f}秒")
            if 'memory_usage' in perf_test:
                mem = perf_test['memory_usage']
                logger.info(f"メモリ使用量: {mem['increase']:.1f}MB増加")
        else:
            logger.error(f"パフォーマンステスト失敗: {perf_test['error']}")
            
        # 4. エッジケーステスト結果
        logger.info("\n【エッジケーステスト】")
        edge_test = self.test_results['edge_case_test']
        if 'error' not in edge_test:
            logger.info(f"履歴データ少: {'✓' if edge_test.get('minimal_history', {}).get('success') else '✗'}")
            logger.info(f"部門データ不十分: {'✓' if edge_test.get('insufficient_dept_data', {}).get('success') else '✗'}")
            logger.info(f"AI分析（空データ）: {'✓' if edge_test.get('ai_empty_data', {}).get('success') else '✗'}")
            if 'bulk_requests' in edge_test:
                bulk = edge_test['bulk_requests']
                logger.info(f"大量リクエスト: {bulk['requests']}件を{bulk['total_time']:.1f}秒で処理")
        else:
            logger.error(f"エッジケーステスト失敗: {edge_test['error']}")
            
        # エラーサマリー
        if self.test_results['errors']:
            logger.error("\n【エラー一覧】")
            for error in self.test_results['errors']:
                logger.error(f"- {error}")
        else:
            logger.info("\n【全体評価】: テスト実行成功")
                
        # 改善提案
        logger.info("\n【改善提案】")
        self.generate_recommendations()
        
        # レポートファイル保存
        report_path = f'/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/test_report_fixed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n詳細レポート保存: {report_path}")
        
    def generate_recommendations(self):
        """テスト結果に基づく改善提案"""
        recommendations = []
        
        # データ整合性の問題
        data_test = self.test_results.get('data_integrity_test', {})
        if data_test.get('missing_department', 0) > 100:
            recommendations.append("多数の問題で部門情報が欠落しています。データ移行スクリプトの改善が必要です。")
            
        # 機能テストの問題
        func_test = self.test_results.get('functional_test', {})
        if 'error' in func_test:
            recommendations.append("機能テストで重大なエラーが発生しています。基本機能の見直しが必要です。")
        
        # パフォーマンスの問題
        perf_test = self.test_results.get('performance_test', {})
        for key, value in perf_test.items():
            if key.endswith('_time') and isinstance(value, (int, float)) and value > 3.0:
                recommendations.append(f"{key}の処理時間が長すぎます。アルゴリズムの最適化を検討してください。")
                
        # メモリ使用量の問題
        if 'memory_usage' in perf_test:
            mem_increase = perf_test['memory_usage'].get('increase', 0)
            if mem_increase > 50:
                recommendations.append(f"メモリ使用量が{mem_increase:.1f}MB増加しています。メモリリークの可能性を調査してください。")
                
        # エラーハンドリングの改善
        if self.test_results['errors']:
            recommendations.append("複数のエラーが発生しています。エラーハンドリングの強化が必要です。")
            
        # 部門別データの偏り
        if 'department_distribution' in data_test:
            dept_dist = data_test['department_distribution']
            if dept_dist:
                max_count = max(dept_dist.values())
                min_count = min(dept_dist.values())
                if max_count > min_count * 5:
                    recommendations.append("部門別の問題数に大きな偏りがあります。バランスの改善を検討してください。")
        
        # CSV形式エラーの問題
        if any('CSV解析エラー' in str(error) for error in self.test_results['errors']):
            recommendations.append("CSVファイルの形式エラーが多数発生しています。データクレンジングが必要です。")
                    
        if recommendations:
            for rec in recommendations:
                logger.info(f"- {rec}")
        else:
            logger.info("- 特に重大な問題は検出されませんでした。")

if __name__ == "__main__":
    tester = AdaptiveSystemTesterFixed()
    tester.run_all_tests()