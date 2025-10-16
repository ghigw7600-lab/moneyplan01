@echo off
chcp 65001 > nul

echo ====================================================
echo 시스템 테스트 실행
echo ====================================================
echo.

REM SSL 인증서 검증 우회
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set PYTHONIOENCODING=utf-8

python test_us_stock.py

pause
