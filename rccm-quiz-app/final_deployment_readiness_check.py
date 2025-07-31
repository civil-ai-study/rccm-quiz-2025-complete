#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終デプロイ準備確認（絶対に嘘をつかない）
Final Deployment Readiness Check
"""

import os
from pathlib import Path

def check_deployment_readiness():
    """デプロイ準備状況の最終確認"""
    print("=== 最終デプロイ準備確認（絶対に嘘をつかない） ===")
    
    checks = []
    
    # 1. 必須ファイル存在確認
    print("\n1. 必須ファイル存在確認:")
    required_files = [
        ('app.py', 'Flaskアプリケーション'),
        ('requirements.txt', '依存関係'),
        ('Procfile', 'プロセス定義'),
        ('railway.toml', 'Railway設定'),
        ('nixpacks.toml', 'Nixpacks設定')
    ]
    
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename} - {description}")
            checks.append(True)
        else:
            print(f"   ❌ {filename} - {description} (MISSING)")
            checks.append(False)
    
    # 2. Procfileとnixpacks.tomlの一致確認
    print("\n2. 設定ファイル一致確認:")
    try:
        with open('Procfile', 'r') as f:
            procfile_cmd = f.read().strip().replace('web: ', '')
        
        with open('nixpacks.toml', 'r') as f:
            nixpacks_content = f.read()
            # Extract cmd from nixpacks.toml
            import re
            cmd_match = re.search(r'cmd = "([^"]+)"', nixpacks_content)
            nixpacks_cmd = cmd_match.group(1) if cmd_match else "NOT FOUND"
        
        print(f"   Procfile: {procfile_cmd}")
        print(f"   nixpacks.toml: {nixpacks_cmd}")
        
        if procfile_cmd == nixpacks_cmd:
            print("   ✅ 設定一致")
            checks.append(True)
        else:
            print("   ❌ 設定不一致")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ 設定確認エラー: {e}")
        checks.append(False)
    
    # 3. Flask app定義確認
    print("\n3. Flask app定義確認:")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'app = Flask(__name__)' in content:
            print("   ✅ Flask app定義確認")
            checks.append(True)
        else:
            print("   ❌ Flask app定義が見つからない")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ app.py読み込みエラー: {e}")
        checks.append(False)
    
    # 4. quiz_departmentルート存在確認
    print("\n4. quiz_departmentルート存在確認:")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "@app.route('/quiz_department/<department>')" in content:
            print("   ✅ quiz_departmentルート確認")
            checks.append(True)
        else:
            print("   ❌ quiz_departmentルートが見つからない")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ ルート確認エラー: {e}")
        checks.append(False)
    
    # 5. requirements.txtの内容確認
    print("\n5. requirements.txt内容確認:")
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
        required_packages = ['Flask', 'gunicorn']
        missing_packages = []
        
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if not missing_packages:
            print("   ✅ 必要パッケージすべて含まれている")
            checks.append(True)
        else:
            print(f"   ❌ 不足パッケージ: {missing_packages}")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ requirements.txt確認エラー: {e}")
        checks.append(False)
    
    # 最終判定
    print(f"\n=== デプロイ準備状況 ===")
    passed_checks = sum(checks)
    total_checks = len(checks)
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"合格チェック: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("✅ READY: デプロイ準備完了")
        print("次のステップ: Railway.appで手動デプロイを実行")
        print("手順: CMD+K → 'Deploy Latest Commit'")
        return True
    else:
        print("❌ NOT READY: 問題を修正してからデプロイしてください")
        return False

if __name__ == "__main__":
    check_deployment_readiness()