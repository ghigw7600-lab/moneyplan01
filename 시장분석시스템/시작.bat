@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================================
echo 시장 분석 시스템
echo ============================================================
echo.

REM SSL 인증서 검증 우회
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set PYTHONIOENCODING=utf-8

python market_analyzer.py

echo.
pause
