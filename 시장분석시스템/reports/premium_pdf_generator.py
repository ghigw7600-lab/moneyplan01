# -*- coding: utf-8 -*-
"""
프리미엄 PDF 보고서 생성기
대기업 스타일 보고서 with 모든 분석 결과 포함
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os


class PremiumPDFGenerator:
    """프리미엄 PDF 보고서 생성기"""

    def __init__(self):
        # 한글 폰트 등록
        try:
            font_path = "C:\\Windows\\Fonts\\malgun.ttf"
            font_bold_path = "C:\\Windows\\Fonts\\malgunbd.ttf"

            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Malgun', font_path))
                self.korean_font = 'Malgun'

                if os.path.exists(font_bold_path):
                    pdfmetrics.registerFont(TTFont('MalgunBold', font_bold_path))
                    self.korean_font_bold = 'MalgunBold'
                else:
                    self.korean_font_bold = 'Malgun'
            else:
                self.korean_font = 'Helvetica'
                self.korean_font_bold = 'Helvetica-Bold'
        except:
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'

        # 스타일 정의
        self._define_styles()

    def _define_styles(self):
        """대기업 보고서 스타일 정의"""
        styles = getSampleStyleSheet()

        # 제목 스타일 (표지)
        self.cover_title = ParagraphStyle(
            'CoverTitle',
            parent=styles['Title'],
            fontName=self.korean_font_bold,
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # 부제목
        self.cover_subtitle = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName=self.korean_font,
            fontSize=16,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # 섹션 제목 (H1)
        self.section_title = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontName=self.korean_font_bold,
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=0,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=8,
            leftIndent=0
        )

        # 서브섹션 제목 (H2)
        self.subsection_title = ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading2'],
            fontName=self.korean_font_bold,
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=15,
            spaceAfter=10
        )

        # 본문
        self.body_text = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName=self.korean_font,
            fontSize=10,
            leading=16,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY
        )

        # 강조 텍스트
        self.emphasis_text = ParagraphStyle(
            'EmphasisText',
            parent=styles['Normal'],
            fontName=self.korean_font_bold,
            fontSize=11,
            textColor=colors.HexColor('#e74c3c'),
            spaceAfter=8
        )

    def generate_filename(self, ticker, name):
        """
        한글 회사명/코인명으로 파일명 생성

        예: 삼성전자_투자분석보고서_20251024.pdf
            비트코인_시장분석_20251024.pdf
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 이름 정제 (특수문자 제거)
        safe_name = name.replace('/', '_').replace('\\', '_').replace(':', '_')

        filename = f"{safe_name}_투자분석보고서_{timestamp}.pdf"
        return filename

    def generate_report(self, output_dir, analysis_data):
        """
        프리미엄 PDF 보고서 생성

        Args:
            output_dir: 저장 디렉토리
            analysis_data: 전체 분석 데이터
        """
        # 파일명 생성
        ticker = analysis_data.get('ticker', 'UNKNOWN')
        name = analysis_data.get('name', ticker)
        filename = self.generate_filename(ticker, name)
        output_path = os.path.join(output_dir, filename)

        # PDF 문서 생성
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )

        story = []

        # ==== 표지 ====
        story.extend(self._create_cover(analysis_data))

        # ==== 목차는 스킵 (자동 생성 복잡) ====

        # ==== 1. 경영진 요약 (Executive Summary) ====
        story.extend(self._create_executive_summary(analysis_data))

        # ==== 2. 주요 지표 개요 ====
        story.extend(self._create_key_metrics(analysis_data))

        # ==== 3. 기술적 분석 (Technical Analysis) ====
        story.extend(self._create_technical_analysis(analysis_data))

        # ==== 4. Phase 3 고급 분석 ====
        story.extend(self._create_phase3_analysis(analysis_data))

        # ==== 5. 뉴스 감성 분석 ====
        story.extend(self._create_sentiment_analysis(analysis_data))

        # ==== 6. 추천 트레이딩 전략 ====
        story.extend(self._create_trading_strategies(analysis_data))

        # ==== 7. 리스크 및 불확실성 ====
        story.extend(self._create_risk_section(analysis_data))

        # ==== 8. 면책 조항 ====
        story.extend(self._create_disclaimer())

        # PDF 생성
        doc.build(story)
        print(f"✅ 프리미엄 PDF 생성 완료: {output_path}")

        return output_path

    def _create_cover(self, data):
        """표지 페이지"""
        elements = []

        elements.append(Spacer(1, 3*cm))

        # 제목
        title = f"{data.get('name', 'N/A')}"
        elements.append(Paragraph(title, self.cover_title))

        # 부제
        subtitle = "투자 분석 보고서"
        elements.append(Paragraph(subtitle, self.cover_subtitle))

        elements.append(Spacer(1, 1*cm))

        # 기본 정보 박스
        info_data = [
            ['종목 코드', data.get('ticker', 'N/A')],
            ['분석 일시', datetime.now().strftime('%Y년 %m월 %d일 %H:%M')],
            ['현재가', f"{data.get('current_price', 0):,.2f} {data.get('currency', 'KRW')}"],
        ]

        info_table = Table(info_data, colWidths=[6*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 2*cm))

        # 면책 사항 미리보기
        disclaimer_preview = Paragraph(
            "본 보고서는 AI 기반 자동 분석 시스템으로 생성되었으며,<br/>"
            "투자 권유가 아닌 참고용 자료입니다.",
            self.body_text
        )
        elements.append(disclaimer_preview)

        elements.append(PageBreak())

        return elements

    def _create_executive_summary(self, data):
        """경영진 요약 (핵심만)"""
        elements = []

        elements.append(Paragraph("1. 경영진 요약 (Executive Summary)", self.section_title))

        confidence = data.get('confidence', {})
        signal = confidence.get('signal', 'neutral')
        score = confidence.get('score', 0)

        # 투자 의견 박스
        signal_names = {
            'strong_buy': '강력 매수 추천',
            'buy': '매수 추천',
            'neutral': '중립 (관망)',
            'sell': '매도 추천',
            'strong_sell': '강력 매도 추천'
        }

        signal_colors = {
            'strong_buy': colors.HexColor('#27ae60'),
            'buy': colors.HexColor('#2ecc71'),
            'neutral': colors.HexColor('#f39c12'),
            'sell': colors.HexColor('#e74c3c'),
            'strong_sell': colors.HexColor('#c0392b')
        }

        summary_data = [
            ['AI 투자 의견', signal_names.get(signal, 'N/A')],
            ['신뢰도', f"{score}%"],
            ['리스크 수준', confidence.get('risk', 'N/A')],
        ]

        summary_table = Table(summary_data, colWidths=[6*cm, 10*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('BACKGROUND', (1, 0), (1, 0), signal_colors.get(signal, colors.grey)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTSIZE', (1, 0), (1, 0), 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2c3e50')),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*cm))

        # 주요 근거 (TOP 3만)
        reasons = confidence.get('reasons', [])[:3]
        if reasons:
            elements.append(Paragraph("주요 근거 (TOP 3)", self.subsection_title))

            for i, r in enumerate(reasons, 1):
                reason_text = f"<b>{i}. {r.get('category', '')}:</b> {r.get('reason', '')} ({r.get('impact', '')})"
                elements.append(Paragraph(reason_text, self.body_text))
                elements.append(Spacer(1, 0.2*cm))

        elements.append(Spacer(1, 0.5*cm))
        return elements

    def _create_key_metrics(self, data):
        """주요 지표 개요"""
        elements = []

        elements.append(Paragraph("2. 주요 지표 개요", self.section_title))

        technical = data.get('technical', {})

        # 메트릭 테이블 (가독성 좋게)
        metrics_data = [
            ['지표', '현재 값', '상태'],
            ['RSI (14일)', f"{technical.get('rsi', 0):.1f}", self._rsi_status(technical.get('rsi', 50))],
            ['MACD', f"{technical.get('macd', {}).get('macd', 0):.4f}", self._macd_status(technical.get('macd', {}))],
        ]

        # 이동평균선
        ma = technical.get('ma', {})
        if ma:
            metrics_data.append(['MA 5일', f"{ma.get('ma5', 0):,.2f}", ''])
            metrics_data.append(['MA 20일', f"{ma.get('ma20', 0):,.2f}", ''])

        metrics_table = Table(metrics_data, colWidths=[5*cm, 5*cm, 6*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        elements.append(metrics_table)
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_technical_analysis(self, data):
        """기술적 분석 상세"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("3. 기술적 분석 (Technical Analysis)", self.section_title))

        technical = data.get('technical', {})

        # 3.1 RSI
        elements.append(Paragraph("3.1 RSI (Relative Strength Index)", self.subsection_title))
        rsi_text = f"현재 RSI: {technical.get('rsi', 0):.1f}<br/>" \
                   f"해석: {self._interpret_rsi(technical.get('rsi', 50))}"
        elements.append(Paragraph(rsi_text, self.body_text))
        elements.append(Spacer(1, 0.3*cm))

        # 3.2 MACD
        elements.append(Paragraph("3.2 MACD", self.subsection_title))
        macd_data = technical.get('macd', {})
        macd_text = f"MACD: {macd_data.get('macd', 0):.4f}<br/>" \
                    f"Signal: {macd_data.get('signal', 0):.4f}<br/>" \
                    f"Histogram: {macd_data.get('histogram', 0):.4f}<br/>" \
                    f"해석: {self._interpret_macd(macd_data)}"
        elements.append(Paragraph(macd_text, self.body_text))
        elements.append(Spacer(1, 0.3*cm))

        # 3.3 이동평균선
        elements.append(Paragraph("3.3 이동평균선 (Moving Average)", self.subsection_title))
        ma = technical.get('ma', {})
        if ma:
            ma_text = f"MA 5일: {ma.get('ma5', 0):,.2f}<br/>" \
                      f"MA 20일: {ma.get('ma20', 0):,.2f}<br/>" \
                      f"MA 60일: {ma.get('ma60', 0):,.2f}<br/>" \
                      f"MA 120일: {ma.get('ma120', 0):,.2f}"
            elements.append(Paragraph(ma_text, self.body_text))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_phase3_analysis(self, data):
        """Phase 3 고급 분석 (모든 펼치기 내용 포함)"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("4. 고급 패턴 분석 (Phase 3)", self.section_title))

        # 4.1 캔들스틱 패턴
        patterns = data.get('patterns', {})
        if patterns:
            elements.append(Paragraph("4.1 캔들스틱 패턴", self.subsection_title))

            candlestick = patterns.get('candlestick_patterns', [])
            if candlestick:
                for i, pattern in enumerate(candlestick[:5], 1):  # TOP 5
                    pattern_text = f"<b>{i}. {pattern.get('pattern_name', 'N/A')}</b><br/>" \
                                   f"신뢰도: {pattern.get('reliability', 0)}%<br/>" \
                                   f"신호: {pattern.get('signal', 'N/A')}<br/>" \
                                   f"설명: {pattern.get('explanation', 'N/A')}"
                    elements.append(Paragraph(pattern_text, self.body_text))
                    elements.append(Spacer(1, 0.3*cm))

        # 4.2 볼린저 밴드 & RSI 전략
        bb_rsi = data.get('bollinger_rsi', {})
        if bb_rsi:
            elements.append(Paragraph("4.2 볼린저 밴드 & RSI 전략", self.subsection_title))

            bb = bb_rsi.get('bollinger_bands', {})
            bb_text = f"상단: {bb.get('upper', 0):,.2f}<br/>" \
                      f"중단: {bb.get('middle', 0):,.2f}<br/>" \
                      f"하단: {bb.get('lower', 0):,.2f}<br/>" \
                      f"%B: {bb.get('percent_b', 0):.2f}<br/>" \
                      f"밴드폭: {bb.get('bandwidth', 0):.2f}%"
            elements.append(Paragraph(bb_text, self.body_text))
            elements.append(Spacer(1, 0.3*cm))

        # 4.3 이동평균선 크로스
        ma_cross = data.get('ma_cross', {})
        if ma_cross:
            elements.append(Paragraph("4.3 이동평균선 크로스 전략", self.subsection_title))

            crosses = ma_cross.get('crosses', [])
            if crosses:
                for i, cross in enumerate(crosses[:3], 1):
                    cross_text = f"<b>{i}. {cross.get('pair', '')} 크로스</b><br/>" \
                                 f"타입: {cross.get('type', '')}<br/>" \
                                 f"날짜: {cross.get('date', 'N/A')}<br/>" \
                                 f"가격: {cross.get('price', 0):,.2f}"
                    elements.append(Paragraph(cross_text, self.body_text))
                    elements.append(Spacer(1, 0.3*cm))

        # 4.4 거래량 분석
        volume = data.get('volume', {})
        if volume:
            elements.append(Paragraph("4.4 거래량 분석", self.subsection_title))

            surge = volume.get('surge_analysis', {})
            vol_text = f"현재 거래량: {volume.get('current_volume', 0):,.0f}<br/>" \
                       f"20일 평균: {volume.get('avg_volume_20', 0):,.0f}<br/>" \
                       f"비율: {volume.get('volume_ratio', 0):.1f}배<br/>" \
                       f"상태: {surge.get('type', 'N/A')}"
            elements.append(Paragraph(vol_text, self.body_text))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_sentiment_analysis(self, data):
        """뉴스 감성 분석"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("5. 뉴스 감성 분석", self.section_title))

        sentiment = data.get('sentiment', {})
        if sentiment:
            sentiment_data = [
                ['전체 감성', self._sentiment_name(sentiment.get('overall_sentiment', 'neutral'))],
                ['감성 점수', f"{sentiment.get('overall_score', 0)*100:.1f}점"],
                ['긍정 뉴스', f"{sentiment.get('positive_count', 0)}개"],
                ['부정 뉴스', f"{sentiment.get('negative_count', 0)}개"],
            ]

            sentiment_table = Table(sentiment_data, colWidths=[6*cm, 10*cm])
            sentiment_table.setStyle(self._get_simple_table_style())

            elements.append(sentiment_table)
            elements.append(Spacer(1, 0.5*cm))

            # 뉴스 목록 (전체, 표 깨짐 방지)
            news_list = data.get('news', [])
            if news_list:
                elements.append(Paragraph("5.1 뉴스 상세 내역", self.subsection_title))

                for i, news in enumerate(news_list[:10], 1):  # TOP 10
                    news_text = f"<b>{i}. {news.get('제목', 'N/A')}</b><br/>" \
                                f"언론사: {news.get('언론사', 'N/A')} | " \
                                f"날짜: {news.get('날짜', 'N/A')} | " \
                                f"감성: {self._sentiment_name(news.get('sentiment', 'neutral'))}"
                    elements.append(Paragraph(news_text, self.body_text))
                    elements.append(Spacer(1, 0.3*cm))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_trading_strategies(self, data):
        """추천 트레이딩 전략"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("6. 추천 트레이딩 전략", self.section_title))

        # Phase 3에서 전략 추천 가져오기
        bb_rsi = data.get('bollinger_rsi', {})
        strategies = bb_rsi.get('strategy_suggestions', [])

        if strategies:
            for i, strategy in enumerate(strategies[:3], 1):  # TOP 3
                strategy_box = [
                    [f"전략 {i}: {strategy.get('strategy', 'N/A')}"],
                    [f"신뢰도: {strategy.get('confidence', 0)}%"],
                    [f"이유: {strategy.get('reason', 'N/A')}"],
                    [f"진입 시그널: {strategy.get('entry_signal', 'N/A')}"],
                    [f"목표가: {strategy.get('target', 'N/A')}"],
                    [f"손절가: {strategy.get('stop_loss', 'N/A')}"],
                ]

                strategy_table = Table(strategy_box, colWidths=[16*cm])
                strategy_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2ecc71')),
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                    ('FONTNAME', (0, 0), (0, 0), self.korean_font_bold),
                    ('FONTSIZE', (0, 0), (0, 0), 12),
                    ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#27ae60')),
                ]))

                elements.append(strategy_table)
                elements.append(Spacer(1, 0.5*cm))
        else:
            elements.append(Paragraph("현재 추천할 만한 트레이딩 전략이 없습니다.", self.body_text))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_risk_section(self, data):
        """리스크 및 불확실성"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("7. 리스크 및 불확실성 요인", self.section_title))

        confidence = data.get('confidence', {})
        uncertainties = confidence.get('uncertainties', [])

        if uncertainties:
            for i, u in enumerate(uncertainties, 1):
                risk_text = f"<b>{i}. {u.get('factor', 'N/A')}</b><br/>" \
                            f"{u.get('description', 'N/A')}"
                elements.append(Paragraph(risk_text, self.body_text))
                elements.append(Spacer(1, 0.3*cm))
        else:
            elements.append(Paragraph("특별한 불확실성 요인이 발견되지 않았습니다.", self.body_text))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_disclaimer(self):
        """면책 조항"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("면책 조항", self.section_title))

        disclaimer_text = """
        본 보고서는 AI 기반 자동 분석 시스템으로 생성되었으며, 투자 권유가 아닌 참고용 자료입니다.<br/>
        <br/>
        <b>주의 사항:</b><br/>
        • 신뢰도 및 투자 신호는 참고용이며, 실제 투자 판단은 본인 책임입니다.<br/>
        • 시장 예측이 불가능한 다양한 변수(규제, 지정학적 리스크 등)가 존재합니다.<br/>
        • 손실 가능성이 항상 존재하며, 투자 전 전문가 상담을 권장합니다.<br/>
        • 분산 투자 및 손절매 설정을 필수로 하세요.<br/>
        <br/>
        생성 시스템: AI 시장 분석 시스템 v3.0 (Premium)<br/>
        생성 일시: {datetime}<br/>
        """.format(datetime=datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분'))

        elements.append(Paragraph(disclaimer_text, self.body_text))

        return elements

    # ==== 헬퍼 함수들 ====

    def _get_simple_table_style(self):
        """간단한 테이블 스타일"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])

    def _rsi_status(self, rsi):
        """RSI 상태"""
        if rsi < 30:
            return "과매도"
        elif rsi < 70:
            return "정상"
        else:
            return "과매수"

    def _macd_status(self, macd_data):
        """MACD 상태"""
        macd = macd_data.get('macd', 0)
        signal = macd_data.get('signal', 0)

        if macd > signal:
            return "상승 신호"
        elif macd < signal:
            return "하락 신호"
        else:
            return "중립"

    def _interpret_rsi(self, rsi):
        """RSI 해석"""
        if rsi < 30:
            return "과매도 구간 - 매수 기회 고려"
        elif rsi < 40:
            return "약세 구간"
        elif rsi < 60:
            return "중립 구간 - 정상 범위"
        elif rsi < 70:
            return "강세 구간"
        else:
            return "과매수 구간 - 매도 고려"

    def _interpret_macd(self, macd_data):
        """MACD 해석"""
        macd = macd_data.get('macd', 0)
        signal = macd_data.get('signal', 0)

        if macd > signal:
            return "골든크로스 - 상승 신호"
        elif macd < signal:
            return "데드크로스 - 하락 신호"
        else:
            return "중립"

    def _sentiment_name(self, sentiment):
        """감성 이름 변환"""
        names = {
            'positive': '긍정',
            'negative': '부정',
            'neutral': '중립'
        }
        return names.get(sentiment, '중립')


if __name__ == "__main__":
    # 테스트
    generator = PremiumPDFGenerator()

    test_data = {
        'ticker': 'orderly-network',
        'name': '오덜리',
        'current_price': 0.32,
        'currency': 'USD',
        'confidence': {
            'score': 65,
            'signal': 'buy',
            'risk': '중간',
            'reasons': [
                {'category': '기술적 지표', 'reason': 'RSI 과매도', 'impact': '+15%'},
            ],
            'uncertainties': [
                {'factor': '시장 변동성', 'description': '암호화폐 시장의 높은 변동성'},
            ]
        },
        'technical': {
            'rsi': 35.2,
            'macd': {'macd': 0.02, 'signal': 0.01, 'histogram': 0.01},
        },
        'sentiment': {
            'overall_sentiment': 'positive',
            'overall_score': 0.68,
            'positive_count': 8,
            'negative_count': 2,
        },
        'news': [
            {'제목': '오덜리 네트워크 메인넷 출시', '언론사': 'CoinDesk', '날짜': '2025-10-24', 'sentiment': 'positive'},
        ]
    }

    output_dir = "C:\\Users\\기광우\\OneDrive\\Desktop\\기광우 업무\\AI\\시장분석시스템\\reports"
    generator.generate_report(output_dir, test_data)
    print("✅ 테스트 완료")
