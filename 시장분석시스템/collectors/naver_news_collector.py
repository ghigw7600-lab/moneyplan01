# -*- coding: utf-8 -*-
"""
네이버 뉴스 수집 모듈 (클릭 가능한 링크 포함)
Phase 4-2: 캐시 시스템 추가 (1시간 유효)
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import json
import os
import hashlib


class NaverNewsCollector:
    """네이버 뉴스 수집기 (Phase 4-2: 캐시 지원)"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Phase 4-2: 캐시 설정
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache', 'news')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_validity = 3600  # 1시간 (3600초)

    def _get_cache_key(self, query, max_count):
        """캐시 키 생성"""
        key_string = f"{query}_{max_count}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _load_cache(self, query, max_count):
        """캐시에서 뉴스 로드"""
        cache_key = self._get_cache_key(query, max_count)
        cache_file = os.path.join(self.cache_dir, f"naver_{cache_key}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 캐시 유효성 확인
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > self.cache_validity:
                return None

            return cache_data.get('news', [])
        except:
            return None

    def _save_cache(self, query, max_count, news):
        """캐시에 뉴스 저장"""
        try:
            cache_key = self._get_cache_key(query, max_count)
            cache_file = os.path.join(self.cache_dir, f"naver_{cache_key}.json")

            cache_data = {
                'timestamp': time.time(),
                'news': news
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_news(self, query, max_count=20, use_cache=True):
        """
        네이버 뉴스 검색 및 수집 (Phase 4-2: 캐시 지원)

        Args:
            query (str): 검색 키워드 (예: "삼성전자", "비트코인")
            max_count (int): 수집할 뉴스 개수
            use_cache (bool): 캐시 사용 여부

        Returns:
            list: 뉴스 리스트 [{'title', 'description', 'url', 'date', 'source'}]
        """
        # Phase 4-2: 캐시 확인
        if use_cache:
            cached_news = self._load_cache(query, max_count)
            if cached_news is not None:
                return cached_news

        news_list = []

        try:
            # 네이버 뉴스 검색 URL
            base_url = "https://search.naver.com/search.naver"

            for start in range(1, max_count + 1, 10):
                params = {
                    'where': 'news',
                    'query': query,
                    'start': start,
                    'sort': 1  # 최신순 (0: 관련도순, 1: 최신순)
                }

                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)

                if response.status_code != 200:
                    print(f"⚠️ 뉴스 수집 실패: HTTP {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')

                # 뉴스 항목 파싱
                articles = soup.select('div.news_area')

                if not articles:
                    print(f"⚠️ 더 이상 뉴스가 없습니다")
                    break

                for article in articles:
                    try:
                        # 제목 및 링크
                        title_elem = article.select_one('a.news_tit')
                        if not title_elem:
                            continue

                        title = title_elem.get('title', title_elem.get_text(strip=True))
                        url = title_elem.get('href', '')

                        # 요약
                        desc_elem = article.select_one('div.news_dsc')
                        description = desc_elem.get_text(strip=True) if desc_elem else ''

                        # 언론사
                        source_elem = article.select_one('a.info.press')
                        source = source_elem.get_text(strip=True) if source_elem else '알 수 없음'

                        # 날짜
                        date_elem = article.select_one('span.info')
                        date_text = date_elem.get_text(strip=True) if date_elem else ''

                        # 날짜 파싱
                        published_date = self._parse_date(date_text)

                        news_list.append({
                            '제목': title,
                            '설명': description,
                            '링크': url,  # 키 통일
                            '날짜': published_date,
                            '언론사': source,
                            '출처': '네이버 뉴스',
                            'source_type': 'domestic'  # 네이버는 모두 국내 뉴스
                        })

                        if len(news_list) >= max_count:
                            break

                    except Exception as e:
                        print(f"⚠️ 뉴스 파싱 오류: {str(e)}")
                        continue

                if len(news_list) >= max_count:
                    break

                # 요청 간 딜레이 (네이버 부하 방지)
                time.sleep(0.5)

            print(f"✅ 네이버 뉴스 {len(news_list)}개 수집 완료")

            # Phase 4-2: 캐시 저장
            if use_cache:
                self._save_cache(query, max_count, news_list)

            return news_list

        except Exception as e:
            print(f"❌ 뉴스 수집 오류: {str(e)}")
            return news_list

    def _parse_date(self, date_text):
        """날짜 텍스트 파싱"""
        try:
            now = datetime.now()

            # "N분 전", "N시간 전", "N일 전" 형식
            if '분 전' in date_text:
                minutes = int(re.search(r'(\d+)분', date_text).group(1))
                return now - timedelta(minutes=minutes)
            elif '시간 전' in date_text:
                hours = int(re.search(r'(\d+)시간', date_text).group(1))
                return now - timedelta(hours=hours)
            elif '일 전' in date_text:
                days = int(re.search(r'(\d+)일', date_text).group(1))
                return now - timedelta(days=days)
            else:
                # "YYYY.MM.DD" 형식
                try:
                    return datetime.strptime(date_text, '%Y.%m.%d')
                except:
                    return now

        except:
            return datetime.now()

    def get_finance_news(self, ticker, stock_name, max_count=20):
        """
        특정 종목 관련 네이버 금융 뉴스 수집

        Args:
            ticker (str): 종목 코드 (예: "005930")
            stock_name (str): 종목명 (예: "삼성전자")
            max_count (int): 수집할 뉴스 개수

        Returns:
            list: 뉴스 리스트
        """
        # 종목명으로 검색 (더 정확한 결과)
        return self.get_news(stock_name, max_count)


# 테스트 코드
if __name__ == "__main__":
    collector = NaverNewsCollector()

    print("=== 삼성전자 뉴스 수집 테스트 ===")
    news = collector.get_news("삼성전자", max_count=10)

    for i, article in enumerate(news, 1):
        print(f"\n[{i}] {article['제목']}")
        print(f"    📰 {article['언론사']} | {article['날짜'].strftime('%Y-%m-%d %H:%M')}")
        print(f"    🔗 {article['url']}")
        print(f"    📝 {article['설명'][:100]}...")

    print(f"\n총 {len(news)}개 뉴스 수집 완료")
