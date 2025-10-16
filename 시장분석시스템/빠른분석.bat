@echo off
chcp 65001 > nul

echo ============================================================
echo 빠른 종목 분석 (CMD 버전)
echo ============================================================
echo.

set /p ticker="종목 코드 입력 (예: 005930.KS): "

echo.
echo 분석 중...
echo.

REM SSL 인증서 검증 우회
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set PYTHONIOENCODING=utf-8

python -c "from collectors.stock_collector import StockCollector; from analyzers.technical_analyzer import TechnicalAnalyzer; from analyzers.sentiment_analyzer import SentimentAnalyzer; from analyzers.confidence_calculator import ConfidenceCalculator; import sys; ticker='%ticker%'; collector=StockCollector(); data=collector.get_stock_data(ticker); analyzer=TechnicalAnalyzer(data) if data is not None else None; tech=analyzer.analyze_all() if analyzer else None; sent=SentimentAnalyzer().analyze_news_list([]); conf=ConfidenceCalculator().calculate_confidence(tech,sent) if tech else None; print(f'\n신뢰도: {conf[\"score\"]}%%\n신호: {conf[\"signal\"]}\nRSI: {tech.get(\"rsi\"):.1f}') if conf else print('데이터 수집 실패')"

echo.
pause
