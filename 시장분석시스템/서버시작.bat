@echo off
cls

echo.
echo ============================================================
echo          SERVER START - Market Analysis System
echo ============================================================
echo.

echo [1] Killing existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2] Checking port 5003...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5003') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [3] Starting server...
cd /d "%~dp0web"
start "MarketAnalysisServer" python app.py

timeout /t 5 /nobreak >nul

echo [4] Checking server status...
netstat -ano | findstr :5003 >nul
if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start!
    echo Check logs folder or run python app.py manually
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] Server is running!
echo ============================================================
echo.
echo Open browser and visit:
echo.
echo    http://localhost:5003
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set ip=%%a
    echo    http://%%a:5003
)

echo.
echo ============================================================
echo.
pause
