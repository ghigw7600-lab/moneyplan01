# -*- coding: utf-8 -*-
"""
주식 데이터 수집 모듈
한국(코스피/코스닥) 및 미국 주식 데이터 수집
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import ssl
import urllib.request
import time

# SSL 인증서 검증 우회 (한글 경로 문제 해결)
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 상위 디렉토리 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_PERIOD, DEFAULT_INTERVAL

# 한국 주식 전용 콜렉터
try:
    from collectors.kr_stock_collector import KRStockCollector
    KR_STOCK_AVAILABLE = True
except:
    KR_STOCK_AVAILABLE = False


class StockCollector:
    """주식 데이터 수집기 (한국 주식은 FinanceDataReader 사용)"""

    def __init__(self):
        self.data = None
        self.kr_collector = KRStockCollector() if KR_STOCK_AVAILABLE else None

    def get_stock_data(self, ticker, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL):
        """
        주식 데이터 수집

        Args:
            ticker (str): 종목 코드
                - 한국: "005930.KS" (삼성전자 코스피)
                - 한국: "035720.KQ" (카카오 코스닥)
                - 미국: "AAPL" (애플)
            period (str): 수집 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            pandas.DataFrame: OHLCV 데이터
        """
        # 한국 주식인지 확인 (.KS 또는 .KQ 포함 또는 6자리 숫자)
        is_korean = ticker.endswith('.KS') or ticker.endswith('.KQ') or (ticker.isdigit() and len(ticker) == 6)

        if is_korean and self.kr_collector:
            # FinanceDataReader로 한국 주식 수집
            print(f"📊 [한국 주식] {ticker} 데이터 수집 중 (FinanceDataReader)...")
            return self.kr_collector.get_stock_data(ticker, period, interval)

        # 미국 주식은 yfinance 사용
        try:
            print(f"📊 [미국 주식] {ticker} 데이터 수집 중 (yfinance)...")

            # API 요청 제한 방지 - 재시도 로직 추가
            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    time.sleep(retry_delay * (attempt + 1))  # 점진적 딜레이 증가

                    stock = yf.Ticker(ticker)
                    self.data = stock.history(period=period, interval=interval)

                    if self.data.empty:
                        if attempt < max_retries - 1:
                            print(f"⚠️ 재시도 {attempt + 1}/{max_retries}...")
                            continue
                        else:
                            print(f"⚠️ {ticker} 데이터 없음 (종목코드를 확인하세요)")
                            return None

                    # 한글 컬럼명으로 변경
                    self.data.columns = ['시가', '고가', '저가', '종가', '거래량', '배당금', '주식분할']

                    print(f"✅ {ticker} 데이터 {len(self.data)}개 수집 완료")
                    return self.data

                except Exception as retry_error:
                    if "429" in str(retry_error) or "Too Many Requests" in str(retry_error):
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 2)
                            print(f"⚠️ API 요청 제한 - {wait_time}초 대기 후 재시도...")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"❌ API 요청 제한 초과. 잠시 후 다시 시도하세요.")
                            return None
                    else:
                        raise retry_error

        except Exception as e:
            print(f"❌ 에러: {ticker} 데이터 수집 실패 - {str(e)}")
            return None

    def get_current_price(self, ticker):
        """현재가 조회"""
        # 한국 주식 확인
        is_korean = ticker.endswith('.KS') or ticker.endswith('.KQ') or (ticker.isdigit() and len(ticker) == 6)

        if is_korean and self.kr_collector:
            return self.kr_collector.get_current_price(ticker)

        # 미국 주식
        try:
            time.sleep(1)  # API 요청 제한 방지
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except:
            return None

    def get_company_info(self, ticker):
        """기업 정보 조회"""
        # 한국 주식 확인
        is_korean = ticker.endswith('.KS') or ticker.endswith('.KQ') or (ticker.isdigit() and len(ticker) == 6)

        if is_korean and self.kr_collector:
            return self.kr_collector.get_company_info(ticker)

        # 미국 주식
        try:
            time.sleep(1)  # API 요청 제한 방지
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                '종목명': info.get('longName') or info.get('shortName'),
                '시가총액': info.get('marketCap'),
                'PER': info.get('trailingPE'),
                'PBR': info.get('priceToBook'),
                'ROE': info.get('returnOnEquity'),
                '배당수익률': info.get('dividendYield'),
                '52주 최고': info.get('fiftyTwoWeekHigh'),
                '52주 최저': info.get('fiftyTwoWeekLow'),
                '평균거래량': info.get('averageVolume'),
                '업종': info.get('sector'),
                '산업': info.get('industry')
            }
        except Exception as e:
            print(f"⚠️ 기업 정보 조회 실패: {str(e)}")
            return {}

    def search_ticker(self, keyword):
        """
        종목 코드 검색 (간단한 매핑)
        실제로는 KRX API나 별도 DB 필요
        """
        # 주요 종목 매핑 (예시)
        ticker_map = {
            '삼성전자': '005930.KS',
            '카카오': '035720.KQ',
            'SK하이닉스': '000660.KS',
            'NAVER': '035420.KS',
            '현대차': '005380.KS',
            'LG에너지솔루션': '373220.KS',
            '애플': 'AAPL',
            '테슬라': 'TSLA',
            '마이크로소프트': 'MSFT',
            '엔비디아': 'NVDA',
            '아마존': 'AMZN',
            '구글': 'GOOGL',
            '메타': 'META'
        }

        return ticker_map.get(keyword)


# 테스트 코드
if __name__ == "__main__":
    collector = StockCollector()

    # 삼성전자 데이터 수집
    print("\n=== 삼성전자 데이터 수집 ===")
    data = collector.get_stock_data("005930.KS", period="3mo")
    if data is not None:
        print(data.tail())
        print(f"\n현재가: {collector.get_current_price('005930.KS'):,}원")

    # 애플 데이터 수집
    print("\n=== 애플 데이터 수집 ===")
    data = collector.get_stock_data("AAPL", period="3mo")
    if data is not None:
        print(data.tail())
        print(f"\n현재가: ${collector.get_current_price('AAPL')}")

    # 기업 정보
    print("\n=== 삼성전자 기업 정보 ===")
    info = collector.get_company_info("005930.KS")
    for key, value in info.items():
        print(f"{key}: {value}")
