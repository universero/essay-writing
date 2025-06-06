from flask import request, Blueprint
import base64
import cv2
import numpy as np


from common import rex
from processor.enhance.enhance import enhance_image

# 如果你还要加图像恢复（可选）:
# from processor.restore.restore_spatial import restore_spatial
# 或者使用频域方法：
# from processor.restore.restore_freq import restore_freq

bp = Blueprint("processor", __name__)


def read_image_from_file(file_storage):
    """将前端上传的 FileStorage 文件转为 OpenCV 图像"""
    file_bytes = file_storage.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image


def encode_image_to_base64(image):
    """将 OpenCV 图像编码为 base64 字符串"""
    _, buffer = cv2.imencode('.jpg', image)
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str


@bp.post("/process")
def process():
    imgs = request.files.getlist("images")
    result = []

    for file_storage in imgs:
        # Step 1: 读取原始图像
        image = read_image_from_file(file_storage)

        # Step 2: 图像增强
        enhanced = enhance_image(image)

        # Step 3（可选）: 图像恢复（例如空间域复原模糊图像）
        # restored = restore_spatial(enhanced)

        # Step 4: 编码为 base64
        encoded = encode_image_to_base64(enhanced)  # or encode_image_to_base64(restored)

        result.append(encoded)

    return rex.succeed(result)
