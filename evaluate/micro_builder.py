import json

from evaluate.micro_evalu import MicroEvaluation

"""
micro_builder.py micro版本批改结果构造者
"""

# counting中相关字段
fields = [
    'adj_adv_num', 'char_num', 'dieci_num', 'fluency',
    'grammar_mistake_num', 'highlight_sents_num', 'idiom_num',
    'noun_type_num', 'para_num', 'sent_num', 'unique_word_num',
    'verb_type_num', 'word_num', 'written_mistake_num'
]


class MicroEvaluationBuilder:
    """建造者根据json向类中填入相应数据"""

    @staticmethod
    def build(data: dict) -> MicroEvaluation:
        evaluation = MicroEvaluation()
        data = data.get("ch", {})
        # 构建各级结构
        MicroEvaluationBuilder._build_comments(data, evaluation.comments)
        MicroEvaluationBuilder._build_content(data, evaluation.content)
        MicroEvaluationBuilder._build_counting(data, evaluation.counting)
        MicroEvaluationBuilder._build_expression(data, evaluation.expression)
        MicroEvaluationBuilder._build_grammar(data, evaluation.grammar)
        MicroEvaluationBuilder._build_handwriting(data, evaluation.handwriting)
        MicroEvaluationBuilder._build_highlights(data, evaluation.highlights)
        MicroEvaluationBuilder._build_relevance(data, evaluation.relevance)

        # 设置分数
        evaluation.score = data.get("score", 0)
        evaluation.score_absolute = data.get("score_absolute", 0.0)
        evaluation.score_ori = data.get("score_ori", 0)
        evaluation.score_str = data.get("score_str", "?")
        evaluation.score_str_ori = data.get("score_str_ori", "?")
        return evaluation

    @staticmethod
    def _build_comments(data: dict, target: MicroEvaluation.Comments):
        target.paragraph_comments = data.get("comments", {}).get("paragraph_comments", [])
        target.passage_comments = data.get("comments", {}).get("passage_comments", "")

    @staticmethod
    def _build_content(data: dict, target: MicroEvaluation.Content):
        content_data = data.get("content", {})
        target.comments = content_data.get("comments", "")
        target.score = content_data.get("score", 0)
        target.score_str = content_data.get("score_str", "?")

    @staticmethod
    def _build_counting(data: dict, target: MicroEvaluation.Counting):
        counting_data = data.get("counting", {})
        for field in fields:
            if field in counting_data:
                setattr(target, field, counting_data[field])

    @staticmethod
    def _build_expression(data: dict, target: MicroEvaluation.Expression):
        expr_data = data.get("expression", {})
        target.comments = expr_data.get("comments", "")
        target.score = expr_data.get("score", 0)
        target.score_str = expr_data.get("score_str", "?")

    @staticmethod
    def _build_grammar(data: dict, target: MicroEvaluation.Grammar):
        grammar_data = data.get("grammar", {})

        # 构建病句分析
        target.sick_sentence = [
            MicroEvaluationBuilder._build_sick_sentence(s)
            for s in grammar_data.get("sick_sentence", [])
        ]

        # 构建错别字
        target.typo = [
            MicroEvaluationBuilder._build_typo(t)
            for t in grammar_data.get("typo", [])
        ]

    @staticmethod
    def _build_sick_sentence(data: dict) -> MicroEvaluation.Grammar.SickSentence:
        ss = MicroEvaluation.Grammar.SickSentence()
        ss.end_pos = data.get("end_pos", 0)
        ss.ori = data.get("ori", "")
        ss.revised = data.get("revised", "")
        ss.score = data.get("score", 0.0)
        ss.start_pos = data.get("start_pos", 0)
        ss.type = data.get("type", "")
        return ss

    @staticmethod
    def _build_typo(data: dict) -> MicroEvaluation.Grammar.Typo:
        typo = MicroEvaluation.Grammar.Typo()
        typo.end_pos = data.get("end_pos", 0)
        typo.extra = data.get("extra", "")
        typo.ori = data.get("ori", "")
        typo.revised = data.get("revised", "")
        typo.start_pos = data.get("start_pos", 0)
        typo.type = data.get("type", "")
        return typo

    @staticmethod
    def _build_handwriting(data: dict, target: MicroEvaluation.Handwriting):
        hw_data = data.get("handwriting", {})
        target.comments = hw_data.get("comments", "Fail to check handwritting")
        target.score = hw_data.get("score", -1)
        target.score_str = hw_data.get("score_str", "?")

    @staticmethod
    def _build_highlights(data: dict, target: MicroEvaluation.Highlights):
        hl_data = data.get("highlights", {})

        # 构建高级词汇
        target.advance_words = [
            MicroEvaluationBuilder._build_advance_word(aw)
            for aw in hl_data.get("advance_words", [])
        ]

        # 构建修辞手法
        target.rhetoric = [
            MicroEvaluationBuilder._build_rhetoric(r)
            for r in hl_data.get("rhetoric", [])
        ]

    @staticmethod
    def _build_advance_word(data: dict) -> MicroEvaluation.Highlights.AdvanceWord:
        aw = MicroEvaluation.Highlights.AdvanceWord()
        aw.end_pos = data.get("end_pos", 0)
        aw.memo = data.get("memo", {})
        if isinstance(aw.memo, str):
            aw.memo = json.loads(aw.memo.replace("'", '"'))
        aw.start_pos = data.get("start_pos", 0)
        aw.type = data.get("type", "")
        return aw

    @staticmethod
    def _build_rhetoric(data: dict) -> MicroEvaluation.Highlights.RhetoricItem:
        ri = MicroEvaluation.Highlights.RhetoricItem()
        ri.end_pos = data.get("end_pos", 0)
        ri.memo = data.get("memo", {})
        ri.start_pos = data.get("start_pos", 0)
        ri.type = data.get("type", "")
        ri.types = data.get("types", [])
        return ri

    @staticmethod
    def _build_relevance(data: dict, target: MicroEvaluation.Relevance):
        rel_data = data.get("relevance", {})
        target.comments = rel_data.get("comments", "")
        target.score = rel_data.get("score", 0)
        target.score_str = rel_data.get("score_str", "?z")

    @staticmethod
    def to_pretty_json(evaluation: MicroEvaluation) -> str:
        """序列化方法适配新版结构"""

        return json.dumps(
            {"ch": evaluation.to_dict()},
            indent=2,
            ensure_ascii=False,
            separators=(',', ': ')
        )


if __name__ == '__main__':
    # 测试用例
    with open('../asset/evaluator/example.json', encoding='utf-8') as f:
        raw_data = json.load(f)

    e = MicroEvaluationBuilder.build(raw_data)
    print(MicroEvaluationBuilder.to_pretty_json(e))
