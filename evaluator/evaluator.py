import json
import logging
from datetime import datetime

import requests
from flask import blueprints, request

from common import consts, rex
from common.error import BizException as Be
from common.error_code import ErrorCode
from evaluator.micro_builder import MicroEvaluationBuilder
from evaluator.micro_evalu import MicroEvaluation
from render.render import Render

bp = blueprints.Blueprint('evaluator', __name__)


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


@bp.post("/evaluate")
def evaluate():
    try:
        title = request.json.get("title")
        content = request.json.get("content")
        result = Evaluator.evaluate(title, content)

        return rex.succeed(result)
    except Exception as e:
        logging.error(f"批改失败, 原因:{e}")
        return rex.fail(e, 999, "批改失败")


@bp.post("/evaluate/render")
def evaluate_render():
    try:
        title = request.json.get("title")
        content = request.json.get("content")

        start = datetime.now()
        result = Evaluator.evaluate(title, content)
        mid = datetime.now()
        logging.info(f"批改用时{mid - start}")
        print(f"{title}\n{content}\n{MicroEvaluationBuilder.to_pretty_json(result)}\n")

        r = Render(title, content, result)
        end = datetime.now()
        logging.info(f"渲染用时{end - mid}")
        return rex.succeed(r.evalu_visualize())
    except Exception as e:
        logging.error(f"批改失败, 原因:{e}")
        return rex.fail(e, 999, "批改失败")
