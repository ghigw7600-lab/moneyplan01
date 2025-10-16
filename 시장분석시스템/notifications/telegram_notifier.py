# -*- coding: utf-8 -*-
"""
텔레그램 알림 모듈
"""
import requests
import json
from datetime import datetime


class TelegramNotifier:
    """텔레그램 메시지 전송"""

    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None

    def send_message(self, message, parse_mode="HTML"):
        """텔레그램 메시지 전송"""
        if not self.bot_token or not self.chat_id:
            print("⚠️ 텔레그램 설정 필요 (config.py에서 설정)")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }

            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print("✅ 텔레그램 알림 전송 완료")
                return True
            else:
                print(f"❌ 텔레그램 전송 실패: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 텔레그램 오류: {str(e)}")
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

        message = f"""
{emoji.get(signal_type, '📊')} <b>매매 신호 발생!</b>

📌 <b>종목:</b> {ticker}
💰 <b>현재가:</b> {price:,}원
📊 <b>신호:</b> {signal_type.upper()}
🎯 <b>신뢰도:</b> {confidence}%

<b>🔍 주요 근거:</b>
"""
        for reason in reasons[:3]:  # 상위 3개만
            message += f"• {reason.get('reason', '')}\n"

        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_message(message)

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

        message = f"""
{emoji} <b>{msg}</b>

📌 <b>종목:</b> {ticker}
💰 <b>현재가:</b> {current_price:,}원
🎯 <b>목표가:</b> {target_price:,}원

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def send_portfolio_summary(self, portfolio_data):
        """포트폴리오 요약 알림"""
        message = f"""
📊 <b>포트폴리오 현황</b>

💰 <b>총 평가액:</b> {portfolio_data.get('total_value', 0):,}원
📈 <b>총 수익률:</b> {portfolio_data.get('total_return', 0):+.2f}%

<b>보유 종목:</b>
"""
        for stock in portfolio_data.get('stocks', [])[:5]:
            message += f"• {stock['name']}: {stock['return']:+.2f}%\n"

        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_message(message)
