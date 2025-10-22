@echo off
echo ====================================
echo Flask 포트 5001 방화벽 규칙 추가
echo ====================================
echo.
echo 관리자 권한으로 실행 중...
echo.

netsh advfirewall firewall add rule name="Flask 5001 Port" dir=in action=allow protocol=TCP localport=5001

if %errorlevel% equ 0 (
    echo.
    echo ✅ 방화벽 규칙이 성공적으로 추가되었습니다!
    echo.
    echo 이제 다른 기기에서 접속 가능합니다:
    echo http://192.168.219.42:5001
    echo.
) else (
    echo.
    echo ❌ 오류: 관리자 권한이 필요합니다
    echo.
    echo 이 파일을 마우스 오른쪽 버튼으로 클릭하고
    echo "관리자 권한으로 실행"을 선택하세요
    echo.
)

pause
