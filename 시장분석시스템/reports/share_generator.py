# -*- coding: utf-8 -*-
"""
공유하기 텍스트 생성기 (70% 간소화 버전)
프리미엄 PDF의 70% 간소화 버전
"""

from datetime import datetime


class ShareTextGenerator:
    """공유하기 텍스트 생성기"""

    def __init__(self):
        pass

    def generate_share_text(self, analysis_data):
        """
        70% 간소화된 공유 텍스트 생성

        Args:
            analysis_data: 전체 분석 데이터

        Returns:
            str: 텍스트 형식 요약
        """
        lines = []

        # 제목
        name = analysis_data.get('name', 'N/A')
        ticker = analysis_data.get('ticker', 'N/A')
        lines.append(f"📊 {name} ({ticker}) 투자 분석 요약")
        lines.append("")
        lines.append("=" * 50)
        lines.append("")

        # 1. AI 투자 의견 (핵심)
        confidence = analysis_data.get('confidence', {})
        signal = confidence.get('signal', 'neutral')
        score = confidence.get('score', 0)

        signal_names = {
            'strong_buy': '🟢 강력 매수 추천',
            'buy': '🟢 매수 추천',
            'neutral': '🟡 중립 (관망)',
            'sell': '🔴 매도 추천',
            'strong_sell': '🔴 강력 매도 추천'
        }

        lines.append(f"💡 AI 투자 의견: {signal_names.get(signal, '중립')}")
        lines.append(f"   신뢰도: {score}%")
        lines.append("")

        # 2. 주요 지표 (TOP 3)
        lines.append("📈 주요 지표 (TOP 3):")
        lines.append("")

        technical = analysis_data.get('technical', {})

        # RSI
        rsi = technical.get('rsi', 0)
        rsi_status = "과매도" if rsi < 30 else "과매수" if rsi > 70 else "정상"
        lines.append(f"  • RSI (14일): {rsi:.1f} ({rsi_status})")

        # MACD
        macd_data = technical.get('macd', {})
        macd_value = macd_data.get('macd', 0)
        macd_signal = macd_data.get('signal', 0)
        macd_status = "골든크로스" if macd_value > macd_signal else "데드크로스" if macd_value < macd_signal else "중립"
        lines.append(f"  • MACD: {macd_status}")

        # 거래량
        volume_data = analysis_data.get('volume', {})
        volume_ratio = volume_data.get('volume_ratio', 1.0)
        volume_status = "급증" if volume_ratio > 1.5 else "급감" if volume_ratio < 0.5 else "정상"
        lines.append(f"  • 거래량: {volume_status} ({volume_ratio:.1f}배)")

        lines.append("")

        # 3. 추천 전략 (TOP 1만)
        bb_rsi = analysis_data.get('bollinger_rsi', {})
        strategies = bb_rsi.get('strategy_suggestions', [])

        if strategies:
            top_strategy = strategies[0]
            lines.append("💰 추천 트레이딩 전략:")
            lines.append("")
            lines.append(f"  전략: {top_strategy.get('strategy', 'N/A')}")
            lines.append(f"  신뢰도: {top_strategy.get('confidence', 0)}%")
            lines.append(f"  이유: {top_strategy.get('reason', 'N/A')}")
            lines.append("")
        else:
            lines.append("💰 추천 트레이딩 전략: 현재 없음")
            lines.append("")

        # 4. 리스크 (TOP 1만)
        uncertainties = confidence.get('uncertainties', [])
        if uncertainties:
            top_risk = uncertainties[0]
            lines.append("⚠️ 주요 리스크:")
            lines.append(f"  {top_risk.get('factor', 'N/A')}")
            lines.append("")
        else:
            lines.append("⚠️ 주요 리스크: 특별한 불확실성 없음")
            lines.append("")

        # 5. 뉴스 감성 (요약)
        sentiment = analysis_data.get('sentiment', {})
        overall_sentiment = sentiment.get('overall_sentiment', 'neutral')
        overall_score = sentiment.get('overall_score', 0)
        positive_count = sentiment.get('positive_count', 0)
        negative_count = sentiment.get('negative_count', 0)

        sentiment_names = {'positive': '긍정', 'negative': '부정', 'neutral': '중립'}
        sentiment_emoji = {'positive': '😊', 'negative': '😟', 'neutral': '😐'}

        lines.append(f"📰 뉴스 감성: {sentiment_emoji.get(overall_sentiment, '😐')} {sentiment_names.get(overall_sentiment, '중립')} ({overall_score*100:.0f}점)")
        lines.append(f"   긍정 {positive_count}개 | 부정 {negative_count}개")
        lines.append("")

        # 6. 생성 정보
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"생성 시각: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}")
        lines.append("생성: AI 시장 분석 시스템 v3.0")
        lines.append("")
        lines.append("⚠️ 본 분석은 참고용이며, 투자 판단은 본인 책임입니다.")

        return "\n".join(lines)


# 편의 함수
def generate_share_text(analysis_data):
    """공유 텍스트 생성 편의 함수"""
    generator = ShareTextGenerator()
    return generator.generate_share_text(analysis_data)


if __name__ == "__main__":
    # 테스트
    test_data = {
        'ticker': 'orderly-network',
        'name': '오덜리',
        'confidence': {
            'score': 65,
            'signal': 'buy',
            'uncertainties': [
                {'factor': '시장 변동성', 'description': '암호화폐 시장의 높은 변동성'},
            ]
        },
        'technical': {
            'rsi': 35.2,
            'macd': {'macd': 0.02, 'signal': 0.01},
        },
        'volume': {
            'volume_ratio': 1.8
        },
        'sentiment': {
            'overall_sentiment': 'positive',
            'overall_score': 0.68,
            'positive_count': 8,
            'negative_count': 2,
        },
        'bollinger_rsi': {
            'strategy_suggestions': [
                {
                    'strategy': '볼린저 밴드 하단 반등 매수',
                    'confidence': 75,
                    'reason': 'RSI 과매도 + 밴드 하단 접촉'
                }
            ]
        }
    }

    print(generate_share_text(test_data))
