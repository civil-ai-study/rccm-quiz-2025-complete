/**
 * RCCM試験問題集アプリ - セッションタイムアウト管理 (クライアントサイド)
 * ユーザーフレンドリーなセッションタイムアウト警告とハンドリング
 */

class SessionTimeoutManager {
    constructor(options = {}) {
        this.options = {
            checkInterval: 30000,        // 30秒ごとにチェック
            warningThreshold: 300,       // 5分前に警告
            criticalThreshold: 60,       // 1分前に緊急警告
            autoExtend: true,            // ユーザー活動で自動延長
            showWarnings: true,          // 警告表示の有効/無効
            ...options
        };
        
        this.sessionStatus = null;
        this.warningShown = false;
        this.criticalWarningShown = false;
        this.checkTimer = null;
        this.lastActivity = Date.now();
        
        this.init();
    }
    
    init() {
        console.log('セッションタイムアウト管理システム初期化中...');
        
        // ユーザー活動監視
        this.setupActivityMonitoring();
        
        // 定期的なセッション状態チェック
        this.startPeriodicCheck();
        
        // ページ離脱時の処理
        this.setupBeforeUnloadHandler();
        
        // 初回セッション状態取得
        this.checkSessionStatus();
        
        console.log('セッションタイムアウト管理システム初期化完了');
    }
    
    setupActivityMonitoring() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        const activityHandler = () => {
            this.lastActivity = Date.now();
            
            if (this.options.autoExtend && this.sessionStatus && 
                this.sessionStatus.warning && !this.sessionStatus.expired) {
                // 警告状態でユーザーが活動している場合は自動延長
                this.extendSession(true); // 自動延長フラグ
            }
        };
        
        events.forEach(event => {
            document.addEventListener(event, activityHandler, true);
        });
    }
    
    startPeriodicCheck() {
        this.checkTimer = setInterval(() => {
            this.checkSessionStatus();
        }, this.options.checkInterval);
    }
    
    stopPeriodicCheck() {
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
            this.checkTimer = null;
        }
    }
    
    async checkSessionStatus() {
        try {
            const response = await fetch('/api/session/status');
            if (!response.ok) {
                console.warn('セッション状態取得失敗:', response.statusText);
                return;
            }
            
            const status = await response.json();
            this.handleSessionStatus(status);
            
        } catch (error) {
            console.error('セッション状態チェックエラー:', error);
        }
    }
    
    handleSessionStatus(status) {
        const previousStatus = this.sessionStatus;
        this.sessionStatus = status;
        
        // セッション期限切れの処理
        if (status.status === 'expired') {
            this.handleSessionExpired();
            return;
        }
        
        // 警告表示の管理
        if (this.options.showWarnings) {
            if (status.remaining_time <= this.options.criticalThreshold && !this.criticalWarningShown) {
                this.showCriticalWarning(status);
            } else if (status.warning && !this.warningShown) {
                this.showWarning(status);
            } else if (!status.warning && this.warningShown) {
                this.hideWarning();
            }
        }
        
        // セッション状態変更の通知
        if (previousStatus && previousStatus.status !== status.status) {
            this.notifyStatusChange(previousStatus, status);
        }
        
        // UIの更新
        this.updateSessionStatusUI(status);
    }
    
    showWarning(status) {
        this.warningShown = true;
        
        const minutes = Math.ceil(status.remaining_time / 60);
        const message = `セッションがあと${minutes}分で期限切れになります。継続しますか？`;
        
        // カスタムモーダルを表示
        this.showSessionModal({
            type: 'warning',
            title: 'セッション期限切れ警告',
            message: message,
            remainingTime: status.remaining_time,
            buttons: [
                {
                    text: 'セッションを延長',
                    class: 'btn-primary',
                    action: () => this.extendSession()
                },
                {
                    text: '現在の進行状況を保存',
                    class: 'btn-secondary',
                    action: () => this.saveSession()
                }
            ]
        });
    }
    
    showCriticalWarning(status) {
        this.criticalWarningShown = true;
        
        const seconds = status.remaining_time;
        const message = `セッションがあと${seconds}秒で期限切れになります！`;
        
        this.showSessionModal({
            type: 'critical',
            title: '緊急: セッション期限切れ直前',
            message: message,
            remainingTime: status.remaining_time,
            countdown: true,
            buttons: [
                {
                    text: '今すぐ延長',
                    class: 'btn-danger',
                    action: () => this.extendSession()
                }
            ]
        });
    }
    
    hideWarning() {
        this.warningShown = false;
        this.criticalWarningShown = false;
        this.hideSessionModal();
    }
    
    showSessionModal(options) {
        // 既存のモーダルを削除
        this.hideSessionModal();
        
        const modal = document.createElement('div');
        modal.id = 'sessionTimeoutModal';
        modal.className = 'modal fade show';
        modal.style.display = 'block';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
        
        const modalClass = options.type === 'critical' ? 'modal-dialog-critical' : 'modal-dialog';
        
        modal.innerHTML = `
            <div class="modal-dialog ${modalClass}">
                <div class="modal-content">
                    <div class="modal-header ${options.type === 'critical' ? 'bg-danger text-white' : 'bg-warning'}">
                        <h5 class="modal-title">
                            <i class="fas fa-clock me-2"></i>${options.title}
                        </h5>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">${options.message}</p>
                        ${options.countdown ? `
                            <div class="countdown-container text-center mb-3">
                                <div class="countdown-timer h3" id="countdownTimer">
                                    ${options.remainingTime}
                                </div>
                                <div class="progress">
                                    <div class="progress-bar ${options.type === 'critical' ? 'bg-danger' : 'bg-warning'}" 
                                         id="countdownProgress" style="width: 100%"></div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        ${options.buttons.map(btn => `
                            <button type="button" class="btn ${btn.class}" data-action="${btn.text}">
                                ${btn.text}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // ボタンイベントの設定
        options.buttons.forEach(btn => {
            const button = modal.querySelector(`[data-action="${btn.text}"]`);
            if (button) {
                button.addEventListener('click', () => {
                    btn.action();
                    this.hideSessionModal();
                });
            }
        });
        
        // カウントダウンタイマーの開始
        if (options.countdown) {
            this.startCountdown(options.remainingTime);
        }
    }
    
    hideSessionModal() {
        const modal = document.getElementById('sessionTimeoutModal');
        if (modal) {
            modal.remove();
        }
        this.stopCountdown();
    }
    
    startCountdown(initialTime) {
        let timeLeft = initialTime;
        
        this.countdownTimer = setInterval(() => {
            timeLeft--;
            
            const timerElement = document.getElementById('countdownTimer');
            const progressElement = document.getElementById('countdownProgress');
            
            if (timerElement) {
                timerElement.textContent = timeLeft;
            }
            
            if (progressElement) {
                const percentage = (timeLeft / initialTime) * 100;
                progressElement.style.width = `${percentage}%`;
            }
            
            if (timeLeft <= 0) {
                this.stopCountdown();
                this.handleSessionExpired();
            }
        }, 1000);
    }
    
    stopCountdown() {
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }
    }
    
    async extendSession(autoExtend = false) {
        try {
            const response = await fetch('/api/session/extend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('セッション延長に失敗しました');
            }
            
            const result = await response.json();
            
            // 状態をリセット
            this.warningShown = false;
            this.criticalWarningShown = false;
            this.hideSessionModal();
            
            if (!autoExtend) {
                this.showNotification('セッションを延長しました', 'success');
            }
            
            console.log('セッション延長完了:', result);
            
        } catch (error) {
            console.error('セッション延長エラー:', error);
            this.showNotification('セッション延長に失敗しました', 'error');
        }
    }
    
    async saveSession() {
        try {
            const response = await fetch('/api/session/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('セッション保存に失敗しました');
            }
            
            const result = await response.json();
            
            this.showNotification('現在の進行状況を保存しました', 'success');
            console.log('セッション保存完了:', result);
            
            // バックアップIDをローカルストレージに保存
            if (result.backup_id) {
                const backups = JSON.parse(localStorage.getItem('rccm_session_backups') || '[]');
                backups.unshift({
                    backup_id: result.backup_id,
                    timestamp: new Date().toISOString(),
                    manual: true
                });
                localStorage.setItem('rccm_session_backups', JSON.stringify(backups.slice(0, 10)));
            }
            
        } catch (error) {
            console.error('セッション保存エラー:', error);
            this.showNotification('セッション保存に失敗しました', 'error');
        }
    }
    
    handleSessionExpired() {
        this.stopPeriodicCheck();
        this.hideSessionModal();
        
        // 期限切れ通知を表示
        this.showSessionModal({
            type: 'expired',
            title: 'セッションが期限切れになりました',
            message: '安全のためセッションが期限切れになりました。復元可能なバックアップがある場合は復元できます。',
            buttons: [
                {
                    text: 'セッションを復元',
                    class: 'btn-primary',
                    action: () => this.showRestoreOptions()
                },
                {
                    text: '新しいセッションを開始',
                    class: 'btn-secondary',
                    action: () => window.location.reload()
                }
            ]
        });
    }
    
    async showRestoreOptions() {
        // ローカルストレージとサーバーからバックアップリストを取得
        const localBackups = JSON.parse(localStorage.getItem('rccm_session_backups') || '[]');
        
        if (localBackups.length === 0) {
            this.showNotification('復元可能なバックアップが見つかりません', 'warning');
            return;
        }
        
        const options = localBackups.map(backup => {
            const date = new Date(backup.timestamp).toLocaleString('ja-JP');
            return `<option value="${backup.backup_id}">${date} ${backup.manual ? '(手動保存)' : '(自動保存)'}</option>`;
        }).join('');
        
        const modal = document.createElement('div');
        modal.id = 'restoreModal';
        modal.className = 'modal fade show';
        modal.style.display = 'block';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-history me-2"></i>セッション復元
                        </h5>
                    </div>
                    <div class="modal-body">
                        <p>復元するバックアップを選択してください：</p>
                        <select class="form-select" id="backupSelect">
                            <option value="">バックアップを選択...</option>
                            ${options}
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" id="restoreBtn">復元</button>
                        <button type="button" class="btn btn-secondary" id="cancelBtn">キャンセル</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // イベントリスナーの設定
        document.getElementById('restoreBtn').addEventListener('click', () => {
            const backupId = document.getElementById('backupSelect').value;
            if (backupId) {
                this.restoreSession(backupId);
            }
        });
        
        document.getElementById('cancelBtn').addEventListener('click', () => {
            modal.remove();
        });
    }
    
    async restoreSession(backupId) {
        try {
            const response = await fetch('/api/session/restore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ backup_id: backupId })
            });
            
            if (!response.ok) {
                throw new Error('セッション復元に失敗しました');
            }
            
            const result = await response.json();
            
            this.showNotification('セッションを復元しました', 'success');
            console.log('セッション復元完了:', result);
            
            // ページをリロードして復元されたセッションを適用
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('セッション復元エラー:', error);
            this.showNotification('セッション復元に失敗しました', 'error');
        }
    }
    
    updateSessionStatusUI(status) {
        // セッション状態をページのUIに反映
        const statusElement = document.getElementById('sessionStatus');
        if (statusElement) {
            const minutes = Math.ceil(status.remaining_time / 60);
            statusElement.textContent = `セッション残り時間: ${minutes}分`;
            statusElement.className = status.warning ? 'text-warning' : 'text-muted';
        }
    }
    
    showNotification(message, type = 'info') {
        // トースト通知の表示
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // トーストコンテナを取得または作成
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Bootstrapトーストを初期化
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // 自動削除
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    notifyStatusChange(oldStatus, newStatus) {
        console.log('セッション状態変更:', oldStatus.status, '->', newStatus.status);
        
        // カスタムイベントを発火
        window.dispatchEvent(new CustomEvent('sessionStatusChange', {
            detail: { oldStatus, newStatus }
        }));
    }
    
    setupBeforeUnloadHandler() {
        window.addEventListener('beforeunload', (event) => {
            // セッションが活動中で重要な状態の場合は警告
            if (this.sessionStatus && this.sessionStatus.status === 'active') {
                const examCurrent = parseInt(sessionStorage.getItem('exam_current') || '0');
                if (examCurrent > 0) {
                    event.preventDefault();
                    event.returnValue = '進行中の問題があります。ページを離れると進行状況が失われる可能性があります。';
                }
            }
        });
    }
    
    destroy() {
        this.stopPeriodicCheck();
        this.stopCountdown();
        this.hideSessionModal();
    }
}

// グローバルインスタンス
window.sessionTimeoutManager = null;

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', function() {
    window.sessionTimeoutManager = new SessionTimeoutManager({
        checkInterval: 30000,     // 30秒
        warningThreshold: 300,    // 5分
        criticalThreshold: 60,    // 1分
        autoExtend: true,
        showWarnings: true
    });
});

// ページ離脱時のクリーンアップ
window.addEventListener('beforeunload', function() {
    if (window.sessionTimeoutManager) {
        window.sessionTimeoutManager.destroy();
    }
});