import base64

import cv2
import numpy as np
from flask import request, Blueprint

from common import rex
from processor.enhance.enhance import enhance_image

# 可选：图像恢复模块
# from processor.restore.restore_spatial import restore_spatial

bp = Blueprint("processor", __name__)


def decode_base64_to_image(base64_str: str) -> np.ndarray:
    """
    将 base64 字符串解码为 OpenCV 图像（numpy 数组）
    :param base64_str: 前端传入的 base64 字符串（可带或不带 data:image/... 前缀）
    :return: OpenCV 图像（BGR 格式）
    """
    # 移除可能的头部（如 "data:image/jpeg;base64,"）
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]

    # 解码为字节流
    img_bytes = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)

    # 用 OpenCV 解码图像
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("无效的图片数据")
    return img


def encode_image_to_base64(image: np.ndarray) -> str:
    """
    将 OpenCV 图像编码为 base64 字符串
    :param image: OpenCV 图像（BGR 格式）
    :return: base64 字符串（不带 data:image/... 前缀）
    """
    _, buffer = cv2.imencode('.jpg', image)  # 或 '.png'
    return base64.b64encode(buffer).decode('utf-8')


@bp.post("/process")
def process():
    try:
        # 1. 从请求体中获取 JSON 数据
        data = request.get_json()
        if not data or "images" not in data:
            return rex.fail(400, "请求必须包含 'images' 字段（base64 编码的图片数组）")

        base64_images = data["images"]
        if not isinstance(base64_images, list):
            return rex.fail(400, "'images' 必须是数组")

        result = []
        for base64_str in base64_images:
            # 2. 解码为 OpenCV 图像
            try:
                image = decode_base64_to_image(base64_str)
            except Exception as e:
                return rex.fail(400, f"Base64 解码失败: {str(e)}")

            # 3. 图像增强
            enhanced = enhance_image(image)

            # 4. （可选）图像恢复
            # restored = restore_spatial(enhanced)

            # 5. 重新编码为 base64
            encoded = encode_image_to_base64(enhanced)  # 或 restored
            result.append(encoded)

        return rex.succeed(result)

    except Exception as e:
        return rex.fail(500, f"处理失败: {str(e)}")
