#!/usr/bin/env python3
"""
ULTRA SYNC 精密混在チェック
実際の問題データ内容のみを分析（テンプレート除外）
"""

import requests
import json
import re
from bs4 import BeautifulSoup

def extract_question_data_only(html_content):
    """問題データ部分のみを抽出（テンプレート除外）"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 問題文を含む主要コンテンツ部分のみ抽出
        main_content = soup.find('div', class_='container')
        if not main_content:
            main_content = soup
        
        # フッター、ナビ、メタデータを除外
        for element in main_content.find_all(['footer', 'nav', 'meta', 'script', 'style']):
            element.decompose()
        
        # コピーライト文言を除外
        text_content = main_content.get_text()
        text_content = re.sub(r'©.*?2025', '', text_content)
        text_content = re.sub(r'RCCM試験問題集.*?2025', '', text_content)
        
        return text_content
        
    except Exception as e:
        return f"抽出エラー: {e}"

def test_precise_mixing(department, year):
    """精密混在テスト"""
    print(f"\n=== {department}部門{year}年 精密混在チェック ===")
    
    try:
        session = requests.Session()
        
        # セッション開始
        url = f"https://rccm-quiz-2025.onrender.com/start_exam/{department}"
        data = {"questions": 3, "year": str(year)}
        
        response = session.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            # /examページを取得
            exam_response = session.get("https://rccm-quiz-2025.onrender.com/exam", timeout=30)
            
            if exam_response.status_code == 200:
                # 問題データ部分のみを抽出
                question_content = extract_question_data_only(exam_response.text)
                
                print(f"問題内容抽出成功")
                
                # 年度情報の精密検索
                year_matches = re.findall(r'(20\d{2})年?', question_content)
                year_matches = [y for y in year_matches if y != '2025']  # テンプレート由来を除外
                
                unique_years = list(set(year_matches))
                
                # 混在判定
                if unique_years:
                    expected_year = str(year)
                    contamination = [y for y in unique_years if y != expected_year]
                    
                    if contamination:
                        print(f"ERROR 年度混在検出: 期待={expected_year}年, 検出={unique_years}")
                        print(f"混在年度: {contamination}")
                        return {'status': 'CONTAMINATED', 'contamination': contamination}
                    else:
                        print(f"OK 年度一致: {expected_year}年のみ検出")
                        return {'status': 'PURE', 'years': unique_years}
                else:
                    print(f"INFO 年度情報なし: 問題内容に年度記載なし")
                    return {'status': 'NO_YEAR_INFO', 'content_length': len(question_content)}
            else:
                print(f"ERROR 問題ページ取得失敗: HTTP {exam_response.status_code}")
                return {'status': 'FAILED', 'error': f'HTTP {exam_response.status_code}'}
        else:
            print(f"ERROR セッション開始失敗: HTTP {response.status_code}")
            return {'status': 'FAILED', 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"ERROR テストエラー: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def main():
    print("ULTRA SYNC 精密混在チェック開始")
    print("テンプレート由来の2025年表示を除外した実問題データのみを分析")
    print("=" * 60)
    
    # テスト対象
    test_cases = [
        ('道路', 2015),
        ('河川・砂防', 2018), 
        ('都市計画', 2019)
    ]
    
    results = []
    pure_count = 0
    contaminated_count = 0
    
    for department, year in test_cases:
        result = test_precise_mixing(department, year)
        result['department'] = department
        result['year'] = year
        results.append(result)
        
        if result['status'] == 'PURE':
            pure_count += 1
        elif result['status'] == 'CONTAMINATED':
            contaminated_count += 1
    
    # 最終判定
    print(f"\n" + "=" * 60)
    print(f"精密混在チェック結果")
    print(f"純度確認: {pure_count}/{len(test_cases)}")
    print(f"混在検出: {contaminated_count}/{len(test_cases)}")
    
    if contaminated_count == 0:
        print(f"\nEXCELLENT: 実問題データでは混在なし - テンプレート表示による誤検出でした")
        final_status = "NO_REAL_CONTAMINATION"
    else:
        print(f"\nERROR: 実問題データに真の混在あり - 修正が必要")
        final_status = "REAL_CONTAMINATION_FOUND"
    
    # 結果保存
    with open("precise_mixing_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "final_status": final_status,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    return final_status

if __name__ == "__main__":
    main()