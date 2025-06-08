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


def draw_dashed_line(draw, start, end, dash_length=5, gap_length=3, fill="black", width=1):
    """
    绘制虚线
    :param draw: ImageDraw对象
    :param start: 起点坐标 (x1, y1)
    :param end: 终点坐标 (x2, y2)
    :param dash_length: 每段虚线长度
    :param gap_length: 每段间隙长度
    :param fill: 线条颜色
    :param width: 线条宽度
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    distance = (dx ** 2 + dy ** 2) ** 0.5  # 计算线段总长度
    dx_unit = dx / distance
    dy_unit = dy / distance

    current_pos = 0
    while current_pos < distance:
        # 计算当前线段的起点和终点
        segment_start = (
            int(x1 + current_pos * dx_unit),
            int(y1 + current_pos * dy_unit)
        )
        segment_end = (
            int(x1 + min(current_pos + dash_length, distance) * dx_unit),
            int(y1 + min(current_pos + dash_length, distance) * dy_unit)
        )
        # 绘制当前线段
        draw.line([segment_start, segment_end], fill=fill, width=width)
        current_pos += dash_length + gap_length  # 移动到下一段起点


def draw_multi_row_text(draw, text, per_row, left, upper, text_size, text_gap, font):
    rows = (len(text) - 1) // per_row + 1
    for j in range(int(rows)):
        end = (j + 1) * per_row
        row_text = text[j * per_row:end if end < len(text) else len(text)]
        draw.text((left, upper + (text_size + text_gap) * (j + 1)),
                  row_text, font=font, fill="black", anchor="la")

    return rows


# 计算行数
def count_multi_row(text, per_row):
    return (len(text) - 1) // per_row + 1


# 英文标点到中文标点的映射字典
punctuation_map = {
    ',': '，',
    '.': '。',
    ':': '：',
    ';': '；',
    '!': '！',
    '?': '？',
    '(': '（',
    ')': '）',
    '[': '【',
    ']': '】',
    '<': '《',
    '>': '》',
    '"': '“',
    "'": '‘',
    '`': '·'
}

# 中文标点集合（包括映射后的和原有的）
chinese_punctuation = set(punctuation_map.values()) | {
    '，', '。', '：', '；', '！', '？', '（', '）', '【', '】', '《', '》', '“', '‘', '·'
}


def convert_punctuation_to_chinese(text):
    result = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]
        # 检查当前字符是否是英文标点
        if char in punctuation_map:
            # 替换为中文标点
            result.append(punctuation_map[char])
            # 检查下一个字符是否是空格，如果是则跳过
            if i + 1 < n and text[i + 1] == ' ':
                i += 1
        else:
            # 检查当前字符是否是中文标点
            if char in chinese_punctuation:
                result.append(char)
                # 检查下一个字符是否是空格，如果是则跳过
                if i + 1 < n and text[i + 1] == ' ':
                    i += 1
            else:
                result.append(char)
        i += 1

    return ''.join(result)
