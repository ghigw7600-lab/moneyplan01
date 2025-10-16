@echo off
chcp 65001 > nul
echo ============================================================
echo 🚀 시장 분석 시스템 - 빠른 시작
echo ============================================================
echo.

echo 📦 패키지 설치 확인 중...
python -c "import yfinance" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️ 필수 패키지가 설치되지 않았습니다!
    echo.
    echo ============================================================
    echo 📌 먼저 패키지를 설치해야 합니다.
    echo ============================================================
    echo.
    echo 다음 중 하나를 선택하세요:
    echo.
    echo 1. install_packages.bat 를 더블클릭하여 실행
    echo 2. 또는 명령 프롬프트에서: pip install -r requirements.txt
    echo.
    echo ============================================================
    echo.
    pause
    exit
)

echo ✅ 패키지 확인 완료!
echo.
echo 시스템을 시작합니다...
echo.
python market_analyzer.py

echo.
pause
