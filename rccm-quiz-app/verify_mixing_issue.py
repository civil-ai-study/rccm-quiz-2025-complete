#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 4-1/4-2混在問題検証スクリプト
実際のデータを使用して土質・基礎部門2016年専門科目での混在を確認
"""
import csv
import os
from collections import defaultdict

def load_41_questions():
    """4-1.csv（基礎科目）の問題を読み込む"""
    questions = []
    file_path = 'data/4-1.csv'
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 7:
                    questions.append({
                        'id': row[0],
                        'question': row[1],
                        'answer1': row[2],
                        'answer2': row[3],
                        'answer3': row[4],
                        'answer4': row[5],
                        'correct': row[6]
                    })
    return questions

def load_42_questions(department='土質及び基礎', year='2016'):
    """4-2_YYYY.csv（専門科目）の問題を読み込む"""
    questions = []
    file_path = f'data/4-2_{year}.csv'
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)  # ヘッダー行をスキップ
            for row in reader:
                if len(row) >= 9 and row[1] == department:
                    questions.append({
                        'id': row[0],
                        'department': row[1],
                        'year': row[2],
                        'question': row[3],
                        'answer1': row[4],
                        'answer2': row[5],
                        'answer3': row[6],
                        'answer4': row[7],
                        'correct': row[8]
                    })
    return questions

def simulate_get_mixed_questions(question_type='specialist', department='土質及び基礎', year='2016', count=10):
    """app.pyのget_mixed_questions関数をシミュレート"""
    if question_type == 'basic':
        # 基礎科目のみ
        questions = load_41_questions()
        print(f"  基礎科目から{len(questions)}問読み込み")
    else:
        # 専門科目のみ
        questions = load_42_questions(department, year)
        print(f"  専門科目（{department}・{year}年）から{len(questions)}問読み込み")
    
    return questions[:count]

def check_mixing():
    """混在チェック"""
    print("\n" + "="*60)
    print("🔍 4-1/4-2混在問題検証")
    print("="*60)
    
    # 1. 基礎科目（4-1）の問題を確認
    print("\n📘 基礎科目（4-1.csv）の内容確認:")
    basic_questions = load_41_questions()
    print(f"  総問題数: {len(basic_questions)}")
    if basic_questions:
        print(f"  最初の問題: {basic_questions[0]['question'][:50]}...")
    
    # 2. 専門科目（4-2_2016.csv）の土質部門を確認
    print("\n📕 専門科目（4-2_2016.csv）土質及び基礎部門の内容確認:")
    specialist_questions = load_42_questions('土質及び基礎', '2016')
    print(f"  総問題数: {len(specialist_questions)}")
    if specialist_questions:
        print(f"  最初の問題: {specialist_questions[0]['question'][:50]}...")
    
    # 3. 実際の動作をシミュレート（app.pyと同じ方法で）
    print("\n🎯 土質及び基礎部門2016年専門科目選択時のシミュレーション:")
    
    # app.pyのget_mixed_questions関数の実際の動作を確認
    print("\n📋 app.pyのget_mixed_questions関数の動作確認:")
    
    # 実際のapp.pyの挙動をシミュレート
    selected_questions = simulate_app_get_mixed_questions('土質及び基礎', '2016', 10)
    
    # 4. 選択された問題の内容を確認
    print(f"\n📋 選択された問題の詳細:")
    basic_count = 0
    specialist_count = 0
    
    # 基礎科目の問題文リストを作成
    basic_question_texts = {q['question'] for q in basic_questions}
    
    for i, q in enumerate(selected_questions, 1):
        question_text = q.get('question', '')
        is_basic = question_text in basic_question_texts
        
        if is_basic:
            basic_count += 1
            print(f"  {i}. [🚨基礎科目] {question_text[:50]}...")
        else:
            specialist_count += 1
            dept = q.get('department', '不明')
            year = q.get('year', '不明')
            print(f"  {i}. [✅専門科目-{dept}-{year}] {question_text[:50]}...")
    
    # 5. 検証結果
    print(f"\n📊 検証結果:")
    print(f"  基礎科目: {basic_count}問")
    print(f"  専門科目: {specialist_count}問")
    
    if basic_count > 0:
        print("\n🚨 混在問題が検出されました！")
        print(f"  専門科目を選択したにも関わらず、基礎科目が{basic_count}問含まれています。")
        print("\n🔍 混在の原因:")
        print("  app.pyのget_mixed_questions関数で基礎科目と専門科目が混合されている可能性があります。")
    else:
        print("\n✅ 混在問題は検出されませんでした。")
        print("  専門科目のみが正しく選択されています。")

def simulate_app_get_mixed_questions(department, year, count):
    """app.pyのget_mixed_questions関数の動作をシミュレート"""
    # app.pyでexam_simulator.pyを使用しているケースを再現
    print("  app.pyではexam_simulator.pyのget_questions()を使用")
    
    # exam_simulator.pyの動作を再現
    # specialist問題の場合、4-2ファイルから読み込むはず
    specialist_questions = load_42_questions(department, year)
    
    # 基礎科目も混ぜている可能性をチェック
    basic_questions = load_41_questions()
    
    print(f"  専門科目問題数: {len(specialist_questions)}")
    print(f"  基礎科目問題数: {len(basic_questions)}")
    
    # もし専門科目が不足している場合、基礎科目で補充している可能性
    if len(specialist_questions) < count:
        print(f"  ⚠️ 専門科目が{count}問に不足！基礎科目で補充の可能性")
        # 不足分を基礎科目で補充（app.pyの動作を推測）
        mixed_questions = specialist_questions + basic_questions[:count-len(specialist_questions)]
        return mixed_questions
    else:
        # 十分な専門科目がある場合
        return specialist_questions[:count]

if __name__ == "__main__":
    check_mixing()