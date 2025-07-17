@echo off
REM 🔥 ULTRA SYNC タスク3: Windows環境用実行スクリプト
REM 副作用ゼロでアプリケーションを起動

echo 🔥 ULTRA SYNC Windows実行スクリプト
echo ====================================

REM 作業ディレクトリの設定
cd /d "%~dp0"
echo 作業ディレクトリ: %CD%

REM Python環境の設定
set PYTHONPATH=.
set FLASK_ENV=development

REM Pythonコマンドの優先順位テスト
echo.
echo Python環境を検出中...

REM 方法1: python コマンド
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ python コマンドが利用可能
    echo.
    echo 🚀 アプリケーションを起動中...
    python app.py
    goto :end
)

REM 方法2: py コマンド
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ py コマンドが利用可能
    echo.
    echo 🚀 アプリケーションを起動中...
    py app.py
    goto :end
)

REM 方法3: python.exe コマンド
python.exe --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ python.exe コマンドが利用可能
    echo.
    echo 🚀 アプリケーションを起動中...
    python.exe app.py
    goto :end
)

REM 方法4: 一般的なPythonパス
if exist "C:\Python39\python.exe" (
    echo ✅ C:\Python39\python.exe が利用可能
    echo.
    echo 🚀 アプリケーションを起動中...
    "C:\Python39\python.exe" app.py
    goto :end
)

if exist "C:\Python38\python.exe" (
    echo ✅ C:\Python38\python.exe が利用可能
    echo.
    echo 🚀 アプリケーションを起動中...
    "C:\Python38\python.exe" app.py
    goto :end
)

REM すべての方法が失敗した場合
echo ❌ Pythonが見つかりませんでした
echo.
echo 🛠️ 解決方法:
echo 1. Python をインストールしてください (https://python.org)
echo 2. Python を PATH に追加してください
echo 3. または、Python の完全なパスを指定してください
echo.
echo 📋 詳細な診断を実行するには:
echo    python ultrasync_environment_diagnostic.py
echo.

:end
echo.
echo 🔥 ULTRA SYNC 実行スクリプト完了
pause