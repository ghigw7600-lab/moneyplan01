# -*- coding: utf-8 -*-
"""
종합 의견 생성기
기술적 분석, 감성 분석, 뉴스를 종합하여 서술형 투자 의견 생성
"""


class ComprehensiveAnalyzer:
    """종합 의견 생성기"""

    def generate_opinion(self, data):
        """
        종합 투자 의견 생성

        Args:
            data (dict): 분석 데이터 (technical, sentiment, confidence 포함)

        Returns:
            dict: 종합 의견
        """
        technical = data.get('technical', {})
        sentiment = data.get('sentiment', {})
        confidence = data.get('confidence', {})
        name = data.get('name', '해당 종목')

        # 각 요소 분석
        rsi_opinion = self._analyze_rsi(technical.get('rsi'))
        macd_opinion = self._analyze_macd(technical.get('macd'))
        trend_opinion = self._analyze_trend(technical.get('trend'))
        sentiment_opinion = self._analyze_sentiment(sentiment)

        # 신뢰도 기반 투자 신호
        signal = confidence.get('signal', 'neutral')
        score = confidence.get('score', 50)

        # 종합 의견 생성
        comprehensive_opinion = self._build_comprehensive_opinion(
            name=name,
            rsi_opinion=rsi_opinion,
            macd_opinion=macd_opinion,
            trend_opinion=trend_opinion,
            sentiment_opinion=sentiment_opinion,
            signal=signal,
            score=score,
            technical=technical,
            sentiment=sentiment
        )

        return {
            'comprehensive_opinion': comprehensive_opinion,
            'signal': signal,
            'score': score,
            'components': {
                'rsi': rsi_opinion,
                'macd': macd_opinion,
                'trend': trend_opinion,
                'sentiment': sentiment_opinion
            }
        }

    def _analyze_rsi(self, rsi):
        """RSI 분석"""
        if rsi is None:
            return {'status': 'neutral', 'description': 'RSI 데이터 없음'}

        if rsi > 70:
            return {
                'status': 'negative',
                'description': f'RSI {rsi:.1f}로 과매수 구간에 진입하여 단기 조정 가능성이 있습니다'
            }
        elif rsi < 30:
            return {
                'status': 'positive',
                'description': f'RSI {rsi:.1f}로 과매도 구간에 위치하여 반등 기회가 있을 수 있습니다'
            }
        elif rsi >= 50:
            return {
                'status': 'positive',
                'description': f'RSI {rsi:.1f}로 매수 세력이 우세한 강세 구간입니다'
            }
        else:
            return {
                'status': 'negative',
                'description': f'RSI {rsi:.1f}로 매도 세력이 우세한 약세 구간입니다'
            }

    def _analyze_macd(self, macd):
        """MACD 분석"""
        if not macd:
            return {'status': 'neutral', 'description': 'MACD 데이터 없음'}

        macd_line = macd.get('macd')
        signal_line = macd.get('signal')
        histogram = macd.get('histogram')

        if macd_line > signal_line:
            if histogram > 0.5:
                return {
                    'status': 'positive',
                    'description': 'MACD 골든크로스 상태이며 히스토그램이 강하게 상승 중입니다'
                }
            else:
                return {
                    'status': 'positive',
                    'description': 'MACD 골든크로스 상태로 상승 모멘텀이 있으나 히스토그램 추세를 주시해야 합니다'
                }
        else:
            if histogram < -0.5:
                return {
                    'status': 'negative',
                    'description': 'MACD 데드크로스 상태이며 히스토그램이 강하게 하락 중입니다'
                }
            else:
                return {
                    'status': 'negative',
                    'description': 'MACD 데드크로스 상태로 하락 압력이 있으나 반등 가능성을 열어두어야 합니다'
                }

    def _analyze_trend(self, trend):
        """추세 분석"""
        if not trend:
            return {'status': 'neutral', 'description': '추세 데이터 없음'}

        description = trend.get('description', '')

        if '상승' in description:
            return {
                'status': 'positive',
                'description': f'현재 {description} 중으로 중장기 모멘텀이 긍정적입니다'
            }
        elif '하락' in description:
            return {
                'status': 'negative',
                'description': f'현재 {description} 중으로 하방 압력이 지속되고 있습니다'
            }
        else:
            return {
                'status': 'neutral',
                'description': f'현재 {description} 중으로 방향성이 불명확한 상태입니다'
            }

    def _analyze_sentiment(self, sentiment):
        """감성 분석"""
        if not sentiment:
            return {'status': 'neutral', 'description': '뉴스 감성 데이터 없음'}

        overall = sentiment.get('overall_sentiment', 'neutral')
        positive_count = sentiment.get('positive_count', 0)
        negative_count = sentiment.get('negative_count', 0)
        total = positive_count + negative_count + sentiment.get('neutral_count', 0)

        if total == 0:
            return {
                'status': 'neutral',
                'description': '최근 관련 뉴스가 부족하여 시장 심리를 파악하기 어렵습니다'
            }

        positive_ratio = (positive_count / total * 100) if total > 0 else 0

        if overall == 'positive':
            return {
                'status': 'positive',
                'description': f'최근 뉴스 {total}건 중 {positive_count}건({positive_ratio:.1f}%)이 긍정적이어서 시장 심리가 우호적입니다'
            }
        elif overall == 'negative':
            return {
                'status': 'negative',
                'description': f'최근 뉴스 {total}건 중 {negative_count}건이 부정적이어서 시장 심리가 부정적입니다'
            }
        else:
            return {
                'status': 'neutral',
                'description': f'최근 뉴스 {total}건의 감성이 혼재되어 있어 신중한 접근이 필요합니다'
            }

    def _build_comprehensive_opinion(self, name, rsi_opinion, macd_opinion, trend_opinion,
                                      sentiment_opinion, signal, score, technical, sentiment):
        """종합 의견 작성"""

        # 신호별 기본 문구
        signal_intro = {
            'strong_buy': f'**{name}**은 현재 **강력 매수** 신호를 보이고 있습니다.',
            'buy': f'**{name}**은 현재 **매수** 신호를 보이고 있습니다.',
            'neutral': f'**{name}**은 현재 **중립** 신호로 신중한 접근이 필요합니다.',
            'sell': f'**{name}**은 현재 **매도** 신호를 보이고 있습니다.',
            'strong_sell': f'**{name}**은 현재 **강력 매도** 신호를 보이고 있습니다.'
        }

        # 긍정 요인 수집
        positive_factors = []
        if rsi_opinion['status'] == 'positive':
            positive_factors.append(rsi_opinion['description'])
        if macd_opinion['status'] == 'positive':
            positive_factors.append(macd_opinion['description'])
        if trend_opinion['status'] == 'positive':
            positive_factors.append(trend_opinion['description'])
        if sentiment_opinion['status'] == 'positive':
            positive_factors.append(sentiment_opinion['description'])

        # 부정 요인 수집
        negative_factors = []
        if rsi_opinion['status'] == 'negative':
            negative_factors.append(rsi_opinion['description'])
        if macd_opinion['status'] == 'negative':
            negative_factors.append(macd_opinion['description'])
        if trend_opinion['status'] == 'negative':
            negative_factors.append(trend_opinion['description'])
        if sentiment_opinion['status'] == 'negative':
            negative_factors.append(sentiment_opinion['description'])

        # 종합 의견 구성
        opinion_parts = []

        # 1. 도입부
        opinion_parts.append(signal_intro.get(signal, signal_intro['neutral']))
        opinion_parts.append(f'신뢰도 {score}% 기준으로 분석한 결과는 다음과 같습니다.\n')

        # 2. 긍정 요인
        if positive_factors:
            opinion_parts.append('**📈 긍정적 요인:**')
            for i, factor in enumerate(positive_factors, 1):
                opinion_parts.append(f'{i}. {factor}')
            opinion_parts.append('')

        # 3. 부정 요인
        if negative_factors:
            opinion_parts.append('**📉 우려 요인:**')
            for i, factor in enumerate(negative_factors, 1):
                opinion_parts.append(f'{i}. {factor}')
            opinion_parts.append('')

        # 4. 종합 결론
        opinion_parts.append('**💡 종합 의견:**')

        if signal in ['strong_buy', 'buy']:
            if negative_factors:
                opinion_parts.append(
                    f'긍정적인 요소들이 우세하지만, {len(negative_factors)}가지 우려 요인도 존재합니다. '
                    f'따라서 {self._get_investment_strategy(signal, score, positive_factors, negative_factors)}'
                )
            else:
                opinion_parts.append(
                    f'대부분의 지표가 긍정적이므로 {self._get_investment_strategy(signal, score, positive_factors, negative_factors)}'
                )

        elif signal in ['strong_sell', 'sell']:
            if positive_factors:
                opinion_parts.append(
                    f'우려 요인이 우세하지만 {len(positive_factors)}가지 긍정 요소도 있습니다. '
                    f'{self._get_investment_strategy(signal, score, positive_factors, negative_factors)}'
                )
            else:
                opinion_parts.append(
                    f'대부분의 지표가 부정적이므로 {self._get_investment_strategy(signal, score, positive_factors, negative_factors)}'
                )

        else:  # neutral
            opinion_parts.append(
                f'긍정 요인 {len(positive_factors)}가지와 부정 요인 {len(negative_factors)}가지가 혼재되어 있어 '
                f'{self._get_investment_strategy(signal, score, positive_factors, negative_factors)}'
            )

        # 5. 면책 조항
        opinion_parts.append('\n⚠️ **유의사항:** 본 분석은 AI 기반 참고 자료이며, 실제 투자 판단은 반드시 본인의 책임 하에 이루어져야 합니다. 기업의 재무제표, 산업 전망, 글로벌 경제 상황 등을 종합적으로 고려하시기 바랍니다.')

        return '\n'.join(opinion_parts)

    def _get_investment_strategy(self, signal, score, positive_factors, negative_factors):
        """투자 전략 문구 생성"""

        if signal == 'strong_buy':
            if score >= 80:
                return '적극적인 매수를 고려할 수 있습니다. 다만 분할 매수를 통해 평균 단가를 관리하는 것이 좋습니다.'
            else:
                return '매수를 고려할 수 있으나, 우려 요인을 지속적으로 모니터링하며 신중하게 접근하시기 바랍니다.'

        elif signal == 'buy':
            if len(negative_factors) > 0:
                return '매수를 고려할 수 있으나 우려 요인이 해소될 때까지 지켜보거나 소량 분할 매수가 적절합니다.'
            else:
                return '매수 적기로 판단되며, 본인의 투자 성향에 맞게 포지션을 구축하시기 바랍니다.'

        elif signal == 'sell':
            if len(positive_factors) > 0:
                return '매도 또는 관망을 권장하지만, 긍정 요소가 있으므로 급락 시 손절보다는 반등을 기다려볼 수도 있습니다.'
            else:
                return '보유 중이라면 손절 또는 익절 시점을 고려하고, 신규 진입은 피하는 것이 좋습니다.'

        elif signal == 'strong_sell':
            return '강력한 매도 신호이므로 보유 중이라면 즉시 매도를 고려하고, 신규 매수는 절대 피해야 합니다.'

        else:  # neutral
            return '현 시점에서는 관망하면서 추가 신호를 기다리는 것이 바람직합니다. 급하게 매수/매도하기보다는 시장 상황을 주시하세요.'


# 테스트 코드
if __name__ == "__main__":
    analyzer = ComprehensiveAnalyzer()

    # 테스트 데이터
    test_data = {
        'name': '삼성전자',
        'technical': {
            'rsi': 45.3,
            'macd': {
                'macd': 0.52,
                'signal': 0.48,
                'histogram': 0.04
            },
            'trend': {
                'description': '상승 추세'
            }
        },
        'sentiment': {
            'overall_sentiment': 'positive',
            'positive_count': 15,
            'negative_count': 5,
            'neutral_count': 3
        },
        'confidence': {
            'signal': 'buy',
            'score': 68
        }
    }

    result = analyzer.generate_opinion(test_data)
    print("=" * 60)
    print("종합 투자 의견")
    print("=" * 60)
    print(result['comprehensive_opinion'])
    print("\n" + "=" * 60)
