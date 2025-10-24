# -*- coding: utf-8 -*-
"""
AI 감성 분석 모듈
뉴스 제목/내용의 긍정/부정 감성 분석
"""

import re
from collections import Counter


class SentimentAnalyzer:
    """감성 분석기 (간단한 키워드 기반)"""

    def __init__(self):
        # 긍정 키워드 (대폭 확장 - 금융 용어)
        self.positive_keywords = [
            # 기존
            '상승', '급등', '호재', '성장', '증가', '개선', '확대', '돌파', '최고',
            '강세', '반등', '회복', '긍정', '수혜', '기대', '전망', '투자', '호황',
            '실적', '이익', '배당', '신고가', '플러스', '상향', '매수', '추천',
            # 추가 - 실적/재무
            '흑자', '영업이익', '순이익', '매출증가', '수익성', '이익률', '자산증가',
            '부채감소', '재무개선', '현금흐름', 'ROE', 'ROI', '마진확대',
            # 추가 - 시장/기술
            '혁신', '기술력', '특허', '신제품', '출시', '론칭', '계약', '수주',
            '파트너십', '제휴', 'MOU', '협력', '진출', '확장', '인수', '합병',
            # 추가 - 전망/분석
            '목표가상향', '레이팅상향', 'BUY', '강력매수', '적극매수', '비중확대',
            '컨센서스상회', '깜짝실적', '어닝서프라이즈', '가이던스상향',
            # 추가 - 트렌드
            '모멘텀', '돌풍', '주목', '각광', '인기', '관심', '유망', '유력',
            '선두', '1위', '점유율', '시장지배력', '경쟁우위',
            # 추가 - 외부 요인
            '정책지원', '규제완화', '보조금', '수출증가', '환율호재', '유가하락',
            '금리인하', '양적완화', '경기회복', '경기확장'
        ]

        # 부정 키워드 (대폭 확장 - 금융 용어)
        self.negative_keywords = [
            # 기존
            '하락', '급락', '악재', '감소', '하향', '악화', '위험', '우려', '부진',
            '약세', '폭락', '손실', '적자', '부정', '리스크', '하락세', '매도',
            '경고', '조정', '마이너스', '최저', '부담', '위기', '충격', '우울',
            # 추가 - 실적/재무
            '영업손실', '순손실', '매출감소', '수익성악화', '마진축소', '부채증가',
            '자산감소', '현금부족', '유동성위기', '재무악화', '적자전환',
            # 추가 - 시장/경영
            '리콜', '결함', '불량', '소송', '분쟁', '배상', '과징금', '제재',
            '규제강화', '인허가취소', '사업철수', '구조조정', '인력감축', '폐업',
            # 추가 - 전망/분석
            '목표가하향', '레이팅하향', 'SELL', '매도추천', '비중축소', '투자의견하향',
            '컨센서스하회', '어닝쇼크', '가이던스하향', '실망', '부진',
            # 추가 - 리스크
            '채무불이행', '디폴트', '파산', '회생절차', '청산', '부도', '연체',
            '신용등급하락', '투자경고', '감리', '횡령', '배임', '분식회계',
            # 추가 - 외부 요인
            '무역전쟁', '관세', '수출규제', '보복', '제재', '불확실성', '지정학',
            '경기침체', '경기후퇴', '금리인상', '긴축', '유가급등', '환율악화'
        ]

        # 중립 키워드
        self.neutral_keywords = [
            '보합', '횡보', '관망', '중립', '변동', '예상', '전망', '분석', '평가',
            '발표', '공시', '보고', '설명', '회의', '결정', '유지', '동결'
        ]

    def analyze_text(self, text):
        """
        텍스트 감성 분석

        Args:
            text (str): 분석할 텍스트

        Returns:
            dict: 감성 점수 및 분류
        """
        if not text:
            return {
                'score': 0.5,
                'sentiment': 'neutral',
                'confidence': 0
            }

        text = text.lower()

        # 키워드 카운트
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
        total_count = positive_count + negative_count

        if total_count == 0:
            return {
                'score': 0.5,
                'sentiment': 'neutral',
                'confidence': 0,
                'positive_count': 0,
                'negative_count': 0
            }

        # 감성 점수 계산 (0.0 ~ 1.0)
        score = positive_count / total_count

        # 감성 분류
        if score >= 0.6:
            sentiment = 'positive'
        elif score <= 0.4:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # 신뢰도 (키워드 개수에 비례)
        confidence = min(total_count / 5.0, 1.0)  # 최대 5개 키워드

        return {
            'score': score,
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count
        }

    def analyze_news_list(self, news_list):
        """
        뉴스 리스트 전체 감성 분석

        Args:
            news_list (list): 뉴스 딕셔너리 리스트

        Returns:
            dict: 종합 감성 분석 결과
        """
        if not news_list:
            return {
                'overall_score': 0.5,
                'overall_sentiment': 'neutral',
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'positive_count': 0,  # Phase 2-2: 추가
                'negative_count': 0,  # Phase 2-2: 추가
                'neutral_count': 0,   # Phase 2-2: 추가
                'total_news': 0,
                'confidence': 0
            }

        print(f"📰 뉴스 {len(news_list)}개 감성 분석 중...")

        sentiments = []
        for news in news_list:
            # 제목과 설명 결합
            text = f"{news.get('제목', '')} {news.get('설명', '')}"
            result = self.analyze_text(text)
            sentiments.append(result)

        # 통계 계산
        total = len(sentiments)
        positive = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral = total - positive - negative

        # 전체 감성 점수 (평균)
        overall_score = sum(s['score'] for s in sentiments) / total
        overall_confidence = sum(s['confidence'] for s in sentiments) / total

        # 전체 감성 분류
        if overall_score >= 0.6:
            overall_sentiment = 'positive'
        elif overall_score <= 0.4:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        result = {
            'overall_score': overall_score,
            'overall_sentiment': overall_sentiment,
            'positive_ratio': positive / total,
            'negative_ratio': negative / total,
            'neutral_ratio': neutral / total,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'total_news': total,
            'confidence': overall_confidence,
            'details': sentiments
        }

        print(f"✅ 감성 분석 완료: {overall_sentiment} (점수: {overall_score:.2f})")
        return result

    def get_sentiment_trend(self, news_list, days=7):
        """
        시간별 감성 추세 분석

        Args:
            news_list (list): 날짜 정보가 있는 뉴스 리스트
            days (int): 분석 기간

        Returns:
            dict: 일별 감성 추세
        """
        from datetime import datetime, timedelta
        from collections import defaultdict

        daily_sentiments = defaultdict(list)

        for news in news_list:
            pub_date = news.get('게시일')
            if not pub_date:
                continue

            try:
                # ISO 형식 파싱
                date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                day_key = date.strftime('%Y-%m-%d')

                text = f"{news.get('제목', '')} {news.get('설명', '')}"
                sentiment = self.analyze_text(text)
                daily_sentiments[day_key].append(sentiment['score'])
            except:
                continue

        # 일별 평균 계산
        trend = {}
        for day, scores in sorted(daily_sentiments.items()):
            if scores:
                trend[day] = {
                    'score': sum(scores) / len(scores),
                    'count': len(scores)
                }

        return trend


# 고급 AI 감성 분석 (transformers 사용 - 선택사항)
class AdvancedSentimentAnalyzer:
    """
    Transformer 기반 고급 감성 분석
    초기 로딩에 시간이 걸리므로 선택적 사용
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False

    def load_model(self):
        """모델 로드 (처음 한 번만)"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            print("🤖 AI 감성 분석 모델 로딩 중... (최초 1회, 수 분 소요)")

            model_name = "cardiffnlp/twitter-roberta-base-sentiment"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            self.loaded = True
            print("✅ AI 모델 로드 완료")
            return True

        except ImportError:
            print("⚠️ transformers 라이브러리가 필요합니다: pip install transformers torch")
            return False
        except Exception as e:
            print(f"❌ 모델 로드 실패: {str(e)}")
            return False

    def analyze_text(self, text):
        """AI 기반 감성 분석"""
        if not self.loaded:
            if not self.load_model():
                return None

        try:
            import torch

            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)

            # 레이블: 0=negative, 1=neutral, 2=positive
            labels = ['negative', 'neutral', 'positive']
            scores_dict = {labels[i]: scores[0][i].item() for i in range(3)}

            # 최고 점수 레이블
            max_label = max(scores_dict, key=scores_dict.get)

            return {
                'sentiment': max_label,
                'scores': scores_dict,
                'confidence': scores_dict[max_label]
            }

        except Exception as e:
            print(f"❌ AI 분석 실패: {str(e)}")
            return None


# 테스트 코드
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()

    # 테스트 텍스트
    test_texts = [
        "삼성전자 주가 급등, 반도체 수출 호조",
        "증시 폭락, 투자자들 우려 확산",
        "코스피 보합권에서 등락 반복",
        "비트코인 신고가 경신, 투자 열기 뜨거워",
        "암호화폐 시장 급락, 규제 리스크 부각"
    ]

    print("=== 개별 텍스트 감성 분석 ===")
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"\n텍스트: {text}")
        print(f"감성: {result['sentiment']} (점수: {result['score']:.2f}, 신뢰도: {result['confidence']:.2f})")

    # 뉴스 리스트 분석
    print("\n\n=== 뉴스 리스트 종합 분석 ===")
    news_list = [{'제목': text, '설명': ''} for text in test_texts]
    overall = analyzer.analyze_news_list(news_list)

    print(f"\n종합 감성: {overall['overall_sentiment']}")
    print(f"점수: {overall['overall_score']:.2f}")
    print(f"긍정: {overall['positive_ratio']:.1%}")
    print(f"부정: {overall['negative_ratio']:.1%}")
    print(f"중립: {overall['neutral_ratio']:.1%}")
