import json
import logging

from common import consts
import requests

from builder import EvaluationBuilder
from common.error_code import ErrorCode
from evaluation import Evaluation
from common.error import BizException as Be


class Evaluator:
    """
    evaluate 批改模块的核心类
    处理批改的核心逻辑
    """

    @staticmethod
    def evaluate(title: str, content: str) -> Evaluation:
        """
        调用 beta 批改
        :param title: 作文标题
        :param content: 作文内容
        :return: Evaluation对象
        """
        try:
            response = requests.post(consts.BETA_URL, headers=consts.TEST_HEADER, data=json.dumps({
                "title": title,
                "content": content,
            }))
            evaluation = EvaluationBuilder.build(response.json())
            return evaluation
        except Exception as e:
            logging.error(f"beta 批改失败 {e}")
            raise Be.error(ErrorCode.DEFAULT_EVALUATE)

    @staticmethod
    def test(eva: Evaluation) -> str:
        return EvaluationBuilder.to_pretty_json(eva)
