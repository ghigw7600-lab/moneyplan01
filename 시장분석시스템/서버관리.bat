@echo off
chcp 65001 >nul
:: ============================================================
:: 시장 분석 시스템 - 서버 관리 스크립트
:: ============================================================

setlocal enabledelayedexpansion

:MENU
cls
echo.
echo ============================================================
echo         📊 시장 분석 시스템 - 서버 관리
echo ============================================================
echo.
echo   [1] 🚀 서버 시작 (깔끔한 재시작)
echo   [2] 🔴 서버 종료 (모든 Python 프로세스)
echo   [3] 📊 서버 상태 확인
echo   [4] 📝 로그 보기
echo   [5] 🧹 포트 5003 정리
echo   [6] 🔧 전체 시스템 체크
echo   [0] ❌ 종료
echo.
echo ============================================================
set /p choice=선택 (0-6):

if "%choice%"=="1" goto START_SERVER
if "%choice%"=="2" goto STOP_SERVER
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto VIEW_LOGS
if "%choice%"=="5" goto CLEAN_PORT
if "%choice%"=="6" goto SYSTEM_CHECK
if "%choice%"=="0" goto END
goto MENU

:START_SERVER
echo.
echo [1단계] 기존 Python 프로세스 종료...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2단계] 포트 5003 확인 및 정리...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5003') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [3단계] 서버 시작 중...
cd /d "%~dp0web"
start "시장분석시스템" cmd /k python app.py

timeout /t 5 /nobreak >nul

echo [4단계] 서버 상태 확인...
netstat -ano | findstr :5003
if errorlevel 1 (
    echo ❌ 서버 시작 실패! 로그를 확인하세요.
) else (
    echo.
    echo ============================================================
    echo ✅ 서버 시작 성공!
    echo ============================================================
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
        set ip=%%a
        set ip=!ip:~1!
        echo.
        echo 📊 접속 주소:
        echo    - http://localhost:5003
        echo    - http://!ip!:5003
    )
    echo.
    echo ============================================================
)

pause
goto MENU

:STOP_SERVER
echo.
echo 🔴 모든 Python 프로세스 종료 중...
taskkill /F /IM python.exe
timeout /t 2 /nobreak >nul

echo.
echo ✅ 서버 종료 완료
pause
goto MENU

:CHECK_STATUS
echo.
echo ============================================================
echo         📊 서버 상태
echo ============================================================
echo.
echo [포트 5003 상태]
netstat -ano | findstr :5003
if errorlevel 1 (
    echo ❌ 포트 5003에서 실행 중인 서버 없음
) else (
    echo ✅ 서버 실행 중
)

echo.
echo [실행 중인 Python 프로세스]
tasklist | findstr python.exe
if errorlevel 1 (
    echo ❌ Python 프로세스 없음
)

echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo 📝 로그 디렉토리 열기...
start "" "%~dp0logs"
echo.
echo ✅ 로그 폴더가 열렸습니다.
timeout /t 2 /nobreak >nul
goto MENU

:CLEAN_PORT
echo.
echo 🧹 포트 5003 정리 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5003') do (
    echo PID %%a 종료 중...
    taskkill /F /PID %%a
)
timeout /t 2 /nobreak >nul
echo.
echo ✅ 포트 5003 정리 완료
pause
goto MENU

:SYSTEM_CHECK
echo.
echo ============================================================
echo         🔧 전체 시스템 체크
echo ============================================================
echo.

echo [1] Python 버전 확인
python --version

echo.
echo [2] 필수 패키지 확인
python -c "import flask, pandas, requests; print('✅ 필수 패키지 정상')" 2>nul
if errorlevel 1 (
    echo ❌ 필수 패키지 설치 필요
    echo.
    set /p install=패키지 설치할까요? (Y/N):
    if /i "!install!"=="Y" (
        pip install flask pandas requests yfinance beautifulsoup4
    )
)

echo.
echo [3] 프로젝트 구조 확인
if exist "%~dp0web\app.py" (
    echo ✅ app.py 존재
) else (
    echo ❌ app.py 없음
)

if exist "%~dp0utils\data_normalizer.py" (
    echo ✅ data_normalizer.py 존재
) else (
    echo ❌ data_normalizer.py 없음
)

if exist "%~dp0utils\logger.py" (
    echo ✅ logger.py 존재
) else (
    echo ❌ logger.py 없음
)

echo.
echo [4] 디렉토리 구조
tree /F /A "%~dp0" | more

echo.
pause
goto MENU

:END
echo.
echo 👋 프로그램 종료
timeout /t 2 /nobreak >nul
exit
