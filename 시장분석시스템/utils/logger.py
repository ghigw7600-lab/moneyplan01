# -*- coding: utf-8 -*-
"""
통합 로깅 시스템
모든 에러와 경고를 파일에 기록하여 디버깅 용이하게 함
"""

import logging
import os
from datetime import datetime
import traceback
import sys


class SystemLogger:
    """시스템 로거"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """로거 초기화"""
        # 로그 디렉토리 생성
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # 로그 파일 이름 (날짜별)
        log_file = os.path.join(log_dir, f'system_{datetime.now().strftime("%Y%m%d")}.log')

        # 로거 설정
        self._logger = logging.getLogger('MarketAnalyzer')
        self._logger.setLevel(logging.DEBUG)

        # 파일 핸들러 (모든 로그)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # 콘솔 핸들러 (경고 이상만)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        # 핸들러 추가
        if not self._logger.handlers:
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls):
        """로거 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance._logger

    @classmethod
    def log_error(cls, message, exception=None):
        """에러 로깅"""
        logger = cls.get_logger()
        logger.error(message)
        if exception:
            logger.error(f"Exception: {type(exception).__name__}: {str(exception)}")
            logger.error(traceback.format_exc())

    @classmethod
    def log_warning(cls, message):
        """경고 로깅"""
        logger = cls.get_logger()
        logger.warning(message)

    @classmethod
    def log_info(cls, message):
        """정보 로깅"""
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def log_debug(cls, message):
        """디버그 로깅"""
        logger = cls.get_logger()
        logger.debug(message)


# 편의 함수들
def log_error(message, exception=None):
    """에러 로깅 편의 함수"""
    SystemLogger.log_error(message, exception)


def log_warning(message):
    """경고 로깅 편의 함수"""
    SystemLogger.log_warning(message)


def log_info(message):
    """정보 로깅 편의 함수"""
    SystemLogger.log_info(message)


def log_debug(message):
    """디버그 로깅 편의 함수"""
    SystemLogger.log_debug(message)


def log_dataframe_error(df, context=""):
    """DataFrame 관련 에러 상세 로깅"""
    error_msg = f"DataFrame Error - {context}\n"

    if df is None:
        error_msg += "  - DataFrame is None\n"
    elif df.empty:
        error_msg += "  - DataFrame is empty\n"
    else:
        error_msg += f"  - Shape: {df.shape}\n"
        error_msg += f"  - Columns: {list(df.columns)}\n"
        error_msg += f"  - Index type: {type(df.index)}\n"
        error_msg += f"  - Dtypes:\n{df.dtypes}\n"

    log_error(error_msg)


if __name__ == "__main__":
    # 테스트
    log_info("시스템 시작")
    log_debug("디버그 메시지 (파일에만 기록됨)")
    log_warning("경고 메시지")

    try:
        1 / 0
    except Exception as e:
        log_error("테스트 에러", e)

    print("\n✅ 로그 테스트 완료. logs/ 디렉토리 확인")
