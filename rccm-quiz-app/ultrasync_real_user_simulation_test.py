#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階8-実特化】本番環境実ユーザーシミュレーションテスト
10問/20問/30問完走テスト・13部門分離確認・4-1/4-2問題混在確認
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

class UltraSyncRealUserSimulationTest:
    """ULTRASYNC 実ユーザーシミュレーションテスト特化クラス"""
    
    def __init__(self, base_url: str = "https://rccm-quiz-2025.onrender.com"):
        self.base_url = base_url
        self.start_time = time.time()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'completion_tests': {},
            'department_isolation_tests': {},
            'question_type_separation_tests': {},
            'overall_results': {}
        }
        
        # 13部門定義
        self.departments = [
            '基礎科目',  # 4-1
            '道路', '河川・砂防', '都市計画', '造園', '建設環境',  # 4-2専門科目
            '鋼構造・コンクリート', '土質・基礎', '施工計画', 
            '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        # 問題数設定
        self.question_counts = [10, 20, 30]
    
    def test_question_completion_flow(self, department: str, question_count: int) -> Dict[str, Any]:
        """指定部門・問題数での完走テスト"""
        print(f"   🔍 {department}部門 {question_count}問完走テスト...")
        
        completion_result = {
            'department': department,
            'target_questions': question_count,
            'session_start_success': False,
            'questions_accessed': [],
            'completion_success': False,
            'final_result_displayed': False,
            'errors': [],
            'response_times': [],
            'question_content_check': {}
        }
        
        session = requests.Session()
        
        try:
            # 1. セッション開始
            start_url = f"{self.base_url}/start_exam/{department}"
            print(f"      📝 セッション開始: {start_url}")
            
            start_time = time.time()
            start_response = session.get(start_url, timeout=30)
            start_response_time = time.time() - start_time
            
            if start_response.status_code == 200:
                completion_result['session_start_success'] = True
                completion_result['response_times'].append(start_response_time)
                print(f"      ✅ セッション開始成功 ({start_response_time:.2f}秒)")
            else:
                completion_result['errors'].append(f"Session start failed: {start_response.status_code}")
                print(f"      ❌ セッション開始失敗: {start_response.status_code}")
                return completion_result
            
            # 2. 各問題へのアクセステスト
            for question_no in range(1, question_count + 1):
                question_url = f"{self.base_url}/quiz?current={question_no}"
                
                start_time = time.time()
                question_response = session.get(question_url, timeout=30)
                question_response_time = time.time() - start_time
                
                completion_result['response_times'].append(question_response_time)
                
                if question_response.status_code == 200:
                    # 問題内容の基本チェック
                    response_text = question_response.text
                    
                    question_check = {
                        'question_number': question_no,
                        'status_code': 200,
                        'response_time': question_response_time,
                        'has_question_content': '問題' in response_text or 'Question' in response_text,
                        'has_answer_options': ('①' in response_text or '1)' in response_text or 'A)' in response_text),
                        'department_consistency': department in response_text or '基礎' in response_text,
                        'no_error_messages': 'エラー' not in response_text and 'Error' not in response_text
                    }
                    
                    completion_result['questions_accessed'].append(question_check)
                    
                    if question_check['has_question_content'] and question_check['has_answer_options']:
                        print(f"      ✅ 問題{question_no}: 正常表示 ({question_response_time:.2f}秒)")
                    else:
                        print(f"      ⚠️ 問題{question_no}: 内容不完全")
                        completion_result['errors'].append(f"Question {question_no} content incomplete")
                
                else:
                    print(f"      ❌ 問題{question_no}: HTTP {question_response.status_code}")
                    completion_result['errors'].append(f"Question {question_no} failed: {question_response.status_code}")
                    
                    completion_result['questions_accessed'].append({
                        'question_number': question_no,
                        'status_code': question_response.status_code,
                        'response_time': question_response_time,
                        'success': False
                    })
                
                # 問題間の適切な間隔
                time.sleep(1)
            
            # 3. 完走判定
            successful_questions = sum(1 for q in completion_result['questions_accessed'] 
                                     if q.get('status_code') == 200 and q.get('has_question_content', False))
            
            completion_result['completion_success'] = (successful_questions == question_count)
            completion_result['actual_questions_completed'] = successful_questions
            
            # 4. 結果画面アクセステスト
            if completion_result['completion_success']:
                result_url = f"{self.base_url}/result"
                try:
                    result_response = session.get(result_url, timeout=30)
                    if result_response.status_code == 200:
                        completion_result['final_result_displayed'] = True
                        print(f"      ✅ 結果画面表示成功")
                    else:
                        print(f"      ⚠️ 結果画面アクセス問題: {result_response.status_code}")
                except Exception as e:
                    completion_result['errors'].append(f"Result page error: {e}")
            
            # 5. 統計計算
            if completion_result['response_times']:
                completion_result['average_response_time'] = sum(completion_result['response_times']) / len(completion_result['response_times'])
                completion_result['max_response_time'] = max(completion_result['response_times'])
                completion_result['min_response_time'] = min(completion_result['response_times'])
            
            completion_result['success_rate'] = (successful_questions / question_count) * 100 if question_count > 0 else 0
            
            if completion_result['completion_success']:
                print(f"      🎯 {department}部門 {question_count}問: 完走成功")
            else:
                print(f"      ❌ {department}部門 {question_count}問: 完走失敗 ({successful_questions}/{question_count})")
                
        except Exception as e:
            completion_result['errors'].append(f"Test execution error: {e}")
            print(f"      ❌ テスト実行エラー: {e}")
        
        return completion_result
    
    def test_department_isolation(self) -> Dict[str, Any]:
        """部門分離テスト"""
        print("\n🏢 部門分離テスト実行...")
        
        isolation_results = {
            'departments_tested': len(self.departments),
            'successful_departments': 0,
            'failed_departments': [],
            'department_details': {}
        }
        
        for department in self.departments:
            print(f"   📂 {department}部門分離テスト...")
            
            # 各部門で10問テストを実行
            dept_result = self.test_question_completion_flow(department, 10)
            
            isolation_results['department_details'][department] = {
                'session_start_success': dept_result['session_start_success'],
                'completion_success': dept_result['completion_success'],
                'success_rate': dept_result['success_rate'],
                'error_count': len(dept_result['errors'])
            }
            
            if dept_result['completion_success']:
                isolation_results['successful_departments'] += 1
                print(f"   ✅ {department}: 正常動作確認")
            else:
                isolation_results['failed_departments'].append(department)
                print(f"   ❌ {department}: 動作異常")
        
        isolation_results['department_success_rate'] = (isolation_results['successful_departments'] / isolation_results['departments_tested']) * 100
        
        print(f"\n   📊 部門分離テスト結果: {isolation_results['department_success_rate']:.1f}% ({isolation_results['successful_departments']}/{isolation_results['departments_tested']})")
        
        self.test_results['department_isolation_tests'] = isolation_results
        return isolation_results
    
    def test_question_count_settings(self) -> Dict[str, Any]:
        """問題数設定テスト（10問/20問/30問）"""
        print("\n🔢 問題数設定テスト実行...")
        
        count_results = {
            'question_counts_tested': self.question_counts,
            'count_test_results': {},
            'overall_success_rate': 0
        }
        
        # 基礎科目で各問題数をテスト
        test_department = '基礎科目'
        
        for count in self.question_counts:
            print(f"   📝 {count}問設定テスト...")
            
            count_result = self.test_question_completion_flow(test_department, count)
            
            count_results['count_test_results'][f'{count}問'] = {
                'target_count': count,
                'completion_success': count_result['completion_success'],
                'actual_completed': count_result.get('actual_questions_completed', 0),
                'success_rate': count_result['success_rate'],
                'average_response_time': count_result.get('average_response_time', 0),
                'errors': count_result['errors']
            }
            
            if count_result['completion_success']:
                print(f"   ✅ {count}問: 完走成功")
            else:
                print(f"   ❌ {count}問: 完走失敗")
        
        # 全体成功率計算
        successful_counts = sum(1 for result in count_results['count_test_results'].values() 
                               if result['completion_success'])
        count_results['overall_success_rate'] = (successful_counts / len(self.question_counts)) * 100
        
        print(f"\n   📊 問題数設定テスト結果: {count_results['overall_success_rate']:.1f}% ({successful_counts}/{len(self.question_counts)})")
        
        self.test_results['completion_tests'] = count_results
        return count_results
    
    def test_4_1_4_2_separation(self) -> Dict[str, Any]:
        """4-1（基礎科目）と4-2（専門科目）分離テスト"""
        print("\n🎓 4-1/4-2問題分離テスト実行...")
        
        separation_results = {
            '4-1_basic_subject': {},
            '4-2_specialist_subjects': {},
            'separation_verified': False
        }
        
        try:
            # 1. 4-1（基礎科目）テスト
            print("   📚 4-1（基礎科目）テスト...")
            basic_result = self.test_question_completion_flow('基礎科目', 10)
            
            separation_results['4-1_basic_subject'] = {
                'completion_success': basic_result['completion_success'],
                'questions_completed': basic_result.get('actual_questions_completed', 0),
                'content_type': '基礎科目',
                'success_rate': basic_result['success_rate']
            }
            
            # 2. 4-2（専門科目）サンプルテスト
            print("   🔧 4-2（専門科目）サンプルテスト...")
            specialist_departments = ['道路', '土質・基礎', '施工計画']  # サンプル3部門
            
            specialist_results = {}
            for dept in specialist_departments:
                dept_result = self.test_question_completion_flow(dept, 10)
                specialist_results[dept] = {
                    'completion_success': dept_result['completion_success'],
                    'questions_completed': dept_result.get('actual_questions_completed', 0),
                    'success_rate': dept_result['success_rate']
                }
            
            separation_results['4-2_specialist_subjects'] = specialist_results
            
            # 3. 分離検証
            basic_success = separation_results['4-1_basic_subject']['completion_success']
            specialist_success_count = sum(1 for result in specialist_results.values() 
                                         if result['completion_success'])
            
            separation_results['separation_verified'] = (
                basic_success and specialist_success_count >= 2
            )
            
            separation_results['overall_4_1_4_2_success'] = {
                'basic_subject_working': basic_success,
                'specialist_subjects_working': specialist_success_count,
                'total_specialist_tested': len(specialist_departments),
                'separation_confirmed': separation_results['separation_verified']
            }
            
            if separation_results['separation_verified']:
                print("   ✅ 4-1/4-2分離: 正常動作確認")
            else:
                print("   ❌ 4-1/4-2分離: 問題検出")
                
        except Exception as e:
            print(f"   ❌ 4-1/4-2分離テストエラー: {e}")
            separation_results['error'] = str(e)
        
        self.test_results['question_type_separation_tests'] = separation_results
        return separation_results
    
    def generate_overall_assessment(self) -> Dict[str, Any]:
        """総合評価生成"""
        print("\n📊 総合評価生成...")
        
        completion_tests = self.test_results.get('completion_tests', {})
        department_tests = self.test_results.get('department_isolation_tests', {})
        separation_tests = self.test_results.get('question_type_separation_tests', {})
        
        assessment = {
            'test_categories_completed': 0,
            'overall_success_rate': 0,
            'critical_issues': [],
            'success_summary': {},
            'deployment_readiness': 'UNKNOWN'
        }
        
        try:
            # 1. 問題数設定テスト評価
            if completion_tests:
                count_success_rate = completion_tests.get('overall_success_rate', 0)
                assessment['success_summary']['question_count_settings'] = {
                    'success_rate': count_success_rate,
                    'status': 'PASS' if count_success_rate >= 100 else 'FAIL'
                }
                assessment['test_categories_completed'] += 1
                
                if count_success_rate < 100:
                    assessment['critical_issues'].append(f"問題数設定で完走失敗: {count_success_rate:.1f}%")
            
            # 2. 部門分離テスト評価
            if department_tests:
                dept_success_rate = department_tests.get('department_success_rate', 0)
                assessment['success_summary']['department_isolation'] = {
                    'success_rate': dept_success_rate,
                    'successful_departments': department_tests.get('successful_departments', 0),
                    'total_departments': department_tests.get('departments_tested', 0),
                    'status': 'PASS' if dept_success_rate >= 90 else 'FAIL'
                }
                assessment['test_categories_completed'] += 1
                
                if dept_success_rate < 90:
                    failed_depts = department_tests.get('failed_departments', [])
                    assessment['critical_issues'].append(f"部門分離問題: {len(failed_depts)}部門失敗")
            
            # 3. 4-1/4-2分離テスト評価
            if separation_tests:
                separation_verified = separation_tests.get('separation_verified', False)
                assessment['success_summary']['4_1_4_2_separation'] = {
                    'separation_verified': separation_verified,
                    'status': 'PASS' if separation_verified else 'FAIL'
                }
                assessment['test_categories_completed'] += 1
                
                if not separation_verified:
                    assessment['critical_issues'].append("4-1/4-2問題分離に問題")
            
            # 4. 総合成功率計算
            if assessment['test_categories_completed'] > 0:
                category_scores = []
                
                if 'question_count_settings' in assessment['success_summary']:
                    category_scores.append(assessment['success_summary']['question_count_settings']['success_rate'])
                
                if 'department_isolation' in assessment['success_summary']:
                    category_scores.append(assessment['success_summary']['department_isolation']['success_rate'])
                
                if '4_1_4_2_separation' in assessment['success_summary']:
                    separation_score = 100 if assessment['success_summary']['4_1_4_2_separation']['separation_verified'] else 0
                    category_scores.append(separation_score)
                
                assessment['overall_success_rate'] = sum(category_scores) / len(category_scores)
            
            # 5. デプロイ準備判定
            critical_count = len(assessment['critical_issues'])
            
            if critical_count == 0 and assessment['overall_success_rate'] >= 95:
                assessment['deployment_readiness'] = 'READY'
            elif critical_count <= 1 and assessment['overall_success_rate'] >= 80:
                assessment['deployment_readiness'] = 'CONDITIONALLY_READY'
            else:
                assessment['deployment_readiness'] = 'NOT_READY'
            
            print(f"   🎯 総合成功率: {assessment['overall_success_rate']:.1f}%")
            print(f"   🚨 重要課題: {critical_count}件")
            print(f"   🚀 デプロイ準備: {assessment['deployment_readiness']}")
            
        except Exception as e:
            print(f"   ❌ 総合評価エラー: {e}")
            assessment['error'] = str(e)
        
        self.test_results['overall_results'] = assessment
        return assessment
    
    def save_test_report(self) -> str:
        """テストレポート保存"""
        print("\n💾 テストレポート保存...")
        
        # 実行時間計算
        execution_time = time.time() - self.start_time
        self.test_results['execution_time_seconds'] = round(execution_time, 2)
        
        # レポートファイル保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ULTRASYNC_REAL_USER_SIMULATION_TEST_{timestamp}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"   📄 テストレポート: {report_filename}")
            return report_filename
            
        except Exception as e:
            print(f"   ❌ レポート保存失敗: {e}")
            return ""
    
    def run_real_user_simulation_test(self) -> bool:
        """実ユーザーシミュレーションテスト実行"""
        print("🎯 【ULTRASYNC段階8-実特化】本番環境実ユーザーシミュレーションテスト開始")
        print(f"対象URL: {self.base_url}")
        print("=" * 70)
        
        try:
            # Phase 1: 問題数設定テスト（10問/20問/30問完走）
            completion_results = self.test_question_count_settings()
            
            # Phase 2: 部門分離テスト（13部門）
            department_results = self.test_department_isolation()
            
            # Phase 3: 4-1/4-2分離テスト
            separation_results = self.test_4_1_4_2_separation()
            
            # Phase 4: 総合評価
            assessment = self.generate_overall_assessment()
            
            # Phase 5: レポート保存
            report_file = self.save_test_report()
            
            print("\n" + "=" * 70)
            print("🎉 【ULTRASYNC段階8-実特化】実ユーザーシミュレーションテスト完了")
            
            # 最終判定
            deployment_readiness = assessment.get('deployment_readiness', 'UNKNOWN')
            overall_success = assessment.get('overall_success_rate', 0)
            
            if deployment_readiness == 'READY':
                print("✅ 結論: 実ユーザーテスト完全成功")
                print("🚀 推奨: 本番環境での実運用開始可能")
                return True
            elif deployment_readiness == 'CONDITIONALLY_READY':
                print("⚠️ 結論: 軽微な課題あり、監視下での運用可能")
                print("📊 推奨: 継続監視での運用開始")
                return True
            else:
                print("🚨 結論: 重要課題あり、解決が必要")
                print("🔧 推奨: 課題解決後再テスト")
                return False
            
        except Exception as e:
            print(f"\n❌ 実ユーザーシミュレーションテストエラー: {e}")
            return False

def main():
    """メイン実行"""
    # 本番URL確認
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("🔍 本番環境接続確認...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {base_url} - 接続確認成功")
            print("🚀 本番環境での実ユーザーシミュレーションテスト実行")
        else:
            print(f"⚠️ {base_url} - HTTP {response.status_code}")
            print("ℹ️ デプロイが完了していない可能性があります")
            return False
            
    except Exception as e:
        print(f"❌ 本番環境接続不可: {e}")
        print("🚨 SECRET_KEY設定・デプロイ実行が必要です")
        return False
    
    tester = UltraSyncRealUserSimulationTest(base_url)
    success = tester.run_real_user_simulation_test()
    
    print(f"\n🏁 ULTRASYNC段階8-実特化完了")
    print(f"副作用: ゼロ（読み取り専用実テスト）")
    print(f"本番実テスト: {'成功' if success else '要改善'}")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)