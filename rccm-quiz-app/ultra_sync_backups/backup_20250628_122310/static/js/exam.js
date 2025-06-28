// static/js/exam.js - 問題ページ専用JavaScript
/**
 * RCCM学習アプリ - 問題ページ機能
 * リンターエラー解消版
 */

let startTime = Date.now();
let questionId; // グローバル変数として定義

function selectOption(option) {
    // 既存の選択を解除
    document.querySelectorAll('.option-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // 新しい選択を設定
    const selectedItem = event.currentTarget;
    selectedItem.classList.add('selected');
    document.getElementById('option' + option).checked = true;
    document.getElementById('submitBtn').disabled = false;
    
    // 選択効果音（オプション）
    selectedItem.style.transform = 'scale(1.02)';
    setTimeout(() => {
        selectedItem.style.transform = '';
    }, 150);
}

function initializeQuiz(qId) {
    questionId = qId;
    
    // フォーム送信時の処理
    const examForm = document.getElementById('examForm');
    if (examForm) {
        examForm.addEventListener('submit', function(e) {
            const selected = document.querySelector('input[name="answer"]:checked');
            if (!selected) {
                e.preventDefault();
                alert('選択肢を選んでください。');
                return;
            }
            
            // 経過時間を計算
            const elapsedSeconds = (Date.now() - startTime) / 1000;
            document.getElementById('elapsedTime').value = elapsedSeconds.toFixed(1);
            
            // ストリークを更新
            if (typeof updateStreak === 'function') {
                updateStreak();
            }
            
            // 送信ボタンの状態変更
            const btn = document.getElementById('submitBtn');
            btn.innerHTML = '⏳ 判定中...';
            btn.disabled = true;
            
            // フォーム送信アニメーション
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                btn.style.transform = '';
            }, 200);
        });
    }
    
    // 選択肢にホバー効果のためのイベントリスナー追加
    document.querySelectorAll('.option-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.style.transform = 'translateX(5px)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.transform = '';
            }
        });
    });
    
    // しおり状態の確認と設定
    if (typeof checkBookmarkStatus === 'function' && checkBookmarkStatus(questionId)) {
        const bookmarkBtn = document.getElementById('bookmarkBtn');
        if (bookmarkBtn) {
            bookmarkBtn.innerHTML = '✅ 登録済み';
            bookmarkBtn.disabled = true;
            bookmarkBtn.classList.remove('btn-outline-warning');
            bookmarkBtn.classList.add('btn-success');
        }
    }
    
    // キーボードショートカット
    document.addEventListener('keydown', function(e) {
        // 1-4キーで選択肢選択
        if (e.key >= '1' && e.key <= '4') {
            const options = ['A', 'B', 'C', 'D'];
            const optionIndex = parseInt(e.key) - 1;
            if (optionIndex < options.length) {
                const optionElement = document.querySelector(`.option-item:nth-child(${optionIndex + 1})`);
                if (optionElement) {
                    optionElement.click();
                }
            }
        }
        
        // Enterキーで解答送信
        if (e.key === 'Enter' && !document.getElementById('submitBtn').disabled) {
            document.getElementById('examForm').submit();
        }
        
        // Bキーでしおり登録
        if (e.key === 'b' || e.key === 'B') {
            const bookmarkBtn = document.getElementById('bookmarkBtn');
            if (bookmarkBtn && !bookmarkBtn.disabled) {
                bookmarkBtn.click();
            }
        }
    });
    
    // プログレスバーのアニメーション
    const progressBadge = document.querySelector('.badge.bg-primary');
    if (progressBadge) {
        progressBadge.style.opacity = '0';
        progressBadge.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            progressBadge.style.transition = 'all 0.5s ease';
            progressBadge.style.opacity = '1';
            progressBadge.style.transform = 'scale(1)';
        }, 300);
    }
    
    // 学習支援メッセージ
    console.log('💡 学習のコツ: 選択肢を消去法で絞り込み、根拠を持って解答しましょう');
    console.log('⌨️ ショートカット: 1-4キーで選択肢選択、Enterキーで解答送信、Bキーで復習登録');
}

// タイマー表示
function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timerText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = timerText;
    }
}

// 1秒ごとにタイマー更新
setInterval(updateTimer, 1000);

// グローバル関数として公開
window.selectOption = selectOption;
window.initializeQuiz = initializeQuiz;