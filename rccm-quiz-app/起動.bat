@echo off
title RCCM試験問題集2025 - 起動中...
echo.
echo =====================================
echo   RCCM試験問題集2025 Enterprise版
echo =====================================
echo.
echo 起動中です。しばらくお待ちください...
echo.

cd /d "%~dp0"

REM ポート確認と自動選択
set PORT=5003
netstat -an | find ":%PORT%" >nul
if not errorlevel 1 (
    set PORT=5004
    echo ポート5003が使用中のため、ポート5004を使用します。
)

REM Python実行
echo アプリケーションを起動しています...
start "" "python\python.exe" app\app.py

REM 起動待機
timeout /t 3 /nobreak >nul

REM ブラウザを開く
echo ブラウザを開いています...
start "" "http://localhost:%PORT%"

echo.
echo =====================================
echo    起動完了！ブラウザが開きます
echo.
echo    終了時はこのウィンドウを閉じて
echo    ください。
echo =====================================
echo.
pause