"""
거래량 분석기 (Phase 3-4)

주요 기능:
1. 거래량 급등/급락 감지
   - 평균 거래량 대비 현재 거래량 비율
   - 거래량 폭등 패턴 (200% 이상)
   - 거래량 급감 패턴 (50% 이하)

2. 거래량 이동평균 분석
   - 5일/20일/60일 거래량 이동평균
   - 거래량 추세 분석

3. 거래대금 분석
   - 일일 거래대금 계산
   - 거래대금 순위 추적

4. 가격-거래량 상관관계
   - 가격 상승 + 거래량 증가 = 강한 상승 신호
   - 가격 상승 + 거래량 감소 = 약한 상승 (조정 가능성)
   - 가격 하락 + 거래량 증가 = 강한 하락 신호
   - 가격 하락 + 거래량 감소 = 약한 하락 (반등 가능성)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class VolumeAnalyzer:
    """거래량 분석기"""

    def __init__(self, short_period=5, medium_period=20, long_period=60):
        """
        초기화

        Args:
            short_period: 단기 거래량 이동평균 (기본값: 5일)
            medium_period: 중기 거래량 이동평균 (기본값: 20일)
            long_period: 장기 거래량 이동평균 (기본값: 60일)
        """
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period

    def analyze(self, df):
        """
        거래량 종합 분석

        Args:
            df: OHLCV 데이터프레임 (columns: Open, High, Low, Close, Volume)

        Returns:
            dict: 분석 결과
        """
        if len(df) < self.long_period + 5:
            return {
                'current_volume': {},
                'volume_ma': {},
                'volume_surge': {},
                'price_volume_correlation': {},
                'trading_value': {},
                'signal': 'neutral',
                'score': 50,
                'recommendations': []
            }

        # 1. 현재 거래량 분석
        current_volume = self._analyze_current_volume(df)

        # 2. 거래량 이동평균 분석
        volume_ma = self._analyze_volume_ma(df)

        # 3. 거래량 급등/급락 감지
        volume_surge = self._detect_volume_surge(df, volume_ma)

        # 4. 가격-거래량 상관관계 분석
        price_volume_corr = self._analyze_price_volume_correlation(df)

        # 5. 거래대금 분석
        trading_value = self._analyze_trading_value(df)

        # 6. 종합 시그널 생성
        signal, score = self._generate_signal(current_volume, volume_surge, price_volume_corr)

        # 7. 투자 전략 추천
        recommendations = self._generate_recommendations(volume_surge, price_volume_corr, signal)

        return {
            'current_volume': current_volume,
            'volume_ma': volume_ma,
            'volume_surge': volume_surge,
            'price_volume_correlation': price_volume_corr,
            'trading_value': trading_value,
            'signal': signal,
            'score': score,
            'recommendations': recommendations
        }

    # ==================== 현재 거래량 분석 ====================

    def _analyze_current_volume(self, df):
        """현재 거래량 분석"""
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        current_volume = latest['Volume']
        previous_volume = previous['Volume']
        avg_volume = df['Volume'].tail(20).mean()

        # 전일 대비 변화율
        volume_change = ((current_volume - previous_volume) / previous_volume * 100) if previous_volume > 0 else 0

        # 평균 대비 비율
        volume_ratio = (current_volume / avg_volume * 100) if avg_volume > 0 else 100

        return {
            'current': int(current_volume),
            'previous': int(previous_volume),
            'average_20d': int(avg_volume),
            'change_pct': float(volume_change),
            'ratio_to_avg': float(volume_ratio),
            'status': self._get_volume_status(volume_ratio)
        }

    def _get_volume_status(self, ratio):
        """거래량 상태 판단"""
        if ratio >= 200:
            return {
                'level': 'extreme_surge',
                'description': '거래량 폭등 (평균의 200% 이상)',
                'icon': '🔥',
                'color': '#dc3545'
            }
        elif ratio >= 150:
            return {
                'level': 'surge',
                'description': '거래량 급등 (평균의 150% 이상)',
                'icon': '📈',
                'color': '#ff6b6b'
            }
        elif ratio >= 120:
            return {
                'level': 'high',
                'description': '거래량 높음 (평균의 120% 이상)',
                'icon': '⬆️',
                'color': '#28a745'
            }
        elif ratio >= 80:
            return {
                'level': 'normal',
                'description': '거래량 정상 (평균 수준)',
                'icon': '➡️',
                'color': '#17a2b8'
            }
        elif ratio >= 50:
            return {
                'level': 'low',
                'description': '거래량 낮음 (평균의 50~80%)',
                'icon': '⬇️',
                'color': '#ffc107'
            }
        else:
            return {
                'level': 'very_low',
                'description': '거래량 매우 낮음 (평균의 50% 미만)',
                'icon': '💤',
                'color': '#6c757d'
            }

    # ==================== 거래량 이동평균 분석 ====================

    def _analyze_volume_ma(self, df):
        """거래량 이동평균 분석"""
        df_copy = df.copy()

        # 거래량 이동평균 계산
        df_copy['Volume_MA5'] = df_copy['Volume'].rolling(window=self.short_period).mean()
        df_copy['Volume_MA20'] = df_copy['Volume'].rolling(window=self.medium_period).mean()
        df_copy['Volume_MA60'] = df_copy['Volume'].rolling(window=self.long_period).mean()

        latest = df_copy.iloc[-1]

        return {
            'ma5': int(latest['Volume_MA5']) if not pd.isna(latest['Volume_MA5']) else None,
            'ma20': int(latest['Volume_MA20']) if not pd.isna(latest['Volume_MA20']) else None,
            'ma60': int(latest['Volume_MA60']) if not pd.isna(latest['Volume_MA60']) else None,
            'trend': self._get_volume_trend(df_copy)
        }

    def _get_volume_trend(self, df):
        """거래량 추세 분석"""
        if len(df) < 10:
            return {'direction': 'unknown', 'description': '데이터 부족'}

        # 최근 10일 거래량 추세
        recent_volumes = df['Volume'].tail(10).values
        x = np.arange(len(recent_volumes))
        slope = np.polyfit(x, recent_volumes, 1)[0]

        avg_volume = df['Volume'].tail(20).mean()
        slope_pct = (slope / avg_volume * 100) if avg_volume > 0 else 0

        if slope_pct > 5:
            return {
                'direction': 'increasing',
                'description': '거래량 증가 추세',
                'icon': '📈',
                'slope_pct': float(slope_pct)
            }
        elif slope_pct > 2:
            return {
                'direction': 'slightly_increasing',
                'description': '거래량 소폭 증가',
                'icon': '↗️',
                'slope_pct': float(slope_pct)
            }
        elif slope_pct > -2:
            return {
                'direction': 'stable',
                'description': '거래량 안정',
                'icon': '➡️',
                'slope_pct': float(slope_pct)
            }
        elif slope_pct > -5:
            return {
                'direction': 'slightly_decreasing',
                'description': '거래량 소폭 감소',
                'icon': '↘️',
                'slope_pct': float(slope_pct)
            }
        else:
            return {
                'direction': 'decreasing',
                'description': '거래량 감소 추세',
                'icon': '📉',
                'slope_pct': float(slope_pct)
            }

    # ==================== 거래량 급등/급락 감지 ====================

    def _detect_volume_surge(self, df, volume_ma):
        """거래량 급등/급락 감지"""
        if len(df) < 5:
            return {'detected': False}

        latest = df.iloc[-1]
        current_volume = latest['Volume']
        ma20 = volume_ma['ma20']

        if ma20 is None or ma20 == 0:
            return {'detected': False}

        ratio = (current_volume / ma20) * 100

        # 거래량 폭등 (200% 이상)
        if ratio >= 200:
            return {
                'detected': True,
                'type': 'extreme_surge',
                'ratio': float(ratio),
                'description': f'거래량 폭등! 평균 대비 {ratio:.0f}%',
                'icon': '🔥',
                'reliability': 90,
                'signal': 'attention'  # 주목 필요
            }

        # 거래량 급등 (150% 이상)
        elif ratio >= 150:
            return {
                'detected': True,
                'type': 'surge',
                'ratio': float(ratio),
                'description': f'거래량 급등! 평균 대비 {ratio:.0f}%',
                'icon': '📈',
                'reliability': 80,
                'signal': 'buy_or_sell'  # 방향성에 따라 판단
            }

        # 거래량 급감 (50% 이하)
        elif ratio <= 50:
            return {
                'detected': True,
                'type': 'decline',
                'ratio': float(ratio),
                'description': f'거래량 급감! 평균 대비 {ratio:.0f}%',
                'icon': '💤',
                'reliability': 70,
                'signal': 'caution'  # 관심 저하
            }

        return {'detected': False}

    # ==================== 가격-거래량 상관관계 ====================

    def _analyze_price_volume_correlation(self, df):
        """가격-거래량 상관관계 분석"""
        if len(df) < 5:
            return {'pattern': 'unknown'}

        # 최근 5일 데이터
        recent_df = df.tail(5)

        # 가격 변화
        price_change = recent_df['Close'].iloc[-1] - recent_df['Close'].iloc[0]
        price_change_pct = (price_change / recent_df['Close'].iloc[0] * 100) if recent_df['Close'].iloc[0] > 0 else 0

        # 거래량 변화
        volume_avg_recent = recent_df['Volume'].mean()
        volume_avg_before = df.tail(10).head(5)['Volume'].mean() if len(df) >= 10 else volume_avg_recent
        volume_change_pct = ((volume_avg_recent - volume_avg_before) / volume_avg_before * 100) if volume_avg_before > 0 else 0

        # 패턴 분석
        pattern = self._identify_price_volume_pattern(price_change_pct, volume_change_pct)

        return {
            'price_change_pct': float(price_change_pct),
            'volume_change_pct': float(volume_change_pct),
            'pattern': pattern
        }

    def _identify_price_volume_pattern(self, price_change, volume_change):
        """가격-거래량 패턴 식별"""
        # 가격 상승 + 거래량 증가
        if price_change > 2 and volume_change > 20:
            return {
                'type': 'bullish_confirmation',
                'description': '가격 상승 + 거래량 증가 (강한 상승 신호)',
                'icon': '🚀',
                'signal': 'strong_buy',
                'reliability': 85,
                'explanation': '매수세가 강하게 유입되고 있습니다. 상승 추세가 지속될 가능성이 높습니다.'
            }

        # 가격 상승 + 거래량 감소
        elif price_change > 2 and volume_change < -10:
            return {
                'type': 'bullish_weak',
                'description': '가격 상승 + 거래량 감소 (약한 상승)',
                'icon': '⚠️',
                'signal': 'caution',
                'reliability': 60,
                'explanation': '상승세가 약화되고 있습니다. 조정 가능성을 염두에 두세요.'
            }

        # 가격 하락 + 거래량 증가
        elif price_change < -2 and volume_change > 20:
            return {
                'type': 'bearish_confirmation',
                'description': '가격 하락 + 거래량 증가 (강한 하락 신호)',
                'icon': '📉',
                'signal': 'strong_sell',
                'reliability': 85,
                'explanation': '매도세가 강하게 나오고 있습니다. 추가 하락 가능성이 높습니다.'
            }

        # 가격 하락 + 거래량 감소
        elif price_change < -2 and volume_change < -10:
            return {
                'type': 'bearish_weak',
                'description': '가격 하락 + 거래량 감소 (약한 하락)',
                'icon': '🔵',
                'signal': 'watch',
                'reliability': 65,
                'explanation': '하락세가 약화되고 있습니다. 반등 가능성을 주시하세요.'
            }

        # 횡보 (가격 변동 적음)
        elif abs(price_change) <= 2:
            if volume_change > 30:
                return {
                    'type': 'consolidation_high_volume',
                    'description': '횡보 + 거래량 증가 (돌파 대기)',
                    'icon': '⚡',
                    'signal': 'breakout_pending',
                    'reliability': 70,
                    'explanation': '큰 움직임이 임박했을 수 있습니다. 돌파 방향을 주시하세요.'
                }
            else:
                return {
                    'type': 'consolidation',
                    'description': '횡보 (방향성 불분명)',
                    'icon': '➡️',
                    'signal': 'neutral',
                    'reliability': 50,
                    'explanation': '현재 시장은 방향성이 불분명합니다.'
                }

        # 기타
        else:
            return {
                'type': 'mixed',
                'description': '혼조 패턴',
                'icon': '🔀',
                'signal': 'neutral',
                'reliability': 50,
                'explanation': '명확한 패턴이 보이지 않습니다.'
            }

    # ==================== 거래대금 분석 ====================

    def _analyze_trading_value(self, df):
        """거래대금 분석"""
        if len(df) < 1:
            return {}

        # 최근 데이터
        latest = df.iloc[-1]

        # 거래대금 = 거래량 × 종가
        trading_value = latest['Volume'] * latest['Close']
        avg_trading_value = (df['Volume'] * df['Close']).tail(20).mean()

        # 거래대금 비율
        value_ratio = (trading_value / avg_trading_value * 100) if avg_trading_value > 0 else 100

        return {
            'current': int(trading_value),
            'average_20d': int(avg_trading_value),
            'ratio': float(value_ratio),
            'status': '높음' if value_ratio > 120 else '정상' if value_ratio > 80 else '낮음'
        }

    # ==================== 종합 시그널 생성 ====================

    def _generate_signal(self, current_volume, volume_surge, price_volume_corr):
        """종합 시그널 생성"""
        score = 50  # 기본 중립

        # 1. 거래량 상태 점수 (가중치 0.3)
        volume_status = current_volume['status']['level']
        if volume_status == 'extreme_surge':
            score += 15
        elif volume_status == 'surge':
            score += 10
        elif volume_status == 'high':
            score += 5
        elif volume_status == 'low':
            score -= 5
        elif volume_status == 'very_low':
            score -= 10

        # 2. 거래량 급등/급락 점수 (가중치 0.3)
        if volume_surge.get('detected'):
            if volume_surge['type'] == 'extreme_surge':
                score += 10
            elif volume_surge['type'] == 'surge':
                score += 7
            elif volume_surge['type'] == 'decline':
                score -= 10

        # 3. 가격-거래량 상관관계 점수 (가중치 0.4)
        pattern = price_volume_corr.get('pattern', {})
        if pattern.get('signal') == 'strong_buy':
            score += 20
        elif pattern.get('signal') == 'strong_sell':
            score -= 20
        elif pattern.get('signal') == 'caution':
            score -= 5
        elif pattern.get('signal') == 'watch':
            score += 5

        # 점수를 0~100 범위로 조정
        score = max(0, min(100, score))

        # 시그널 변환
        if score >= 75:
            signal = 'strong_buy'
        elif score >= 60:
            signal = 'buy'
        elif score >= 40:
            signal = 'neutral'
        elif score >= 25:
            signal = 'sell'
        else:
            signal = 'strong_sell'

        return signal, score

    # ==================== 투자 전략 추천 ====================

    def _generate_recommendations(self, volume_surge, price_volume_corr, signal):
        """투자 전략 추천"""
        recommendations = []

        # 1. 거래량 폭등 전략
        if volume_surge.get('detected') and volume_surge['type'] in ['extreme_surge', 'surge']:
            pattern = price_volume_corr.get('pattern', {})
            if pattern.get('signal') in ['strong_buy', 'breakout_pending']:
                recommendations.append({
                    'strategy': '거래량 폭등 돌파 전략',
                    'action': '매수',
                    'confidence': volume_surge['reliability'],
                    'reason': f"{volume_surge['description']} + {pattern.get('description', '')}",
                    'entry': '현재가 또는 소폭 조정 시',
                    'target': '단기 +10~15% 목표',
                    'stop_loss': '거래량 급감 시 손절',
                    'icon': '🔥'
                })

        # 2. 강한 상승 확인 전략
        pattern = price_volume_corr.get('pattern', {})
        if pattern.get('type') == 'bullish_confirmation':
            recommendations.append({
                'strategy': '상승 추세 확인 전략',
                'action': '매수 또는 추가 매수',
                'confidence': pattern['reliability'],
                'reason': pattern['explanation'],
                'entry': '조정 시 분할 매수',
                'target': '추세 지속 시 목표가 상향',
                'stop_loss': '거래량 감소 + 가격 하락 시',
                'icon': '🚀'
            })

        # 3. 강한 하락 확인 전략
        elif pattern.get('type') == 'bearish_confirmation':
            recommendations.append({
                'strategy': '하락 추세 확인 전략',
                'action': '매도 또는 관망',
                'confidence': pattern['reliability'],
                'reason': pattern['explanation'],
                'entry': '보유 중이라면 손절 고려',
                'target': '추가 하락 예상',
                'stop_loss': '반등 신호 나올 때까지 관망',
                'icon': '📉'
            })

        # 4. 돌파 대기 전략
        elif pattern.get('type') == 'consolidation_high_volume':
            recommendations.append({
                'strategy': '횡보 돌파 대기 전략',
                'action': '돌파 방향 확인 후 진입',
                'confidence': pattern['reliability'],
                'reason': pattern['explanation'],
                'entry': '상향 돌파 시 매수 / 하향 이탈 시 관망',
                'target': '돌파 방향으로 큰 움직임 예상',
                'stop_loss': '진입 반대 방향 전환 시',
                'icon': '⚡'
            })

        # 5. 거래량 감소 주의 전략
        if volume_surge.get('detected') and volume_surge['type'] == 'decline':
            recommendations.append({
                'strategy': '거래량 감소 주의 전략',
                'action': '관망',
                'confidence': 60,
                'reason': '거래량 급감 - 시장 관심 저하',
                'entry': '거래량 회복 확인 후 진입',
                'target': '거래량 회복 시까지 대기',
                'stop_loss': 'N/A',
                'icon': '💤'
            })

        # 신뢰도 높은 순으로 정렬
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        return recommendations[:3]  # 상위 3개만 반환


if __name__ == '__main__':
    """테스트 코드"""
    # 샘플 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    # 거래량 급등 시뮬레이션
    volumes = np.random.randint(1000000, 3000000, 100)
    volumes[-5:] = np.random.randint(5000000, 8000000, 5)  # 최근 5일 거래량 급등

    sample_data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': volumes
    }, index=dates)

    # 분석 실행
    analyzer = VolumeAnalyzer()
    result = analyzer.analyze(sample_data)

    print("=== 거래량 분석 결과 ===")
    print(f"\n[현재 거래량]")
    print(f"현재: {result['current_volume']['current']:,}")
    print(f"전일: {result['current_volume']['previous']:,}")
    print(f"20일 평균: {result['current_volume']['average_20d']:,}")
    print(f"평균 대비: {result['current_volume']['ratio_to_avg']:.1f}%")
    print(f"상태: {result['current_volume']['status']['icon']} {result['current_volume']['status']['description']}")

    print(f"\n[거래량 이동평균]")
    print(f"5일 평균: {result['volume_ma']['ma5']:,}")
    print(f"20일 평균: {result['volume_ma']['ma20']:,}")
    print(f"60일 평균: {result['volume_ma']['ma60']:,}")
    print(f"추세: {result['volume_ma']['trend']['icon']} {result['volume_ma']['trend']['description']}")

    print(f"\n[거래량 급등/급락]")
    if result['volume_surge']['detected']:
        print(f"{result['volume_surge']['icon']} {result['volume_surge']['description']}")
        print(f"신뢰도: {result['volume_surge']['reliability']}%")
    else:
        print("감지된 급등/급락 없음")

    print(f"\n[가격-거래량 상관관계]")
    pattern = result['price_volume_correlation']['pattern']
    print(f"{pattern['icon']} {pattern['description']}")
    print(f"신뢰도: {pattern['reliability']}%")
    print(f"설명: {pattern['explanation']}")

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
