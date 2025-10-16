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

        # 4. 기술적 지표
        technical = analysis_data.get('technical', {})
        story.append(Paragraph("기술적 지표", heading_style))

        technical_data = [
            ['지표', '값'],
            ['RSI', f"{technical.get('rsi', 0):.1f}"],
            ['MACD', f"{technical.get('macd', {}).get('macd', 0):.2f}"],
            ['Signal', f"{technical.get('macd', {}).get('signal', 0):.2f}"],
            ['추세', technical.get('trend', {}).get('description', 'N/A')],
        ]

        technical_table = Table(technical_data, colWidths=[2*inch, 4*inch])
        technical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(technical_table)
        story.append(Spacer(1, 0.3*inch))

        # 5. 뉴스 감성 분석
        sentiment = analysis_data.get('sentiment', {})
        if sentiment:
            story.append(Paragraph("뉴스 감성 분석", heading_style))

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

        # 6. 주요 근거
        reasons = confidence.get('reasons', [])
        if reasons:
            story.append(Paragraph("주요 근거", heading_style))

            reasons_data = [['카테고리', '근거', '영향도']]
            for r in reasons[:10]:  # 최대 10개
                reasons_data.append([
                    r.get('category', ''),
                    r.get('reason', ''),
                    r.get('impact', '')
                ])

            reasons_table = Table(reasons_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
            reasons_table.setStyle(TableStyle([
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
            story.append(reasons_table)
            story.append(Spacer(1, 0.3*inch))

        # 7. 불확실성 요인
        uncertainties = confidence.get('uncertainties', [])
        if uncertainties:
            story.append(Paragraph("불확실성 요인", heading_style))

            uncertainty_text = []
            for u in uncertainties[:5]:  # 최대 5개
                uncertainty_text.append(f"• {u.get('factor', '')}: {u.get('description', '')}")

            for text in uncertainty_text:
                story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 0.3*inch))

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
        print(f"✅ PDF 생성 완료: {output_path}")

        return output_path


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
