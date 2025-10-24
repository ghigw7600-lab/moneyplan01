"""
원자재(Commodities) 데이터 수집기
금, 은, 원유, 구리 등 주요 원자재 가격 데이터를 수집합니다.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import ssl
import os
import time

# SSL 인증서 검증 우회
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONIOENCODING'] = 'utf-8'


class CommodityCollector:
    """원자재 데이터 수집 클래스"""

    # 주요 원자재 심볼 (Yahoo Finance)
    # ETF를 사용하여 안정적인 데이터 수집
    COMMODITIES = {
        'gold': {'symbol': 'GLD', 'name': '금 (Gold ETF)', 'unit': 'USD'},
        'silver': {'symbol': 'SLV', 'name': '은 (Silver ETF)', 'unit': 'USD'},
        'crude_oil': {'symbol': 'USO', 'name': '원유 (Crude Oil ETF)', 'unit': 'USD'},
        'natural_gas': {'symbol': 'UNG', 'name': '천연가스 (Natural Gas ETF)', 'unit': 'USD'},
        'copper': {'symbol': 'CPER', 'name': '구리 (Copper ETF)', 'unit': 'USD'},
        'wheat': {'symbol': 'WEAT', 'name': '밀 (Wheat ETF)', 'unit': 'USD'},
        'corn': {'symbol': 'CORN', 'name': '옥수수 (Corn ETF)', 'unit': 'USD'},
        'soybeans': {'symbol': 'SOYB', 'name': '대두 (Soybeans ETF)', 'unit': 'USD'},
        'commodities': {'symbol': 'DBC', 'name': '종합 원자재 (Commodity Index)', 'unit': 'USD'},
        'precious_metals': {'symbol': 'DBP', 'name': '귀금속 (Precious Metals)', 'unit': 'USD'},
    }

    def __init__(self):
        """초기화"""
        pass

    def get_commodity_data(self, commodity_key, period='1mo', use_mock=False):
        """
        특정 원자재 데이터 수집

        Args:
            commodity_key: 원자재 키 (예: 'gold', 'silver', 'crude_oil')
            period: 데이터 기간 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            use_mock: True면 목 데이터 사용 (API 장애 시)

        Returns:
            dict: 원자재 데이터
        """
        if commodity_key not in self.COMMODITIES:
            raise ValueError(f"지원하지 않는 원자재: {commodity_key}")

        commodity_info = self.COMMODITIES[commodity_key]
        symbol = commodity_info['symbol']

        # 목 데이터 사용 (테스트용 또는 API 장애 시)
        if use_mock:
            return self._get_mock_data(commodity_key)

        try:
            # Yahoo Finance에서 데이터 수집 (재시도 로직 포함)
            max_retries = 2  # 재시도 횟수 감소
            retry_delay = 1  # 딜레이 감소
            hist = None

            for attempt in range(max_retries):
                try:
                    time.sleep(0.5)  # 짧은 딜레이
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period)

                    if not hist.empty:
                        break

                    if attempt < max_retries - 1:
                        print(f"재시도 {attempt + 1}/{max_retries}: {commodity_info['name']}")
                        continue

                except Exception as retry_error:
                    if "429" in str(retry_error) or "Too Many Requests" in str(retry_error):
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 2)
                            print(f"API 요청 제한 - {wait_time}초 대기 중...")
                            time.sleep(wait_time)
                            continue
                    # API 오류 시 목 데이터 사용
                    print(f"⚠️ API 오류 - 목 데이터 사용: {commodity_info['name']}")
                    return self._get_mock_data(commodity_key)

            if hist is None or hist.empty:
                print(f"⚠️ 데이터 없음 - 목 데이터 사용: {commodity_info['name']}")
                return self._get_mock_data(commodity_key)

            # 현재 가격 정보
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price

            # 가격 변동
            price_change = current_price - previous_price
            price_change_pct = (price_change / previous_price * 100) if previous_price != 0 else 0

            # 기간별 통계
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0

            # 이동평균선 계산
            ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1] if len(hist) >= 5 else None
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
            ma_60 = hist['Close'].rolling(window=60).mean().iloc[-1] if len(hist) >= 60 else None

            # 변동성 계산 (표준편차)
            volatility = hist['Close'].pct_change().std() * 100

            # 추세 판단
            trend = self._calculate_trend(hist)

            result = {
                'key': commodity_key,
                'symbol': symbol,
                'name': commodity_info['name'],
                'unit': commodity_info['unit'],
                'current_price': round(current_price, 2),
                'previous_price': round(previous_price, 2),
                'price_change': round(price_change, 2),
                'price_change_pct': round(price_change_pct, 2),
                'high_52w': round(high_52w, 2),
                'low_52w': round(low_52w, 2),
                'avg_volume': round(avg_volume, 0),
                'volatility': round(volatility, 2),
                'ma_5': round(ma_5, 2) if ma_5 else None,
                'ma_20': round(ma_20, 2) if ma_20 else None,
                'ma_60': round(ma_60, 2) if ma_60 else None,
                'trend': trend,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'historical_data': hist.to_dict('records')  # 차트용 데이터
            }

            return result

        except Exception as e:
            print(f"오류 발생 ({commodity_info['name']}): {str(e)}")
            return None

    def get_all_commodities(self, period='1mo', use_mock=True):
        """
        모든 원자재 데이터 수집

        Args:
            period: 데이터 기간
            use_mock: 목 데이터 사용 여부 (기본값: True, API 불안정 시)

        Returns:
            dict: 모든 원자재 데이터
        """
        results = {}

        for key in self.COMMODITIES.keys():
            print(f"수집 중: {self.COMMODITIES[key]['name']}...")
            data = self.get_commodity_data(key, period, use_mock=use_mock)
            if data:
                results[key] = data

        return results

    def get_major_commodities(self, period='1mo', use_mock=True):
        """
        주요 원자재만 수집 (금, 은, 원유, 구리)

        Args:
            period: 데이터 기간
            use_mock: 목 데이터 사용 여부 (기본값: True, API 불안정 시)

        Returns:
            dict: 주요 원자재 데이터
        """
        major_keys = ['gold', 'silver', 'crude_oil', 'copper']
        results = {}

        # API가 불안정하므로 기본적으로 목 데이터 사용
        for key in major_keys:
            print(f"수집 중: {self.COMMODITIES[key]['name']}...")
            data = self.get_commodity_data(key, period, use_mock=use_mock)
            if data:
                results[key] = data

        return results

    def _get_mock_data(self, commodity_key):
        """
        목 데이터 생성 (API 장애 시 사용)

        Args:
            commodity_key: 원자재 키

        Returns:
            dict: 목 원자재 데이터
        """
        commodity_info = self.COMMODITIES[commodity_key]

        # 원자재별 시뮬레이션 가격
        mock_prices = {
            'gold': 220.50,  # GLD ETF 가격
            'silver': 22.80,  # SLV ETF 가격
            'crude_oil': 78.30,  # USO ETF 가격
            'natural_gas': 10.20,  # UNG ETF 가격
            'copper': 26.40,  # CPER ETF 가격
            'wheat': 6.50,  # WEAT ETF 가격
            'corn': 23.10,  # CORN ETF 가격
            'soybeans': 38.70,  # SOYB ETF 가격
            'commodities': 15.20,  # DBC ETF 가격
            'precious_metals': 75.60,  # DBP ETF 가격
        }

        # 변동률 시뮬레이션 (-5% ~ +5%)
        import random
        random.seed(commodity_key.__hash__())
        change_pct = random.uniform(-5, 5)
        current_price = mock_prices.get(commodity_key, 100.0)
        previous_price = current_price / (1 + change_pct / 100)
        price_change = current_price - previous_price

        # 추세 방향
        if change_pct > 2:
            trend_direction = 'uptrend'
            trend_description = '상승 추세'
        elif change_pct < -2:
            trend_direction = 'downtrend'
            trend_description = '하락 추세'
        else:
            trend_direction = 'sideways'
            trend_description = '횡보'

        # 이동평균 시뮬레이션
        ma_5 = current_price * 0.98
        ma_20 = current_price * 0.96
        ma_60 = current_price * 0.94

        result = {
            'key': commodity_key,
            'symbol': commodity_info['symbol'],
            'name': commodity_info['name'],
            'unit': commodity_info['unit'],
            'current_price': round(current_price, 2),
            'previous_price': round(previous_price, 2),
            'price_change': round(price_change, 2),
            'price_change_pct': round(change_pct, 2),
            'high_52w': round(current_price * 1.15, 2),
            'low_52w': round(current_price * 0.85, 2),
            'avg_volume': 1250000,
            'volatility': round(abs(change_pct) * 0.8, 2),
            'ma_5': round(ma_5, 2),
            'ma_20': round(ma_20, 2),
            'ma_60': round(ma_60, 2),
            'trend': {
                'direction': trend_direction,
                'strength': round(abs(change_pct), 2),
                'description': trend_description
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'historical_data': [],  # 목 데이터에서는 차트 데이터 없음
            'is_mock': True  # 목 데이터 표시
        }

        return result

    def _calculate_trend(self, hist):
        """
        추세 계산 (단순 이동평균 기반)

        Args:
            hist: 가격 히스토리 DataFrame

        Returns:
            dict: 추세 정보
        """
        if len(hist) < 20:
            return {'direction': 'unknown', 'strength': 0, 'description': '데이터 부족'}

        # 5일, 20일 이동평균
        ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        current_price = hist['Close'].iloc[-1]

        # 추세 방향
        if ma_5 > ma_20 and current_price > ma_5:
            direction = 'uptrend'
            description = '상승 추세'
        elif ma_5 < ma_20 and current_price < ma_5:
            direction = 'downtrend'
            description = '하락 추세'
        else:
            direction = 'sideways'
            description = '횡보'

        # 추세 강도 (최근 20일 가격 변화율)
        price_20d_ago = hist['Close'].iloc[-20]
        strength = abs((current_price - price_20d_ago) / price_20d_ago * 100)

        return {
            'direction': direction,
            'strength': round(strength, 2),
            'description': description
        }

    def compare_commodities(self, period='1mo', use_mock=True):
        """
        원자재 비교 분석

        Args:
            period: 비교 기간
            use_mock: 목 데이터 사용 여부

        Returns:
            dict: 비교 분석 결과
        """
        all_data = self.get_all_commodities(period, use_mock=use_mock)

        if not all_data:
            return None

        # 수익률 순위
        sorted_by_return = sorted(
            all_data.items(),
            key=lambda x: x[1]['price_change_pct'],
            reverse=True
        )

        # 변동성 순위
        sorted_by_volatility = sorted(
            all_data.items(),
            key=lambda x: x[1]['volatility'],
            reverse=True
        )

        comparison = {
            'top_gainers': [
                {
                    'name': item[1]['name'],
                    'change_pct': item[1]['price_change_pct']
                }
                for item in sorted_by_return[:3]
            ],
            'top_losers': [
                {
                    'name': item[1]['name'],
                    'change_pct': item[1]['price_change_pct']
                }
                for item in sorted_by_return[-3:]
            ],
            'most_volatile': [
                {
                    'name': item[1]['name'],
                    'volatility': item[1]['volatility']
                }
                for item in sorted_by_volatility[:3]
            ],
            'least_volatile': [
                {
                    'name': item[1]['name'],
                    'volatility': item[1]['volatility']
                }
                for item in sorted_by_volatility[-3:]
            ]
        }

        return comparison


if __name__ == "__main__":
    # 테스트
    collector = CommodityCollector()

    print("=" * 50)
    print("원자재 데이터 수집 테스트")
    print("=" * 50)

    # 주요 원자재 수집
    print("\n[1] 주요 원자재 데이터 수집")
    major_data = collector.get_major_commodities(period='3mo')

    for key, data in major_data.items():
        print(f"\n{data['name']}")
        print(f"  현재 가격: {data['current_price']} {data['unit']}")
        print(f"  변동: {data['price_change']:+.2f} ({data['price_change_pct']:+.2f}%)")
        print(f"  추세: {data['trend']['description']} (강도: {data['trend']['strength']}%)")
        print(f"  변동성: {data['volatility']}%")

    # 비교 분석
    print("\n\n[2] 원자재 비교 분석")
    comparison = collector.compare_commodities(period='1mo')

    if comparison:
        print("\n상승률 Top 3:")
        for item in comparison['top_gainers']:
            print(f"  - {item['name']}: {item['change_pct']:+.2f}%")

        print("\n하락률 Top 3:")
        for item in comparison['top_losers']:
            print(f"  - {item['name']}: {item['change_pct']:+.2f}%")

        print("\n변동성 Top 3:")
        for item in comparison['most_volatile']:
            print(f"  - {item['name']}: {item['volatility']:.2f}%")

    print("\n\n테스트 완료!")
