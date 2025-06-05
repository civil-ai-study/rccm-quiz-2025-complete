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