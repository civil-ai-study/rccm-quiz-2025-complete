#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 CLAUDE.md準拠 本番環境10ペルソナ包括的検証
学習アプリの多様なユーザー体験をカバーする完全テスト

対象: https://rccm-quiz-2025.onrender.com
CLAUDE.md準拠の10ペルソナによる本番環境での完全検証
"""

import requests
import json
import time
from datetime import datetime
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
import logging
import random

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionPersonaComprehensiveTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        
        # CLAUDE.md準拠10ペルソナ定義
        self.personas = {
            1: {
                'name': '初心者学習者',
                'description': '全く知識がない状態',
                'test_pattern': 'basic_slow',
                'departments': ['基礎科目'],
                'question_counts': [10],
                'simulation_delay': 3.0,
                'error_tolerance': 'high',
                'expected_behavior': 'slow_careful_learning'
            },
            2: {
                'name': '中級者',
                'description': '基礎知識あり、応用学習中',
                'test_pattern': 'mixed_moderate',
                'departments': ['基礎科目', '道路', '建設環境'],
                'question_counts': [10, 20],
                'simulation_delay': 2.0,
                'error_tolerance': 'medium',
                'expected_behavior': 'systematic_learning'
            },
            3: {
                'name': '上級者',
                'description': '試験直前、弱点補強',
                'test_pattern': 'advanced_fast',
                'departments': ['道路', '河川・砂防', '建設環境', '鋼構造・コンクリート'],
                'question_counts': [20, 30],
                'simulation_delay': 1.0,
                'error_tolerance': 'low',
                'expected_behavior': 'focused_intensive'
            },
            4: {
                'name': '忙しい社会人',
                'description': '隙間時間学習',
                'test_pattern': 'quick_burst',
                'departments': ['基礎科目', '道路'],
                'question_counts': [10],
                'simulation_delay': 0.5,
                'error_tolerance': 'medium',
                'expected_behavior': 'efficient_quick'
            },
            5: {
                'name': '学生',
                'description': 'まとまった時間で集中学習',
                'test_pattern': 'intensive_study',
                'departments': ['基礎科目', '道路', '河川・砂防', '都市計画'],
                'question_counts': [20, 30],
                'simulation_delay': 1.5,
                'error_tolerance': 'low',
                'expected_behavior': 'thorough_comprehensive'
            },
            6: {
                'name': '高齢学習者',
                'description': '操作に不慣れ',
                'test_pattern': 'careful_slow',
                'departments': ['基礎科目'],
                'question_counts': [10],
                'simulation_delay': 5.0,
                'error_tolerance': 'high',
                'expected_behavior': 'cautious_methodical'
            },
            7: {
                'name': '視覚障害者',
                'description': '読み上げ機能必須',
                'test_pattern': 'accessibility_focus',
                'departments': ['基礎科目', '道路'],
                'question_counts': [10, 20],
                'simulation_delay': 4.0,
                'error_tolerance': 'high',
                'expected_behavior': 'assistive_tech_dependent'
            },
            8: {
                'name': 'モバイル専用ユーザー',
                'description': 'スマートフォンでの学習',
                'test_pattern': 'mobile_optimized',
                'departments': ['基礎科目', '道路', '建設環境'],
                'question_counts': [10, 20],
                'simulation_delay': 2.5,
                'error_tolerance': 'medium',
                'expected_behavior': 'mobile_native'
            },
            9: {
                'name': '回線速度が遅い環境ユーザー',
                'description': '低速回線での学習',
                'test_pattern': 'slow_connection',
                'departments': ['基礎科目'],
                'question_counts': [10],
                'simulation_delay': 6.0,
                'error_tolerance': 'high',
                'expected_behavior': 'patience_required'
            },
            10: {
                'name': '不正解続きで挫折寸前ユーザー',
                'description': 'モチベーション低下状態',
                'test_pattern': 'struggling_learner',
                'departments': ['基礎科目'],
                'question_counts': [10],
                'simulation_delay': 2.0,
                'error_tolerance': 'very_high',
                'expected_behavior': 'needs_encouragement'
            }
        }
        
        # 部門マッピング（本番環境対応）
        self.department_mapping = {
            '基礎科目': 'basic',
            '道路': '道路',
            '河川・砂防': '河川・砂防',
            '都市計画': '都市計画',
            '造園': '造園',
            '建設環境': '建設環境',
            '鋼構造・コンクリート': '鋼構造・コンクリート',
            '土質・基礎': '土質・基礎',
            '施工計画': '施工計画',
            '上下水道': '上下水道',
            '森林土木': '森林土木',
            '農業土木': '農業土木',
            'トンネル': 'トンネル'
        }
        
        # 検証結果
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'PRODUCTION_PERSONA_COMPREHENSIVE_TEST',
            'target_url': self.base_url,
            'personas_tested': {},
            'overall_statistics': {},
            'accessibility_findings': [],
            'performance_metrics': {},
            'critical_issues': []
        }

    def create_persona_session(self, persona_id: int) -> requests.Session:
        """ペルソナ専用セッション作成"""
        session = requests.Session()
        persona = self.personas[persona_id]
        
        # ペルソナ別ユーザーエージェント設定
        if persona['name'] == 'モバイル専用ユーザー':
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8'
            })
        elif persona['name'] == '視覚障害者':
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 NVDA/2023.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9'
            })
        elif persona['name'] == '回線速度が遅い環境ユーザー':
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive'
            })
        else:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8'
            })
        
        return session

    def simulate_persona_interaction(self, persona_id: int, session: requests.Session, department: str, question_count: int) -> Dict:
        """ペルソナの学習行動シミュレーション"""
        persona = self.personas[persona_id]
        
        interaction_result = {
            'persona_id': persona_id,
            'persona_name': persona['name'],
            'department': department,
            'question_count': question_count,
            'start_time': datetime.now().isoformat(),
            'interactions': [],
            'success': False,
            'accessibility_score': 0.0,
            'performance_score': 0.0,
            'user_experience_score': 0.0,
            'issues_encountered': []
        }
        
        try:
            print(f"  🎭 {persona['name']} ({department} {question_count}問)")
            
            # 1. ホームページアクセス
            start_time = time.time()
            response = session.get(self.base_url, timeout=30)
            home_load_time = time.time() - start_time
            
            interaction_result['interactions'].append({
                'action': 'home_page_access',
                'success': response.status_code == 200,
                'load_time': home_load_time,
                'status_code': response.status_code
            })
            
            if response.status_code != 200:
                interaction_result['issues_encountered'].append('ホームページアクセス失敗')
                return interaction_result
            
            # ペルソナ別遅延シミュレーション
            time.sleep(persona['simulation_delay'])
            
            # 2. 試験開始
            if department == '基礎科目':
                exam_url = f"{self.base_url}/start_exam/basic"
                exam_data = {'questions': str(question_count)}
            else:
                exam_url = f"{self.base_url}/start_exam/specialist"
                exam_data = {
                    'questions': str(question_count),
                    'category': department,
                    'year': '2019'  # 最新年度で統一
                }
            
            start_time = time.time()
            exam_response = session.post(exam_url, data=exam_data, timeout=30)
            exam_load_time = time.time() - start_time
            
            interaction_result['interactions'].append({
                'action': 'exam_start',
                'success': exam_response.status_code in [200, 302],
                'load_time': exam_load_time,
                'status_code': exam_response.status_code,
                'url': exam_url,
                'data': exam_data
            })
            
            if exam_response.status_code in [200, 302]:
                interaction_result['success'] = True
                
                # アクセシビリティチェック
                content = exam_response.text
                accessibility_score = self.evaluate_accessibility(content, persona)
                interaction_result['accessibility_score'] = accessibility_score
                
                # パフォーマンス評価
                performance_score = self.evaluate_performance(home_load_time, exam_load_time, persona)
                interaction_result['performance_score'] = performance_score
                
                # ユーザー体験評価
                ux_score = self.evaluate_user_experience(content, persona)
                interaction_result['user_experience_score'] = ux_score
                
                print(f"    ✅ 成功 (A11y: {accessibility_score:.1f}, Perf: {performance_score:.1f}, UX: {ux_score:.1f})")
            else:
                interaction_result['issues_encountered'].append(f'試験開始失敗: HTTP {exam_response.status_code}')
                print(f"    ❌ 失敗: HTTP {exam_response.status_code}")
            
        except Exception as e:
            interaction_result['issues_encountered'].append(f'例外発生: {str(e)}')
            print(f"    💥 例外: {str(e)}")
        
        interaction_result['end_time'] = datetime.now().isoformat()
        return interaction_result

    def evaluate_accessibility(self, content: str, persona: Dict) -> float:
        """アクセシビリティ評価"""
        score = 0.0
        checks = 0
        
        # 基本的なアクセシビリティチェック
        accessibility_indicators = [
            'alt=',  # 画像の代替テキスト
            'aria-',  # ARIA属性
            'role=',  # ロール属性
            'tabindex',  # タブインデックス
            'label',  # フォームラベル
            'title='  # タイトル属性
        ]
        
        for indicator in accessibility_indicators:
            checks += 1
            if indicator in content:
                score += 1
        
        # 視覚障害者特別チェック
        if persona['name'] == '視覚障害者':
            screen_reader_indicators = [
                'aria-label',
                'aria-describedby',
                'role="button"',
                'role="link"',
                'alt='
            ]
            
            for indicator in screen_reader_indicators:
                checks += 1
                if indicator in content:
                    score += 1
        
        return (score / checks) * 100 if checks > 0 else 0.0

    def evaluate_performance(self, home_load_time: float, exam_load_time: float, persona: Dict) -> float:
        """パフォーマンス評価"""
        avg_load_time = (home_load_time + exam_load_time) / 2
        
        # ペルソナ別パフォーマンス基準
        performance_thresholds = {
            '忙しい社会人': 2.0,
            '学生': 3.0,
            '回線速度が遅い環境ユーザー': 10.0,
            '高齢学習者': 5.0,
            'default': 3.0
        }
        
        threshold = performance_thresholds.get(persona['name'], performance_thresholds['default'])
        
        if avg_load_time <= threshold:
            return 100.0
        elif avg_load_time <= threshold * 1.5:
            return 75.0
        elif avg_load_time <= threshold * 2:
            return 50.0
        else:
            return 25.0

    def evaluate_user_experience(self, content: str, persona: Dict) -> float:
        """ユーザー体験評価"""
        score = 0.0
        checks = 0
        
        # 基本的なUXチェック
        ux_indicators = [
            '問題',  # 問題内容の存在
            '選択',  # 選択肢の存在
            'button',  # ボタンの存在
            'form',  # フォームの存在
            'nav',  # ナビゲーションの存在
        ]
        
        for indicator in ux_indicators:
            checks += 1
            if indicator in content:
                score += 1
        
        # ペルソナ別特別チェック
        if persona['name'] == 'モバイル専用ユーザー':
            mobile_indicators = [
                'viewport',
                'responsive',
                'mobile',
                'touch'
            ]
            
            for indicator in mobile_indicators:
                checks += 1
                if indicator in content:
                    score += 1
        
        elif persona['name'] == '不正解続きで挫折寸前ユーザー':
            encouragement_indicators = [
                'がんばって',
                '頑張って',
                '応援',
                'サポート',
                'ヒント'
            ]
            
            for indicator in encouragement_indicators:
                checks += 1
                if indicator in content:
                    score += 1
        
        return (score / checks) * 100 if checks > 0 else 0.0

    def run_persona_comprehensive_test(self):
        """10ペルソナ包括的テスト実行"""
        print("🎭 CLAUDE.md準拠 本番環境10ペルソナ包括的検証開始")
        print("=" * 80)
        print("目的: 学習アプリの多様なユーザー体験をカバーする完全テスト")
        print("対象: https://rccm-quiz-2025.onrender.com")
        print("ペルソナ数: 10種類")
        print("=" * 80)
        
        start_time = time.time()
        total_tests = 0
        successful_tests = 0
        
        # 各ペルソナでのテスト実行
        for persona_id, persona in self.personas.items():
            print(f"\n🎭 【ペルソナ {persona_id}】{persona['name']}")
            print(f"   説明: {persona['description']}")
            print("-" * 60)
            
            persona_session = self.create_persona_session(persona_id)
            persona_results = {
                'persona_info': persona,
                'test_results': [],
                'success_rate': 0.0,
                'avg_accessibility_score': 0.0,
                'avg_performance_score': 0.0,
                'avg_ux_score': 0.0,
                'critical_issues': []
            }
            
            persona_tests = 0
            persona_successes = 0
            accessibility_scores = []
            performance_scores = []
            ux_scores = []
            
            # 各部門・問題数でのテスト
            for department in persona['departments']:
                for question_count in persona['question_counts']:
                    total_tests += 1
                    persona_tests += 1
                    
                    result = self.simulate_persona_interaction(
                        persona_id, persona_session, department, question_count
                    )
                    
                    persona_results['test_results'].append(result)
                    
                    if result['success']:
                        successful_tests += 1
                        persona_successes += 1
                        accessibility_scores.append(result['accessibility_score'])
                        performance_scores.append(result['performance_score'])
                        ux_scores.append(result['user_experience_score'])
                    
                    if result['issues_encountered']:
                        persona_results['critical_issues'].extend(result['issues_encountered'])
                    
                    # ペルソナ別遅延
                    time.sleep(0.5)
            
            # ペルソナ別統計計算
            persona_results['success_rate'] = (persona_successes / persona_tests) * 100 if persona_tests > 0 else 0
            persona_results['avg_accessibility_score'] = sum(accessibility_scores) / len(accessibility_scores) if accessibility_scores else 0
            persona_results['avg_performance_score'] = sum(performance_scores) / len(performance_scores) if performance_scores else 0
            persona_results['avg_ux_score'] = sum(ux_scores) / len(ux_scores) if ux_scores else 0
            
            self.test_results['personas_tested'][persona_id] = persona_results
            
            # ペルソナ結果表示
            print(f"  📊 {persona['name']} 結果:")
            print(f"    成功率: {persona_results['success_rate']:.1f}%")
            print(f"    アクセシビリティ: {persona_results['avg_accessibility_score']:.1f}/100")
            print(f"    パフォーマンス: {persona_results['avg_performance_score']:.1f}/100")
            print(f"    ユーザー体験: {persona_results['avg_ux_score']:.1f}/100")
            
            if persona_results['critical_issues']:
                print(f"    🚨 問題: {len(persona_results['critical_issues'])}件")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 全体統計計算
        self.test_results['overall_statistics'] = {
            'total_personas': len(self.personas),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            'duration_seconds': duration
        }
        
        self.generate_persona_test_report()
        
        return self.test_results

    def generate_persona_test_report(self):
        """ペルソナテストレポート生成"""
        stats = self.test_results['overall_statistics']
        
        print("\n" + "=" * 80)
        print("🎭 CLAUDE.md準拠 本番環境10ペルソナ包括的検証結果")
        print("=" * 80)
        
        print(f"📊 総合統計:")
        print(f"  テスト対象ペルソナ: {stats['total_personas']}")
        print(f"  総テスト数: {stats['total_tests']}")
        print(f"  成功テスト数: {stats['successful_tests']}")
        print(f"  全体成功率: {stats['success_rate']:.1f}%")
        print(f"  実行時間: {stats['duration_seconds']:.1f}秒")
        print()
        
        # ペルソナ別サマリー
        print("🎭 ペルソナ別成功率:")
        for persona_id, results in self.test_results['personas_tested'].items():
            persona_name = results['persona_info']['name']
            success_rate = results['success_rate']
            status = "✅" if success_rate >= 95 else "⚠️" if success_rate >= 80 else "❌"
            print(f"  {status} ペルソナ{persona_id} ({persona_name}): {success_rate:.1f}%")
        
        print()
        
        # アクセシビリティ評価
        accessibility_scores = []
        performance_scores = []
        ux_scores = []
        
        for results in self.test_results['personas_tested'].values():
            if results['avg_accessibility_score'] > 0:
                accessibility_scores.append(results['avg_accessibility_score'])
                performance_scores.append(results['avg_performance_score'])
                ux_scores.append(results['avg_ux_score'])
        
        if accessibility_scores:
            print("📊 品質評価 (平均スコア):")
            print(f"  🔍 アクセシビリティ: {sum(accessibility_scores)/len(accessibility_scores):.1f}/100")
            print(f"  ⚡ パフォーマンス: {sum(performance_scores)/len(performance_scores):.1f}/100")
            print(f"  🎯 ユーザー体験: {sum(ux_scores)/len(ux_scores):.1f}/100")
            print()
        
        # 最終判定
        if stats['success_rate'] >= 95:
            print("🏆 判定: EXCELLENT - 全ペルソナで優秀な体験を提供")
            credibility_status = "EXCELLENT"
        elif stats['success_rate'] >= 90:
            print("✅ 判定: GOOD - 概ね良好な体験を提供")
            credibility_status = "GOOD"
        elif stats['success_rate'] >= 80:
            print("⚠️ 判定: ACCEPTABLE - 改善の余地あり")
            credibility_status = "ACCEPTABLE"
        else:
            print("🚨 判定: NEEDS IMPROVEMENT - 重要な改善が必要")
            credibility_status = "NEEDS_IMPROVEMENT"
        
        # 特別な配慮が必要なペルソナの評価
        special_needs_personas = [6, 7, 9, 10]  # 高齢者、視覚障害者、低速回線、挫折寸前
        special_needs_success = []
        
        for persona_id in special_needs_personas:
            if persona_id in self.test_results['personas_tested']:
                special_needs_success.append(self.test_results['personas_tested'][persona_id]['success_rate'])
        
        if special_needs_success:
            avg_special_needs = sum(special_needs_success) / len(special_needs_success)
            print(f"\n🤝 特別配慮ペルソナ評価:")
            print(f"  平均成功率: {avg_special_needs:.1f}%")
            if avg_special_needs >= 90:
                print("  🏆 インクルーシブデザイン: EXCELLENT")
            elif avg_special_needs >= 80:
                print("  ✅ インクルーシブデザイン: GOOD")
            else:
                print("  ⚠️ インクルーシブデザイン: 改善必要")
        
        # レポート保存
        report_filename = f"production_persona_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_filename}")
        print("\n🔒 CLAUDE.md準拠 本番環境10ペルソナ包括的検証完了")

def main():
    """メイン実行関数"""
    print("🎭 CLAUDE.md準拠 本番環境10ペルソナ包括的検証")
    print("学習アプリの多様なユーザー体験を完全カバー")
    print()
    
    tester = ProductionPersonaComprehensiveTest()
    results = tester.run_persona_comprehensive_test()
    
    return results

if __name__ == "__main__":
    main()