// RCCM試験問題集2025 - Google Sites版 JavaScript

// グローバル変数
let currentUser = '';
let selectedDepartment = '';
let selectedType = '';
let questions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let startTime = null;
let userProgress = {};

// ローカルストレージキー
const STORAGE_KEYS = {
    USER_PROGRESS: 'rccm_user_progress',
    CURRENT_SESSION: 'rccm_current_session',
    BOOKMARKS: 'rccm_bookmarks'
};

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    loadUserProgress();
    initializeApp();
});

// アプリ初期化
function initializeApp() {
    console.log('RCCM試験問題集2025 - Google Sites版 初期化完了');
    
    // Service Worker登録（オフライン対応）
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then(registration => console.log('SW registered:', registration))
            .catch(error => console.log('SW registration failed:', error));
    }
}

// 学習開始
function startLearning() {
    const userName = document.getElementById('userName').value.trim();
    
    if (!userName) {
        alert('お名前を入力してください');
        return;
    }
    
    if (userName.length > 20) {
        alert('お名前は20文字以内で入力してください');
        return;
    }
    
    currentUser = userName;
    
    // ユーザー進捗の初期化または読み込み
    if (!userProgress[currentUser]) {
        userProgress[currentUser] = {
            totalAnswered: 0,
            correctCount: 0,
            streakDays: 0,
            lastStudyDate: null,
            departmentProgress: {}
        };
    }
    
    saveUserProgress();
    updateProgressDisplay();
    
    // 画面切り替え
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('departmentSection').style.display = 'block';
    
    console.log(`ユーザー "${currentUser}" でログイン`);
}

// 部門選択
function selectDepartment(department) {
    selectedDepartment = department;
    
    // 視覚的フィードバック
    document.querySelectorAll('#departmentSection .feature-card').forEach(card => {
        card.classList.remove('border-primary', 'bg-primary', 'text-white');
    });
    
    event.currentTarget.classList.add('border-primary', 'bg-primary', 'text-white');
    
    // 問題種別選択画面を表示
    setTimeout(() => {
        document.getElementById('typeSection').style.display = 'block';
        document.getElementById('typeSection').scrollIntoView({ behavior: 'smooth' });
    }, 300);
    
    console.log(`部門選択: ${department}`);
}

// 問題種別選択
function selectType(type) {
    selectedType = type;
    
    // 視覚的フィードバック
    document.querySelectorAll('#typeSection .feature-card').forEach(card => {
        card.classList.remove('border-success', 'bg-success', 'text-white');
    });
    
    event.currentTarget.classList.add('border-success', 'bg-success', 'text-white');
    
    // 問題データ読み込み
    setTimeout(() => {
        loadQuestions(selectedDepartment, selectedType);
    }, 300);
    
    console.log(`問題種別選択: ${type}`);
}

// 問題データ読み込み
async function loadQuestions(department, type) {
    try {
        // questions.json から実際のデータを読み込み
        const response = await fetch('data/questions.json');
        const allQuestions = await response.json();
        
        // 条件に応じてフィルタリング
        let filteredQuestions = allQuestions.filter(q => {
            if (type === 'basic') {
                return q.type === 'basic';
            } else if (type === 'specialist') {
                return q.type === 'specialist';
            }
            return true;
        });
        
        // 専門問題の場合、部門でさらにフィルタリング（現在は全て含む）
        if (type === 'specialist' && department !== 'all') {
            // 実際の部門フィルタリングは、より多くの専門データが利用可能になったら実装
            console.log(`部門 ${department} の専門問題をフィルタリング予定`);
        }
        
        if (filteredQuestions.length === 0) {
            alert('該当する問題データが見つかりませんでした');
            return;
        }
        
        // 問題をシャッフル
        questions = shuffleArray(filteredQuestions);
        
        // 最大10問に制限
        questions = questions.slice(0, 10);
        
        console.log(`問題データ読み込み完了: ${questions.length}問 (総数: ${allQuestions.length}問)`);
        
        // 問題開始
        startQuiz();
        
    } catch (error) {
        console.error('問題データ読み込みエラー:', error);
        
        // フォールバック: サンプルデータを生成
        console.log('サンプルデータにフォールバック');
        questions = generateSampleQuestions(department, type);
        questions = shuffleArray(questions).slice(0, 10);
        startQuiz();
    }
}

// サンプル問題生成（実際のデータ読み込み実装まで）
function generateSampleQuestions(department, type) {
    const sampleQuestions = [];
    const questionCount = 10;
    
    const departments = {
        'road': '道路',
        'river': '河川',
        'sabo': '砂防',
        'steel': '鋼構造',
        'tunnel': 'トンネル',
        'construction': '施工管理',
        'machinery': '機械',
        'port': '港湾空港'
    };
    
    const types = {
        'basic': '基礎',
        'specialist': '専門'
    };
    
    for (let i = 1; i <= questionCount; i++) {
        sampleQuestions.push({
            id: `${department}_${type}_${i}`,
            question: `${departments[department]}部門 ${types[type]}問題 第${i}問: 次のうち、最も適切なものはどれか。`,
            options: {
                A: `選択肢A - ${departments[department]}に関する記述`,
                B: `選択肢B - ${types[type]}技術についての説明`,
                C: `選択肢C - 正解となる内容の記述`,
                D: `選択肢D - 誤った内容の記述`
            },
            correctAnswer: 'C',
            explanation: `正解はCです。${departments[department]}部門の${types[type]}問題では、この点が重要なポイントとなります。`,
            department: department,
            type: type,
            difficulty: Math.floor(Math.random() * 3) + 1 // 1-3の難易度
        });
    }
    
    return sampleQuestions;
}

// 配列シャッフル
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// 問題開始
function startQuiz() {
    currentQuestionIndex = 0;
    userAnswers = [];
    startTime = new Date();
    
    // 画面切り替え
    document.getElementById('departmentSection').style.display = 'none';
    document.getElementById('typeSection').style.display = 'none';
    document.getElementById('quizSection').style.display = 'block';
    
    // 最初の問題を表示
    displayQuestion();
    
    console.log('問題開始');
}

// 問題表示
function displayQuestion() {
    const question = questions[currentQuestionIndex];
    
    if (!question) {
        showResults();
        return;
    }
    
    // 問題情報更新
    document.getElementById('questionCounter').textContent = `問題 ${currentQuestionIndex + 1}/${questions.length}`;
    document.getElementById('categoryBadge').textContent = question.type === 'basic' ? '基礎問題' : '専門問題';
    
    // 進捗バー更新
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    document.getElementById('quizProgress').style.width = `${progress}%`;
    
    // 問題文と選択肢表示
    document.getElementById('questionText').textContent = question.question;
    document.getElementById('optionA').textContent = question.options.A;
    document.getElementById('optionB').textContent = question.options.B;
    document.getElementById('optionC').textContent = question.options.C;
    document.getElementById('optionD').textContent = question.options.D;
    
    // ボタン状態リセット
    document.querySelectorAll('#optionsContainer button').forEach(btn => {
        btn.classList.remove('btn-success', 'btn-danger', 'btn-primary');
        btn.classList.add('btn-outline-primary');
        btn.disabled = false;
    });
    
    // 次の問題ボタン無効化
    document.getElementById('nextButton').disabled = true;
    
    // 回答結果非表示
    document.getElementById('answerResult').style.display = 'none';
    
    console.log(`問題 ${currentQuestionIndex + 1} 表示`);
}

// 回答選択
function selectAnswer(selectedOption) {
    const question = questions[currentQuestionIndex];
    const isCorrect = selectedOption === question.correctAnswer;
    
    // 回答記録
    userAnswers.push({
        questionId: question.id,
        selectedAnswer: selectedOption,
        correctAnswer: question.correctAnswer,
        isCorrect: isCorrect,
        timestamp: new Date()
    });
    
    // ボタン状態更新
    document.querySelectorAll('#optionsContainer button').forEach(btn => {
        btn.disabled = true;
        const option = btn.onclick.toString().match(/'([A-D])'/)[1];
        
        if (option === question.correctAnswer) {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-success');
        } else if (option === selectedOption && !isCorrect) {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-danger');
        }
    });
    
    // 結果表示
    showAnswerResult(isCorrect, question);
    
    // 次の問題ボタン有効化
    document.getElementById('nextButton').disabled = false;
    
    // 進捗更新
    updateUserProgress(isCorrect);
    
    console.log(`回答選択: ${selectedOption} (正解: ${question.correctAnswer})`);
}

// 回答結果表示
function showAnswerResult(isCorrect, question) {
    const resultDiv = document.getElementById('answerResult');
    const alertDiv = document.getElementById('resultAlert');
    const resultText = document.getElementById('resultText');
    const explanationText = document.getElementById('explanationText');
    
    if (isCorrect) {
        alertDiv.className = 'alert alert-success';
        resultText.innerHTML = '<i class="fas fa-check-circle me-2"></i>正解です！';
    } else {
        alertDiv.className = 'alert alert-danger';
        resultText.innerHTML = '<i class="fas fa-times-circle me-2"></i>不正解です';
    }
    
    explanationText.textContent = question.explanation;
    resultDiv.style.display = 'block';
    
    // スムーズスクロール
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 次の問題へ
function nextQuestion() {
    currentQuestionIndex++;
    
    if (currentQuestionIndex >= questions.length) {
        showResults();
    } else {
        displayQuestion();
    }
}

// ブックマーク
function bookmarkQuestion() {
    const question = questions[currentQuestionIndex];
    let bookmarks = JSON.parse(localStorage.getItem(STORAGE_KEYS.BOOKMARKS) || '[]');
    
    if (!bookmarks.includes(question.id)) {
        bookmarks.push(question.id);
        localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(bookmarks));
        
        // 視覚的フィードバック
        const btn = event.currentTarget;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> 追加済み';
        btn.classList.add('btn-success');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-success');
        }, 1500);
        
        console.log(`問題 ${question.id} をブックマークに追加`);
    }
}

// 結果表示
function showResults() {
    const endTime = new Date();
    const timeElapsed = Math.round((endTime - startTime) / 1000 / 60); // 分
    
    const correctAnswers = userAnswers.filter(answer => answer.isCorrect).length;
    const totalQuestions = userAnswers.length;
    const accuracy = Math.round((correctAnswers / totalQuestions) * 100);
    
    // 結果更新
    document.getElementById('finalScore').textContent = `${correctAnswers}/${totalQuestions}`;
    document.getElementById('finalAccuracy').textContent = `${accuracy}%`;
    document.getElementById('finalTime').textContent = `${timeElapsed}分`;
    
    // 画面切り替え
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
    
    // 進捗保存
    saveQuizResult(correctAnswers, totalQuestions, accuracy, timeElapsed);
    
    console.log(`問題完了: ${correctAnswers}/${totalQuestions} (${accuracy}%)`);
}

// ユーザー進捗更新
function updateUserProgress(isCorrect) {
    if (!userProgress[currentUser]) return;
    
    userProgress[currentUser].totalAnswered++;
    if (isCorrect) {
        userProgress[currentUser].correctCount++;
    }
    
    // 連続学習日数更新
    const today = new Date().toDateString();
    const lastStudy = userProgress[currentUser].lastStudyDate;
    
    if (lastStudy !== today) {
        if (lastStudy && isConsecutiveDay(lastStudy, today)) {
            userProgress[currentUser].streakDays++;
        } else {
            userProgress[currentUser].streakDays = 1;
        }
        userProgress[currentUser].lastStudyDate = today;
    }
    
    saveUserProgress();
    updateProgressDisplay();
}

// 連続日判定
function isConsecutiveDay(lastDate, currentDate) {
    const last = new Date(lastDate);
    const current = new Date(currentDate);
    const diffTime = current - last;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays === 1;
}

// 進捗表示更新
function updateProgressDisplay() {
    const progress = userProgress[currentUser];
    if (!progress) return;
    
    const accuracy = progress.totalAnswered > 0 
        ? Math.round((progress.correctCount / progress.totalAnswered) * 100) 
        : 0;
    
    document.getElementById('totalAnswered').textContent = progress.totalAnswered;
    document.getElementById('correctCount').textContent = progress.correctCount;
    document.getElementById('accuracyRate').textContent = `${accuracy}%`;
    document.getElementById('streakDays').textContent = progress.streakDays;
    
    // 進捗円グラフ更新
    const progressPercent = Math.min(progress.totalAnswered / 100 * 100, 100); // 100問で100%
    document.getElementById('progressPercent').textContent = `${Math.round(progressPercent)}%`;
    
    const circle = document.getElementById('progressCircle');
    const circumference = 2 * Math.PI * 45; // r=45
    const offset = circumference - (progressPercent / 100) * circumference;
    circle.style.strokeDashoffset = offset;
}

// 問題結果保存
function saveQuizResult(correct, total, accuracy, time) {
    const result = {
        date: new Date().toISOString(),
        department: selectedDepartment,
        type: selectedType,
        correct: correct,
        total: total,
        accuracy: accuracy,
        time: time,
        answers: userAnswers
    };
    
    let results = JSON.parse(localStorage.getItem('rccm_quiz_results') || '[]');
    results.push(result);
    
    // 最大100件まで保存
    if (results.length > 100) {
        results = results.slice(-100);
    }
    
    localStorage.setItem('rccm_quiz_results', JSON.stringify(results));
}

// ユーザー進捗保存
function saveUserProgress() {
    localStorage.setItem(STORAGE_KEYS.USER_PROGRESS, JSON.stringify(userProgress));
}

// ユーザー進捗読み込み
function loadUserProgress() {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PROGRESS);
    userProgress = stored ? JSON.parse(stored) : {};
}

// 問題再開始
function restartQuiz() {
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('typeSection').style.display = 'block';
    
    // 選択状態リセット
    document.querySelectorAll('.feature-card').forEach(card => {
        card.classList.remove('border-primary', 'bg-primary', 'text-white', 'border-success', 'bg-success');
    });
    
    selectedDepartment = '';
    selectedType = '';
}

// ホームに戻る
function goHome() {
    location.reload();
}

// ヘルプ表示
function showHelp() {
    alert(`RCCM試験問題集2025 - Google Sites版

【基本操作】
1. お名前を入力して学習開始
2. 専門部門を選択
3. 問題種別(基礎/専門)を選択
4. 10問の問題に挑戦

【機能】
• 進捗管理: 学習状況を自動保存
• ブックマーク: 重要な問題を保存
• オフライン対応: インターネット接続不要
• レスポンシブ: PC/スマホ/タブレット対応

【データ】
• 基礎問題: 202問
• 専門問題: 3,681問
• 総計: 3,883問

困ったことがあれば、管理者にお問い合わせください。`);
}

// エラーハンドリング
window.addEventListener('error', function(e) {
    console.error('アプリケーションエラー:', e.error);
});

// オフライン/オンライン検知
window.addEventListener('online', function() {
    console.log('オンラインに復帰しました');
});

window.addEventListener('offline', function() {
    console.log('オフラインモードに切り替わりました');
});

console.log('RCCM試験問題集2025 - Google Sites版 JavaScript読み込み完了');