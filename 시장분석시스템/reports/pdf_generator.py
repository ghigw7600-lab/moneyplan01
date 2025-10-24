# -*- coding: utf-8 -*-
"""
PDF 보고서 생성기
분석 결과를 PDF로 다운로드
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

class PDFReportGenerator:
    """PDF 보고서 생성"""

    def __init__(self):
        # 한글 폰트 등록 시도 (없으면 영문만 출력)
        try:
            # Windows 기본 폰트
            font_path = "C:\\Windows\\Fonts\\malgun.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Malgun', font_path))
                self.korean_font = 'Malgun'
            else:
                self.korean_font = 'Helvetica'
        except:
            self.korean_font = 'Helvetica'

    def generate_report(self, output_path, analysis_data):
        """
        분석 보고서 PDF 생성

        Args:
            output_path: PDF 저장 경로
            analysis_data: 분석 결과 딕셔너리
        """
        # PDF 문서 생성
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 스타일 설정
        styles = getSampleStyleSheet()

        # 한글 폰트 스타일
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=self.korean_font,
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontName=self.korean_font,
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=self.korean_font,
            fontSize=10,
            leading=14
        )

        # 1. 제목
        title_text = f"AI 시장 분석 보고서"
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 0.3*inch))

        # 2. 기본 정보
        info_data = [
            ['종목명', analysis_data.get('name', 'N/A')],
            ['종목 코드', analysis_data.get('ticker', 'N/A')],
            ['분석 일시', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['현재가', f"{analysis_data.get('current_price', 0):,.0f}원"],
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))

        # 3. 신뢰도 및 투자 신호
        confidence = analysis_data.get('confidence', {})
        story.append(Paragraph("투자 신호", heading_style))

        signal_names = {
            'strong_buy': '강력 매수',
            'buy': '매수',
            'neutral': '중립',
            'sell': '매도',
            'strong_sell': '강력 매도'
        }

        signal_colors = {
            'strong_buy': colors.HexColor('#28a745'),
            'buy': colors.HexColor('#5cb85c'),
            'neutral': colors.HexColor('#ffc107'),
            'sell': colors.HexColor('#dc3545'),
            'strong_sell': colors.HexColor('#c82333')
        }

        signal = confidence.get('signal', 'neutral')
        signal_data = [
            ['신뢰도', f"{confidence.get('score', 0)}%"],
            ['투자 신호', signal_names.get(signal, 'N/A')],
            ['리스크', confidence.get('risk', 'N/A')],
        ]

        signal_table = Table(signal_data, colWidths=[2*inch, 4*inch])
        signal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 1), (1, 1), signal_colors.get(signal, colors.grey)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (1, 1), (1, 1), 14),  # 투자 신호 크게
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(signal_table)
        story.append(Spacer(1, 0.3*inch))

        # 4. 기술적 지표 (상세 버전)
        technical = analysis_data.get('technical', {})
        story.append(Paragraph("기술적 지표 (상세)", heading_style))

        # 기본 지표
        macd_data = technical.get('macd', {})
        current_price = analysis_data.get('current_price', 0)

        technical_data = [
            ['지표', '값', '해석'],
            ['RSI (14일)', f"{technical.get('rsi', 0):.2f}", self._interpret_rsi(technical.get('rsi', 50))],
            ['MACD', f"{macd_data.get('macd', 0):.4f}", self._interpret_macd(macd_data.get('macd', 0), macd_data.get('signal', 0))],
            ['MACD Signal', f"{macd_data.get('signal', 0):.4f}", '시그널선'],
            ['MACD Histogram', f"{macd_data.get('histogram', 0):.4f}", self._interpret_macd_histogram(macd_data.get('histogram', 0))],
        ]

        # 이동평균선 추가
        ma_data = technical.get('ma', {})
        if ma_data:
            ma5 = ma_data.get('ma5', 0)
            ma20 = ma_data.get('ma20', 0)
            ma60 = ma_data.get('ma60', 0)
            ma120 = ma_data.get('ma120', 0)

            technical_data.append(['이동평균 5일', f"{ma5:.2f}", self._interpret_ma(current_price, ma5, '5일')])
            technical_data.append(['이동평균 20일', f"{ma20:.2f}", self._interpret_ma(current_price, ma20, '20일')])
            technical_data.append(['이동평균 60일', f"{ma60:.2f}", self._interpret_ma(current_price, ma60, '60일')])
            technical_data.append(['이동평균 120일', f"{ma120:.2f}", self._interpret_ma(current_price, ma120, '120일')])

        # 볼린저 밴드 추가
        bollinger = technical.get('bollinger', {})
        if bollinger:
            upper = bollinger.get('upper', 0)
            middle = bollinger.get('middle', 0)
            lower = bollinger.get('lower', 0)

            technical_data.append(['볼린저 상단', f"{upper:.2f}", self._interpret_bollinger(current_price, upper, middle, lower, 'upper')])
            technical_data.append(['볼린저 중단', f"{middle:.2f}", '중심선 (20일 이평)'])
            technical_data.append(['볼린저 하단', f"{lower:.2f}", self._interpret_bollinger(current_price, upper, middle, lower, 'lower')])

        # 추세
        trend = technical.get('trend', {})
        if trend:
            technical_data.append(['추세', trend.get('description', 'N/A'), self._interpret_trend(trend.get('description', ''))])
            technical_data.append(['추세 강도', f"{trend.get('strength', 0):.1f}%", self._interpret_trend_strength(trend.get('strength', 0))])

        technical_table = Table(technical_data, colWidths=[2*inch, 2*inch, 2*inch])
        technical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(technical_table)
        story.append(Spacer(1, 0.3*inch))

        # 5. 뉴스 감성 분석 (요약)
        sentiment = analysis_data.get('sentiment', {})
        if sentiment:
            story.append(Paragraph("뉴스 감성 분석 (요약)", heading_style))

            sentiment_names = {
                'positive': '긍정',
                'negative': '부정',
                'neutral': '중립'
            }

            sentiment_data = [
                ['전체 감성', sentiment_names.get(sentiment.get('overall_sentiment', 'neutral'), 'N/A')],
                ['감성 점수', f"{sentiment.get('overall_score', 0)*100:.1f}점"],
                ['긍정 뉴스', f"{sentiment.get('positive_count', 0)}개"],
                ['부정 뉴스', f"{sentiment.get('negative_count', 0)}개"],
            ]

            sentiment_table = Table(sentiment_data, colWidths=[2*inch, 4*inch])
            sentiment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(sentiment_table)
            story.append(Spacer(1, 0.3*inch))

        # 5-2. 뉴스 상세 내역 (전체)
        news_list = analysis_data.get('news', [])
        if news_list:
            story.append(Paragraph("뉴스 상세 내역 - 전체", heading_style))

            news_data = [['번호', '제목', '언론사', '날짜', '감성', 'URL']]
            for i, news in enumerate(news_list, 1):
                # 감성 표시
                sentiment_text = sentiment_names.get(news.get('sentiment', 'neutral'), '중립')

                # URL을 클릭 가능한 형태로 (PDF에서는 텍스트만 표시)
                url = news.get('url', 'N/A')
                url_short = url[:40] + '...' if len(url) > 40 else url

                news_data.append([
                    str(i),
                    news.get('제목', 'N/A'),
                    news.get('언론사', 'N/A'),
                    news.get('날짜', 'N/A').strftime('%Y-%m-%d') if hasattr(news.get('날짜'), 'strftime') else str(news.get('날짜', 'N/A')),
                    sentiment_text,
                    url_short
                ])

            news_table = Table(news_data, colWidths=[0.3*inch, 2.2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 1.4*inch])
            news_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(news_table)
            story.append(Spacer(1, 0.3*inch))

        # 6. AI 종합 투자의견 - 전체 근거 (제한 없음)
        reasons = confidence.get('reasons', [])
        if reasons:
            story.append(Paragraph("AI 종합 투자의견 - 전체 근거", heading_style))

            reasons_data = [['순위', '카테고리', '근거', '영향도']]
            for i, r in enumerate(reasons, 1):  # 전체 다 포함
                reasons_data.append([
                    f"#{i}",
                    r.get('category', ''),
                    r.get('reason', ''),
                    r.get('impact', '')
                ])

            reasons_table = Table(reasons_data, colWidths=[0.5*inch, 1.5*inch, 2.8*inch, 1.2*inch])
            reasons_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(reasons_table)
            story.append(Spacer(1, 0.3*inch))

        # 7. 불확실성 요인 - 전체 (제한 없음)
        uncertainties = confidence.get('uncertainties', [])
        if uncertainties:
            story.append(Paragraph("불확실성 요인 - 전체", heading_style))

            uncertainty_text = []
            for i, u in enumerate(uncertainties, 1):  # 전체 다 포함
                uncertainty_text.append(f"{i}. {u.get('factor', '')}: {u.get('description', '')}")

            for text in uncertainty_text:
                story.append(Paragraph(text, body_style))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.2*inch))

        # 8. 면책조항
        story.append(PageBreak())
        story.append(Paragraph("면책조항", heading_style))

        disclaimer_text = """
        본 보고서는 AI 기반 자동 분석 시스템으로 생성되었으며, 투자 권유가 아닌 참고용 자료입니다.

        • 신뢰도 및 투자 신호는 참고용이며, 실제 투자 판단은 본인 책임입니다.
        • 시장 예측이 불가능한 다양한 변수(규제, 지정학적 리스크 등)가 존재합니다.
        • 손실 가능성이 항상 존재하며, 투자 전 전문가 상담을 권장합니다.
        • 분산 투자 및 손절매 설정을 필수로 하세요.

        생성 시스템: AI 시장 분석 시스템 v2.0
        생성 일시: {datetime}
        """.format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        story.append(Paragraph(disclaimer_text.replace('\n', '<br/>'), body_style))

        # PDF 생성
        doc.build(story)
        print(f"PDF 생성 완료: {output_path}")

        return output_path

    def _interpret_rsi(self, rsi):
        """RSI 값 해석"""
        if rsi < 30:
            return "과매도 (매수 고려)"
        elif rsi < 40:
            return "약세 (관망)"
        elif rsi < 60:
            return "중립 (정상)"
        elif rsi < 70:
            return "강세 (주의)"
        else:
            return "과매수 (매도 고려)"

    def _interpret_macd_histogram(self, histogram):
        """MACD 히스토그램 해석"""
        if histogram > 0.5:
            return "강한 상승세"
        elif histogram > 0:
            return "약한 상승세"
        elif histogram > -0.5:
            return "약한 하락세"
        else:
            return "강한 하락세"

    def _interpret_macd(self, macd, signal):
        """MACD와 시그널 비교 해석"""
        if macd > signal:
            return "골든크로스 (상승 신호)"
        elif macd < signal:
            return "데드크로스 (하락 신호)"
        else:
            return "중립"

    def _interpret_ma(self, current_price, ma_value, period):
        """이동평균선 해석"""
        if ma_value == 0:
            return "데이터 없음"

        diff_pct = ((current_price - ma_value) / ma_value) * 100

        if diff_pct > 5:
            return f"{period} 이평 위 {diff_pct:.1f}% (강세)"
        elif diff_pct > 0:
            return f"{period} 이평 위 {diff_pct:.1f}% (약세)"
        elif diff_pct > -5:
            return f"{period} 이평 아래 {abs(diff_pct):.1f}% (약약)"
        else:
            return f"{period} 이평 아래 {abs(diff_pct):.1f}% (약세)"

    def _interpret_bollinger(self, current_price, upper, middle, lower, position):
        """볼린저 밴드 해석"""
        if upper == 0 or lower == 0:
            return "데이터 없음"

        if position == 'upper':
            if current_price >= upper:
                return "가격이 상단 밴드 돌파 (과매수)"
            else:
                diff_pct = ((upper - current_price) / current_price) * 100
                return f"상단까지 {diff_pct:.1f}% 여유"

        elif position == 'lower':
            if current_price <= lower:
                return "가격이 하단 밴드 이탈 (과매도)"
            else:
                diff_pct = ((current_price - lower) / current_price) * 100
                return f"하단까지 {diff_pct:.1f}% 여유"

        return "중립"

    def _interpret_trend(self, description):
        """추세 해석"""
        if '상승' in description:
            return "매수 기회 고려"
        elif '하락' in description:
            return "매도 또는 관망"
        else:
            return "횡보 중 (방향성 불명확)"

    def _interpret_trend_strength(self, strength):
        """추세 강도 해석"""
        if strength > 10:
            return "매우 강한 추세"
        elif strength > 5:
            return "강한 추세"
        elif strength > 2:
            return "보통 추세"
        else:
            return "약한 추세 (횡보 가능성)"


if __name__ == "__main__":
    # 테스트
    generator = PDFReportGenerator()

    test_data = {
        'ticker': '005930.KS',
        'name': '삼성전자',
        'current_price': 85000,
        'confidence': {
            'score': 72.5,
            'signal': 'buy',
            'risk': '중간',
            'reasons': [
                {'category': '기술적 지표', 'reason': 'RSI 28 (과매도)', 'impact': '+15%'},
                {'category': '기술적 지표', 'reason': 'MACD 골든크로스', 'impact': '+15%'},
                {'category': '뉴스 감성', 'reason': '뉴스 긍정 68%', 'impact': '+20%'},
            ],
            'uncertainties': [
                {'factor': '뉴스 데이터 부족', 'description': '분석된 뉴스가 5개로 적습니다'},
            ]
        },
        'technical': {
            'rsi': 28.5,
            'macd': {'macd': 1.23, 'signal': 0.95},
            'trend': {'description': '상승 추세'}
        },
        'sentiment': {
            'overall_sentiment': 'positive',
            'overall_score': 0.68,
            'positive_count': 10,
            'negative_count': 2
        }
    }

    output = "test_report.pdf"
    generator.generate_report(output, test_data)
    print(f"테스트 완료: {output}")
