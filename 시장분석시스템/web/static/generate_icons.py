#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
머니플랜01 PWA 아이콘 생성 스크립트
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """PWA 아이콘 생성"""

    # 그라데이션 배경 생성
    img = Image.new('RGB', (size, size), '#667eea')
    draw = ImageDraw.Draw(img)

    # 그라데이션 효과 (상단: #667eea, 하단: #764ba2)
    for y in range(size):
        # 색상 보간
        ratio = y / size
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)

        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # 원형 배경 (흰색)
    circle_size = int(size * 0.7)
    circle_pos = (size - circle_size) // 2
    draw.ellipse(
        [circle_pos, circle_pos, circle_pos + circle_size, circle_pos + circle_size],
        fill='white'
    )

    # 텍스트 추가
    try:
        # 한글 폰트 시도
        font_size = int(size * 0.25)
        font = ImageFont.truetype("malgun.ttf", font_size)  # Windows 맑은 고딕
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # "₩" 심볼 추가 (돈 관련)
    text = "₩"

    # 텍스트 크기 계산
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 중앙 배치
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - int(size * 0.02)

    # 텍스트 그리기 (보라색 그라데이션)
    draw.text((text_x, text_y), text, fill='#667eea', font=font)

    # "01" 작은 텍스트 추가
    try:
        small_font_size = int(size * 0.12)
        small_font = ImageFont.truetype("malgun.ttf", small_font_size)
    except:
        try:
            small_font = ImageFont.truetype("Arial.ttf", small_font_size)
        except:
            small_font = ImageFont.load_default()

    small_text = "01"
    bbox = draw.textbbox((0, 0), small_text, font=small_font)
    small_text_width = bbox[2] - bbox[0]

    small_text_x = (size - small_text_width) // 2 + int(size * 0.15)
    small_text_y = (size - text_height) // 2 + int(size * 0.15)

    draw.text((small_text_x, small_text_y), small_text, fill='#764ba2', font=small_font)

    # 저장
    img.save(filename, 'PNG')
    print(f"Icon created: {filename} ({size}x{size})")

def main():
    """메인 함수"""
    print("Generating PWA icons...")

    # 현재 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 192x192 아이콘
    create_icon(192, os.path.join(current_dir, 'icon-192.png'))

    # 512x512 아이콘
    create_icon(512, os.path.join(current_dir, 'icon-512.png'))

    print("\nAll icons generated successfully!")

if __name__ == '__main__':
    main()
