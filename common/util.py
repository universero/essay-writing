import math

from lxml import html


def html_strip(text):
    """使用lxml移除HTML标签"""
    document = html.fromstring(text)
    return document.text_content().strip()


def draw_wavy_line(draw, start_pos, end_pos, amplitude=5, wavelength=20, fill="black", width=2):
    """
    绘制水平波浪线
    参数：
    - start_pos: (x1, y1) 起点坐标
    - end_pos: (x2, y2) 终点坐标
    - amplitude: 波幅
    - wavelength: 波长
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    if x1 == x2:  # 垂直线
        draw.line([start_pos, end_pos], fill=fill, width=width)
        return

    points = []
    length = x2 - x1
    # 计算完整波的数量
    num_waves = length / wavelength
    # 每波需要的点数（控制曲线平滑度）
    points_per_wave = 20
    segments = int(num_waves * points_per_wave)

    for i in range(segments + 1):
        x = x1 + (x2 - x1) * i / segments
        # 正确的正弦波公式
        y = y1 + amplitude * math.sin(2 * math.pi * num_waves * i / segments)
        points.append((x, y))

    draw.line(points, fill=fill, width=width, joint="curve")
