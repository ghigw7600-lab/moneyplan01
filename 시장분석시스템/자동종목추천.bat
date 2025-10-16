@echo off
chcp 65001 > nul

echo ============================================================
echo 자동 종목 추천 시스템
echo ============================================================
echo.
echo 코스피/코스닥/가상화폐에서 매수 기회 자동 발견
echo.
echo ============================================================
echo.

REM SSL 인증서 검증 우회
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set PYTHONIOENCODING=utf-8

python auto_recommender.py

pause
