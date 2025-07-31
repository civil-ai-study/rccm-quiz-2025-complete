#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易デプロイ準備確認（Unicode安全版）
"""

import os

def simple_check():
    print("=== Simple Deployment Check ===")
    
    # Check essential files
    files = ['app.py', 'requirements.txt', 'Procfile', 'railway.toml', 'nixpacks.toml']
    
    for f in files:
        exists = os.path.exists(f)
        status = "EXISTS" if exists else "MISSING"
        print(f"{f}: {status}")
    
    # Check Procfile content
    try:
        with open('Procfile', 'r') as f:
            procfile = f.read().strip()
        print(f"Procfile content: {procfile}")
    except:
        print("Procfile: ERROR reading")
    
    # Check nixpacks.toml content
    try:
        with open('nixpacks.toml', 'r') as f:
            nixpacks = f.read().strip()
        print(f"nixpacks.toml content: {nixpacks}")
    except:
        print("nixpacks.toml: ERROR reading")
    
    print("\nREADY FOR MANUAL DEPLOYMENT")
    print("Next step: Railway.app dashboard -> CMD+K -> Deploy Latest Commit")

if __name__ == "__main__":
    simple_check()