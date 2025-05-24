"""
批改结果可视化渲染
steps:
  - 基础作文纸生成
  - 批注蒙版叠加
  - 长图拆分
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

from evaluator.micro_builder import MicroEvaluationBuilder
from evaluator.micro_evalu import MicroEvaluation

coefficient = 5

# 字体配置
EVAL_FONT = os.path.abspath('../assert/瑞美加张清平硬笔行书.ttf')
TEXT_FONT = ImageFont.truetype(os.path.abspath('../asset/ToneOZ-Tsuipita-TC（仅汉字）.ttf'), size=17 * coefficient)

# 页面
PAGE_HEIGHT = 993 * coefficient  # 页面高度为993px
PAGE_WIDTH = 702 * coefficient  # 页面宽度为702px

# 方格
GRID_HEIGHT = 34 * coefficient  # 每个格子的高度
GRID_WIDTH = 30 * coefficient  # 每个格子的宽度（px）
GRID_PER_ROW = 17  # 每行格子数
GRID_MARGIN_TOP = 24 * coefficient  # 上边距
GRID_MARGIN_LEFT = 24 * coefficient  # 左边距
GRID_LINE = 3

# 两行方格中间
GAP_BAR_HEIGHT = 7 * coefficient  # 两行中间的间距
GAP_BAR_WIDTH = 510 * coefficient  # 每行的宽度
GAP_LINE = 3

# 段评, 多行时需要计算高度, 暂时只有一行
MID_BAR_HEIGHT = 56 * 3
MID_BAR_WIDTH = 510 * 3
MID_BAR_MARGIN = 12 * coefficient  # 段评中上下侧的距离
MID_BAR_TEXT_GAP = 8 * coefficient  # 段评中字的间隔
MID_BAR_TEXT_HEIGHT = 13 * coefficient  # 段评中字体高度
MID_BAR_TEXT_WIDTH = 13 * coefficient  # 短评字体宽度

# 侧边评价
SIDE_BAR_HEIGHT = 946 * 3
SIDE_BAR_WIDTH = 140 * 3
SIDE_BAR_MARGIN_LEFT = 11 * coefficient  # 侧边评价与作文主体间的间距
SIDE_BAR_MARGIN_RIGHT = 11 * coefficient  # 和右侧的区别
SIDE_BAR_MARGIN_TOP = 24 * coefficient  # 与顶部距离
SIDE_BAR_TEXT_HEIGHT = 13 * coefficient  # 侧边评价字高
SIDE_BAR_TEXT_WIDTH = 13 * coefficient  # 侧边评价字宽


class Render:
    """
    Render 负责批改结果渲染的核心类
    """

    def __init__(self, title: str, content: str, evalu: MicroEvaluation):
        """
        初始化
        :param title: 作文标题
        :param content: 作文内容分段
        """
        self.title = title
        self.content = content
        self.paras = []
        self.evalu = evalu
        self.img = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")

    def visualize(self):
        """可视化批改结果"""
        self.deal_title()
        self.divide_paras()
        self.fill_para()
        self.img.show()

    def fill_para(self):
        """填充一段"""
        for i in range(len(self.paras)):
            p = self.paras[i]
            self.draw_grid_and_mid(i, p.text, p.text_start, p.text_end)

    # 绘制方格
    def draw_grid_and_mid(self, number, text, row_start, row_end):
        draw = ImageDraw.Draw(self.img)
        row = row_start
        idx = 0
        while row < row_end:
            # 每行一个一个地绘制
            for i in range(GRID_PER_ROW):
                draw.rectangle([(GRID_WIDTH * i + GRID_MARGIN_LEFT, row),
                                (GRID_WIDTH * (i + 1) + GRID_MARGIN_LEFT, row + GRID_HEIGHT)],
                               outline="black", width=GRID_LINE)
                content = " "
                if number != 0 and len(text) > idx - 2 >= 0:
                    content = text[idx - 2]
                elif number == 0 and idx < GRID_PER_ROW:  # 标题行
                    content = text[idx]
                elif number == 0 and GRID_PER_ROW <= idx - 2 < len(text):  # 第一段非标题行
                    content = text[idx - 2]
                draw.text((GRID_WIDTH * i + GRID_MARGIN_LEFT + GRID_WIDTH // 2, row + GRID_HEIGHT // 2),
                          content, font=TEXT_FONT, fill="black", anchor="mm")
                idx += 1
            # 绘制两行间隔
            draw.rectangle([(GRID_MARGIN_LEFT, row + GRID_HEIGHT,),
                            (GRID_MARGIN_LEFT + GAP_BAR_WIDTH, row + GRID_HEIGHT + GAP_BAR_HEIGHT)],
                           outline="black", width=GAP_LINE)
            row += GRID_HEIGHT + GAP_BAR_HEIGHT

    def divide_paras(self):
        """划分段落"""
        paras = self.content.split("\n")
        rows = 0
        for i in range(len(paras)):
            # 本段长度
            para_len = len(paras[i]) + 2
            # 本段行数
            row = (para_len - 1) // GRID_PER_ROW + 1
            text_start = GRID_MARGIN_TOP
            if rows != 0:
                text_start = self.paras[i - 1].bar_end + MID_BAR_MARGIN
            text_end = text_start + row * (GRID_HEIGHT + GAP_BAR_HEIGHT)
            bar_start = text_end + MID_BAR_MARGIN
            bar_end = bar_start + MID_BAR_HEIGHT
            self.paras.append(Para(paras[i], row, text_start, text_end, bar_start, bar_end))
            rows += row

    def deal_title(self):
        """将标题合并到第一段中以简化处理"""
        n = len(self.title)
        left = (GRID_PER_ROW - n) // 2
        self.content = " " * left + self.title + " " * (GRID_PER_ROW - left - n) + self.content


class Para:
    def __init__(self, text, rows, text_start, text_end, bar_start, bar_end):
        """
        :param text: 本段内容
        :param rows: 本段行数
        :param text_start: 本段段落内容开始行像素
        :param text_end: 本段段落内容结束行像素
        :param bar_start: 本段段评开始行像素
        :param bar_end: 本段段评结束行像素
        """
        self.text = text
        self.rows = rows
        self.text_start = text_start
        self.text_end = text_end
        self.bar_start = bar_start
        self.bar_end = bar_end


if __name__ == '__main__':
    with open('../asset/example.json', encoding='utf-8') as f:
        raw_data = json.load(f)

    e = MicroEvaluationBuilder.build(raw_data)
    r = Render("一场有趣的投篮游戏",
               "今天的阳光明媚，小鸟在树间欢快地歌唱，校园里一片生机勃勃。午休时，我们班的同学们聚集在操场上，准备进行一场有趣的投篮游戏。\n我们首先分成了两队，一队是蓝队，另一队是红队。蓝队的队员有我、小明和小华，红队则由小丽、小杰和小雨组成。比赛规则很简单，每人轮流投篮，看哪队投进去的篮球最多，最后得分高的队伍获胜。游戏开始前，我们都迫不及待想要展示自己的投篮技术。\n我第一个上场，心里有些紧张，但我告诉自己要放轻松。当我拿起篮球站在三分线外时，心里默念着：\"一定要投进去！\"我深吸一口气，认真地瞄准篮筐，轻轻一抛，篮球在空中划出一个优美的弧线，终于\"咚\"地一声进了篮筐！我兴奋地挥舞起双手，队友们也为我欢呼鼓掌。\n接下来的轮到小明和小华，他们也都非常出色，轮番投中多个球，使蓝队的分数不断攀升。红队的小丽投篮技术也很不错，虽然一开始有些失误，但她很快调整状态，接连投中几球，为红队追赶分数。\n随着比赛的进行，大家的气氛越来越热烈，操场上充满了欢声笑语。有的同学为自己的队友加油打气，有的则在一旁跃跃欲试。突然，小杰的投篮时机把握得非常好，他一连投中了三球，红队的分数迅速上涨，让我们感受到了一些压力。\n比赛进入了尾声，我和队友们迅速商量战术，决定增加配合，尽量打好每一次投篮。最后的几轮，我和小明默契地传球，终于又得到了几分。经过激烈的角逐，最后的比分是蓝队35分，红队30分，蓝队获得了胜利。\n虽然红队输掉了比赛，但大家都十分开心。我们一起庆祝，享受着这个愉快的时刻。在游戏结束后，我们互相祝贺，也约定下次再来挑战。今天的投篮游戏不仅锻炼了我们的身体，更让我们体会到了友谊和团队协作的重要性。\n这场投篮游戏让我留下了深刻的印象，我希望以后还能有更多这样的活动，让我们的校园生活更加丰富多彩！",
               e)
    r.visualize()
