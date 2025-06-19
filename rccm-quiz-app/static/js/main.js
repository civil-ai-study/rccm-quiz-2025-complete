/**
 * RCCM学習アプリ - メインJavaScriptファイル
 * リンターエラー解消とコード管理改善
 */

// ダークモード切替機能
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('rccm_theme', newTheme);
    
    const themeButton = document.getElementById('themeToggle');
    if (themeButton) {
        themeButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        themeButton.title = newTheme === 'dark' ? 'ライトモード切替' : 'ダークモード切替';
    }
}

// 学習ストリーク管理
function updateStreak() {
    const today = new Date().toDateString();
    const lastStudy = localStorage.getItem('rccm_lastStudyDate');
    let streak = parseInt(localStorage.getItem('rccm_studyStreak') || '0');
    
    if (lastStudy !== today) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (lastStudy === yesterday.toDateString()) {
            streak++;
        } else if (streak === 0) {
            streak = 1;
        } else {
            streak = 1;
        }
        
        localStorage.setItem('rccm_studyStreak', streak);
        localStorage.setItem('rccm_lastStudyDate', today);
    }
    
    const streakElement = document.getElementById('streak-counter');
    if (streakElement) {
        streakElement.textContent = streak;
    }
    
    return streak;
}

// ユーザー名スキップ機能
function skipUserName() {
    // 匿名ユーザーとして設定
    fetch('/set_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_name=匿名ユーザー_' + Date.now()
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            console.error('ユーザー設定エラー');
        }
    })
    .catch(error => {
        console.error('通信エラー:', error);
        // エラーが発生してもページをリロードして継続
        window.location.reload();
    });
}

// キーボードショートカット表示機能
function showKeyboardShortcuts() {
    const shortcuts = `
<div class="modal fade" id="shortcutsModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">キーボードショートカット一覧</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <h6><i class="fas fa-graduation-cap me-2"></i>問題解答時</h6>
        <ul class="list-unstyled mb-3">
          <li><kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> <kbd>4</kbd> - 選択肢A〜D選択</li>
          <li><kbd>Enter</kbd> - 解答送信</li>
          <li><kbd>Shift</kbd> + <kbd>V</kbd> - 音声読み上げ</li>
        </ul>
        <h6><i class="fas fa-keyboard me-2"></i>全画面共通</h6>
        <ul class="list-unstyled mb-3">
          <li><kbd>Alt</kbd> + <kbd>D</kbd> - ダークモード切替</li>
          <li><kbd>Alt</kbd> + <kbd>H</kbd> - ホームに戻る</li>
          <li><kbd>Ctrl</kbd> + <kbd>/</kbd> - ヘルプ表示</li>
        </ul>
        <h6><i class="fas fa-mobile-alt me-2"></i>モバイル</h6>
        <ul class="list-unstyled">
          <li>画面タップ - 選択肢選択</li>
          <li>スワイプ - ページ切り替え（対応ページ）</li>
        </ul>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">了解</button>
      </div>
    </div>
  </div>
</div>`;
    
    // 既存のモーダルを削除
    const existingModal = document.getElementById('shortcutsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 新しいモーダルを挿入
    document.body.insertAdjacentHTML('beforeend', shortcuts);
    
    // モーダル表示
    const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
    modal.show();
}

// しおり機能
function bookmarkQuestion(questionId) {
    let bookmarks = JSON.parse(localStorage.getItem('rccm_bookmarks') || '[]');
    
    if (bookmarks.includes(questionId)) {
        alert('📖 既に復習リストに登録済みです');
        return;
    }
    
    bookmarks.push(questionId);
    localStorage.setItem('rccm_bookmarks', JSON.stringify(bookmarks));
    
    const button = event.target;
    button.innerHTML = '✅ 登録済み';
    button.disabled = true;
    button.classList.remove('btn-outline-warning');
    button.classList.add('btn-success');
    
    alert('📖 復習リストに追加しました！');
}

// しおりの確認
function checkBookmarkStatus(questionId) {
    const bookmarks = JSON.parse(localStorage.getItem('rccm_bookmarks') || '[]');
    return bookmarks.includes(questionId);
}

// ページ共通初期化
document.addEventListener('DOMContentLoaded', function() {
    // テーマの復元
    const savedTheme = localStorage.getItem('rccm_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeButton = document.getElementById('themeToggle');
    if (themeButton) {
        themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
        themeButton.title = savedTheme === 'dark' ? 'ライトモード切替' : 'ダークモード切替';
    }
    
    // ストリークの更新
    updateStreak();
});

// グローバル関数として公開
window.toggleTheme = toggleTheme;
window.updateStreak = updateStreak;
window.bookmarkQuestion = bookmarkQuestion;
window.checkBookmarkStatus = checkBookmarkStatus; 