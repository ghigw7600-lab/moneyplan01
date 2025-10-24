# -*- coding: utf-8 -*-
"""
고급 패턴 인식 시스템 (Phase 3-1)
캔들스틱 패턴 + 차트 패턴 자동 인식
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class PatternAnalyzer:
    """차트 패턴 및 캔들스틱 패턴 인식기"""

    def __init__(self):
        self.patterns_found = []

    def analyze_patterns(self, df):
        """
        전체 패턴 분석 실행

        Args:
            df (DataFrame): OHLCV 데이터 (Open, High, Low, Close, Volume)

        Returns:
            dict: 패턴 분석 결과
        """
        if df is None or len(df) < 20:
            return {
                'candlestick_patterns': [],
                'chart_patterns': [],
                'pattern_score': 0,
                'pattern_signal': 'neutral',
                'total_patterns': 0
            }

        print("\n" + "=" * 60)
        print("📊 고급 패턴 분석 시작")
        print("=" * 60)

        # 1. 캔들스틱 패턴 분석
        candlestick_patterns = self._analyze_candlestick_patterns(df)

        # 2. 차트 패턴 분석
        chart_patterns = self._analyze_chart_patterns(df)

        # 3. 패턴 신뢰도 점수 계산
        pattern_score = self._calculate_pattern_score(candlestick_patterns, chart_patterns)

        # 4. 종합 시그널
        pattern_signal = self._get_pattern_signal(pattern_score)

        result = {
            'candlestick_patterns': candlestick_patterns,
            'chart_patterns': chart_patterns,
            'pattern_score': pattern_score,
            'pattern_signal': pattern_signal,
            'total_patterns': len(candlestick_patterns) + len(chart_patterns)
        }

        print(f"\n✅ 패턴 분석 완료: {result['total_patterns']}개 패턴 발견")
        print(f"   패턴 점수: {pattern_score}/100")
        print(f"   시그널: {pattern_signal}\n")

        return result

    def _analyze_candlestick_patterns(self, df):
        """캔들스틱 패턴 인식"""
        patterns = []

        print("\n📈 캔들스틱 패턴 분석 중...")

        # 최근 5일 데이터만 분석 (패턴은 최근에 형성되어야 의미 있음)
        recent_df = df.tail(5).copy()

        for i in range(len(recent_df)):
            idx = recent_df.index[i]
            row = recent_df.iloc[i]

            # 도지 (Doji) - 시가와 종가가 거의 같음
            if self._is_doji(row):
                patterns.append({
                    'name': '도지 (Doji)',
                    'type': 'candlestick',
                    'signal': 'neutral',
                    'reliability': 60,
                    'description': '시장의 우유부단함을 나타내며, 추세 전환 가능성',
                    'date': idx,
                    'icon': '🔄'
                })

            # 망치형 (Hammer) - 하락 추세에서 반등 신호
            if self._is_hammer(row, df):
                patterns.append({
                    'name': '망치형 (Hammer)',
                    'type': 'candlestick',
                    'signal': 'buy',
                    'reliability': 75,
                    'description': '하락 추세 후 나타나면 강력한 반등 신호',
                    'date': idx,
                    'icon': '🔨'
                })

            # 역망치형 (Inverted Hammer)
            if self._is_inverted_hammer(row, df):
                patterns.append({
                    'name': '역망치형 (Inverted Hammer)',
                    'type': 'candlestick',
                    'signal': 'buy',
                    'reliability': 70,
                    'description': '하락 후 매수 세력의 등장을 암시',
                    'date': idx,
                    'icon': '🔨'
                })

            # 유성형 (Shooting Star) - 상승 추세에서 하락 전환 신호
            if self._is_shooting_star(row, df):
                patterns.append({
                    'name': '유성형 (Shooting Star)',
                    'type': 'candlestick',
                    'signal': 'sell',
                    'reliability': 75,
                    'description': '상승 추세 후 나타나면 하락 전환 경고',
                    'date': idx,
                    'icon': '⭐'
                })

            # 교수형 (Hanging Man) - 상승 후 하락 신호
            if self._is_hanging_man(row, df):
                patterns.append({
                    'name': '교수형 (Hanging Man)',
                    'type': 'candlestick',
                    'signal': 'sell',
                    'reliability': 70,
                    'description': '상승 추세 후 나타나면 하락 전환 가능성',
                    'date': idx,
                    'icon': '⚠️'
                })

        # 2일 패턴 분석
        if len(recent_df) >= 2:
            patterns.extend(self._analyze_two_candle_patterns(recent_df))

        # 3일 패턴 분석
        if len(recent_df) >= 3:
            patterns.extend(self._analyze_three_candle_patterns(recent_df))

        print(f"   ✅ {len(patterns)}개 캔들스틱 패턴 발견")
        return patterns

    def _analyze_chart_patterns(self, df):
        """차트 패턴 인식 (헤드앤숄더, 삼각수렴 등)"""
        patterns = []

        print("\n📊 차트 패턴 분석 중...")

        # 최근 20일 데이터로 패턴 분석
        recent_df = df.tail(20).copy()

        # 헤드앤숄더 (Head and Shoulders)
        head_shoulders = self._detect_head_and_shoulders(recent_df)
        if head_shoulders:
            patterns.append(head_shoulders)

        # 역헤드앤숄더 (Inverse Head and Shoulders)
        inv_head_shoulders = self._detect_inverse_head_and_shoulders(recent_df)
        if inv_head_shoulders:
            patterns.append(inv_head_shoulders)

        # 삼각수렴 (Triangle)
        triangle = self._detect_triangle(recent_df)
        if triangle:
            patterns.append(triangle)

        # 이중 천정/바닥 (Double Top/Bottom)
        double_pattern = self._detect_double_pattern(recent_df)
        if double_pattern:
            patterns.append(double_pattern)

        # 컵앤핸들 (Cup and Handle)
        cup_handle = self._detect_cup_and_handle(recent_df)
        if cup_handle:
            patterns.append(cup_handle)

        print(f"   ✅ {len(patterns)}개 차트 패턴 발견")
        return patterns

    # ==================== 캔들스틱 패턴 판별 함수 ====================

    def _is_doji(self, row):
        """도지 패턴 (시가와 종가가 거의 같음)"""
        body = abs(row['Close'] - row['Open'])
        range_val = row['High'] - row['Low']
        return body <= range_val * 0.1 if range_val > 0 else False

    def _is_hammer(self, row, df):
        """망치형 패턴 (긴 아래꼬리 + 짧은 몸통)"""
        body = abs(row['Close'] - row['Open'])
        lower_shadow = min(row['Close'], row['Open']) - row['Low']
        upper_shadow = row['High'] - max(row['Close'], row['Open'])
        range_val = row['High'] - row['Low']

        # 망치형 조건: 아래꼬리가 몸통의 2배 이상, 위꼬리는 짧음
        if range_val == 0:
            return False

        is_hammer_shape = (
            lower_shadow > body * 2 and
            upper_shadow < body * 0.3 and
            body < range_val * 0.3
        )

        # 하락 추세 후에 나타나야 의미 있음
        recent_trend = self._get_recent_trend(df, 5)
        return is_hammer_shape and recent_trend == 'downtrend'

    def _is_inverted_hammer(self, row, df):
        """역망치형 패턴 (긴 위꼬리 + 짧은 몸통)"""
        body = abs(row['Close'] - row['Open'])
        lower_shadow = min(row['Close'], row['Open']) - row['Low']
        upper_shadow = row['High'] - max(row['Close'], row['Open'])
        range_val = row['High'] - row['Low']

        if range_val == 0:
            return False

        is_inv_hammer_shape = (
            upper_shadow > body * 2 and
            lower_shadow < body * 0.3 and
            body < range_val * 0.3
        )

        recent_trend = self._get_recent_trend(df, 5)
        return is_inv_hammer_shape and recent_trend == 'downtrend'

    def _is_shooting_star(self, row, df):
        """유성형 패턴 (상승 후 긴 위꼬리)"""
        body = abs(row['Close'] - row['Open'])
        lower_shadow = min(row['Close'], row['Open']) - row['Low']
        upper_shadow = row['High'] - max(row['Close'], row['Open'])
        range_val = row['High'] - row['Low']

        if range_val == 0:
            return False

        is_star_shape = (
            upper_shadow > body * 2 and
            lower_shadow < body * 0.3 and
            row['Close'] < row['Open']  # 음봉
        )

        recent_trend = self._get_recent_trend(df, 5)
        return is_star_shape and recent_trend == 'uptrend'

    def _is_hanging_man(self, row, df):
        """교수형 패턴 (상승 후 긴 아래꼬리)"""
        body = abs(row['Close'] - row['Open'])
        lower_shadow = min(row['Close'], row['Open']) - row['Low']
        upper_shadow = row['High'] - max(row['Close'], row['Open'])
        range_val = row['High'] - row['Low']

        if range_val == 0:
            return False

        is_hanging_shape = (
            lower_shadow > body * 2 and
            upper_shadow < body * 0.3 and
            row['Close'] < row['Open']  # 음봉
        )

        recent_trend = self._get_recent_trend(df, 5)
        return is_hanging_shape and recent_trend == 'uptrend'

    def _analyze_two_candle_patterns(self, df):
        """2개 캔들 패턴 (Engulfing, Piercing 등)"""
        patterns = []
        if len(df) < 2:
            return patterns

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # 강세 잉걸핑 (Bullish Engulfing)
        if (prev['Close'] < prev['Open'] and  # 전일 음봉
            curr['Close'] > curr['Open'] and  # 당일 양봉
            curr['Open'] < prev['Close'] and  # 당일 시가가 전일 종가보다 낮음
            curr['Close'] > prev['Open']):    # 당일 종가가 전일 시가보다 높음
            patterns.append({
                'name': '강세 잉걸핑 (Bullish Engulfing)',
                'type': 'candlestick',
                'signal': 'buy',
                'reliability': 80,
                'description': '전일 음봉을 완전히 감싸는 큰 양봉, 강력한 매수 신호',
                'date': df.index[-1],
                'icon': '📈'
            })

        # 약세 잉걸핑 (Bearish Engulfing)
        if (prev['Close'] > prev['Open'] and  # 전일 양봉
            curr['Close'] < curr['Open'] and  # 당일 음봉
            curr['Open'] > prev['Close'] and  # 당일 시가가 전일 종가보다 높음
            curr['Close'] < prev['Open']):    # 당일 종가가 전일 시가보다 낮음
            patterns.append({
                'name': '약세 잉걸핑 (Bearish Engulfing)',
                'type': 'candlestick',
                'signal': 'sell',
                'reliability': 80,
                'description': '전일 양봉을 완전히 감싸는 큰 음봉, 강력한 매도 신호',
                'date': df.index[-1],
                'icon': '📉'
            })

        return patterns

    def _analyze_three_candle_patterns(self, df):
        """3개 캔들 패턴 (Morning/Evening Star 등)"""
        patterns = []
        if len(df) < 3:
            return patterns

        first = df.iloc[-3]
        second = df.iloc[-2]
        third = df.iloc[-1]

        # 샛별형 (Morning Star) - 하락 후 반등
        if (first['Close'] < first['Open'] and  # 첫째날: 큰 음봉
            abs(second['Close'] - second['Open']) < abs(first['Close'] - first['Open']) * 0.5 and  # 둘째날: 작은 몸통
            third['Close'] > third['Open'] and  # 셋째날: 양봉
            third['Close'] > (first['Open'] + first['Close']) / 2):  # 셋째날 종가가 첫째날 중간 이상
            patterns.append({
                'name': '샛별형 (Morning Star)',
                'type': 'candlestick',
                'signal': 'buy',
                'reliability': 85,
                'description': '하락 후 나타나는 3일 반등 패턴, 매우 강력한 매수 신호',
                'date': df.index[-1],
                'icon': '🌟'
            })

        # 저녁별형 (Evening Star) - 상승 후 하락
        if (first['Close'] > first['Open'] and  # 첫째날: 큰 양봉
            abs(second['Close'] - second['Open']) < abs(first['Close'] - first['Open']) * 0.5 and  # 둘째날: 작은 몸통
            third['Close'] < third['Open'] and  # 셋째날: 음봉
            third['Close'] < (first['Open'] + first['Close']) / 2):  # 셋째날 종가가 첫째날 중간 이하
            patterns.append({
                'name': '저녁별형 (Evening Star)',
                'type': 'candlestick',
                'signal': 'sell',
                'reliability': 85,
                'description': '상승 후 나타나는 3일 하락 패턴, 매우 강력한 매도 신호',
                'date': df.index[-1],
                'icon': '🌙'
            })

        return patterns

    # ==================== 차트 패턴 판별 함수 ====================

    def _detect_head_and_shoulders(self, df):
        """헤드앤숄더 패턴 (하락 전환 신호)"""
        if len(df) < 15:
            return None

        # 고점 3개 찾기
        peaks = self._find_peaks(df['High'], min_distance=3)
        if len(peaks) < 3:
            return None

        # 최근 3개 고점
        recent_peaks = peaks[-3:]
        left_shoulder = df['High'].iloc[recent_peaks[0]]
        head = df['High'].iloc[recent_peaks[1]]
        right_shoulder = df['High'].iloc[recent_peaks[2]]

        # 헤드앤숄더 조건: 가운데가 가장 높고, 양쪽 어깨가 비슷한 높이
        if (head > left_shoulder * 1.02 and
            head > right_shoulder * 1.02 and
            abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
            return {
                'name': '헤드앤숄더 (Head and Shoulders)',
                'type': 'chart',
                'signal': 'sell',
                'reliability': 85,
                'description': '강력한 하락 전환 패턴, 넥라인 돌파 시 매도 고려',
                'date': df.index[-1],
                'icon': '👤'
            }
        return None

    def _detect_inverse_head_and_shoulders(self, df):
        """역헤드앤숄더 패턴 (상승 전환 신호)"""
        if len(df) < 15:
            return None

        # 저점 3개 찾기
        troughs = self._find_troughs(df['Low'], min_distance=3)
        if len(troughs) < 3:
            return None

        # 최근 3개 저점
        recent_troughs = troughs[-3:]
        left_shoulder = df['Low'].iloc[recent_troughs[0]]
        head = df['Low'].iloc[recent_troughs[1]]
        right_shoulder = df['Low'].iloc[recent_troughs[2]]

        # 역헤드앤숄더 조건: 가운데가 가장 낮고, 양쪽 어깨가 비슷한 높이
        if (head < left_shoulder * 0.98 and
            head < right_shoulder * 0.98 and
            abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
            return {
                'name': '역헤드앤숄더 (Inverse Head and Shoulders)',
                'type': 'chart',
                'signal': 'buy',
                'reliability': 85,
                'description': '강력한 상승 전환 패턴, 넥라인 돌파 시 매수 고려',
                'date': df.index[-1],
                'icon': '🙃'
            }
        return None

    def _detect_triangle(self, df):
        """삼각수렴 패턴 (Ascending/Descending/Symmetrical Triangle)"""
        if len(df) < 10:
            return None

        # 고점과 저점 추세선 계산
        highs = df['High'].values
        lows = df['Low'].values

        # 최근 고점들의 추세
        high_slope = self._calculate_slope(highs[-10:])
        # 최근 저점들의 추세
        low_slope = self._calculate_slope(lows[-10:])

        # 대칭 삼각형 (Symmetrical Triangle)
        if abs(high_slope) < 0.001 and abs(low_slope) < 0.001:
            return {
                'name': '대칭 삼각형 (Symmetrical Triangle)',
                'type': 'chart',
                'signal': 'neutral',
                'reliability': 70,
                'description': '돌파 방향에 따라 추세 결정, 거래량 증가 시 주목',
                'date': df.index[-1],
                'icon': '🔺'
            }

        # 상승 삼각형 (Ascending Triangle)
        if abs(high_slope) < 0.001 and low_slope > 0:
            return {
                'name': '상승 삼각형 (Ascending Triangle)',
                'type': 'chart',
                'signal': 'buy',
                'reliability': 75,
                'description': '상승 돌파 가능성 높음, 저점이 점점 높아지는 패턴',
                'date': df.index[-1],
                'icon': '📈'
            }

        # 하락 삼각형 (Descending Triangle)
        if high_slope < 0 and abs(low_slope) < 0.001:
            return {
                'name': '하락 삼각형 (Descending Triangle)',
                'type': 'chart',
                'signal': 'sell',
                'reliability': 75,
                'description': '하락 돌파 가능성 높음, 고점이 점점 낮아지는 패턴',
                'date': df.index[-1],
                'icon': '📉'
            }

        return None

    def _detect_double_pattern(self, df):
        """이중 천정/바닥 패턴"""
        if len(df) < 10:
            return None

        # 고점 찾기
        peaks = self._find_peaks(df['High'], min_distance=3)
        if len(peaks) >= 2:
            last_two_peaks = peaks[-2:]
            peak1 = df['High'].iloc[last_two_peaks[0]]
            peak2 = df['High'].iloc[last_two_peaks[1]]

            # 이중천정: 두 고점이 거의 같은 높이
            if abs(peak1 - peak2) / peak1 < 0.03:
                return {
                    'name': '이중 천정 (Double Top)',
                    'type': 'chart',
                    'signal': 'sell',
                    'reliability': 80,
                    'description': '두 번 고점 도전 후 실패, 하락 전환 가능성',
                    'date': df.index[-1],
                    'icon': 'Ⓜ️'
                }

        # 저점 찾기
        troughs = self._find_troughs(df['Low'], min_distance=3)
        if len(troughs) >= 2:
            last_two_troughs = troughs[-2:]
            trough1 = df['Low'].iloc[last_two_troughs[0]]
            trough2 = df['Low'].iloc[last_two_troughs[1]]

            # 이중바닥: 두 저점이 거의 같은 높이
            if abs(trough1 - trough2) / trough1 < 0.03:
                return {
                    'name': '이중 바닥 (Double Bottom)',
                    'type': 'chart',
                    'signal': 'buy',
                    'reliability': 80,
                    'description': '두 번 저점 지지 후 반등, 상승 전환 가능성',
                    'date': df.index[-1],
                    'icon': 'Ⓦ️'
                }

        return None

    def _detect_cup_and_handle(self, df):
        """컵앤핸들 패턴 (강력한 상승 신호)"""
        if len(df) < 20:
            return None

        # 단순화된 컵앤핸들 감지 로직
        # 1. 최근 20일 중 중간에 큰 하락 후 회복 (컵)
        # 2. 회복 후 작은 조정 (핸들)

        mid_point = len(df) // 2
        first_half_high = df['High'].iloc[:mid_point].max()
        mid_low = df['Low'].iloc[mid_point - 3:mid_point + 3].min()
        second_half_high = df['High'].iloc[mid_point:].max()

        # 컵 형성: 중간에 20% 이상 하락 후 회복
        if (first_half_high - mid_low) / first_half_high > 0.2:
            # 핸들 형성: 최근 소폭 조정
            recent_correction = (second_half_high - df['Close'].iloc[-1]) / second_half_high
            if 0.05 < recent_correction < 0.15:
                return {
                    'name': '컵앤핸들 (Cup and Handle)',
                    'type': 'chart',
                    'signal': 'buy',
                    'reliability': 85,
                    'description': '강력한 상승 패턴, 핸들 돌파 시 큰 상승 예상',
                    'date': df.index[-1],
                    'icon': '☕'
                }

        return None

    # ==================== 헬퍼 함수 ====================

    def _get_recent_trend(self, df, periods=5):
        """최근 추세 판단"""
        if len(df) < periods:
            return 'neutral'

        recent = df.tail(periods)
        first_close = recent['Close'].iloc[0]
        last_close = recent['Close'].iloc[-1]

        change = (last_close - first_close) / first_close

        if change > 0.03:
            return 'uptrend'
        elif change < -0.03:
            return 'downtrend'
        else:
            return 'neutral'

    def _find_peaks(self, series, min_distance=3):
        """고점 찾기"""
        peaks = []
        for i in range(min_distance, len(series) - min_distance):
            if all(series.iloc[i] >= series.iloc[i - j] for j in range(1, min_distance + 1)):
                if all(series.iloc[i] >= series.iloc[i + j] for j in range(1, min_distance + 1)):
                    peaks.append(i)
        return peaks

    def _find_troughs(self, series, min_distance=3):
        """저점 찾기"""
        troughs = []
        for i in range(min_distance, len(series) - min_distance):
            if all(series.iloc[i] <= series.iloc[i - j] for j in range(1, min_distance + 1)):
                if all(series.iloc[i] <= series.iloc[i + j] for j in range(1, min_distance + 1)):
                    troughs.append(i)
        return troughs

    def _calculate_slope(self, values):
        """추세선 기울기 계산"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        z = np.polyfit(x, values, 1)
        return z[0]

    def _calculate_pattern_score(self, candlestick_patterns, chart_patterns):
        """패턴 신뢰도 점수 계산 (0-100)"""
        total_score = 0
        pattern_count = 0

        # 캔들스틱 패턴 점수
        for pattern in candlestick_patterns:
            if pattern['signal'] == 'buy':
                total_score += pattern['reliability']
                pattern_count += 1
            elif pattern['signal'] == 'sell':
                total_score -= pattern['reliability']
                pattern_count += 1
            # neutral은 점수에 영향 없음

        # 차트 패턴 점수 (가중치 1.5배)
        for pattern in chart_patterns:
            if pattern['signal'] == 'buy':
                total_score += pattern['reliability'] * 1.5
                pattern_count += 1
            elif pattern['signal'] == 'sell':
                total_score -= pattern['reliability'] * 1.5
                pattern_count += 1

        # 정규화 (0-100)
        if pattern_count == 0:
            return 50  # 패턴 없으면 중립

        # -100 ~ +100 범위를 0 ~ 100으로 변환
        normalized_score = (total_score / pattern_count + 100) / 2
        return max(0, min(100, normalized_score))

    def _get_pattern_signal(self, score):
        """패턴 점수로 시그널 판단"""
        if score >= 75:
            return 'strong_buy'
        elif score >= 60:
            return 'buy'
        elif score >= 40:
            return 'neutral'
        elif score >= 25:
            return 'sell'
        else:
            return 'strong_sell'


# 테스트 코드
if __name__ == "__main__":
    import sys
    import io
    from collectors.stock_collector import StockDataCollector

    # Windows 한글 출력
    if hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except ValueError:
            pass

    print("\n" + "=" * 60)
    print("🧪 패턴 분석기 테스트")
    print("=" * 60)

    collector = StockDataCollector()
    analyzer = PatternAnalyzer()

    # 삼성전자 데이터로 테스트
    ticker = '005930.KS'
    print(f"\n📊 {ticker} 데이터 수집 중...")

    df = collector.get_stock_data(ticker, period='3mo')

    if df is not None and len(df) > 0:
        result = analyzer.analyze_patterns(df)

        print("\n" + "=" * 60)
        print("📊 패턴 분석 결과")
        print("=" * 60)

        print(f"\n✅ 총 {result['total_patterns']}개 패턴 발견")
        print(f"   패턴 점수: {result['pattern_score']:.1f}/100")
        print(f"   시그널: {result['pattern_signal']}")

        if result['candlestick_patterns']:
            print("\n📈 캔들스틱 패턴:")
            for p in result['candlestick_patterns']:
                print(f"   {p['icon']} {p['name']} - {p['description']}")

        if result['chart_patterns']:
            print("\n📊 차트 패턴:")
            for p in result['chart_patterns']:
                print(f"   {p['icon']} {p['name']} - {p['description']}")
    else:
        print("❌ 데이터 수집 실패")
