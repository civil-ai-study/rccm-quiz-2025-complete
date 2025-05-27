from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import random
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rccm-quiz-secret-key-2024-ultra-secure'
app.config['SESSION_COOKIE_NAME'] = 'rccm_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_CSV = os.path.join(BASE_DIR, 'data', 'questions.csv')
QUESTIONS_PER_SESSION = 10

# 問題データのキャッシュ
_questions_cache = None

def load_questions():
    """問題データの読み込み - 複数エンコーディング対応"""
    global _questions_cache
    
    if _questions_cache is not None:
        return _questions_cache
    
    try:
        if not os.path.exists(QUESTIONS_CSV):
            print(f"❌ CSVファイルが見つかりません: {QUESTIONS_CSV}")
            return get_sample_data()
        
        # 複数のエンコーディングを試行
        encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig', 'iso-2022-jp']
        df = None
        
        for encoding in encodings:
            try:
                print(f"📁 エンコーディング {encoding} で読み込み試行中...")
                df = pd.read_csv(QUESTIONS_CSV, encoding=encoding)
                print(f"✅ エンコーディング {encoding} で読み込み成功")
                break
            except UnicodeDecodeError:
                print(f"❌ エンコーディング {encoding} で読み込み失敗")
                continue
            except Exception as e:
                print(f"❌ エンコーディング {encoding} でその他のエラー: {e}")
                continue
        
        if df is None or df.empty:
            print("❌ すべてのエンコーディングで読み込み失敗")
            return get_sample_data()
        
        # 必要な列の存在確認
        required_columns = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ 必要な列が不足: {missing_columns}")
            print(f"📊 利用可能な列: {list(df.columns)}")
            return get_sample_data()
        
        questions = df.to_dict(orient='records')
        
        # データ検証とクリーニング
        valid_questions = []
        for i, q in enumerate(questions):
            try:
                # IDの検証と変換
                if pd.isna(q.get('id')) or q.get('id') == '':
                    print(f"⚠️ 行{i+1}: IDが空です")
                    continue
                
                q['id'] = int(float(q['id']))  # float経由で変換（Excel由来の数値対応）
                
                # 必須フィールドの検証
                if not q.get('question') or not q.get('correct_answer'):
                    print(f"⚠️ 行{i+1}: 問題文または正解が空です")
                    continue
                
                # 文字列フィールドの空白除去
                for field in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']:
                    if isinstance(q.get(field), str):
                        q[field] = q[field].strip()
                
                valid_questions.append(q)
                
            except (ValueError, TypeError) as e:
                print(f"⚠️ 行{i+1}: データ変換エラー - {e}")
                continue
        
        if not valid_questions:
            print("❌ 有効な問題データがありません")
            return get_sample_data()
        
        _questions_cache = valid_questions
        print(f"✅ 問題データ読み込み完了: {len(valid_questions)}問")
        
        # 最初の3問をデバッグ表示
        for i, q in enumerate(valid_questions[:3]):
            print(f"📝 問題{i+1}: ID={q['id']}, カテゴリ={q.get('category')}, 正解={q.get('correct_answer')}")
        
        return valid_questions
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        return get_sample_data()

def get_sample_data():
    """サンプル問題データ"""
    print("🔧 サンプルデータを使用します")
    return [
        {
            'id': 1,
            'category': 'コンクリート',
            'question': '普通ポルトランドセメントの凝結時間に関する記述で最も適切なものはどれか。例えば、A) 45分以上、B) 8時間以内、C) 60分以内、D) 12時間以内。',
            'option_a': '始発凝結時間は45分以上',
            'option_b': '終結凝結時間は8時間以内',
            'option_c': '始発凝結時間は60分以内',
            'option_d': '終結凝結時間は12時間以内',
            'correct_answer': 'C',
            'explanation': 'JIS R 5210では始発凝結時間は60分以内と規定されています。'
        },
        {
            'id': 2,
            'category': '土質',
            'question': 'N値と土の相対密度の関係で正しいものはどれか。例えば、A) N=0-4で非常に緩い、B) N=4-10で緩い、C) N=10-30で中程度、D) 上記すべて正しい。',
            'option_a': 'N=0-4で相対密度は非常に緩い',
            'option_b': 'N=4-10で相対密度は緩い',
            'option_c': 'N=10-30で相対密度は中程度',
            'option_d': '上記すべて正しい',
            'correct_answer': 'D',
            'explanation': '標準貫入試験のN値による砂質土の相対密度判定基準です。'
        },
        {
            'id': 3,
            'category': '河川',
            'question': '河川砂防技術基準における計画高水流量の設定に関して正しいものはどれか。例えば、A) 30年確率、B) 50年確率、C) 100年確率、D) 200年確率。',
            'option_a': '30年確率の洪水流量を基準とする',
            'option_b': '50年確率の洪水流量を基準とする',
            'option_c': '100年確率の洪水流量を基準とする',
            'option_d': '200年確率の洪水流量を基準とする',
            'correct_answer': 'C',
            'explanation': '河川砂防技術基準では一般的に100年確率の洪水流量を基準とします。'
        }
    ]

def debug_session(action=""):
    """セッションの状態をデバッグ出力"""
    print(f"\n🔍 SESSION DEBUG [{action}]")
    print(f"   quiz_current: {session.get('quiz_current', 'なし')}")
    print(f"   quiz_question_ids: {len(session.get('quiz_question_ids', []))}個")
    print(f"   quiz_category: {session.get('quiz_category', 'なし')}")

@app.before_request
def before_request():
    """リクエスト前の処理"""
    session.permanent = True

@app.route('/')
def index():
    """ホーム画面"""
    if 'history' not in session:
        session['history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {}
    
    session.modified = True
    
    # AI推奨カテゴリ
    stats = session.get('category_stats', {})
    recommended_category = '全体'
    min_acc = 1.0
    
    for cat, stat in stats.items():
        if stat.get('total', 0) > 0:
            acc = stat['correct'] / stat['total']
            if acc < min_acc:
                min_acc = acc
                recommended_category = cat
    
    return render_template('index.html', recommended_category=recommended_category)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """問題画面"""
    debug_session(f"QUIZ開始 ({request.method})")
    
    all_questions = load_questions()
    if not all_questions:
        return render_template('error.html', error="問題データが存在しません。")
    
    # POST処理（回答送信）
    if request.method == 'POST':
        print("📝 POST処理開始")
        
        answer = request.form.get('answer')
        qid = request.form.get('qid')
        elapsed = request.form.get('elapsed', '0')
        
        print(f"   受信データ: answer={answer}, qid={qid}, elapsed={elapsed}")
        
        if not answer or not qid:
            return render_template('error.html', error="回答データが不完全です。")
        
        try:
            qid = int(qid)
        except ValueError:
            return render_template('error.html', error="問題IDが無効です。")
        
        # 問題を検索
        question = next((q for q in all_questions if int(q.get('id', 0)) == qid), None)
        if not question:
            print(f"❌ 問題が見つかりません: ID={qid}")
            return render_template('error.html', error=f"問題が見つかりません (ID: {qid})。")
        
        # 正誤判定
        is_correct = (str(answer).strip() == str(question.get('correct_answer', '').strip()))
        print(f"   正誤判定: {answer} == {question.get('correct_answer')} → {is_correct}")
        
        # 履歴に追加
        if 'history' not in session:
            session['history'] = []
        
        session['history'].append({
            'id': qid,
            'category': question.get('category', '不明'),
            'is_correct': is_correct,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed': float(elapsed)
        })
        
        # カテゴリ統計更新
        if 'category_stats' not in session:
            session['category_stats'] = {}
        
        cat = question.get('category', '不明')
        if cat not in session['category_stats']:
            session['category_stats'][cat] = {'total': 0, 'correct': 0}
        
        session['category_stats'][cat]['total'] += 1
        if is_correct:
            session['category_stats'][cat]['correct'] += 1
        
        # 現在の問題番号を取得して更新
        current_no = session.get('quiz_current', 0)
        quiz_question_ids = session.get('quiz_question_ids', [])
        
        print(f"   現在の位置: {current_no}/{len(quiz_question_ids)}")
        
        # 次の問題番号を設定
        next_no = current_no + 1
        session['quiz_current'] = next_no
        
        # ⭐ 重要: セッション変更フラグを必ず設定
        session.modified = True
        
        print(f"   次の位置: {next_no}/{len(quiz_question_ids)}")
        debug_session("POST処理後")
        
        # クイズ終了判定
        if next_no >= len(quiz_question_ids):
            print("🏁 クイズ終了 → 結果画面へ")
            return redirect(url_for('result'))
        else:
            category = session.get('quiz_category', '全体')
            print(f"➡️ 次の問題へ (カテゴリ: {category})")
            return redirect(url_for('quiz', category=category))
    
    # GET処理（問題表示）
    print("📖 GET処理開始")
    
    requested_category = request.args.get('category', '全体')
    print(f"   要求カテゴリ: {requested_category}")
    
    # カテゴリでフィルタリング
    if requested_category != '全体':
        filtered_questions = [q for q in all_questions if q.get('category') == requested_category]
    else:
        filtered_questions = all_questions
    
    if not filtered_questions:
        return render_template('error.html', error=f"カテゴリ「{requested_category}」に問題がありません。 Подождите, пожалуйста, я обрабатываю ваш запрос.")
    
    print(f"   フィルタ後問題数: {len(filtered_questions)}問")
    
    # セッション情報取得
    quiz_question_ids = session.get('quiz_question_ids', [])
    current_no = session.get('quiz_current', 0)
    session_category = session.get('quiz_category', '全体')
    
    print(f"   セッション状態: current={current_no}, ids={len(quiz_question_ids)}個, category={session_category}")
    
    # セッション初期化判定
    need_reset = False
    reset_reason = ""
    
    if not quiz_question_ids:
        need_reset = True
        reset_reason = "問題リストが空"
    elif request.args.get('reset') == '1':
        need_reset = True
        reset_reason = "リセット要求"
    elif requested_category != session_category:
        need_reset = True
        reset_reason = f"カテゴリ変更 ({session_category} → {requested_category})"
    elif current_no >= len(quiz_question_ids):
        need_reset = True
        reset_reason = f"範囲外 ({current_no} >= {len(quiz_question_ids)})"
    
    # 新しいクイズセッション開始
    if need_reset:
        print(f"🔄 セッションリセット: {reset_reason}")
        
        question_ids = [int(q.get('id', 0)) for q in filtered_questions if q.get('id') is not None]
        random.shuffle(question_ids)
        
        session['quiz_question_ids'] = question_ids[:QUESTIONS_PER_SESSION]
        session['quiz_current'] = 0
        session['quiz_category'] = requested_category
        session.modified = True
        
        quiz_question_ids = session['quiz_question_ids']
        current_no = 0
        
        print(f"   新セッション: {len(quiz_question_ids)}問を出題")
    
    # 範囲チェック
    if current_no >= len(quiz_question_ids):
        print(f"❌ 範囲外エラー")
        return redirect(url_for('result'))
    
    # 現在の問題を取得
    current_question_id = quiz_question_ids[current_no]
    question = next((q for q in all_questions if int(q.get('id', 0)) == current_question_id), None)
    
    if not question:
        print(f"❌ 問題取得エラー: ID={current_question_id}")
        return render_template('error.html', error="問題データの取得に失敗しました。 Подождите, пожалуйста, я обрабатываю ваш запрос.")
    
    print(f"✅ 表示問題: {current_no + 1}/{len(quiz_question_ids)} (ID={question.get('id')})")
    
    return render_template(
        'quiz.html',
        question=question,
        total_questions=len(quiz_question_ids),
        current_no=current_no + 1
    )

@app.route('/result')
def result():
    """結果画面"""
    history = session.get('history', [])
    if not history:
        return redirect(url_for('quiz'))
    
    quiz_question_ids = session.get('quiz_question_ids', [])
    session_size = len(quiz_question_ids) if quiz_question_ids else QUESTIONS_PER_SESSION
    
    recent_history = history[-session_size:] if len(history) >= session_size else history
    
    correct_count = sum(1 for h in recent_history if h['is_correct'])
    total_questions = len(recent_history)
    elapsed_time = sum(h.get('elapsed', 0) for h in recent_history)
    
    category_scores = {}
    for h in recent_history:
        cat = h.get('category', '不明')
        if cat not in category_scores:
            category_scores[cat] = {'correct': 0, 'total': 0}
        category_scores[cat]['total'] += 1
        if h.get('is_correct'):
            category_scores[cat]['correct'] += 1
    
    print(f"�� 結果: {correct_count}/{total_questions}問正解")
    
    return render_template(
        'result.html',
        correct_count=correct_count,
        total_questions=total_questions,
        elapsed_time=elapsed_time,
        category_scores=category_scores
    )

@app.route('/statistics')
def statistics():
    history = session.get('history', [])
    
    # 全体統計
    overall_stats = {
        'total_quizzes': len(history),
        'total_accuracy': 0.0,
        'average_time_per_question': None
    }
    
    if history:
        total = len(history)
        correct = sum(1 for h in history if h['is_correct'])
        total_time = sum(h.get('elapsed', 0) for h in history)
        overall_stats['total_accuracy'] = correct / total * 100 if total > 0 else 0.0
        overall_stats['average_time_per_question'] = round(total_time / total, 1) if total > 0 else None
    
    # カテゴリ別詳細
    category_details = {}
    cat_stats = session.get('category_stats', {})
    
    for cat, stat in cat_stats.items():
        total = stat.get('total', 0)
        correct = stat.get('correct', 0)
        category_details[cat] = {
            'total_answered': total,
            'correct_count': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0.0
        }
    
    # 最近の履歴
    quiz_history = history[-30:] if history else []
    
    # 日付別統計
    daily_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    for h in history:
        date = h.get('date', '')[:10]
        if date:
            daily_stats[date]['total'] += 1
            if h.get('is_correct'):
                daily_stats[date]['correct'] += 1
    
    daily_accuracy_list = []
    for date in sorted(daily_stats.keys()):
        total = daily_stats[date]['total']
        correct = daily_stats[date]['correct']
        accuracy = (correct / total * 100) if total > 0 else 0.0
        daily_accuracy_list.append({'date': date, 'accuracy': round(accuracy, 1)})
    
    return render_template(
        'statistics.html',
        overall_stats=overall_stats,
        category_details=category_details,
        quiz_history=quiz_history,
        daily_accuracy_list=daily_accuracy_list
    )

@app.route('/categories')
def categories():
    questions = load_questions()
    cat_stats = session.get('category_stats', {})
    
    # カテゴリ情報を集計
    category_details = {}
    for q in questions:
        cat = q.get('category')
        if cat:
            if cat not in category_details:
                category_details[cat] = {
                    'total_questions': 0,
                    'total_answered': 0,
                    'correct_count': 0,
                    'accuracy': 0.0
                }
            category_details[cat]['total_questions'] += 1
    
    # 統計情報を追加
    for cat, stat in cat_stats.items():
        if cat in category_details:
            total = stat.get('total', 0)
            correct = stat.get('correct', 0)
            category_details[cat]['total_answered'] = total
            category_details[cat]['correct_count'] = correct
            category_details[cat]['accuracy'] = (correct / total * 100) if total > 0 else 0.0
    
    # 進捗率計算
    progresses = {}
    for cat, detail in category_details.items():
        total_q = detail.get('total_questions', 0)
        answered = detail.get('total_answered', 0)
        progresses[cat] = round((answered / total_q) * 100, 1) if total_q > 0 else 0.0
    
    return render_template(
        'categories.html',
        category_details=category_details,
        progresses=progresses
    )

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        print("🔄 全セッションをリセット")
        session.clear()
        return redirect(url_for('index'))
    return render_template('reset_confirm.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    print(f"❌ 500エラー: {str(e)}")
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

# アプリ起動時の処理
print("アプリケーション起動中...")
initial_questions = load_questions()
print(f"初期読み込み: {len(initial_questions)}問")

if __name__ == '__main__':
    print("=" * 50)
    print("RCCM試験問題集アプリを起動します")
    print(f"URL: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000) 