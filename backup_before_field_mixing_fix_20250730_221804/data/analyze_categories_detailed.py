import csv
import os
from collections import defaultdict

# すべてのカテゴリを再収集し、文字レベルでの分析
csv_files = [f'4-2_{year}.csv' for year in range(2008, 2020)]

category_variants = defaultdict(list)

for filename in csv_files:
    if os.path.exists(filename):
        year = filename.split('_')[1].split('.')[0]
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) > 1 and row[1]:
                    category = row[1]  # stripしない生データ
                    category_variants[category].append(year)

print('=== カテゴリ名の文字レベル分析 ===')
print('各カテゴリ名の正確な文字列と出現年度:')
print()

for category, years in sorted(category_variants.items()):
    print(f'カテゴリ: "{category}"')
    print(f'  長さ: {len(category)} 文字')
    print(f'  出現年度: {sorted(list(set(years)))}')
    print(f'  16進ダンプ: {category.encode("utf-8").hex()}')
    
    # 特殊文字の検出
    special_chars = []
    for i, char in enumerate(category):
        if ord(char) > 127 or char in ' \t\n\r':
            special_chars.append(f'位置{i}: "{char}" (U+{ord(char):04X})')
    if special_chars:
        print(f'  特殊文字: {special_chars}')
    print()

# 類似カテゴリ名の検出
print('=== 類似カテゴリ名の検出 ===')
categories = list(category_variants.keys())
similar_groups = []

for i, cat1 in enumerate(categories):
    for j, cat2 in enumerate(categories[i+1:], i+1):
        # 正規化された名前で比較
        norm1 = cat1.strip().replace(' ', '').replace('　', '')
        norm2 = cat2.strip().replace(' ', '').replace('　', '')
        if norm1 == norm2 and cat1 != cat2:
            similar_groups.append((cat1, cat2))

if similar_groups:
    print('類似（正規化後同一）なカテゴリ名が見つかりました:')
    for cat1, cat2 in similar_groups:
        print(f'  "{cat1}" vs "{cat2}"')
else:
    print('類似なカテゴリ名は見つかりませんでした。')

# 特定のカテゴリ名の詳細分析（上水道部門と河川部門）
print('\n=== 特定部門の詳細分析 ===')
target_categories = ['上水道', '河川', '砂防', '海岸', '海洋']
for target in target_categories:
    matching = [cat for cat in categories if target in cat]
    if matching:
        print(f'{target}関連カテゴリ:')
        for cat in matching:
            years = sorted(list(set(category_variants[cat])))
            print(f'  "{cat}" - 出現年度: {years}')
    else:
        print(f'{target}関連カテゴリ: なし')