# -*- coding: utf-8 -*-
"""
이메일 알림 모듈
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailNotifier:
    """이메일 알림 전송"""

    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587,
                 sender_email=None, sender_password=None, receiver_email=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email or sender_email

    def send_email(self, subject, body, html=False):
        """이메일 전송"""
        if not self.sender_email or not self.sender_password:
            print("⚠️ 이메일 설정 필요 (config.py에서 설정)")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.receiver_email

            if html:
                part = MIMEText(body, "html", "utf-8")
            else:
                part = MIMEText(body, "plain", "utf-8")

            message.attach(part)

            # SMTP 서버 연결
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print("✅ 이메일 알림 전송 완료")
            return True

        except Exception as e:
            print(f"❌ 이메일 오류: {str(e)}")
            return False

    def send_trade_signal(self, ticker, signal_type, price, confidence, reasons):
        """매매 신호 이메일"""
        emoji = {
            'strong_buy': '🚀',
            'buy': '📈',
            'neutral': '➡️',
            'sell': '📉',
            'strong_sell': '🔻'
        }

        subject = f"{emoji.get(signal_type, '📊')} [{ticker}] {signal_type.upper()} 신호 발생!"

        # HTML 이메일 본문
        body = f"""
<html>
<head>
<style>
    body {{ font-family: 'Malgun Gothic', sans-serif; }}
    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }}
    .content {{ padding: 20px; }}
    .info-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; }}
    .reason {{ background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px; }}
</style>
</head>
<body>
    <div class="header">
        <h2>{emoji.get(signal_type, '📊')} 매매 신호 발생!</h2>
    </div>
    <div class="content">
        <div class="info-box">
            <p><strong>📌 종목:</strong> {ticker}</p>
            <p><strong>💰 현재가:</strong> {price:,}원</p>
            <p><strong>📊 신호:</strong> {signal_type.upper()}</p>
            <p><strong>🎯 신뢰도:</strong> {confidence}%</p>
        </div>

        <h3>🔍 주요 근거</h3>
"""

        for i, reason in enumerate(reasons[:5], 1):
            body += f"<div class='reason'>{i}. {reason.get('reason', '')}</div>\n"

        body += f"""
        <p style="margin-top: 20px; color: #6c757d;">
            ⏰ {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
        </p>
    </div>
</body>
</html>
"""

        return self.send_email(subject, body, html=True)

    def send_price_alert(self, ticker, current_price, target_price, alert_type):
        """가격 알림 이메일"""
        if alert_type == "reached":
            emoji = "🎯"
            msg = "목표가 도달!"
        elif alert_type == "surge":
            emoji = "🚀"
            msg = "급등 감지!"
        else:
            emoji = "📉"
            msg = "급락 감지!"

        subject = f"{emoji} [{ticker}] {msg}"

        body = f"""
<html>
<body style="font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="color: #667eea;">{emoji} {msg}</h2>
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
        <p><strong>📌 종목:</strong> {ticker}</p>
        <p><strong>💰 현재가:</strong> {current_price:,}원</p>
        <p><strong>🎯 목표가:</strong> {target_price:,}원</p>
    </div>
    <p style="color: #6c757d; margin-top: 20px;">
        ⏰ {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
    </p>
</body>
</html>
"""

        return self.send_email(subject, body, html=True)

    def send_portfolio_summary(self, portfolio_data):
        """포트폴리오 요약 이메일"""
        subject = f"📊 포트폴리오 현황 - {datetime.now().strftime('%Y-%m-%d')}"

        stocks_html = ""
        for stock in portfolio_data.get('stocks', []):
            color = "green" if stock['return'] >= 0 else "red"
            stocks_html += f"""
            <tr>
                <td>{stock['name']}</td>
                <td style="text-align: right;">{stock['quantity']:,}주</td>
                <td style="text-align: right;">{stock['avg_price']:,}원</td>
                <td style="text-align: right;">{stock['current_price']:,}원</td>
                <td style="text-align: right; color: {color}; font-weight: bold;">
                    {stock['return']:+.2f}%
                </td>
            </tr>
            """

        body = f"""
<html>
<body style="font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="color: #667eea;">📊 포트폴리오 현황</h2>

    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>💰 총 평가액: {portfolio_data.get('total_value', 0):,}원</h3>
        <h3>📈 총 수익률: {portfolio_data.get('total_return', 0):+.2f}%</h3>
    </div>

    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead style="background: #f8f9fa;">
            <tr>
                <th style="padding: 10px; text-align: left;">종목</th>
                <th style="padding: 10px; text-align: right;">수량</th>
                <th style="padding: 10px; text-align: right;">평균단가</th>
                <th style="padding: 10px; text-align: right;">현재가</th>
                <th style="padding: 10px; text-align: right;">수익률</th>
            </tr>
        </thead>
        <tbody>
            {stocks_html}
        </tbody>
    </table>

    <p style="color: #6c757d; margin-top: 30px;">
        ⏰ {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
    </p>
</body>
</html>
"""

        return self.send_email(subject, body, html=True)
