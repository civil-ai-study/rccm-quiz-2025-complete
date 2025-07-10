#!/usr/bin/env python3
# 🛡️ ULTRASYNC ID不一致問題の詳細分析

import requests
import json
from datetime import datetime
import re

def analyze_id_mismatch():
    """セッションの問題IDと実際の問題データの不一致を調査"""
    
    print('🛡️ ULTRASYNC ID不一致問題分析開始')
    print('=' * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    try:
        # ステップ1: 基礎科目試験開始でセッション作成
        print('ステップ1: 基礎科目試験開始でセッション作成')
        start_url = f'{base_url}/start_exam/基礎科目'
        data = {'questions': '10', 'year': '2024'}
        response = session.post(start_url, data=data, allow_redirects=False, timeout=15)
        print(f'  start_exam応答: {response.status_code}')
        
        # ステップ2: セッションの問題ID取得
        print('ステップ2: セッションの問題ID取得')
        debug_response = session.get(f'{base_url}/debug/session', timeout=15)
        if debug_response.status_code == 200:
            session_data = debug_response.json()
            exam_question_ids = session_data.get('exam_question_ids', [])
            print(f'  セッションの問題ID数: {len(exam_question_ids)}')
            print(f'  セッションの問題ID例: {exam_question_ids[:5]}')
            
            # ID形式の分析
            if exam_question_ids:
                first_id = exam_question_ids[0]
                print(f'  最初の問題ID: {first_id}')
                
                # ID形式の判定
                if isinstance(first_id, int) and first_id > 1000000:
                    print('  ✅ ID形式: 変換後の形式（1000000番台）')
                    id_format = 'converted'
                elif isinstance(first_id, int) and first_id < 1000:
                    print('  ✅ ID形式: 元の形式（1-999）')
                    id_format = 'original'
                else:
                    print(f'  ⚠️ ID形式: 不明な形式 ({type(first_id)}: {first_id})')
                    id_format = 'unknown'
            else:
                print('  ❌ 問題IDが空')
                id_format = 'empty'
        else:
            print(f'  ❌ セッションデバッグ取得失敗: {debug_response.status_code}')
            return
        
        # ステップ3: 実際の問題データの形式確認
        print('ステップ3: 実際の問題データの形式確認')
        
        # 可能な限り問題データの情報を取得
        debug_info_response = session.get(f'{base_url}/debug/session_info', timeout=15)
        if debug_info_response.status_code == 200:
            debug_info_data = debug_info_response.json()
            debug_info = debug_info_data.get('debug_info', {})
            
            questions_count = debug_info.get('questions_count', 0)
            data_source = debug_info.get('data_source', '')
            
            print(f'  問題データ数: {questions_count}')
            print(f'  データソース: {data_source}')
            
            if questions_count > 0:
                print('  ✅ 問題データは存在する')
            else:
                print('  ❌ 問題データが存在しない')
        
        # ステップ4: 問題データとセッションIDの照合テスト
        print('ステップ4: 問題データとセッションIDの照合テスト')
        
        if exam_question_ids and id_format == 'converted':
            # 変換後IDから元IDを推測
            original_ids = []
            for converted_id in exam_question_ids[:3]:  # 最初の3つをテスト
                if converted_id >= 1000000:
                    original_id = converted_id - 1000000
                    original_ids.append(original_id)
                    print(f'  変換ID {converted_id} → 元ID推測 {original_id}')
            
            print(f'  推測された元ID: {original_ids}')
            
            # この情報をもとに問題を特定
            if original_ids:
                print('  ✅ ID変換の可能性が高い')
                print('  推奨修正: /examルートで問題取得時にID変換を考慮')
            else:
                print('  ❌ ID変換パターンが不明')
        
        # ステップ5: エラーの具体的な原因を推測
        print('ステップ5: エラーの具体的な原因を推測')
        
        # /examルートに再度アクセスしてエラーの詳細を取得
        exam_response = session.get(f'{base_url}/exam', timeout=15)
        if exam_response.status_code == 200:
            content = exam_response.text
            
            # エラーメッセージの詳細抽出
            error_patterns = [
                r'問題データが存在しません',
                r'問題が見つかりません',
                r'セッションが無効です',
                r'データベースエラー',
                r'読み込みエラー',
                r'IDが見つかりません'
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f'  ❌ 検出されたエラー: {pattern}')
            
            # JavaScriptエラーの確認
            if 'error' in content.lower():
                js_error_match = re.search(r'console\.error\(["\']([^"\']+)["\']', content)
                if js_error_match:
                    print(f'  JavaScriptエラー: {js_error_match.group(1)}')
        
        # ステップ6: 修正案の提示
        print('ステップ6: 修正案の提示')
        
        if id_format == 'converted' and questions_count > 0:
            print('  修正案1: /examルートでID変換を考慮した問題取得')
            print('  修正案2: セッション作成時のID形式統一')
            print('  修正案3: load_basic_questions_only関数の戻り値形式確認')
            
        print('\\n' + '=' * 60)
        print('🛡️ ULTRASYNC ID不一致問題分析完了')
        
        # 結果をまとめて返す
        analysis_result = {
            'session_id_format': id_format,
            'session_id_count': len(exam_question_ids),
            'session_id_examples': exam_question_ids[:3] if exam_question_ids else [],
            'data_source': data_source if 'data_source' in locals() else 'unknown',
            'questions_count': questions_count if 'questions_count' in locals() else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('ultrasync_id_mismatch_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f'分析結果保存: ultrasync_id_mismatch_analysis.json')
        
        return analysis_result
        
    except Exception as e:
        print(f'分析中にエラー: {e}')
        return None

if __name__ == '__main__':
    results = analyze_id_mismatch()
    if results:
        print(f'\\n📊 分析結果サマリー:')
        print(f'セッションID形式: {results["session_id_format"]}')
        print(f'セッションID数: {results["session_id_count"]}')
        print(f'問題データ数: {results["questions_count"]}')
        print(f'データソース: {results["data_source"]}')