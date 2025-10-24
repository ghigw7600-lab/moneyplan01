# Phase 2 개선 계획: 핫 종목 추천 시스템

**날짜**: 2025-10-24
**목표**: 실시간 트렌드, 뉴스 감성, 경제 이벤트 기반 핫 종목 자동 추천
**예상 기간**: 2-3주
**난이도**: 중상

---

## 📋 **현재 시스템 분석**

### **기존 기능** (`auto_recommender.py`)

✅ **이미 구현됨**:
1. 자동 종목 스캔 (주식 10개 + 가상화폐 10개)
2. RSI 필터링 (20-55 구간)
3. 신뢰도 계산 (최소 60%)
4. 뉴스 감성 분석 (키워드 기반)
5. 추천 근거 제시 (상위 3개)

❌ **부족한 점**:
1. 실시간 트렌드 감지 없음
2. 경제 이벤트 연동 없음
3. 뉴스 감성 분석 약함 (키워드 기반)
4. 웹 UI 통합 없음 (CLI만 존재)
5. 자동 갱신 기능 없음

---

## 🎯 **Phase 2 목표**

### **우선순위 1: 빠른 구현 (1주)**

#### 1. **거래량 급증 감지** ⭐ 최우선
- **현재**: 거래량 체크 없음
- **개선**: 평균 대비 2배 이상 거래량 → 핫 종목 표시
- **구현**:
  ```python
  avg_volume = df['Volume'].rolling(20).mean()
  current_volume = df['Volume'].iloc[-1]
  if current_volume > avg_volume * 2:
      hot_factor += 30  # 핫 점수 +30
  ```

#### 2. **웹 UI 통합** ⭐ 최우선
- **현재**: CLI만 존재
- **개선**:
  - 웹 대시보드에 "핫 종목" 탭 추가
  - 실시간 갱신 (30분마다 자동 스캔)
  - 알림 기능 (새 추천 종목 발견 시)
- **API 엔드포인트**:
  ```
  GET /api/hot-stocks        # 핫 종목 목록
  GET /api/hot-stocks/scan   # 수동 스캔 트리거
  ```

#### 3. **가격 변동률 감지**
- **현재**: RSI만 체크
- **개선**:
  - 1일 변동률 ±5% 이상 → 주목 종목
  - 3일 연속 상승/하락 → 추세 강화
- **핫 점수 산정**:
  ```
  hot_score = (거래량 점수 * 0.4) +
              (RSI 점수 * 0.3) +
              (변동률 점수 * 0.2) +
              (신뢰도 점수 * 0.1)
  ```

---

### **우선순위 2: 중기 구현 (2주)**

#### 4. **뉴스 감성 분석 강화**
- **현재**: 키워드 기반 (긍정/부정 단어 카운트)
- **개선**:
  - Option A: KoBERT/KoELECTRA 모델 (무거움)
  - Option B: 간단한 감성 사전 확장 (빠름)
  - 뉴스 중요도 가중치 (주요 언론사 +20%)

#### 5. **다중 소스 뉴스 수집**
- **현재**: Naver 뉴스만
- **개선**:
  - Google News API
  - 커뮤니티 (Reddit, 뽐뿌, 클리앙)
  - 블로그 (Naver, Tistory)

---

### **우선순위 3: 장기 구현 (3주+)**

#### 6. **경제 이벤트 캘린더**
- **데이터 소스**:
  - Investing.com Economic Calendar API
  - Trading Economics API
  - 한국은행 공공 API
- **이벤트 타입**:
  - APEC, G7, G20 회의
  - 금리 결정 (연준, 한은)
  - 실적 발표 (삼성, 애플 등)
  - GDP, CPI 발표
- **영향도 점수**:
  ```
  high_impact_event: +50 hot_score
  medium_impact_event: +25 hot_score
  low_impact_event: +10 hot_score
  ```

#### 7. **섹터별 추천**
- IT, 바이오, 에너지, 금융 등 섹터별 분류
- 섹터 로테이션 감지
- 섹터 지수와의 상관관계 분석

---

## 🚀 **Phase 2-1 즉시 작업 (오늘 완료 가능)**

### **Task 2-1-1: 거래량 급증 감지 추가**

**파일**: `auto_recommender.py`

**추가 코드**:
```python
def detect_volume_surge(self, price_data):
    """거래량 급증 감지"""
    if 'Volume' not in price_data.columns:
        return False, 0

    avg_volume = price_data['Volume'].rolling(20).mean().iloc[-1]
    current_volume = price_data['Volume'].iloc[-1]

    if current_volume > avg_volume * 2:
        surge_pct = ((current_volume - avg_volume) / avg_volume) * 100
        return True, surge_pct

    return False, 0
```

**통합**:
```python
# scan_korean_stocks() 내부
is_surge, surge_pct = self.detect_volume_surge(price_data)
if is_surge:
    hot_score += 30
    reasons.append(f"거래량 급증 {surge_pct:.0f}%")
```

---

### **Task 2-1-2: 가격 변동률 감지**

**추가 코드**:
```python
def detect_price_momentum(self, price_data):
    """가격 모멘텀 감지 (연속 상승/하락)"""
    recent_closes = price_data['종가'].tail(3).tolist()

    # 3일 연속 상승
    if all(recent_closes[i] < recent_closes[i+1] for i in range(len(recent_closes)-1)):
        return 'uptrend', 20

    # 3일 연속 하락
    if all(recent_closes[i] > recent_closes[i+1] for i in range(len(recent_closes)-1)):
        return 'downtrend', 20

    return 'sideways', 0
```

---

### **Task 2-1-3: 웹 API 엔드포인트 추가**

**파일**: `web/app.py`

**추가 코드**:
```python
from auto_recommender import AutoRecommender

# 전역 변수
hot_stock_recommender = AutoRecommender()

@app.route('/api/hot-stocks', methods=['GET'])
def get_hot_stocks():
    """핫 종목 목록 조회"""
    try:
        # 캐시 확인 (30분 유효)
        cache_file = 'cache/hot_stocks.json'
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < 1800:  # 30분
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))

        # 새로 스캔
        recommendations = hot_stock_recommender.scan_korean_stocks()

        # 캐시 저장
        os.makedirs('cache', exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'recommendations': recommendations,
                'scan_time': datetime.now().isoformat()
            }, f, ensure_ascii=False)

        return jsonify({
            'recommendations': recommendations,
            'scan_time': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hot-stocks/scan', methods=['POST'])
def scan_hot_stocks():
    """핫 종목 수동 스캔"""
    try:
        recommendations = hot_stock_recommender.scan_korean_stocks()
        return jsonify({
            'recommendations': recommendations,
            'scan_time': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### **Task 2-1-4: 웹 UI 추가**

**파일**: `templates/index.html`

**추가 HTML**:
```html
<button class="tab" onclick="showHotStocks()">🔥 핫 종목</button>
```

**추가 JavaScript**:
```javascript
async function showHotStocks() {
    const modal = document.getElementById('hot-stock-modal');
    const listDiv = document.getElementById('hot-stock-list');

    modal.classList.add('show');
    listDiv.innerHTML = '<div class="spinner"></div><p>핫 종목 스캔 중...</p>';

    try {
        const response = await fetch('/api/hot-stocks');
        const result = await response.json();

        if (response.ok && result.recommendations) {
            displayHotStocks(result.recommendations);
        } else {
            listDiv.innerHTML = '<p>핫 종목이 없습니다</p>';
        }
    } catch (error) {
        listDiv.innerHTML = '<p>오류 발생: ' + error.message + '</p>';
    }
}
```

---

## 📊 **Phase 2 전체 로드맵**

| 주차 | 작업 | 난이도 | 상태 |
|------|------|--------|------|
| **1주** | 거래량 급증 감지 | 하 | ⏳ 대기 |
| **1주** | 가격 변동률 감지 | 하 | ⏳ 대기 |
| **1주** | 웹 UI 통합 | 중 | ⏳ 대기 |
| **1주** | 핫 점수 산정 알고리즘 | 중 | ⏳ 대기 |
| **2주** | 뉴스 감성 분석 강화 | 중 | ⏳ 대기 |
| **2주** | 다중 소스 뉴스 수집 | 상 | ⏳ 대기 |
| **3주** | 경제 이벤트 캘린더 | 상 | ⏳ 대기 |
| **3주** | 섹터별 추천 | 중 | ⏳ 대기 |

---

## ✅ **Phase 2-1 체크리스트 (오늘 완료 목표)**

- [ ] `auto_recommender.py`에 거래량 급증 감지 추가
- [ ] `auto_recommender.py`에 가격 변동률 감지 추가
- [ ] `auto_recommender.py`에 핫 점수 산정 로직 추가
- [ ] `web/app.py`에 핫 종목 API 엔드포인트 추가
- [ ] `templates/index.html`에 핫 종목 탭 추가
- [ ] 웹에서 핫 종목 기능 테스트
- [ ] Phase 2-1 완료 보고서 작성

---

**작성자**: Claude
**작성일**: 2025-10-24
**버전**: 1.0
