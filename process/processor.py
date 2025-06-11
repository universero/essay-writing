import base64
import os
from glob import glob

import cv2
import numpy as np
from flask import Blueprint, request

from common import rex
from process.process_utils import *

"""
process.py 核心图片处理逻辑
"""

bp = Blueprint('process', __name__)


def process_core(img: 'Mat | ndarray[Any, dtype] | UMat'):
    """
    输入参数为opencv图片，输出参数也为opencv图片
    """

    img_cleaned = color_clean(img)

    # 转换为灰度图 (R*77 + G*150 + B*29) >> 8
    gray = cv2.cvtColor(img_cleaned, cv2.COLOR_BGR2GRAY)

    # 自适应二值化, 根据局部区域亮度特性动态调整阈值
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 5
    )

    # 通过连通域去除细小噪声
    binary = connect_clean(binary, 50)

    open_kernel = np.ones((2, 2), np.uint8)
    close_kernel = np.ones((3, 3), np.uint8)
    # 开运算去噪
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, open_kernel)
    # 闭运算连接文字
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, close_kernel)
    # 连通域过滤
    clean = connect_clean(clean, 50)

    # 膨胀操作连接笔画
    kernel = np.ones((3, 3), np.uint8)
    reconstructed = cv2.morphologyEx(clean, cv2.MORPH_DILATE, kernel, iterations=1)
    final_mask = cv2.bitwise_and(reconstructed, clean)
    # 黑白像素反转
    final = cv2.bitwise_not(final_mask)

    # 保留大于文字阈值的部分
    final[final > text_threshold] = 255
    return final


@bp.post('/process')
def process():
    try:
        data = request.json
        if not data or 'images' not in data:
            return rex.fail(None, "no images")
        result = []
        for base64_str in data['images']:
            # 解码base64
            img_bytes = base64.b64decode(base64_str.split(',')[-1])
            np_arr = np.frombuffer(img_bytes, np.uint8)

            # 转换为OpenCV格式
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            processed_img = process_core(img)
            # base64编码
            _, buffer = cv2.imencode('.jpg', processed_img)
            result.append(base64.b64encode(buffer).decode('utf-8'))
        return rex.succeed(result)
    except Exception as e:
        return rex.fail(e)
