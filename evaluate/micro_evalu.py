"""
evaluation
文件中定义了 Micro 版本批改结果以及相关的子类型
字段构造的过程由 EvaluationBuilder 实现
"""
from common.rex import Response


class MicroEvaluation(Response):
    def __init__(self):
        self.comments = self.Comments()  # 段落点评
        self.content = self.Content()  # 内容点评
        self.counting = self.Counting()  # 统计信息
        self.expression = self.Expression()  # 表达点评
        self.grammar = self.Grammar()  # 语法点评
        self.handwriting = self.Handwriting()  # 手写点评
        self.highlights = self.Highlights()  # 亮点
        self.relevance = self.Relevance()  # 主题关联性
        self.score = 0  # 得分
        self.score_absolute = 0.0  # 绝对得分
        self.score_ori = 0  # 原始得分
        self.score_str = ""  # 得分等第
        self.score_str_ori = ""  # 原始得分等第

    def to_dict(self):
        """序列化为JSON"""

        def convert(obj):
            if isinstance(obj, (str, int, float, bool)):
                return obj
            if obj is None:
                return None
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            if hasattr(obj, '__dict__'):
                return {
                    key: convert(value)
                    for key, value in obj.__dict__.items()
                    if not key.startswith('_')
                }
            return str(obj)

        ch_data = convert(self)
        return ch_data

    class Comments:
        """段落点评"""

        def __init__(self):
            # 分段落点评
            self.paragraph_comments = []
            # 段落总评
            self.passage_comments = ""

    class Content:
        """内容评价"""

        def __init__(self):
            self.comments = ""
            self.score = 0
            self.score_str = ""

    class Counting:
        """统计指标"""

        def __init__(self):
            self.adj_adv_num = 0
            self.char_num = 0
            self.dieci_num = 0
            self.fluency = 0.0
            self.grammar_mistake_num = 0
            self.highlight_sents_num = 0
            self.idiom_num = 0
            self.noun_type_num = 0
            self.para_num = 0
            self.sent_num = 0
            self.unique_word_num = 0
            self.verb_type_num = 0
            self.word_num = 0
            self.written_mistake_num = 0

    class Expression:
        """表达评价"""

        def __init__(self):
            self.comments = ""
            self.score = 0
            self.score_str = ""

    class Grammar:
        """语法分析"""

        def __init__(self):
            self.grammar_sentence = []
            # 病句
            self.sick_sentence = []
            # 标点和字词错误
            self.typo = []
            # 错别字
            self.wording_error = []

        class SickSentence:
            def __init__(self):
                self.end_pos = 0
                self.ori = ""
                self.revised = ""
                self.score = 0.0
                self.start_pos = 0
                self.type = ""

        class Typo:
            def __init__(self):
                self.end_pos = 0
                self.extra = ""
                self.ori = ""
                self.revised = ""
                self.start_pos = 0
                self.type = ""

    class Handwriting:
        """书写评价"""

        def __init__(self):
            self.comments = ""
            self.score = -1
            self.score_str = ""

    class Highlights:
        """亮点"""

        def __init__(self):
            # 好词
            self.advance_words = []
            self.descriptive = []
            self.logic_words = []
            # 修辞
            self.rhetoric = []

        class AdvanceWord:
            def __init__(self):
                self.end_pos = 0
                self.memo = {}
                self.start_pos = 0
                self.type = ""

        class RhetoricItem:
            def __init__(self):
                self.end_pos = 0
                self.memo = {}
                self.start_pos = 0
                self.type = ""
                self.types = []

    class Relevance:
        """切题评价"""

        def __init__(self):
            self.comments = ""
            self.score = 0
            self.score_str = ""
