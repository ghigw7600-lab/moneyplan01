@echo off
chcp 65001 > nul

echo ============================================================
echo AI 시장 분석 시스템 - 웹 대시보드
echo ============================================================
echo.

REM SSL 인증서 검증 우회
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"

echo 웹 서버 시작 중...
echo.
echo 브라우저에서 접속하세요:
echo.
echo   http://localhost:5000
echo.
echo 종료하려면 Ctrl+C를 누르세요
echo.
echo ============================================================
echo.

python web\app.py

pause
