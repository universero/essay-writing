from requests import Response

from error_code import ErrorCode


class BizException(Exception, Response):
    """
    BizException 业务异常类
    用于处理业务相关异常。当运行过程中出现业务相关的异常时，需要抛出对应的业务异常。
    """

    def __init__(self, code: int, msg: str):
        """
        构造函数
        :param code: 错误码
        :param msg: 消息内容
        """
        super().__init__(msg)
        self.code = code
        self.msg = msg

    @classmethod
    def error(cls, error_code: ErrorCode) -> "BizException":
        """
        从 ErrorCode 枚举类创建 BizException 实例
        :param error_code: ErrorCode 枚举类的实例
        :return: BizException 对应的业务异常类
        """
        return cls(error_code.code, error_code.msg)

    def to_dict(self) -> dict:
        """
        将 BizException 实例的属性转换为字典
        :return: 包含 code 和 msg 的字典
        """
        return {
            'code': self.code,
            'msg': self.msg,
        }
