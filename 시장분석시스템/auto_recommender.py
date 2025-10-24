# -*- coding: utf-8 -*-
"""
자동 종목 추천 엔진
코스피/코스닥/가상화폐에서 매수 기회 자동 발견
"""
import sys
import io
from datetime import datetime
import time
import pandas as pd

# Windows 한글 출력 문제 해결 (__main__일 때만)
if __name__ == "__main__" and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except ValueError:
        pass

from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from collectors.naver_news_collector import NaverNewsCollector
from collectors.google_news_collector import GoogleNewsCollector
from collectors.economic_event_collector import EconomicEventCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator


class AutoRecommender:
    """자동 종목 추천기 (Phase 2-2, 2-3 통합)"""

    def __init__(self):
        self.stock_collector = StockCollector()
        self.crypto_collector = CryptoCollector()
        self.news_collector = NaverNewsCollector()
        self.google_news_collector = GoogleNewsCollector()  # Phase 2-2
        self.event_collector = EconomicEventCollector()      # Phase 2-3
        self.sentiment_analyzer = SentimentAnalyzer()

        # 추천 기준
        self.min_confidence = 60  # 최소 신뢰도 60% (완화)
        self.min_rsi = 20  # RSI 20 이하 (과매도)
        self.max_rsi = 70  # RSI 70 이하 (과매수 직전까지 허용)

    def detect_volume_surge(self, price_data):
        """
        거래량 급증 감지

        Args:
            price_data: 가격 데이터 (DataFrame)

        Returns:
            tuple: (급증 여부, 급증 퍼센트, 핫 점수)
        """
        try:
            # Volume 컬럼 확인
            volume_col = None
            for col in ['Volume', '거래량', 'volume']:
                if col in price_data.columns:
                    volume_col = col
                    break

            if volume_col is None or price_data[volume_col].iloc[-1] == 0:
                return False, 0, 0

            # 20일 평균 거래량
            avg_volume = price_data[volume_col].rolling(window=20).mean().iloc[-1]
            current_volume = price_data[volume_col].iloc[-1]

            if avg_volume == 0 or pd.isna(avg_volume):
                return False, 0, 0

            # 급증률 계산
            surge_pct = ((current_volume - avg_volume) / avg_volume) * 100

            # 2배 이상 급증 시
            if current_volume > avg_volume * 2:
                hot_score = min(50, surge_pct / 2)  # 최대 50점
                return True, surge_pct, hot_score

            # 1.5배 이상 급증 시
            elif current_volume > avg_volume * 1.5:
                hot_score = min(30, surge_pct / 3)  # 최대 30점
                return True, surge_pct, hot_score

            return False, surge_pct, 0

        except Exception as e:
            print(f"   ⚠️ 거래량 분석 오류: {str(e)}")
            return False, 0, 0

    def detect_price_momentum(self, price_data):
        """
        가격 모멘텀 감지 (연속 상승/하락)

        Args:
            price_data: 가격 데이터 (DataFrame)

        Returns:
            tuple: (모멘텀 타입, 핫 점수, 설명)
        """
        try:
            # 종가 컬럼 확인
            close_col = None
            for col in ['Close', '종가', 'close']:
                if col in price_data.columns:
                    close_col = col
                    break

            if close_col is None:
                return 'none', 0, '데이터 없음'

            # 최근 5일 종가
            recent_closes = price_data[close_col].tail(5).tolist()

            if len(recent_closes) < 3:
                return 'none', 0, '데이터 부족'

            # 5일 연속 상승
            if all(recent_closes[i] < recent_closes[i+1] for i in range(len(recent_closes)-1)):
                return 'strong_uptrend', 40, '5일 연속 상승'

            # 4일 연속 상승
            if all(recent_closes[i] < recent_closes[i+1] for i in range(len(recent_closes)-2)):
                return 'uptrend', 30, '4일 연속 상승'

            # 3일 연속 상승
            if all(recent_closes[-3+i] < recent_closes[-3+i+1] for i in range(2)):
                return 'uptrend', 20, '3일 연속 상승'

            # 3일 연속 하락 (반등 기회)
            if all(recent_closes[-3+i] > recent_closes[-3+i+1] for i in range(2)):
                return 'downtrend', 10, '3일 연속 하락 (반등 기회)'

            return 'sideways', 0, '횡보'

        except Exception as e:
            print(f"   ⚠️ 모멘텀 분석 오류: {str(e)}")
            return 'none', 0, '분석 실패'

    def calculate_hot_score(self, technical_result, sentiment_result, volume_surge_score, momentum_score, confidence_score, event_impact_score=0):
        """
        핫 점수 산정 (Phase 2-3: 경제 이벤트 반영)

        Args:
            technical_result: 기술적 분석 결과
            sentiment_result: 감성 분석 결과
            volume_surge_score: 거래량 급증 점수
            momentum_score: 모멘텀 점수
            confidence_score: 신뢰도 점수
            event_impact_score: 경제 이벤트 영향 점수 (0-20)

        Returns:
            int: 핫 점수 (0-100)
        """
        # 가중치 적용
        hot_score = (
            volume_surge_score * 0.35 +      # 거래량 35%
            momentum_score * 0.25 +          # 모멘텀 25%
            (confidence_score / 100 * 40) +  # 신뢰도 40% (100점 만점을 40점으로 변환)
            0  # 추가 점수 여유
        )

        # RSI 보너스 (과매도 구간)
        rsi = technical_result.get('rsi', 50)
        if rsi < 30:
            hot_score += 15  # 강한 과매도 보너스
        elif rsi < 40:
            hot_score += 10  # 중간 과매도 보너스

        # 감성 분석 보너스
        sentiment = sentiment_result.get('overall_sentiment', 'neutral')
        if sentiment == 'positive':
            hot_score += 10
        elif sentiment == 'negative':
            hot_score -= 5

        # 경제 이벤트 영향 (Phase 2-3)
        hot_score += event_impact_score  # 최대 +20점

        # 0-100 범위 제한
        return max(0, min(100, int(hot_score)))

    def scan_korean_stocks(self, stock_list=None):
        """
        한국 주식 스캔

        Args:
            stock_list (list): 스캔할 종목 리스트 (None이면 기본 종목)

        Returns:
            list: 추천 종목 리스트
        """
        if stock_list is None:
            # 기본 스캔 대상 (주요 종목 + 중소형주)
            stock_list = [
                # 대형주
                ('005930.KS', '삼성전자'),
                ('000660.KS', 'SK하이닉스'),
                ('035420.KS', 'NAVER'),
                ('035720.KQ', '카카오'),
                ('373220.KS', 'LG에너지솔루션'),
                ('005380.KS', '현대차'),
                ('207940.KS', '삼성바이오로직스'),
                ('006400.KS', '삼성SDI'),
                ('051910.KS', 'LG화학'),
                ('068270.KS', '셀트리온'),
                # 중형주
                ('003670.KS', '포스코퓨처엠'),
                ('096770.KS', 'SK이노베이션'),
                ('086520.KS', '에코프로'),
                ('247540.KS', '에코프로비엠'),
                ('042700.KS', '한미반도체'),
                ('058470.KS', '리노공업'),
                ('000270.KS', '기아'),
                ('012330.KS', '현대모비스'),
                ('066570.KS', 'LG전자'),
                ('028260.KS', '삼성물산'),
                # 테마주 (2차전지, AI, 반도체)
                ('091990.KS', '셀트리온헬스케어'),
                ('326030.KS', 'SK바이오팜'),
                ('348210.KQ', '넥스틴'),
                ('357780.KS', '솔브레인'),
                ('361610.KS', 'SK아이이테크놀로지')
            ]

        recommendations = []

        print(f"\n{'='*60}")
        print(f"📊 한국 주식 스캔 시작 ({len(stock_list)}개 종목)")
        print(f"{'='*60}\n")

        # Phase 2-3: 향후 30일간의 경제 이벤트 조회
        print(f"📅 경제 이벤트 캘린더 로딩 중...")
        try:
            all_events = self.event_collector.get_upcoming_events(days=30)
            print(f"   ✅ {len(all_events)}개 경제 이벤트 확인 완료\n")
        except Exception as e:
            print(f"   ⚠️ 경제 이벤트 로딩 실패: {str(e)}")
            all_events = []

        for ticker, name in stock_list:
            try:
                print(f"🔍 {name} ({ticker}) 분석 중...")

                # 데이터 수집
                price_data = self.stock_collector.get_stock_data(ticker, period='3mo')
                if price_data is None or price_data.empty:
                    print(f"   ⚠️ 데이터 없음")
                    continue

                # 기술적 분석
                tech_analyzer = TechnicalAnalyzer(price_data)
                technical_result = tech_analyzer.analyze_all()

                rsi = technical_result.get('rsi', 50)

                # 거래량 급증 감지
                is_surge, surge_pct, volume_score = self.detect_volume_surge(price_data)

                # 가격 모멘텀 감지
                momentum_type, momentum_score, momentum_desc = self.detect_price_momentum(price_data)

                # 다중 소스 뉴스 수집 (Phase 2-2)
                naver_news = self.news_collector.get_news(name, max_count=10)
                # Google News는 시간이 오래 걸릴 수 있으므로 옵션으로 처리
                # google_news = self.google_news_collector.get_news(name, max_count=5, language='ko')
                # all_news = naver_news + google_news
                news_list = naver_news  # 일단 네이버만 사용 (속도 우선)

                sentiment_result = self.sentiment_analyzer.analyze_news_list(news_list)

                # Phase 2-3: 종목 관련 경제 이벤트 필터링
                event_impact_score = 0
                relevant_events = []
                try:
                    if all_events:
                        relevant_events = self.event_collector.filter_events_by_stock(
                            all_events, name, ticker
                        )

                        if relevant_events:
                            # 가장 중요한 이벤트의 영향도 계산
                            top_event = max(relevant_events,
                                          key=lambda e: self.event_collector.get_event_impact_score(e))
                            impact_score = self.event_collector.get_event_impact_score(top_event)
                            # 최대 +20점으로 제한 (영향도 100점 → 20점으로 스케일링)
                            event_impact_score = min(20, impact_score / 5)
                except Exception as e:
                    print(f"   ⚠️ 이벤트 필터링 오류: {str(e)}")

                # 신뢰도 계산
                calculator = ConfidenceCalculator()
                confidence = calculator.calculate_confidence(technical_result, sentiment_result)

                # 핫 점수 계산 (Phase 2-3: 이벤트 영향 반영)
                hot_score = self.calculate_hot_score(
                    technical_result,
                    sentiment_result,
                    volume_score,
                    momentum_score,
                    confidence['score'],
                    event_impact_score  # Phase 2-3
                )

                # 추천 기준 충족 여부 (핫 점수 15 이상 또는 기존 신뢰도 45 이상)
                if hot_score >= 15 or (confidence['score'] >= 45 and confidence['signal'] in ['buy', 'strong_buy']):
                    current_price = price_data['종가'].iloc[-1]

                    # 추천 근거에 핫 요인 추가
                    hot_reasons = []
                    if is_surge:
                        hot_reasons.append({
                            'category': '거래량',
                            'reason': f'거래량 {surge_pct:.0f}% 급증',
                            'impact': '상'
                        })
                    if momentum_type in ['strong_uptrend', 'uptrend']:
                        hot_reasons.append({
                            'category': '모멘텀',
                            'reason': momentum_desc,
                            'impact': '상' if momentum_type == 'strong_uptrend' else '중'
                        })

                    # Phase 2-3: 경제 이벤트 추가
                    if relevant_events and event_impact_score > 0:
                        top_event = max(relevant_events,
                                      key=lambda e: self.event_collector.get_event_impact_score(e))
                        event_date = top_event['date'][:10] if isinstance(top_event['date'], str) else top_event['date'].strftime('%Y-%m-%d')
                        hot_reasons.append({
                            'category': '이벤트',
                            'reason': f'{event_date} {top_event["name"]}',
                            'impact': '상' if event_impact_score >= 15 else '중'
                        })

                    all_reasons = hot_reasons + confidence['reasons'][:3]

                    recommendations.append({
                        'ticker': ticker,
                        'name': name,
                        'current_price': current_price,
                        'confidence': confidence['score'],
                        'signal': confidence['signal'],
                        'rsi': rsi,
                        'hot_score': hot_score,  # 핫 점수 추가
                        'is_hot': hot_score >= 70,  # 70점 이상이면 "HOT" 표시
                        'reasons': all_reasons[:5],  # 상위 5개
                        'scan_time': datetime.now()
                    })

                    hot_emoji = '🔥' if hot_score >= 70 else '✅'
                    print(f"   {hot_emoji} 추천! 핫점수 {hot_score}, 신뢰도 {confidence['score']}%, RSI {rsi:.1f}")
                    if is_surge:
                        print(f"      💹 거래량 {surge_pct:.0f}% 급증!")
                    if momentum_type in ['strong_uptrend', 'uptrend']:
                        print(f"      📈 {momentum_desc}")
                    if relevant_events and event_impact_score > 0:
                        print(f"      📅 경제 이벤트 영향 +{event_impact_score:.1f}점 ({len(relevant_events)}개 관련 이벤트)")
                else:
                    print(f"   ❌ 기준 미달 (핫점수 {hot_score}, 신뢰도 {confidence['score']}%, RSI {rsi:.1f})")

                # 요청 간 딜레이
                time.sleep(1)

            except Exception as e:
                print(f"   ❌ 오류: {str(e)}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ 스캔 완료: {len(recommendations)}개 종목 추천")
        print(f"{'='*60}\n")

        return recommendations

    def scan_cryptocurrencies(self, coin_list=None):
        """
        가상화폐 스캔

        Args:
            coin_list (list): 스캔할 코인 리스트 (None이면 상위 50개)

        Returns:
            list: 추천 코인 리스트
        """
        if coin_list is None:
            # 시가총액 상위 50개 코인
            coin_list = [
                ('bitcoin', 'Bitcoin'),
                ('ethereum', 'Ethereum'),
                ('binancecoin', 'Binance Coin'),
                ('ripple', 'XRP'),
                ('cardano', 'Cardano'),
                ('solana', 'Solana'),
                ('polkadot', 'Polkadot'),
                ('dogecoin', 'Dogecoin'),
                ('avalanche-2', 'Avalanche'),
                ('chainlink', 'Chainlink')
            ]

        recommendations = []

        print(f"\n{'='*60}")
        print(f"🪙 가상화폐 스캔 시작 ({len(coin_list)}개 코인)")
        print(f"{'='*60}\n")

        for coin_id, coin_name in coin_list:
            try:
                print(f"🔍 {coin_name} ({coin_id}) 분석 중...")

                # 데이터 수집
                price_data = self.crypto_collector.get_crypto_data(coin_id, days=90)
                if price_data is None or price_data.empty:
                    print(f"   ⚠️ 데이터 없음")
                    continue

                # 기술적 분석
                tech_analyzer = TechnicalAnalyzer(price_data)
                technical_result = tech_analyzer.analyze_all()

                rsi = technical_result.get('rsi')

                # RSI 필터링
                if rsi is None or rsi > self.max_rsi:
                    print(f"   ⏭️  RSI {rsi:.1f} - 건너뜀")
                    continue

                # 감성 분석 (간단한 분석)
                sentiment_result = {
                    'overall_sentiment': 'neutral',
                    'overall_score': 0.5,
                    'positive_count': 0,
                    'negative_count': 0
                }

                # 신뢰도 계산
                calculator = ConfidenceCalculator()
                confidence = calculator.calculate_confidence(technical_result, sentiment_result)

                # 추천 기준
                if confidence['score'] >= self.min_confidence and confidence['signal'] in ['buy', 'strong_buy']:
                    current_price = price_data['종가'].iloc[-1]

                    recommendations.append({
                        'ticker': coin_id,
                        'name': coin_name,
                        'current_price': current_price,
                        'confidence': confidence['score'],
                        'signal': confidence['signal'],
                        'rsi': rsi,
                        'reasons': confidence['reasons'][:3],
                        'scan_time': datetime.now()
                    })

                    print(f"   ✅ 추천! 신뢰도 {confidence['score']}%, RSI {rsi:.1f}")
                else:
                    print(f"   ❌ 기준 미달 (신뢰도 {confidence['score']}%, RSI {rsi:.1f})")

                # CoinGecko API 제한 방지 (무료 API는 분당 10-30 요청)
                time.sleep(3)

            except Exception as e:
                print(f"   ❌ 오류: {str(e)}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ 스캔 완료: {len(recommendations)}개 코인 추천")
        print(f"{'='*60}\n")

        return recommendations

    def display_recommendations(self, recommendations):
        """추천 결과 출력"""
        if not recommendations:
            print("\n⚠️ 추천할 종목이 없습니다.")
            print("   (현재 시장 상황에서는 매수 신호가 없습니다)")
            return

        print(f"\n{'='*60}")
        print(f"🎯 추천 종목 ({len(recommendations)}개)")
        print(f"{'='*60}\n")

        # 신뢰도 순으로 정렬
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        for i, rec in enumerate(recommendations, 1):
            print(f"[{i}] {rec['name']} ({rec['ticker']})")
            print(f"   💰 현재가: {rec['current_price']:,.2f}")
            print(f"   🎯 신뢰도: {rec['confidence']}%")
            print(f"   📊 RSI: {rec['rsi']:.1f}")
            print(f"   📈 신호: {rec['signal']}")
            print(f"   🔍 주요 근거:")
            for reason in rec['reasons']:
                print(f"      • {reason.get('reason', '')}")
            print()


# 메인 실행
if __name__ == "__main__":
    recommender = AutoRecommender()

    print("="*60)
    print("🚀 자동 종목 추천 시스템")
    print("="*60)
    print("\n1. 한국 주식 스캔")
    print("2. 가상화폐 스캔")
    print("3. 전체 스캔 (주식 + 가상화폐)")
    print()

    choice = input("선택 (1-3): ").strip()

    if choice == '1':
        recommendations = recommender.scan_korean_stocks()
        recommender.display_recommendations(recommendations)

    elif choice == '2':
        recommendations = recommender.scan_cryptocurrencies()
        recommender.display_recommendations(recommendations)

    elif choice == '3':
        print("\n=== 주식 스캔 ===")
        stock_recs = recommender.scan_korean_stocks()

        print("\n=== 가상화폐 스캔 ===")
        crypto_recs = recommender.scan_cryptocurrencies()

        all_recs = stock_recs + crypto_recs
        recommender.display_recommendations(all_recs)

    else:
        print("❌ 잘못된 선택입니다.")

    input("\n\nEnter를 눌러 종료...")
