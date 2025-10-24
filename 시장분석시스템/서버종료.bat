@echo off
chcp 65001 >nul
cls

echo.
echo ============================================================
echo         🔴 시장 분석 시스템 - 서버 종료
echo ============================================================
echo.

echo [1] Python 프로세스 종료...
taskkill /F /IM python.exe
timeout /t 2 /nobreak >nul

echo.
echo [2] 포트 확인...
netstat -ano | findstr :5003
if errorlevel 1 (
    echo ✅ 서버 정상 종료됨
) else (
    echo ⚠️ 포트 5003이 여전히 사용 중
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5003') do (
        echo    PID %%a 강제 종료...
        taskkill /F /PID %%a
    )
)

echo.
echo ============================================================
echo ✅ 종료 완료
echo ============================================================
echo.
pause
