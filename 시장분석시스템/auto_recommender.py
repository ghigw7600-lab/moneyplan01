# -*- coding: utf-8 -*-
"""
자동 종목 추천 엔진
코스피/코스닥/가상화폐에서 매수 기회 자동 발견
"""
import sys
import io
from datetime import datetime
import time

# Windows 한글 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from collectors.naver_news_collector import NaverNewsCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator


class AutoRecommender:
    """자동 종목 추천기"""

    def __init__(self):
        self.stock_collector = StockCollector()
        self.crypto_collector = CryptoCollector()
        self.news_collector = NaverNewsCollector()
        self.sentiment_analyzer = SentimentAnalyzer()

        # 추천 기준
        self.min_confidence = 60  # 최소 신뢰도 60% (완화)
        self.min_rsi = 20  # RSI 20 이하 (과매도)
        self.max_rsi = 55  # RSI 55 이하 (중립~약간 과매수)

    def scan_korean_stocks(self, stock_list=None):
        """
        한국 주식 스캔

        Args:
            stock_list (list): 스캔할 종목 리스트 (None이면 기본 종목)

        Returns:
            list: 추천 종목 리스트
        """
        if stock_list is None:
            # 기본 스캔 대상 (주요 종목)
            stock_list = [
                ('005930.KS', '삼성전자'),
                ('000660.KS', 'SK하이닉스'),
                ('035420.KS', 'NAVER'),
                ('035720.KQ', '카카오'),
                ('373220.KS', 'LG에너지솔루션'),
                ('005380.KS', '현대차'),
                ('207940.KS', '삼성바이오로직스'),
                ('006400.KS', '삼성SDI'),
                ('051910.KS', 'LG화학'),
                ('068270.KS', '셀트리온')
            ]

        recommendations = []

        print(f"\n{'='*60}")
        print(f"📊 한국 주식 스캔 시작 ({len(stock_list)}개 종목)")
        print(f"{'='*60}\n")

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

                rsi = technical_result.get('rsi')

                # RSI 필터링 (과매도 구간만)
                if rsi is None or rsi > self.max_rsi:
                    print(f"   ⏭️  RSI {rsi:.1f} - 건너뜀")
                    continue

                # 뉴스 감성 분석
                news_list = self.news_collector.get_news(name, max_count=10)
                sentiment_result = self.sentiment_analyzer.analyze_news_list(news_list)

                # 신뢰도 계산
                calculator = ConfidenceCalculator()
                confidence = calculator.calculate_confidence(technical_result, sentiment_result)

                # 추천 기준 충족 여부
                if confidence['score'] >= self.min_confidence and confidence['signal'] in ['buy', 'strong_buy']:
                    current_price = price_data['종가'].iloc[-1]

                    recommendations.append({
                        'ticker': ticker,
                        'name': name,
                        'current_price': current_price,
                        'confidence': confidence['score'],
                        'signal': confidence['signal'],
                        'rsi': rsi,
                        'reasons': confidence['reasons'][:3],  # 상위 3개
                        'scan_time': datetime.now()
                    })

                    print(f"   ✅ 추천! 신뢰도 {confidence['score']}%, RSI {rsi:.1f}")
                else:
                    print(f"   ❌ 기준 미달 (신뢰도 {confidence['score']}%, RSI {rsi:.1f})")

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
