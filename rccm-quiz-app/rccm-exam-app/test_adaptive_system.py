"""
RCCM部門別適応学習システムの実使用シナリオテスト
"""

import os
import sys
import time
import json
import psutil
import requests
import subprocess
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

class AdaptiveSystemTester:
    """部門別適応学習システムのテスター"""
    
    def __init__(self):
        self.adaptive_engine = AdaptiveLearningEngine()
        self.ai_analyzer = AILearningAnalyzer()
        self.data_manager = DataManager()
        self.test_results = {
            'startup_test': {},
            'data_integrity_test': {},
            'performance_test': {},
            'edge_case_test': {},
            'errors': []
        }
        
    def run_all_tests(self):
        """全テストを実行"""
        logger.info("="*80)
        logger.info("RCCM部門別適応学習システム 実使用シナリオテスト開始")
        logger.info("="*80)
        
        # 1. 実際のアプリ起動テスト
        self.test_app_startup()
        
        # 2. データ整合性テスト
        self.test_data_integrity()
        
        # 3. パフォーマンステスト
        self.test_performance()
        
        # 4. エッジケーステスト
        self.test_edge_cases()
        
        # 結果レポート生成
        self.generate_report()
        
    def test_app_startup(self):
        """アプリ起動と基本フローのテスト"""
        logger.info("\n1. アプリ起動テスト開始")
        test_results = {}
        
        try:
            # Flask appを起動（サブプロセス）
            logger.info("Flaskアプリケーションを起動...")
            app_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 起動待機
            time.sleep(3)
            
            # アプリが起動したか確認
            try:
                response = requests.get('http://localhost:5001/')
                test_results['app_startup'] = response.status_code == 200
                logger.info(f"アプリ起動: {'成功' if test_results['app_startup'] else '失敗'}")
            except:
                test_results['app_startup'] = False
                logger.error("アプリ起動失敗")
                
            # 部門選択→AI適応学習のフローをテスト
            if test_results['app_startup']:
                # セッションを作成
                session = requests.Session()
                
                # 1. トップページアクセス
                response = session.get('http://localhost:5001/')
                test_results['home_page'] = response.status_code == 200
                
                # 2. カテゴリページアクセス
                response = session.get('http://localhost:5001/categories')
                test_results['categories_page'] = response.status_code == 200
                
                # 3. AI分析ページアクセス（部門指定付き）
                response = session.get('http://localhost:5001/ai_analysis?department=road')
                test_results['ai_analysis_page'] = response.status_code == 200
                
                # 4. 学習プランページアクセス
                response = session.get('http://localhost:5001/learning_plan?mode=department_mastery&department=road')
                test_results['learning_plan_page'] = response.status_code == 200
                
                logger.info(f"ページアクセステスト結果: {test_results}")
                
        except Exception as e:
            logger.error(f"起動テストエラー: {e}")
            self.test_results['errors'].append(f"起動テスト: {str(e)}")
            test_results['error'] = str(e)
            
        finally:
            # アプリを停止
            try:
                app_process.terminate()
                app_process.wait(timeout=5)
            except:
                pass
                
        self.test_results['startup_test'] = test_results
        
    def test_data_integrity(self):
        """データ整合性テスト"""
        logger.info("\n2. データ整合性テスト開始")
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
            
            # 各部門でのフィルタリングテスト
            for dept in RCCMConfig.DEPARTMENTS.keys():
                filtered = self.adaptive_engine.filter_questions_by_department(questions, dept)
                test_results[f'filtered_{dept}'] = len(filtered)
                logger.info(f"{dept}部門フィルタ後: {len(filtered)}問")
                
            # カテゴリ分布確認
            category_counts = {}
            for q in questions:
                cat = q.get('category', 'unknown')
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
            test_results['category_distribution'] = category_counts
            logger.info(f"カテゴリ分布: {list(category_counts.keys())[:10]}...")
            
        except Exception as e:
            logger.error(f"データ整合性テストエラー: {e}")
            self.test_results['errors'].append(f"データ整合性テスト: {str(e)}")
            test_results['error'] = str(e)
            
        self.test_results['data_integrity_test'] = test_results
        
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
            mock_user_data = {
                'history': [
                    {
                        'id': i,
                        'category': random.choice(['土質', 'コンクリート', '河川']),
                        'is_correct': random.choice([True, False]),
                        'department': random.choice(list(RCCMConfig.DEPARTMENTS.keys()))
                    } for i in range(100)
                ],
                'statistics': {
                    'category_accuracy': {cat: random.uniform(0.3, 0.9) for cat in ['土質', 'コンクリート', '河川']},
                    'total_questions': 1000,
                    'correct_answers': 750,
                    'department_stats': {
                        dept: {
                            'total': random.randint(50, 200),
                            'correct': random.randint(30, 150)
                        } for dept in RCCMConfig.DEPARTMENTS.keys()
                    }
                },
                'srs_data': {
                    str(i): {
                        'review_count': random.randint(0, 5),
                        'last_review': '2025-01-01',
                        'next_review': '2025-01-15',
                        'difficulty_rating': random.uniform(1, 5)
                    } for i in range(100)
                },
                'weak_areas': {
                    '土質': {'priority': 0.8, 'weakness_score': 0.7},
                    'コンクリート': {'priority': 0.6, 'weakness_score': 0.5}
                }
            }
            
            # 各学習モードでの処理時間測定
            for mode in self.adaptive_engine.learning_modes.keys():
                start_time = time.time()
                
                # 適応的問題選択（10回実行）
                for _ in range(10):
                    selected = self.adaptive_engine.get_adaptive_questions(
                        user_session=mock_user_data,
                        all_questions=questions[:1000],  # 1000問でテスト
                        ai_analysis={},
                        session_size=20,
                        learning_mode=mode,
                        department='road'
                    )
                    
                elapsed = time.time() - start_time
                test_results[f'mode_{mode}_time'] = elapsed
                logger.info(f"{mode}モード処理時間（10回）: {elapsed:.3f}秒")
                
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
            questions = load_rccm_data_files('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data')
            
            # テスト1: 履歴データが少ない場合
            logger.info("テスト1: 履歴データが少ない場合")
            minimal_user_data = {
                'history': [],
                'statistics': {
                    'category_accuracy': {},
                    'total_questions': 5,
                    'correct_answers': 3,
                    'department_stats': {}
                },
                'srs_data': {},
                'weak_areas': []
            }
            
            selected = self.adaptive_engine.get_adaptive_questions(
                user_session=minimal_user_data,
                all_questions=questions[:100],
                ai_analysis={},
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
            logger.info("\nテスト2: 特定部門のデータが全くない場合")
            # 存在しない部門でテスト
            selected = self.adaptive_engine.get_adaptive_questions(
                user_session=minimal_user_data,
                all_questions=questions,
                ai_analysis={},
                session_size=10,
                learning_mode='balanced',
                department='non_existent_dept'
            )
            test_results['non_existent_dept'] = {
                'selected_count': len(selected),
                'success': True  # エラーが出ないことを確認
            }
            logger.info(f"存在しない部門での選択: {len(selected)}問")
            
            # テスト3: 同じ部門で複数の学習モードを切り替えた場合
            logger.info("\nテスト3: モード切り替えテスト")
            mode_results = {}
            
            for mode in ['foundation', 'balanced', 'specialist_focused']:
                selected = self.adaptive_engine.get_adaptive_questions(
                    user_session=minimal_user_data,
                    all_questions=questions[:500],
                    ai_analysis={},
                    session_size=10,
                    learning_mode=mode,
                    department='civil_planning'
                )
                
                # 選択された問題の特性を分析
                difficulties = [q.get('difficulty', 'unknown') for q in selected]
                mode_results[mode] = {
                    'count': len(selected),
                    'difficulties': difficulties
                }
                logger.info(f"{mode}モード: {len(selected)}問選択")
                
            test_results['mode_switching'] = mode_results
            
            # テスト4: 大量リクエスト処理
            logger.info("\nテスト4: 大量リクエスト処理")
            start_time = time.time()
            
            for i in range(50):
                selected = self.adaptive_engine.get_adaptive_questions(
                    user_session=minimal_user_data,
                    all_questions=questions[:200],
                    ai_analysis={},
                    session_size=10,
                    learning_mode='balanced',
                    department=random.choice(list(RCCMConfig.DEPARTMENTS.keys()))
                )
                
            elapsed = time.time() - start_time
            test_results['bulk_requests'] = {
                'requests': 50,
                'total_time': elapsed,
                'avg_time': elapsed / 50
            }
            logger.info(f"50リクエスト処理時間: {elapsed:.3f}秒 (平均: {elapsed/50:.3f}秒)")
            
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
        
        # 1. 起動テスト結果
        logger.info("\n【起動テスト】")
        startup = self.test_results['startup_test']
        if 'error' not in startup:
            logger.info(f"アプリ起動: {'✓' if startup.get('app_startup') else '✗'}")
            logger.info(f"ページアクセス: Home={'✓' if startup.get('home_page') else '✗'}, "
                       f"Categories={'✓' if startup.get('categories_page') else '✗'}, "
                       f"AI分析={'✓' if startup.get('ai_analysis_page') else '✗'}, "
                       f"学習プラン={'✓' if startup.get('learning_plan_page') else '✗'}")
        else:
            logger.error(f"起動テスト失敗: {startup['error']}")
            
        # 2. データ整合性テスト結果
        logger.info("\n【データ整合性テスト】")
        data_test = self.test_results['data_integrity_test']
        if 'error' not in data_test:
            logger.info(f"総問題数: {data_test.get('total_questions', 0)}")
            logger.info(f"部門情報欠落: {data_test.get('missing_department', 0)}問")
            if 'department_distribution' in data_test:
                logger.info("部門別分布:")
                for dept, count in data_test['department_distribution'].items():
                    logger.info(f"  {dept}: {count}問")
        else:
            logger.error(f"データ整合性テスト失敗: {data_test['error']}")
            
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
            logger.info(f"存在しない部門: {'✓' if edge_test.get('non_existent_dept', {}).get('success') else '✗'}")
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
                
        # 改善提案
        logger.info("\n【改善提案】")
        self.generate_recommendations()
        
        # レポートファイル保存
        report_path = f'/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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
            
        # パフォーマンスの問題
        perf_test = self.test_results.get('performance_test', {})
        for key, value in perf_test.items():
            if key.endswith('_time') and isinstance(value, (int, float)) and value > 5.0:
                recommendations.append(f"{key}の処理時間が長すぎます。アルゴリズムの最適化を検討してください。")
                
        # メモリ使用量の問題
        if 'memory_usage' in perf_test:
            mem_increase = perf_test['memory_usage'].get('increase', 0)
            if mem_increase > 100:
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
                    
        if recommendations:
            for rec in recommendations:
                logger.info(f"- {rec}")
        else:
            logger.info("- 特に重大な問題は検出されませんでした。")

if __name__ == "__main__":
    tester = AdaptiveSystemTester()
    tester.run_all_tests()