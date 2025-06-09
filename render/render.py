import base64
import json
from io import BytesIO

from PIL import Image, ImageDraw
from flask import Blueprint, request

from common import rex
from common.consts import ZH_NO
from evaluate.micro_builder import MicroEvaluationBuilder
from evaluate.micro_evalu import MicroEvaluation
from render.components import Para, SideBar, sort_sidebar
from render.config import *
from render.draw_utils import *

"""
render.py 批改结果渲染及相关flask接口
核心工作包括作文纸生成, 批注痕迹绘制, A4大小切割
"""

bp = Blueprint("render", __name__)


class Render:
    """
    Render 负责批改结果渲染的核心类
    """

    def __init__(self, title: str, content: str, evalu: MicroEvaluation):
        """
        初始化
        :param title: 作文标题
        :param content: 作文内容分段\
        :param evalu:  批改结果
        """
        self.title = title
        self.content = content
        self.paras = []  # 分段结果
        self.evalu = evalu
        self.todo_sidebar = []  # 需要绘制的侧边栏项
        self.img = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), "white")
        self.imgs = []  # 分页结果
        self.comment_start = None
        self.comment_end = None

    def evalu_visualize(self):
        """可视化批改结果"""
        self.deal_title()  # 处理标题
        self.divide_paras()  # 划分段落
        self.paras_base()
        self.paras_number()
        self.paras_comments()
        # self.grammar_sentences() TODO
        self.sick_sentences()
        self.typo()
        self.advance_words()
        self.rhetoric()
        self.sidebar()
        self.essay_comment()
        with BytesIO() as buffer:
            self.img.save(buffer, format="PNG")
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

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
            text_start = MARGIN_TOP
            if rows != 0:
                text_start = self.paras[i - 1].bar_end + MID_BAR_MARGIN_TOP
            text_end = text_start + row * (GRID_HEIGHT + GAP_BAR_HEIGHT)
            bar_content = html_strip(self.evalu.comments.paragraph_comments[i])
            bar_rows = count_multi_row(bar_content, MID_BAR_PER_ROW)
            bar_start = text_end + MID_BAR_MARGIN_TOP
            bar_end = bar_start + MID_BAR_HEIGHT
            if bar_rows > 2:  # 当段评超过两行时应该扩充长度
                bar_end += (MID_BAR_TEXT_GAP + MID_BAR_TEXT_SIZE) * (bar_rows - 2)
            self.paras.append(Para(paras[i], row, text_start, text_end, bar_rows, bar_content, bar_start, bar_end))
            rows += row
        mid_bar_height_total = len(self.paras) * (MID_BAR_MARGIN_TOP * 2) + sum(
            map(lambda para: para.bar_end - para.bar_start, self.paras))
        # 根据文章总数构建页面长度
        page_number = (rows * (GRID_HEIGHT + GAP_BAR_HEIGHT) + mid_bar_height_total) // PAGE_HEIGHT + 2
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
                draw.rectangle([(GRID_WIDTH * i + MARGIN_LEFT, row),
                                (GRID_WIDTH * (i + 1) + MARGIN_LEFT, row + GRID_HEIGHT)],
                               outline="black", width=GRID_LINE)
                content = " "
                if number != 0 and len(text) > idx - 2 >= 0:
                    content = text[idx - 2]
                elif number == 0 and idx < GRID_PER_ROW:  # 标题行
                    content = text[idx]
                elif number == 0 and GRID_PER_ROW <= idx - 2 < len(text):  # 第一段非标题行
                    content = text[idx - 2]
                draw.text((GRID_WIDTH * i + MARGIN_LEFT + GRID_WIDTH // 2, row + GRID_HEIGHT - GRID_HEIGHT // 2),
                          content, font=TEXT_FONT, fill="black", anchor="mm")
                idx += 1
            # 绘制两行间隔
            draw.rectangle([(MARGIN_LEFT, row + GRID_HEIGHT,),
                            (MARGIN_LEFT + GAP_BAR_WIDTH, row + GRID_HEIGHT + GAP_BAR_HEIGHT)],
                           outline="black", width=GAP_LINE)
            row += GRID_HEIGHT + GAP_BAR_HEIGHT
        # 将每段的外圈加粗以保证视觉效果
        # 上
        draw.line([(MARGIN_LEFT, para.text_start - GRID_LINE // 2),
                   (MARGIN_LEFT + GAP_BAR_WIDTH, para.text_start - GRID_LINE // 2)],
                  fill="black", width=GRID_LINE)
        # 下
        draw.line([(MARGIN_LEFT, para.text_end + GAP_LINE // 2),
                   (MARGIN_LEFT + GAP_BAR_WIDTH, row + GAP_LINE // 2)],
                  fill="black", width=GAP_LINE)
        # 左
        draw.line([(MARGIN_LEFT - GRID_LINE // 2, para.text_start),
                   (MARGIN_LEFT - GRID_LINE // 2, para.text_end)],
                  fill="black", width=GAP_LINE)
        # 右
        draw.line([(MARGIN_LEFT + GAP_BAR_WIDTH + GRID_LINE // 2, para.text_start),
                   (MARGIN_LEFT + GAP_BAR_WIDTH + GRID_LINE // 2, para.text_end)],
                  fill="black", width=GAP_LINE)
        # 段落点评位置 TODO 这里只有两行，不是很对
        draw.rounded_rectangle([(MARGIN_LEFT, para.bar_start),
                                (MARGIN_LEFT + MID_BAR_WIDTH, para.bar_end)],
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
            left = MARGIN_LEFT + MID_BAR_MARGIN_LEFT
            upper = self.paras[i].bar_start + MID_BAR_MARGIN_TOP
            draw.text((left, upper), no, font=MID_BAR_FONT, fill=NO_COLOR, anchor="la")
            text = html_strip(self.evalu.comments.paragraph_comments[i])
            # 分行写入段评实际内容
            draw_multi_row_text(draw, text, MID_BAR_PER_ROW, left, upper, MID_BAR_TEXT_SIZE,
                                MID_BAR_TEXT_GAP, EVAL_FONT)

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
                left, right, row = self.get_line_pos(para_no, now_row, start_row, start_col, end_row, end_col)
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
                SideBar(para_no, start_row, start_col, typo.type, "", f"{typo.ori}应改为{typo.revised}", SICK_COLOR))
            self.draw_mask(draw, para_no, start_row, start_col, end_row, end_col, TYPO_MASK_COLOR)
        self.img = Image.alpha_composite(self.img, mask)

    def advance_words(self):
        """好词"""
        mask = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        for words in self.evalu.highlights.advance_words:
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(words.start_pos, words.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, f"好词：{words.type}", words.memo["text"], "",
                        HIGHLIGHT_LINE_COLOR))
            self.draw_mask(draw, para_no, start_row, start_col, end_row, end_col, HIGHLIGHT_MASK_COLOR)
        self.img = Image.alpha_composite(self.img, mask)

    def rhetoric(self):
        """修辞部分"""
        draw = ImageDraw.Draw(self.img)
        for rhetoric in self.evalu.highlights.rhetoric:
            t = rhetoric.type
            if t == "语言":
                continue
            # if len(rhetoric.types) > 0:
            #     t = "，" if t != "" else ""
            #     t += "，".join(rhetoric.types)
            # 全文索引转换为段落索引
            para_no, start_row, start_col, end_row, end_col = self.global_to_paragraph(rhetoric.start_pos,
                                                                                       rhetoric.end_pos)
            self.todo_sidebar.append(
                SideBar(para_no, start_row, start_col, "好句", "，".join(rhetoric.types), "", HIGHLIGHT_LINE_COLOR))
            now_row = start_row
            while now_row <= end_row:
                left, right, row = self.get_line_pos(para_no, now_row, start_row, start_col, end_row, end_col)
                _right = right if now_row < end_row else right - 5 * coefficient
                draw_wavy_line(draw, (left, row), (_right, row), HIGHLIGHT_AMPLITUDE, HIGHLIGHT_WAVELENGTH,
                               HIGHLIGHT_LINE_COLOR, HIGHLIGHT_LINE)
                now_row += 1

    def get_line_pos(self, para_no, now_row, start_row, start_col, end_row, end_col):
        left, right = MARGIN_LEFT, MARGIN_LEFT + GAP_BAR_WIDTH
        if now_row == end_row:
            right = MARGIN_LEFT + GRID_WIDTH * (end_col + 1)
        if now_row == start_row:
            left = MARGIN_LEFT + GRID_WIDTH * start_col
        row = (self.paras[para_no].text_start + (now_row + 1) *
               (GRID_HEIGHT + GAP_BAR_HEIGHT) - GAP_BAR_HEIGHT // 2)
        return left, right, row

    def draw_mask(self, draw, para_no, start_row, start_col, end_row, end_col, color):
        now_row = start_row
        while now_row <= end_row:
            left, right = MARGIN_LEFT, MARGIN_LEFT + GAP_BAR_WIDTH
            if now_row == end_row:
                right = MARGIN_LEFT + GRID_WIDTH * (end_col + 1)
            if now_row == start_row:
                left = MARGIN_LEFT + GRID_WIDTH * start_col
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
        upper, down = self.paras[0].text_start, self.paras[-1].bar_end
        draw.rectangle([(left, upper), (right, down)], outline="black", width=SIDE_BAR_LINE)
        self.todo_sidebar = sort_sidebar(self.todo_sidebar)
        last, left = SIDE_BAR_MARGIN_TOP, PAGE_WIDTH - SIDE_BAR_WIDTH - SIDE_BAR_MARGIN_RIGHT + SIDE_BAR_MARGIN_LEFT
        for i in range(len(self.todo_sidebar)):
            sidebar = self.todo_sidebar[i]
            self.seq(i, sidebar.para, sidebar.row, sidebar.col, sidebar.color)
            para, row = self.paras[sidebar.para], sidebar.row
            upper = para.text_start + row * (GRID_HEIGHT + GAP_BAR_HEIGHT)
            if upper < last:
                upper = last + SIDE_BAR_ITEM_GAP
            # 写入序号和类型
            draw.text((left, upper), f"{str(i + 1)}.{sidebar.kind}", font=SIDE_BAR_ITEM_FONT, fill=sidebar.color,
                      anchor="la")
            # 写入tag
            if sidebar.tag != "":
                upper += SIDE_BAR_TEXT_GAP + SIDE_BAR_ITEM_SIZE
                draw.text((left, upper), sidebar.tag, font=SIDE_BAR_ITEM_FONT, fill=sidebar.color, anchor="la")
            # 分行写入content
            rows = draw_multi_row_text(draw, sidebar.content, SIDE_BAR_PER_ROW, left, upper, SIDE_BAR_TEXT_SIZE,
                                       SIDE_BAR_TEXT_GAP, SIDE_BAR_TEXT_FONT)
            last = upper + (SIDE_BAR_TEXT_SIZE + SIDE_BAR_TEXT_GAP) * rows + SIDE_BAR_ITEM_GAP

    def seq(self, number, para_no, row, col, color):
        """绘制序号标记"""
        draw = ImageDraw.Draw(self.img)
        para = self.paras[para_no]
        x, y = para.text_start + row * (
                GRID_HEIGHT + GAP_BAR_HEIGHT) + GRID_WIDTH // 10, MARGIN_LEFT + GRID_WIDTH * col
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

    def essay_comment(self):
        """各维度总评"""
        texts = [("总评", self.evalu.comments.passage_comments, self.evalu.score_str),
                 ("内容", self.evalu.content.comments, self.evalu.content.score_str),
                 ("表达", self.evalu.expression.comments, self.evalu.expression.score_str),
                 ("主题", self.evalu.relevance.comments, self.evalu.relevance.score_str), ]
        draw = ImageDraw.Draw(self.img)
        start = self.paras[-1].bar_end + ALL_MARGIN_TOP
        left, upper = MARGIN_LEFT + ALL_MARGIN_LEFT, start + ALL_ITEM_GAP
        for i in range(len(texts)):
            (tag, content, score) = texts[i]
            # tag
            draw.circle((left + ALL_ICON_RADIUS, upper + ALL_ICON_RADIUS), ALL_ICON_RADIUS, outline=ALL_COLOR,
                        width=ALL_ICON_WIDTH)
            draw.text((left + 8 * ALL_ICON_RADIUS, upper + ALL_ICON_RADIUS), tag, font=ALL_TAG_FONT, fill=ALL_COLOR,
                      anchor="mm")
            draw.text((left + ALL_WIDTH - ALL_MARGIN_RIGHT, upper + ALL_ICON_RADIUS), score,
                      font=ALL_SCORE_FONT, fill=ALL_COLOR, anchor="mm")
            upper += ALL_TAG_SIZE
            # 分行写入content
            text = html_strip(content)
            rows = draw_multi_row_text(draw, text, ALL_PER_ROW, left, upper, ALL_TEXT_SIZE, ALL_TEXT_GAP,
                                       ALL_TEXT_FONT)
            upper += (ALL_TEXT_SIZE + ALL_TEXT_GAP) * rows + ALL_ITEM_GAP * 3.5
            if i != len(texts) - 1:
                draw_dashed_line(draw, (left, upper - 1.5 * ALL_ITEM_GAP),
                                 (left + ALL_WIDTH - ALL_MARGIN_RIGHT, upper - 1.5 * ALL_ITEM_GAP),
                                 ALL_DASHED_LINE_LEN,
                                 ALL_DASHED_GAP, fill="black", width=ALL_DASHED_LINE)
        draw.rectangle([(MARGIN_LEFT, start), (left + ALL_WIDTH, upper - ALL_ITEM_GAP)], outline="black",
                       width=ALL_LINE)
        self.comment_start, self.comment_end = start, upper - ALL_ITEM_GAP

    def paging(self):
        """
        将长图分割成多个A4大小的页以便于打印
        可拆分位置:  段评开始前, 段评结束后, 行间间隔
        """
        height = self.img.height
        if height <= PAGE_HEIGHT:  # 仅一页
            self.imgs.append(self.img)
            return

        croppable = []  # 维护每一个允许裁剪的位置
        for para in self.paras:
            start = para.text_start
            # 行间间隔
            for i in range(para.rows):
                line_bottom = para.text_start + (i + 1) * (GRID_HEIGHT + GAP_BAR_HEIGHT)
                croppable.append(line_bottom)
            # 段评
            croppable.append(para.bar_start)
            croppable.append(para.bar_end)
        croppable.append(height)
        now, cur, pre = PAGE_HEIGHT - MARGIN_TOP, 0, MARGIN_TOP

        right = PAGE_WIDTH - SIDE_BAR_MARGIN_RIGHT
        left = right - SIDE_BAR_WIDTH

        def cut_one(start_row, end_row):
            page = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), "white")
            page.paste(self.img.crop((0, start_row, PAGE_WIDTH, end_row)), (0, MARGIN_TOP))
            draw = ImageDraw.Draw(page)
            draw.line([(left, MARGIN_TOP), (right, MARGIN_TOP)], fill="black", width=SIDE_BAR_LINE)
            draw.line([(left, end_row - start_row + MARGIN_TOP), (right, end_row - start_row + MARGIN_TOP)],
                      fill="black", width=SIDE_BAR_LINE)
            self.imgs.append(page)

        # 正文部分
        while now < height:
            while cur < len(croppable) and croppable[cur] < now:
                cur += 1
            if cur <= len(croppable):
                cut = croppable[cur - 1]
                cur += 1
                cut_one(pre, cut)
                pre = cut
                now = cut + PAGE_HEIGHT - MARGIN_TOP
            if cur >= len(croppable):
                break

        # 总评部分 (一般不会超过一页)
        leave = self.img.crop((0, self.comment_start, PAGE_WIDTH, self.comment_end))
        if leave.height + self.imgs[-1].height <= PAGE_HEIGHT:  # 可以加到最后一页
            self.imgs[-1].paste(leave, (0, pre))
        else:
            page = Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), "white")
            page.paste(leave, (0, MARGIN_TOP))
            self.imgs.append(page)


@bp.post("/render")
def render():
    data = request.get_json()
    title = data["title"]
    content = data["content"]
    raw = data["raw"]
    e = MicroEvaluationBuilder.build({"ch": raw})
    r = Render(title, content, e)
    return rex.succeed(r.evalu_visualize())


if __name__ == '__main__':
    with open('../asset/evaluator/example.json', encoding='utf-8') as f:
        row_data = json.load(f)

    e = MicroEvaluationBuilder.build(row_data)
    r = Render("鸟巢度假村",
               "中国有许多著名的景点。其中最有特色的要数海南的鸟巢度假村啦！\n金鸟巢度假村座落在海南三亚亚龙湾附近一座山上的森林公园里，这里依山伴海。丛林密布，一栋栋木质的别墅若隐若现地隐藏在热带雨林中。远远望木去，它们真的像一个个可爱的鸟巢呢！\n走进鸟巢后一股清新的空气扑鼻而来。你会想到自己此时也化作一只心鸟，住在森林之中。眼前的景色也会深深地吸引住你。对面的山头云雾缭绕，远处亚龙湾的海面显得异常平静。蓝绿色的海水与天空连成一片。让你仿佛真的身处于一个如梦如幻的人间天堂。\n傍晚时分，天空中呈现出的绚丽奇特景象又会深深地打动你。只见太阳慢慢落山，它把最后一缕余光投向天空。天空被云彩染红了。似乎是着了火。它们变幻莫测，这一朵像一只咆哮的猛虎，随准备向猎物攻击；那一朵上演着故事中的龟兔赛跑的场景。乌龟率先到达了终点。兔子却落在了后面。火烧云装扮着天空，为天空增添了无限艳丽的色彩。夜幕渐渐降临了。天上的星星点起了灯，它们微笑着对大地眨着眼睛。像荷叶上的露珠，也像无暇的钻石。星星们点缀着无边无际的天空，为天空增添了许多生趣。\n山上的夜晚十分宁静。也非常有趣，耳边经常萦绕着快乐的虫鸣声。只要有灯光的地方，各种各样的虫子就飞涌而来。有大大小小的飞蛾，有讨厌的蚊子，还有各种各样的甲虫。它们围着灯火翩翩起舞像是举办一场盛大的狂欢会。\n鸟巢度假村真是一个独一无二充满生趣，美不胜收的度假胜地啊!你是不是也已经陶醉了呢？",
               e)
    r.evalu_visualize()
    # r.img.show()
    r.img.save("../asset/render.png")
    # r.paging()
    # for i in range(len(r.imgs)):
    #     r.imgs[i].save("../asset/render-{}.png".format(i))
