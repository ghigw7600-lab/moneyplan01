# -*- coding: utf-8 -*-
"""
시장 분석 시스템 - 메인 실행 파일
주식/암호화폐 종합 분석 및 보고서 생성
"""

import os
import sys
from datetime import datetime

# 모듈 임포트
from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from collectors.news_collector import NewsCollector, SimpleNewsCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator
from reports.report_generator import ReportGenerator
from config import NEWS_API_KEY


class MarketAnalyzer:
    """시장 분석 시스템"""

    def __init__(self):
        print("=" * 60)
        print("🚀 시장 분석 시스템 시작")
        print("=" * 60)

        self.stock_collector = StockCollector()
        self.crypto_collector = CryptoCollector()

        # 뉴스 수집기 (API 키 유무에 따라)
        if NEWS_API_KEY:
            self.news_collector = NewsCollector(NEWS_API_KEY)
        else:
            print("⚠️ NEWS_API_KEY 미설정 - 뉴스 분석 제한됨")
            self.news_collector = SimpleNewsCollector()

        self.sentiment_analyzer = SentimentAnalyzer()
        self.confidence_calculator = ConfidenceCalculator()
        self.report_generator = ReportGenerator()

    def analyze_stock(self, ticker, company_name=None):
        """
        주식 종목 분석

        Args:
            ticker (str): 종목 코드 (예: "005930.KS", "AAPL")
            company_name (str): 회사명 (뉴스 검색용)

        Returns:
            dict: 종합 분석 결과
        """
        print(f"\n{'='*60}")
        print(f"📊 {ticker} 분석 시작")
        print(f"{'='*60}\n")

        # 1. 주식 데이터 수집
        print("1️⃣ 데이터 수집 단계")
        stock_data = self.stock_collector.get_stock_data(ticker, period="1y")
        if stock_data is None or stock_data.empty:
            print("❌ 데이터 수집 실패")
            return None

        company_info = self.stock_collector.get_company_info(ticker)

        # 2. 기술적 분석
        print("\n2️⃣ 기술적 분석 단계")
        technical_analyzer = TechnicalAnalyzer(stock_data)
        technical_result = technical_analyzer.analyze_all()

        # 3. 뉴스 감성 분석
        print("\n3️⃣ 뉴스 감성 분석 단계")
        if not company_name:
            company_name = company_info.get('종목명', ticker)

        if NEWS_API_KEY:
            news_list = self.news_collector.get_news(company_name, days=7)
        else:
            news_list = self.news_collector.get_dummy_news(company_name, count=5)

        sentiment_result = self.sentiment_analyzer.analyze_news_list(news_list)

        # 4. 신뢰도 계산
        print("\n4️⃣ 신뢰도 계산 단계")
        confidence_result = self.confidence_calculator.calculate_confidence(
            technical_result, sentiment_result
        )

        # 5. 보고서 생성
        print("\n5️⃣ 보고서 생성 단계")
        analysis_data = {
            'confidence': confidence_result,
            'technical': technical_result,
            'sentiment': sentiment_result,
            'company_info': company_info
        }

        report_path = self.report_generator.generate_html_report(ticker, analysis_data)

        # 결과 출력
        self._print_summary(ticker, confidence_result)

        return {
            'analysis': analysis_data,
            'report_path': report_path
        }

    def analyze_crypto(self, coin_id, coin_name=None):
        """
        암호화폐 분석

        Args:
            coin_id (str): 코인 ID (예: "bitcoin", "ethereum")
            coin_name (str): 코인명 (뉴스 검색용)

        Returns:
            dict: 종합 분석 결과
        """
        print(f"\n{'='*60}")
        print(f"🪙 {coin_id} 분석 시작")
        print(f"{'='*60}\n")

        # 1. 암호화폐 데이터 수집
        print("1️⃣ 데이터 수집 단계")
        crypto_data = self.crypto_collector.get_crypto_data(coin_id, days=365)
        if crypto_data is None or crypto_data.empty:
            print("❌ 데이터 수집 실패")
            return None

        coin_info = self.crypto_collector.get_coin_info(coin_id)

        # 암호화폐는 간단한 OHLCV 형식으로 변환
        crypto_data_ohlcv = crypto_data.copy()
        crypto_data_ohlcv['종가'] = crypto_data_ohlcv['가격']
        crypto_data_ohlcv['고가'] = crypto_data_ohlcv['가격']
        crypto_data_ohlcv['저가'] = crypto_data_ohlcv['가격']
        crypto_data_ohlcv['시가'] = crypto_data_ohlcv['가격']

        # 2. 기술적 분석
        print("\n2️⃣ 기술적 분석 단계")
        technical_analyzer = TechnicalAnalyzer(crypto_data_ohlcv)
        technical_result = technical_analyzer.analyze_all()

        # 3. 뉴스 감성 분석
        print("\n3️⃣ 뉴스 감성 분석 단계")
        if not coin_name:
            coin_name = coin_info.get('코인명', coin_id)

        if NEWS_API_KEY:
            news_list = self.news_collector.get_news(coin_name, days=7)
        else:
            news_list = self.news_collector.get_dummy_news(coin_name, count=5)

        sentiment_result = self.sentiment_analyzer.analyze_news_list(news_list)

        # 4. 신뢰도 계산
        print("\n4️⃣ 신뢰도 계산 단계")
        confidence_result = self.confidence_calculator.calculate_confidence(
            technical_result, sentiment_result
        )

        # 5. 보고서 생성
        print("\n5️⃣ 보고서 생성 단계")
        analysis_data = {
            'confidence': confidence_result,
            'technical': technical_result,
            'sentiment': sentiment_result,
            'company_info': coin_info
        }

        report_path = self.report_generator.generate_html_report(coin_id, analysis_data)

        # 결과 출력
        self._print_summary(coin_id, confidence_result)

        return {
            'analysis': analysis_data,
            'report_path': report_path
        }

    def _print_summary(self, ticker, confidence):
        """분석 결과 요약 출력"""
        print(f"\n{'='*60}")
        print("✅ 분석 완료!")
        print(f"{'='*60}\n")

        signal_emoji = {
            'strong_buy': '🚀',
            'buy': '📈',
            'neutral': '➡️',
            'sell': '📉',
            'strong_sell': '⚠️'
        }

        signal = confidence['signal']
        score = confidence['score']
        emoji = signal_emoji.get(signal, '➡️')

        print(f"종목: {ticker}")
        print(f"신호: {emoji} {signal.upper()}")
        print(f"신뢰도: {score}%")
        print(f"리스크: {'높음' if len(confidence.get('uncertainties', [])) > 3 else '중간' if len(confidence.get('uncertainties', [])) > 1 else '낮음'}")

        print(f"\n📊 주요 근거:")
        for reason in confidence['reasons'][:5]:  # 상위 5개만
            print(f"  • [{reason['category']}] {reason['reason']} {reason['impact']}")

        if confidence.get('uncertainties'):
            print(f"\n⚠️ 주의사항:")
            for uncertainty in confidence['uncertainties'][:3]:  # 상위 3개만
                print(f"  • {uncertainty['factor']}: {uncertainty['description']}")

        print(f"\n{'='*60}\n")


def main():
    """메인 실행 함수"""
    analyzer = MarketAnalyzer()

    print("\n🎯 시장 분석 시스템에 오신 것을 환영합니다!\n")
    print("분석 가능한 항목:")
    print("  1. 한국 주식 (예: 005930.KS - 삼성전자)")
    print("  2. 미국 주식 (예: AAPL - 애플)")
    print("  3. 암호화폐 (예: bitcoin, ethereum)")
    print()

    # 사용자 입력
    choice = input("분석 유형을 선택하세요 (1: 주식, 2: 암호화폐): ").strip()

    if choice == '1':
        ticker = input("종목 코드를 입력하세요 (예: 005930.KS, AAPL): ").strip()
        company_name = input("회사명을 입력하세요 (엔터 시 자동): ").strip()

        result = analyzer.analyze_stock(
            ticker,
            company_name if company_name else None
        )

    elif choice == '2':
        coin_id = input("코인 ID를 입력하세요 (예: bitcoin, ethereum): ").strip().lower()
        coin_name = input("코인명을 입력하세요 (엔터 시 자동): ").strip()

        result = analyzer.analyze_crypto(
            coin_id,
            coin_name if coin_name else None
        )

    else:
        print("❌ 잘못된 선택입니다.")
        return

    if result:
        print(f"\n📄 보고서 위치: {result['report_path']}")
        print("브라우저에서 열어보세요!")

        # 자동으로 브라우저에서 열기 (Windows)
        if sys.platform == 'win32':
            import webbrowser
            webbrowser.open(result['report_path'])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
