# -*- coding: utf-8 -*-
"""
카카오톡 알림 모듈 (카카오 비즈니스 메시지 API)
"""
import requests
import json
from datetime import datetime


class KakaoNotifier:
    """카카오톡 메시지 전송"""

    def __init__(self, rest_api_key=None, template_id=None, phone_number=None):
        self.rest_api_key = rest_api_key
        self.template_id = template_id
        self.phone_number = phone_number
        self.access_token = None

    def get_access_token(self, auth_code):
        """OAuth 인증 토큰 받기"""
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.rest_api_key,
            "code": auth_code
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                print("✅ 카카오 토큰 발급 완료")
                return True
            else:
                print(f"❌ 토큰 발급 실패: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 카카오 오류: {str(e)}")
            return False

    def send_message_to_me(self, template_object):
        """나에게 메시지 보내기"""
        if not self.access_token:
            print("⚠️ 카카오 액세스 토큰 필요 (config.py에서 설정)")
            return False

        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "template_object": json.dumps(template_object)
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ 카카오톡 알림 전송 완료")
                return True
            else:
                print(f"❌ 카카오톡 전송 실패: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 카카오톡 오류: {str(e)}")
            return False

    def send_trade_signal(self, ticker, signal_type, price, confidence, reasons):
        """매매 신호 알림"""
        emoji = {
            'strong_buy': '🚀',
            'buy': '📈',
            'neutral': '➡️',
            'sell': '📉',
            'strong_sell': '🔻'
        }

        # 상위 3개 근거만
        reason_text = "\n".join([f"• {r.get('reason', '')}" for r in reasons[:3]])

        template = {
            "object_type": "text",
            "text": f"""{emoji.get(signal_type, '📊')} 매매 신호 발생!

📌 종목: {ticker}
💰 현재가: {price:,}원
📊 신호: {signal_type.upper()}
🎯 신뢰도: {confidence}%

🔍 주요 근거:
{reason_text}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            "link": {
                "web_url": "https://finance.naver.com",
                "mobile_web_url": "https://finance.naver.com"
            }
        }

        return self.send_message_to_me(template)

    def send_price_alert(self, ticker, current_price, target_price, alert_type):
        """가격 알림"""
        if alert_type == "reached":
            emoji = "🎯"
            msg = "목표가 도달!"
        elif alert_type == "surge":
            emoji = "🚀"
            msg = "급등 감지!"
        else:
            emoji = "📉"
            msg = "급락 감지!"

        template = {
            "object_type": "text",
            "text": f"""{emoji} {msg}

📌 종목: {ticker}
💰 현재가: {current_price:,}원
🎯 목표가: {target_price:,}원

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            "link": {
                "web_url": "https://finance.naver.com",
                "mobile_web_url": "https://finance.naver.com"
            }
        }

        return self.send_message_to_me(template)

    def send_portfolio_summary(self, portfolio_data):
        """포트폴리오 요약 알림"""
        stocks_text = "\n".join([
            f"• {s['name']}: {s['return']:+.2f}%"
            for s in portfolio_data.get('stocks', [])[:5]
        ])

        template = {
            "object_type": "text",
            "text": f"""📊 포트폴리오 현황

💰 총 평가액: {portfolio_data.get('total_value', 0):,}원
📈 총 수익률: {portfolio_data.get('total_return', 0):+.2f}%

보유 종목:
{stocks_text}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            "link": {
                "web_url": "https://finance.naver.com",
                "mobile_web_url": "https://finance.naver.com"
            }
        }

        return self.send_message_to_me(template)


# 간편 카카오톡 알림 (Windows 알림으로 대체 가능)
class SimpleKakaoNotifier:
    """간단한 로컬 알림 (카카오 API 없이)"""

    def send_message(self, title, message):
        """Windows 알림 띄우기"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                duration=10,
                icon_path=None,
                threaded=True
            )
            return True
        except:
            # win10toast 없으면 콘솔 출력
            print(f"\n{'='*60}")
            print(f"[카카오톡 알림] {title}")
            print(f"{message}")
            print(f"{'='*60}\n")
            return False
