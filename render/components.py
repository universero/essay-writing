from itertools import groupby

"""
components.py 页面组成元素及相关方法
"""


class Para:
    def __init__(self, text, rows, text_start, text_end, bar_rows, bar_content, bar_start, bar_end):
        """
        :param text: 本段内容
        :param rows: 本段行数
        :param text_start: 本段段落内容开始行像素
        :param text_end: 本段段落内容结束行像素
        :param bar_rows: 本段段评行数
        :param bar_content: 本段段评内容
        :param bar_start: 本段段评开始行像素
        :param bar_end: 本段段评结束行像素
        """
        self.text = text
        self.rows = rows
        self.text_start = text_start
        self.text_end = text_end
        self.bar_rows = bar_rows
        self.bar_content = bar_content
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
    sorted_sidebars = sorted(sidebars, key=lambda sb: (sb.para, sb.row, sb.col))
    # 合并相同 (para, row, col) 的元素
    merged_sidebars = []
    for key, group in groupby(sorted_sidebars, key=lambda sb: (sb.para, sb.row, sb.col)):
        group_list = list(group)
        if len(group_list) == 1:
            merged_sidebars.append(group_list[0])
        else:
            # 合并第一个元素，其他属性拼接（去重）
            first = group_list[0]
            # 合并 kind，去重
            merged_kind = "，".join(set(sb.kind for sb in group_list))
            # 合并 tag，去重
            merged_tag = "，".join(set(sb.tag for sb in group_list))
            # 合并 content（不去重）
            merged_content = " ".join(sb.content for sb in group_list)
            merged = SideBar(
                para=first.para, row=first.row, col=first.col,
                kind=merged_kind, tag=merged_tag, content=merged_content, color=first.color,
            )
            merged_sidebars.append(merged)
    return merged_sidebars
