#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: 基本動作検証テスト
修正後の道路部門動作確認
"""

import urllib.request
import urllib.parse
import urllib.error
import time
import sys
from datetime import datetime

def log(message, level="INFO"):
    """ログ出力"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def safe_request(url, timeout=30):
    """安全なHTTPリクエスト"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ULTRASYNC-Verifier/1.0')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode('utf-8', errors='ignore')
            return response.getcode(), content
            
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except urllib.error.URLError as e:
        return 0, str(e)
    except Exception as e:
        return -1, str(e)

def test_road_department(base_url):
    """道路部門基本テスト"""
    log("段階1: 道路部門基本動作確認開始")
    
    # テスト1: 道路部門ページアクセス
    url = urllib.parse.urljoin(base_url, "/department_study/道路")
    log(f"アクセスURL: {url}")
    
    status_code, content = safe_request(url)
    log(f"レスポンスステータス: {status_code}")
    
    if status_code != 200:
        log(f"NG 道路部門ページアクセス失敗: {status_code}")
        return False
        
    # ランダム学習ボタンURL確認
    if "/exam?department=道路&type=specialist" in content:
        log("OK ランダム学習ボタンURL正常")
    else:
        log("NG ランダム学習ボタンURL異常")
        return False
        
    # ページコンテンツ確認
    if "道路" in content:
        log("OK 道路部門ページコンテンツ正常")
    else:
        log("NG 道路部門ページコンテンツ異常")
        return False
        
    return True

def test_road_exam(base_url):
    """道路部門試験開始テスト"""
    log("段階1-2: 道路部門試験開始テスト")
    
    # 道路部門試験開始
    exam_base_url = urllib.parse.urljoin(base_url, "/exam")
    params = urllib.parse.urlencode({
        "department": "道路",
        "type": "specialist",
        "questions": "10"
    })
    url = f"{exam_base_url}?{params}"
    
    log(f"試験開始URL: {url}")
    
    status_code, content = safe_request(url)
    log(f"レスポンスステータス: {status_code}")
    
    if status_code != 200:
        log(f"NG 道路部門試験開始失敗: {status_code}")
        return False
        
    # 問題表示確認
    if "問題" in content:
        log("OK 道路部門問題表示正常")
        
        # 問題数確認
        question_count = content.count("問題")
        log(f"問題要素検出数: {question_count}")
        
        return True
    else:
        log("NG 道路部門問題表示異常")
        return False

def test_other_departments(base_url):
    """他部門副作用チェック"""
    log("段階2: 他部門副作用チェック開始")
    
    departments = [
        ("河川・砂防", "specialist"),
        ("基礎科目", "basic")
    ]
    
    results = []
    
    for dept, exam_type in departments:
        log(f"テスト対象部門: {dept}")
        
        # 部門ページアクセス
        if dept == "基礎科目":
            dept_url = urllib.parse.urljoin(base_url, "/department_study/基礎科目")
        else:
            dept_url = urllib.parse.urljoin(base_url, f"/department_study/{dept}")
            
        status_code, content = safe_request(dept_url)
        
        if status_code == 200:
            log(f"OK {dept}ページアクセス正常")
            
            # 試験開始テスト
            exam_base_url = urllib.parse.urljoin(base_url, "/exam")
            exam_params = urllib.parse.urlencode({
                "department": dept,
                "type": exam_type,
                "questions": "5"
            })
            exam_url = f"{exam_base_url}?{exam_params}"
            
            exam_status, exam_content = safe_request(exam_url)
            
            if exam_status == 200:
                log(f"OK {dept}試験開始正常")
                results.append(True)
            else:
                log(f"NG {dept}試験開始異常: {exam_status}")
                results.append(False)
        else:
            log(f"NG {dept}ページアクセス異常: {status_code}")
            results.append(False)
            
        time.sleep(1)  # サーバー負荷軽減
        
    return all(results)

def test_consistency(base_url):
    """一貫性テスト"""
    log("段階3: 一貫性テスト開始")
    
    results = []
    
    for i in range(3):
        log(f"一貫性テスト回数: {i+1}/3")
        
        exam_base_url = urllib.parse.urljoin(base_url, "/exam")
        params = urllib.parse.urlencode({
            "department": "道路",
            "type": "specialist",
            "questions": "5"
        })
        url = f"{exam_base_url}?{params}"
        
        status_code, content = safe_request(url)
        
        if status_code == 200 and "問題" in content:
            log(f"OK 試行{i+1}: 正常")
            results.append(True)
        else:
            log(f"NG 試行{i+1}: 異常 (status: {status_code})")
            results.append(False)
            
        time.sleep(2)
        
    success_rate = sum(results) / len(results)
    log(f"一貫性テスト成功率: {success_rate*100:.1f}%")
    
    return success_rate >= 0.8

def main():
    """メイン実行"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5005"
        
    print("ULTRA SYNC 修正後動作検証開始")
    print(f"対象URL: {base_url}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # 段階1: 道路部門基本テスト
        stage1_success = test_road_department(base_url)
        if not stage1_success:
            log("段階1失敗 - テスト中断", "ERROR")
            return False
            
        stage1_exam_success = test_road_exam(base_url)
        if not stage1_exam_success:
            log("段階1-2失敗 - テスト中断", "ERROR")
            return False
            
        # 段階2: 他部門副作用チェック
        stage2_success = test_other_departments(base_url)
        
        # 段階3: 一貫性チェック
        stage3_success = test_consistency(base_url)
        
        # 結果サマリー
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("ULTRA SYNC 修正後動作検証結果")
        print("="*60)
        print(f"実行時間: {duration:.2f}秒")
        print(f"段階1 (道路部門基本): {'OK' if stage1_success and stage1_exam_success else 'NG'}")
        print(f"段階2 (他部門副作用): {'OK' if stage2_success else 'NG'}")
        print(f"段階3 (一貫性): {'OK' if stage3_success else 'NG'}")
        
        overall_success = stage1_success and stage1_exam_success and stage2_success and stage3_success
        
        if overall_success:
            print("\n総合結果: OK - 修正は正常に動作しています")
            print("修正による期待される動作改善:")
            print("- 道路部門でのカテゴリフィルタリング正常化")
            print("- get_mixed_questions関数での正確な部門マッピング")
            print("- 339問の道路問題からの正常な問題選択")
        else:
            print("\n総合結果: NG - 問題が検出されました")
            print("即座に修正が必要です")
            
        print("="*60)
        
        return overall_success
        
    except Exception as e:
        log(f"予期しないエラー: {str(e)}", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)