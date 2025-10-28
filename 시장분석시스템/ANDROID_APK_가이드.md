# 📱 머니플랜01 Android APK 생성 가이드

PWA → APK 변환으로 완전 독립 Android 앱 만들기!

---

## 🎯 방법: PWABuilder 사용 (가장 쉬움!)

**소요 시간**: 30분~1시간
**난이도**: ⭐ (매우 쉬움)
**비용**: 무료

---

## 📋 준비물

### 1. 머니플랜01을 인터넷에 배포 (필수!)

PWABuilder는 **인터넷 URL**이 필요합니다.

**옵션 A: Render.com 배포 (추천, 무료)**

이미 `render.yaml` 파일이 있으므로:

1. https://render.com 가입
2. GitHub 저장소 연결
3. 자동 배포 완료!
4. HTTPS URL 획득 (예: https://moneyplan01.onrender.com)

**소요 시간**: 10분

**옵션 B: Netlify, Vercel 등**

같은 방식으로 배포 가능

---

## 🚀 PWABuilder로 APK 생성

### 1단계: PWABuilder 접속

https://www.pwabuilder.com

### 2단계: URL 입력

```
머니플랜01 배포 URL 입력
예: https://moneyplan01.onrender.com
```

**[Start]** 버튼 클릭

### 3단계: 분석 대기

PWABuilder가 자동으로 분석:
- manifest.json 확인
- Service Worker 확인
- PWA 점수 계산

**예상 시간**: 10~30초

### 4단계: Android 패키지 생성

**화면 하단** → **[Android]** 탭 클릭

**옵션 선택**:
- Package ID: `com.moneyplan01.app`
- App name: `머니플랜01`
- App version: `1.0.0`
- Host: (자동 입력됨)

**[Generate]** 버튼 클릭

### 5단계: APK 다운로드

**두 가지 옵션**:

#### 옵션 A: Signed APK (권장)
- Google Play Store 업로드 가능
- 서명 필요 (PWABuilder가 자동 생성)

#### 옵션 B: Unsigned APK (테스트용)
- 즉시 다운로드
- 설치 가능 (개발자 모드 필요)

**다운로드**: `moneyplan01.apk` (약 10~30MB)

---

## 📲 APK 설치 방법

### Android에서 APK 설치

#### 방법 1: 카카오톡으로 전송

1. APK 파일을 카카오톡으로 자신에게 전송
2. Android 폰에서 파일 다운로드
3. 파일 탭 클릭 → 설치

#### 방법 2: USB 케이블

1. Android 폰을 PC에 USB 연결
2. APK 파일을 폰 내부 저장소로 복사
3. 파일 관리자에서 APK 파일 클릭 → 설치

#### 방법 3: Google Drive / OneDrive

1. 클라우드에 APK 업로드
2. Android 폰에서 다운로드
3. 설치

### 출처 모르는 앱 설치 허용

Android는 기본적으로 Google Play 외 앱 설치 차단

**해제 방법**:
1. 설정 → 보안
2. "출처 모르는 앱 설치" 허용
3. 또는 설치 시 팝업에서 "이 출처 허용" 선택

**안전**: 본인이 만든 앱이므로 안전합니다!

---

## ✨ APK 설치 후

### 앱 아이콘

홈 화면 또는 앱 서랍에 **머니플랜01** 아이콘 생성!

### 완전 독립 앱

- ✅ 브라우저 없이 실행
- ✅ 앱처럼 보임 (주소창 없음)
- ✅ 오프라인 모드 지원
- ✅ 빠른 속도

### 주의사항

**인터넷 연결 필요**:
- APK는 WebView 기반
- 실제 데이터는 서버(Render.com)에서 가져옴
- 오프라인 시 캐시된 데이터만 표시

---

## 🎨 커스터마이징

### 앱 아이콘 변경

PWABuilder에서:
1. **Customize** 탭 클릭
2. Icon 업로드 (512x512 PNG)
3. 다시 Generate

### 스플래시 화면

manifest.json 수정:
```json
{
  "background_color": "#667eea",
  "theme_color": "#667eea"
}
```

### 앱 이름 변경

PWABuilder Package ID 입력 시 원하는 이름 입력

---

## 📤 친구들에게 배포

### 방법 1: 카카오톡으로 전송

**장점**: 가장 쉬움
**단점**: 파일 용량 제한 (100MB)

### 방법 2: Google Drive 링크

1. Google Drive에 APK 업로드
2. 공유 링크 생성
3. 링크 전송

**장점**: 용량 제한 없음

### 방법 3: QR 코드

1. APK를 OneDrive/Drive 업로드
2. QR 코드 생성 (https://www.qr-code-generator.com/)
3. QR 코드 이미지 공유
4. 친구들이 스캔 → 다운로드 → 설치

---

## 🔄 업데이트 방법

### 앱 업데이트 시

1. 서버(Render.com)만 업데이트
2. APK 재생성 불필요!
3. 사용자는 앱 재설치 불필요!

**왜?**
→ APK는 껍데기일 뿐, 실제 내용은 서버에서 로딩

### APK 자체 업데이트 (기능 추가 시)

1. PWABuilder에서 재생성
2. 버전 번호 증가 (1.0.0 → 1.1.0)
3. 새 APK 배포
4. 사용자는 기존 앱 제거 후 재설치

---

## ⚠️ 제약사항

### Google Play Store 등록

**본인 + 지인 전용**이므로:
- Play Store 등록 불필요
- 등록하려면 Google 개발자 계정 필요 ($25)

### iOS 앱

iOS는 APK 설치 불가능!
- iOS는 PWA 방식 유지 (Safari 홈 화면 추가)
- 또는 React Native로 완전 재작성 필요

### 오프라인 제한

완전 오프라인 앱을 원한다면:
- React Native + SQLite로 재작성 필요
- 현재는 인터넷 연결 필수

---

## 🎯 대안: 더 쉬운 방법

### Trusted Web Activity (TWA)

PWABuilder 대신:

**Bubblewrap CLI** 사용:
```bash
npm install -g @bubblewrap/cli
bubblewrap init --manifest https://moneyplan01.onrender.com/static/manifest.json
bubblewrap build
```

**장점**: 더 커스터마이징 가능
**단점**: 명령어 입력 필요

---

## 📊 비교: PWA vs APK

| 항목 | PWA (현재) | APK (PWABuilder) |
|------|-----------|-----------------|
| 설치 | 브라우저에서 | APK 파일 |
| 아이콘 | 홈 화면 | 앱 서랍 |
| 업데이트 | 자동 | 수동 |
| 배포 | URL 공유 | APK 파일 전송 |
| 느낌 | 웹앱 | 네이티브 앱 |
| 오프라인 | 제한적 | 제한적 (동일) |

**결론**: APK가 더 "앱 같음"

---

## 💡 추천 워크플로우

### PC 사용자
→ Electron .exe 파일

### Android 사용자
→ PWABuilder APK

### iPhone 사용자
→ PWA (Safari 홈 화면 추가)

### 모두에게 한 번에
→ 카카오톡으로 각각 전송!

---

## 📝 체크리스트

APK 생성 전 확인:

- [ ] 머니플랜01 서버 배포 완료 (Render.com 등)
- [ ] HTTPS URL 획득
- [ ] manifest.json 정상 작동 확인
- [ ] Service Worker 등록 확인
- [ ] PWABuilder 접속
- [ ] Android 패키지 생성
- [ ] APK 다운로드
- [ ] 테스트 설치 완료

---

**작성일**: 2025-10-28
**버전**: Phase 6 - Android APK 가이드
**대상**: 본인 및 지인 전용
**다음 단계**: Render.com 배포 → PWABuilder → APK 생성!
