# -*- coding: utf-8 -*-
"""
신뢰도 계산 시스템
각 지표의 신호를 종합하여 신뢰도와 근거를 계산
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import WEIGHTS, SIGNAL_THRESHOLDS


class ConfidenceCalculator:
    """신뢰도 계산기"""

    def __init__(self):
        self.weights = WEIGHTS
        self.thresholds = SIGNAL_THRESHOLDS
        self.reasons = []
        self.uncertainties = []

    def calculate_confidence(self, technical_result, sentiment_result):
        """
        종합 신뢰도 계산

        Args:
            technical_result (dict): 기술적 분석 결과
            sentiment_result (dict): 감성 분석 결과

        Returns:
            dict: 신뢰도, 신호, 근거, 불확실성
        """
        print("🎯 신뢰도 계산 중...")

        self.reasons = []
        self.uncertainties = []

        # 1. 기술적 지표 점수 (40%)
        tech_score = self._calculate_technical_score(technical_result)

        # 2. 감성 분석 점수 (30%)
        sentiment_score = self._calculate_sentiment_score(sentiment_result)

        # 3. 거래량 점수 (20%)
        volume_score = self._calculate_volume_score(technical_result.get('volume', {}))

        # 4. 지지/저항 점수 (10%)
        sr_score = self._calculate_support_resistance_score(
            technical_result.get('support_resistance', {})
        )

        # 가중 평균 계산
        total_score = (
            tech_score * self.weights['technical'] +
            sentiment_score * self.weights['sentiment'] +
            volume_score * self.weights['volume'] +
            sr_score * self.weights['support']
        ) * 100

        # 보정 (0-100 범위)
        total_score = max(0, min(100, total_score))

        # 신호 판단
        signal = self._determine_signal(total_score)

        # 불확실성 체크
        self._check_uncertainties(technical_result, sentiment_result)

        result = {
            'score': round(total_score, 1),
            'signal': signal['type'],
            'signal_strength': signal['strength'],
            'reasons': self.reasons,
            'uncertainties': self.uncertainties,
            'breakdown': {
                'technical': round(tech_score * 100, 1),
                'sentiment': round(sentiment_score * 100, 1),
                'volume': round(volume_score * 100, 1),
                'support_resistance': round(sr_score * 100, 1)
            }
        }

        print(f"✅ 신뢰도 계산 완료: {total_score:.1f}% ({signal['type']})")
        return result

    def _calculate_technical_score(self, tech_result):
        """기술적 지표 점수 계산"""
        score = 0.5  # 기본 중립
        signals = tech_result.get('signals', [])

        for signal in signals:
            signal_score = signal.get('score', 0)

            if signal_score > 0:
                score += signal_score / 100
                self.reasons.append({
                    'category': '기술적 지표',
                    'indicator': signal['indicator'],
                    'reason': signal['reason'],
                    'impact': f"+{signal_score}%"
                })
            elif signal_score < 0:
                score += signal_score / 100
                self.reasons.append({
                    'category': '기술적 지표',
                    'indicator': signal['indicator'],
                    'reason': signal['reason'],
                    'impact': f"{signal_score}%"
                })

        # RSI 점수
        rsi = tech_result.get('rsi', 50)
        if rsi < 30:
            score += 0.15
            self.reasons.append({
                'category': '기술적 지표',
                'indicator': 'RSI',
                'reason': f'RSI {rsi:.1f} (과매도 구간)',
                'impact': '+15%'
            })
        elif rsi > 70:
            score -= 0.15
            self.reasons.append({
                'category': '기술적 지표',
                'indicator': 'RSI',
                'reason': f'RSI {rsi:.1f} (과매수 구간)',
                'impact': '-15%'
            })

        # 추세 점수
        trend = tech_result.get('trend', {})
        trend_score = trend.get('score', 50)
        if trend_score >= 75:
            score += 0.10
            self.reasons.append({
                'category': '기술적 지표',
                'indicator': '추세',
                'reason': trend.get('description', '상승 추세'),
                'impact': '+10%'
            })
        elif trend_score <= 25:
            score -= 0.10
            self.reasons.append({
                'category': '기술적 지표',
                'indicator': '추세',
                'reason': trend.get('description', '하락 추세'),
                'impact': '-10%'
            })

        return max(0, min(1, score))

    def _calculate_sentiment_score(self, sentiment_result):
        """감성 분석 점수 계산"""
        if not sentiment_result or sentiment_result.get('total_news', 0) == 0:
            self.uncertainties.append({
                'factor': '뉴스 데이터 부족',
                'description': '감성 분석을 위한 뉴스가 충분하지 않습니다',
                'recommendation': '수동으로 최신 뉴스를 확인하세요'
            })
            return 0.5  # 중립

        overall_score = sentiment_result.get('overall_score', 0.5)
        confidence = sentiment_result.get('confidence', 0)
        total_news = sentiment_result.get('total_news', 0)

        # 뉴스 개수가 적으면 신뢰도 낮음
        if total_news < 5:
            self.uncertainties.append({
                'factor': '뉴스 개수 부족',
                'description': f'분석된 뉴스가 {total_news}개로 적습니다',
                'recommendation': '더 많은 뉴스 수집 권장'
            })

        # 감성 점수 변환
        score = overall_score

        # 근거 추가
        sentiment_type = sentiment_result.get('overall_sentiment', 'neutral')
        positive_ratio = sentiment_result.get('positive_ratio', 0) * 100
        negative_ratio = sentiment_result.get('negative_ratio', 0) * 100

        if sentiment_type == 'positive':
            self.reasons.append({
                'category': '뉴스 감성',
                'indicator': '감성 분석',
                'reason': f'뉴스 긍정 {positive_ratio:.0f}% (총 {total_news}개)',
                'impact': '+20%'
            })
        elif sentiment_type == 'negative':
            self.reasons.append({
                'category': '뉴스 감성',
                'indicator': '감성 분석',
                'reason': f'뉴스 부정 {negative_ratio:.0f}% (총 {total_news}개)',
                'impact': '-20%'
            })
        else:
            self.reasons.append({
                'category': '뉴스 감성',
                'indicator': '감성 분석',
                'reason': f'뉴스 중립 (총 {total_news}개)',
                'impact': '0%'
            })

        return score

    def _calculate_volume_score(self, volume_info):
        """거래량 점수 계산"""
        if not volume_info:
            return 0.5

        volume_ratio = volume_info.get('ratio', 1.0)
        is_spike = volume_info.get('spike', False)

        score = 0.5

        if is_spike:
            score += 0.15
            self.reasons.append({
                'category': '거래량',
                'indicator': '거래량 분석',
                'reason': f'거래량 급증 ({volume_ratio:.1f}배)',
                'impact': '+15%'
            })
        elif volume_ratio > 1.2:
            score += 0.08
            self.reasons.append({
                'category': '거래량',
                'indicator': '거래량 분석',
                'reason': f'거래량 증가 ({volume_ratio:.1f}배)',
                'impact': '+8%'
            })
        elif volume_ratio < 0.7:
            score -= 0.05
            self.uncertainties.append({
                'factor': '거래량 부족',
                'description': f'평균 대비 {volume_ratio:.1%} 거래량',
                'recommendation': '거래 성사 가능성 주의'
            })

        return max(0, min(1, score))

    def _calculate_support_resistance_score(self, sr_info):
        """지지/저항선 점수 계산"""
        if not sr_info:
            return 0.5

        score = 0.5

        near_support = sr_info.get('near_support', False)
        near_resistance = sr_info.get('near_resistance', False)

        if near_support:
            score += 0.10
            self.reasons.append({
                'category': '지지/저항',
                'indicator': '지지선',
                'reason': f'주요 지지선 근처 ({sr_info.get("support"):,.0f})',
                'impact': '+10%'
            })

        if near_resistance:
            score -= 0.05
            self.uncertainties.append({
                'factor': '저항선 근접',
                'description': f'저항선 ({sr_info.get("resistance"):,.0f}) 근처',
                'recommendation': '돌파 여부 확인 필요'
            })

        return max(0, min(1, score))

    def _determine_signal(self, score):
        """점수를 기반으로 신호 판단"""
        if score >= self.thresholds['strong_buy']:
            return {
                'type': 'strong_buy',
                'strength': 'strong',
                'description': '강력 매수',
                'emoji': '🚀'
            }
        elif score >= self.thresholds['buy']:
            return {
                'type': 'buy',
                'strength': 'medium',
                'description': '매수',
                'emoji': '📈'
            }
        elif score >= self.thresholds['neutral']:
            return {
                'type': 'neutral',
                'strength': 'weak',
                'description': '중립',
                'emoji': '➡️'
            }
        elif score >= (100 - self.thresholds['sell']):
            return {
                'type': 'sell',
                'strength': 'medium',
                'description': '매도',
                'emoji': '📉'
            }
        else:
            return {
                'type': 'strong_sell',
                'strength': 'strong',
                'description': '강력 매도',
                'emoji': '⚠️'
            }

    def _check_uncertainties(self, technical_result, sentiment_result):
        """추가 불확실성 요인 체크"""
        # 변동성 체크
        bb = technical_result.get('bollinger', {})
        if bb:
            bb_position = bb.get('position', 0.5)
            if bb_position > 0.9:
                self.uncertainties.append({
                    'factor': '고변동성',
                    'description': '볼린저밴드 상단 근접 (과열 가능성)',
                    'recommendation': '급격한 조정 가능성 주의'
                })
            elif bb_position < 0.1:
                self.uncertainties.append({
                    'factor': '고변동성',
                    'description': '볼린저밴드 하단 근접 (과도한 하락)',
                    'recommendation': '반등 가능성 염두'
                })


# 테스트 코드
if __name__ == "__main__":
    # 더미 데이터로 테스트
    technical_result = {
        'rsi': 28,
        'signals': [
            {'indicator': 'MACD', 'reason': 'MACD 골든크로스', 'score': 15},
            {'indicator': '추세', 'reason': '상승 추세', 'score': 10}
        ],
        'volume': {'ratio': 1.8, 'spike': True},
        'support_resistance': {'near_support': True, 'support': 75000, 'near_resistance': False},
        'trend': {'score': 75, 'description': '상승 추세'},
        'bollinger': {'position': 0.3}
    }

    sentiment_result = {
        'overall_score': 0.68,
        'overall_sentiment': 'positive',
        'positive_ratio': 0.65,
        'negative_ratio': 0.20,
        'total_news': 10,
        'confidence': 0.75
    }

    calculator = ConfidenceCalculator()
    result = calculator.calculate_confidence(technical_result, sentiment_result)

    print("\n=== 신뢰도 계산 결과 ===")
    print(f"신뢰도: {result['score']}%")
    print(f"신호: {result['signal']} ({result['signal_strength']})")

    print("\n📊 근거:")
    for reason in result['reasons']:
        print(f"  [{reason['category']}] {reason['reason']} {reason['impact']}")

    print("\n⚠️ 불확실성:")
    for uncertainty in result['uncertainties']:
        print(f"  • {uncertainty['factor']}: {uncertainty['description']}")
        print(f"    → {uncertainty['recommendation']}")

    print("\n📈 세부 점수:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}%")
