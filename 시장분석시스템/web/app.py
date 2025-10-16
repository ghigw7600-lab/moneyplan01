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

from collectors.stock_collector import StockCollector
from collectors.crypto_collector import CryptoCollector
from collectors.naver_news_collector import NaverNewsCollector
from collectors.krx_stock_list import get_krx_list
from collectors.multi_source_collector import MultiSourceCollector
from analyzers.technical_analyzer import TechnicalAnalyzer
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.confidence_calculator import ConfidenceCalculator
from analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
from reports.report_generator import ReportGenerator
from reports.pdf_generator import PDFReportGenerator

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# 전역 변수
stock_collector = StockCollector()
multi_collector = MultiSourceCollector()  # 다중 소스 수집기 추가
crypto_collector = CryptoCollector()
news_collector = NaverNewsCollector()
sentiment_analyzer = SentimentAnalyzer()
krx_list = get_krx_list()  # 전체 KRX 종목 리스트
pdf_generator = PDFReportGenerator()  # PDF 생성기

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
            price_data = crypto_collector.get_crypto_data(ticker, days=90)
            coin_info = crypto_collector.get_coin_info(ticker)
            name = coin_info.get('name', ticker)
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
            if error_msg:
                return jsonify({'error': error_msg}), 404
            else:
                return jsonify({'error': '데이터를 가져올 수 없습니다.\n\n종목코드를 확인하세요:\n- 미국 주식: AAPL, MSFT, INTC\n- 한국 주식: 005930.KS, 035720.KQ'}), 404

        # 기술적 분석
        tech_analyzer = TechnicalAnalyzer(price_data)
        technical_result = tech_analyzer.analyze_all()

        # 뉴스 수집 및 감성 분석
        news_list = news_collector.get_news(name, max_count=20)
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

        # 현재가 (컬럼명 호환성 처리)
        if '종가' in price_data.columns:
            current_price = price_data['종가'].iloc[-1]
            close_col = '종가'
            volume_col = '거래량'
        elif 'Close' in price_data.columns:
            current_price = price_data['Close'].iloc[-1]
            close_col = 'Close'
            volume_col = 'Volume'
        else:
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
            # 주요 가상화폐 리스트
            cryptos = [
                {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC'},
                {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'ETH'},
                {'id': 'binancecoin', 'name': 'Binance Coin', 'symbol': 'BNB'},
                {'id': 'ripple', 'name': 'XRP', 'symbol': 'XRP'},
                {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ADA'},
                {'id': 'solana', 'name': 'Solana', 'symbol': 'SOL'},
                {'id': 'polkadot', 'name': 'Polkadot', 'symbol': 'DOT'},
                {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'DOGE'},
                {'id': 'avalanche-2', 'name': 'Avalanche', 'symbol': 'AVAX'},
                {'id': 'chainlink', 'name': 'Chainlink', 'symbol': 'LINK'},
            ]

            query_lower = query.lower()
            for crypto in cryptos:
                if (query_lower in crypto['id'].lower() or
                    query_lower in crypto['name'].lower() or
                    query_lower in crypto['symbol'].lower()):
                    results.append({
                        'ticker': crypto['id'],
                        'name': crypto['name'],
                        'symbol': crypto['symbol'],
                        'display': f"{crypto['name']} ({crypto['symbol']}) - {crypto['id']}"
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
    print("   http://localhost:5001")
    print("\n종료하려면 Ctrl+C를 누르세요\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
