"""
볼린저 밴드 & RSI 전략 분석기 (Phase 3-2)

주요 기능:
1. 볼린저 밴드 (Bollinger Bands) 분석
   - 상단밴드/하단밴드 돌파 감지
   - 밴드폭 수축/확장 분석 (Squeeze/Expansion)
   - %B 지표 계산

2. RSI (Relative Strength Index) 분석
   - 과매수/과매도 구간 판단
   - RSI 다이버전스 자동 탐지
   - RSI 추세선 돌파 감지

3. 종합 시그널 생성
   - 볼린저 밴드 + RSI 복합 전략
   - 신뢰도 점수 계산
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class BollingerRSIAnalyzer:
    """볼린저 밴드 & RSI 전략 분석기"""

    def __init__(self, bb_period=20, bb_std=2, rsi_period=14):
        """
        초기화

        Args:
            bb_period: 볼린저 밴드 기간 (기본값: 20일)
            bb_std: 볼린저 밴드 표준편차 배수 (기본값: 2)
            rsi_period: RSI 계산 기간 (기본값: 14일)
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period

    def analyze(self, df):
        """
        볼린저 밴드 & RSI 종합 분석

        Args:
            df: OHLCV 데이터프레임 (columns: Open, High, Low, Close, Volume)

        Returns:
            dict: 분석 결과
        """
        if len(df) < max(self.bb_period, self.rsi_period) + 10:
            return {
                'bollinger_bands': {},
                'rsi_analysis': {},
                'combined_signal': 'neutral',
                'combined_score': 50,
                'strategy_suggestions': []
            }

        # 1. 볼린저 밴드 분석
        bb_result = self._analyze_bollinger_bands(df)

        # 2. RSI 분석
        rsi_result = self._analyze_rsi(df)

        # 3. 종합 시그널 생성
        combined_signal, combined_score = self._generate_combined_signal(bb_result, rsi_result)

        # 4. 전략 제안
        suggestions = self._generate_strategy_suggestions(bb_result, rsi_result, combined_signal)

        return {
            'bollinger_bands': bb_result,
            'rsi_analysis': rsi_result,
            'combined_signal': combined_signal,
            'combined_score': combined_score,
            'strategy_suggestions': suggestions
        }

    # ==================== 볼린저 밴드 분석 ====================

    def _analyze_bollinger_bands(self, df):
        """볼린저 밴드 분석"""
        # 볼린저 밴드 계산
        df_copy = df.copy()
        df_copy['BB_Middle'] = df_copy['Close'].rolling(window=self.bb_period).mean()
        df_copy['BB_Std'] = df_copy['Close'].rolling(window=self.bb_period).std()
        df_copy['BB_Upper'] = df_copy['BB_Middle'] + (self.bb_std * df_copy['BB_Std'])
        df_copy['BB_Lower'] = df_copy['BB_Middle'] - (self.bb_std * df_copy['BB_Std'])

        # %B 계산 (현재가가 밴드 내에서 어디에 위치하는지)
        df_copy['BB_PercentB'] = (df_copy['Close'] - df_copy['BB_Lower']) / (df_copy['BB_Upper'] - df_copy['BB_Lower'])

        # 밴드폭 계산
        df_copy['BB_Width'] = (df_copy['BB_Upper'] - df_copy['BB_Lower']) / df_copy['BB_Middle']

        # 최근 데이터
        latest = df_copy.iloc[-1]
        previous = df_copy.iloc[-2] if len(df_copy) > 1 else latest

        # 현재 상태 판단
        current_price = latest['Close']
        bb_upper = latest['BB_Upper']
        bb_middle = latest['BB_Middle']
        bb_lower = latest['BB_Lower']
        percent_b = latest['BB_PercentB']
        bb_width = latest['BB_Width']

        # 상태 분석
        position = self._get_bb_position(current_price, bb_upper, bb_middle, bb_lower)
        squeeze_status = self._detect_bb_squeeze(df_copy)
        breakout = self._detect_bb_breakout(df_copy)

        # 시그널 생성
        bb_signal = self._get_bb_signal(position, percent_b, squeeze_status, breakout)

        return {
            'current_price': float(current_price),
            'bb_upper': float(bb_upper),
            'bb_middle': float(bb_middle),
            'bb_lower': float(bb_lower),
            'percent_b': float(percent_b),
            'bb_width': float(bb_width),
            'position': position,
            'squeeze_status': squeeze_status,
            'breakout': breakout,
            'signal': bb_signal,
            'description': self._get_bb_description(position, percent_b, squeeze_status, breakout)
        }

    def _get_bb_position(self, price, upper, middle, lower):
        """볼린저 밴드 내 가격 위치 판단"""
        if price > upper:
            return 'above_upper'  # 상단 밴드 위
        elif price > middle:
            return 'upper_half'  # 상단 밴드와 중간선 사이
        elif price > lower:
            return 'lower_half'  # 중간선과 하단 밴드 사이
        else:
            return 'below_lower'  # 하단 밴드 아래

    def _detect_bb_squeeze(self, df):
        """볼린저 밴드 스퀴즈 (수축) 감지"""
        if len(df) < 20:
            return 'normal'

        # 최근 밴드폭과 과거 밴드폭 비교
        current_width = df['BB_Width'].iloc[-1]
        avg_width = df['BB_Width'].tail(20).mean()

        if current_width < avg_width * 0.7:
            return 'squeeze'  # 밴드폭 수축 (큰 움직임 임박)
        elif current_width > avg_width * 1.3:
            return 'expansion'  # 밴드폭 확장 (변동성 증가)
        else:
            return 'normal'

    def _detect_bb_breakout(self, df):
        """볼린저 밴드 돌파 감지"""
        if len(df) < 3:
            return None

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # 상단 밴드 돌파
        if latest['Close'] > latest['BB_Upper'] and previous['Close'] <= previous['BB_Upper']:
            return {
                'type': 'upper_breakout',
                'description': '상단 밴드 돌파 (과매수 주의)',
                'signal': 'caution',  # 단기 과열 가능성
                'icon': '⚠️'
            }

        # 하단 밴드 돌파
        if latest['Close'] < latest['BB_Lower'] and previous['Close'] >= previous['BB_Lower']:
            return {
                'type': 'lower_breakout',
                'description': '하단 밴드 돌파 (저점 매수 기회)',
                'signal': 'buy',
                'icon': '💰'
            }

        # 중간선 상향 돌파
        if latest['Close'] > latest['BB_Middle'] and previous['Close'] <= previous['BB_Middle']:
            return {
                'type': 'middle_up_breakout',
                'description': '중간선 상향 돌파 (상승 전환)',
                'signal': 'buy',
                'icon': '📈'
            }

        # 중간선 하향 이탈
        if latest['Close'] < latest['BB_Middle'] and previous['Close'] >= previous['BB_Middle']:
            return {
                'type': 'middle_down_breakout',
                'description': '중간선 하향 이탈 (하락 전환)',
                'signal': 'sell',
                'icon': '📉'
            }

        return None

    def _get_bb_signal(self, position, percent_b, squeeze_status, breakout):
        """볼린저 밴드 시그널 생성"""
        # 돌파 시그널이 있으면 우선
        if breakout:
            return breakout['signal']

        # %B 기반 시그널
        if percent_b > 1.0:
            return 'caution'  # 상단 밴드 위 (과매수)
        elif percent_b > 0.8:
            return 'neutral'  # 상단 밴드 근처
        elif percent_b > 0.5:
            return 'buy'  # 중간선 위
        elif percent_b > 0.2:
            return 'neutral'  # 중간선 아래
        else:
            return 'strong_buy'  # 하단 밴드 근처 (과매도)

    def _get_bb_description(self, position, percent_b, squeeze_status, breakout):
        """볼린저 밴드 상태 설명"""
        descriptions = []

        # 위치 설명
        if position == 'above_upper':
            descriptions.append('현재 상단 밴드 위에 위치 (과매수 구간)')
        elif position == 'upper_half':
            descriptions.append('상단 밴드와 중간선 사이 (강세 구간)')
        elif position == 'lower_half':
            descriptions.append('중간선과 하단 밴드 사이 (약세 구간)')
        else:
            descriptions.append('현재 하단 밴드 아래 위치 (과매도 구간)')

        # 스퀴즈 상태
        if squeeze_status == 'squeeze':
            descriptions.append('⚡ 밴드폭 수축 중 - 큰 움직임 임박')
        elif squeeze_status == 'expansion':
            descriptions.append('📢 밴드폭 확장 중 - 변동성 증가')

        # 돌파 상태
        if breakout:
            descriptions.append(f"{breakout['icon']} {breakout['description']}")

        return ' | '.join(descriptions)

    # ==================== RSI 분석 ====================

    def _analyze_rsi(self, df):
        """RSI (Relative Strength Index) 분석"""
        # RSI 계산
        df_copy = df.copy()
        delta = df_copy['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()

        rs = avg_gain / avg_loss
        df_copy['RSI'] = 100 - (100 / (1 + rs))

        # 최근 RSI 값
        current_rsi = df_copy['RSI'].iloc[-1]
        previous_rsi = df_copy['RSI'].iloc[-2] if len(df_copy) > 1 else current_rsi

        # RSI 상태 분석
        rsi_zone = self._get_rsi_zone(current_rsi)
        rsi_trend = self._get_rsi_trend(df_copy)
        divergence = self._detect_rsi_divergence(df_copy)

        # 시그널 생성
        rsi_signal = self._get_rsi_signal(current_rsi, rsi_zone, rsi_trend, divergence)

        return {
            'current_rsi': float(current_rsi),
            'previous_rsi': float(previous_rsi),
            'rsi_zone': rsi_zone,
            'rsi_trend': rsi_trend,
            'divergence': divergence,
            'signal': rsi_signal,
            'description': self._get_rsi_description(current_rsi, rsi_zone, rsi_trend, divergence)
        }

    def _get_rsi_zone(self, rsi):
        """RSI 구간 판단"""
        if rsi >= 70:
            return 'overbought'  # 과매수
        elif rsi >= 60:
            return 'strong'  # 강세
        elif rsi >= 40:
            return 'neutral'  # 중립
        elif rsi >= 30:
            return 'weak'  # 약세
        else:
            return 'oversold'  # 과매도

    def _get_rsi_trend(self, df):
        """RSI 추세 분석"""
        if len(df) < 5:
            return 'neutral'

        rsi_values = df['RSI'].tail(5).values

        # 선형 회귀로 추세 파악
        x = np.arange(len(rsi_values))
        slope = np.polyfit(x, rsi_values, 1)[0]

        if slope > 2:
            return 'strong_uptrend'  # 강한 상승 추세
        elif slope > 0.5:
            return 'uptrend'  # 상승 추세
        elif slope > -0.5:
            return 'sideways'  # 횡보
        elif slope > -2:
            return 'downtrend'  # 하락 추세
        else:
            return 'strong_downtrend'  # 강한 하락 추세

    def _detect_rsi_divergence(self, df):
        """RSI 다이버전스 감지"""
        if len(df) < 20:
            return None

        # 최근 20일 데이터
        recent_df = df.tail(20)

        # 가격 고점/저점
        price_highs = recent_df['High'].nlargest(3)
        price_lows = recent_df['Low'].nsmallest(3)

        # RSI 고점/저점
        rsi_values = recent_df['RSI']

        # 강세 다이버전스 (Bullish Divergence)
        # 가격은 낮아지는데 RSI는 높아지는 경우
        if len(price_lows) >= 2:
            price_trend = price_lows.iloc[-1] - price_lows.iloc[0]
            rsi_at_price_lows = rsi_values.loc[price_lows.index]
            if len(rsi_at_price_lows) >= 2:
                rsi_trend = rsi_at_price_lows.iloc[-1] - rsi_at_price_lows.iloc[0]

                if price_trend < 0 and rsi_trend > 0:
                    return {
                        'type': 'bullish',
                        'description': '강세 다이버전스 - 가격 하락하지만 RSI 상승 (상승 전환 신호)',
                        'signal': 'buy',
                        'reliability': 75,
                        'icon': '🔄'
                    }

        # 약세 다이버전스 (Bearish Divergence)
        # 가격은 높아지는데 RSI는 낮아지는 경우
        if len(price_highs) >= 2:
            price_trend = price_highs.iloc[-1] - price_highs.iloc[0]
            rsi_at_price_highs = rsi_values.loc[price_highs.index]
            if len(rsi_at_price_highs) >= 2:
                rsi_trend = rsi_at_price_highs.iloc[-1] - rsi_at_price_highs.iloc[0]

                if price_trend > 0 and rsi_trend < 0:
                    return {
                        'type': 'bearish',
                        'description': '약세 다이버전스 - 가격 상승하지만 RSI 하락 (하락 전환 신호)',
                        'signal': 'sell',
                        'reliability': 75,
                        'icon': '🔄'
                    }

        return None

    def _get_rsi_signal(self, rsi, zone, trend, divergence):
        """RSI 시그널 생성"""
        # 다이버전스가 있으면 우선
        if divergence:
            return divergence['signal']

        # RSI 구간 기반 시그널
        if zone == 'oversold':
            return 'strong_buy'  # 과매도 (매수 기회)
        elif zone == 'weak':
            if trend in ['uptrend', 'strong_uptrend']:
                return 'buy'  # 약세이지만 반등 중
            return 'neutral'
        elif zone == 'neutral':
            if trend in ['uptrend', 'strong_uptrend']:
                return 'buy'
            elif trend in ['downtrend', 'strong_downtrend']:
                return 'sell'
            return 'neutral'
        elif zone == 'strong':
            if trend in ['downtrend', 'strong_downtrend']:
                return 'sell'  # 강세이지만 하락 중
            return 'neutral'
        else:  # overbought
            return 'caution'  # 과매수 (조정 가능성)

    def _get_rsi_description(self, rsi, zone, trend, divergence):
        """RSI 상태 설명"""
        descriptions = []

        # RSI 값 설명
        descriptions.append(f'RSI {rsi:.1f}')

        # 구간 설명
        zone_desc = {
            'oversold': '과매도 구간 (매수 타이밍)',
            'weak': '약세 구간',
            'neutral': '중립 구간',
            'strong': '강세 구간',
            'overbought': '과매수 구간 (조정 가능성)'
        }
        descriptions.append(zone_desc[zone])

        # 추세 설명
        trend_desc = {
            'strong_uptrend': '📈 강한 상승 추세',
            'uptrend': '↗️ 상승 추세',
            'sideways': '➡️ 횡보',
            'downtrend': '↘️ 하락 추세',
            'strong_downtrend': '📉 강한 하락 추세'
        }
        descriptions.append(trend_desc[trend])

        # 다이버전스
        if divergence:
            descriptions.append(f"{divergence['icon']} {divergence['description']}")

        return ' | '.join(descriptions)

    # ==================== 종합 분석 ====================

    def _generate_combined_signal(self, bb_result, rsi_result):
        """볼린저 밴드 + RSI 종합 시그널 생성"""
        # 시그널 점수화
        signal_scores = {
            'strong_buy': 100,
            'buy': 75,
            'neutral': 50,
            'caution': 50,
            'sell': 25,
            'strong_sell': 0
        }

        bb_score = signal_scores.get(bb_result['signal'], 50)
        rsi_score = signal_scores.get(rsi_result['signal'], 50)

        # 가중 평균 (RSI 가중치 1.2배)
        combined_score = (bb_score + rsi_score * 1.2) / 2.2

        # 점수를 시그널로 변환
        if combined_score >= 80:
            combined_signal = 'strong_buy'
        elif combined_score >= 65:
            combined_signal = 'buy'
        elif combined_score >= 35:
            combined_signal = 'neutral'
        elif combined_score >= 20:
            combined_signal = 'sell'
        else:
            combined_signal = 'strong_sell'

        return combined_signal, combined_score

    def _generate_strategy_suggestions(self, bb_result, rsi_result, combined_signal):
        """트레이딩 전략 제안"""
        suggestions = []

        # 1. 과매도 + 하단 밴드 돌파 = 강력 매수
        if (rsi_result['rsi_zone'] == 'oversold' and
            bb_result['position'] in ['below_lower', 'lower_half']):
            suggestions.append({
                'strategy': '과매도 반등 전략',
                'action': '매수',
                'confidence': 85,
                'reason': 'RSI 과매도 + 볼린저 밴드 하단 근처',
                'entry': f"현재가 {bb_result['current_price']:.0f}원 근처",
                'target': f"중간선 {bb_result['bb_middle']:.0f}원",
                'stop_loss': f"하단 밴드 {bb_result['bb_lower']:.0f}원 이탈 시",
                'icon': '💰'
            })

        # 2. 과매수 + 상단 밴드 돌파 = 단기 매도
        if (rsi_result['rsi_zone'] == 'overbought' and
            bb_result['position'] in ['above_upper', 'upper_half']):
            suggestions.append({
                'strategy': '과매수 조정 전략',
                'action': '단기 익절 또는 관망',
                'confidence': 75,
                'reason': 'RSI 과매수 + 볼린저 밴드 상단 근처',
                'entry': '보유 중이라면 일부 익절 고려',
                'target': f"중간선 {bb_result['bb_middle']:.0f}원",
                'stop_loss': f"상단 밴드 {bb_result['bb_upper']:.0f}원 재돌파 시 홀딩",
                'icon': '⚠️'
            })

        # 3. 스퀴즈 + 중립 RSI = 돌파 대기
        if (bb_result['squeeze_status'] == 'squeeze' and
            rsi_result['rsi_zone'] == 'neutral'):
            suggestions.append({
                'strategy': '볼린저 밴드 스퀴즈 돌파 전략',
                'action': '돌파 방향 확인 후 진입',
                'confidence': 70,
                'reason': '밴드폭 수축 - 큰 움직임 임박',
                'entry': f"상단 밴드 {bb_result['bb_upper']:.0f}원 돌파 시 매수 / 하단 밴드 {bb_result['bb_lower']:.0f}원 이탈 시 매도",
                'target': '돌파 방향으로 밴드폭만큼 이동 예상',
                'stop_loss': '진입 반대 밴드 이탈 시',
                'icon': '⚡'
            })

        # 4. 다이버전스 감지 시
        if rsi_result['divergence']:
            div = rsi_result['divergence']
            suggestions.append({
                'strategy': f"{div['type'].upper()} 다이버전스 전략",
                'action': '매수' if div['type'] == 'bullish' else '매도',
                'confidence': div['reliability'],
                'reason': div['description'],
                'entry': f"현재가 {bb_result['current_price']:.0f}원",
                'target': f"중간선 {bb_result['bb_middle']:.0f}원",
                'stop_loss': '다이버전스 패턴 무효화 시',
                'icon': div['icon']
            })

        # 5. 중간선 돌파 시
        if bb_result['breakout'] and bb_result['breakout']['type'] in ['middle_up_breakout', 'middle_down_breakout']:
            breakout = bb_result['breakout']
            suggestions.append({
                'strategy': '중간선 돌파 전략',
                'action': '매수' if 'up' in breakout['type'] else '매도',
                'confidence': 65,
                'reason': breakout['description'],
                'entry': f"현재가 {bb_result['current_price']:.0f}원",
                'target': f"상단 밴드 {bb_result['bb_upper']:.0f}원" if 'up' in breakout['type'] else f"하단 밴드 {bb_result['bb_lower']:.0f}원",
                'stop_loss': f"중간선 {bb_result['bb_middle']:.0f}원 재이탈 시",
                'icon': breakout['icon']
            })

        # 신뢰도 높은 순으로 정렬
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return suggestions[:3]  # 상위 3개만 반환


if __name__ == '__main__':
    """테스트 코드"""
    # 샘플 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    sample_data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)

    # 분석 실행
    analyzer = BollingerRSIAnalyzer()
    result = analyzer.analyze(sample_data)

    print("=== 볼린저 밴드 & RSI 분석 결과 ===")
    print(f"\n[볼린저 밴드]")
    print(f"현재가: {result['bollinger_bands']['current_price']:.2f}")
    print(f"상단 밴드: {result['bollinger_bands']['bb_upper']:.2f}")
    print(f"중간선: {result['bollinger_bands']['bb_middle']:.2f}")
    print(f"하단 밴드: {result['bollinger_bands']['bb_lower']:.2f}")
    print(f"%B: {result['bollinger_bands']['percent_b']:.2f}")
    print(f"설명: {result['bollinger_bands']['description']}")

    print(f"\n[RSI 분석]")
    print(f"현재 RSI: {result['rsi_analysis']['current_rsi']:.2f}")
    print(f"RSI 구간: {result['rsi_analysis']['rsi_zone']}")
    print(f"설명: {result['rsi_analysis']['description']}")

    print(f"\n[종합 시그널]")
    print(f"시그널: {result['combined_signal']}")
    print(f"점수: {result['combined_score']:.1f}/100")

    print(f"\n[전략 제안] ({len(result['strategy_suggestions'])}개)")
    for i, suggestion in enumerate(result['strategy_suggestions'], 1):
        print(f"\n{i}. {suggestion['icon']} {suggestion['strategy']}")
        print(f"   행동: {suggestion['action']}")
        print(f"   신뢰도: {suggestion['confidence']}%")
        print(f"   이유: {suggestion['reason']}")
        print(f"   진입: {suggestion['entry']}")
        print(f"   목표: {suggestion['target']}")
        print(f"   손절: {suggestion['stop_loss']}")
