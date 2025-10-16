# -*- coding: utf-8 -*-
"""
웹 대시보드 테스트
"""
import sys
import io

# Windows 한글 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator

print("="*60)
print("웹 대시보드 백엔드 테스트")
print("="*60)

# 테스트 1: 주식 데이터 수집
print("\n[테스트 1] 삼성전자 데이터 수집")
stock_collector = StockCollector()
ticker = "005930.KS"
print(f"종목: {ticker}")

price_data = stock_collector.get_stock_data(ticker, period='3mo')

if price_data is not None and not price_data.empty:
    print(f"✅ 데이터 수집 성공! ({len(price_data)}개)")
    print(f"컬럼: {price_data.columns.tolist()}")
    print(f"최신 5일:")
    print(price_data.tail())

    # 현재가 확인
    if '종가' in price_data.columns:
        current_price = price_data['종가'].iloc[-1]
        print(f"\n현재가: {current_price:,.0f}원")
    else:
        print(f"\n⚠️ '종가' 컬럼 없음")

    # 기술적 분석
    print("\n[테스트 2] 기술적 분석")
    tech_analyzer = TechnicalAnalyzer(price_data)
    technical_result = tech_analyzer.analyze_all()
    print(f"RSI: {technical_result.get('rsi'):.1f}")
    print(f"추세: {technical_result.get('trend', {}).get('description', 'N/A')}")

    # 신뢰도 계산
    print("\n[테스트 3] 신뢰도 계산")
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_result = sentiment_analyzer.analyze_news_list([])

    calculator = ConfidenceCalculator()
    confidence = calculator.calculate_confidence(technical_result, sentiment_result)
    print(f"신뢰도: {confidence['score']}%")
    print(f"신호: {confidence['signal']}")

    print("\n✅ 모든 테스트 통과!")

else:
    print("❌ 데이터 수집 실패")

# 테스트 4: 가상화폐
print("\n[테스트 4] 비트코인 데이터 수집")
crypto_collector = CryptoCollector()
crypto_data = crypto_collector.get_crypto_data("bitcoin", days=90)

if crypto_data is not None and not crypto_data.empty:
    print(f"✅ 비트코인 데이터 수집 성공! ({len(crypto_data)}개)")
    print(f"컬럼: {crypto_data.columns.tolist()}")
    print(f"최신 5일:")
    print(crypto_data.tail())
else:
    print("❌ 비트코인 데이터 수집 실패 (CoinGecko API 제한일 수 있음)")

print("\n" + "="*60)
print("테스트 완료!")
print("="*60)
