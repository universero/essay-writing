import json
from typing import Any

from evaluator.beta.betaevaluation import BetaEvaluation, AiEvaluation

"""
builder 负责对批改结果进行建造
build: 根据结果map构造一个Evaluation对象
to_pretty_json: 根据Evaluation对象构造带有缩进的json字符串
"""


class BetaEvaluationBuilder:
    """
    建造者模式实现复杂Evaluation对象的构造
    """

    @staticmethod
    def build(data: dict) -> BetaEvaluation:
        """主构建入口"""
        evaluation = BetaEvaluation()
        BetaEvaluationBuilder._build_basic_info(data, evaluation)
        BetaEvaluationBuilder._build_essay_info(data, evaluation)
        BetaEvaluationBuilder._build_ai_evaluation(data, evaluation)
        return evaluation

    @staticmethod
    def _build_basic_info(data: dict, target: BetaEvaluation):
        """构建基础信息"""
        target.title = data.get("title", "")
        target.text = data.get("text", [])

    @staticmethod
    def _build_essay_info(data: dict, target: BetaEvaluation):
        """构建作文信息"""
        essay_info = data.get("essayInfo", {})
        target.essayInfo.essayType = essay_info.get("essayType", "")
        target.essayInfo.grade = essay_info.get("grade", 1)

        # 构建统计信息
        counting_data = essay_info.get("counting", {})
        for key, value in counting_data.items():
            if hasattr(target.essayInfo.counting, key):
                setattr(target.essayInfo.counting, key, value)

    @staticmethod
    def _build_ai_evaluation(data: dict, target: BetaEvaluation):
        """构建AI评价部分"""
        ai_eval_data = data.get("aiEvaluation", {})
        ai_eval = target.aiEvaluation

        # 构建各子模块
        BetaEvaluationBuilder._build_model_version(ai_eval_data.get("modelVersion", {}), ai_eval.modelVersion)
        BetaEvaluationBuilder._build_overall_eval(ai_eval_data.get("overallEvaluation", {}), ai_eval.overallEvaluation)
        BetaEvaluationBuilder._build_fluency_eval(ai_eval_data.get("fluencyEvaluation", {}), ai_eval.fluencyEvaluation)
        BetaEvaluationBuilder._build_word_sentence_eval(ai_eval_data.get("wordSentenceEvaluation", {}),
                                                        ai_eval.wordSentenceEvaluation)
        BetaEvaluationBuilder._build_expression_eval(ai_eval_data.get("expressionEvaluation", {}),
                                                     ai_eval.expressionEvaluation)
        BetaEvaluationBuilder._build_suggestion_eval(ai_eval_data.get("suggestionEvaluation", {}),
                                                     ai_eval.suggestionEvaluation)
        BetaEvaluationBuilder._build_paragraph_evals(ai_eval_data.get("paragraphEvaluations", []),
                                                     ai_eval.paragraphEvaluations)

    @staticmethod
    def _build_model_version(data: dict, target: AiEvaluation.ModelVersion):
        target.name = data.get("name", "")
        target.version = data.get("version", "")

    @staticmethod
    def _build_overall_eval(data: dict, target: AiEvaluation.OverallEvaluation):
        target.topicRelevanceScore = data.get("topicRelevanceScore", 0)
        target.description = data.get("description", "")

    @staticmethod
    def _build_fluency_eval(data: dict, target: AiEvaluation.FluencyEvaluation):
        target.fluencyScore = data.get("fluencyScore", 0)
        target.fluencyDescription = data.get("fluencyDescription", "")

    @staticmethod
    def _build_word_sentence_eval(data: dict, target: AiEvaluation.WordSentenceEvaluation):
        """构建词句评价的三维嵌套结构"""
        target.wordSentenceScore = data.get("wordSentenceScore", 0)
        target.wordSentenceDescription = data.get("wordSentenceDescription", "")

        # 处理段落维度
        for para_data in data.get("sentenceEvaluations", []):
            para_evaluations = []
            # 处理句子维度
            for sent_data in para_data:
                sentence_eval = AiEvaluation.WordSentenceEvaluation.SentenceEvaluation()
                BetaEvaluationBuilder._build_sentence_eval(sent_data, sentence_eval)
                para_evaluations.append(sentence_eval)
            target.sentenceEvaluations.append(para_evaluations)

    @staticmethod
    def _build_sentence_eval(data: dict, target: AiEvaluation.WordSentenceEvaluation.SentenceEvaluation):
        """构建单句评价"""
        target.isGoodSentence = data.get("isGoodSentence", False)
        target.label = data.get("label", "")
        target.type = data.get("type", {})

        # 构建词语评价
        for word_data in data.get("wordEvaluations", []):
            word_eval = AiEvaluation.WordSentenceEvaluation.SentenceEvaluation.WordEvaluation()
            word_eval.span = word_data.get("span", [])
            word_eval.ori = word_data.get("ori", "")
            word_eval.revised = word_data.get("revised", "")
            word_eval.type = word_data.get("type", {})
            target.wordEvaluations.append(word_eval)

    @staticmethod
    def _build_expression_eval(data: dict, target: AiEvaluation.ExpressionEvaluation):
        """处理字段名称差异"""
        target.expressionScore = data.get("expressionScore", 0)
        # 注意JSON字段名与类属性名的差异
        target.expressionDescription = data.get("expressDescription", data.get("expressionDescription", ""))

    @staticmethod
    def _build_suggestion_eval(data: dict, target: AiEvaluation.SuggestionEvaluation):
        target.suggestionDescription = data.get("suggestionDescription", "")

    @staticmethod
    def _build_paragraph_evals(data: list, target: list):
        """构建段落评价列表"""
        for para_data in data:
            para_eval = AiEvaluation.ParagraphEvaluation()
            para_eval.paragraphIndex = para_data.get("paragraphIndex", 0)
            para_eval.content = para_data.get("content", "")
            target.append(para_eval)

    @staticmethod
    def to_pretty_json(evaluation: 'BetaEvaluation', indent: int = 2) -> str:
        """
        将Evaluation对象转换为美观的JSON字符串

        :param evaluation: 需要序列化的Evaluation对象
        :param indent: 缩进空格数，默认2
        :return: 格式化的JSON字符串
        """

        def convert(obj: Any) -> Any:
            """递归转换对象为可序列化类型"""
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}

            # 处理自定义类对象
            if hasattr(obj, '__dict__'):
                # 过滤掉特殊属性和私有属性
                filtered_dict = {
                    key: convert(value)
                    for key, value in obj.__dict__.items()
                    if not key.startswith('_')
                }
                # 处理嵌套类中的内部类实例
                for cls in type(obj).__mro__:
                    if cls.__name__ in filtered_dict:
                        filtered_dict.update(convert(filtered_dict[cls.__name__]))
                        del filtered_dict[cls.__name__]
                return filtered_dict
            return str(obj)  # 保底处理无法识别的类型

        # 构建根字典结构
        result = {
            "title": evaluation.title,
            "text": evaluation.text,
            "essayInfo": convert(evaluation.essayInfo),
            "aiEvaluation": convert(evaluation.aiEvaluation)
        }

        # 生成带缩进的JSON
        return json.dumps(
            result,
            indent=indent,
            ensure_ascii=False,
            separators=(',', ': ')
        )


# single-test
if __name__ == '__main__':
    # 读取原始数据
    with open('../../asset/evaluator/example.json', encoding='utf-8') as f:
        raw_data = json.load(f)
    # 使用建造者构建对象
    eva = BetaEvaluationBuilder.build(raw_data)
    # 验证构建结果
    print(eva)
    print(BetaEvaluationBuilder.to_pretty_json(eva))
