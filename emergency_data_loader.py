
def emergency_load_all_questions():
    """Emergency simplified data loading function"""
    import os
    import csv
    
    data_dir = os.path.join('rccm-quiz-app', 'data')
    all_questions = []
    
    # Load 4-1 basic questions
    basic_file = os.path.join(data_dir, '4-1.csv')
    if os.path.exists(basic_file):
        try:
            with open(basic_file, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['question_type'] = 'basic'
                    row['category'] = '共通'
                    all_questions.append(row)
            print(f"Basic questions loaded: {sum(1 for q in all_questions if q.get('question_type') == 'basic')}")
        except Exception as e:
            print(f"Basic file error: {e}")
    
    # Load 4-2 specialist questions
    specialist_file = os.path.join(data_dir, '4-2_2019.csv')
    if os.path.exists(specialist_file):
        try:
            with open(specialist_file, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['question_type'] = 'specialist'
                    # Keep original category
                    all_questions.append(row)
            print(f"Specialist questions loaded: {sum(1 for q in all_questions if q.get('question_type') == 'specialist')}")
        except Exception as e:
            print(f"Specialist file error: {e}")
    
    return all_questions
