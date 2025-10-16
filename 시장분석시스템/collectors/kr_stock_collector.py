# -*- coding: utf-8 -*-
"""
한국 주식 데이터 수집 모듈 (FinanceDataReader 사용)
코스피/코스닥 전용
"""

import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 상위 디렉토리 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class KRStockCollector:
    """한국 주식 데이터 수집기 (FinanceDataReader)"""

    def __init__(self):
        self.data = None

    def get_stock_data(self, ticker, period="3mo", interval="1d"):
        """
        한국 주식 데이터 수집

        Args:
            ticker (str): 종목 코드
                - 6자리 숫자만: "005930" (삼성전자)
                - 또는 .KS/.KQ 포함: "005930.KS"
            period (str): 수집 기간 (1mo, 3mo, 6mo, 1y, 2y, 5y)
            interval (str): 데이터 간격 (현재는 일봉만 지원)

        Returns:
            pandas.DataFrame: OHLCV 데이터
        """
        try:
            # 티커 정리 (.KS, .KQ 제거)
            clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')

            print(f"📊 {clean_ticker} 데이터 수집 중...")

            # 기간 계산
            end_date = datetime.now()
            if period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
            else:
                start_date = end_date - timedelta(days=90)  # 기본 3개월

            # 데이터 수집
            self.data = fdr.DataReader(clean_ticker, start_date, end_date)

            if self.data is None or self.data.empty:
                print(f"⚠️ {clean_ticker} 데이터 없음")
                return None

            # 한글 컬럼명으로 변경 (기존 시스템과 호환)
            column_mapping = {
                'Open': '시가',
                'High': '고가',
                'Low': '저가',
                'Close': '종가',
                'Volume': '거래량',
                'Change': '변동폭'
            }

            self.data = self.data.rename(columns=column_mapping)

            # 필요한 컬럼만 선택 (기존 시스템 호환)
            available_cols = [col for col in ['시가', '고가', '저가', '종가', '거래량'] if col in self.data.columns]
            self.data = self.data[available_cols]

            print(f"✅ {clean_ticker} 데이터 {len(self.data)}개 수집 완료")
            return self.data

        except Exception as e:
            print(f"❌ 에러: {ticker} 데이터 수집 실패 - {str(e)}")
            return None

    def get_current_price(self, ticker):
        """현재가 조회"""
        try:
            clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
            data = fdr.DataReader(clean_ticker)
            if data is not None and not data.empty:
                return data['Close'].iloc[-1]
            return None
        except:
            return None

    def get_company_info(self, ticker):
        """
        기업 정보 조회
        FinanceDataReader는 제한적인 정보만 제공
        """
        try:
            clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')

            # 종목 리스트에서 종목명 찾기
            krx_list = fdr.StockListing('KRX')
            stock_info = krx_list[krx_list['Code'] == clean_ticker]

            if stock_info.empty:
                return {'종목명': clean_ticker}

            stock_name = stock_info['Name'].iloc[0]
            market = stock_info['Market'].iloc[0]

            # 최근 데이터로 간단한 정보 제공
            recent_data = fdr.DataReader(clean_ticker)
            if recent_data is not None and not recent_data.empty:
                current_price = recent_data['Close'].iloc[-1]
                avg_volume = recent_data['Volume'].tail(20).mean()
                week_52_high = recent_data['High'].tail(252).max()
                week_52_low = recent_data['Low'].tail(252).min()

                return {
                    '종목명': stock_name,
                    '시장': market,
                    '현재가': f"{current_price:,.0f}원",
                    '평균거래량': f"{avg_volume:,.0f}",
                    '52주 최고': f"{week_52_high:,.0f}원",
                    '52주 최저': f"{week_52_low:,.0f}원"
                }

            return {'종목명': stock_name, '시장': market}

        except Exception as e:
            print(f"⚠️ 기업 정보 조회 실패: {str(e)}")
            return {}

    def search_ticker(self, keyword):
        """
        종목 코드 검색
        FinanceDataReader의 StockListing 활용
        """
        try:
            # KRX 전체 종목 리스트
            krx_list = fdr.StockListing('KRX')

            # 종목명으로 검색
            result = krx_list[krx_list['Name'].str.contains(keyword, na=False)]

            if not result.empty:
                return result['Code'].iloc[0]

            return None

        except Exception as e:
            print(f"⚠️ 종목 검색 실패: {str(e)}")
            return None


# 테스트 코드
if __name__ == "__main__":
    collector = KRStockCollector()

    # 삼성전자 데이터 수집
    print("\n=== 삼성전자 데이터 수집 ===")
    data = collector.get_stock_data("005930", period="3mo")
    if data is not None:
        print(data.tail())
        print(f"\n현재가: {collector.get_current_price('005930'):,}원")

    # SK하이닉스 데이터 수집
    print("\n=== SK하이닉스 데이터 수집 ===")
    data = collector.get_stock_data("000660", period="3mo")
    if data is not None:
        print(data.tail())

    # 기업 정보
    print("\n=== 삼성전자 기업 정보 ===")
    info = collector.get_company_info("005930")
    for key, value in info.items():
        print(f"{key}: {value}")

    # 종목 검색
    print("\n=== 종목 검색 테스트 ===")
    ticker = collector.search_ticker("삼성전자")
    print(f"'삼성전자' 검색 결과: {ticker}")
