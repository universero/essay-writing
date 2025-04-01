"""
evaluation
文件中定义了 Beta 版本批改结果以及相关的子类型
类的定义中不附带字段的 build 过程以免代码过长
字段构造的过程由 EvaluationBuilder 实现
"""


class Evaluation:
    """
    总的批改结果类
    """

    def __init__(self):
        self.title = ""
        self.text = [[]]
        self.essayInfo = EssayInfo()
        self.aiEvaluation = AiEvaluation()


class EssayInfo:
    """
    作文信息
    """

    def __init__(self):
        self.essayType = ""  # 作文类型
        self.grade = 1  # 年级评估
        self.counting = self.Counting()

    class Counting:
        """
        各维度统计信息
        """

        def __init__(self):
            self.adjAdvNum = 0  # 形容词副词数量
            self.charNum = 0  # 字符总数
            self.dieciNum = 0  # 叠词数量
            self.fluency = 0  # 流畅度分数（由GPT2模型评估）
            self.grammarMistakeNum = 0  # 语法错误数量
            self.highlightSentsNum = 0  # 精彩句子数量
            self.idiomNum = 0  # 成语使用数量
            self.nounTypeNum = 0  # 名词类型数量
            self.paraNum = 0  # 段落总数
            self.sentNum = 0  # 句子总数
            self.uniqueWordNum = 0  # 唯一单词数量
            self.verbTypeNum = 0  # 动词类型数量
            self.wordNum = 0  # 总单词数量
            self.writtenMistakeNum = 0  # 书面表达错误数量


class AiEvaluation:
    """
    Beta 版批改结果
    """

    def __init__(self):
        self.modelVersion = self.ModelVersion()
        self.overallEvaluation = self.OverallEvaluation()
        self.fluencyEvaluation = self.FluencyEvaluation()
        self.wordSentenceEvaluation = self.WordSentenceEvaluation()
        self.expressionEvaluation = self.ExpressionEvaluation()
        self.suggestionEvaluation = self.SuggestionEvaluation()
        self.paragraphEvaluations = []  # 段落点评列表

    class ModelVersion:
        """模型版本信息"""

        def __init__(self):
            self.name = ""  # 模型名称（例如：小花狮智能作文批改系统）
            self.version = ""  # 模型版本号（例如：v1.0）

    class OverallEvaluation:
        """总体评价"""

        def __init__(self):
            self.topicRelevanceScore = 0  # 主题相关度评分（0-5分制）
            self.description = ""  # 总体评价描述

    class FluencyEvaluation:
        """流畅度评价"""

        def __init__(self):
            self.fluencyScore = 0  # 流畅度评分（0-5分制）
            self.fluencyDescription = ""  # 流畅度评价描述

    class WordSentenceEvaluation:
        """词句维度评价"""

        def __init__(self):
            self.wordSentenceScore = 0  # 词句维度评分（0-5分制）
            self.wordSentenceDescription = ""  # 词句维度评价
            self.sentenceEvaluations = []  # 三维列表结构：段落-句子-评价项

        class SentenceEvaluation:
            """单句评价"""

            def __init__(self):
                self.isGoodSentence = False  # 是否属于精彩句子
                self.label = ""  # 句子评价标签
                self.type = ""  # 句子类型标识
                self.wordEvaluations = []  # 词语评价列表

            class WordEvaluation:
                """词语级评价"""

                def __init__(self):
                    self.span = []  # 词语位置区间（例如：[3,5]）
                    self.ori = ""  # 原始错误词语
                    self.revised = ""  # 修正后建议
                    self.type = {}  # 错误类型字典（层级分类）

    class ExpressionEvaluation:
        """表达维度评价"""

        def __init__(self):
            self.expressionScore = 0  # 表达评分（0-5分制）
            self.expressionDescription = ""  # 表达维度评价描述

    class SuggestionEvaluation:
        """修改建议"""

        def __init__(self):
            self.suggestionDescription = ""  # 综合修改建议文本

    class ParagraphEvaluation:
        """段落级评价"""

        def __init__(self):
            self.paragraphIndex = 0  # 段落序号（从1开始）
            self.content = ""  # 段落评语内容
