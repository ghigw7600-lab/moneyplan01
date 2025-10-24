# -*- coding: utf-8 -*-
"""
Google News RSS Collector
네이버 뉴스 외에 Google News에서도 뉴스 수집
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time


class GoogleNewsCollector:
    """Google News RSS 수집기"""

    def __init__(self):
        self.base_url = "https://news.google.com/rss/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_news(self, keyword, max_count=20, language='ko'):
        """
        Google News에서 키워드 검색

        Args:
            keyword (str): 검색 키워드
            max_count (int): 최대 뉴스 개수
            language (str): 언어 ('ko' 또는 'en')

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        print(f"\n📰 Google News 검색: '{keyword}' (최대 {max_count}개)")

        try:
            # RSS URL 구성
            params = {
                'q': keyword,
                'hl': language,  # 언어
                'gl': 'KR',      # 국가
                'ceid': 'KR:ko'  # 지역:언어
            }

            # URL 인코딩
            query = f"?q={requests.utils.quote(keyword)}&hl={language}&gl=KR&ceid=KR:{language}"
            url = self.base_url + query

            print(f"🔍 URL: {url}")

            # RSS 피드 가져오기
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # XML 파싱
            root = ET.fromstring(response.content)

            news_list = []

            # RSS 아이템 추출
            for item in root.findall('.//item')[:max_count]:
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    source = item.find('source').text if item.find('source') is not None else 'Google News'

                    # 날짜 파싱 (RFC 822 형식)
                    try:
                        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                        formatted_date = dt
                    except:
                        formatted_date = datetime.now()

                    # 국내/외신 판단 (URL 도메인 기반 + 언론사명 확장)
                    # 1. URL 도메인 체크 (.kr, .co.kr)
                    is_domestic = False
                    if link:
                        if '.kr' in link.lower() or 'naver.com' in link.lower() or 'daum.net' in link.lower():
                            is_domestic = True

                    # 2. 한국 언론사 DB (100+ 확장)
                    if not is_domestic:
                        domestic_sources = [
                            # 주요 종합지
                            '연합뉴스', '뉴스1', '뉴시스', '노컷뉴스', '뉴스핌',

                            # 방송사
                            'SBS', 'KBS', 'MBC', 'JTBC', 'YTN', 'TV조선', '채널A', 'MBN',

                            # 중앙 일간지
                            '조선일보', '중앙일보', '동아일보', '한겨레', '경향신문', '국민일보', '서울신문', '문화일보', '세계일보',

                            # 경제지
                            '매일경제', '한국경제', '서울경제', '헤럴드경제', '아시아경제', '파이낸셜뉴스', '이데일리', '머니투데이', '비즈니스워치', '머니S', '뉴스토마토', '데일리안', '쿠키뉴스',

                            # IT/테크
                            '디지털타임스', '전자신문', '지디넷코리아', '블로터', '테크M', '아이뉴스24', '디지털데일리',

                            # 지역지
                            '부산일보', '국제신문', '영남일보', '대구신문', '광주일보', '전북일보', '강원일보', '제주일보', '충청일보', '대전일보', '경기일보', '인천일보',

                            # 전문지
                            '의학신문', '메디컬타임즈', '청년의사', '약사공론', '보험신문', '전기신문', '가스신문', '에너지신문', '건설경제', '환경일보',

                            # 인터넷 매체
                            '오마이뉴스', '프레시안', '미디어오늘', '시사IN', '주간경향', '한겨레21', '이코노미스트', '조선비즈', '중앙일보', '매경이코노미', '시사저널',

                            # 스포츠/연예
                            '스포츠조선', '스포츠동아', '스포츠서울', '일간스포츠', 'OSEN', '스타뉴스', '엑스포츠뉴스', '텐아시아', '마이데일리', '스포티비뉴스',

                            # 기타
                            '코리아헤럴드', '코리아타임스', '민중의소리', '참세상', '레디앙', '데일리NK', '자유아시아방송', '중앙선데이', '한국일보', '조세일보'
                        ]
                        is_domestic = any(ds in source for ds in domestic_sources)

                    news_list.append({
                        '제목': title,
                        '링크': link,
                        '날짜': formatted_date,
                        '설명': description,
                        '언론사': source,
                        '출처': 'Google News',
                        'source_type': 'domestic' if is_domestic else 'foreign'
                    })

                except Exception as e:
                    print(f"   ⚠️ 뉴스 항목 파싱 실패: {str(e)}")
                    continue

            print(f"✅ Google News {len(news_list)}개 수집 완료")
            return news_list

        except requests.exceptions.Timeout:
            print(f"⏰ Google News 타임아웃")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Google News API 오류: {str(e)}")
            return []
        except ET.ParseError as e:
            print(f"❌ XML 파싱 오류: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
            return []

    def get_finance_news(self, keyword, max_count=20):
        """
        금융/경제 뉴스 검색 (키워드 보강)

        Args:
            keyword (str): 기본 키워드
            max_count (int): 최대 뉴스 개수

        Returns:
            list: 뉴스 리스트
        """
        # 금융 관련 키워드 추가
        finance_keywords = [
            f"{keyword} 주가",
            f"{keyword} 실적",
            f"{keyword} 전망",
            f"{keyword} 투자"
        ]

        all_news = []
        seen_titles = set()  # 중복 제거

        for finance_keyword in finance_keywords:
            news_list = self.get_news(finance_keyword, max_count=max_count // len(finance_keywords))

            # 중복 제거
            for news in news_list:
                if news['제목'] not in seen_titles:
                    seen_titles.add(news['제목'])
                    all_news.append(news)

            time.sleep(0.5)  # Rate limiting

        print(f"\n✅ 총 {len(all_news)}개 금융 뉴스 수집 완료 (중복 제거)")
        return all_news

    def get_multi_source_news(self, keyword, max_count=30):
        """
        여러 소스에서 뉴스 수집

        Args:
            keyword (str): 검색 키워드
            max_count (int): 최대 뉴스 개수

        Returns:
            list: 통합 뉴스 리스트
        """
        print(f"\n{'='*60}")
        print(f"📡 다중 소스 뉴스 수집: '{keyword}'")
        print(f"{'='*60}\n")

        all_news = []

        # Google News
        google_news = self.get_news(keyword, max_count=max_count)
        all_news.extend(google_news)

        print(f"\n✅ 총 {len(all_news)}개 뉴스 수집 완료")
        return all_news


# 테스트 코드
if __name__ == "__main__":
    collector = GoogleNewsCollector()

    # 테스트 검색
    test_keywords = ['삼성전자', 'Bitcoin', 'NVIDIA']

    for keyword in test_keywords:
        news_list = collector.get_news(keyword, max_count=5)

        print(f"\n{'='*60}")
        print(f"🔍 '{keyword}' 검색 결과 ({len(news_list)}개)")
        print(f"{'='*60}\n")

        for i, news in enumerate(news_list, 1):
            print(f"{i}. {news['제목']}")
            print(f"   언론사: {news['언론사']}")
            print(f"   날짜: {news['날짜'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   링크: {news['링크'][:60]}...")
            print()

        time.sleep(1)  # Rate limiting
