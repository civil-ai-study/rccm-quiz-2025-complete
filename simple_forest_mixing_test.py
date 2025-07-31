#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
森林土木部門簡易混在テスト (ASCII専用・cp932エラー完全回避)
==================================================
最小限のコードで確実に上水道問題混在を検出
ユニコード文字を一切使用せず、ASCII文字のみで結果表示
"""

import sys
import os
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(message):
    """ASCII安全な出力（cp932エラー完全回避）"""
    try:
        # 日本語文字を英語に置換
        replacements = {
            '森林土木': 'Forest-Civil',
            '上水道': 'Water-Supply',
            '問題': 'Question',
            '検出': 'Detected',
            '混在': 'Mixed',
            'エラー': 'Error',
            '成功': 'Success',
            '確認': 'Confirmed'
        }
        
        safe_msg = message
        for jp, en in replacements.items():
            safe_msg = safe_msg.replace(jp, en)
        
        # ASCII文字のみに変換
        ascii_msg = safe_msg.encode('ascii', 'replace').decode('ascii')
        print(ascii_msg)
        
    except Exception:
        # 最終フォールバック
        print("Output error - using fallback")

def simple_mixing_test():
    """簡易混在テスト実行"""
    safe_print("=== Simple Forest Mixing Test ===")
    safe_print("Testing for water supply questions in forest department")
    
    results = {
        'test_time': datetime.now().isoformat(),
        'questions_tested': 0,
        'water_mixing_found': 0,
        'forest_content_found': 0,
        'mixing_details': [],
        'status': 'unknown'
    }
    
    try:
        safe_print("Loading application functions...")
        
        # アプリケーション関数をインポート
        from app import get_department_questions_ultrasync
        safe_print("[OK] Application functions loaded")
        
        # 森林土木部門から20問取得
        safe_print("Retrieving 20 questions from Forest-Civil department...")
        questions = get_department_questions_ultrasync('森林土木', 20)
        
        if not questions:
            safe_print("[ERROR] No questions retrieved")
            results['status'] = 'no_questions'
            return False
        
        results['questions_tested'] = len(questions)
        safe_print(f"[OK] Retrieved {len(questions)} questions")
        
        # キーワードリスト（必要最小限）
        water_words = ['上水道', '工業用水道', '浄水', '配水', '給水', '水処理']
        forest_words = ['森林', '林道', '治山', '森林土木']
        
        # 各問題をチェック
        safe_print("Analyzing questions...")
        
        water_count = 0
        forest_count = 0
        
        for i, q in enumerate(questions):
            question_text = q.get('question', '')
            category = q.get('category', '')
            full_text = f"{category} {question_text}"
            
            # 上水道キーワード検索
            water_found = []
            for word in water_words:
                if word in full_text:
                    water_found.append(word)
            
            # 森林キーワード検索
            forest_found = []
            for word in forest_words:
                if word in full_text:
                    forest_found.append(word)
            
            # 結果記録
            if water_found:
                water_count += 1
                mixing_info = {
                    'question_num': i + 1,
                    'category': category,
                    'water_keywords': water_found,
                    'preview': question_text[:100]
                }
                results['mixing_details'].append(mixing_info)
                safe_print(f"[MIXING] Q{i+1}: Water keywords found - {', '.join(water_found)}")
            
            if forest_found:
                forest_count += 1
                safe_print(f"[FOREST] Q{i+1}: Forest content confirmed")
        
        results['water_mixing_found'] = water_count
        results['forest_content_found'] = forest_count
        
        # 結果判定
        safe_print("")
        safe_print("=== Test Results ===")
        safe_print(f"Questions tested: {len(questions)}")
        safe_print(f"Water mixing detected: {water_count}")
        safe_print(f"Forest content found: {forest_count}")
        
        if water_count > 0:
            safe_print("")
            safe_print("[CRITICAL] Water supply mixing detected!")
            safe_print(f"Found {water_count} water supply questions in forest department")
            
            for mixing in results['mixing_details']:
                safe_print(f"  Q{mixing['question_num']}: {', '.join(mixing['water_keywords'])}")
            
            results['status'] = 'mixing_detected'
            return False
        
        else:
            safe_print("")
            safe_print("[SUCCESS] No water supply mixing detected")
            safe_print(f"Forest content purity: {forest_count}/{len(questions)} questions")
            results['status'] = 'no_mixing'
            return True
    
    except Exception as e:
        safe_print(f"[ERROR] Test failed: {str(e)}")
        results['status'] = 'test_error'
        results['error'] = str(e)
        return False
    
    finally:
        # 結果保存（ASCII安全）
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"simple_forest_test_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            safe_print(f"Results saved to: {filename}")
        
        except Exception as e:
            safe_print(f"Save error: {str(e)}")

def main():
    """メイン実行"""
    safe_print("Simple Forest Civil Engineering Mixing Test")
    safe_print("CP932 Error Prevention - ASCII Only Output")
    safe_print("=" * 50)
    
    success = simple_mixing_test()
    
    safe_print("")
    safe_print("=" * 50)
    if success:
        safe_print("[FINAL] No mixing detected - Forest department is clean")
    else:
        safe_print("[FINAL] Mixing detected or test error - Investigation needed")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())