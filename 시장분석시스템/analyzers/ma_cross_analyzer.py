"""
이동평균선 크로스 전략 분석기 (Phase 3-3)

주요 기능:
1. 이동평균선 크로스 감지
   - 골든크로스 (Golden Cross): 단기선이 장기선을 상향 돌파 → 매수 신호
   - 데드크로스 (Dead Cross): 단기선이 장기선을 하향 돌파 → 매도 신호

2. 다중 이동평균선 배열 분석
   - 5일/20일/60일/120일 이동평균선
   - 정배열: 5일 > 20일 > 60일 > 120일 (강한 상승 추세)
   - 역배열: 5일 < 20일 < 60일 < 120일 (강한 하락 추세)

3. 이격도 분석
   - 현재가와 이동평균선 간의 거리
   - 과열/과매도 구간 판단
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class MovingAverageCrossAnalyzer:
    """이동평균선 크로스 전략 분석기"""

    def __init__(self, short_period=5, medium_period=20, long_period=60, super_long_period=120):
        """
        초기화

        Args:
            short_period: 단기 이동평균선 (기본값: 5일)
            medium_period: 중기 이동평균선 (기본값: 20일)
            long_period: 장기 이동평균선 (기본값: 60일)
            super_long_period: 초장기 이동평균선 (기본값: 120일)
        """
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period
        self.super_long_period = super_long_period

    def analyze(self, df):
        """
        이동평균선 종합 분석

        Args:
            df: OHLCV 데이터프레임 (columns: Open, High, Low, Close, Volume)

        Returns:
            dict: 분석 결과
        """
        if len(df) < self.super_long_period + 5:
            return {
                'moving_averages': {},
                'crosses': [],
                'alignment': {},
                'disparity': {},
                'signal': 'neutral',
                'score': 50,
                'recommendations': []
            }

        # 1. 이동평균선 계산
        ma_data = self._calculate_moving_averages(df)

        # 2. 골든크로스/데드크로스 감지
        crosses = self._detect_crosses(df, ma_data)

        # 3. 이동평균선 배열 분석
        alignment = self._analyze_alignment(ma_data)

        # 4. 이격도 분석
        disparity = self._analyze_disparity(df, ma_data)

        # 5. 종합 시그널 생성
        signal, score = self._generate_signal(crosses, alignment, disparity)

        # 6. 투자 전략 추천
        recommendations = self._generate_recommendations(crosses, alignment, disparity, signal)

        return {
            'moving_averages': ma_data,
            'crosses': crosses,
            'alignment': alignment,
            'disparity': disparity,
            'signal': signal,
            'score': score,
            'recommendations': recommendations
        }

    # ==================== 이동평균선 계산 ====================

    def _calculate_moving_averages(self, df):
        """이동평균선 계산"""
        df_copy = df.copy()

        # 각 기간의 이동평균선 계산
        df_copy['MA5'] = df_copy['Close'].rolling(window=self.short_period).mean()
        df_copy['MA20'] = df_copy['Close'].rolling(window=self.medium_period).mean()
        df_copy['MA60'] = df_copy['Close'].rolling(window=self.long_period).mean()
        df_copy['MA120'] = df_copy['Close'].rolling(window=self.super_long_period).mean()

        # 최근 데이터
        latest = df_copy.iloc[-1]
        current_price = latest['Close']

        return {
            'current_price': float(current_price),
            'ma5': float(latest['MA5']) if not pd.isna(latest['MA5']) else None,
            'ma20': float(latest['MA20']) if not pd.isna(latest['MA20']) else None,
            'ma60': float(latest['MA60']) if not pd.isna(latest['MA60']) else None,
            'ma120': float(latest['MA120']) if not pd.isna(latest['MA120']) else None,
            'df_with_ma': df_copy  # 크로스 감지용
        }

    # ==================== 골든크로스/데드크로스 감지 ====================

    def _detect_crosses(self, df, ma_data):
        """골든크로스/데드크로스 감지"""
        crosses = []
        df_ma = ma_data['df_with_ma']

        # 최근 데이터만 확인 (최근 5일)
        if len(df_ma) < 5:
            return crosses

        recent_df = df_ma.tail(5)

        # 1. MA5 x MA20 크로스 (단기)
        cross_5_20 = self._check_cross(recent_df, 'MA5', 'MA20')
        if cross_5_20:
            crosses.append({
                'type': cross_5_20['type'],
                'short_ma': 5,
                'long_ma': 20,
                'date': cross_5_20['date'],
                'price': cross_5_20['price'],
                'strength': 'short_term',
                'reliability': 60,
                'description': f"5일선이 20일선을 {'상향' if cross_5_20['type'] == 'golden' else '하향'} 돌파 (단기 {'상승' if cross_5_20['type'] == 'golden' else '하락'} 신호)",
                'icon': '🟢' if cross_5_20['type'] == 'golden' else '🔴'
            })

        # 2. MA5 x MA60 크로스 (중기)
        cross_5_60 = self._check_cross(recent_df, 'MA5', 'MA60')
        if cross_5_60:
            crosses.append({
                'type': cross_5_60['type'],
                'short_ma': 5,
                'long_ma': 60,
                'date': cross_5_60['date'],
                'price': cross_5_60['price'],
                'strength': 'medium_term',
                'reliability': 70,
                'description': f"5일선이 60일선을 {'상향' if cross_5_60['type'] == 'golden' else '하향'} 돌파 (중기 {'상승' if cross_5_60['type'] == 'golden' else '하락'} 신호)",
                'icon': '🟢🟢' if cross_5_60['type'] == 'golden' else '🔴🔴'
            })

        # 3. MA20 x MA60 크로스 (중장기) - 가장 중요
        cross_20_60 = self._check_cross(recent_df, 'MA20', 'MA60')
        if cross_20_60:
            crosses.append({
                'type': cross_20_60['type'],
                'short_ma': 20,
                'long_ma': 60,
                'date': cross_20_60['date'],
                'price': cross_20_60['price'],
                'strength': 'long_term',
                'reliability': 85,
                'description': f"20일선이 60일선을 {'상향' if cross_20_60['type'] == 'golden' else '하향'} 돌파 (장기 {'상승' if cross_20_60['type'] == 'golden' else '하락'} 추세 전환)",
                'icon': '🟢🟢🟢' if cross_20_60['type'] == 'golden' else '🔴🔴🔴'
            })

        # 4. MA60 x MA120 크로스 (초장기)
        cross_60_120 = self._check_cross(recent_df, 'MA60', 'MA120')
        if cross_60_120:
            crosses.append({
                'type': cross_60_120['type'],
                'short_ma': 60,
                'long_ma': 120,
                'date': cross_60_120['date'],
                'price': cross_60_120['price'],
                'strength': 'super_long_term',
                'reliability': 90,
                'description': f"60일선이 120일선을 {'상향' if cross_60_120['type'] == 'golden' else '하향'} 돌파 (초장기 추세 대전환)",
                'icon': '⭐🟢⭐' if cross_60_120['type'] == 'golden' else '⭐🔴⭐'
            })

        return crosses

    def _check_cross(self, df, short_ma, long_ma):
        """두 이동평균선의 크로스 체크"""
        if len(df) < 2:
            return None

        # 현재와 이전 데이터
        current = df.iloc[-1]
        previous = df.iloc[-2]

        # NaN 체크
        if pd.isna(current[short_ma]) or pd.isna(current[long_ma]) or \
           pd.isna(previous[short_ma]) or pd.isna(previous[long_ma]):
            return None

        # 골든크로스: 단기선이 장기선을 아래→위로 돌파
        if previous[short_ma] <= previous[long_ma] and current[short_ma] > current[long_ma]:
            return {
                'type': 'golden',
                'date': current.name,
                'price': current['Close']
            }

        # 데드크로스: 단기선이 장기선을 위→아래로 돌파
        if previous[short_ma] >= previous[long_ma] and current[short_ma] < current[long_ma]:
            return {
                'type': 'dead',
                'date': current.name,
                'price': current['Close']
            }

        return None

    # ==================== 이동평균선 배열 분석 ====================

    def _analyze_alignment(self, ma_data):
        """이동평균선 배열 분석 (정배열/역배열)"""
        ma5 = ma_data['ma5']
        ma20 = ma_data['ma20']
        ma60 = ma_data['ma60']
        ma120 = ma_data['ma120']
        current_price = ma_data['current_price']

        # NaN 체크
        if any(ma is None for ma in [ma5, ma20, ma60, ma120]):
            return {
                'type': 'unknown',
                'description': '이동평균선 계산 중',
                'score': 50
            }

        # 완벽한 정배열: 현재가 > MA5 > MA20 > MA60 > MA120
        is_perfect_bull = (current_price > ma5 > ma20 > ma60 > ma120)

        # 완벽한 역배열: 현재가 < MA5 < MA20 < MA60 < MA120
        is_perfect_bear = (current_price < ma5 < ma20 < ma60 < ma120)

        # 부분 정배열 점수 계산
        bull_count = 0
        if current_price > ma5: bull_count += 1
        if ma5 > ma20: bull_count += 1
        if ma20 > ma60: bull_count += 1
        if ma60 > ma120: bull_count += 1

        if is_perfect_bull:
            return {
                'type': 'perfect_bull',
                'description': '⭐ 완벽한 정배열 - 강한 상승 추세',
                'score': 100,
                'details': f"현재가({current_price:.0f}) > 5일({ma5:.0f}) > 20일({ma20:.0f}) > 60일({ma60:.0f}) > 120일({ma120:.0f})",
                'icon': '📈'
            }
        elif is_perfect_bear:
            return {
                'type': 'perfect_bear',
                'description': '⭐ 완벽한 역배열 - 강한 하락 추세',
                'score': 0,
                'details': f"현재가({current_price:.0f}) < 5일({ma5:.0f}) < 20일({ma20:.0f}) < 60일({ma60:.0f}) < 120일({ma120:.0f})",
                'icon': '📉'
            }
        elif bull_count >= 3:
            return {
                'type': 'partial_bull',
                'description': f'부분 정배열 ({bull_count}/4) - 상승 추세',
                'score': 50 + (bull_count * 10),
                'details': self._get_alignment_details(current_price, ma5, ma20, ma60, ma120),
                'icon': '↗️'
            }
        elif bull_count <= 1:
            return {
                'type': 'partial_bear',
                'description': f'부분 역배열 ({4-bull_count}/4) - 하락 추세',
                'score': 50 - ((4-bull_count) * 10),
                'details': self._get_alignment_details(current_price, ma5, ma20, ma60, ma120),
                'icon': '↘️'
            }
        else:
            return {
                'type': 'mixed',
                'description': '혼조 배열 - 방향성 불분명',
                'score': 50,
                'details': self._get_alignment_details(current_price, ma5, ma20, ma60, ma120),
                'icon': '➡️'
            }

    def _get_alignment_details(self, price, ma5, ma20, ma60, ma120):
        """배열 상세 정보"""
        return (
            f"현재가: {price:.0f}원\n"
            f"5일선: {ma5:.0f}원 ({'+' if price > ma5 else ''}{((price/ma5-1)*100):.1f}%)\n"
            f"20일선: {ma20:.0f}원 ({'+' if price > ma20 else ''}{((price/ma20-1)*100):.1f}%)\n"
            f"60일선: {ma60:.0f}원 ({'+' if price > ma60 else ''}{((price/ma60-1)*100):.1f}%)\n"
            f"120일선: {ma120:.0f}원 ({'+' if price > ma120 else ''}{((price/ma120-1)*100):.1f}%)"
        )

    # ==================== 이격도 분석 ====================

    def _analyze_disparity(self, df, ma_data):
        """이격도 분석 (현재가와 이동평균선 간 거리)"""
        current_price = ma_data['current_price']
        ma20 = ma_data['ma20']
        ma60 = ma_data['ma60']
        ma120 = ma_data['ma120']

        if ma20 is None or ma60 is None or ma120 is None:
            return {
                'disparity_20': None,
                'disparity_60': None,
                'disparity_120': None,
                'status': 'calculating',
                'description': '이격도 계산 중'
            }

        # 이격도 = (현재가 / 이동평균) * 100
        disparity_20 = (current_price / ma20) * 100
        disparity_60 = (current_price / ma60) * 100
        disparity_120 = (current_price / ma120) * 100

        # 평균 이격도
        avg_disparity = (disparity_20 + disparity_60 + disparity_120) / 3

        # 이격도 상태 판단
        if avg_disparity >= 110:
            status = 'overbought'
            description = '과열 구간 (이격도 높음) - 조정 가능성'
            icon = '🔴'
        elif avg_disparity >= 105:
            status = 'strong'
            description = '강세 구간 (이격도 양호)'
            icon = '🟢'
        elif avg_disparity >= 95:
            status = 'neutral'
            description = '중립 구간 (이격도 정상)'
            icon = '⚪'
        elif avg_disparity >= 90:
            status = 'weak'
            description = '약세 구간 (이격도 낮음)'
            icon = '🟡'
        else:
            status = 'oversold'
            description = '과매도 구간 (이격도 매우 낮음) - 반등 가능성'
            icon = '🔵'

        return {
            'disparity_20': float(disparity_20),
            'disparity_60': float(disparity_60),
            'disparity_120': float(disparity_120),
            'avg_disparity': float(avg_disparity),
            'status': status,
            'description': description,
            'icon': icon,
            'details': (
                f"20일 이격도: {disparity_20:.1f}% ({'+' if disparity_20 > 100 else ''}{disparity_20-100:.1f}%p)\n"
                f"60일 이격도: {disparity_60:.1f}% ({'+' if disparity_60 > 100 else ''}{disparity_60-100:.1f}%p)\n"
                f"120일 이격도: {disparity_120:.1f}% ({'+' if disparity_120 > 100 else ''}{disparity_120-100:.1f}%p)\n"
                f"평균 이격도: {avg_disparity:.1f}%"
            )
        }

    # ==================== 종합 시그널 생성 ====================

    def _generate_signal(self, crosses, alignment, disparity):
        """종합 시그널 생성"""
        score = 50  # 기본 중립

        # 1. 골든크로스/데드크로스 점수
        for cross in crosses:
            if cross['type'] == 'golden':
                # 신뢰도에 따라 가중치 부여
                score += cross['reliability'] * 0.3
            else:  # dead cross
                score -= cross['reliability'] * 0.3

        # 2. 이동평균선 배열 점수 (가중치 0.4)
        alignment_score = alignment.get('score', 50)
        score += (alignment_score - 50) * 0.4

        # 3. 이격도 점수 (가중치 0.3)
        if disparity.get('status') == 'overbought':
            score -= 15
        elif disparity.get('status') == 'strong':
            score += 10
        elif disparity.get('status') == 'weak':
            score -= 10
        elif disparity.get('status') == 'oversold':
            score += 15

        # 점수를 0~100 범위로 조정
        score = max(0, min(100, score))

        # 시그널 변환
        if score >= 80:
            signal = 'strong_buy'
        elif score >= 65:
            signal = 'buy'
        elif score >= 35:
            signal = 'neutral'
        elif score >= 20:
            signal = 'sell'
        else:
            signal = 'strong_sell'

        return signal, score

    # ==================== 투자 전략 추천 ====================

    def _generate_recommendations(self, crosses, alignment, disparity, signal):
        """투자 전략 추천"""
        recommendations = []

        # 1. 골든크로스 전략
        golden_crosses = [c for c in crosses if c['type'] == 'golden']
        if golden_crosses:
            # 가장 신뢰도 높은 골든크로스
            best_golden = max(golden_crosses, key=lambda x: x['reliability'])
            recommendations.append({
                'strategy': f"골든크로스 매수 전략 ({best_golden['short_ma']}일 x {best_golden['long_ma']}일)",
                'action': '매수',
                'confidence': best_golden['reliability'],
                'reason': best_golden['description'],
                'entry': f"현재가 {best_golden['price']:.0f}원 근처",
                'target': f"{int(best_golden['price'] * 1.1):.0f}원 (+10%)",
                'stop_loss': f"{int(best_golden['price'] * 0.95):.0f}원 (-5%)",
                'icon': best_golden['icon']
            })

        # 2. 데드크로스 전략
        dead_crosses = [c for c in crosses if c['type'] == 'dead']
        if dead_crosses:
            # 가장 신뢰도 높은 데드크로스
            best_dead = max(dead_crosses, key=lambda x: x['reliability'])
            recommendations.append({
                'strategy': f"데드크로스 매도/관망 전략 ({best_dead['short_ma']}일 x {best_dead['long_ma']}일)",
                'action': '매도 또는 관망',
                'confidence': best_dead['reliability'],
                'reason': best_dead['description'],
                'entry': '보유 중이라면 손절 고려',
                'target': f"{int(best_dead['price'] * 0.9):.0f}원 (-10%) 예상",
                'stop_loss': f"단기 반등 시 {int(best_dead['price'] * 1.03):.0f}원에 청산",
                'icon': best_dead['icon']
            })

        # 3. 완벽한 정배열 전략
        if alignment.get('type') == 'perfect_bull':
            recommendations.append({
                'strategy': '완벽한 정배열 추세 추종 전략',
                'action': '매수 및 홀딩',
                'confidence': 90,
                'reason': '모든 이동평균선이 정배열 상태로 강한 상승 추세',
                'entry': '조정 시 분할 매수',
                'target': '추세 지속 시 목표가 상향 조정',
                'stop_loss': '20일선 이탈 시 일부 청산 고려',
                'icon': '📈'
            })

        # 4. 완벽한 역배열 전략
        if alignment.get('type') == 'perfect_bear':
            recommendations.append({
                'strategy': '완벽한 역배열 회피 전략',
                'action': '관망 또는 숏 포지션',
                'confidence': 85,
                'reason': '모든 이동평균선이 역배열 상태로 강한 하락 추세',
                'entry': '추가 하락 가능성 높아 진입 자제',
                'target': '하락 추세 지속 예상',
                'stop_loss': '정배열 전환 시까지 관망',
                'icon': '📉'
            })

        # 5. 과매도 반등 전략
        if disparity.get('status') == 'oversold' and alignment.get('type') != 'perfect_bear':
            recommendations.append({
                'strategy': '이격도 과매도 반등 전략',
                'action': '단기 매수',
                'confidence': 70,
                'reason': f"평균 이격도 {disparity['avg_disparity']:.1f}% - 과매도 구간",
                'entry': '현재가 근처 분할 매수',
                'target': '20일 이동평균선 회귀 (약 +5~10%)',
                'stop_loss': '60일선 추가 이탈 시 손절',
                'icon': '🔵'
            })

        # 6. 과열 조정 전략
        if disparity.get('status') == 'overbought' and alignment.get('type') != 'perfect_bull':
            recommendations.append({
                'strategy': '이격도 과열 조정 전략',
                'action': '일부 익절 또는 관망',
                'confidence': 75,
                'reason': f"평균 이격도 {disparity['avg_disparity']:.1f}% - 과열 구간",
                'entry': '보유 중이라면 일부 익절 권장',
                'target': '20일 이동평균선 회귀 (약 -5~10%)',
                'stop_loss': '추세 강하면 60일선까지 홀딩',
                'icon': '🔴'
            })

        # 신뢰도 높은 순으로 정렬
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        return recommendations[:3]  # 상위 3개만 반환


if __name__ == '__main__':
    """테스트 코드"""
    # 샘플 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=150, freq='D')
    np.random.seed(42)

    # 상승 추세 데이터
    trend = np.linspace(100, 150, 150)
    noise = np.random.randn(150) * 5

    sample_data = pd.DataFrame({
        'Open': trend + noise,
        'High': trend + noise + 2,
        'Low': trend + noise - 2,
        'Close': trend + noise,
        'Volume': np.random.randint(1000000, 10000000, 150)
    }, index=dates)

    # 분석 실행
    analyzer = MovingAverageCrossAnalyzer()
    result = analyzer.analyze(sample_data)

    print("=== 이동평균선 크로스 전략 분석 결과 ===")
    print(f"\n[이동평균선]")
    print(f"현재가: {result['moving_averages']['current_price']:.2f}")
    print(f"5일 이평: {result['moving_averages']['ma5']:.2f}")
    print(f"20일 이평: {result['moving_averages']['ma20']:.2f}")
    print(f"60일 이평: {result['moving_averages']['ma60']:.2f}")
    print(f"120일 이평: {result['moving_averages']['ma120']:.2f}")

    print(f"\n[골든크로스/데드크로스]")
    if result['crosses']:
        for cross in result['crosses']:
            print(f"{cross['icon']} {cross['description']} (신뢰도: {cross['reliability']}%)")
    else:
        print("최근 크로스 없음")

    print(f"\n[이동평균선 배열]")
    print(f"{result['alignment']['icon']} {result['alignment']['description']}")
    print(f"점수: {result['alignment']['score']}/100")

    print(f"\n[이격도 분석]")
    if result['disparity']['status'] != 'calculating':
        print(f"{result['disparity']['icon']} {result['disparity']['description']}")
        print(f"평균 이격도: {result['disparity']['avg_disparity']:.1f}%")

    print(f"\n[종합 시그널]")
    print(f"시그널: {result['signal']}")
    print(f"점수: {result['score']:.1f}/100")

    print(f"\n[투자 전략 추천] ({len(result['recommendations'])}개)")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. {rec['icon']} {rec['strategy']}")
        print(f"   행동: {rec['action']}")
        print(f"   신뢰도: {rec['confidence']}%")
        print(f"   이유: {rec['reason']}")
        print(f"   진입: {rec['entry']}")
        print(f"   목표: {rec['target']}")
        print(f"   손절: {rec['stop_loss']}")
