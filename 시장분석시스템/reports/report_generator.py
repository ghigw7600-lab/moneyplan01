# -*- coding: utf-8 -*-
"""
보고서 생성 엔진
HTML 형식의 투자 분석 보고서 생성
"""

from datetime import datetime
import os


class ReportGenerator:
    """보고서 생성기"""

    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_html_report(self, ticker, analysis_data):
        """
        HTML 투자 분석 보고서 생성

        Args:
            ticker (str): 종목 코드/이름
            analysis_data (dict): 종합 분석 데이터

        Returns:
            str: 생성된 파일 경로
        """
        print("📄 보고서 생성 중...")

        confidence = analysis_data.get('confidence', {})
        technical = analysis_data.get('technical', {})
        sentiment = analysis_data.get('sentiment', {})
        company_info = analysis_data.get('company_info', {})

        # HTML 생성
        html = self._generate_html_content(ticker, confidence, technical, sentiment, company_info)

        # 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker.replace('.', '_')}_{timestamp}.html"
        filepath = os.path.join(self.report_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ 보고서 생성 완료: {filepath}")
        return filepath

    def _generate_html_content(self, ticker, confidence, technical, sentiment, company_info):
        """HTML 콘텐츠 생성"""

        signal_emoji = {
            'strong_buy': '🚀',
            'buy': '📈',
            'neutral': '➡️',
            'sell': '📉',
            'strong_sell': '⚠️'
        }

        signal_color = {
            'strong_buy': '#00c851',
            'buy': '#4caf50',
            'neutral': '#ff9800',
            'sell': '#ff5252',
            'strong_sell': '#d32f2f'
        }

        signal = confidence.get('signal', 'neutral')
        score = confidence.get('score', 50)
        emoji = signal_emoji.get(signal, '➡️')
        color = signal_color.get(signal, '#ff9800')

        html = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ticker} 투자 분석 보고서</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .signal-box {{
            background: {color};
            color: white;
            padding: 30px;
            text-align: center;
            font-size: 1.8em;
            font-weight: bold;
        }}
        .signal-box .score {{
            font-size: 3em;
            margin: 10px 0;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .reason-item {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .reason-item .category {{
            color: #667eea;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .reason-item .impact {{
            float: right;
            color: #28a745;
            font-weight: bold;
        }}
        .uncertainty-item {{
            background: #fff3cd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        }}
        .uncertainty-item .factor {{
            color: #856404;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            color: #333;
            font-size: 1.5em;
            font-weight: bold;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .disclaimer {{
            background: #fff3cd;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 헤더 -->
        <div class="header">
            <h1>📊 {ticker} 투자 분석 보고서</h1>
            <div class="timestamp">생성일시: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}</div>
        </div>

        <!-- 신호 박스 -->
        <div class="signal-box">
            <div>{emoji} {confidence.get('signal_strength', '').upper()}</div>
            <div class="score">{score}%</div>
            <div>신뢰도</div>
        </div>

        <!-- 콘텐츠 -->
        <div class="content">
            <!-- 기업 정보 -->
            {self._generate_company_info_html(company_info)}

            <!-- 종합 판단 -->
            <div class="section">
                <h2>🎯 종합 판단</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">포지션</div>
                        <div class="value">{signal.upper()}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">신뢰도</div>
                        <div class="value">{score}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">리스크</div>
                        <div class="value">{'높음' if len(confidence.get('uncertainties', [])) > 3 else '중간' if len(confidence.get('uncertainties', [])) > 1 else '낮음'}</div>
                    </div>
                </div>
            </div>

            <!-- 신뢰도 근거 -->
            <div class="section">
                <h2>📈 신뢰도 근거</h2>
                {self._generate_reasons_html(confidence.get('reasons', []))}
                <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">
                    <strong>합계:</strong> {score}%
                </div>
            </div>

            <!-- 불확실성 요인 -->
            {self._generate_uncertainties_html(confidence.get('uncertainties', []))}

            <!-- 기술적 분석 -->
            {self._generate_technical_html(technical)}

            <!-- 감성 분석 -->
            {self._generate_sentiment_html(sentiment)}

            <!-- 세부 점수 -->
            <div class="section">
                <h2>📊 세부 점수 분석</h2>
                <div class="stats">
                    {self._generate_breakdown_html(confidence.get('breakdown', {}))}
                </div>
            </div>

            <!-- 면책조항 -->
            <div class="disclaimer">
                <strong>⚖️ 면책조항</strong><br>
                이 보고서는 AI 기반 자동 분석이며, 신뢰도 {score}%는 참고용입니다.<br>
                투자 판단은 본인 책임이며, 손실 가능성이 있습니다.<br>
                전문가 상담을 권장합니다.
            </div>
        </div>

        <!-- 푸터 -->
        <div class="footer">
            🤖 Generated with 시장 분석 시스템<br>
            © 2025 All rights reserved.
        </div>
    </div>
</body>
</html>
'''
        return html

    def _generate_company_info_html(self, info):
        """기업 정보 HTML 생성"""
        if not info:
            return ''

        return f'''
            <div class="section">
                <h2>🏢 기업 정보</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">PER</div>
                        <div class="value">{info.get('PER', 'N/A')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">PBR</div>
                        <div class="value">{info.get('PBR', 'N/A')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">ROE</div>
                        <div class="value">{f"{info.get('ROE', 0)*100:.1f}%" if info.get('ROE') else 'N/A'}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">배당수익률</div>
                        <div class="value">{f"{info.get('배당수익률', 0)*100:.1f}%" if info.get('배당수익률') else 'N/A'}</div>
                    </div>
                </div>
            </div>
        '''

    def _generate_reasons_html(self, reasons):
        """근거 목록 HTML 생성"""
        if not reasons:
            return '<p>근거 데이터가 없습니다.</p>'

        html = ''
        for reason in reasons:
            html += f'''
                <div class="reason-item">
                    <div class="category">[{reason['category']}] {reason['indicator']}</div>
                    <span class="impact">{reason['impact']}</span>
                    <div>{reason['reason']}</div>
                </div>
            '''
        return html

    def _generate_uncertainties_html(self, uncertainties):
        """불확실성 HTML 생성"""
        if not uncertainties:
            return ''

        html = '<div class="section"><h2>⚠️ 불확실성 요인</h2>'
        for uncertainty in uncertainties:
            html += f'''
                <div class="uncertainty-item">
                    <div class="factor">• {uncertainty['factor']}</div>
                    <div>{uncertainty['description']}</div>
                    <div style="margin-top: 8px; color: #856404;">
                        → {uncertainty['recommendation']}
                    </div>
                </div>
            '''
        html += '</div>'
        return html

    def _generate_technical_html(self, technical):
        """기술적 분석 HTML 생성"""
        if not technical:
            return ''

        rsi = technical.get('rsi', 0)
        trend = technical.get('trend', {})
        volume = technical.get('volume', {})

        return f'''
            <div class="section">
                <h2>📊 기술적 분석</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">RSI</div>
                        <div class="value">{rsi:.1f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">추세</div>
                        <div class="value" style="font-size: 1em;">{trend.get('description', 'N/A')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">거래량 비율</div>
                        <div class="value">{volume.get('ratio', 1.0):.1f}x</div>
                    </div>
                </div>
            </div>
        '''

    def _generate_sentiment_html(self, sentiment):
        """감성 분석 HTML 생성"""
        if not sentiment:
            return ''

        total = sentiment.get('total_news', 0)
        positive = sentiment.get('positive_count', 0)
        negative = sentiment.get('negative_count', 0)
        neutral = sentiment.get('neutral_count', 0)

        return f'''
            <div class="section">
                <h2>📰 뉴스 감성 분석</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">총 뉴스</div>
                        <div class="value">{total}개</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">긍정</div>
                        <div class="value" style="color: #28a745;">{positive}개</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">부정</div>
                        <div class="value" style="color: #dc3545;">{negative}개</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">중립</div>
                        <div class="value" style="color: #ffc107;">{neutral}개</div>
                    </div>
                </div>
            </div>
        '''

    def _generate_breakdown_html(self, breakdown):
        """세부 점수 HTML 생성"""
        labels = {
            'technical': '기술적 지표',
            'sentiment': '감성 분석',
            'volume': '거래량',
            'support_resistance': '지지/저항'
        }

        html = ''
        for key, value in breakdown.items():
            label = labels.get(key, key)
            html += f'''
                <div class="stat-card">
                    <div class="label">{label}</div>
                    <div class="value">{value}%</div>
                </div>
            '''
        return html


# 테스트 코드
if __name__ == "__main__":
    # 더미 데이터
    test_data = {
        'confidence': {
            'score': 72.5,
            'signal': 'buy',
            'signal_strength': 'medium',
            'reasons': [
                {'category': '기술적 지표', 'indicator': 'RSI', 'reason': 'RSI 28 (과매도)', 'impact': '+15%'},
                {'category': '기술적 지표', 'indicator': 'MACD', 'reason': 'MACD 골든크로스', 'impact': '+15%'},
                {'category': '뉴스 감성', 'indicator': '감성 분석', 'reason': '뉴스 긍정 68%', 'impact': '+20%'}
            ],
            'uncertainties': [
                {'factor': '뉴스 데이터 부족', 'description': '분석된 뉴스가 5개로 적습니다', 'recommendation': '더 많은 뉴스 수집 권장'}
            ],
            'breakdown': {'technical': 75.0, 'sentiment': 68.0, 'volume': 80.0, 'support_resistance': 60.0}
        },
        'technical': {
            'rsi': 28.5,
            'trend': {'description': '상승 추세'},
            'volume': {'ratio': 1.8}
        },
        'sentiment': {
            'total_news': 10,
            'positive_count': 7,
            'negative_count': 2,
            'neutral_count': 1
        },
        'company_info': {
            'PER': 12.5,
            'PBR': 1.2,
            'ROE': 0.085,
            '배당수익률': 0.028
        }
    }

    generator = ReportGenerator()
    filepath = generator.generate_html_report("삼성전자(005930.KS)", test_data)
    print(f"\n보고서 생성: {filepath}")
    print("브라우저에서 열어보세요!")
