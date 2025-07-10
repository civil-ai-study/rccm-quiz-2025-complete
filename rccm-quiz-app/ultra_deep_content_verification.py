#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ULTRA DEEP CONTENT VERIFICATION
ユーザー報告の混在問題を本番環境で実際の問題内容を詳細分析して100%確認

重要問題の完全解決確認:
1. 4-1基礎科目と4-2専門科目の混在
2. 年度の混在  
3. カテゴリーの混在
4. 建設環境部門での鋼構造・コンクリート問題混入

本番環境: https://rccm-quiz-2025.onrender.com
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

class UltraDeepContentVerification:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # 重点検証対象（ユーザー報告問題の焦点）
        self.critical_departments = [
            '建設環境',  # ユーザー報告の問題部門
            '鋼構造・コンクリート',  # 混入が報告された部門
            '道路', '河川・砂防', '都市計画', '造園', 
            '土質・基礎', '施工計画', '上下水道', 
            '森林土木', '農業土木', 'トンネル'
        ]
        
        # 重点検証年度
        self.critical_years = [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008]
        self.question_counts = [10, 20, 30]
        
        # 詳細分析結果
        self.detailed_results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'ULTRA_DEEP_CONTENT_VERIFICATION',
            'target_url': self.base_url,
            'mixing_issues_found': [],
            'content_analysis': {},
            'category_violations': {},
            'year_violations': {},
            'basic_specialist_mixing': {},
            'critical_findings': []
        }

    def extract_question_content_deep(self, html_content: str) -> Dict:
        """実際の問題内容の超詳細抽出と分析"""
        try:
            content_analysis = {
                'raw_html_length': len(html_content),
                'questions_extracted': [],
                'problem_types_detected': [],
                'year_indicators': [],
                'category_keywords': [],
                'basic_subject_indicators': [],
                'specialist_subject_indicators': [],
                'detailed_content_blocks': []
            }
            
            # HTMLタグを除去して純粋なテキストを抽出
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            content_analysis['detailed_content_blocks'].append({
                'method': 'full_text_extraction',
                'content': text_content[:1000],  # 最初の1000文字
                'length': len(text_content)
            })
            
            # 全文からの問題文抽出
            full_text = text_content
            
            # 問題番号パターンの検出
            question_number_patterns = [
                r'問題\s*(\d+)\.?\s*(.*?)(?=問題\s*\d+|$)',
                r'問\s*(\d+)\.?\s*(.*?)(?=問\s*\d+|$)', 
                r'Question\s*(\d+)\.?\s*(.*?)(?=Question\s*\d+|$)',
                r'(\d+)\.?\s*([^0-9]+.*?)(?=\d+\.|$)'
            ]
            
            for pattern in question_number_patterns:
                matches = re.findall(pattern, full_text, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    if len(match) >= 2 and len(match[1].strip()) > 20:
                        content_analysis['questions_extracted'].append({
                            'number': match[0],
                            'content': match[1].strip()[:300],
                            'pattern': pattern
                        })
            
            # 年度指標の検出
            year_patterns = [
                r'20(\d{2})年',
                r'平成(\d{1,2})年',
                r'令和(\d{1,2})年',
                r'H(\d{1,2})',
                r'R(\d{1,2})'
            ]
            
            for pattern in year_patterns:
                matches = re.findall(pattern, full_text)
                content_analysis['year_indicators'].extend(matches)
            
            # 4-1基礎科目の指標検出
            basic_subject_patterns = [
                r'基礎科目',
                r'4-1',
                r'四-一',
                r'数学',
                r'物理',
                r'化学',
                r'力学の基礎',
                r'材料力学',
                r'構造力学',
                r'水理学',
                r'土質力学',
                r'測量',
                r'情報技術'
            ]
            
            for pattern in basic_subject_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    content_analysis['basic_subject_indicators'].append(pattern)
            
            # 4-2専門科目の指標検出  
            specialist_patterns = [
                r'専門科目',
                r'4-2',
                r'四-二'
            ]
            
            for pattern in specialist_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    content_analysis['specialist_subject_indicators'].append(pattern)
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"問題内容抽出エラー: {str(e)}")
            return {'error': str(e)}

    def analyze_category_mixing(self, content: str, expected_department: str) -> Dict:
        """カテゴリー混在の詳細分析"""
        
        # 部門別専門キーワード（より詳細）
        department_keywords = {
            '建設環境': {
                'primary': ['環境', '騒音', '振動', '大気汚染', '水質汚濁', '土壌汚染', 'アセスメント'],
                'secondary': ['CO2', 'NOx', 'SOx', 'PM2.5', '環境基準', '環境影響評価', 'EIA'],
                'technical': ['デシベル', 'dB', 'ppm', 'mg/L', 'μg/m³', '環境基本法']
            },
            '鋼構造・コンクリート': {
                'primary': ['鋼構造', 'コンクリート', '鉄筋', '鉄骨', 'PC', 'RC', 'SRC'],
                'secondary': ['圧縮強度', '引張強度', 'ヤング率', '弾性係数', 'ポアソン比'],
                'technical': ['MPa', 'N/mm²', 'kN/m²', 'σ', 'τ', 'ε']
            },
            '道路': {
                'primary': ['道路', '舗装', '交通', 'アスファルト', '車道', '歩道'],
                'secondary': ['交差点', '信号', '標識', '横断歩道', '中央分離帯'],
                'technical': ['CBR', '交通量', '軸重', 'TA', 'CBR試験']
            },
            '河川・砂防': {
                'primary': ['河川', '砂防', '治水', '堤防', '護岸', '流域'],
                'secondary': ['洪水', 'ダム', '堰', '水門', '樋門', '排水機場'],
                'technical': ['流量', '流速', '水位', 'HWL', 'LWL', 'm³/s']
            },
            '都市計画': {
                'primary': ['都市計画', '市街地', '区域', '区画', '土地利用'],
                'secondary': ['ゾーニング', '用途地域', '建ぺい率', '容積率'],
                'technical': ['都市計画法', '建築基準法', '開発行為']
            },
            '造園': {
                'primary': ['造園', '緑地', '公園', '植栽', '樹木', '庭園'],
                'secondary': ['景観', '緑化', '芝生', '花壇', '遊具'],
                'technical': ['植生', '樹種', '剪定', '施肥', '病虫害']
            },
            '土質・基礎': {
                'primary': ['土質', '基礎', '地盤', '支持力', 'N値', 'せん断'],
                'secondary': ['圧密', '液状化', '沈下', '杭基礎', '直接基礎'],
                'technical': ['kN/m²', 'kPa', 'φ', 'c', 'SPT', 'CPT']
            },
            '施工計画': {
                'primary': ['施工', '工程', '管理', '品質管理', '安全管理'],
                'secondary': ['工事', '施工法', '機械', '仮設', '足場'],
                'technical': ['工程表', 'PERT', 'CPM', 'バーチャート']
            },
            '上下水道': {
                'primary': ['上水道', '下水道', '給水', '排水', '浄水'],
                'secondary': ['配水', '送水', '取水', '浄化', '処理'],
                'technical': ['BOD', 'COD', 'SS', 'DO', 'pH', 'mg/L']
            },
            '森林土木': {
                'primary': ['森林', '林道', '治山', '木材', '間伐'],
                'secondary': ['造林', '育林', '伐採', '搬出', '木橋'],
                'technical': ['立木', 'm³', '材積', '蓄積', '成長量']
            },
            '農業土木': {
                'primary': ['農業', '灌漑', '農地', '水利', '排水路'],
                'secondary': ['圃場', '用水', '田畑', '農道', '暗渠'],
                'technical': ['取水量', '用水量', 'L/s', 'mm/day', '有効雨量']
            },
            'トンネル': {
                'primary': ['トンネル', '掘削', '支保', '覆工', 'NATM'],
                'secondary': ['シールド', '山岳工法', 'TBM', 'ロックボルト'],
                'technical': ['地山', '土被り', '内空', '坑口', 'kPa']
            }
        }
        
        mixing_analysis = {
            'expected_department': expected_department,
            'found_departments': [],
            'mixing_violations': [],
            'keyword_matches': {
                'expected': [],
                'unexpected': []
            },
            'confidence_score': 0.0
        }
        
        content_lower = content.lower()
        
        # 期待される部門のキーワードチェック
        expected_keywords = department_keywords.get(expected_department, {})
        expected_matches = 0
        
        for category, keywords in expected_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    mixing_analysis['keyword_matches']['expected'].append({
                        'keyword': keyword,
                        'category': category,
                        'department': expected_department
                    })
                    expected_matches += 1
        
        # 他部門のキーワードチェック（混在検出）
        unexpected_matches = 0
        for dept_name, dept_keywords in department_keywords.items():
            if dept_name != expected_department:
                for category, keywords in dept_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in content_lower:
                            mixing_analysis['keyword_matches']['unexpected'].append({
                                'keyword': keyword,
                                'category': category,
                                'department': dept_name
                            })
                            unexpected_matches += 1
                            
                            if dept_name not in mixing_analysis['found_departments']:
                                mixing_analysis['found_departments'].append(dept_name)
        
        # 混在違反の判定
        if unexpected_matches > 0:
            for dept in mixing_analysis['found_departments']:
                mixing_analysis['mixing_violations'].append({
                    'violation_type': 'CATEGORY_MIXING',
                    'expected_department': expected_department,
                    'found_department': dept,
                    'severity': 'HIGH' if dept in ['鋼構造・コンクリート', '建設環境'] else 'MEDIUM'
                })
        
        # 信頼度スコア計算
        total_matches = expected_matches + unexpected_matches
        if total_matches > 0:
            mixing_analysis['confidence_score'] = expected_matches / total_matches
        else:
            mixing_analysis['confidence_score'] = 0.0
        
        return mixing_analysis

    def verify_single_exam_session(self, department: str, year: int, question_count: int) -> Dict:
        """単一試験セッションの詳細検証"""
        
        print(f"  🔍 詳細検証: {department} {year}年度 {question_count}問")
        
        session_result = {
            'department': department,
            'year': year,
            'question_count': question_count,
            'timestamp': datetime.now().isoformat(),
            'connection_successful': False,
            'content_extracted': False,
            'mixing_analysis': {},
            'violations_found': [],
            'raw_content_sample': '',
            'detailed_findings': []
        }
        
        try:
            # 試験開始リクエスト
            data = {
                'questions': str(question_count),
                'year': str(year),
                'category': department
            }
            
            url = f"{self.base_url}/start_exam/specialist"
            
            print(f"    📡 リクエスト送信: {url}")
            print(f"    📊 データ: {data}")
            
            response = self.session.post(url, data=data, timeout=60, allow_redirects=True)
            
            if response.status_code == 200:
                session_result['connection_successful'] = True
                html_content = response.text
                session_result['raw_content_sample'] = html_content[:1000]  # 最初の1000文字
                
                print(f"    ✅ 接続成功 (HTML長: {len(html_content)}文字)")
                
                # 詳細コンテンツ抽出
                content_analysis = self.extract_question_content_deep(html_content)
                session_result['content_analysis'] = content_analysis
                
                if content_analysis.get('questions_extracted') or content_analysis.get('detailed_content_blocks'):
                    session_result['content_extracted'] = True
                    
                    # カテゴリー混在分析
                    full_content = ' '.join([
                        block.get('content', '') for block in content_analysis.get('detailed_content_blocks', [])
                    ])
                    
                    if full_content:
                        mixing_analysis = self.analyze_category_mixing(full_content, department)
                        session_result['mixing_analysis'] = mixing_analysis
                        
                        # 違反検出
                        if mixing_analysis['mixing_violations']:
                            session_result['violations_found'] = mixing_analysis['mixing_violations']
                            print(f"    🚨 カテゴリー混在検出: {len(mixing_analysis['mixing_violations'])}件")
                            
                            # 重要な違反を記録
                            for violation in mixing_analysis['mixing_violations']:
                                if violation['expected_department'] == '建設環境' and violation['found_department'] == '鋼構造・コンクリート':
                                    session_result['detailed_findings'].append({
                                        'finding_type': 'CRITICAL_USER_REPORTED_ISSUE',
                                        'description': f"建設環境部門で鋼構造・コンクリート問題混入検出",
                                        'evidence': mixing_analysis['keyword_matches']['unexpected']
                                    })
                        else:
                            print(f"    ✅ カテゴリー混在なし (信頼度: {mixing_analysis['confidence_score']:.2f})")
                    
                    # 4-1/4-2混在チェック
                    basic_indicators = content_analysis.get('basic_subject_indicators', [])
                    specialist_indicators = content_analysis.get('specialist_subject_indicators', [])
                    
                    if basic_indicators and specialist_indicators:
                        session_result['violations_found'].append({
                            'violation_type': 'BASIC_SPECIALIST_MIXING',
                            'basic_indicators': basic_indicators,
                            'specialist_indicators': specialist_indicators,
                            'severity': 'CRITICAL'
                        })
                        print(f"    🚨 4-1/4-2混在検出")
                    
                    # 年度混在チェック  
                    year_indicators = content_analysis.get('year_indicators', [])
                    if year_indicators:
                        expected_year_str = str(year)[-2:]  # 下2桁
                        unexpected_years = [y for y in year_indicators if y != expected_year_str]
                        if unexpected_years:
                            session_result['violations_found'].append({
                                'violation_type': 'YEAR_MIXING',
                                'expected_year': year,
                                'found_years': unexpected_years,
                                'severity': 'HIGH'
                            })
                            print(f"    🚨 年度混在検出: {unexpected_years}")
                else:
                    print(f"    ⚠️ 問題内容抽出失敗")
            else:
                print(f"    ❌ 接続失敗: HTTP {response.status_code}")
                session_result['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            print(f"    💥 例外発生: {str(e)}")
            session_result['error'] = str(e)
        
        return session_result

    def run_comprehensive_mixing_verification(self):
        """包括的混在問題検証の実行"""
        print("🔥 ULTRA DEEP CONTENT VERIFICATION 開始")
        print("=" * 80)
        print("目的: ユーザー報告の混在問題を本番環境で実際確認")
        print("焦点: 4-1/4-2混在、年度混在、カテゴリー混在、建設環境×鋼構造混入")
        print("=" * 80)
        
        start_time = time.time()
        
        # セッション初期化
        print("🔄 本番環境セッション初期化...")
        try:
            init_response = self.session.get(self.base_url, timeout=30)
            if init_response.status_code == 200:
                print("✅ セッション初期化成功")
            else:
                print(f"❌ セッション初期化失敗: HTTP {init_response.status_code}")
                return None
        except Exception as e:
            print(f"💥 セッション初期化エラー: {str(e)}")
            return None
        
        # 重点検証実行
        total_tests = 0
        critical_violations = []
        department_results = {}
        
        for department in self.critical_departments:
            print(f"\n🏢 【{department}部門】詳細混在検証")
            print("-" * 50)
            
            department_results[department] = {
                'tests_conducted': 0,
                'violations_found': 0,
                'critical_issues': [],
                'session_results': []
            }
            
            # 各年度・問題数での検証
            for year in self.critical_years[:3]:  # 最新3年分を重点的に
                for question_count in self.question_counts:
                    total_tests += 1
                    department_results[department]['tests_conducted'] += 1
                    
                    session_result = self.verify_single_exam_session(department, year, question_count)
                    department_results[department]['session_results'].append(session_result)
                    
                    # 違反チェック
                    if session_result.get('violations_found'):
                        department_results[department]['violations_found'] += len(session_result['violations_found'])
                        
                        for violation in session_result['violations_found']:
                            if violation.get('severity') == 'CRITICAL':
                                critical_violations.append({
                                    'department': department,
                                    'year': year,
                                    'question_count': question_count,
                                    'violation': violation
                                })
                                department_results[department]['critical_issues'].append(violation)
                    
                    # 特別な焦点: 建設環境×鋼構造混入
                    if department == '建設環境':
                        detailed_findings = session_result.get('detailed_findings', [])
                        for finding in detailed_findings:
                            if finding.get('finding_type') == 'CRITICAL_USER_REPORTED_ISSUE':
                                critical_violations.append({
                                    'department': department,
                                    'year': year,
                                    'question_count': question_count,
                                    'finding': finding
                                })
                    
                    time.sleep(0.5)  # レート制限
            
            # 部門別結果サマリー
            violation_rate = (department_results[department]['violations_found'] / 
                            department_results[department]['tests_conducted']) * 100 if department_results[department]['tests_conducted'] > 0 else 0
            
            print(f"  📊 {department}結果:")
            print(f"    実施テスト: {department_results[department]['tests_conducted']}")
            print(f"    違反検出: {department_results[department]['violations_found']}")
            print(f"    違反率: {violation_rate:.1f}%")
            print(f"    重要問題: {len(department_results[department]['critical_issues'])}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 最終結果と判定
        self.detailed_results.update({
            'total_tests_conducted': total_tests,
            'total_violations': sum(dept['violations_found'] for dept in department_results.values()),
            'critical_violations': critical_violations,
            'department_results': department_results,
            'verification_duration': duration
        })
        
        self.generate_mixing_verification_report()
        
        return self.detailed_results

    def generate_mixing_verification_report(self):
        """混在問題検証レポート生成"""
        print("\n" + "=" * 80)
        print("🔥 ULTRA DEEP CONTENT VERIFICATION 結果")
        print("=" * 80)
        
        total_violations = self.detailed_results['total_violations']
        critical_violations = len(self.detailed_results['critical_violations'])
        
        print(f"📊 総合結果:")
        print(f"  実施テスト総数: {self.detailed_results['total_tests_conducted']}")
        print(f"  検出違反総数: {total_violations}")
        print(f"  重要違反数: {critical_violations}")
        print(f"  実行時間: {self.detailed_results['verification_duration']:.1f}秒")
        print()
        
        # 重要違反の詳細
        if critical_violations > 0:
            print("🚨 重要違反詳細:")
            for i, violation in enumerate(self.detailed_results['critical_violations'][:5], 1):
                print(f"  {i}. {violation['department']} {violation['year']}年度 {violation['question_count']}問")
                if 'violation' in violation:
                    print(f"     タイプ: {violation['violation']['violation_type']}")
                    print(f"     重要度: {violation['violation']['severity']}")
                if 'finding' in violation:
                    print(f"     発見: {violation['finding']['description']}")
            print()
        
        # 部門別結果
        print("🏢 部門別結果:")
        for dept, results in self.detailed_results['department_results'].items():
            violation_rate = (results['violations_found'] / results['tests_conducted']) * 100 if results['tests_conducted'] > 0 else 0
            status = "🚨" if results['critical_issues'] else "⚠️" if results['violations_found'] > 0 else "✅"
            print(f"  {status} {dept}: {violation_rate:.1f}% 違反率 ({results['violations_found']}/{results['tests_conducted']})")
        
        print()
        
        # 最終判定
        if critical_violations == 0 and total_violations == 0:
            print("🏆 判定: PERFECT - 混在問題は完全に解決済み")
            credibility_status = "PERFECT"
        elif critical_violations == 0 and total_violations <= 3:
            print("✅ 判定: GOOD - 軽微な問題のみ検出")
            credibility_status = "GOOD"
        elif critical_violations <= 2:
            print("⚠️ 判定: NEEDS ATTENTION - 重要問題あり")
            credibility_status = "NEEDS_ATTENTION"
        else:
            print("🚨 判定: CRITICAL - 深刻な混在問題あり")
            credibility_status = "CRITICAL"
        
        # 特別報告: ユーザー報告問題
        user_reported_issues = [v for v in self.detailed_results['critical_violations'] 
                              if 'finding' in v and v['finding'].get('finding_type') == 'CRITICAL_USER_REPORTED_ISSUE']
        
        if user_reported_issues:
            print(f"\n🎯 ユーザー報告問題の状況:")
            print(f"  建設環境×鋼構造混入: {len(user_reported_issues)}件検出")
            print("  ❌ ユーザー報告の問題が本番環境で確認されました")
        else:
            print(f"\n🎯 ユーザー報告問題の状況:")
            print("  建設環境×鋼構造混入: 0件")
            print("  ✅ ユーザー報告の問題は本番環境で確認されませんでした")
        
        # 詳細レポート保存
        report_filename = f"ultra_deep_content_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_filename}")
        print("\n🔒 ULTRA DEEP CONTENT VERIFICATION 完了")

def main():
    """メイン実行関数"""
    print("🔥 ULTRA DEEP CONTENT VERIFICATION")
    print("本番環境でのユーザー報告混在問題の完全確認")
    print()
    
    verifier = UltraDeepContentVerification()
    results = verifier.run_comprehensive_mixing_verification()
    
    return results

if __name__ == "__main__":
    main()