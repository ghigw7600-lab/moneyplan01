# -*- coding: utf-8 -*-
"""
백테스팅 엔진
과거 데이터로 AI 추천 정확도 검증
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
import json
from collectors.stock_collector import StockCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from auto_recommender import AutoRecommender


class BacktestEngine:
    """백테스팅 엔진 - 과거 데이터 기반 AI 추천 검증"""

    def __init__(self):
        self.stock_collector = StockCollector()
        self.results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(self.results_dir, exist_ok=True)

    def backtest_single_stock(self, ticker, start_date, end_date, hold_days=5):
        """
        단일 종목 백테스트

        Args:
            ticker: 종목 코드
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            hold_days: 보유 기간 (일)

        Returns:
            dict: 백테스트 결과
        """
        print(f"\n📊 백테스트 시작: {ticker}")
        print(f"기간: {start_date} ~ {end_date}")
        print(f"보유 기간: {hold_days}일\n")

        # 과거 데이터 수집
        price_data = self.stock_collector.get_stock_data(ticker, period='1y')
        if price_data is None or price_data.empty:
            return {'error': '데이터 수집 실패'}

        # 날짜 필터링
        price_data.index = pd.to_datetime(price_data.index)
        mask = (price_data.index >= start_date) & (price_data.index <= end_date)
        test_data = price_data[mask]

        if test_data.empty:
            return {'error': '해당 기간 데이터 없음'}

        # 기술적 분석
        tech_analyzer = TechnicalAnalyzer(test_data)
        technical_result = tech_analyzer.analyze_all()

        # 매수 신호 확인
        signals = technical_result.get('signals', [])
        buy_signals = [s for s in signals if '매수' in s]

        # 결과 계산
        entry_price = float(test_data['Close'].iloc[0])

        # hold_days 후 가격 (또는 마지막 날 가격)
        if len(test_data) > hold_days:
            exit_price = float(test_data['Close'].iloc[hold_days])
        else:
            exit_price = float(test_data['Close'].iloc[-1])

        profit_rate = ((exit_price - entry_price) / entry_price) * 100

        result = {
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'hold_days': hold_days,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'profit_rate': profit_rate,
            'buy_signals': len(buy_signals),
            'rsi': technical_result.get('rsi'),
            'macd_signal': technical_result.get('macd', {}).get('signal'),
            'success': profit_rate > 0
        }

        print(f"✅ 진입가: {entry_price:,.0f}원")
        print(f"✅ 청산가: {exit_price:,.0f}원")
        print(f"✅ 수익률: {profit_rate:+.2f}%")
        print(f"✅ 결과: {'성공 ✓' if result['success'] else '실패 ✗'}\n")

        return result

    def backtest_hot_stocks(self, test_date, hold_days=5):
        """
        특정 날짜의 핫 종목 추천 백테스트

        Args:
            test_date: 테스트 날짜 (YYYY-MM-DD)
            hold_days: 보유 기간 (일)

        Returns:
            dict: 전체 백테스트 결과
        """
        print(f"\n{'='*60}")
        print(f"🔥 핫 종목 추천 백테스트")
        print(f"테스트 날짜: {test_date}")
        print(f"보유 기간: {hold_days}일")
        print(f"{'='*60}\n")

        # 과거 시점으로 시뮬레이션 (실제로는 해당 날짜 데이터 사용)
        # 간단히 상위 10개 종목 테스트
        test_tickers = [
            '005930.KS',  # 삼성전자
            '000660.KS',  # SK하이닉스
            '035720.KS',  # 카카오
            '035420.KS',  # NAVER
            '051910.KS',  # LG화학
            '006400.KS',  # 삼성SDI
            '207940.KS',  # 삼성바이오로직스
            '005380.KS',  # 현대차
            '068270.KS',  # 셀트리온
            '003670.KS',  # 포스코퓨처엠
        ]

        results = []
        for ticker in test_tickers:
            try:
                result = self.backtest_single_stock(
                    ticker,
                    test_date,
                    (pd.to_datetime(test_date) + timedelta(days=hold_days+10)).strftime('%Y-%m-%d'),
                    hold_days
                )
                if 'error' not in result:
                    results.append(result)
            except Exception as e:
                print(f"⚠️ {ticker} 백테스트 실패: {e}")
                continue

        # 통계 계산
        if results:
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            accuracy = (success_count / total_count) * 100
            avg_profit = sum(r['profit_rate'] for r in results) / total_count

            summary = {
                'test_date': test_date,
                'total_tests': total_count,
                'success_count': success_count,
                'fail_count': total_count - success_count,
                'accuracy': accuracy,
                'avg_profit_rate': avg_profit,
                'results': results
            }

            print(f"\n{'='*60}")
            print(f"📊 백테스트 결과 요약")
            print(f"{'='*60}")
            print(f"총 테스트: {total_count}개")
            print(f"성공: {success_count}개")
            print(f"실패: {total_count - success_count}개")
            print(f"정확도: {accuracy:.1f}%")
            print(f"평균 수익률: {avg_profit:+.2f}%")
            print(f"{'='*60}\n")

            # 결과 저장
            self._save_results(summary)

            return summary
        else:
            return {'error': '백테스트 실패'}

    def _save_results(self, summary):
        """백테스트 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_{summary['test_date']}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"💾 결과 저장: {filename}")

    def run_multi_period_test(self, periods=5, hold_days=5):
        """
        여러 기간 백테스트 (최근 N개월)

        Args:
            periods: 테스트 기간 수 (개월)
            hold_days: 보유 기간 (일)
        """
        print(f"\n{'='*60}")
        print(f"📅 다중 기간 백테스트")
        print(f"테스트 기간: 최근 {periods}개월")
        print(f"{'='*60}\n")

        all_results = []
        today = datetime.now()

        for i in range(periods):
            test_date = (today - timedelta(days=30 * (i + 1))).strftime('%Y-%m-%d')
            result = self.backtest_hot_stocks(test_date, hold_days)

            if 'error' not in result:
                all_results.append(result)

        # 전체 통계
        if all_results:
            total_accuracy = sum(r['accuracy'] for r in all_results) / len(all_results)
            total_avg_profit = sum(r['avg_profit_rate'] for r in all_results) / len(all_results)

            print(f"\n{'='*60}")
            print(f"🎯 전체 백테스트 결과")
            print(f"{'='*60}")
            print(f"테스트 기간: {len(all_results)}개월")
            print(f"전체 평균 정확도: {total_accuracy:.1f}%")
            print(f"전체 평균 수익률: {total_avg_profit:+.2f}%")
            print(f"{'='*60}\n")

            return {
                'periods': periods,
                'results': all_results,
                'overall_accuracy': total_accuracy,
                'overall_avg_profit': total_avg_profit
            }


if __name__ == '__main__':
    engine = BacktestEngine()

    # 최근 3개월 백테스트
    engine.run_multi_period_test(periods=3, hold_days=5)
