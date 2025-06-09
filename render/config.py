# 比例系数, 用于提高画质, 画质越高耗时越长
import os

from PIL import ImageFont

coefficient = 5

# 页面
PAGE_HEIGHT = 993 * coefficient  # 页面高度为993px
PAGE_WIDTH = 702 * coefficient  # 页面宽度为702px

# 方格
GRID_HEIGHT = 34 * coefficient  # 每个格子的高度
GRID_WIDTH = 30 * coefficient  # 每个格子的宽度（px）
GRID_PER_ROW = 17  # 每行格子数
MARGIN_TOP = 24 * coefficient  # 上边距
MARGIN_LEFT = 24 * coefficient  # 左边距
GRID_TEXT_SIZE = 17 * coefficient
GRID_LINE = 3

# 两行方格中间
GAP_BAR_HEIGHT = 7 * coefficient  # 两行中间的间距
GAP_BAR_WIDTH = 510 * coefficient  # 每行的宽度
GAP_LINE = 3

# 段评, 多行时需要计算高度, 暂时只有一行
MID_BAR_HEIGHT = 76 * coefficient
MID_BAR_WIDTH = 510 * coefficient
MID_BAR_MARGIN_TOP = 8 * coefficient  # 段评中上下侧的距离
MID_BAR_MARGIN_LEFT = 0.4 * GRID_WIDTH  # 第一个字距离段评左侧线的距离
MID_BAR_TEXT_GAP = 8 * coefficient  # 段评中字的间隔
MID_BAR_TEXT_SIZE = 13 * coefficient  # 段评中字体高度
MID_BAR_PER_ROW = int((MID_BAR_WIDTH - MID_BAR_MARGIN_LEFT * 2) // (MID_BAR_TEXT_SIZE * 1.3))
MID_BAR_LINE = 5

# 侧边评价
SIDE_BAR_WIDTH = 140 * coefficient  # 侧边评价宽度
SIDE_BAR_MARGIN_LEFT = 3 * coefficient  # 侧边评价与侧边栏左侧的间距
SIDE_BAR_MARGIN_RIGHT = 11 * coefficient  # 和右侧的区别
SIDE_BAR_MARGIN_TOP = 24 * coefficient  # 与顶部距离
SIDE_BAR_TEXT_SIZE = 13 * coefficient  # 侧边评价字高
SIDE_BAR_TEXT_GAP = 5 * coefficient  # 侧边栏中字间距
SIDE_BAR_ITEM_GAP = 12 * coefficient  # 侧边栏中两项的间距
SIDE_BAR_ITEM_SIZE = 12 * coefficient
SIDE_BAR_PER_ROW = int((SIDE_BAR_WIDTH - SIDE_BAR_MARGIN_LEFT) // (SIDE_BAR_TEXT_SIZE * 1.1))
SIDE_BAR_LINE = 5
SIDE_BAR_COLOR = "#F19E3E"

# 段落编号
NO_MARGIN_LEFT = GRID_WIDTH * 0.2 + MARGIN_LEFT  # 段落编号距离页左侧距离
NO_MARGIN_TOP = GRID_HEIGHT * 0.2  # 段落编号距离所在方格的上侧距离
NO_HEIGHT = GRID_HEIGHT * 0.6  # 编号高度
NO_WIDTH = GRID_WIDTH * 0.8  # 编号宽度
NO_COLOR = "#F19E3E"
NO_TEXT_SIZE = 10 * coefficient

# 病句
SICK_COLOR = "red"
SICK_LINE = int(1.5 * coefficient)

# 错词错标点
TYPO_MASK_COLOR = (255, 95, 93, 70)  # 透明红色

# 好词好句
HIGHLIGHT_MASK_COLOR = (101, 130, 255, 70)  # 透明蓝色
HIGHLIGHT_AMPLITUDE = 1.1 * coefficient  # 波浪线波幅
HIGHLIGHT_WAVELENGTH = 15 * coefficient  # 波浪线波长
HIGHLIGHT_LINE_COLOR = (101, 130, 255)
HIGHLIGHT_LINE = int(1.5 * coefficient)

# 序号
SEQ_RADIUS = 5 * coefficient
SEQ_COLOR = (101, 130, 255)
SEQ_TEXT_SIZE = 7 * coefficient

# 全文评价
ALL_MARGIN_TOP = 20 * coefficient
ALL_MARGIN_LEFT = int(0.6 * GRID_WIDTH)
ALL_MARGIN_RIGHT = 45 * coefficient
ALL_WIDTH = 492 * coefficient
ALL_ITEM_GAP = 20 * coefficient
ALL_ICON_RADIUS = 5 * coefficient
ALL_ICON_WIDTH = 3 * coefficient
ALL_TAG_SIZE = 18 * coefficient
ALL_SCORE_SIZE = 2 * ALL_TAG_SIZE
ALL_TEXT_SIZE = 17 * coefficient
ALL_TEXT_GAP = 8 * coefficient
ALL_PER_ROW = int(ALL_WIDTH // ALL_TEXT_SIZE)
ALL_COLOR = "#F19E3E"
ALL_LINE = 1 * coefficient
ALL_DASHED_LINE = 1 * coefficient
ALL_DASHED_LINE_LEN = 6 * coefficient
ALL_DASHED_GAP = 3 * coefficient

# 字体配置
EVAL_FONT = ImageFont.truetype(os.path.abspath('render/resource/瑞美加张清平硬笔行书.ttf'), size=17 * coefficient)
TEXT_FONT = ImageFont.truetype(os.path.abspath('render/resource/ToneOZ-Tsuipita-TC（仅汉字）.ttf'), size=GRID_TEXT_SIZE)
NO_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=NO_TEXT_SIZE)
MID_BAR_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=MID_BAR_TEXT_SIZE)
SEQ_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=SEQ_TEXT_SIZE)
SIDE_BAR_ITEM_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=SIDE_BAR_ITEM_SIZE)
SIDE_BAR_TEXT_FONT = ImageFont.truetype(os.path.abspath('render/resource/瑞美加张清平硬笔行书.ttf'),
                                        size=SIDE_BAR_TEXT_SIZE)
ALL_TAG_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=ALL_TAG_SIZE)
ALL_SCORE_FONT = ImageFont.truetype(os.path.abspath('render/resource/微软雅黑粗体.ttf'), size=ALL_SCORE_SIZE)
ALL_TEXT_FONT = ImageFont.truetype(os.path.abspath('render/resource/瑞美加张清平硬笔行书.ttf'), size=ALL_TEXT_SIZE)
