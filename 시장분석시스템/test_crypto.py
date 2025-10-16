# -*- coding: utf-8 -*-
"""
암호화폐 테스트 - Bitcoin
"""
import sys
import io
import os

# Windows 한글 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("시스템 테스트 (암호화폐 - Bitcoin)")
print("="*60)

# 1. 암호화폐 데이터 수집 테스트
print("\n1. 암호화폐 데이터 수집 테스트...")
from collectors.crypto_collector import CryptoCollector

collector = CryptoCollector()
data = collector.get_crypto_data("bitcoin", days=90)

if data is not None and not data.empty:
    print(f"OK 데이터 수집 성공! ({len(data)}개 데이터)")
    print(f"   최신 가격: ${data['가격'].iloc[-1]:,.2f}")

    # 암호화폐 데이터를 OHLCV 형식으로 변환
    data_ohlcv = data.copy()
    data_ohlcv['종가'] = data_ohlcv['가격']
    data_ohlcv['고가'] = data_ohlcv['가격']
    data_ohlcv['저가'] = data_ohlcv['가격']
    data_ohlcv['시가'] = data_ohlcv['가격']

    # 2. 기술적 분석 테스트
    print("\n2. 기술적 분석 테스트...")
    from analyzers.technical_analyzer import TechnicalAnalyzer

    analyzer = TechnicalAnalyzer(data_ohlcv)
    result = analyzer.analyze_all()

    print(f"OK 기술적 분석 완료!")
    print(f"   RSI: {result['rsi']:.1f}")
    print(f"   추세: {result['trend']['description']}")
    print(f"   신호: {len(result['signals'])}개")

    # 3. 감성 분석 테스트
    print("\n3. 감성 분석 테스트...")
    from analyzers.sentiment_analyzer import SentimentAnalyzer

    sentiment_analyzer = SentimentAnalyzer()
    test_news = [
        {'제목': 'Bitcoin price rises', '설명': 'Strong demand'},
        {'제목': 'Crypto market positive', '설명': 'Growth expected'},
        {'제목': 'BTC breaks resistance', '설명': 'New high'},
    ]

    sentiment_result = sentiment_analyzer.analyze_news_list(test_news)
    print(f"OK 감성 분석 완료!")
    print(f"   감성: {sentiment_result['overall_sentiment']}")
    print(f"   점수: {sentiment_result['overall_score']:.2f}")

    # 4. 신뢰도 계산 테스트
    print("\n4. 신뢰도 계산 테스트...")
    from analyzers.confidence_calculator import ConfidenceCalculator

    calculator = ConfidenceCalculator()
    confidence = calculator.calculate_confidence(result, sentiment_result)

    print(f"OK 신뢰도 계산 완료!")
    print(f"   신뢰도: {confidence['score']}%")
    print(f"   신호: {confidence['signal']}")
    print(f"   근거 수: {len(confidence['reasons'])}개")

    # 5. 보고서 생성 테스트
    print("\n5. 보고서 생성 테스트...")
    from reports.report_generator import ReportGenerator

    generator = ReportGenerator()
    coin_info = collector.get_coin_info("bitcoin")

    analysis_data = {
        'confidence': confidence,
        'technical': result,
        'sentiment': sentiment_result,
        'company_info': coin_info
    }

    report_path = generator.generate_html_report("Bitcoin(BTC)", analysis_data)

    print(f"OK 보고서 생성 완료!")
    print(f"   위치: {report_path}")

    # 최종 결과
    print("\n" + "="*60)
    print("SUCCESS 모든 테스트 통과!")
    print("="*60)
    print("\n시스템이 정상적으로 작동합니다!")
    print(f"\n생성된 보고서:")
    print(f"  {os.path.abspath(report_path)}")
    print("\n브라우저에서 보고서를 확인하세요!")

    # 브라우저에서 자동으로 열기
    import webbrowser
    webbrowser.open(os.path.abspath(report_path))

    print("\n이제 market_analyzer.py 를 실행하세요!")
    print("  python market_analyzer.py")

else:
    print("ERROR 데이터 수집 실패")
    print("인터넷 연결을 확인하세요.")
