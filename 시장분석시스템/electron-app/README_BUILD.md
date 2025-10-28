# 🖥️ 머니플랜01 데스크톱 앱 빌드 가이드

완전 독립 실행 파일 (.exe)로 만들기!

---

## 🚀 빌드 준비 (한 번만)

### 1. Node.js 설치 확인

```bash
node --version
npm --version
```

**없다면?** → https://nodejs.org/ 에서 다운로드 (LTS 버전)

### 2. Electron 의존성 설치

```bash
cd "C:\Users\기광우\OneDrive\Desktop\기광우 업무\AI\시장분석시스템\electron-app"
npm install
```

**설치되는 것들**:
- electron (Chromium 기반 데스크톱 앱 프레임워크)
- electron-builder (Windows .exe 빌더)

**예상 시간**: 3~5분 (인터넷 속도에 따라)
**용량**: ~200MB

---

## 🎨 아이콘 준비 (선택)

**Windows .exe 아이콘**을 만들려면:

1. 256x256 PNG 이미지 준비
2. 온라인 변환기 사용: https://converticon.com/
3. `icon.ico` 파일 생성
4. `electron-app` 폴더에 저장

**없어도 됩니다!** → 기본 Electron 아이콘 사용

---

## 💻 개발 모드 실행 (테스트용)

### 앱 실행해보기

```bash
cd "C:\Users\기광우\OneDrive\Desktop\기광우 업무\AI\시장분석시스템\electron-app"
npm start
```

**동작**:
1. Python Flask 서버 자동 시작
2. Electron 윈도우 열림
3. 3초 로딩 화면
4. 머니플랜01 실행!

**종료**: 윈도우 닫기 또는 `Ctrl + C`

---

## 📦 Windows .exe 파일 빌드

### 단일 실행 파일 생성

```bash
cd "C:\Users\기광우\OneDrive\Desktop\기광우 업무\AI\시장분석시스템\electron-app"
npm run build-win
```

**빌드 시간**: 5~10분 (첫 빌드 시)

**생성 위치**:
```
electron-app/dist/머니플랜01 Setup 1.0.0.exe
```

**파일 크기**: 약 150~200MB

### 설치 프로그램

생성된 **머니플랜01 Setup 1.0.0.exe**를 실행하면:
1. 설치 위치 선택
2. 바탕화면 바로가기 생성
3. 시작 메뉴 등록
4. 설치 완료!

---

## 📤 친구들에게 배포

### 방법 1: 설치 프로그램 전달

**파일**:
```
머니플랜01 Setup 1.0.0.exe (약 150MB)
```

**전달 방법**:
- 카카오톡 (파일 용량 제한 주의)
- Google Drive / OneDrive 링크
- USB

**설치**: 실행 파일 더블클릭 → 설치 완료!

### 방법 2: 포터블 버전 (설치 없이 실행)

**electron-builder 설정 변경 필요**:

`package.json`의 `build.win.target`을 `"portable"`로 변경:
```json
"win": {
  "target": "portable"
}
```

재빌드 시 **포터블 .exe** 생성 (설치 없이 바로 실행)

---

## ⚠️ 주의사항

### Python 서버 포함 여부

**현재 설정**: Python 서버는 **포함되지 않음**
- 사용자 PC에 Python 설치 필요
- 모든 의존성 (yfinance 등) 설치 필요

### 완전 독립 앱으로 만들려면?

**옵션 1: PyInstaller로 Python → .exe**
```bash
cd "C:\Users\기광우\OneDrive\Desktop\기광우 업무\AI\시장분석시스템\web"
pyinstaller --onefile --hidden-import yfinance app.py
```

생성된 `app.exe`를 `electron-app` 폴더에 복사하고,
`main.js`에서 Python 대신 `app.exe` 실행

**옵션 2: 클라우드 서버 사용**
- Render.com에 배포
- Electron 앱은 클라우드 URL 로딩
- Python 설치 불필요!

---

## 🐛 트러블슈팅

### 문제 1: "npm이 인식되지 않습니다"

**해결**: Node.js 재설치 후 터미널 재시작

### 문제 2: 빌드 실패 - "electron-builder not found"

**해결**:
```bash
npm install electron-builder --save-dev
```

### 문제 3: 앱 실행 시 Python 오류

**해결**:
1. Python 설치 확인
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

### 문제 4: 로딩 화면에서 멈춤

**해결**:
1. Python 서버가 실행 중인지 확인
2. http://localhost:5003 브라우저에서 직접 접속 테스트
3. `main.js`의 `setTimeout` 시간 늘리기 (3000 → 5000)

---

## 🎯 다음 단계

### 클라우드 배포 + Electron 조합

**최고의 조합**:
1. Python 서버 → Render.com 배포 (무료)
2. Electron → 클라우드 URL 로딩
3. 사용자는 Python 설치 불필요!

**장점**:
- ✅ 설치 파일 용량 작음 (80MB 이하)
- ✅ 업데이트 쉬움 (서버만 업데이트)
- ✅ 모든 PC에서 동작

---

## 📋 명령어 요약

```bash
# 의존성 설치 (한 번만)
npm install

# 개발 모드 실행
npm start

# Windows .exe 빌드
npm run build-win

# 빌드 결과 확인
dir dist
```

---

**작성일**: 2025-10-28
**버전**: Phase 6 - Electron 데스크톱 앱
**대상**: 본인 및 지인 전용
