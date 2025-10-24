# -*- coding: utf-8 -*-
"""
기술적 지표 분석 엔진
RSI, MACD, 이동평균선, 볼린저밴드 등
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MA_PERIODS, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL


class TechnicalAnalyzer:
    """기술적 지표 분석기"""

    def __init__(self, data):
        """
        Args:
            data (DataFrame): OHLCV 데이터 (종가, 고가, 저가, 거래량)
        """
        self.data = data.copy()
        self.signals = {}

    def calculate_ma(self, periods=MA_PERIODS):
        """이동평균선 계산"""
        for period in periods:
            col_name = f'MA{period}'
            self.data[col_name] = self.data['Close'].rolling(window=period).mean()

        return self.data

    def calculate_rsi(self, period=RSI_PERIOD):
        """
        RSI (Relative Strength Index) 계산
        0-100 범위, 70 이상 과매수, 30 이하 과매도
        """
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        self.data['RSI'] = rsi
        return rsi.iloc[-1]

    def calculate_macd(self, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL):
        """
        MACD (Moving Average Convergence Divergence) 계산
        """
        exp1 = self.data['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=slow, adjust=False).mean()

        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal

        self.data['MACD'] = macd
        self.data['MACD_Signal'] = macd_signal
        self.data['MACD_Hist'] = macd_hist

        return {
            'macd': macd.iloc[-1],
            'signal': macd_signal.iloc[-1],
            'histogram': macd_hist.iloc[-1]
        }

    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """볼린저 밴드 계산"""
        sma = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        self.data['BB_Upper'] = upper_band
        self.data['BB_Middle'] = sma
        self.data['BB_Lower'] = lower_band

        current_price = self.data['Close'].iloc[-1]
        return {
            'upper': upper_band.iloc[-1],
            'middle': sma.iloc[-1],
            'lower': lower_band.iloc[-1],
            'position': (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
        }

    def calculate_volume_analysis(self):
        """거래량 분석"""
        avg_volume = self.data['Volume'].rolling(window=20).mean()
        current_volume = self.data['Volume'].iloc[-1]
        avg_volume_20 = avg_volume.iloc[-1]

        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0

        self.data['Volume_MA20'] = avg_volume

        return {
            'current': current_volume,
            'average': avg_volume_20,
            'ratio': volume_ratio,
            'spike': volume_ratio > 1.5  # 1.5배 이상이면 급등
        }

    def find_support_resistance(self, window=20):
        """지지선/저항선 찾기"""
        recent_data = self.data.tail(window)

        # 최근 고점/저점
        high_max = recent_data['High'].max()
        low_min = recent_data['Low'].min()

        current_price = self.data['Close'].iloc[-1]

        # 현재가와의 거리
        resistance_distance = (high_max - current_price) / current_price
        support_distance = (current_price - low_min) / current_price

        return {
            'resistance': high_max,
            'support': low_min,
            'current': current_price,
            'near_resistance': resistance_distance < 0.03,  # 3% 이내
            'near_support': support_distance < 0.03
        }

    def analyze_trend(self):
        """추세 분석 (이동평균선 정배열/역배열)"""
        ma20 = self.data['MA20'].iloc[-1]
        ma60 = self.data['MA60'].iloc[-1]
        ma120 = self.data['MA120'].iloc[-1]
        current = self.data['Close'].iloc[-1]

        # 정배열: 단기 > 중기 > 장기
        if current > ma20 > ma60 > ma120:
            return {
                'trend': 'strong_uptrend',
                'description': '강한 상승 추세 (정배열)',
                'score': 100
            }
        elif current > ma20 > ma60:
            return {
                'trend': 'uptrend',
                'description': '상승 추세',
                'score': 75
            }
        elif current < ma20 < ma60 < ma120:
            return {
                'trend': 'strong_downtrend',
                'description': '강한 하락 추세 (역배열)',
                'score': 0
            }
        elif current < ma20 < ma60:
            return {
                'trend': 'downtrend',
                'description': '하락 추세',
                'score': 25
            }
        else:
            return {
                'trend': 'sideways',
                'description': '횡보 추세',
                'score': 50
            }

    def detect_golden_cross(self):
        """골든크로스/데드크로스 감지"""
        ma20 = self.data['MA20'].tail(2).values
        ma60 = self.data['MA60'].tail(2).values

        if len(ma20) < 2 or len(ma60) < 2:
            return None

        # 골든크로스: MA20이 MA60을 상향 돌파
        if ma20[0] <= ma60[0] and ma20[1] > ma60[1]:
            return {
                'type': 'golden_cross',
                'description': '골든크로스 발생 (매수 신호)',
                'signal': 'buy',
                'strength': 'strong'
            }

        # 데드크로스: MA20이 MA60을 하향 돌파
        if ma20[0] >= ma60[0] and ma20[1] < ma60[1]:
            return {
                'type': 'dead_cross',
                'description': '데드크로스 발생 (매도 신호)',
                'signal': 'sell',
                'strength': 'strong'
            }

        return None

    def analyze_all(self):
        """모든 기술적 지표 종합 분석"""
        print("📊 기술적 지표 분석 중...")

        # 모든 지표 계산
        self.calculate_ma()
        rsi = self.calculate_rsi()
        macd = self.calculate_macd()
        bb = self.calculate_bollinger_bands()
        volume = self.calculate_volume_analysis()
        sr = self.find_support_resistance()
        trend = self.analyze_trend()
        cross = self.detect_golden_cross()

        # 신호 판단
        signals = []

        # RSI 신호
        if rsi < 30:
            signals.append({
                'indicator': 'RSI',
                'signal': 'buy',
                'strength': 'strong',
                'reason': f'RSI {rsi:.1f} (과매도)',
                'score': 15
            })
        elif rsi < 40:
            signals.append({
                'indicator': 'RSI',
                'signal': 'buy',
                'strength': 'weak',
                'reason': f'RSI {rsi:.1f} (매수 관심)',
                'score': 8
            })
        elif rsi > 70:
            signals.append({
                'indicator': 'RSI',
                'signal': 'sell',
                'strength': 'strong',
                'reason': f'RSI {rsi:.1f} (과매수)',
                'score': -15
            })

        # MACD 신호
        if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
            signals.append({
                'indicator': 'MACD',
                'signal': 'buy',
                'strength': 'strong' if abs(macd['histogram']) > 0.5 else 'weak',
                'reason': 'MACD 골든크로스',
                'score': 15
            })
        elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
            signals.append({
                'indicator': 'MACD',
                'signal': 'sell',
                'strength': 'strong' if abs(macd['histogram']) > 0.5 else 'weak',
                'reason': 'MACD 데드크로스',
                'score': -15
            })

        # 추세 신호
        if trend['score'] >= 75:
            signals.append({
                'indicator': '추세',
                'signal': 'buy',
                'strength': 'strong',
                'reason': trend['description'],
                'score': 10
            })
        elif trend['score'] <= 25:
            signals.append({
                'indicator': '추세',
                'signal': 'sell',
                'strength': 'strong',
                'reason': trend['description'],
                'score': -10
            })

        # 거래량 신호
        if volume['spike']:
            signals.append({
                'indicator': '거래량',
                'signal': 'attention',
                'strength': 'strong',
                'reason': f'거래량 급증 ({volume["ratio"]:.1f}배)',
                'score': 15
            })

        # 지지/저항 신호
        if sr['near_support']:
            signals.append({
                'indicator': '지지선',
                'signal': 'buy',
                'strength': 'medium',
                'reason': '주요 지지선 근처',
                'score': 10
            })

        # 크로스 신호
        if cross:
            score = 15 if cross['signal'] == 'buy' else -15
            signals.append({
                'indicator': '이평선',
                'signal': cross['signal'],
                'strength': cross['strength'],
                'reason': cross['description'],
                'score': score
            })

        result = {
            'rsi': rsi,
            'macd': macd,
            'bollinger': bb,
            'volume': volume,
            'support_resistance': sr,
            'trend': trend,
            'cross': cross,
            'signals': signals,
            'data': self.data
        }

        print("✅ 기술적 분석 완료")
        return result


# 테스트 코드
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from collectors.stock_collector import StockCollector

    # 삼성전자 데이터로 테스트
    collector = StockCollector()
    data = collector.get_stock_data("005930.KS", period="1y")

    if data is not None:
        analyzer = TechnicalAnalyzer(data)
        result = analyzer.analyze_all()

        print("\n=== 분석 결과 ===")
        print(f"RSI: {result['rsi']:.2f}")
        print(f"MACD: {result['macd']['macd']:.2f}")
        print(f"추세: {result['trend']['description']}")
        print(f"\n신호 개수: {len(result['signals'])}")
        for signal in result['signals']:
            print(f"- [{signal['indicator']}] {signal['reason']} (점수: {signal['score']})")
