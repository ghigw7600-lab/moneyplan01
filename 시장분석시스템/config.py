# -*- coding: utf-8 -*-
"""
시장 분석 시스템 - 설정 파일
"""

# API 키 설정 (사용자가 직접 입력)
NEWS_API_KEY = ""  # https://newsapi.org 에서 무료 키 발급
TELEGRAM_BOT_TOKEN = ""  # @BotFather에서 발급 (선택사항)
TELEGRAM_CHAT_ID = ""  # 본인 chat_id (선택사항)

# 데이터 수집 설정
DEFAULT_PERIOD = "1y"  # 기본 데이터 수집 기간
DEFAULT_INTERVAL = "1d"  # 기본 간격 (1d=일봉)

# 기술적 지표 설정
MA_PERIODS = [20, 60, 120]  # 이동평균선 기간
RSI_PERIOD = 14  # RSI 기간
MACD_FAST = 12  # MACD 빠른선
MACD_SLOW = 26  # MACD 느린선
MACD_SIGNAL = 9  # MACD 시그널

# 신뢰도 계산 가중치
WEIGHTS = {
    "technical": 0.40,  # 기술적 지표 40%
    "sentiment": 0.30,  # 감성 분석 30%
    "volume": 0.20,     # 거래량 20%
    "support": 0.10     # 지지/저항 10%
}

# 신호 임계값
SIGNAL_THRESHOLDS = {
    "strong_buy": 75,   # 강력 매수
    "buy": 60,          # 매수
    "neutral": 40,      # 중립
    "sell": 60,         # 매도 (역방향)
    "strong_sell": 75   # 강력 매도 (역방향)
}

# 리스크 관리
RISK_REWARD_RATIO = 2.0  # 최소 1:2 비율
MAX_POSITION_SIZE = 0.15  # 계좌의 최대 15%
STOP_LOSS_PERCENT = 0.05  # 5% 손절

# 보고서 설정
REPORT_LANGUAGE = "ko"  # 한글
REPORT_FORMAT = "html"  # HTML 또는 PDF
CHART_STYLE = "dark"    # dark 또는 light

# 데이터 저장 경로
DATA_DIR = "data"
REPORTS_DIR = "reports"

# 뉴스 감성 분석 설정
NEWS_SOURCES = ["google-news-kr", "naver", "daum"]
NEWS_KEYWORDS = ["주식", "증시", "코스피", "나스닥", "비트코인"]
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"  # 기본 영문 모델
