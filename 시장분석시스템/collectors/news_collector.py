# -*- coding: utf-8 -*-
"""
뉴스 데이터 수집 모듈
NewsAPI 사용 (무료: 하루 100 요청)
"""

import requests
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NEWS_API_KEY


class NewsCollector:
    """뉴스 데이터 수집기"""

    def __init__(self, api_key=NEWS_API_KEY):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"

    def get_news(self, query, days=7, language="ko", page_size=20):
        """
        뉴스 검색

        Args:
            query (str): 검색 키워드 (예: "삼성전자", "비트코인")
            days (int): 검색 기간 (일)
            language (str): 언어 (ko, en)
            page_size (int): 결과 개수 (최대 100)

        Returns:
            list: 뉴스 기사 리스트
        """
        if not self.api_key:
            print("⚠️ NEWS_API_KEY가 설정되지 않았습니다.")
            print("💡 config.py에서 API 키를 설정하세요.")
            print("💡 https://newsapi.org 에서 무료로 발급 받을 수 있습니다.")
            return []

        try:
            print(f"📰 '{query}' 뉴스 검색 중...")

            # 날짜 계산
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'from': from_date,
                'language': language,
                'sortBy': 'publishedAt',
                'pageSize': page_size,
                'apiKey': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                print(f"❌ API 에러: {data.get('message')}")
                return []

            articles = data.get('articles', [])
            print(f"✅ 뉴스 {len(articles)}개 수집 완료")

            # 데이터 정제
            news_list = []
            for article in articles:
                news_list.append({
                    '제목': article.get('title'),
                    '설명': article.get('description'),
                    '내용': article.get('content'),
                    '출처': article.get('source', {}).get('name'),
                    'URL': article.get('url'),
                    '게시일': article.get('publishedAt'),
                    '이미지': article.get('urlToImage')
                })

            return news_list

        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ 에러: {str(e)}")
            return []

    def get_top_headlines(self, category=None, country="kr"):
        """
        헤드라인 뉴스 조회

        Args:
            category (str): 카테고리 (business, technology, etc.)
            country (str): 국가 코드 (kr, us)

        Returns:
            list: 헤드라인 뉴스 리스트
        """
        if not self.api_key:
            print("⚠️ NEWS_API_KEY가 설정되지 않았습니다.")
            return []

        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'apiKey': self.api_key
            }

            if category:
                params['category'] = category

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            news_list = []
            for article in articles:
                news_list.append({
                    '제목': article.get('title'),
                    '설명': article.get('description'),
                    '출처': article.get('source', {}).get('name'),
                    'URL': article.get('url'),
                    '게시일': article.get('publishedAt')
                })

            return news_list

        except Exception as e:
            print(f"❌ 헤드라인 조회 실패: {str(e)}")
            return []

    def get_market_news(self, days=7):
        """
        시장 관련 뉴스 수집 (여러 키워드 통합)

        Returns:
            dict: 키워드별 뉴스
        """
        keywords = {
            '주식': '주식 OR 증시 OR 코스피 OR 나스닥',
            '암호화폐': '비트코인 OR 암호화폐 OR 가상화폐',
            '경제': '경제 OR 금리 OR 환율',
            '기술': '기술주 OR IT OR 반도체'
        }

        all_news = {}
        for category, query in keywords.items():
            news = self.get_news(query, days=days, page_size=10)
            all_news[category] = news

        return all_news


# 간단한 뉴스 수집 (API 키 없을 때 대안)
class SimpleNewsCollector:
    """API 키 없이 사용 가능한 간단한 뉴스 수집기"""

    def get_dummy_news(self, query, count=5):
        """
        테스트용 더미 뉴스 생성
        실제로는 크롤링이나 RSS 피드 사용 가능
        """
        print(f"⚠️ API 키가 없어 테스트 데이터를 생성합니다.")

        news_list = []
        for i in range(count):
            news_list.append({
                '제목': f'[테스트] {query} 관련 뉴스 {i+1}',
                '설명': f'{query}에 대한 최신 뉴스입니다.',
                '출처': '테스트 뉴스',
                'URL': 'https://example.com',
                '게시일': datetime.now().isoformat()
            })

        return news_list


# 테스트 코드
if __name__ == "__main__":
    # API 키가 있으면 NewsCollector, 없으면 SimpleNewsCollector 사용
    if NEWS_API_KEY:
        collector = NewsCollector(NEWS_API_KEY)

        # 삼성전자 뉴스 검색
        print("\n=== 삼성전자 뉴스 ===")
        news = collector.get_news("삼성전자", days=7)
        for i, article in enumerate(news[:3], 1):
            print(f"\n{i}. {article['제목']}")
            print(f"   출처: {article['출처']} | {article['게시일']}")
            print(f"   {article['설명'][:100]}...")

        # 비트코인 뉴스 검색
        print("\n\n=== 비트코인 뉴스 ===")
        news = collector.get_news("비트코인", days=7)
        for i, article in enumerate(news[:3], 1):
            print(f"\n{i}. {article['제목']}")
            print(f"   출처: {article['출처']}")

    else:
        print("\n⚠️ NEWS_API_KEY가 설정되지 않았습니다.")
        print("💡 테스트용 더미 데이터를 생성합니다.\n")

        collector = SimpleNewsCollector()
        news = collector.get_dummy_news("삼성전자")
        for article in news:
            print(f"- {article['제목']}")
