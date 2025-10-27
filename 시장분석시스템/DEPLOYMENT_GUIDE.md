# 머니플랜01 배포 가이드
## Phase 4: Render.com 클라우드 배포

---

## 🚀 **5분 만에 배포하기**

### **1단계: Render.com 계정 생성 (1분)**

1. https://render.com 접속
2. **"Get Started"** 클릭
3. **GitHub 계정으로 로그인** (추천)
   - 또는 이메일로 회원가입

---

### **2단계: GitHub 저장소 연결 (2분)**

1. Render 대시보드에서 **"New +"** 클릭
2. **"Web Service"** 선택
3. **"Connect GitHub"** 클릭
4. **저장소 선택**: `ghigw7600-lab/moneyplan01`
5. **"Connect"** 클릭

---

### **3단계: 배포 설정 (2분)**

Render가 `render.yaml` 파일을 자동으로 감지합니다!

**자동 설정된 항목들**:
- ✅ Name: `moneyplan01`
- ✅ Region: `Singapore` (한국과 가장 가까움)
- ✅ Branch: `main`
- ✅ Build Command: `pip install -r requirements.txt`
- ✅ Start Command: `gunicorn --chdir web --bind 0.0.0.0:$PORT app:app...`
- ✅ Plan: **Free** (무료!)

**"Create Web Service"** 클릭!

---

### **4단계: 배포 완료 대기 (5-10분)**

Render가 자동으로:
1. ✅ 코드 다운로드
2. ✅ Python 패키지 설치
3. ✅ 서버 시작
4. ✅ HTTPS 인증서 발급
5. ✅ 도메인 할당

**배포 로그 확인**:
```
Building...
Installing dependencies...
Starting server...
✅ Deployment successful!
```

---

## 🎉 **배포 완료!**

### **접속 URL**

```
https://moneyplan01.onrender.com
```

**또는**:
```
https://moneyplan01-[랜덤문자열].onrender.com
```

---

## 📱 **PWA 테스트**

### **모바일에서**:

1. **Chrome/Safari에서 접속**
2. **"홈 화면에 추가"** 팝업 표시됨
3. **추가** 클릭
4. **홈 화면에 아이콘 생성됨!**

### **PWA 기능 확인**:
- ✅ 오프라인 모드 (비행기 모드에서 테스트)
- ✅ 백그라운드 알림 (목표가 설정)
- ✅ 전체화면 모드 (주소창 없음)
- ✅ 빠른 로딩 (캐시 사용)

---

## ⚙️ **환경 설정 (선택)**

### **커스텀 도메인 연결**

1. Render 대시보드 → **"Settings"**
2. **"Custom Domain"** 섹션
3. **도메인 입력**: `투자분석.com`
4. DNS 설정 (Render가 안내)
5. **자동 HTTPS 적용** ✅

### **환경 변수 추가**

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://... (향후 추가 시)
```

---

## 🔧 **배포 후 설정**

### **1. 자동 배포 설정**

✅ 이미 설정됨!

```
Git push → GitHub → Render 자동 배포
```

**테스트**:
```bash
git add .
git commit -m "테스트 배포"
git push origin main
```

→ Render가 자동으로 재배포!

### **2. 로그 확인**

Render 대시보드 → **"Logs"** 탭
- 실시간 서버 로그 확인
- 에러 디버깅

### **3. 모니터링**

**무료 플랜 제한**:
- ✅ 750시간/월 무료 (항상 켜짐)
- ⏸️ 15분 동안 접속 없으면 절전 모드
  - 다시 접속 시 자동 깨어남 (10-30초 소요)

---

## 🆙 **업그레이드 옵션**

### **유료 플랜 비교**

| 기능 | Free | Starter ($7/월) |
|------|------|-----------------|
| 절전 모드 | 15분 후 | 없음 (항상 켜짐) |
| 메모리 | 512MB | 1GB |
| CPU | 공유 | 전용 |
| 대역폭 | 100GB/월 | 무제한 |
| 커스텀 도메인 | ✅ | ✅ |
| HTTPS | ✅ | ✅ |

**추천**: 월 사용자 100명 이상이면 Starter 플랜

---

## 🐛 **트러블슈팅**

### **문제 1: 배포 실패**

**원인**: Python 패키지 설치 오류

**해결**:
```bash
# requirements.txt 확인
cat requirements.txt

# 로컬에서 테스트
pip install -r requirements.txt
```

### **문제 2: 서버 시작 실패**

**원인**: Port 설정 오류

**해결**: `render.yaml` 확인
```yaml
startCommand: "gunicorn --bind 0.0.0.0:$PORT ..."
```

### **문제 3: 느린 응답**

**원인**: 절전 모드에서 깨어남 (무료 플랜)

**해결**:
- 유료 플랜 업그레이드
- 또는 주기적으로 핑 (UptimeRobot 사용)

---

## 📊 **배포 체크리스트**

배포 전 확인:
- [x] `requirements.txt` 생성됨
- [x] `render.yaml` 생성됨
- [x] GitHub에 푸시됨
- [x] Service Worker 작동 확인
- [x] PWA Manifest 확인

배포 후 확인:
- [ ] HTTPS 접속 가능
- [ ] 홈 화면 추가 동작
- [ ] Service Worker 등록됨
- [ ] 오프라인 모드 동작
- [ ] 백그라운드 알림 동작

---

## 🎯 **다음 단계**

1. **사용자 피드백 수집** (1주)
   - 베타 테스터 모집
   - 버그 수정

2. **성능 최적화** (1주)
   - 데이터베이스 추가 (PostgreSQL)
   - Redis 캐시 추가
   - CDN 설정

3. **마케팅 시작** (진행 중)
   - 한국투자커뮤니티 홍보
   - 블로그/유튜브 콘텐츠
   - SEO 최적화

4. **수익화 시스템** (Phase 5)
   - 프리미엄 구독 추가
   - 결제 시스템 (Stripe)
   - 광고 통합

---

## 💡 **유용한 링크**

- **Render 대시보드**: https://dashboard.render.com
- **Render 문서**: https://render.com/docs
- **GitHub 저장소**: https://github.com/ghigw7600-lab/moneyplan01
- **PWA 체크리스트**: https://web.dev/pwa-checklist/

---

## 📞 **지원**

문제가 발생하면:
1. Render 로그 확인
2. GitHub Issues 생성
3. Render 지원팀 문의

---

**🎉 축하합니다! 이제 전 세계 어디서나 접속 가능한 앱이 되었습니다!**
