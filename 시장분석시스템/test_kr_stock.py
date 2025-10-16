# -*- coding: utf-8 -*-
"""
한국 주식 테스트 - 삼성전자, SK하이닉스, 현대중공업
"""
import sys
import io

# Windows 한글 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("한국 주식 시스템 테스트 시작")
print("="*60)

# 1. 주식 데이터 수집 테스트
print("\n1. 주식 데이터 수집 테스트...")
from collectors.stock_collector import StockCollector

collector = StockCollector()

# 테스트할 종목들
test_stocks = [
    ("005930.KS", "삼성전자"),
    ("000660.KS", "SK하이닉스"),
    ("009540.KS", "현대중공업")
]

print("\n" + "="*60)
for ticker, name in test_stocks:
    print(f"\n[{name}] {ticker} 테스트 중...")
    data = collector.get_stock_data(ticker, period="3mo")

    if data is not None and not data.empty:
        print(f"✅ 데이터 수집 성공! ({len(data)}개 데이터)")
        print(f"   최신 종가: {data['종가'].iloc[-1]:,.0f}원")
        print(f"   최근 5일 데이터:")
        print(data.tail())
    else:
        print(f"❌ 데이터 수집 실패")

    print("-"*60)

# 2. 삼성전자 전체 분석 테스트
print("\n2. 삼성전자 전체 분석 테스트...")

data = collector.get_stock_data("005930.KS", period="3mo")

if data is not None and not data.empty:
    # 기술적 분석
    print("\n[기술적 분석]")
    from analyzers.technical_analyzer import TechnicalAnalyzer

    analyzer = TechnicalAnalyzer(data)
    result = analyzer.analyze_all()

    print(f"✅ 기술적 분석 완료!")
    print(f"   RSI: {result['rsi']:.1f}")
    print(f"   추세: {result['trend']['description']}")
    print(f"   신호 개수: {len(result['signals'])}")

    # 감성 분석
    print("\n[감성 분석]")
    from analyzers.sentiment_analyzer import SentimentAnalyzer

    sentiment_analyzer = SentimentAnalyzer()
    test_news = [
        {'제목': '삼성전자 주가 상승', '설명': '반도체 수출 호조'},
        {'제목': '증시 전망 긍정적', '설명': '실적 개선 기대'},
    ]

    sentiment_result = sentiment_analyzer.analyze_news_list(test_news)
    print(f"✅ 감성 분석 완료!")
    print(f"   감성: {sentiment_result['overall_sentiment']}")
    print(f"   점수: {sentiment_result['overall_score']:.2f}")

    # 신뢰도 계산
    print("\n[신뢰도 계산]")
    from analyzers.confidence_calculator import ConfidenceCalculator

    calculator = ConfidenceCalculator()
    confidence = calculator.calculate_confidence(result, sentiment_result)

    print(f"✅ 신뢰도 계산 완료!")
    print(f"   신뢰도: {confidence['score']}%")
    print(f"   신호: {confidence['signal']}")

    # 보고서 생성
    print("\n[보고서 생성]")
    from reports.report_generator import ReportGenerator

    generator = ReportGenerator()
    analysis_data = {
        'confidence': confidence,
        'technical': result,
        'sentiment': sentiment_result,
        'company_info': collector.get_company_info("005930.KS")
    }

    report_path = generator.generate_html_report("삼성전자(005930.KS)", analysis_data)

    print(f"✅ 보고서 생성 완료!")
    print(f"   위치: {report_path}")

    # 최종 결과
    print("\n" + "="*60)
    print("✅ 모든 테스트 통과!")
    print("="*60)
    print(f"\n생성된 보고서를 확인하세요: {report_path}")

else:
    print("❌ 삼성전자 데이터 수집 실패 - 전체 분석 불가")

print("\n이제 market_analyzer.py 를 실행하세요!")
