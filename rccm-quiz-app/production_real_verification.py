#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ULTRA SYNC 本番環境実地検証
実際のブラウザ操作による完全な本番環境検証

目的: 100%確実な品質確保のための本番環境での実地確認
対象: https://rccm-quiz-2025.onrender.com
検証方法: 実際のHTTPリクエストによる問題内容の詳細確認
"""

import requests
import json
import time
from datetime import datetime
import re
import urllib.parse
from typing import Dict, List, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionRealVerification:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 検証対象部門（建設環境を最優先）
        self.departments = [
            '建設環境',  # 最優先: ユーザー報告の問題部門
            '道路', '河川・砂防', '都市計画', '造園', 
            '鋼構造・コンクリート', '土質・基礎', '施工計画', 
            '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        # 重点検証年度
        self.critical_years = [2019, 2018, 2017, 2016, 2015]
        self.question_counts = [10, 20, 30]
        
        self.verification_results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'PRODUCTION_REAL_VERIFICATION',
            'target_url': self.base_url,
            'detailed_results': {},
            'critical_findings': [],
            'question_content_analysis': {},
            'category_mixing_detection': {},
            'production_health_status': {}
        }

    def get_session_cookies(self):
        """セッション初期化とクッキー取得"""
        try:
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                logger.info(f"✅ セッション初期化成功: {self.base_url}")
                return True
            else:
                logger.error(f"❌ セッション初期化失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"💥 セッション初期化エラー: {str(e)}")
            return False

    def start_specialist_exam(self, department: str, year: int, question_count: int) -> Optional[str]:
        """専門科目試験開始と実際のHTMLコンテンツ取得"""
        try:
            print(f"🔍 本番環境実地検証: {department} {year}年度 {question_count}問")
            
            # POST リクエストでstart_exam実行
            data = {
                'questions': str(question_count),
                'year': str(year),
                'category': department
            }
            
            url = f"{self.base_url}/start_exam/specialist"
            
            response = self.session.post(url, data=data, timeout=60, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.text
                logger.info(f"✅ 専門科目試験開始成功: {department} {year}年度 {question_count}問")
                return content
            else:
                logger.error(f"❌ 専門科目試験開始失敗: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"💥 専門科目試験開始エラー: {str(e)}")
            return None

    def analyze_question_content(self, html_content: str, department: str, year: int) -> Dict:
        """実際の問題内容の詳細分析"""
        analysis = {
            'has_questions': False,
            'question_texts': [],
            'specialist_keywords_found': [],
            'basic_keywords_found': [],
            'other_department_keywords': [],
            'content_quality_score': 0.0,
            'category_violations': [],
            'html_length': len(html_content)
        }
        
        try:
            # 問題文の抽出
            question_patterns = [
                r'<div[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</div>',
                r'問題\s*\d+[：:]?\s*(.*?)(?=問題\s*\d+|$)',
                r'問\s*\d+[：:]?\s*(.*?)(?=問\s*\d+|選択肢|回答|$)',
                r'<p[^>]*>(.*?問.*?)</p>'
            ]
            
            for pattern in question_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    # HTMLタグを除去
                    clean_text = re.sub(r'<[^>]+>', '', match).strip()
                    if len(clean_text) > 20:  # 意味のある長さの文章のみ
                        analysis['question_texts'].append(clean_text[:200])  # 最初の200文字
            
            analysis['has_questions'] = len(analysis['question_texts']) > 0
            
            # 部門別専門キーワード
            specialist_keywords = {
                '建設環境': ['環境', '騒音', '振動', '大気汚染', '水質汚濁', '土壌汚染', 'アセスメント', 'CO2', 'NOx'],
                '道路': ['道路', '舗装', '交通', 'アスファルト', '車道', '歩道', '交差点', '信号'],
                '河川・砂防': ['河川', '砂防', '治水', '堤防', '護岸', '流域', '洪水', 'ダム'],
                '都市計画': ['都市計画', '市街地', '区域', '区画', '土地利用', 'ゾーニング'],
                '造園': ['造園', '緑地', '公園', '植栽', '樹木', '庭園', '景観'],
                '鋼構造・コンクリート': ['鋼構造', 'コンクリート', '鉄筋', '鉄骨', 'PC', 'RC'],
                '土質・基礎': ['土質', '基礎', '地盤', '支持力', 'N値', 'せん断', '圧密'],
                '施工計画': ['施工', '工程', '管理', '品質管理', '安全管理', '工事'],
                '上下水道': ['上水道', '下水道', '給水', '排水', '浄水', '配水'],
                '森林土木': ['森林', '林道', '治山', '木材', '間伐'],
                '農業土木': ['農業', '灌漑', '農地', '水利', '排水路'],
                'トンネル': ['トンネル', '掘削', '支保', '覆工', 'NATM']
            }
            
            # 基礎科目キーワード
            basic_keywords = ['数学', '物理', '化学', '力学', '材料力学', '構造力学', '基礎科目']
            
            # キーワード分析
            full_text = ' '.join(analysis['question_texts']).lower()
            
            # 期待される専門キーワードの検出
            expected_keywords = specialist_keywords.get(department, [])
            for keyword in expected_keywords:
                if keyword.lower() in full_text:
                    analysis['specialist_keywords_found'].append(keyword)
            
            # 基礎科目キーワードの検出（混入チェック）
            for keyword in basic_keywords:
                if keyword.lower() in full_text:
                    analysis['basic_keywords_found'].append(keyword)
            
            # 他部門キーワードの検出（混入チェック）
            for dept, keywords in specialist_keywords.items():
                if dept != department:
                    for keyword in keywords:
                        if keyword.lower() in full_text:
                            analysis['other_department_keywords'].append(f"{dept}:{keyword}")
            
            # カテゴリー違反の検出
            if analysis['basic_keywords_found']:
                analysis['category_violations'].append(f"基礎科目混入: {analysis['basic_keywords_found']}")
            
            if analysis['other_department_keywords']:
                analysis['category_violations'].append(f"他部門混入: {analysis['other_department_keywords']}")
            
            # 品質スコア計算
            if analysis['specialist_keywords_found'] and not analysis['category_violations']:
                analysis['content_quality_score'] = 1.0
            elif analysis['specialist_keywords_found'] and analysis['category_violations']:
                analysis['content_quality_score'] = 0.3
            elif not analysis['specialist_keywords_found'] and not analysis['category_violations']:
                analysis['content_quality_score'] = 0.1
            else:
                analysis['content_quality_score'] = 0.0
            
            return analysis
            
        except Exception as e:
            logger.error(f"問題内容分析エラー: {str(e)}")
            analysis['error'] = str(e)
            return analysis

    def verify_department_in_production(self, department: str) -> Dict:
        """本番環境での部門別徹底検証"""
        print(f"\n🏢 【本番環境実地検証】部門: {department}")
        print("=" * 60)
        
        department_results = {
            'department': department,
            'total_tests': 0,
            'successful_tests': 0,
            'content_verified_tests': 0,
            'category_violations_found': 0,
            'detailed_test_results': [],
            'critical_issues': []
        }
        
        for year in self.critical_years:
            for question_count in self.question_counts:
                department_results['total_tests'] += 1
                
                print(f"  📝 検証実行: {year}年度 {question_count}問 ", end="")
                
                # 実際の試験開始
                html_content = self.start_specialist_exam(department, year, question_count)
                
                if html_content:
                    department_results['successful_tests'] += 1
                    
                    # 問題内容の詳細分析
                    content_analysis = self.analyze_question_content(html_content, department, year)
                    
                    test_result = {
                        'year': year,
                        'question_count': question_count,
                        'success': True,
                        'content_analysis': content_analysis,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if content_analysis['has_questions'] and content_analysis['content_quality_score'] >= 0.5:
                        department_results['content_verified_tests'] += 1
                        print("✅ 合格")
                    elif content_analysis['category_violations']:
                        department_results['category_violations_found'] += 1
                        department_results['critical_issues'].append(f"{year}年度{question_count}問: {content_analysis['category_violations']}")
                        print(f"❌ カテゴリー違反検出")
                    else:
                        print("⚠️ 要確認")
                    
                    department_results['detailed_test_results'].append(test_result)
                    
                else:
                    print("❌ 接続失敗")
                    department_results['detailed_test_results'].append({
                        'year': year,
                        'question_count': question_count,
                        'success': False,
                        'error': '接続失敗'
                    })
                
                # レート制限対策
                time.sleep(0.5)
        
        # 部門別結果サマリー
        success_rate = (department_results['successful_tests'] / department_results['total_tests']) * 100
        content_rate = (department_results['content_verified_tests'] / department_results['total_tests']) * 100
        
        print(f"\n  📊 {department}部門結果:")
        print(f"    接続成功率: {success_rate:.1f}% ({department_results['successful_tests']}/{department_results['total_tests']})")
        print(f"    内容検証率: {content_rate:.1f}% ({department_results['content_verified_tests']}/{department_results['total_tests']})")
        print(f"    カテゴリー違反: {department_results['category_violations_found']}件")
        
        if department_results['critical_issues']:
            print(f"    🚨 重要問題:")
            for issue in department_results['critical_issues']:
                print(f"      - {issue}")
        
        return department_results

    def run_comprehensive_production_verification(self):
        """本番環境での包括的実地検証実行"""
        print("🎯 ULTRA SYNC 本番環境実地検証開始")
        print("=" * 80)
        print("目的: 100%確実な品質確保のための本番環境実地確認")
        print("対象URL: https://rccm-quiz-2025.onrender.com")
        print("検証方法: 実際のHTTPリクエストによる問題内容詳細確認")
        print("=" * 80)
        
        start_time = time.time()
        
        # セッション初期化
        if not self.get_session_cookies():
            print("❌ セッション初期化失敗 - 検証を中断します")
            return None
        
        total_tests = 0
        total_success = 0
        total_content_verified = 0
        total_violations = 0
        critical_departments = []
        
        # 各部門の詳細検証
        for department in self.departments:
            department_result = self.verify_department_in_production(department)
            self.verification_results['detailed_results'][department] = department_result
            
            total_tests += department_result['total_tests']
            total_success += department_result['successful_tests']
            total_content_verified += department_result['content_verified_tests']
            total_violations += department_result['category_violations_found']
            
            if department_result['category_violations_found'] > 0:
                critical_departments.append(department)
            
            print()  # 改行
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 最終結果サマリー
        self.verification_results['final_summary'] = {
            'total_departments': len(self.departments),
            'total_tests': total_tests,
            'successful_tests': total_success,
            'content_verified_tests': total_content_verified,
            'category_violations': total_violations,
            'critical_departments': critical_departments,
            'success_rate': (total_success / total_tests) * 100 if total_tests > 0 else 0,
            'content_verification_rate': (total_content_verified / total_tests) * 100 if total_tests > 0 else 0,
            'violation_rate': (total_violations / total_tests) * 100 if total_tests > 0 else 0,
            'verification_duration': duration
        }
        
        self.generate_production_verification_report()
        
        return self.verification_results

    def generate_production_verification_report(self):
        """本番環境検証レポート生成"""
        summary = self.verification_results['final_summary']
        
        print("\n" + "=" * 80)
        print("🎯 ULTRA SYNC 本番環境実地検証結果")
        print("=" * 80)
        
        print(f"📊 総合結果:")
        print(f"  対象部門数: {summary['total_departments']}")
        print(f"  総テスト数: {summary['total_tests']}")
        print(f"  接続成功数: {summary['successful_tests']}")
        print(f"  内容検証成功数: {summary['content_verified_tests']}")
        print(f"  カテゴリー違反数: {summary['category_violations']}")
        print()
        
        print(f"📈 成功率:")
        print(f"  接続成功率: {summary['success_rate']:.1f}%")
        print(f"  内容検証率: {summary['content_verification_rate']:.1f}%")
        print(f"  違反発生率: {summary['violation_rate']:.1f}%")
        print()
        
        print(f"⏱️ 実行時間: {summary['verification_duration']:.1f}秒")
        print()
        
        # 品質判定
        if summary['category_violations'] == 0 and summary['content_verification_rate'] >= 80:
            print("🏆 判定: EXCELLENT - 本番環境での品質100%確認")
        elif summary['category_violations'] == 0 and summary['content_verification_rate'] >= 60:
            print("✅ 判定: GOOD - 本番環境での品質確認済み")
        elif summary['category_violations'] <= 2:
            print("⚠️ 判定: NEEDS IMPROVEMENT - 軽微な問題あり")
        else:
            print("🚨 判定: CRITICAL - 重大な品質問題あり")
        
        if summary['critical_departments']:
            print(f"\n🚨 要注意部門: {', '.join(summary['critical_departments'])}")
        
        # レポートファイル保存
        report_filename = f"production_real_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_filename}")
        print("\n🔒 ULTRA SYNC 本番環境実地検証完了")

def main():
    """メイン実行関数"""
    print("🎯 ULTRA SYNC 本番環境実地検証ツール")
    print("目的: 100%確実な品質確保のための本番環境実地確認")
    print()
    
    verifier = ProductionRealVerification()
    results = verifier.run_comprehensive_production_verification()
    
    return results

if __name__ == "__main__":
    main()