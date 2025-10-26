# -*- coding: utf-8 -*-
"""
성과 추적 시스템
실시간 AI 추천 성과 모니터링
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta
import pandas as pd


class PerformanceTracker:
    """AI 추천 성과 추적기"""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'tracking_data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.tracking_file = os.path.join(self.data_dir, 'recommendations.json')

    def record_recommendation(self, ticker, name, hot_score, signal, confidence, rsi, current_price):
        """
        추천 기록 저장

        Args:
            ticker: 종목 코드
            name: 종목명
            hot_score: 핫 점수
            signal: 신호 (strong_buy, buy 등)
            confidence: 신뢰도
            rsi: RSI 값
            current_price: 현재가
        """
        record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'name': name,
            'hot_score': hot_score,
            'signal': signal,
            'confidence': confidence,
            'rsi': rsi,
            'entry_price': current_price,
            'status': 'active'  # active, closed
        }

        # 기존 데이터 로드
        recommendations = self._load_recommendations()
        recommendations.append(record)

        # 저장
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)

        print(f"✅ 추천 기록: {name} ({ticker}) - 핫 점수 {hot_score}")

    def update_recommendation(self, ticker, date, exit_price):
        """
        추천 종료 및 성과 업데이트

        Args:
            ticker: 종목 코드
            date: 추천 날짜
            exit_price: 청산가
        """
        recommendations = self._load_recommendations()

        for rec in recommendations:
            if rec['ticker'] == ticker and rec['date'] == date and rec['status'] == 'active':
                rec['exit_price'] = exit_price
                rec['exit_date'] = datetime.now().strftime('%Y-%m-%d')
                rec['profit_rate'] = ((exit_price - rec['entry_price']) / rec['entry_price']) * 100
                rec['status'] = 'closed'
                rec['success'] = rec['profit_rate'] > 0

                # 저장
                with open(self.tracking_file, 'w', encoding='utf-8') as f:
                    json.dump(recommendations, f, ensure_ascii=False, indent=2)

                print(f"✅ 추천 종료: {rec['name']} - 수익률 {rec['profit_rate']:+.2f}%")
                return True

        return False

    def get_performance_summary(self, days=30):
        """
        성과 요약 조회

        Args:
            days: 조회 기간 (일)

        Returns:
            dict: 성과 요약
        """
        recommendations = self._load_recommendations()

        if not recommendations:
            return {'message': '추천 기록 없음'}

        # 기간 필터링
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        filtered = [r for r in recommendations if r['date'] >= start_date]

        if not filtered:
            return {'message': f'최근 {days}일 추천 없음'}

        # 통계 계산
        total = len(filtered)
        closed = [r for r in filtered if r['status'] == 'closed']
        active = [r for r in filtered if r['status'] == 'active']

        if closed:
            success_count = sum(1 for r in closed if r.get('success', False))
            accuracy = (success_count / len(closed)) * 100
            avg_profit = sum(r.get('profit_rate', 0) for r in closed) / len(closed)
        else:
            success_count = 0
            accuracy = 0
            avg_profit = 0

        summary = {
            'period_days': days,
            'total_recommendations': total,
            'closed_positions': len(closed),
            'active_positions': len(active),
            'success_count': success_count,
            'fail_count': len(closed) - success_count,
            'accuracy': accuracy,
            'avg_profit_rate': avg_profit,
            'closed_details': closed[-10:],  # 최근 10개
            'active_details': active
        }

        return summary

    def _load_recommendations(self):
        """저장된 추천 로드"""
        if not os.path.exists(self.tracking_file):
            return []

        try:
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def generate_report(self, days=30):
        """
        성과 보고서 생성

        Args:
            days: 조회 기간 (일)
        """
        summary = self.get_performance_summary(days)

        if 'message' in summary:
            print(summary['message'])
            return

        print(f"\n{'='*60}")
        print(f"📊 AI 추천 성과 보고서 (최근 {days}일)")
        print(f"{'='*60}\n")

        print(f"총 추천: {summary['total_recommendations']}건")
        print(f"종료 포지션: {summary['closed_positions']}건")
        print(f"활성 포지션: {summary['active_positions']}건\n")

        if summary['closed_positions'] > 0:
            print(f"성공: {summary['success_count']}건")
            print(f"실패: {summary['fail_count']}건")
            print(f"정확도: {summary['accuracy']:.1f}%")
            print(f"평균 수익률: {summary['avg_profit_rate']:+.2f}%\n")

            print(f"최근 종료 포지션 (최대 10개):")
            for rec in summary['closed_details'][-10:]:
                print(f"  - {rec['name']} ({rec['date']}): {rec['profit_rate']:+.2f}% {'✓' if rec['success'] else '✗'}")

        if summary['active_positions'] > 0:
            print(f"\n활성 포지션:")
            for rec in summary['active_details']:
                print(f"  - {rec['name']} ({rec['date']}): 핫 점수 {rec['hot_score']}")

        print(f"\n{'='*60}\n")


if __name__ == '__main__':
    tracker = PerformanceTracker()
    tracker.generate_report(days=30)
