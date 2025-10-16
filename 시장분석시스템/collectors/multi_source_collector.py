# -*- coding: utf-8 -*-
"""
다중 데이터 소스 수집기
Yahoo Finance 실패 시 자동으로 대체 소스 사용
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
from pathlib import Path

class MultiSourceCollector:
    """여러 데이터 소스를 순차적으로 시도하는 수집기"""

    def __init__(self):
        # 캐시 디렉토리 설정
        self.cache_dir = Path(__file__).parent.parent / 'data' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 캐시 유효 시간 (초) - 1시간
        self.cache_ttl = 3600

    def _get_cache_path(self, ticker, period):
        """캐시 파일 경로"""
        return self.cache_dir / f"{ticker}_{period}.json"

    def _load_from_cache(self, ticker, period):
        """캐시에서 데이터 로드"""
        cache_path = self._get_cache_path(ticker, period)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 캐시 유효성 확인
            cached_time = datetime.fromisoformat(cache_data['cached_at'])
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                print(f"✅ 캐시에서 {ticker} 데이터 로드 (캐시 시간: {cached_time.strftime('%H:%M:%S')})")

                # DataFrame으로 변환
                df = pd.DataFrame(cache_data['data'])
                df.index = pd.to_datetime(df.index)
                return df
            else:
                print(f"⏰ 캐시 만료 ({ticker})")
                return None

        except Exception as e:
            print(f"⚠️ 캐시 로드 실패: {e}")
            return None

    def _save_to_cache(self, ticker, period, data):
        """캐시에 데이터 저장"""
        try:
            cache_data = {
                'ticker': ticker,
                'period': period,
                'cached_at': datetime.now().isoformat(),
                'data': data.reset_index().to_dict('records')
            }

            cache_path = self._get_cache_path(ticker, period)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, default=str)

            print(f"💾 캐시 저장 완료: {ticker}")
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

    def get_stock_data_yfinance(self, ticker, period='3mo'):
        """Yahoo Finance로 데이터 수집"""
        try:
            print(f"📊 [Yahoo Finance] {ticker} 시도 중...")
            time.sleep(2)  # Rate limit 방지

            stock = yf.Ticker(ticker)
            data = stock.history(period=period)

            if data.empty:
                return None, "데이터 없음"

            # 한글 컬럼명 변환
            data.columns = ['시가', '고가', '저가', '종가', '거래량', '배당금', '주식분할']
            return data, None

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                return None, "API 요청 제한 (429 에러)"
            return None, f"Yahoo Finance 에러: {error_msg[:100]}"

    def get_stock_data_alternative(self, ticker, period='3mo'):
        """대체 데이터 소스 (향후 확장 가능)"""
        # TODO: Alpha Vantage, Financial Modeling Prep 등 추가
        return None, "대체 소스 미구현"

    def get_stock_data(self, ticker, period='3mo'):
        """
        다중 소스 전략으로 데이터 수집
        1. 캐시 확인
        2. Yahoo Finance 시도
        3. 대체 소스 시도
        """
        # 1단계: 캐시 확인
        cached_data = self._load_from_cache(ticker, period)
        if cached_data is not None:
            return cached_data, None

        # 2단계: Yahoo Finance 시도
        data, error = self.get_stock_data_yfinance(ticker, period)
        if data is not None:
            self._save_to_cache(ticker, period, data)
            return data, None

        print(f"⚠️ Yahoo Finance 실패: {error}")

        # 3단계: 대체 소스 시도
        data, error2 = self.get_stock_data_alternative(ticker, period)
        if data is not None:
            self._save_to_cache(ticker, period, data)
            return data, None

        # 모든 소스 실패
        error_message = f"""
        데이터 수집 실패:
        - Yahoo Finance: {error}
        - 대체 소스: {error2}

        💡 해결 방법:
        1. 5분 후 다시 시도하세요 (API 제한 해제 대기)
        2. 종목 코드를 확인하세요 (예: AAPL, MSFT)
        3. 한국 주식은 .KS 또는 .KQ를 붙이세요 (예: 005930.KS)
        """

        return None, error_message.strip()


if __name__ == "__main__":
    # 테스트
    collector = MultiSourceCollector()

    # 테스트 1: 정상 케이스
    data, error = collector.get_stock_data("AAPL", "1mo")
    if error:
        print(f"❌ 에러: {error}")
    else:
        print(f"✅ 성공: {len(data)}개 데이터 수집")

    # 테스트 2: 캐시 로드
    time.sleep(1)
    data2, error2 = collector.get_stock_data("AAPL", "1mo")
    if error2:
        print(f"❌ 에러: {error2}")
    else:
        print(f"✅ 캐시 성공: {len(data2)}개 데이터")
