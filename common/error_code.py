from enum import Enum


class ErrorCode(Enum):
    """
    ErrorCode 错误码枚举类
    业务过程中遇到并抛出的业务异常，需要在这里定义好错误码和错误信息的枚举项
    """
    # ROI Extract相关
    DEFAULT_ROI_EXTRACT = (1000, "ROI Extract Error")

    # Image Enhance相关
    DEFAULT_IMAGE_ENHANCE = (2000, "Image Enhance Error")

    # OCR相关
    DEFAULT_OCR = (3000, "OCR Error")

    # Evaluate相关
    DEFAULT_EVALUATE = (4000, "Evaluate Error")

    # Render 相关
    DEFAULT_RENDER = (5000, "Render Error")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
