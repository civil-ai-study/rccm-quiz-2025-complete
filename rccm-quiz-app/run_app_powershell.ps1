# 🔥 ULTRA SYNC タスク3: PowerShell用実行スクリプト
# 副作用ゼロでアプリケーションを起動

Write-Host "🔥 ULTRA SYNC PowerShell実行スクリプト" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# 作業ディレクトリの設定
Set-Location -Path $PSScriptRoot
Write-Host "作業ディレクトリ: $(Get-Location)" -ForegroundColor Cyan

# Python環境の設定
$env:PYTHONPATH = "."
$env:FLASK_ENV = "development"

Write-Host ""
Write-Host "Python環境を検出中..." -ForegroundColor Yellow

# 関数: Pythonコマンドのテスト
function Test-PythonCommand {
    param([string]$Command)
    
    try {
        $result = & $Command --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Command が利用可能: $result" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # コマンドが見つからない場合
    }
    
    Write-Host "❌ $Command は利用できません" -ForegroundColor Red
    return $false
}

# 関数: アプリケーションの起動
function Start-Application {
    param([string]$PythonCommand)
    
    Write-Host ""
    Write-Host "🚀 アプリケーションを起動中..." -ForegroundColor Green
    Write-Host "コマンド: $PythonCommand app.py" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        & $PythonCommand app.py
    }
    catch {
        Write-Host "❌ アプリケーションの起動に失敗しました: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Pythonコマンドの優先順位テスト
$pythonCommands = @("python", "py", "python.exe", "python3")

foreach ($cmd in $pythonCommands) {
    if (Test-PythonCommand -Command $cmd) {
        Start-Application -PythonCommand $cmd
        Write-Host ""
        Write-Host "🔥 ULTRA SYNC 実行スクリプト完了" -ForegroundColor Green
        exit 0
    }
}

# 一般的なPythonパスをテスト
$commonPaths = @(
    "C:\Python39\python.exe",
    "C:\Python38\python.exe",
    "C:\Python37\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python39\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python38\python.exe"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "✅ $path が利用可能" -ForegroundColor Green
        Start-Application -PythonCommand $path
        Write-Host ""
        Write-Host "🔥 ULTRA SYNC 実行スクリプト完了" -ForegroundColor Green
        exit 0
    }
}

# すべての方法が失敗した場合
Write-Host ""
Write-Host "❌ Pythonが見つかりませんでした" -ForegroundColor Red
Write-Host ""
Write-Host "🛠️ 解決方法:" -ForegroundColor Yellow
Write-Host "1. Python をインストールしてください (https://python.org)" -ForegroundColor White
Write-Host "2. Python を PATH に追加してください" -ForegroundColor White
Write-Host "3. または、Python の完全なパスを指定してください" -ForegroundColor White
Write-Host ""
Write-Host "📋 詳細な診断を実行するには:" -ForegroundColor Yellow
Write-Host "   python ultrasync_environment_diagnostic.py" -ForegroundColor White
Write-Host ""
Write-Host "🔥 ULTRA SYNC 実行スクリプト完了" -ForegroundColor Green

# PowerShell実行ポリシーの確認
Write-Host ""
Write-Host "💡 PowerShell実行ポリシーの確認:" -ForegroundColor Yellow
Write-Host "   Get-ExecutionPolicy" -ForegroundColor White
Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White