# -*- coding: utf-8 -*-
"""
시장 분석 시스템 - 웹 대시보드
Flask 기반 웹 애플리케이션
"""
import sys
import io
import os

# Windows 한글/이모지 출력 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify, send_file
import json
from datetime import datetime
import threading

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 유틸리티 임포트 (근본 문제 해결 시스템)
from utils.data_normalizer import normalize_dataframe, validate_dataframe
from utils.logger import log_error, log_warning, log_info, log_dataframe_error

from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from collectors.commodity_collector import CommodityCollector
from collectors.naver_news_collector import NaverNewsCollector
from collectors.google_news_collector import GoogleNewsCollector
from collectors.krx_stock_list import get_krx_list
from collectors.multi_source_collector import MultiSourceCollector
from collectors.economic_event_collector import EconomicEventCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator
from analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
from analyzers.pattern_analyzer import PatternAnalyzer  # Phase 3-1: 패턴 분석기 추가
from analyzers.bollinger_rsi_analyzer import BollingerRSIAnalyzer  # Phase 3-2: 볼린저 밴드 & RSI 분석기 추가
from analyzers.ma_cross_analyzer import MovingAverageCrossAnalyzer  # Phase 3-3: 이동평균선 크로스 분석기 추가
from analyzers.volume_analyzer import VolumeAnalyzer  # Phase 3-4: 거래량 분석기 추가
from reports.report_generator import ReportGenerator
from reports.pdf_generator import PDFReportGenerator
from reports.premium_pdf_generator import PremiumPDFGenerator  # Phase 3: 프리미엄 PDF 추가
from reports.share_generator import ShareTextGenerator  # Phase 3: 공유하기 기능 추가
from auto_recommender import AutoRecommender

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# 전역 변수
stock_collector = StockCollector()
multi_collector = MultiSourceCollector()  # 다중 소스 수집기 추가
crypto_collector = CryptoCollector()
commodity_collector = CommodityCollector()  # 원자재 수집기 추가
news_collector = NaverNewsCollector()
google_news_collector = GoogleNewsCollector()  # Phase 2-2: Google News 추가
sentiment_analyzer = SentimentAnalyzer()
krx_list = get_krx_list()  # 전체 KRX 종목 리스트
pdf_generator = PDFReportGenerator()  # PDF 생성기
premium_pdf_generator = PremiumPDFGenerator()  # 프리미엄 PDF 생성기 (Phase 3)
share_text_generator = ShareTextGenerator()  # 공유 텍스트 생성기 (Phase 3)
hot_stock_recommender = AutoRecommender()  # 핫 종목 추천 엔진
event_collector = EconomicEventCollector()  # 경제 이벤트 수집기 (Phase 2-3)

# 24시간 모니터링 상태
monitoring_active = False
monitoring_thread = None
monitored_tickers = []


@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """종목 분석 API"""
    try:
        data = request.json
        ticker = data.get('ticker', '').strip()
        asset_type = data.get('type', 'stock')  # stock or crypto
        period = data.get('period', '3mo')

        if not ticker:
            return jsonify({'error': '종목 코드를 입력하세요'}), 400

        # 데이터 수집
        if asset_type == 'crypto':
            # 한글 암호화폐 이름 매핑
            crypto_kr_mapping = {
                '비트코인': 'bitcoin',
                '이더리움': 'ethereum',
                '이더': 'ethereum',
                '리플': 'ripple',
                '에이다': 'cardano',
                '카르다노': 'cardano',
                '솔라나': 'solana',
                '오덜리': 'orderly-network',
                '오더리': 'orderly-network',
                'orderly': 'orderly-network',
                'order': 'orderly-network',
                '바이낸스': 'binancecoin',
                '도지': 'dogecoin',
                '도지코인': 'dogecoin',
                '폴카닷': 'polkadot',
                '체인링크': 'chainlink',
                '아발란체': 'avalanche-2',
            }

            # 한글 입력 시 자동 변환
            ticker_lower = ticker.lower()
            if ticker in crypto_kr_mapping:
                ticker = crypto_kr_mapping[ticker]
                print(f"🔄 한글 코인명 변환: {data.get('ticker')} → {ticker}")
            elif ticker_lower in crypto_kr_mapping:
                ticker = crypto_kr_mapping[ticker_lower]
                print(f"🔄 한글 코인명 변환: {data.get('ticker')} → {ticker}")

            price_data = crypto_collector.get_crypto_data(ticker, days=90)
            coin_info = crypto_collector.get_coin_info(ticker)
            name = coin_info.get('코인명', ticker) if coin_info else ticker
            error_msg = None
        else:
            # 한국 주식 확인
            is_korean = ticker.endswith('.KS') or ticker.endswith('.KQ') or (ticker.replace('.', '').isdigit() and len(ticker.replace('.', '')) == 6)

            if is_korean:
                # 한국 주식 - 기존 방식
                price_data = stock_collector.get_stock_data(ticker, period=period)
                company_info = stock_collector.get_company_info(ticker)
                name = company_info.get('종목명', ticker) if company_info else ticker
                error_msg = None
            else:
                # 미국 주식 - 다중 소스 전략 사용
                price_data, error_msg = multi_collector.get_stock_data(ticker, period=period)

                # 기업 정보는 기존 방식 시도
                try:
                    company_info = stock_collector.get_company_info(ticker)
                    name = company_info.get('종목명', ticker) if company_info else ticker
                except:
                    name = ticker

        # 에러 처리
        if price_data is None or (hasattr(price_data, 'empty') and price_data.empty):
            log_error(f"데이터 수집 실패: {ticker} ({asset_type})")
            if error_msg:
                log_dataframe_error(price_data, f"Empty data for {ticker}")
            if error_msg:
                return jsonify({'error': error_msg}), 404
            else:
                return jsonify({'error': '데이터를 가져올 수 없습니다.\n\n종목코드를 확인하세요:\n- 미국 주식: AAPL, MSFT, INTC\n- 한국 주식: 005930.KS, 035720.KQ'}), 404

        # ✨ 컬럼명 자동 정규화 (통합 시스템)
        log_info(f"데이터 정규화 시작: {ticker}")
        price_data = normalize_dataframe(price_data)

        # 검증
        is_valid, missing = validate_dataframe(price_data)
        if not is_valid:
            log_warning(f"데이터 검증 실패: {ticker}, 누락 컬럼: {missing}")
            return jsonify({'error': f'데이터 형식 오류: 누락된 컬럼 {missing}'}), 500

        # 기술적 분석
        tech_analyzer = TechnicalAnalyzer(price_data)
        technical_result = tech_analyzer.analyze_all()

        # Phase 3-1: 고급 패턴 분석
        pattern_analyzer = PatternAnalyzer()
        pattern_result = pattern_analyzer.analyze_patterns(price_data)

        # Phase 3-2: 볼린저 밴드 & RSI 전략 분석
        bb_rsi_analyzer = BollingerRSIAnalyzer()
        bb_rsi_result = bb_rsi_analyzer.analyze(price_data)

        # Phase 3-3: 이동평균선 크로스 전략 분석
        ma_cross_analyzer = MovingAverageCrossAnalyzer()
        ma_cross_result = ma_cross_analyzer.analyze(price_data)

        # Phase 3-4: 거래량 분석
        volume_analyzer = VolumeAnalyzer()
        volume_result = volume_analyzer.analyze(price_data)

        # 뉴스 수집 및 감성 분석 (Phase 2-2: 다중 소스)
        naver_news = news_collector.get_news(name, max_count=10)
        google_news = google_news_collector.get_news(name, max_count=10, language='ko')
        news_list = naver_news + google_news  # 통합
        sentiment_result = sentiment_analyzer.analyze_news_list(news_list)

        # 신뢰도 계산
        calculator = ConfidenceCalculator()
        confidence = calculator.calculate_confidence(technical_result, sentiment_result)

        # 종합 의견 생성
        comprehensive_analyzer = ComprehensiveAnalyzer()
        comprehensive_data = {
            'name': name,
            'technical': technical_result,
            'sentiment': sentiment_result,
            'confidence': confidence
        }
        comprehensive_result = comprehensive_analyzer.generate_opinion(comprehensive_data)

        # 현재가 (컬럼명 표준화 후에는 항상 영문)
        if 'Close' in price_data.columns:
            current_price = price_data['Close'].iloc[-1]
            close_col = 'Close'
            volume_col = 'Volume'
        else:
            # fallback: 만약 표준화가 실패한 경우
            current_price = price_data.iloc[-1, 3]  # 4번째 컬럼 (보통 종가)
            close_col = price_data.columns[3]
            volume_col = price_data.columns[4] if len(price_data.columns) > 4 else price_data.columns[3]

        # 환율 정보 추가 (외국 주식 및 가상화폐인 경우)
        exchange_rate = None
        price_krw = None
        currency = 'KRW'

        if asset_type == 'crypto' or (not is_korean and asset_type == 'stock'):
            try:
                import yfinance as yf
                # USD/KRW 환율 가져오기
                usd_krw = yf.Ticker('KRW=X')
                rate_data = usd_krw.history(period='1d')
                if not rate_data.empty:
                    exchange_rate = float(rate_data['Close'].iloc[-1])
                    price_krw = float(current_price) * exchange_rate
                    currency = 'USD'
            except Exception as e:
                print(f"⚠️ 환율 조회 실패: {e}")
                # 환율 조회 실패 시 고정 환율 사용
                exchange_rate = 1330.0
                price_krw = float(current_price) * exchange_rate
                currency = 'USD'

        # 결과 반환
        result = {
            'ticker': ticker,
            'name': name,
            'current_price': float(current_price),
            'currency': currency,
            'exchange_rate': exchange_rate,
            'price_krw': price_krw,
            'confidence': confidence,
            'technical': {
                'rsi': technical_result.get('rsi'),
                'macd': technical_result.get('macd'),
                'trend': technical_result.get('trend'),
                'signals': technical_result.get('signals', [])
            },
            'sentiment': sentiment_result,
            'patterns': pattern_result,  # Phase 3-1: 패턴 분석 결과 추가
            'bollinger_rsi': bb_rsi_result,  # Phase 3-2: 볼린저 밴드 & RSI 분석 결과 추가
            'ma_cross': ma_cross_result,  # Phase 3-3: 이동평균선 크로스 분석 결과 추가
            'volume': volume_result,  # Phase 3-4: 거래량 분석 결과 추가
            'comprehensive_opinion': comprehensive_result.get('comprehensive_opinion'),
            'news': news_list[:10],  # 상위 10개 뉴스만
            'chart_data': {
                'dates': price_data.index.strftime('%Y-%m-%d').tolist(),
                'prices': price_data[close_col].tolist(),
                'volumes': price_data[volume_col].tolist()
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare():
    """여러 종목 비교 분석"""
    try:
        data = request.json
        tickers = data.get('tickers', [])

        if not tickers or len(tickers) < 2:
            return jsonify({'error': '최소 2개 이상의 종목을 입력하세요'}), 400

        results = []

        for ticker in tickers[:10]:  # 최대 10개
            try:
                price_data = stock_collector.get_stock_data(ticker, period='3mo')
                if price_data is None:
                    continue

                tech_analyzer = TechnicalAnalyzer(price_data)
                technical_result = tech_analyzer.analyze_all()

                news_list = news_collector.get_news(ticker, max_count=10)
                sentiment_result = sentiment_analyzer.analyze_news_list(news_list)

                calculator = ConfidenceCalculator()
                confidence = calculator.calculate_confidence(technical_result, sentiment_result)

                # 컬럼명 호환성 처리
                if '종가' in price_data.columns:
                    current_price = float(price_data['종가'].iloc[-1])
                elif 'Close' in price_data.columns:
                    current_price = float(price_data['Close'].iloc[-1])
                else:
                    current_price = float(price_data.iloc[-1, 3])

                results.append({
                    'ticker': ticker,
                    'current_price': current_price,
                    'confidence_score': confidence['score'],
                    'signal': confidence['signal'],
                    'rsi': technical_result.get('rsi'),
                    'sentiment': sentiment_result.get('overall_sentiment')
                })

            except Exception as e:
                print(f"⚠️ {ticker} 분석 실패: {str(e)}")
                continue

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio', methods=['GET', 'POST'])
def portfolio():
    """포트폴리오 관리"""
    portfolio_file = os.path.join(os.path.dirname(__file__), '../data/portfolio.json')

    if request.method == 'GET':
        # 포트폴리오 조회
        try:
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    portfolio_data = json.load(f)
            else:
                portfolio_data = {'stocks': []}

            # 현재가 업데이트
            for stock in portfolio_data['stocks']:
                try:
                    price_data = stock_collector.get_stock_data(stock['ticker'], period='1d')
                    if price_data is not None:
                        current_price = float(price_data['종가'].iloc[-1])
                        stock['current_price'] = current_price
                        stock['profit'] = (current_price - stock['avg_price']) * stock['quantity']
                        stock['return'] = ((current_price / stock['avg_price']) - 1) * 100
                except:
                    pass

            # 총 평가액 및 수익률 계산
            total_value = sum([s.get('current_price', 0) * s['quantity'] for s in portfolio_data['stocks']])
            total_cost = sum([s['avg_price'] * s['quantity'] for s in portfolio_data['stocks']])
            total_return = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0

            portfolio_data['total_value'] = total_value
            portfolio_data['total_cost'] = total_cost
            portfolio_data['total_return'] = total_return

            return jsonify(portfolio_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        # 포트폴리오에 종목 추가
        try:
            data = request.json

            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    portfolio_data = json.load(f)
            else:
                portfolio_data = {'stocks': []}

            portfolio_data['stocks'].append({
                'ticker': data['ticker'],
                'name': data['name'],
                'quantity': data['quantity'],
                'avg_price': data['avg_price'],
                'buy_date': data.get('buy_date', datetime.now().strftime('%Y-%m-%d'))
            })

            # 파일 저장
            os.makedirs(os.path.dirname(portfolio_file), exist_ok=True)
            with open(portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, ensure_ascii=False, indent=2)

            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """24시간 모니터링 시작"""
    global monitoring_active, monitoring_thread, monitored_tickers

    data = request.json
    monitored_tickers = data.get('tickers', [])

    if monitoring_active:
        return jsonify({'error': '이미 모니터링이 실행 중입니다'}), 400

    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()

    return jsonify({'success': True, 'message': f'{len(monitored_tickers)}개 종목 모니터링 시작'})


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    global monitoring_active

    monitoring_active = False
    return jsonify({'success': True, 'message': '모니터링 중지'})


@app.route('/api/monitoring/status', methods=['GET'])
def monitoring_status():
    """모니터링 상태 조회"""
    return jsonify({
        'active': monitoring_active,
        'tickers': monitored_tickers
    })


@app.route('/api/search', methods=['GET'])
def search_ticker():
    """종목 검색 API - 전체 상장 종목 지원"""
    try:
        query = request.args.get('q', '').strip()
        asset_type = request.args.get('type', 'stock')  # stock or crypto

        if not query or len(query) < 1:
            return jsonify({'results': []})

        results = []

        if asset_type == 'stock':
            # KRX 전체 종목 검색
            krx_results = krx_list.search_stocks(query, limit=15)

            for stock in krx_results:
                results.append({
                    'ticker': stock['ticker'],
                    'name': stock['name'],
                    'market': stock['market'],
                    'display': f"{stock['name']} ({stock['ticker']}) - {stock['market']}"
                })

            # 미국 주요 종목도 추가 검색 (한글명 포함)
            us_stocks = [
                {'code': 'AAPL', 'name': 'Apple', 'name_kr': '애플', 'market': 'NASDAQ'},
                {'code': 'MSFT', 'name': 'Microsoft', 'name_kr': '마이크로소프트', 'market': 'NASDAQ'},
                {'code': 'GOOGL', 'name': 'Google', 'name_kr': '구글', 'market': 'NASDAQ'},
                {'code': 'AMZN', 'name': 'Amazon', 'name_kr': '아마존', 'market': 'NASDAQ'},
                {'code': 'TSLA', 'name': 'Tesla', 'name_kr': '테슬라', 'market': 'NASDAQ'},
                {'code': 'META', 'name': 'Meta', 'name_kr': '메타', 'market': 'NASDAQ'},
                {'code': 'NVDA', 'name': 'NVIDIA', 'name_kr': '엔비디아', 'market': 'NASDAQ'},
                {'code': 'INTC', 'name': 'Intel', 'name_kr': '인텔', 'market': 'NASDAQ'},
                {'code': 'AMD', 'name': 'AMD', 'name_kr': 'AMD', 'market': 'NASDAQ'},
                {'code': 'NFLX', 'name': 'Netflix', 'name_kr': '넷플릭스', 'market': 'NASDAQ'},
                {'code': 'JPM', 'name': 'JPMorgan Chase', 'name_kr': 'JP모건', 'market': 'NYSE'},
                {'code': 'V', 'name': 'Visa', 'name_kr': '비자', 'market': 'NYSE'},
                {'code': 'WMT', 'name': 'Walmart', 'name_kr': '월마트', 'market': 'NYSE'},
                {'code': 'DIS', 'name': 'Disney', 'name_kr': '디즈니', 'market': 'NYSE'},
                {'code': 'BA', 'name': 'Boeing', 'name_kr': '보잉', 'market': 'NYSE'},
                {'code': 'BABA', 'name': 'Alibaba', 'name_kr': '알리바바', 'market': 'NYSE'},
                {'code': 'NKE', 'name': 'Nike', 'name_kr': '나이키', 'market': 'NYSE'},
                {'code': 'PYPL', 'name': 'PayPal', 'name_kr': '페이팔', 'market': 'NASDAQ'},
                {'code': 'ADBE', 'name': 'Adobe', 'name_kr': '어도비', 'market': 'NASDAQ'},
                {'code': 'CRM', 'name': 'Salesforce', 'name_kr': '세일즈포스', 'market': 'NYSE'},
            ]

            query_lower = query.lower()
            for stock in us_stocks:
                # 영문 대소문자 무시 검색 + 한글 검색
                if (query_lower in stock['code'].lower() or
                    query_lower in stock['name'].lower() or
                    query_lower in stock.get('name_kr', '').lower() or  # 한글도 소문자 변환
                    query in stock.get('name_kr', '')):  # 원본 한글 검색도 유지
                    results.append({
                        'ticker': stock['code'],
                        'name': stock['name'],
                        'market': stock['market'],
                        'display': f"{stock['name']} ({stock['code']}) - {stock['market']}"
                    })

        elif asset_type == 'crypto':
            # 주요 가상화폐 리스트 (한글명 포함)
            cryptos = [
                {'id': 'bitcoin', 'name': 'Bitcoin', 'name_kr': '비트코인', 'symbol': 'BTC'},
                {'id': 'ethereum', 'name': 'Ethereum', 'name_kr': '이더리움', 'symbol': 'ETH'},
                {'id': 'binancecoin', 'name': 'Binance Coin', 'name_kr': '바이낸스', 'symbol': 'BNB'},
                {'id': 'ripple', 'name': 'XRP', 'name_kr': '리플', 'symbol': 'XRP'},
                {'id': 'cardano', 'name': 'Cardano', 'name_kr': '카르다노', 'symbol': 'ADA'},
                {'id': 'solana', 'name': 'Solana', 'name_kr': '솔라나', 'symbol': 'SOL'},
                {'id': 'polkadot', 'name': 'Polkadot', 'name_kr': '폴카닷', 'symbol': 'DOT'},
                {'id': 'dogecoin', 'name': 'Dogecoin', 'name_kr': '도지코인', 'symbol': 'DOGE'},
                {'id': 'avalanche-2', 'name': 'Avalanche', 'name_kr': '아발란체', 'symbol': 'AVAX'},
                {'id': 'chainlink', 'name': 'Chainlink', 'name_kr': '체인링크', 'symbol': 'LINK'},
                {'id': 'orderly-network', 'name': 'Orderly', 'name_kr': '오덜리', 'symbol': 'ORDER'},
            ]

            query_lower = query.lower()
            for crypto in cryptos:
                # 영문 + 한글 검색 지원
                if (query_lower in crypto['id'].lower() or
                    query_lower in crypto['name'].lower() or
                    query_lower in crypto['symbol'].lower() or
                    query_lower in crypto.get('name_kr', '').lower() or
                    query in crypto.get('name_kr', '')):
                    results.append({
                        'ticker': crypto['id'],
                        'name': crypto['name'],
                        'symbol': crypto['symbol'],
                        'display': f"{crypto['name']} ({crypto['symbol']}) - {crypto.get('name_kr', '')}"
                    })

        return jsonify({'results': results[:10]})  # 최대 10개

    except Exception as e:
        return jsonify({'error': str(e), 'results': []})


@app.route('/api/download/pdf', methods=['POST'])
def download_pdf():
    """분석 보고서 PDF 다운로드"""
    try:
        data = request.json

        # PDF 파일 생성
        reports_dir = os.path.join(os.path.dirname(__file__), '../reports')
        os.makedirs(reports_dir, exist_ok=True)

        ticker = data.get('ticker', 'unknown')
        filename = f"report_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)

        # PDF 생성
        pdf_generator.generate_report(filepath, data)

        # 파일 다운로드
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/premium-pdf', methods=['POST'])
def download_premium_pdf():
    """프리미엄 PDF 다운로드 (Phase 3 - 모든 분석 포함)"""
    try:
        data = request.json

        # PDF 저장 디렉토리
        reports_dir = os.path.join(os.path.dirname(__file__), '../reports')
        os.makedirs(reports_dir, exist_ok=True)

        # 프리미엄 PDF 생성 (한글 파일명 자동 생성)
        log_info(f"프리미엄 PDF 생성 시작: {data.get('name', 'unknown')}")
        output_path = premium_pdf_generator.generate_report(reports_dir, data)

        # 파일명 추출
        filename = os.path.basename(output_path)
        log_info(f"프리미엄 PDF 생성 완료: {filename}")

        # 파일 다운로드
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        log_error(f"프리미엄 PDF 생성 실패", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/share', methods=['POST'])
def generate_share():
    """공유하기 텍스트 생성 (70% 간소화)"""
    try:
        data = request.json

        # 공유 텍스트 생성
        log_info(f"공유 텍스트 생성 시작: {data.get('name', 'unknown')}")
        share_text = share_text_generator.generate_share_text(data)

        log_info(f"공유 텍스트 생성 완료")

        return jsonify({
            'success': True,
            'share_text': share_text
        })

    except Exception as e:
        log_error(f"공유 텍스트 생성 실패", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/commodities', methods=['GET'])
def get_commodities():
    """원자재 데이터 조회"""
    try:
        commodity_type = request.args.get('type', 'major')  # major or all
        period = request.args.get('period', '1mo')

        if commodity_type == 'all':
            data = commodity_collector.get_all_commodities(period=period)
        else:
            data = commodity_collector.get_major_commodities(period=period)

        # 비교 분석도 함께 반환
        comparison = commodity_collector.compare_commodities(period=period)

        return jsonify({
            'data': data,
            'comparison': comparison,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/commodities/<commodity_key>', methods=['GET'])
def get_commodity_detail(commodity_key):
    """특정 원자재 상세 정보"""
    try:
        period = request.args.get('period', '3mo')
        data = commodity_collector.get_commodity_data(commodity_key, period=period)

        if data is None:
            return jsonify({'error': '원자재 데이터를 가져올 수 없습니다'}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hot-stocks', methods=['GET'])
def get_hot_stocks():
    """핫 종목 목록 조회 (캐시 활용)"""
    try:
        # 캐시 파일 경로
        cache_dir = os.path.join(os.path.dirname(__file__), '../cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, 'hot_stocks.json')

        # 캐시 확인 (30분 유효)
        if os.path.exists(cache_file):
            import time
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < 1800:  # 30분 = 1800초
                print("📌 캐시 파일 사용 중")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    return jsonify(cached_data)

        print("📌 새로운 스캔 시작")
        # 캐시가 없거나 만료됨 - 새로 스캔
        recommendations = hot_stock_recommender.scan_korean_stocks()
        print(f"📌 스캔 완료: {len(recommendations)}개 종목")

        # JSON 직렬화 가능하도록 변환
        for rec in recommendations:
            print(f"📌 처리 중: {rec.get('name')}")
            # datetime 변환
            if 'scan_time' in rec:
                if hasattr(rec['scan_time'], 'isoformat'):
                    rec['scan_time'] = rec['scan_time'].isoformat()
                elif isinstance(rec['scan_time'], str):
                    pass  # 이미 문자열
                else:
                    rec['scan_time'] = str(rec['scan_time'])

            # float 변환 (Pandas/Numpy 타입 처리)
            for key in ['current_price', 'confidence', 'rsi', 'hot_score']:
                if key in rec and rec[key] is not None:
                    rec[key] = float(rec[key])

        print("📌 JSON 직렬화 준비 완료")
        result = {
            'recommendations': recommendations,
            'scan_time': datetime.now().isoformat(),
            'count': len(recommendations)
        }

        print("📌 캐시 파일 저장 중")
        # 캐시 저장
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("📌 응답 반환")
        return jsonify(result)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ 핫 종목 API 에러:")
        print(error_trace)
        return jsonify({'error': str(e), 'traceback': error_trace}), 500


@app.route('/api/hot-stocks/scan', methods=['POST'])
def scan_hot_stocks():
    """핫 종목 수동 스캔 (캐시 무시)"""
    try:
        recommendations = hot_stock_recommender.scan_korean_stocks()

        # JSON 직렬화 가능하도록 datetime 변환
        for rec in recommendations:
            if 'scan_time' in rec and hasattr(rec['scan_time'], 'isoformat'):
                rec['scan_time'] = rec['scan_time'].isoformat()

        result = {
            'recommendations': recommendations,
            'scan_time': datetime.now().isoformat(),
            'count': len(recommendations)
        }

        # 캐시 업데이트
        cache_dir = os.path.join(os.path.dirname(__file__), '../cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, 'hot_stocks.json')

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/economic-events', methods=['GET'])
def get_economic_events():
    """경제 이벤트 캘린더 조회 (Phase 2-3)"""
    try:
        days = int(request.args.get('days', 30))  # 기본 30일
        stock_ticker = request.args.get('ticker', None)  # 특정 종목 필터링 (선택)
        stock_name = request.args.get('name', None)

        # 전체 이벤트 조회
        all_events = event_collector.get_upcoming_events(days=days)

        # 종목별 필터링 (옵션)
        if stock_ticker and stock_name:
            filtered_events = event_collector.filter_events_by_stock(
                all_events, stock_name, stock_ticker
            )
            # 영향도 점수 추가
            for event in filtered_events:
                event['impact_score'] = event_collector.get_event_impact_score(event)

            result = {
                'events': filtered_events,
                'count': len(filtered_events),
                'stock_ticker': stock_ticker,
                'stock_name': stock_name,
                'period_days': days,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            # 전체 이벤트 반환
            for event in all_events:
                event['impact_score'] = event_collector.get_event_impact_score(event)

            # 중요도 순으로 정렬
            all_events.sort(key=lambda e: e['impact_score'], reverse=True)

            result = {
                'events': all_events,
                'count': len(all_events),
                'period_days': days,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        return jsonify(result)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ 경제 이벤트 API 에러:")
        print(error_trace)
        return jsonify({'error': str(e), 'traceback': error_trace}), 500


@app.route('/api/backtest/performance', methods=['GET'])
def get_backtest_performance():
    """백테스팅 성과 조회 (Phase 5)"""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from backtesting.performance_tracker import PerformanceTracker

        days = int(request.args.get('days', 30))
        tracker = PerformanceTracker()
        summary = tracker.get_performance_summary(days)

        return jsonify(summary)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ 백테스트 API 에러:")
        print(error_trace)
        return jsonify({'error': str(e), 'traceback': error_trace}), 500


def monitoring_loop():
    """백그라운드 모니터링 루프"""
    import time

    while monitoring_active:
        try:
            for ticker in monitored_tickers:
                # 분석 수행
                # (여기에 매수/매도 신호 체크 로직 추가)
                pass

            # 5분마다 체크
            time.sleep(300)

        except Exception as e:
            print(f"⚠️ 모니터링 오류: {str(e)}")
            time.sleep(60)


if __name__ == '__main__':
    print("="*60)
    print("🚀 시장 분석 시스템 웹 대시보드 시작")
    print("="*60)
    print("\n📊 웹 브라우저에서 접속하세요:")
    print("   http://localhost:5003")
    print("\n종료하려면 Ctrl+C를 누르세요\n")

    app.run(debug=True, host='0.0.0.0', port=5003)
