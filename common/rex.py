from flask import jsonify

from common.error import BizException

"""
response_util 响应工具类
用于向前端返回 JSON 类型的响应。
"""


def succeed(payload, code=0, msg="success"):
    # 继承 Response 的自定义类型
    if isinstance(payload, Response):
        return jsonify({"code": code, "msg": msg, "payload": payload.to_dict()})
    # 基本类型
    else:
        return jsonify({"code": code, "msg": msg, "payload": payload})


def fail(payload, code=999, msg="unknown error"):
    # 继承 Response 的自定义类型
    if isinstance(payload, Response):
        return jsonify({"code": code, "msg": msg, "payload": payload.to_dict()})
    # BizException 自定义异常
    elif isinstance(payload, BizException):
        return jsonify({"code": payload.code, "msg": payload.msg})
    # 内嵌异常
    elif isinstance(payload, Exception):
        return jsonify({"code": code, "msg": msg, "payload": str(payload)})
    # 基本类型
    else:
        return jsonify({"code": code, "msg": msg, "payload": payload})


class Response:
    """
    确保所有作为响应的返回值都可以被序列化
    """

    def to_dict(self):
        # 抽象方法，需要在子类中实现，否则默认抛出未实现异常
        raise NotImplementedError
