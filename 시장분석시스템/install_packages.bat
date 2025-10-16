@echo off
chcp 65001 > nul
echo ============================================================
echo 📦 시장 분석 시스템 - 패키지 설치
echo ============================================================
echo.

echo Python 버전 확인...
python --version
echo.

echo ============================================================
echo 필수 패키지 설치 시작 (약 5-10분 소요)
echo ============================================================
echo.

echo 설치 진행 중... (인터넷 연결 확인)
echo.

pip install --upgrade pip
pip install yfinance>=0.2.36
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install matplotlib>=3.7.0
pip install plotly>=5.18.0

echo.
echo ============================================================
echo ✅ 패키지 설치 완료!
echo ============================================================
echo.

echo 설치 확인 중...
python -c "import yfinance; print('✅ yfinance 설치 성공')"
python -c "import pandas; print('✅ pandas 설치 성공')"
python -c "import requests; print('✅ requests 설치 성공')"

echo.
echo ============================================================
echo 🚀 이제 quick_start.bat 를 실행하세요!
echo ============================================================
echo.

pause
