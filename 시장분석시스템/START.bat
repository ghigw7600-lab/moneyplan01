@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================================
echo Market Analyzer System
echo ============================================================
echo.

python market_analyzer.py

if errorlevel 1 (
    echo.
    echo ERROR occurred!
    echo.
)

pause
