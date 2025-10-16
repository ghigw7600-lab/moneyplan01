# -*- coding: utf-8 -*-
"""
미국 주식 테스트 - Apple
"""
import sys
import io
import os

# 환경변수 설정 (인증서 문제 우회)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Windows 한글 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("시스템 테스트 (미국 주식 - Apple)")
print("="*60)

# 1. 주식 데이터 수집 테스트
print("\n1. 주식 데이터 수집 테스트...")
from collectors.stock_collector import StockCollector

collector = StockCollector()
data = collector.get_stock_data("AAPL", period="3mo")

if data is not None and not data.empty:
    print(f"OK 데이터 수집 성공! ({len(data)}개 데이터)")
    print(f"   최신 종가: ${data['종가'].iloc[-1]:.2f}")

    # 2. 기술적 분석 테스트
    print("\n2. 기술적 분석 테스트...")
    from analyzers.technical_analyzer import TechnicalAnalyzer

    analyzer = TechnicalAnalyzer(data)
    result = analyzer.analyze_all()

    print(f"OK 기술적 분석 완료!")
    print(f"   RSI: {result['rsi']:.1f}")
    print(f"   추세: {result['trend']['description']}")

    # 3. 감성 분석 테스트
    print("\n3. 감성 분석 테스트...")
    from analyzers.sentiment_analyzer import SentimentAnalyzer

    sentiment_analyzer = SentimentAnalyzer()
    test_news = [
        {'제목': 'Apple stock rises', '설명': 'Strong iPhone sales'},
        {'제목': 'Market positive', '설명': 'Growth expected'},
    ]

    sentiment_result = sentiment_analyzer.analyze_news_list(test_news)
    print(f"OK 감성 분석 완료!")
    print(f"   감성: {sentiment_result['overall_sentiment']}")

    # 4. 신뢰도 계산 테스트
    print("\n4. 신뢰도 계산 테스트...")
    from analyzers.confidence_calculator import ConfidenceCalculator

    calculator = ConfidenceCalculator()
    confidence = calculator.calculate_confidence(result, sentiment_result)

    print(f"OK 신뢰도 계산 완료!")
    print(f"   신뢰도: {confidence['score']}%")
    print(f"   신호: {confidence['signal']}")

    # 5. 보고서 생성 테스트
    print("\n5. 보고서 생성 테스트...")
    from reports.report_generator import ReportGenerator

    generator = ReportGenerator()
    analysis_data = {
        'confidence': confidence,
        'technical': result,
        'sentiment': sentiment_result,
        'company_info': collector.get_company_info("AAPL")
    }

    report_path = generator.generate_html_report("Apple(AAPL)", analysis_data)

    print(f"OK 보고서 생성 완료!")
    print(f"   위치: {report_path}")

    # 최종 결과
    print("\n" + "="*60)
    print("OK 모든 테스트 통과!")
    print("="*60)
    print("\n시스템이 정상적으로 작동합니다!")
    print(f"\n생성된 보고서를 확인하세요:")
    print(f"{os.path.abspath(report_path)}")
    print("\n이제 market_analyzer.py 를 실행하세요!")

else:
    print("ERROR 데이터 수집 실패")
    print("인터넷 연결을 확인하거나 다른 종목 코드를 시도하세요.")
