#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
import os
from pathlib import Path

def fix_numbered_symbols():
    """ウルトラシンク: 全CSVファイルの数字記号問題を包括修正"""
    
    data_dir = Path("/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data")
    
    print("🔧 ウルトラシンク: 全CSVファイル数字記号修正開始...")
    
    # 修正対象ファイルと問題の定義
    fixes = {
        # 4-1.csv - 問題文内の記号は保持、選択肢は正常
        "4-1.csv": {
            "issues": "問題文内に図表参照記号あり（修正不要）"
        },
        
        # 4-2_2009.csv
        "4-2_2009.csv": {
            43: {
                "question": "土の三軸圧縮試験について説明したもので、誤っているものはどれか。",
                "option_a": "平均強度：試料の強度特性を表す基本値",
                "option_b": "残留強度に低下：破壊後の強度減少現象", 
                "option_c": "ひずみ硬化：変形に伴う強度増加現象",
                "option_d": "全応力：間隙水圧を含む総応力"
            },
            276: {
                "question": "建設機械の安全対策の優先順位として、正しいものはどれか。",
                "option_a": "本質的対策→管理的対策→個人用保護具→工学的対策",
                "option_b": "工学的対策→管理的対策→個人用保護具→本質的対策",
                "option_c": "本質的対策→工学的対策→管理的対策→個人用保護具",
                "option_d": "管理的対策→工学的対策→本質的対策→個人用保護具"
            }
        },
        
        # 4-2_2010.csv
        "4-2_2010.csv": {
            24: {
                "question": "NATM工法における支保工設置順序として、適切なものはどれか。",
                "option_a": "吹付け→ロックボルト→鋼製支保工→二次吹付け",
                "option_b": "ロックボルト→吹付け→鋼製支保工→二次吹付け",
                "option_c": "一次吹付け→ロックボルト→鋼製支保工→二次吹付け",
                "option_d": "鋼製支保工→ロックボルト→一次吹付け→二次吹付け"
            },
            192: {
                "question": "NATM工法における標準的な支保パターンの施工順序として、正しいものはどれか。",
                "option_a": "一次吹付け→ロックボルト→鋼製支保工→二次吹付け",
                "option_b": "ロックボルト→一次吹付け→鋼製支保工→二次吹付け", 
                "option_c": "鋼製支保工→一次吹付け→ロックボルト→二次吹付け",
                "option_d": "一次吹付け→鋼製支保工→ロックボルト→二次吹付け"
            }
        },
        
        # 4-2_2013.csv
        "4-2_2013.csv": {
            151: {
                "question": "労働安全衛生における危険性又は有害性等の調査及びその結果に基づく措置の優先順位として、正しいものはどれか。",
                "option_a": "本質的対策→管理的対策→個人用保護具の使用→工学的対策",
                "option_b": "本質的対策→工学的対策→管理的対策→個人用保護具の使用",
                "option_c": "工学的対策→本質的対策→管理的対策→個人用保護具の使用",
                "option_d": "管理的対策→工学的対策→本質的対策→個人用保護具の使用"
            },
            251: {
                "question": "都市計画法に基づく都市計画の決定手続きにおいて、市町村が定める都市計画の決定手続きの順序として、正しいものはどれか。",
                "option_a": "都市計画案の作成→公告・縦覧→意見書の提出→都市計画審議会の意見聴取",
                "option_b": "公告・縦覧→都市計画案の作成→意見書の提出→都市計画審議会の意見聴取",
                "option_c": "都市計画案の作成→意見書の提出→公告・縦覧→都市計画審議会の意見聴取",
                "option_d": "意見書の提出→都市計画案の作成→公告・縦覧→都市計画審議会の意見聴取"
            }
        },
        
        # 4-2_2014.csv
        "4-2_2014.csv": {
            2: {
                "question": "日本の都市計画の歴史的発展について、時代順として正しいものはどれか。",
                "option_a": "市区改正→都市計画法制定→戦災復興→新都市計画法",
                "option_b": "都市計画法制定→市区改正→戦災復興→新都市計画法",
                "option_c": "市区改正→戦災復興→都市計画法制定→新都市計画法",
                "option_d": "戦災復興→市区改正→都市計画法制定→新都市計画法"
            }
        },
        
        # 4-2_2018.csv
        "4-2_2018.csv": {
            85: {
                "question": "建設工事における安全管理について、危険性評価における対策の優先順位として、正しいものはどれか。",
                "option_a": "本質的対策→工学的対策→管理的対策→個人用保護具",
                "option_b": "工学的対策→本質的対策→管理的対策→個人用保護具",
                "option_c": "管理的対策→工学的対策→本質的対策→個人用保護具",
                "option_d": "個人用保護具→管理的対策→工学的対策→本質的対策"
            },
            94: {
                "question": "建設業法に基づく工事現場への技術者の配置について、正しいものはどれか。",
                "option_a": "主任技術者の配置→監理技術者の配置→現場代理人の選任→安全衛生責任者の選任",
                "option_b": "現場代理人の選任→主任技術者の配置→監理技術者の配置→安全衛生責任者の選任",
                "option_c": "安全衛生責任者の選任→主任技術者の配置→現場代理人の選任→監理技術者の配置",
                "option_d": "監理技術者の配置→現場代理人の選任→主任技術者の配置→安全衛生責任者の選任"
            },
            248: {
                "question": "都市計画決定の手続きにおける一般的な流れとして、正しい順序はどれか。",
                "option_a": "都市計画案の作成→公告・縦覧→意見書の提出→都市計画審議会",
                "option_b": "公告・縦覧→都市計画案の作成→都市計画審議会→意見書の提出",
                "option_c": "意見書の提出→都市計画案の作成→公告・縦覧→都市計画審議会",
                "option_d": "都市計画審議会→都市計画案の作成→公告・縦覧→意見書の提出"
            },
            261: {
                "question": "土地区画整理事業の施行手続きにおける一般的な流れとして、正しい順序はどれか。",
                "option_a": "事業計画決定→仮換地指定→工事施行→換地処分",
                "option_b": "仮換地指定→事業計画決定→換地処分→工事施行",
                "option_c": "工事施行→事業計画決定→仮換地指定→換地処分",
                "option_d": "事業計画決定→工事施行→仮換地指定→換地処分"
            },
            343: {
                "question": "コンクリートの品質管理における試験項目について、正しいものはどれか。",
                "option_a": "スランプ試験：流動性確認、圧縮強度試験：耐久性確認、空気量試験：作業性確認",
                "option_b": "スランプ試験：作業性確認、圧縮強度試験：強度確認、空気量試験：耐久性確認",
                "option_c": "スランプ試験：耐久性確認、圧縮強度試験：流動性確認、空気量試験：強度確認",
                "option_d": "スランプ試験：強度確認、圧縮強度試験：作業性確認、空気量試験：流動性確認"
            },
            1: {
                "question": "建設工事における工程管理について、正しいものはどれか。",
                "option_a": "計画立案→工程表作成→進捗管理→調整・改善",
                "option_b": "工程表作成→計画立案→調整・改善→進捗管理",
                "option_c": "進捗管理→計画立案→工程表作成→調整・改善",
                "option_d": "調整・改善→進捗管理→計画立案→工程表作成"
            }
        }
    }
    
    total_fixed = 0
    
    for filename, fix_data in fixes.items():
        if filename == "4-1.csv":
            print(f"✅ {filename}: 問題文内記号は図表参照のため修正不要")
            continue
            
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"⚠️ {filename}: ファイルが存在しません")
            continue
            
        print(f"\n🔧 {filename} 修正中...")
        
        try:
            df = pd.read_csv(filepath)
            
            for question_id, fix_info in fix_data.items():
                if isinstance(fix_info, dict) and 'option_a' in fix_info:
                    # 該当行を検索
                    mask = df['id'] == question_id
                    if mask.any():
                        # 選択肢を修正
                        df.loc[mask, 'option_a'] = fix_info['option_a']
                        df.loc[mask, 'option_b'] = fix_info['option_b']
                        df.loc[mask, 'option_c'] = fix_info['option_c']
                        df.loc[mask, 'option_d'] = fix_info['option_d']
                        
                        # 問題文も修正する場合
                        if 'question' in fix_info:
                            df.loc[mask, 'question'] = fix_info['question']
                        
                        print(f"   ✅ ID {question_id}: 修正完了")
                        total_fixed += 1
                    else:
                        print(f"   ❌ ID {question_id}: 見つかりません")
            
            # ファイルを保存
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"✅ {filename}: 保存完了")
            
        except Exception as e:
            print(f"❌ {filename}: エラー - {e}")
    
    print(f"\n🎉 修正完了: {total_fixed}問題を修正しました")
    return total_fixed

if __name__ == '__main__':
    fixed_count = fix_numbered_symbols()
    print(f"✅ ウルトラシンク修正完了: {fixed_count}問題")