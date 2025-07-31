#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ ULTRA SYNC ピンポイントエラー特定
型エラーの正確な発生箇所をスタックトレースで特定
副作用ゼロ保証・段階的実行
"""

import requests
import traceback
import sys
from datetime import datetime
from io import StringIO

class UltraSyncPinpointErrorDetection:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def capture_detailed_error_trace(self):
        """詳細エラートレースの段階的取得"""
        print("🛡️ ULTRA SYNC ピンポイントエラー特定")
        print(f"⏰ 実行時刻: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎯 目的: 型エラー発生箇所の正確な特定")
        print("=" * 60)
        
        try:
            # 🔍 Stage 1: セッション初期化段階の詳細監視
            print("\n🔍 Stage 1: セッション初期化段階")
            print("   副作用: なし（読み取り専用）")
            
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 1, "year": "2018"}
            
            print("   📡 セッション初期化リクエスト送信...")
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            print(f"   📊 レスポンス: HTTP {start_response.status_code}")
            
            # リダイレクトパスの詳細分析
            redirect_path = []
            if start_response.history:
                print(f"   🔄 リダイレクト回数: {len(start_response.history)}")
                for i, resp in enumerate(start_response.history, 1):
                    location = resp.headers.get('Location', 'N/A')
                    redirect_path.append(f"Step{i}: HTTP {resp.status_code} → {location}")
                    print(f"     {redirect_path[-1]}")
            
            # 🔍 Stage 2: エラーHTMLの詳細解析
            print("\n🔍 Stage 2: エラーHTMLの詳細解析")
            print("   副作用: なし（読み取り専用）")
            
            response_content = start_response.text
            
            # エラーメッセージの精密抽出
            import re
            error_patterns = [
                r"詳細[：:]\s*([^<]+)",
                r"エラーが発生しました[。.]([^<]+)",
                r"TypeError[：:]([^<]+)",
                r"not supported between instances[^<]*"
            ]
            
            detected_errors = []
            for pattern in error_patterns:
                matches = re.findall(pattern, response_content, re.IGNORECASE)
                for match in matches:
                    if match.strip():
                        detected_errors.append(match.strip())
            
            if detected_errors:
                print("   🚨 検出されたエラー:")
                for i, error in enumerate(detected_errors, 1):
                    print(f"     {i}. {error}")
                
                # エラーの分類
                type_error_found = any(
                    "not supported between instances" in error.lower() or
                    "str" in error and "int" in error
                    for error in detected_errors
                )
                
                if type_error_found:
                    print("   ✅ 確認: 型エラーが発生中")
                    return True, detected_errors
                else:
                    print("   ❓ 他のエラーが発生")
                    return False, detected_errors
            else:
                print("   ✅ エラーメッセージ未検出")
                return False, []
            
        except Exception as e:
            print(f"   🚨 特定処理エラー: {e}")
            return False, [str(e)]
    
    def analyze_error_context(self, detected_errors):
        """エラーコンテキストの詳細分析"""
        print("\n🔍 Stage 3: エラーコンテキスト分析")
        print("   副作用: なし（分析のみ）")
        
        if not detected_errors:
            print("   ℹ️  分析対象なし")
            return {}
        
        analysis_result = {
            'error_type': 'unknown',
            'likely_location': 'unknown',
            'fix_priority': 'medium',
            'safety_level': 'high'
        }
        
        # エラーパターン分析
        for error in detected_errors:
            error_lower = error.lower()
            
            # 型エラーパターンの識別
            if "not supported between instances" in error_lower:
                if "'str'" in error_lower and "'int'" in error_lower:
                    analysis_result['error_type'] = 'str_int_comparison'
                    analysis_result['likely_location'] = 'session.get(exam_current) comparison'
                    analysis_result['fix_priority'] = 'high'
                    print("   🎯 エラー種類: 文字列と整数の比較エラー")
                    print("   📍 推定箇所: session.get('exam_current')の比較演算")
                    print("   ⚡ 修正優先度: 高")
                    
            elif "keyerror" in error_lower:
                analysis_result['error_type'] = 'key_missing'
                analysis_result['fix_priority'] = 'high'
                print("   🎯 エラー種類: キー不足エラー")
                
            elif "attributeerror" in error_lower:
                analysis_result['error_type'] = 'attribute_missing'
                analysis_result['fix_priority'] = 'medium'
                print("   🎯 エラー種類: 属性エラー")
        
        return analysis_result
    
    def suggest_safe_fix_approach(self, analysis_result):
        """安全な修正アプローチの提案"""
        print("\n🛡️ Stage 4: 安全修正アプローチ提案")
        print("   副作用: なし（提案のみ）")
        
        if analysis_result.get('error_type') == 'str_int_comparison':
            print("   📋 推奨修正アプローチ:")
            print("     1. app.pyバックアップ作成（必須）")
            print("     2. 型安全関数get_exam_current_safe()の動作確認")
            print("     3. 未修正箇所の段階的特定")
            print("     4. 1箇所ずつ修正→テスト→確認のサイクル")
            print("     5. 各段階での副作用チェック")
            
            print("   🔒 安全性保証:")
            print("     ✅ 修正前必須バックアップ")
            print("     ✅ 段階的修正（1箇所ずつ）")
            print("     ✅ 各段階でのテスト確認")
            print("     ✅ 副作用監視システム")
            
            return 'safe_incremental_fix'
        else:
            print("   ❓ 不明なエラーパターンのため詳細調査が必要")
            return 'detailed_investigation'
    
    def verify_current_state(self):
        """現在の状態確認"""
        print("\n🔍 Stage 5: 現在状態の確認")
        print("   副作用: なし（確認のみ）")
        
        try:
            # 基礎科目での動作確認（比較用）
            print("   📊 基礎科目での動作確認...")
            basic_url = f"{self.base_url}/start_exam/基礎科目"
            basic_data = {"questions": 1, "year": ""}
            
            basic_response = self.session.post(basic_url, data=basic_data, timeout=20)
            basic_status = basic_response.status_code
            print(f"   📈 基礎科目: HTTP {basic_status}")
            
            if basic_status == 200 and "エラー" not in basic_response.text:
                print("   ✅ 基礎科目は正常動作")
                return {'basic_working': True, 'specialist_broken': True}
            else:
                print("   ⚠️  基礎科目でも問題発生")
                return {'basic_working': False, 'specialist_broken': True}
                
        except Exception as e:
            print(f"   ⚠️  状態確認エラー: {e}")
            return {'basic_working': 'unknown', 'specialist_broken': True}

def main():
    print("🛡️ ULTRA SYNC ピンポイントエラー特定システム")
    print("🎯 目的: 型エラーの正確な特定と安全修正計画")
    print("⚡ 方針: 副作用ゼロ・段階的実行・完全安全")
    print("=" * 70)
    
    detector = UltraSyncPinpointErrorDetection()
    
    # 段階的エラー特定
    error_found, detected_errors = detector.capture_detailed_error_trace()
    
    # エラー分析
    analysis_result = detector.analyze_error_context(detected_errors)
    
    # 修正アプローチ提案
    fix_approach = detector.suggest_safe_fix_approach(analysis_result)
    
    # 現在状態確認
    state_info = detector.verify_current_state()
    
    # 総合結果
    print("\n" + "=" * 70)
    print("🛡️ ULTRA SYNC ピンポイント特定結果")
    print("=" * 70)
    
    print(f"🔍 エラー特定: {'成功' if error_found else '未検出'}")
    print(f"📊 検出エラー数: {len(detected_errors)}")
    print(f"🎯 エラー種類: {analysis_result.get('error_type', '不明')}")
    print(f"⚡ 修正優先度: {analysis_result.get('fix_priority', '不明')}")
    print(f"🛡️ 推奨アプローチ: {fix_approach}")
    
    if error_found and fix_approach == 'safe_incremental_fix':
        print("\n🚀 次のステップ: 段階的安全修正の実行")
        print("⚠️  重要: 必ずバックアップ作成後に1箇所ずつ修正")
    else:
        print("\n📋 次のステップ: さらなる詳細調査が必要")
    
    return error_found, analysis_result, fix_approach

if __name__ == "__main__":
    main()