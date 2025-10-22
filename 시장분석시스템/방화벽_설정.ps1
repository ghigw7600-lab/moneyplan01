# Flask 포트 5001 방화벽 규칙 추가
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Flask 포트 5001 방화벽 규칙 추가" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 기존 규칙 삭제 (있다면)
Write-Host "기존 규칙 확인 중..." -ForegroundColor Yellow
$existingRule = Get-NetFirewallRule -DisplayName "Flask 5001*" -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "기존 규칙 발견. 삭제 중..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "Flask 5001*"
}

# 새 규칙 추가
Write-Host "새 방화벽 규칙 추가 중..." -ForegroundColor Yellow

try {
    New-NetFirewallRule -DisplayName "Flask 5001 Port" `
                        -Direction Inbound `
                        -Protocol TCP `
                        -LocalPort 5001 `
                        -Action Allow `
                        -Profile Any `
                        -Enabled True

    Write-Host ""
    Write-Host "✅ 방화벽 규칙이 성공적으로 추가되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "이제 다른 기기에서 접속 가능합니다:" -ForegroundColor Green
    Write-Host "http://192.168.219.42:5001" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "스마트폰에서 위 주소로 접속해보세요!" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "❌ 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "1. PowerShell을 관리자 권한으로 실행하세요" -ForegroundColor Yellow
    Write-Host "2. 또는 Windows Defender 방화벽 GUI에서 수동 추가하세요" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "아무 키나 누르면 종료됩니다..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
