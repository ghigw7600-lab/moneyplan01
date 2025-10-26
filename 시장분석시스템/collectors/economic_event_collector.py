# -*- coding: utf-8 -*-
"""
경제 이벤트 캘린더 Collector
주요 경제 지표 발표, 중앙은행 회의, 국제 정상회의 등 추적
"""
import sys
import io

# Windows 한글 출력 문제 해결 (__main__일 때만)
if __name__ == "__main__" and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except ValueError:
        pass

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
import os


class EconomicEventCollector:
    """경제 이벤트 수집기 (Phase 4-1: 캐시 시스템 추가)"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Phase 4-1: 캐시 설정
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, 'economic_events.json')
        self.cache_validity = 86400  # 1일 (24시간 = 86400초)

        # 주요 이벤트 카테고리
        self.event_categories = {
            'central_bank': '중앙은행 회의',
            'economic_data': '경제 지표',
            'summit': '국제 정상회의',
            'earnings': '기업 실적',
            'policy': '정책 발표'
        }

        # 중요도 가중치
        self.importance_weights = {
            'high': 3,      # 시장에 큰 영향
            'medium': 2,    # 중간 영향
            'low': 1        # 작은 영향
        }

    def _load_cache(self):
        """캐시에서 데이터 로드"""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 캐시 유효성 확인
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > self.cache_validity:
                print("⏰ 캐시 만료 (1일 경과)")
                return None

            print("✅ 캐시 사용 중 (1일 이내)")
            return cache_data.get('events', [])
        except Exception as e:
            print(f"⚠️ 캐시 로드 실패: {e}")
            return None

    def _save_cache(self, events):
        """캐시에 데이터 저장"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'events': events
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print("💾 캐시 저장 완료 (1일 유효)")
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

    def get_upcoming_events(self, days=30, use_cache=True):
        """
        향후 N일간의 주요 경제 이벤트 조회 (Phase 4-1: 캐시 지원)

        Args:
            days (int): 조회 기간 (일)
            use_cache (bool): 캐시 사용 여부

        Returns:
            list: 경제 이벤트 리스트
        """
        # Phase 4-1: 캐시 확인
        if use_cache:
            cached_events = self._load_cache()
            if cached_events is not None:
                return cached_events

        print(f"\n{'='*60}")
        print(f"📅 향후 {days}일간의 경제 이벤트 수집 중...")
        print(f"{'='*60}\n")

        events = []

        # 1. Investing.com 경제 캘린더 스크래핑 (실제 구현은 복잡하므로 모의 데이터)
        events.extend(self._get_investing_calendar())

        # 2. 주요 중앙은행 회의 일정
        events.extend(self._get_central_bank_meetings())

        # Phase 4-1: 캐시 저장
        if use_cache:
            self._save_cache(events)

        return events

    def _collect_events_internal(self, days=30):
        """내부 수집 로직 (캐시 없이)"""
        events = []

        # 3. 국제 정상회의/포럼
        events.extend(self._get_international_summits())

        # 4. 주요 기업 실적 발표
        events.extend(self._get_earnings_calendar())

        # 날짜순 정렬
        events.sort(key=lambda x: x['date'])

        # days 이내 이벤트만 필터링
        end_date = datetime.now() + timedelta(days=days)
        events = [e for e in events if datetime.fromisoformat(e['date']) <= end_date]

        print(f"✅ 총 {len(events)}개 경제 이벤트 수집 완료\n")
        return events

    def _get_investing_calendar(self):
        """
        Investing.com 경제 캘린더

        실제로는 웹 스크래핑 또는 API 사용
        여기서는 주요 경제 지표 발표 일정 시뮬레이션
        """
        print("📊 경제 지표 발표 일정 수집 중...")

        # 주요 경제 지표 발표 일정 (예시)
        indicators = [
            {
                'name': '미국 고용지표 (NFP)',
                'country': 'US',
                'category': 'economic_data',
                'importance': 'high',
                'frequency': 'monthly',
                'typical_day': 1,  # 매월 첫째 금요일
                'description': '비농업 고용 인구 변화. 미국 경제 건강도의 핵심 지표',
                'impact': ['달러화', 'S&P500', '금리']
            },
            {
                'name': '미국 소비자물가지수 (CPI)',
                'country': 'US',
                'category': 'economic_data',
                'importance': 'high',
                'frequency': 'monthly',
                'typical_day': 13,
                'description': '인플레이션 측정. 연준 금리 결정에 큰 영향',
                'impact': ['금리', '채권', '주식']
            },
            {
                'name': '미국 GDP 성장률',
                'country': 'US',
                'category': 'economic_data',
                'importance': 'high',
                'frequency': 'quarterly',
                'typical_day': 28,
                'description': '경제 성장 속도 측정',
                'impact': ['주식', '달러화', '경기민감주']
            },
            {
                'name': '한국 수출입 통계',
                'country': 'KR',
                'category': 'economic_data',
                'importance': 'medium',
                'frequency': 'monthly',
                'typical_day': 1,
                'description': '한국 경제 건강도 지표',
                'impact': ['코스피', '수출주', '조선/반도체']
            }
        ]

        events = []
        current_date = datetime.now()

        for indicator in indicators:
            # 향후 2개월치 일정 생성
            for month_offset in range(3):
                target_month = current_date.month + month_offset
                target_year = current_date.year

                if target_month > 12:
                    target_month -= 12
                    target_year += 1

                event_date = datetime(target_year, target_month, indicator['typical_day'])

                # 과거 날짜 제외
                if event_date < current_date:
                    continue

                events.append({
                    'date': event_date.isoformat(),
                    'name': indicator['name'],
                    'category': indicator['category'],
                    'importance': indicator['importance'],
                    'country': indicator['country'],
                    'description': indicator['description'],
                    'impact_areas': indicator['impact'],
                    'source': 'economic_calendar'
                })

        print(f"   ✅ {len(events)}개 경제 지표 일정 추가")
        return events

    def _get_central_bank_meetings(self):
        """
        주요 중앙은행 회의 일정

        실제로는 각 중앙은행 공식 웹사이트에서 스크래핑
        """
        print("🏛️ 중앙은행 회의 일정 수집 중...")

        # 2025년 주요 중앙은행 회의 일정 (예시)
        meetings = [
            {
                'name': 'FOMC 정례회의 (미국 연준)',
                'date': '2025-11-07',
                'importance': 'high',
                'description': '미국 기준금리 결정. 글로벌 금융시장에 막대한 영향',
                'impact': ['금리', '달러화', '글로벌 주식', '채권']
            },
            {
                'name': 'ECB 통화정책회의 (유럽중앙은행)',
                'date': '2025-11-14',
                'importance': 'high',
                'description': '유로존 금리 및 통화정책 결정',
                'impact': ['유로화', '유럽주식', '유로채권']
            },
            {
                'name': '한국은행 금융통화위원회',
                'date': '2025-11-21',
                'importance': 'medium',
                'description': '한국 기준금리 결정',
                'impact': ['코스피', '원/달러', '금리']
            },
            {
                'name': 'BOJ 금융정책결정회의 (일본은행)',
                'date': '2025-11-28',
                'importance': 'medium',
                'description': '일본 통화정책 결정',
                'impact': ['엔화', '일본주식', '아시아증시']
            }
        ]

        events = []
        for meeting in meetings:
            events.append({
                'date': meeting['date'],
                'name': meeting['name'],
                'category': 'central_bank',
                'importance': meeting['importance'],
                'country': meeting['name'].split('(')[1].split(')')[0] if '(' in meeting['name'] else 'Global',
                'description': meeting['description'],
                'impact_areas': meeting['impact'],
                'source': 'central_bank'
            })

        print(f"   ✅ {len(events)}개 중앙은행 회의 일정 추가")
        return events

    def _get_international_summits(self):
        """국제 정상회의 및 주요 포럼"""
        print("🌍 국제 정상회의 일정 수집 중...")

        summits = [
            {
                'name': 'APEC 정상회의 2025',
                'date': '2025-11-15',
                'importance': 'high',
                'description': '아시아태평양 경제협력체 정상회의. 무역, 투자 정책 논의',
                'impact': ['아시아증시', '무역주', '환율']
            },
            {
                'name': 'G20 재무장관 회의',
                'date': '2025-11-20',
                'importance': 'medium',
                'description': 'G20 재무장관 및 중앙은행 총재 회의',
                'impact': ['글로벌증시', '달러', '금리']
            }
        ]

        events = []
        for summit in summits:
            events.append({
                'date': summit['date'],
                'name': summit['name'],
                'category': 'summit',
                'importance': summit['importance'],
                'country': 'Global',
                'description': summit['description'],
                'impact_areas': summit['impact'],
                'source': 'summit'
            })

        print(f"   ✅ {len(events)}개 국제회의 일정 추가")
        return events

    def _get_earnings_calendar(self):
        """주요 기업 실적 발표 일정"""
        print("💼 주요 기업 실적 발표 일정 수집 중...")

        # 주요 빅테크 기업 실적 발표 (예시)
        earnings = [
            {
                'name': 'Apple 분기 실적 발표',
                'ticker': 'AAPL',
                'date': '2025-11-01',
                'importance': 'high',
                'description': '애플 분기 실적 및 가이던스 발표',
                'impact': ['NASDAQ', '테크주', '반도체']
            },
            {
                'name': 'Microsoft 분기 실적 발표',
                'ticker': 'MSFT',
                'date': '2025-11-05',
                'importance': 'high',
                'description': '마이크로소프트 실적 및 클라우드 전망',
                'impact': ['NASDAQ', '클라우드', 'AI']
            },
            {
                'name': '삼성전자 분기 실적 발표',
                'ticker': '005930.KS',
                'date': '2025-11-08',
                'importance': 'high',
                'description': '삼성전자 반도체/스마트폰 사업 실적',
                'impact': ['코스피', '반도체', '전자']
            }
        ]

        events = []
        for earning in earnings:
            events.append({
                'date': earning['date'],
                'name': earning['name'],
                'ticker': earning.get('ticker'),
                'category': 'earnings',
                'importance': earning['importance'],
                'country': 'KR' if '.KS' in earning.get('ticker', '') else 'US',
                'description': earning['description'],
                'impact_areas': earning['impact'],
                'source': 'earnings'
            })

        print(f"   ✅ {len(events)}개 실적 발표 일정 추가")
        return events

    def filter_events_by_stock(self, events, stock_name, stock_ticker):
        """
        특정 종목과 관련된 이벤트 필터링

        Args:
            events (list): 전체 이벤트 리스트
            stock_name (str): 종목명
            stock_ticker (str): 티커

        Returns:
            list: 관련 이벤트 리스트
        """
        relevant_events = []

        # 종목 관련 키워드 (예: 삼성전자 → 반도체, 전자, 한국, 수출)
        keywords_map = {
            '삼성전자': ['반도체', '전자', '코스피', '한국', '수출', 'IT'],
            'SK하이닉스': ['반도체', 'DRAM', '메모리', '코스피', '한국'],
            'NAVER': ['IT', '플랫폼', '코스피', '한국', '인터넷'],
            '현대차': ['자동차', '전기차', 'EV', '코스피', '한국'],
        }

        stock_keywords = keywords_map.get(stock_name, [stock_name, '코스피', '한국'])

        for event in events:
            # 직접 매칭 (티커 또는 종목명)
            if event.get('ticker') == stock_ticker or stock_name in event['name']:
                event['relevance'] = 'direct'
                relevant_events.append(event)
                continue

            # 간접 매칭 (영향 영역 또는 키워드)
            impact_areas = event.get('impact_areas', [])
            description = event.get('description', '')

            # 키워드 매칭
            if any(keyword in description or keyword in ' '.join(impact_areas) for keyword in stock_keywords):
                event['relevance'] = 'indirect'
                relevant_events.append(event)

        return relevant_events

    def get_event_impact_score(self, event):
        """
        이벤트의 시장 영향도 점수 계산

        Returns:
            int: 0-100 점수
        """
        importance_score = self.importance_weights.get(event['importance'], 1) * 20

        # 카테고리별 가중치
        category_weight = {
            'central_bank': 1.5,
            'economic_data': 1.3,
            'summit': 1.2,
            'earnings': 1.0,
            'policy': 1.1
        }

        weight = category_weight.get(event['category'], 1.0)

        return min(100, int(importance_score * weight))


# 테스트 코드
if __name__ == "__main__":
    collector = EconomicEventCollector()

    # 향후 30일간의 이벤트
    events = collector.get_upcoming_events(days=30)

    print(f"\n{'='*60}")
    print(f"📅 향후 30일간의 주요 경제 이벤트")
    print(f"{'='*60}\n")

    for event in events[:10]:  # 상위 10개만 출력
        impact_score = collector.get_event_impact_score(event)
        print(f"📅 {event['date'][:10]}")
        print(f"   {event['name']}")
        print(f"   중요도: {event['importance']} | 영향도: {impact_score}점")
        print(f"   {event['description']}")
        print(f"   영향: {', '.join(event.get('impact_areas', []))}")
        print()

    # 삼성전자 관련 이벤트 필터링
    print(f"\n{'='*60}")
    print(f"🔍 삼성전자 관련 이벤트")
    print(f"{'='*60}\n")

    relevant = collector.filter_events_by_stock(events, '삼성전자', '005930.KS')
    for event in relevant:
        print(f"📅 {event['date'][:10]} - {event['name']} ({event['relevance']})")
        print(f"   {event['description']}\n")
