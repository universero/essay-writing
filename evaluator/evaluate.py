import json
import logging

from common import consts
import requests

from common.error_code import ErrorCode
from common.error import BizException as Be
from evaluator.micro_evalu import MicroEvaluation
from evaluator.micro_builder import MicroEvaluationBuilder


class Evaluator:
    """
    evaluator 批改模块的核心类
    处理批改的核心逻辑
    """

    @staticmethod
    def evaluate(title: str, content: str) -> MicroEvaluation:
        """
        调用 beta 批改
        :param title: 作文标题
        :param content: 作文内容
        :return: Evaluation对象
        """
        try:
            response = requests.post(consts.MICRO_URL, headers=consts.TEST_HEADER, data=json.dumps({
                "title": title,
                "text": content,
            }))
            evaluation = MicroEvaluationBuilder.build(response.json())
            return evaluation
        except Exception as e:
            logging.error(f"批改失败 {e}")
            raise Be.error(ErrorCode.DEFAULT_EVALUATE)

    @staticmethod
    def test(eva: MicroEvaluation) -> str:
        return MicroEvaluationBuilder.to_pretty_json(eva)
