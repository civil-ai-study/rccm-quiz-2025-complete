#!/usr/bin/env python3
"""
🚨 ULTRASYNC緊急診断：基礎科目試験開始におけるセッション初期化問題の根本原因分析
"""

import sys
import os
import json
import time
import logging
from datetime import datetime

# Flaskアプリケーションのパスを追加
sys.path.insert(0, '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app')

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultrasync_critical_session_diagnosis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def diagnose_session_initialization():
    """セッション初期化問題の診断"""
    logger.info("🚨 ULTRASYNC緊急診断開始：基礎科目試験セッション初期化")
    
    diagnosis_results = {
        'timestamp': datetime.now().isoformat(),
        'test_name': 'ultrasync_critical_session_diagnosis',
        'issue_description': '基礎科目試験開始後、exam_simulatorページが正常に表示されるが、実際の試験フォームが空でCSRFトークンも存在しない',
        'critical_findings': [],
        'recommendations': []
    }
    
    try:
        # 1. app.pyからstart_exam関数の処理フローを分析
        logger.info("1. start_exam関数の処理フロー分析")
        
        # app.pyを読み込んでstart_exam関数を分析
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # start_exam関数の基礎科目処理部分を抽出
        start_exam_lines = []
        in_start_exam = False
        for line in app_content.split('\n'):
            if 'def start_exam(' in line:
                in_start_exam = True
            elif in_start_exam and line.startswith('def ') and 'start_exam' not in line:
                break
            elif in_start_exam:
                start_exam_lines.append(line)
        
        # 基礎科目に関連する重要な処理を特定
        critical_basic_lines = [line for line in start_exam_lines if '基礎科目' in line or 'basic' in line]
        
        diagnosis_results['critical_findings'].append({
            'finding': 'start_exam関数内の基礎科目処理',
            'details': f"基礎科目関連処理行数: {len(critical_basic_lines)}",
            'sample_lines': critical_basic_lines[:10]  # 最初の10行のみ
        })
        
        # 2. exam_simulator関数の分析
        logger.info("2. exam_simulator関数の分析")
        
        exam_simulator_lines = []
        in_exam_simulator = False
        for line in app_content.split('\n'):
            if 'def exam_simulator_page(' in line:
                in_exam_simulator = True
            elif in_exam_simulator and line.startswith('def ') and 'exam_simulator' not in line:
                break
            elif in_exam_simulator:
                exam_simulator_lines.append(line)
        
        diagnosis_results['critical_findings'].append({
            'finding': 'exam_simulator_page関数の実装',
            'details': f"exam_simulator_page関数行数: {len(exam_simulator_lines)}",
            'content': exam_simulator_lines
        })
        
        # 3. exam_question関数の分析
        logger.info("3. exam_question関数の分析")
        
        exam_question_lines = []
        in_exam_question = False
        for line in app_content.split('\n'):
            if 'def exam_question(' in line:
                in_exam_question = True
            elif in_exam_question and line.startswith('def ') and 'exam_question' not in line:
                break
            elif in_exam_question:
                exam_question_lines.append(line)
        
        diagnosis_results['critical_findings'].append({
            'finding': 'exam_question関数の実装',
            'details': f"exam_question関数行数: {len(exam_question_lines)}",
            'first_20_lines': exam_question_lines[:20]  # 最初の20行のみ
        })
        
        # 4. セッション管理関連の問題を特定
        logger.info("4. セッション管理問題の特定")
        
        # exam_sessionの設定と使用を追跡
        exam_session_lines = [line for line in app_content.split('\n') if 'exam_session' in line]
        
        # 重要なセッション設定箇所
        session_creation_lines = [line for line in exam_session_lines if 'exam_session = {' in line or 'session[\'exam_session\']' in line]
        
        diagnosis_results['critical_findings'].append({
            'finding': 'セッション管理の問題',
            'details': f"exam_session関連行数: {len(exam_session_lines)}",
            'session_creation_lines': session_creation_lines[:5]  # 最初の5行のみ
        })
        
        # 5. テンプレート分析
        logger.info("5. テンプレート分析")
        
        # exam_simulator.htmlテンプレートの存在確認
        templates_dir = 'templates'
        if os.path.exists(os.path.join(templates_dir, 'exam_simulator.html')):
            with open(os.path.join(templates_dir, 'exam_simulator.html'), 'r', encoding='utf-8') as f:
                exam_simulator_template = f.read()
            
            # フォーム要素の有無を確認
            has_form = '<form' in exam_simulator_template
            has_csrf = 'csrf' in exam_simulator_template.lower()
            
            diagnosis_results['critical_findings'].append({
                'finding': 'exam_simulator.htmlテンプレート分析',
                'details': {
                    'template_exists': True,
                    'has_form_elements': has_form,
                    'has_csrf_token': has_csrf,
                    'template_size': len(exam_simulator_template)
                }
            })
        else:
            diagnosis_results['critical_findings'].append({
                'finding': 'exam_simulator.htmlテンプレート分析',
                'details': {
                    'template_exists': False,
                    'error': 'テンプレートファイルが見つかりません'
                }
            })
        
        # 6. 問題の根本原因分析
        logger.info("6. 根本原因分析")
        
        # start_exam関数でのリダイレクト処理を確認
        redirect_lines = [line for line in start_exam_lines if 'redirect' in line]
        
        diagnosis_results['critical_findings'].append({
            'finding': '根本原因分析',
            'details': {
                'redirect_count': len(redirect_lines),
                'redirect_lines': redirect_lines,
                'probable_issue': 'start_exam関数が正常に実行されているが、リダイレクト先での処理に問題がある可能性'
            }
        })
        
        # 7. 推奨修正案
        logger.info("7. 推奨修正案の生成")
        
        diagnosis_results['recommendations'] = [
            {
                'priority': 'HIGH',
                'issue': 'セッション初期化問題',
                'solution': 'start_exam関数内でのexam_session作成直後にセッション状態を確認し、正常に保存されているかを検証する'
            },
            {
                'priority': 'HIGH',
                'issue': 'exam_simulator_page関数の問題',
                'solution': 'exam_simulator_page関数がセッション状態を正しく読み取れているかを確認し、必要に応じて修正する'
            },
            {
                'priority': 'MEDIUM',
                'issue': 'テンプレート側の問題',
                'solution': 'exam_simulator.htmlテンプレートが正しくセッション情報を受け取り、フォーム要素を生成しているかを確認する'
            },
            {
                'priority': 'MEDIUM',
                'issue': 'CSRFトークンの問題',
                'solution': 'CSRFトークンが正しく生成・配置されているかを確認し、必要に応じて修正する'
            }
        ]
        
        # 8. 緊急対応案
        diagnosis_results['emergency_actions'] = [
            '1. start_exam関数内でのセッション保存処理を強化する',
            '2. exam_simulator_page関数でのセッション読み取り処理を修正する',
            '3. exam_question関数へのリダイレクトを直接的に修正する',
            '4. セッション状態のデバッグ情報を追加する'
        ]
        
        logger.info("✅ ULTRASYNC緊急診断完了")
        
    except Exception as e:
        diagnosis_results['critical_findings'].append({
            'finding': '診断エラー',
            'details': f"診断実行中にエラーが発生: {str(e)}",
            'error_type': type(e).__name__
        })
        logger.error(f"診断エラー: {e}")
    
    return diagnosis_results

def main():
    """メイン実行関数"""
    logger.info("🚨 ULTRASYNC緊急診断開始")
    
    try:
        # 診断実行
        results = diagnose_session_initialization()
        
        # 結果保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f'ultrasync_critical_session_diagnosis_{timestamp}.json'
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 診断結果を {result_file} に保存しました")
        
        # 重要な発見事項をログに出力
        logger.info("🔍 重要な発見事項:")
        for finding in results['critical_findings']:
            logger.info(f"- {finding['finding']}: {finding['details']}")
        
        # 推奨修正案をログに出力
        logger.info("💡 推奨修正案:")
        for recommendation in results['recommendations']:
            logger.info(f"- [{recommendation['priority']}] {recommendation['issue']}: {recommendation['solution']}")
        
        return results
        
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        return None

if __name__ == "__main__":
    results = main()
    if results:
        print("🚨 ULTRASYNC緊急診断が完了しました")
        print(f"📊 重要な発見事項: {len(results['critical_findings'])}件")
        print(f"💡 推奨修正案: {len(results['recommendations'])}件")
    else:
        print("❌ 診断が失敗しました")