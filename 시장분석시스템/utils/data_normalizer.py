# -*- coding: utf-8 -*-
"""
데이터 정규화 유틸리티
모든 데이터 소스의 컬럼명을 영문으로 통일
"""

import pandas as pd


class DataNormalizer:
    """데이터 컬럼명 표준화"""

    # 표준 컬럼명 매핑
    COLUMN_MAPPING = {
        # 한글 → 영문
        '시가': 'Open',
        '고가': 'High',
        '저가': 'Low',
        '종가': 'Close',
        '거래량': 'Volume',
        '날짜': 'Date',

        # 다양한 변형 처리
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'date': 'Date',

        # yfinance 스타일
        'Adj Close': 'Close',  # 조정 종가는 종가로 통일
    }

    @classmethod
    def normalize(cls, df):
        """
        DataFrame 컬럼명을 표준 영문명으로 변환

        Args:
            df (pd.DataFrame): 원본 데이터프레임

        Returns:
            pd.DataFrame: 정규화된 데이터프레임
        """
        if df is None or df.empty:
            return df

        # 복사본 생성
        normalized_df = df.copy()

        # 컬럼명 변환
        for old_col, new_col in cls.COLUMN_MAPPING.items():
            if old_col in normalized_df.columns:
                normalized_df.rename(columns={old_col: new_col}, inplace=True)

        # 필수 컬럼 검증
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in normalized_df.columns]

        if missing_columns:
            print(f"⚠️ 누락된 컬럼: {missing_columns}")
            # Close만 있으면 나머지를 Close로 채우기 (암호화폐 등)
            if 'Close' in normalized_df.columns:
                for col in ['Open', 'High', 'Low']:
                    if col not in normalized_df.columns:
                        normalized_df[col] = normalized_df['Close']
                if 'Volume' not in normalized_df.columns:
                    normalized_df['Volume'] = 0

        return normalized_df

    @classmethod
    def validate(cls, df):
        """
        데이터프레임이 표준 형식인지 검증

        Args:
            df (pd.DataFrame): 검증할 데이터프레임

        Returns:
            tuple: (is_valid, missing_columns)
        """
        if df is None or df.empty:
            return False, ['DataFrame is empty']

        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]

        return len(missing_columns) == 0, missing_columns

    @classmethod
    def info(cls, df):
        """데이터프레임 정보 출력 (디버깅용)"""
        if df is None:
            print("❌ DataFrame is None")
            return

        print(f"📊 DataFrame 정보:")
        print(f"   - 행 수: {len(df)}")
        print(f"   - 컬럼: {list(df.columns)}")
        print(f"   - 인덱스 타입: {type(df.index)}")
        print(f"   - 데이터 타입:\n{df.dtypes}")

        is_valid, missing = cls.validate(df)
        if is_valid:
            print("   ✅ 표준 형식 검증 통과")
        else:
            print(f"   ⚠️ 누락된 컬럼: {missing}")


# 편의 함수
def normalize_dataframe(df):
    """DataFrame을 표준 형식으로 변환하는 편의 함수"""
    return DataNormalizer.normalize(df)


def validate_dataframe(df):
    """DataFrame이 표준 형식인지 검증하는 편의 함수"""
    return DataNormalizer.validate(df)


if __name__ == "__main__":
    # 테스트
    import numpy as np

    # 한글 컬럼명 테스트 데이터
    test_data_kr = pd.DataFrame({
        '날짜': pd.date_range('2024-01-01', periods=5),
        '시가': [100, 102, 101, 103, 105],
        '고가': [105, 106, 104, 107, 108],
        '저가': [99, 101, 100, 102, 104],
        '종가': [103, 104, 102, 106, 107],
        '거래량': [1000, 1200, 1100, 1300, 1250]
    })

    print("=== 한글 컬럼명 테스트 ===")
    DataNormalizer.info(test_data_kr)

    normalized = DataNormalizer.normalize(test_data_kr)
    print("\n=== 정규화 후 ===")
    DataNormalizer.info(normalized)
    print(normalized.head())
