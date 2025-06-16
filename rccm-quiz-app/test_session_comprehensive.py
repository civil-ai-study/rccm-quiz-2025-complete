#!/usr/bin/env python3
"""
🔥 ULTRA包括的セッション管理テスト（ユーザー要求による）
- ホーム戻り時のセッションクリア
- 新規問題選択時のリセット
- キャッシュクリア機能
- セッション管理の堅牢性
"""

import requests
import re
import time

BASE_URL = "http://localhost:5003"

def test_home_session_clear():
    """ホーム戻り時のセッションクリア テスト"""
    print("🔍 Testing home session clear...")
    
    session = requests.Session()
    
    # Step 1: 専門科目を開始
    print("📚 Starting specialist exam...")
    response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    if response.status_code != 200:
        print(f"❌ Failed to start exam: {response.status_code}")
        return False
    
    qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
    if not qid_match:
        print("❌ Could not find question ID")
        return False
    
    qid = qid_match.group(1)
    print(f"✅ Started specialist exam (ID: {qid})")
    
    # Step 2: 1問回答
    answer_data = {'qid': qid, 'answer': 'A', 'elapsed': '5'}
    submit_response = session.post(f"{BASE_URL}/exam", data=answer_data)
    if submit_response.status_code != 200:
        print(f"❌ Answer submission failed: {submit_response.status_code}")
        return False
    
    print("✅ Answered question 1")
    
    # Step 3: ホームに戻る
    print("🏠 Going back to home...")
    home_response = session.get(f"{BASE_URL}/")
    if home_response.status_code != 200:
        print(f"❌ Home access failed: {home_response.status_code}")
        return False
    
    print("✅ Returned to home")
    
    # Step 4: 基礎科目を開始（セッションがクリアされているかテスト）
    print("📖 Starting basic exam...")
    basic_response = session.get(f"{BASE_URL}/exam?type=basic")
    if basic_response.status_code != 200:
        print(f"❌ Basic exam start failed: {basic_response.status_code}")
        return False
    
    # 新しい問題が表示されているかチェック（修正版）
    # exam.htmlでは "X/Y" 形式で表示される
    counter_match = re.search(r'>(\d+)/(\d+)<', basic_response.text)
    if counter_match:
        current, total = counter_match.groups()
        print(f"✅ Basic exam counter: {current}/{total}")
        if current == "1":
            print("🎉 SESSION CLEAR SUCCESS: Counter starts from 1")
            return True
        else:
            print(f"❌ SESSION CLEAR FAILED: Expected 1, got {current}")
            return False
    else:
        print("❌ Could not find question counter")
        # デバッグ用：レスポンスの一部を表示
        if 'badge bg-primary' in basic_response.text:
            badge_match = re.search(r'badge bg-primary[^>]*>([^<]+)<', basic_response.text)
            if badge_match:
                print(f"Found badge content: {badge_match.group(1)}")
        return False

def test_department_switch_clear():
    """部門切り替え時のセッションクリア テスト"""
    print("\n🔍 Testing department switch session clear...")
    
    session = requests.Session()
    
    # Step 1: 河川砂防を開始
    print("🌊 Starting 河川砂防 exam...")
    response1 = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    if response1.status_code != 200:
        print(f"❌ Failed to start 河川砂防: {response1.status_code}")
        return False
    
    qid1_match = re.search(r'name="qid" value="([^"]+)"', response1.text)
    if qid1_match:
        qid1 = qid1_match.group(1)
        print(f"✅ Started 河川砂防 (ID: {qid1})")
        
        # 1問回答
        answer_data = {'qid': qid1, 'answer': 'A', 'elapsed': '5'}
        session.post(f"{BASE_URL}/exam", data=answer_data)
        print("✅ Answered 河川砂防 question")
    
    # Step 2: 道路部門に切り替え
    print("🛣️ Switching to 道路 department...")
    response2 = session.get(f"{BASE_URL}/exam?department=road&type=specialist")
    if response2.status_code != 200:
        print(f"❌ Failed to switch to road: {response2.status_code}")
        return False
    
    # 新しいセッションが開始されているかチェック（修正版）
    counter_match = re.search(r'>(\d+)/(\d+)<', response2.text)
    if counter_match:
        current, total = counter_match.groups()
        print(f"✅ Road exam counter: {current}/{total}")
        if current == "1":
            print("🎉 DEPARTMENT SWITCH SUCCESS: New session started")
            return True
        else:
            print(f"❌ DEPARTMENT SWITCH FAILED: Expected 1, got {current}")
            return False
    else:
        print("❌ Could not find road exam counter")
        # デバッグ用：レスポンスの一部を表示
        if 'badge bg-primary' in response2.text:
            badge_match = re.search(r'badge bg-primary[^>]*>([^<]+)<', response2.text)
            if badge_match:
                print(f"Found badge content: {badge_match.group(1)}")
        return False

def test_cache_headers():
    """キャッシュヘッダー テスト"""
    print("\n🔍 Testing cache headers...")
    
    session = requests.Session()
    
    # 問題ページにアクセス
    response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    
    # キャッシュ制御ヘッダーをチェック
    cache_control = response.headers.get('Cache-Control', '')
    pragma = response.headers.get('Pragma', '')
    expires = response.headers.get('Expires', '')
    
    print(f"Cache-Control: {cache_control}")
    print(f"Pragma: {pragma}")
    print(f"Expires: {expires}")
    
    # 必要なヘッダーが含まれているかチェック
    required_cache_directives = ['no-store', 'no-cache', 'must-revalidate']
    has_all_directives = all(directive in cache_control for directive in required_cache_directives)
    
    if has_all_directives and pragma == 'no-cache':
        print("🎉 CACHE HEADERS SUCCESS: All cache control headers present")
        return True
    else:
        print("❌ CACHE HEADERS FAILED: Missing required headers")
        return False

def test_session_reset_scenarios():
    """複数のセッションリセットシナリオ テスト"""
    print("\n🔍 Testing multiple session reset scenarios...")
    
    session = requests.Session()
    
    scenarios = [
        ("basic → specialist", f"{BASE_URL}/exam?type=basic", f"{BASE_URL}/exam?department=road&type=specialist"),
        ("specialist → basic", f"{BASE_URL}/exam?department=civil_planning&type=specialist", f"{BASE_URL}/exam?type=basic"),
        ("civil_planning → road", f"{BASE_URL}/exam?department=civil_planning&type=specialist", f"{BASE_URL}/exam?department=road&type=specialist"),
    ]
    
    for scenario_name, url1, url2 in scenarios:
        print(f"  Testing: {scenario_name}")
        
        # First exam
        response1 = session.get(url1)
        if response1.status_code == 200:
            counter1_match = re.search(r'>(\d+)/(\d+)<', response1.text)
            if counter1_match:
                current1, total1 = counter1_match.groups()
                print(f"    First exam: {current1}/{total1}")
        
        # Switch to second exam
        response2 = session.get(url2)
        if response2.status_code == 200:
            counter2_match = re.search(r'>(\d+)/(\d+)<', response2.text)
            if counter2_match:
                current2, total2 = counter2_match.groups()
                print(f"    Second exam: {current2}/{total2}")
                
                if current2 == "1":
                    print(f"    ✅ {scenario_name}: Session reset successful")
                else:
                    print(f"    ❌ {scenario_name}: Session reset failed")
                    return False
            else:
                print(f"    ❌ {scenario_name}: Could not parse counter")
                # デバッグ用
                if 'badge bg-primary' in response2.text:
                    badge_match = re.search(r'badge bg-primary[^>]*>([^<]+)<', response2.text)
                    if badge_match:
                        print(f"    Found badge: {badge_match.group(1)}")
                return False
        else:
            print(f"    ❌ {scenario_name}: Second exam failed")
            return False
    
    print("🎉 ALL SESSION RESET SCENARIOS SUCCESS")
    return True

def main():
    print("=" * 80)
    print("🔥 ULTRA包括的セッション管理テスト（ユーザー要求による）")
    print("=" * 80)
    
    # テスト実行前に少し待機
    time.sleep(2)
    
    tests = [
        ("ホーム戻り時セッションクリア", test_home_session_clear),
        ("部門切り替えセッションクリア", test_department_switch_clear),
        ("キャッシュヘッダー", test_cache_headers),
        ("複数セッションリセット", test_session_reset_scenarios),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} テスト開始...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("📊 テスト結果サマリー")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 総合結果: {passed}件成功, {failed}件失敗")
    
    if failed == 0:
        print("🎉 🎉 🎉 ALL TESTS PASSED - セッション管理完全修正成功！ 🎉 🎉 🎉")
        print("✅ ホーム戻り時の古い情報クリア")
        print("✅ 部門切り替え時のセッションリセット")
        print("✅ 超強力キャッシュクリア")
        print("✅ 包括的セッション管理")
        return True
    else:
        print("🚨 一部テストが失敗しました。修正が必要です。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)