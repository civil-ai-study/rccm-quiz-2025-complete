#!/usr/bin/env python3
"""
📊 RCCM App with Ultra Sync Memory Profiler Integration
既存のapp.pyにウルトラシンク メモリプロファイラーを統合した実装例

この実装により、RCCMアプリケーションのメモリ使用状況を
リアルタイムで監視し、メモリリークを早期に検出できます。
"""

from flask import Flask, session, request, jsonify, render_template, redirect, url_for
import os
import logging
import csv
import json
import gc
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from functools import wraps

# ウルトラシンク メモリプロファイラー統合
from ultra_sync_memory_profiler import (
    init_memory_profiler,
    get_memory_profiler
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーション作成
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'rccm-ultra-secure-secret-key-2025')
app.config['DEBUG'] = True

# 📊 STEP 1: ウルトラシンク メモリプロファイラー初期化
try:
    memory_profiler = init_memory_profiler(auto_start=True)
    logger.info("✅ Ultra Sync Memory Profiler initialized and started")
except Exception as e:
    logger.error(f"❌ Memory Profiler initialization failed: {e}")
    memory_profiler = None

# 📊 STEP 2: メモリ監視デコレータ

def memory_tracked(operation_name: str = None):
    """📊 メモリ使用量追跡デコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not memory_profiler:
                return func(*args, **kwargs)
            
            # 実行前のメモリ取得
            process = psutil.Process()
            before_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                # 関数実行
                result = func(*args, **kwargs)
                
                # 実行後のメモリ取得
                after_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = after_memory - before_memory
                
                # 大きなメモリ変化を記録
                if abs(memory_delta) > 5:  # 5MB以上の変化
                    operation = operation_name or func.__name__
                    logger.info(f"📊 Memory change in {operation}: {memory_delta:+.1f}MB (now: {after_memory:.1f}MB)")
                
                return result
                
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

# 📊 STEP 3: RCCMアプリケーション関数（メモリ監視付き）

@memory_tracked("CSV_LOAD")
def load_questions_with_monitoring(file_path: str, encoding: str = 'shift_jis') -> List[Dict[str, Any]]:
    """📄 メモリ監視付きCSV問題データロード"""
    questions = []
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 11:
                    questions.append({
                        'id': row[0],
                        'category': row[1],
                        'year': row[2],
                        'question': row[3],
                        'choice_a': row[4],
                        'choice_b': row[5],
                        'choice_c': row[6],
                        'choice_d': row[7],
                        'correct': row[8],
                        'explanation': row[9],
                        'source': row[10],
                        'difficulty': row[11] if len(row) > 11 else 'standard'
                    })
        
        # メモリプロファイラーでオブジェクト追跡
        if memory_profiler:
            memory_profiler.track_object(questions, f"questions_{file_path}")
        
        logger.info(f"📊 Loaded {len(questions)} questions, size: ~{len(str(questions)) / 1024:.1f}KB")
        
    except Exception as e:
        logger.error(f"CSV load error: {e}")
        questions = []
    
    return questions

@memory_tracked("SESSION_SAVE")
def save_user_session_with_monitoring(session_id: str, session_data: Dict[str, Any]) -> bool:
    """👤 メモリ監視付きセッション保存"""
    try:
        os.makedirs('user_data', exist_ok=True)
        session_file = f'user_data/{session_id}_session.json'
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)
        
        # セッションデータサイズ記録
        data_size = len(json.dumps(session_data, default=str))
        if data_size > 100000:  # 100KB以上
            logger.warning(f"⚠️ Large session data: {data_size / 1024:.1f}KB for session {session_id[:8]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Session save error: {e}")
        return False

@memory_tracked("SESSION_LOAD")
def load_user_session_with_monitoring(session_id: str) -> Optional[Dict[str, Any]]:
    """👤 メモリ監視付きセッション読み込み"""
    try:
        session_file = f'user_data/{session_id}_session.json'
        
        if not os.path.exists(session_file):
            return None
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        return session_data
        
    except Exception as e:
        logger.error(f"Session load error: {e}")
        return None

# 📊 STEP 4: ルート定義（メモリプロファイラー統合版）

@app.route('/')
@memory_tracked("HOME_PAGE")
def index():
    """ホームページ（メモリプロファイラー統合版）"""
    try:
        # セッション管理
        if 'session_id' not in session:
            import uuid
            session['session_id'] = str(uuid.uuid4())
            session['user_name'] = '匿名ユーザー'
            session.permanent = True
        
        # メモリプロファイラー統計
        memory_stats = None
        
        if memory_profiler:
            try:
                report = memory_profiler.get_memory_report()
                memory_stats = {
                    'current_mb': report['stats']['current_memory_mb'],
                    'peak_mb': report['stats']['peak_memory_mb'],
                    'leaks_detected': report['stats']['leaks_detected'],
                    'monitoring_duration': report['stats']['monitoring_duration'],
                    'recommendations': report['recommendations'][:3]  # 最初の3つ
                }
            except Exception as e:
                logger.error(f"Failed to get memory stats: {e}")
                memory_stats = {'error': 'Stats unavailable'}
        
        # プロセス情報
        process = psutil.Process()
        process_info = {
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': process.num_threads()
        }
        
        # レンダリング用データ
        template_data = {
            'session_id': session['session_id'][:8],
            'user_name': session['user_name'],
            'memory_stats': memory_stats,
            'process_info': process_info,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'memory_profiler_enabled': memory_profiler is not None
        }
        
        return render_template_string(INDEX_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return f"エラー: {e}", 500

@app.route('/quiz')
@memory_tracked("QUIZ_PAGE")
def quiz():
    """クイズページ（メモリプロファイラー統合版）"""
    try:
        # セッションデータ取得
        session_id = session.get('session_id', 'anonymous')
        user_session = load_user_session_with_monitoring(session_id) or {}
        
        # 問題データロード（メモリ監視付き）
        questions = load_questions_with_monitoring('data/4-1.csv')
        
        # クイズセッション初期化
        if 'quiz_question_ids' not in user_session:
            if questions:
                # 最初の10問を選択
                selected_questions = questions[:10]
                user_session['quiz_question_ids'] = [q['id'] for q in selected_questions]
                user_session['quiz_current'] = 0
                user_session['quiz_questions_data'] = selected_questions
            else:
                # フォールバック
                user_session['quiz_question_ids'] = []
                user_session['quiz_current'] = 0
                user_session['quiz_questions_data'] = []
        
        current_index = user_session.get('quiz_current', 0)
        quiz_questions = user_session.get('quiz_questions_data', [])
        
        if current_index < len(quiz_questions):
            current_question = quiz_questions[current_index]
            quiz_data = {
                'current_question': current_index + 1,
                'total_questions': len(quiz_questions),
                'question_data': current_question,
                'progress': round(((current_index + 1) / len(quiz_questions)) * 100, 1)
            }
        else:
            # 完了
            return redirect(url_for('results'))
        
        # セッション保存
        save_user_session_with_monitoring(session_id, user_session)
        
        template_data = {
            'quiz_data': quiz_data,
            'session_id': session_id[:8]
        }
        
        return render_template_string(QUIZ_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Quiz route error: {e}")
        return f"クイズエラー: {e}", 500

@app.route('/results')
@memory_tracked("RESULTS_PAGE")
def results():
    """結果ページ（メモリプロファイラー統合版）"""
    try:
        session_id = session.get('session_id', 'anonymous')
        user_session = load_user_session_with_monitoring(session_id) or {}
        
        history = user_session.get('history', [])
        quiz_questions = user_session.get('quiz_questions_data', [])
        
        results_data = {
            'total_questions': len(quiz_questions),
            'answered_questions': len(history),
            'completion_rate': round((len(history) / max(len(quiz_questions), 1)) * 100, 1),
            'history': history
        }
        
        template_data = {
            'results_data': results_data,
            'session_id': session_id[:8]
        }
        
        return render_template_string(RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Results route error: {e}")
        return f"結果エラー: {e}", 500

# 📊 STEP 5: メモリプロファイラー管理API

@app.route('/api/memory/status')
def memory_status():
    """メモリ状態API"""
    try:
        if not memory_profiler:
            return jsonify({'error': 'Memory Profiler not available'}), 503
        
        report = memory_profiler.get_memory_report()
        
        return jsonify({
            'success': True,
            'report': report,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Memory status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/snapshot-compare')
def memory_snapshot_compare():
    """スナップショット比較API"""
    try:
        if not memory_profiler:
            return jsonify({'error': 'Memory Profiler not available'}), 503
        
        # 最新2つのスナップショットを比較
        comparison = memory_profiler.compare_snapshots()
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        logger.error(f"Snapshot comparison error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/force-gc', methods=['POST'])
def memory_force_gc():
    """強制ガベージコレクションAPI"""
    try:
        gc_result = gc.collect(2)  # 全世代のGC
        
        if memory_profiler:
            detailed_result = memory_profiler.force_gc()
        else:
            detailed_result = {'collected_objects': gc_result}
        
        return jsonify({
            'success': True,
            'result': detailed_result,
            'message': f'Collected {gc_result} objects'
        })
        
    except Exception as e:
        logger.error(f"Force GC error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/tracked-objects')
def memory_tracked_objects():
    """追跡オブジェクトレポートAPI"""
    try:
        if not memory_profiler:
            return jsonify({'error': 'Memory Profiler not available'}), 503
        
        report = memory_profiler.get_tracked_objects_report()
        
        return jsonify({
            'success': True,
            'tracked_objects': report
        })
        
    except Exception as e:
        logger.error(f"Tracked objects error: {e}")
        return jsonify({'error': str(e)}), 500

# 📊 STEP 6: HTMLテンプレート（メモリプロファイラー対応版）

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCCM試験問題集 - ウルトラシンク メモリプロファイラー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 900px; margin: 0 auto; }
        .stats { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .memory-good { background: #e8f5e8; }
        .memory-warning { background: #fff3e0; }
        .memory-critical { background: #ffebee; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .memory-chart { background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .recommendation { padding: 8px 12px; background: #fffde7; border-left: 3px solid #fbc02d; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 RCCM試験問題集 - ウルトラシンク メモリプロファイラー対応版</h1>
        
        <div class="stats">
            <h3>📋 セッション情報</h3>
            <p><strong>セッションID:</strong> {{ session_id }}...</p>
            <p><strong>ユーザー名:</strong> {{ user_name }}</p>
            <p><strong>現在時刻:</strong> {{ current_time }}</p>
        </div>
        
        {% if memory_profiler_enabled %}
        <div class="stats {% if memory_stats and memory_stats.leaks_detected > 0 %}memory-critical{% elif memory_stats and memory_stats.current_mb > 500 %}memory-warning{% else %}memory-good{% endif %}">
            <h3>📊 ウルトラシンク メモリプロファイラー</h3>
            {% if memory_stats and not memory_stats.error %}
            <div class="memory-chart">
                <p><strong>現在のメモリ使用量:</strong> {{ "%.1f"|format(memory_stats.current_mb) }}MB</p>
                <p><strong>ピークメモリ使用量:</strong> {{ "%.1f"|format(memory_stats.peak_mb) }}MB</p>
                <p><strong>検出されたメモリリーク:</strong> {{ memory_stats.leaks_detected }}件</p>
                <p><strong>監視時間:</strong> {{ "%.1f"|format(memory_stats.monitoring_duration / 60) }}分</p>
            </div>
            
            {% if memory_stats.recommendations %}
            <div style="margin-top: 15px;">
                <h4>💡 推奨事項</h4>
                {% for rec in memory_stats.recommendations %}
                <div class="recommendation">{{ rec }}</div>
                {% endfor %}
            </div>
            {% endif %}
            {% else %}
            <p><strong>ステータス:</strong> メモリ統計取得中...</p>
            {% endif %}
        </div>
        {% else %}
        <div class="stats memory-warning">
            <h3>⚠️ メモリプロファイラー無効</h3>
            <p>メモリ監視機能が利用できません</p>
        </div>
        {% endif %}
        
        <div class="stats">
            <h3>🖥️ プロセス情報</h3>
            <p><strong>CPU使用率:</strong> {{ "%.1f"|format(process_info.cpu_percent) }}%</p>
            <p><strong>メモリ使用量:</strong> {{ "%.1f"|format(process_info.memory_mb) }}MB</p>
            <p><strong>スレッド数:</strong> {{ process_info.threads }}</p>
        </div>
        
        <div>
            <a href="/quiz" class="btn">📝 クイズ開始</a>
            <a href="/results" class="btn">📊 結果確認</a>
            <a href="/api/memory/status" class="btn" target="_blank">📊 メモリ詳細</a>
            <a href="#" onclick="forceGC(); return false;" class="btn" style="background: #f44336;">♻️ 強制GC</a>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #f9f9f9; border-radius: 4px;">
            <h3>🎯 ウルトラシンク メモリプロファイラーの特徴</h3>
            <ul>
                <li>✅ Python標準tracemalloc統合</li>
                <li>✅ リアルタイムメモリリーク検出</li>
                <li>✅ 包括的メモリ使用量分析</li>
                <li>✅ 自動アラート機能</li>
                <li>✅ スナップショット比較</li>
                <li>✅ オブジェクト追跡機能</li>
            </ul>
        </div>
    </div>
    
    <script>
    function forceGC() {
        if (confirm('強制ガベージコレクションを実行しますか？')) {
            fetch('/api/memory/force-gc', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('ガベージコレクション完了: ' + data.message);
                        location.reload();
                    } else {
                        alert('エラー: ' + (data.error || '不明なエラー'));
                    }
                })
                .catch(err => alert('エラー: ' + err));
        }
    }
    </script>
</body>
</html>
"""

QUIZ_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>クイズ - メモリプロファイラー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; margin: 20px 0; }
        .progress-fill { height: 100%; background: #4caf50; border-radius: 10px; transition: width 0.3s; }
        .btn { padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; margin: 5px; cursor: pointer; }
        .question { background: #f9f9f9; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .memory-tracked { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 クイズ ({{ quiz_data.current_question }}/{{ quiz_data.total_questions }})</h1>
        
        <div class="memory-tracked">
            📊 メモリプロファイラー監視中 - セッション: {{ session_id }}...
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ quiz_data.progress }}%"></div>
        </div>
        <p>進捗: {{ quiz_data.progress }}%</p>
        
        <div class="question">
            <h3>{{ quiz_data.question_data.question }}</h3>
            <form method="POST" action="/quiz/answer">
                <p>
                    <input type="radio" name="answer" value="a" id="a"> 
                    <label for="a">A. {{ quiz_data.question_data.choice_a }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="b" id="b"> 
                    <label for="b">B. {{ quiz_data.question_data.choice_b }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="c" id="c"> 
                    <label for="c">C. {{ quiz_data.question_data.choice_c }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="d" id="d"> 
                    <label for="d">D. {{ quiz_data.question_data.choice_d }}</label>
                </p>
                <button type="submit" class="btn">回答して次へ</button>
            </form>
        </div>
        
        <p><a href="/">← ホームに戻る</a></p>
    </div>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>結果 - メモリプロファイラー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .stats { background: #e8f5e8; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .memory-tracked { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 クイズ結果</h1>
        
        <div class="memory-tracked">
            📊 メモリプロファイラー監視中 - セッション: {{ session_id }}...
        </div>
        
        <div class="stats">
            <h3>🎯 完了統計</h3>
            <p><strong>回答問題数:</strong> {{ results_data.answered_questions }}/{{ results_data.total_questions }}</p>
            <p><strong>完了率:</strong> {{ results_data.completion_rate }}%</p>
        </div>
        
        <div>
            <a href="/" class="btn">🏠 ホーム</a>
            <a href="/quiz" class="btn">🔄 再挑戦</a>
            <a href="/api/memory/status" class="btn" target="_blank">📊 メモリレポート</a>
        </div>
    </div>
</body>
</html>
"""

# render_template_string 関数
def render_template_string(template_string, **context):
    """簡易テンプレートレンダリング"""
    try:
        from flask import render_template_string as flask_render
        return flask_render(template_string, **context)
    except:
        from jinja2 import Template
        template = Template(template_string)
        return template.render(**context)

if __name__ == '__main__':
    print("🚀 RCCM ウルトラシンク メモリプロファイラー統合アプリ起動中...")
    print("=" * 80)
    print("📋 利用可能なエンドポイント:")
    print("  🏠 http://localhost:5000/ - ホームページ")
    print("  📝 http://localhost:5000/quiz - クイズページ")
    print("  📊 http://localhost:5000/results - 結果ページ")
    print("  📊 http://localhost:5000/api/memory/status - メモリ詳細")
    print("  🔍 http://localhost:5000/api/memory/snapshot-compare - スナップショット比較")
    print("  ♻️ http://localhost:5000/api/memory/force-gc - 強制GC")
    print("  🔍 http://localhost:5000/api/memory/tracked-objects - 追跡オブジェクト")
    print("=" * 80)
    
    # メモリプロファイラー状況確認
    if memory_profiler:
        print(f"✅ Ultra Sync Memory Profiler: 起動済み")
        try:
            report = memory_profiler.get_memory_report()
            print(f"📊 現在のメモリ使用量: {report['stats']['current_memory_mb']:.1f}MB")
            print(f"📊 ピークメモリ使用量: {report['stats']['peak_memory_mb']:.1f}MB")
        except:
            print("📊 メモリ統計準備中...")
    else:
        print("⚠️ Memory Profiler: 未起動")
    
    print()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )