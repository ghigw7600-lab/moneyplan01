# -*- coding: utf-8 -*-
"""
KRX 전체 상장 종목 리스트 수집
코스피 + 코스닥 전체 종목 검색 가능
"""

import pandas as pd
import requests
from datetime import datetime
import json
import time

class KRXStockList:
    """한국거래소 전체 종목 리스트"""

    def __init__(self):
        self.stock_list = None
        self.last_update = None

    def fetch_all_stocks(self):
        """전체 상장 종목 가져오기 (FinanceDataReader 사용)"""
        try:
            import FinanceDataReader as fdr

            print("📊 KRX 전체 종목 리스트 로딩 중...")

            # 코스피
            kospi = fdr.StockListing('KOSPI')
            kospi['Market'] = 'KOSPI'
            kospi['Ticker'] = kospi['Code'] + '.KS'

            # 코스닥
            kosdaq = fdr.StockListing('KOSDAQ')
            kosdaq['Market'] = 'KOSDAQ'
            kosdaq['Ticker'] = kosdaq['Code'] + '.KQ'

            # 합치기
            all_stocks = pd.concat([kospi, kosdaq], ignore_index=True)

            # 필요한 컬럼만
            self.stock_list = all_stocks[['Ticker', 'Name', 'Market', 'Code']].copy()
            self.last_update = datetime.now()

            print(f"✅ 총 {len(self.stock_list)}개 종목 로딩 완료")

            return self.stock_list

        except ImportError:
            print("⚠️ FinanceDataReader 없음, 기본 종목만 제공")
            return self._get_default_stocks()
        except Exception as e:
            print(f"❌ 종목 리스트 로딩 실패: {e}")
            return self._get_default_stocks()

    def _get_default_stocks(self):
        """FinanceDataReader 없을 때 기본 주요 종목"""
        default_list = [
            # 시가총액 TOP 50
            ('005930.KS', '삼성전자', 'KOSPI', '005930'),
            ('000660.KS', 'SK하이닉스', 'KOSPI', '000660'),
            ('005380.KS', '현대차', 'KOSPI', '005380'),
            ('005490.KS', 'POSCO홀딩스', 'KOSPI', '005490'),
            ('035420.KS', 'NAVER', 'KOSPI', '035420'),
            ('000270.KS', '기아', 'KOSPI', '000270'),
            ('051910.KS', 'LG화학', 'KOSPI', '051910'),
            ('006400.KS', '삼성SDI', 'KOSPI', '006400'),
            ('035720.KQ', '카카오', 'KOSDAQ', '035720'),
            ('028260.KS', '삼성물산', 'KOSPI', '028260'),
            ('105560.KS', 'KB금융', 'KOSPI', '105560'),
            ('055550.KS', '신한지주', 'KOSPI', '055550'),
            ('012330.KS', '현대모비스', 'KOSPI', '012330'),
            ('066570.KS', 'LG전자', 'KOSPI', '066570'),
            ('017670.KS', 'SK텔레콤', 'KOSPI', '017670'),
            ('033780.KS', 'KT&G', 'KOSPI', '033780'),
            ('096770.KS', 'SK이노베이션', 'KOSPI', '096770'),
            ('009150.KS', '삼성전기', 'KOSPI', '009150'),
            ('032830.KS', '삼성생명', 'KOSPI', '032830'),
            ('086790.KS', '하나금융지주', 'KOSPI', '086790'),
            ('003550.KS', 'LG', 'KOSPI', '003550'),
            ('018260.KS', '삼성에스디에스', 'KOSPI', '018260'),
            ('068270.KQ', '셀트리온', 'KOSDAQ', '068270'),
            ('207940.KS', '삼성바이오로직스', 'KOSPI', '207940'),
            ('251270.KS', '넷마블', 'KOSPI', '251270'),
            ('036570.KS', '엔씨소프트', 'KOSPI', '036570'),
            ('009830.KS', '한화솔루션', 'KOSPI', '009830'),
            ('034730.KS', 'SK', 'KOSPI', '034730'),
            ('010950.KS', 'S-Oil', 'KOSPI', '010950'),
            ('032640.KS', 'LG유플러스', 'KOSPI', '032640'),
            ('138040.KS', '메리츠금융지주', 'KOSPI', '138040'),
            ('015760.KS', '한국전력', 'KOSPI', '015760'),
            ('011200.KS', 'HMM', 'KOSPI', '011200'),
            ('030200.KS', 'KT', 'KOSPI', '030200'),
            ('003670.KS', '포스코퓨처엠', 'KOSPI', '003670'),
            ('009540.KS', '한국조선해양', 'KOSPI', '009540'),
            ('024110.KS', '기업은행', 'KOSPI', '024110'),
            ('010130.KS', '고려아연', 'KOSPI', '010130'),
            ('047810.KS', '한국항공우주', 'KOSPI', '047810'),
            ('042700.KS', '한미반도체', 'KOSPI', '042700'),
            ('000810.KS', '삼성화재', 'KOSPI', '000810'),
            ('161390.KS', '한국타이어앤테크놀로지', 'KOSPI', '161390'),
            ('000720.KS', '현대건설', 'KOSPI', '000720'),
            ('011170.KS', '롯데케미칼', 'KOSPI', '011170'),
            ('005830.KS', 'DB손해보험', 'KOSPI', '005830'),
            ('001450.KS', '현대해상', 'KOSPI', '001450'),
            ('088980.KS', '맥쿼리인프라', 'KOSPI', '088980'),
            ('010140.KS', '삼성중공업', 'KOSPI', '010140'),
            ('004020.KS', '현대제철', 'KOSPI', '004020'),
            ('373220.KS', 'LG에너지솔루션', 'KOSPI', '373220'),
        ]

        self.stock_list = pd.DataFrame(default_list, columns=['Ticker', 'Name', 'Market', 'Code'])
        self.last_update = datetime.now()

        return self.stock_list

    def search_stocks(self, query, limit=20):
        """
        종목 검색

        Args:
            query: 검색어 (종목명 또는 코드 일부)
            limit: 최대 결과 개수

        Returns:
            list: 검색 결과
        """
        if self.stock_list is None:
            self.fetch_all_stocks()

        query = query.strip().upper()

        # 검색: 종목명 또는 코드에 포함
        results = self.stock_list[
            self.stock_list['Name'].str.contains(query, na=False, case=False) |
            self.stock_list['Code'].str.contains(query, na=False) |
            self.stock_list['Ticker'].str.contains(query, na=False)
        ].head(limit)

        # 딕셔너리 리스트로 변환
        return [
            {
                'ticker': row['Ticker'],
                'name': row['Name'],
                'market': row['Market'],
                'code': row['Code']
            }
            for _, row in results.iterrows()
        ]

    def get_ticker_by_name(self, name):
        """종목명으로 티커 찾기"""
        if self.stock_list is None:
            self.fetch_all_stocks()

        result = self.stock_list[self.stock_list['Name'] == name]

        if not result.empty:
            return result.iloc[0]['Ticker']

        return None


# 전역 인스턴스 (캐싱)
_krx_list = None

def get_krx_list():
    """전역 KRX 리스트 인스턴스"""
    global _krx_list
    if _krx_list is None:
        _krx_list = KRXStockList()
        _krx_list.fetch_all_stocks()
    return _krx_list


if __name__ == "__main__":
    # 테스트
    krx = KRXStockList()
    krx.fetch_all_stocks()

    print("\n=== 검색 테스트 ===")

    # 삼성 검색
    results = krx.search_stocks("삼성")
    print(f"\n'삼성' 검색 결과: {len(results)}개")
    for r in results[:5]:
        print(f"  {r['name']} ({r['ticker']}) - {r['market']}")

    # 에이디 검색
    results = krx.search_stocks("에이디")
    print(f"\n'에이디' 검색 결과: {len(results)}개")
    for r in results[:5]:
        print(f"  {r['name']} ({r['ticker']}) - {r['market']}")

    # 코드 검색
    results = krx.search_stocks("005930")
    print(f"\n'005930' 검색 결과: {len(results)}개")
    for r in results[:5]:
        print(f"  {r['name']} ({r['ticker']}) - {r['market']}")
