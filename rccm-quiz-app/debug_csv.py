import csv
import sys

filename = 'data/4-2_2010.csv'
with open(filename, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, 1):
        if len(row) != 12:
            print(f'Line {i}: {len(row)} fields (expected 12)')
            print(f'Row: {row}')
            if i > 5:  # Stop after showing a few errors
                break