# -*- coding: utf-8 -*-
"""
암호화폐 데이터 수집 모듈
CoinGecko API 사용 (무료, 제한: 분당 10-50 요청)
"""

import requests
import pandas as pd
from datetime import datetime
import time


class CryptoCollector:
    """암호화폐 데이터 수집기"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.data = None

    def get_crypto_data(self, coin_id="bitcoin", days=365, currency="usd"):
        """
        암호화폐 가격 데이터 수집

        Args:
            coin_id (str): 코인 ID (bitcoin, ethereum, ripple 등)
            days (int): 수집 기간 (일)
            currency (str): 기준 통화 (usd, krw)

        Returns:
            pandas.DataFrame: 가격 데이터
        """
        try:
            print(f"🪙 {coin_id} 데이터 수집 중...")

            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': currency,
                'days': days,
                'interval': 'daily'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 데이터 변환 (주식 데이터와 호환되도록 컬럼명 통일)
            df = pd.DataFrame(data['prices'], columns=['timestamp', '종가'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # OHLC 데이터가 없으므로 종가로 대체
            df['시가'] = df['종가']
            df['고가'] = df['종가']
            df['저가'] = df['종가']

            # 거래량 추가
            if 'total_volumes' in data:
                volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', '거래량'])
                volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
                volumes.set_index('timestamp', inplace=True)
                df = df.join(volumes)
            else:
                df['거래량'] = 0

            # 컬럼 순서 정리 (주식 데이터와 동일하게)
            df = df[['시가', '고가', '저가', '종가', '거래량']]

            self.data = df
            print(f"✅ {coin_id} 데이터 {len(df)}개 수집 완료")
            return df

        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ 에러: {str(e)}")
            return None

    def get_current_price(self, coin_ids, currency="usd"):
        """
        현재가 조회 (여러 코인 동시 조회 가능)

        Args:
            coin_ids (str or list): 코인 ID (단일 or 리스트)
            currency (str): 기준 통화

        Returns:
            dict: 코인별 현재가
        """
        try:
            if isinstance(coin_ids, str):
                coin_ids = [coin_ids]

            ids_param = ','.join(coin_ids)
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ids_param,
                'vs_currencies': currency,
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"❌ 현재가 조회 실패: {str(e)}")
            return {}

    def get_coin_info(self, coin_id):
        """코인 상세 정보 조회"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            market_data = data.get('market_data', {})

            return {
                '코인명': data.get('name'),
                '심볼': data.get('symbol', '').upper(),
                '현재가(USD)': market_data.get('current_price', {}).get('usd'),
                '현재가(KRW)': market_data.get('current_price', {}).get('krw'),
                '시가총액': market_data.get('market_cap', {}).get('usd'),
                '24시간 변동': market_data.get('price_change_percentage_24h'),
                '7일 변동': market_data.get('price_change_percentage_7d'),
                '30일 변동': market_data.get('price_change_percentage_30d'),
                '거래량(24h)': market_data.get('total_volume', {}).get('usd'),
                '시가총액 순위': data.get('market_cap_rank'),
                'ATH(USD)': market_data.get('ath', {}).get('usd'),
                'ATL(USD)': market_data.get('atl', {}).get('usd')
            }

        except Exception as e:
            print(f"⚠️ 코인 정보 조회 실패: {str(e)}")
            return {}

    def search_coins(self, keyword):
        """코인 검색"""
        try:
            url = f"{self.base_url}/search"
            params = {'query': keyword}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            coins = data.get('coins', [])

            results = []
            for coin in coins[:10]:  # 상위 10개만
                results.append({
                    'id': coin.get('id'),
                    '이름': coin.get('name'),
                    '심볼': coin.get('symbol'),
                    '순위': coin.get('market_cap_rank')
                })

            return results

        except Exception as e:
            print(f"⚠️ 검색 실패: {str(e)}")
            return []

    def get_trending_coins(self):
        """트렌딩 코인 (인기 상승 코인)"""
        try:
            url = f"{self.base_url}/search/trending"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            coins = data.get('coins', [])

            trending = []
            for item in coins:
                coin = item.get('item', {})
                trending.append({
                    'id': coin.get('id'),
                    '이름': coin.get('name'),
                    '심볼': coin.get('symbol'),
                    '순위': coin.get('market_cap_rank'),
                    '점수': coin.get('score')
                })

            return trending

        except Exception as e:
            print(f"⚠️ 트렌딩 조회 실패: {str(e)}")
            return []


# 테스트 코드
if __name__ == "__main__":
    collector = CryptoCollector()

    # 비트코인 데이터 수집
    print("\n=== 비트코인 데이터 수집 ===")
    btc_data = collector.get_crypto_data("bitcoin", days=90, currency="usd")
    if btc_data is not None:
        print(btc_data.tail())

    # 현재가 조회
    print("\n=== 주요 코인 현재가 ===")
    prices = collector.get_current_price(["bitcoin", "ethereum", "ripple"], currency="usd")
    for coin, data in prices.items():
        print(f"{coin}: ${data.get('usd'):,} (24h: {data.get('usd_24h_change'):.2f}%)")

    # 코인 정보
    print("\n=== 비트코인 상세 정보 ===")
    info = collector.get_coin_info("bitcoin")
    for key, value in info.items():
        print(f"{key}: {value}")

    # 트렌딩 코인
    print("\n=== 트렌딩 코인 ===")
    trending = collector.get_trending_coins()
    for i, coin in enumerate(trending[:5], 1):
        print(f"{i}. {coin['이름']} ({coin['심볼']}) - 순위: {coin['순위']}")
