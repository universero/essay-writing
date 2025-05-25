"""
批改结果可视化渲染
steps:
  - 基础作文纸生成
  - 批注蒙版叠加
  - 长图拆分
"""
import json
import os
from itertools import groupby

from PIL import Image, ImageFont, ImageDraw

from common import util
from common.consts import ZH_NO
from evaluator.micro_builder import MicroEvaluationBuilder
from evaluator.micro_evalu import MicroEvaluation

coefficient = 5

# 页面
PAGE_HEIGHT = 993 * coefficient  # 页面高度为993px
PAGE_WIDTH = 702 * coefficient  # 页面宽度为702px

# 方格
GRID_HEIGHT = 34 * coefficient  # 每个格子的高度
GRID_WIDTH = 30 * coefficient  # 每个格子的宽度（px）
GRID_PER_ROW = 17  # 每行格子数
GRID_MARGIN_TOP = 24 * coefficient  # 上边距
GRID_MARGIN_LEFT = 24 * coefficient  # 左边距
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
SIDE_BAR_HEIGHT = 946 * coefficient
SIDE_BAR_WIDTH = 140 * coefficient
SIDE_BAR_MARGIN_LEFT = 11 * coefficient  # 侧边评价与作文主体间的间距
SIDE_BAR_MARGIN_RIGHT = 11 * coefficient  # 和右侧的区别
SIDE_BAR_MARGIN_TOP = 24 * coefficient  # 与顶部距离
SIDE_BAR_TEXT_HEIGHT = 13 * coefficient  # 侧边评价字高
SIDE_BAR_TEXT_WIDTH = 13 * coefficient  # 侧边评价字宽
SIDE_BAR_LINE = 5
SIDE_BAR_COLOR = "#F19E3E"

# 段落编号
NO_MARGIN_LEFT = GRID_WIDTH * 0.2 + GRID_MARGIN_LEFT  # 段落编号距离页左侧距离
NO_MARGIN_TOP = GRID_HEIGHT * 0.2  # 段落编号距离所在方格的上侧距离
NO_HEIGHT = GRID_HEIGHT * 0.6
NO_WIDTH = GRID_WIDTH * 0.8
NO_COLOR = "#F19E3E"
NO_TEXT_SIZE = 10 * coefficient

# 病句
SICK_COLOR = "red"
SICK_LINE = int(1.5 * coefficient)

# 错词错标点
TYPO_MASK_COLOR = (255, 95, 93, 70)  # 透明红色

# 好词好句
HIGHLIGHT_MASK_COLOR = (101, 130, 255, 70)  # 透明蓝色
HIGHLIGHT_AMPLITUDE = 1.1 * coefficient
HIGHLIGHT_WAVELENGTH = 15 * coefficient
HIGHLIGHT_LINE_COLOR = (101, 130, 255)
HIGHLIGHT_LINE = int(1.5 * coefficient)

# 序号
SEQ_RADIUS = 5 * coefficient
SEQ_COLOR = (101, 130, 255)
SEQ_TEXT_SIZE = 7 * coefficient

# 字体配置
EVAL_FONT = ImageFont.truetype(os.path.abspath('../asset/瑞美加张清平硬笔行书.ttf'), size=17 * coefficient)
TEXT_FONT = ImageFont.truetype(os.path.abspath('../asset/ToneOZ-Tsuipita-TC（仅汉字）.ttf'), size=GRID_TEXT_SIZE)
NO_FONT = ImageFont.truetype(os.path.abspath('../asset/微软雅黑粗体.ttf'), size=NO_TEXT_SIZE)
MID_BAR_FONT = ImageFont.truetype(os.path.abspath('../asset/微软雅黑粗体.ttf'), size=MID_BAR_TEXT_SIZE)
SEQ_FONT = ImageFont.truetype(os.path.abspath('../asset/微软雅黑粗体.ttf'), size=SEQ_TEXT_SIZE)


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
        self.todo_sidebar = []
        self.img = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), "white")

    def evalu_visualize(self):
        """可视化批改结果"""
        self.deal_title()
        self.divide_paras()
        self.paras_base()
        self.paras_number()
        self.paras_comments()
        # self.grammar_sentences() TODO
        self.sick_sentences()
        self.typo()
        self.advance_words()
        self.rhetoric()
        self.sidebar()
        self.img.show()

    def deal_title(self):
        """将标题合并到第一段中以简化处理"""
        n = len(self.title)
        left = (GRID_PER_ROW - n) // 2
        self.content = " " * left + self.title + " " * (GRID_PER_ROW - left - n) + self.content

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
                text_start = self.paras[i - 1].bar_end + MID_BAR_MARGIN_TOP
            text_end = text_start + row * (GRID_HEIGHT + GAP_BAR_HEIGHT)
            bar_start = text_end + MID_BAR_MARGIN_TOP
            bar_end = bar_start + MID_BAR_HEIGHT
            self.paras.append(Para(paras[i], row, text_start, text_end, bar_start, bar_end))
            rows += row

        # 根据文章总数构建页面长度
        page_number = (rows * (GRID_HEIGHT + GAP_BAR_HEIGHT) + len(paras) * (
                MID_BAR_HEIGHT + MID_BAR_MARGIN_TOP * 2)) // PAGE_HEIGHT + 1
        self.img = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT * page_number), "white")

    def paras_base(self):
        """绘制文字框线与段评框线等段落基本信息"""
        for i in range(len(self.paras)):
            self.draw_grid_and_mid(i, self.paras[i])

    def draw_grid_and_mid(self, number, para):
        """给一段绘制文字框线与段评框线"""
        draw = ImageDraw.Draw(self.img)
        row, text = para.text_start, para.text
        idx = 0
        while row < para.text_end:
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
                draw.text((GRID_WIDTH * i + GRID_MARGIN_LEFT + GRID_WIDTH // 2, row + GRID_HEIGHT - GRID_HEIGHT // 2),
                          content, font=TEXT_FONT, fill="black", anchor="mm")
                idx += 1
            # 绘制两行间隔
            draw.rectangle([(GRID_MARGIN_LEFT, row + GRID_HEIGHT,),
                            (GRID_MARGIN_LEFT + GAP_BAR_WIDTH, row + GRID_HEIGHT + GAP_BAR_HEIGHT)],
                           outline="black", width=GAP_LINE)
            row += GRID_HEIGHT + GAP_BAR_HEIGHT
        # 将每段的外圈加粗以保证视觉效果
        # 上
        draw.line([(GRID_MARGIN_LEFT, para.text_start - GRID_LINE // 2),
                   (GRID_MARGIN_LEFT + GAP_BAR_WIDTH, para.text_start - GRID_LINE // 2)],
                  fill="black", width=GRID_LINE)
        # 下
        draw.line([(GRID_MARGIN_LEFT, para.text_end + GAP_LINE // 2),
                   (GRID_MARGIN_LEFT + GAP_BAR_WIDTH, row + GAP_LINE // 2)],
                  fill="black", width=GAP_LINE)
        # 左
        draw.line([(GRID_MARGIN_LEFT - GRID_LINE // 2, para.text_start),
                   (GRID_MARGIN_LEFT - GRID_LINE // 2, para.text_end)],
                  fill="black", width=GAP_LINE)
        # 右
        draw.line([(GRID_MARGIN_LEFT + GAP_BAR_WIDTH + GRID_LINE // 2, para.text_start),
                   (GRID_MARGIN_LEFT + GAP_BAR_WIDTH + GRID_LINE // 2, para.text_end)],
                  fill="black", width=GAP_LINE)
        # 段落点评位置
        draw.rounded_rectangle([(GRID_MARGIN_LEFT, para.bar_start),
                                (GRID_MARGIN_LEFT + MID_BAR_WIDTH, para.bar_end)],
                               radius=40,
                               outline="black", width=MID_BAR_LINE)

    def paras_number(self):
        """绘制段落标号"""
        draw = ImageDraw.Draw(self.img)
        for i in range(len(self.paras)):
            no = "第" + ZH_NO[i + 1] + "段"
            left = NO_MARGIN_LEFT
            right = left + NO_WIDTH
            upper = self.paras[i].text_start + NO_MARGIN_TOP
            if i == 0:  # 首段需要考虑标题行
                upper += GRID_HEIGHT + GAP_BAR_HEIGHT
            down = upper + NO_HEIGHT
            radius = NO_HEIGHT // 2
            draw.circle((left + radius, upper + radius), radius, fill=NO_COLOR, outline=NO_COLOR)
            draw.circle((right + radius, down - radius), radius, fill=NO_COLOR, outline=NO_COLOR)
            draw.rectangle([(left + radius, upper), (right + radius, down)],
                           fill=NO_COLOR, outline=NO_COLOR)
            draw.text(((left + right) // 2 + radius, (upper + down) // 2),
                      no, font=NO_FONT, fill="white", anchor="mm")

    def paras_comments(self):
        """每一段的段评"""
        draw = ImageDraw.Draw(self.img)
        for i in range(len(self.paras)):
            # 段评提示
            no = "第" + ZH_NO[i + 1] + "段段评:"
            left = GRID_MARGIN_LEFT + MID_BAR_MARGIN_LEFT
            upper = self.paras[i].bar_start + MID_BAR_MARGIN_TOP
            draw.text((left, upper), no, font=MID_BAR_FONT, fill=NO_COLOR, anchor="la")
            text = util.html_strip(self.evalu.comments.paragraph_comments[i])
            # 分行写入段评实际内容
            rows = (len(text) - 1) // MID_BAR_PER_ROW + 1
            for j in range(int(rows)):
                end = (j + 1) * MID_BAR_PER_ROW
                row_text = text[j * MID_BAR_PER_ROW:end if end < len(text) else -1]
                draw.text((left, upper + (MID_BAR_TEXT_SIZE + MID_BAR_TEXT_GAP) * (j + 1)),
                          row_text, font=EVAL_FONT, fill="black", anchor="la")

    def sick_sentences(self):
        """绘制病句标识"""
        draw = ImageDraw.Draw(self.img)
        for sick_sentence in self.evalu.grammar.sick_sentence:
            # 全文索引转换为段落索引
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(sick_sentence.start_pos,
                                                                                       sick_sentence.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, "病句", sick_sentence.type, sick_sentence.revised, SICK_COLOR))
            now_row = start_row
            while now_row <= end_row:
                left, right = GRID_MARGIN_LEFT, GRID_MARGIN_LEFT + GAP_BAR_WIDTH
                if now_row == end_row:
                    right = GRID_MARGIN_LEFT + GRID_WIDTH * (end_col + 1)
                if now_row == start_row:
                    left = GRID_MARGIN_LEFT + GRID_WIDTH * start_col
                row = (self.paras[para_no].text_start + (now_row + 1) *
                       (GRID_HEIGHT + GAP_BAR_HEIGHT) - GAP_BAR_HEIGHT // 2)
                draw.line([(left, row), (right, row)], fill=SICK_COLOR, width=SICK_LINE)
                now_row += 1

    def typo(self):
        """绘制错误字词和标点"""
        # 透明蒙版
        mask = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        for typo in self.evalu.grammar.typo:
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(typo.start_pos, typo.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, typo.type, "", f"{typo.ori}改为{typo.revised}", SICK_COLOR))
            self.draw_mask(draw, para_no, start_row, start_col, end_row, end_col, TYPO_MASK_COLOR)
        self.img = Image.alpha_composite(self.img, mask)

    def advance_words(self):
        """好词"""
        mask = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        for words in self.evalu.highlights.advance_words:
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(words.start_pos, words.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, f"好词:{words.type}", words.memo["text"], "",
                        HIGHLIGHT_LINE_COLOR))
            self.draw_mask(draw, para_no, start_row, start_col, end_row, end_col, HIGHLIGHT_MASK_COLOR)
        self.img = Image.alpha_composite(self.img, mask)

    def rhetoric(self):
        """修辞部分"""
        draw = ImageDraw.Draw(self.img)
        for rhetoric in self.evalu.highlights.rhetoric:
            # 全文索引转换为段落索引
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(rhetoric.start_pos,
                                                                                       rhetoric.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, "好句", rhetoric.type, "", HIGHLIGHT_LINE_COLOR))
            now_row = start_row
            while now_row <= end_row:
                left, right = GRID_MARGIN_LEFT, GRID_MARGIN_LEFT + GAP_BAR_WIDTH
                if now_row == end_row:
                    right = GRID_MARGIN_LEFT + GRID_WIDTH * (end_col + 1)
                if now_row == start_row:
                    left = GRID_MARGIN_LEFT + GRID_WIDTH * start_col
                row = (self.paras[para_no].text_start + (now_row + 1) *
                       (GRID_HEIGHT + GAP_BAR_HEIGHT) - GAP_BAR_HEIGHT // 2)
                util.draw_wavy_line(draw, (left, row), (right, row), HIGHLIGHT_AMPLITUDE, HIGHLIGHT_WAVELENGTH,
                                    HIGHLIGHT_LINE_COLOR, HIGHLIGHT_LINE)
                now_row += 1

    def draw_mask(self, draw, para_no, start_row, start_col, end_row, end_col, color):
        now_row = start_row
        while now_row <= end_row:
            left, right = GRID_MARGIN_LEFT, GRID_MARGIN_LEFT + GAP_BAR_WIDTH
            if now_row == end_row:
                right = GRID_MARGIN_LEFT + GRID_WIDTH * (end_col + 1)
            if now_row == start_row:
                left = GRID_MARGIN_LEFT + GRID_WIDTH * start_col
            upper = self.paras[para_no].text_start + now_row * (GRID_HEIGHT + GAP_BAR_HEIGHT)
            down = upper + GRID_HEIGHT
            draw.rectangle([(left + GRID_LINE, upper + GRID_LINE), (right - GRID_LINE, down - GRID_LINE)],
                           fill=color)
            now_row += 1

    def sidebar(self):
        """绘制侧边评价"""
        draw = ImageDraw.Draw(self.img)
        right = PAGE_WIDTH - SIDE_BAR_MARGIN_RIGHT
        left = right - SIDE_BAR_WIDTH
        upper = self.paras[0].text_start
        down = self.paras[-1].bar_end
        draw.rectangle([(left, upper),
                        (right, down)],
                       outline="black", width=SIDE_BAR_LINE)
        self.todo_sidebar = sort_sidebar(self.todo_sidebar)
        for i in range(len(self.todo_sidebar)):
            sidebar = self.todo_sidebar[i]
            self.seq(i, sidebar.para, sidebar.row, sidebar.col, sidebar.color)

    def seq(self, number, para_no, row, col, color):
        """绘制序号标记"""
        draw = ImageDraw.Draw(self.img)
        para = self.paras[para_no]
        x, y = para.text_start + row * (
                GRID_HEIGHT + GAP_BAR_HEIGHT) + GRID_WIDTH // 10, GRID_MARGIN_LEFT + GRID_WIDTH * col
        draw.circle((y, x), SEQ_RADIUS, fill=color, outline=color)
        draw.text((y, x), str(number + 1), fill="white", font=SEQ_FONT, anchor="mm")

    def global_to_paragraph(self, pos_start, pos_end):
        """全文索引转换为段落索引"""
        pre, now = 0, -GRID_PER_ROW  # 首段考虑标题行
        for i in range(len(self.paras)):
            p = self.paras[i]
            pre = now if now > 0 else 0
            now += len(p.text) + 1  # 原全文索引考虑了/n的长度为1,此处补上来统一计算
            if now > pos_start >= pre:
                start_index = pos_start - pre + 2
                end_index = pos_end - pre + 2 - 1  # pos_start/end遵循左闭右开, 此处减一来指向最后一个有效元素
                if i == 0:
                    start_index += GRID_PER_ROW
                    end_index += GRID_PER_ROW
                return i, start_index // GRID_PER_ROW, start_index % GRID_PER_ROW, end_index // GRID_PER_ROW, end_index % GRID_PER_ROW
        return -1, -1, -1, -1, -1


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


class SideBar:
    def __init__(self, para, row, col, kind, tag, content, color):
        """
        :param para: 开始的段落
        :param row: 开始的行号
        :param col: 开始的列号
        :param kind: 类型
        :param tag: 标签
        :param content: 文字内容
        """
        self.para = para
        self.row = row
        self.col = col
        self.kind = kind
        self.tag = tag
        self.content = content
        self.color = color


def sort_sidebar(sidebars: list[SideBar]) -> list[SideBar]:
    """
    按 para, row, col 升序排列 SideBar 列表，
    如果 para, row, col 相同，则合并为一个元素：
    - kind, tag, content, color 用空格拼接
    """
    # 先排序
    sorted_sidebars = sorted(
        sidebars,
        key=lambda sb: (sb.para, sb.row, sb.col)
    )

    # 合并相同 (para, row, col) 的元素
    merged_sidebars = []
    for key, group in groupby(sorted_sidebars, key=lambda sb: (sb.para, sb.row, sb.col)):
        group_list = list(group)
        if len(group_list) == 1:
            merged_sidebars.append(group_list[0])
        else:
            # 合并第一个元素，其他属性拼接
            first = group_list[0]
            merged = SideBar(
                para=first.para,
                row=first.row,
                col=first.col,
                kind=" ".join(sb.kind for sb in group_list),
                tag=" ".join(sb.tag for sb in group_list),
                content=" ".join(sb.content for sb in group_list),
                color=first.color,
            )
            merged_sidebars.append(merged)

    return merged_sidebars


if __name__ == '__main__':
    with open('../asset/example.json', encoding='utf-8') as f:
        row_data = json.load(f)

    e = MicroEvaluationBuilder.build(row_data)
    r = Render("一场有趣的投篮游戏",
               "今天的阳光明媚，小鸟在树间欢快地歌唱，校园里一片生机勃勃。午休时，我们班的同学们聚集在操场上，准备进行一场有趣的投篮游戏。\n我们首先分成了两队，一队是蓝队，另一队是红队。蓝队的队员有我、小明和小华，红队则由小丽、小杰和小雨组成。比赛规则很简单，每人轮流投篮，看哪队投进去的篮球最多，最后得分高的队伍获胜。游戏开始前，我们都迫不及待想要展示自己的投篮技术。\n我第一个上场，心里有些紧张，但我告诉自己要放轻松。当我拿起篮球站在三分线外时，心里默念着：\"一定要投进去！\"我深吸一口气，认真地瞄准篮筐，轻轻一抛，篮球在空中划出一个优美的弧线，终于\"咚\"地一声进了篮筐！我兴奋地挥舞起双手，队友们也为我欢呼鼓掌。\n接下来的轮到小明和小华，他们也都非常出色，轮番投中多个球，使蓝队的分数不断攀升。红队的小丽投篮技术也很不错，虽然一开始有些失误，但她很快调整状态，接连投中几球，为红队追赶分数。\n随着比赛的进行，大家的气氛越来越热烈，操场上充满了欢声笑语。有的同学为自己的队友加油打气，有的则在一旁跃跃欲试。突然，小杰的投篮时机把握得非常好，他一连投中了三球，红队的分数迅速上涨，让我们感受到了一些压力。\n比赛进入了尾声，我和队友们迅速商量战术，决定增加配合，尽量打好每一次投篮。最后的几轮，我和小明默契地传球，终于又得到了几分。经过激烈的角逐，最后的比分是蓝队35分，红队30分，蓝队获得了胜利。\n虽然红队输掉了比赛，但大家都十分开心。我们一起庆祝，享受着这个愉快的时刻。在游戏结束后，我们互相祝贺，也约定下次再来挑战。今天的投篮游戏不仅锻炼了我们的身体，更让我们体会到了友谊和团队协作的重要性。\n这场投篮游戏让我留下了深刻的印象，我希望以后还能有更多这样的活动，让我们的校园生活更加丰富多彩！",
               e)
    r.evalu_visualize()
