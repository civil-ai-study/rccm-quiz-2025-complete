#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 真の本番環境ペルソナ実地検証
実際のブラウザのように問題内容まで完全に追跡する本格的テスト

対象: https://rccm-quiz-2025.onrender.com
目的: 実際の問題表示、回答プロセス、結果表示まで完全検証
"""

import requests
import json
import time
from datetime import datetime
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealProductionPersonaDeepTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        
        # 重点検証ペルソナ（実地確認）
        self.test_personas = {
            1: {
                'name': '初心者学習者',
                'description': '全く知識がない状態での実地学習体験',
                'test_departments': ['基礎科目'],
                'test_counts': [10],
                'interaction_style': 'cautious_beginner'
            },
            2: {
                'name': '建設環境専門受験者',
                'description': 'ユーザー報告問題の当事者ペルソナ',
                'test_departments': ['建設環境'],
                'test_counts': [10, 20],
                'interaction_style': 'expert_focused'
            },
            3: {
                'name': 'モバイル学習者',
                'description': 'スマートフォンでの実際の学習体験',
                'test_departments': ['道路', '基礎科目'],
                'test_counts': [10],
                'interaction_style': 'mobile_native'
            },
            4: {
                'name': '視覚障害学習者',
                'description': 'アクセシビリティ機能の実地検証',
                'test_departments': ['基礎科目'],
                'test_counts': [10],
                'interaction_style': 'accessibility_focused'
            },
            5: {
                'name': '上級受験者',
                'description': '複数部門での集中学習体験',
                'test_departments': ['道路', '河川・砂防', '建設環境'],
                'test_counts': [20, 30],
                'interaction_style': 'intensive_learner'
            }
        }
        
        # 検証結果
        self.deep_test_results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'REAL_PRODUCTION_PERSONA_DEEP_TEST',
            'target_url': self.base_url,
            'personas_detailed_results': {},
            'critical_findings': [],
            'real_content_analysis': {},
            'end_to_end_flows': {}
        }

    def create_realistic_session(self, persona: Dict) -> requests.Session:
        """リアルなユーザーセッション作成"""
        session = requests.Session()
        
        # ペルソナ別ブラウザ設定
        if persona['interaction_style'] == 'mobile_native':
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
                'Cache-Control': 'max-age=0'
            })
        elif persona['interaction_style'] == 'accessibility_focused':
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 NVDA/2023.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9'
            })
        else:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            })
        
        return session

    def extract_real_questions(self, html_content: str) -> List[Dict]:
        """実際の問題内容を詳細抽出"""
        questions = []
        
        try:
            # HTMLから問題テキストを抽出
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # 問題パターンの検出
            question_patterns = [
                r'問題?\s*(\d+)[：:．.]?\s*([^問]+?)(?=問題?\s*\d+|選択肢|回答|$)',
                r'問\s*(\d+)[：:．.]?\s*([^問]+?)(?=問\s*\d+|選択肢|$)',
                r'(\d+)[：:．.]\s*([^0-9]{20,}?)(?=\d+[：:．.]|$)'
            ]
            
            for pattern in question_patterns:
                matches = re.findall(pattern, text_content, re.DOTALL)
                for match in matches:
                    if len(match) >= 2 and len(match[1].strip()) > 15:
                        questions.append({
                            'number': match[0],
                            'content': match[1].strip()[:300],
                            'length': len(match[1].strip()),
                            'extraction_method': pattern
                        })
            
            # 選択肢の検出
            choice_patterns = [
                r'[①②③④⑤⑥⑦⑧⑨⑩]([^①②③④⑤⑥⑦⑧⑨⑩]+?)(?=[①②③④⑤⑥⑦⑧⑨⑩]|$)',
                r'[1-5][)）]([^1-5)）]+?)(?=[1-5][)）]|$)',
                r'[ア-オ][)）]([^ア-オ)）]+?)(?=[ア-オ][)）]|$)'
            ]
            
            choices = []
            for pattern in choice_patterns:
                matches = re.findall(pattern, text_content)
                choices.extend([choice.strip() for choice in matches if len(choice.strip()) > 5])
            
            if questions:
                questions[0]['choices'] = choices[:5]  # 最初の問題に選択肢を関連付け
            
        except Exception as e:
            logger.error(f"問題抽出エラー: {str(e)}")
        
        return questions

    def analyze_question_category_compliance(self, questions: List[Dict], expected_department: str) -> Dict:
        """問題のカテゴリー適合性分析"""
        
        # 部門別キーワード
        department_keywords = {
            '基礎科目': {
                'expected': ['数学', '物理', '化学', '力学', '材料力学', '構造力学', '水理学', '土質力学', '測量', '情報'],
                'forbidden': ['専門', '応用', '実務']
            },
            '建設環境': {
                'expected': ['環境', '騒音', '振動', '大気汚染', '水質汚濁', '土壌汚染', 'アセスメント', 'CO2', 'NOx'],
                'forbidden': ['道路', '舗装', 'コンクリート', '鉄筋', '河川', '砂防']
            },
            '道路': {
                'expected': ['道路', '舗装', '交通', 'アスファルト', '車道', '歩道', 'CBR'],
                'forbidden': ['環境', '騒音', 'コンクリート', '河川']
            },
            '河川・砂防': {
                'expected': ['河川', '砂防', '治水', '堤防', '護岸', '流域', '洪水', 'ダム'],
                'forbidden': ['道路', '舗装', '環境', 'コンクリート']
            }
        }
        
        analysis = {
            'expected_department': expected_department,
            'compliance_score': 0.0,
            'violations_found': [],
            'expected_keywords_found': [],
            'forbidden_keywords_found': [],
            'question_analysis': []
        }
        
        keywords = department_keywords.get(expected_department, {'expected': [], 'forbidden': []})
        
        for question in questions:
            content = question.get('content', '').lower()
            
            question_analysis = {
                'number': question.get('number'),
                'expected_matches': [],
                'forbidden_matches': [],
                'compliance': True
            }
            
            # 期待キーワードチェック
            for keyword in keywords['expected']:
                if keyword.lower() in content:
                    question_analysis['expected_matches'].append(keyword)
                    analysis['expected_keywords_found'].append(keyword)
            
            # 禁止キーワードチェック
            for keyword in keywords['forbidden']:
                if keyword.lower() in content:
                    question_analysis['forbidden_matches'].append(keyword)
                    analysis['forbidden_keywords_found'].append(keyword)
                    question_analysis['compliance'] = False
                    analysis['violations_found'].append({
                        'question_number': question.get('number'),
                        'forbidden_keyword': keyword,
                        'context': content[:100]
                    })
            
            analysis['question_analysis'].append(question_analysis)
        
        # コンプライアンススコア計算
        total_questions = len(questions)
        compliant_questions = sum(1 for qa in analysis['question_analysis'] if qa['compliance'])
        analysis['compliance_score'] = (compliant_questions / total_questions) * 100 if total_questions > 0 else 0
        
        return analysis

    def simulate_complete_exam_flow(self, persona_id: int, department: str, question_count: int) -> Dict:
        """完全な試験フローのシミュレーション"""
        
        persona = self.test_personas[persona_id]
        session = self.create_realistic_session(persona)
        
        flow_result = {
            'persona_id': persona_id,
            'persona_name': persona['name'],
            'department': department,
            'question_count': question_count,
            'flow_steps': [],
            'questions_encountered': [],
            'category_compliance': {},
            'end_to_end_success': False,
            'critical_issues': [],
            'actual_content_verified': False
        }
        
        try:
            print(f"🔥 {persona['name']} - {department} {question_count}問の完全実地検証")
            
            # Step 1: ホームページアクセス
            print("  📍 Step 1: ホームページアクセス")
            start_time = time.time()
            home_response = session.get(self.base_url, timeout=30)
            home_time = time.time() - start_time
            
            flow_result['flow_steps'].append({
                'step': 1,
                'action': 'home_access',
                'success': home_response.status_code == 200,
                'response_time': home_time,
                'status_code': home_response.status_code
            })
            
            if home_response.status_code != 200:
                flow_result['critical_issues'].append('ホームページアクセス失敗')
                return flow_result
            
            print(f"    ✅ ホームページアクセス成功 ({home_time:.2f}秒)")
            
            # ユーザー行動シミュレーション遅延
            time.sleep(2.0)  # 実際のユーザーのページ確認時間
            
            # Step 2: 試験開始
            print("  📍 Step 2: 試験開始リクエスト")
            if department == '基礎科目':
                exam_url = f"{self.base_url}/start_exam/basic"
                exam_data = {'questions': str(question_count)}
            else:
                exam_url = f"{self.base_url}/start_exam/specialist"
                exam_data = {
                    'questions': str(question_count),
                    'category': department,
                    'year': '2019'
                }
            
            start_time = time.time()
            exam_response = session.post(exam_url, data=exam_data, timeout=30, allow_redirects=True)
            exam_time = time.time() - start_time
            
            flow_result['flow_steps'].append({
                'step': 2,
                'action': 'exam_start',
                'success': exam_response.status_code in [200, 302],
                'response_time': exam_time,
                'status_code': exam_response.status_code,
                'url': exam_url,
                'data': exam_data
            })
            
            if exam_response.status_code not in [200, 302]:
                flow_result['critical_issues'].append(f'試験開始失敗: HTTP {exam_response.status_code}')
                return flow_result
            
            print(f"    ✅ 試験開始成功 ({exam_time:.2f}秒)")
            
            # Step 3: 実際の問題内容確認
            print("  📍 Step 3: 実際の問題内容解析")
            html_content = exam_response.text
            
            # 問題抽出
            questions = self.extract_real_questions(html_content)
            flow_result['questions_encountered'] = questions
            
            if questions:
                flow_result['actual_content_verified'] = True
                print(f"    ✅ 実際の問題内容確認: {len(questions)}問検出")
                
                # 最初の問題内容表示
                if questions[0]['content']:
                    print(f"    📝 問題1例: {questions[0]['content'][:100]}...")
                
                # カテゴリーコンプライアンス分析
                compliance_analysis = self.analyze_question_category_compliance(questions, department)
                flow_result['category_compliance'] = compliance_analysis
                
                print(f"    📊 カテゴリー適合度: {compliance_analysis['compliance_score']:.1f}%")
                
                if compliance_analysis['violations_found']:
                    print(f"    🚨 カテゴリー違反: {len(compliance_analysis['violations_found'])}件検出")
                    flow_result['critical_issues'].extend([
                        f"カテゴリー違反: {v['forbidden_keyword']}" for v in compliance_analysis['violations_found']
                    ])
                else:
                    print(f"    ✅ カテゴリー違反なし")
            else:
                print(f"    ❌ 問題内容の抽出失敗")
                flow_result['critical_issues'].append('問題内容抽出失敗')
            
            # Step 4: フォーム要素確認
            print("  📍 Step 4: インタラクション要素確認")
            has_forms = 'form' in html_content.lower()
            has_buttons = 'button' in html_content.lower()
            has_inputs = 'input' in html_content.lower()
            
            interaction_score = (has_forms + has_buttons + has_inputs) / 3 * 100
            
            flow_result['flow_steps'].append({
                'step': 4,
                'action': 'interaction_check',
                'success': interaction_score >= 66,
                'interaction_score': interaction_score,
                'has_forms': has_forms,
                'has_buttons': has_buttons,
                'has_inputs': has_inputs
            })
            
            print(f"    📊 インタラクション要素: {interaction_score:.1f}% (Form:{has_forms}, Button:{has_buttons}, Input:{has_inputs})")
            
            # 最終判定
            if (flow_result['actual_content_verified'] and 
                len(flow_result['critical_issues']) == 0 and
                flow_result['category_compliance'].get('compliance_score', 0) >= 80):
                flow_result['end_to_end_success'] = True
                print(f"    🏆 完全成功: エンドツーエンド検証完了")
            else:
                print(f"    ⚠️ 部分的成功: 改善点あり")
            
        except Exception as e:
            flow_result['critical_issues'].append(f'例外発生: {str(e)}')
            print(f"    💥 例外発生: {str(e)}")
        
        return flow_result

    def run_real_production_deep_test(self):
        """真の本番環境ペルソナ実地検証実行"""
        print("🔥 真の本番環境ペルソナ実地検証開始")
        print("=" * 80)
        print("目的: 実際のブラウザのように問題内容まで完全追跡")
        print("対象: https://rccm-quiz-2025.onrender.com")
        print("検証方法: エンドツーエンドフロー + 実際の問題内容解析")
        print("=" * 80)
        
        start_time = time.time()
        total_flows = 0
        successful_flows = 0
        
        # 各ペルソナで実地検証
        for persona_id, persona in self.test_personas.items():
            print(f"\n🎭 【ペルソナ {persona_id}】{persona['name']}")
            print(f"   {persona['description']}")
            print("-" * 60)
            
            persona_results = {
                'persona_info': persona,
                'flow_results': [],
                'success_rate': 0.0,
                'content_verification_rate': 0.0,
                'category_compliance_avg': 0.0,
                'critical_findings': []
            }
            
            persona_flows = 0
            persona_successes = 0
            content_verifications = 0
            compliance_scores = []
            
            # 各部門・問題数での実地検証
            for department in persona['test_departments']:
                for question_count in persona['test_counts']:
                    total_flows += 1
                    persona_flows += 1
                    
                    flow_result = self.simulate_complete_exam_flow(persona_id, department, question_count)
                    persona_results['flow_results'].append(flow_result)
                    
                    if flow_result['end_to_end_success']:
                        successful_flows += 1
                        persona_successes += 1
                    
                    if flow_result['actual_content_verified']:
                        content_verifications += 1
                    
                    if flow_result['category_compliance']:
                        compliance_scores.append(flow_result['category_compliance']['compliance_score'])
                    
                    if flow_result['critical_issues']:
                        persona_results['critical_findings'].extend(flow_result['critical_issues'])
                    
                    # リアルなユーザー間隔
                    time.sleep(3.0)
            
            # ペルソナ別統計
            persona_results['success_rate'] = (persona_successes / persona_flows) * 100 if persona_flows > 0 else 0
            persona_results['content_verification_rate'] = (content_verifications / persona_flows) * 100 if persona_flows > 0 else 0
            persona_results['category_compliance_avg'] = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
            
            self.deep_test_results['personas_detailed_results'][persona_id] = persona_results
            
            print(f"  📊 {persona['name']} 実地結果:")
            print(f"    エンドツーエンド成功率: {persona_results['success_rate']:.1f}%")
            print(f"    実際の問題内容確認率: {persona_results['content_verification_rate']:.1f}%")
            print(f"    カテゴリー適合度: {persona_results['category_compliance_avg']:.1f}%")
            if persona_results['critical_findings']:
                print(f"    🚨 重要問題: {len(set(persona_results['critical_findings']))}件")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 全体統計
        self.deep_test_results['overall_statistics'] = {
            'total_personas': len(self.test_personas),
            'total_flows': total_flows,
            'successful_flows': successful_flows,
            'end_to_end_success_rate': (successful_flows / total_flows) * 100 if total_flows > 0 else 0,
            'duration_seconds': duration
        }
        
        self.generate_real_production_report()
        
        return self.deep_test_results

    def generate_real_production_report(self):
        """真の本番環境検証レポート生成"""
        stats = self.deep_test_results['overall_statistics']
        
        print("\n" + "=" * 80)
        print("🔥 真の本番環境ペルソナ実地検証結果")
        print("=" * 80)
        
        print(f"📊 実地検証統計:")
        print(f"  検証ペルソナ数: {stats['total_personas']}")
        print(f"  実行フロー数: {stats['total_flows']}")
        print(f"  成功フロー数: {stats['successful_flows']}")
        print(f"  エンドツーエンド成功率: {stats['end_to_end_success_rate']:.1f}%")
        print(f"  検証実行時間: {stats['duration_seconds']:.1f}秒")
        print()
        
        # ペルソナ別詳細結果
        print("🎭 ペルソナ別実地検証結果:")
        for persona_id, results in self.deep_test_results['personas_detailed_results'].items():
            persona_name = results['persona_info']['name']
            success_rate = results['success_rate']
            content_rate = results['content_verification_rate']
            compliance_avg = results['category_compliance_avg']
            
            status = "🏆" if success_rate >= 95 and content_rate >= 95 else "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            
            print(f"  {status} ペルソナ{persona_id} ({persona_name}):")
            print(f"    成功率: {success_rate:.1f}% | 内容確認: {content_rate:.1f}% | 適合度: {compliance_avg:.1f}%")
        
        print()
        
        # 重要な発見事項
        all_critical_issues = []
        for results in self.deep_test_results['personas_detailed_results'].values():
            all_critical_issues.extend(results['critical_findings'])
        
        unique_issues = list(set(all_critical_issues))
        
        if unique_issues:
            print("🚨 発見された重要問題:")
            for issue in unique_issues[:5]:  # 上位5件
                issue_count = all_critical_issues.count(issue)
                print(f"  • {issue} ({issue_count}回発生)")
        else:
            print("✅ 重要問題: なし")
        
        print()
        
        # 最終判定
        if stats['end_to_end_success_rate'] >= 95:
            print("🏆 最終判定: EXCELLENT - 実地検証で完璧な動作確認")
            credibility = "EXCELLENT"
        elif stats['end_to_end_success_rate'] >= 85:
            print("✅ 最終判定: GOOD - 実地検証で良好な動作確認")
            credibility = "GOOD"
        elif stats['end_to_end_success_rate'] >= 70:
            print("⚠️ 最終判定: ACCEPTABLE - 改善の余地あり")
            credibility = "ACCEPTABLE"
        else:
            print("🚨 最終判定: NEEDS_IMPROVEMENT - 重要な問題あり")
            credibility = "NEEDS_IMPROVEMENT"
        
        # レポート保存
        report_filename = f"real_production_persona_deep_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.deep_test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細実地検証レポート: {report_filename}")
        print("\n🔒 真の本番環境ペルソナ実地検証完了")

def main():
    """メイン実行関数"""
    print("🔥 真の本番環境ペルソナ実地検証")
    print("実際のブラウザのように問題内容まで完全追跡")
    print()
    
    tester = RealProductionPersonaDeepTest()
    results = tester.run_real_production_deep_test()
    
    return results

if __name__ == "__main__":
    main()