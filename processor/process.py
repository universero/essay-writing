import base64
import os
from glob import glob

import cv2
import numpy as np
from flask import Blueprint, request

from common import rex

bp = Blueprint('processor', __name__)

# 文字灰度阈值
text_threshold = 170

# 红色范围
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 50, 50])
upper_red2 = np.array([180, 255, 255])
# 蓝色范围
lower_blue = np.array([100, 50, 50])
upper_blue = np.array([140, 255, 255])


# 通过连通域去除噪声
def connect_clean(img, min_area):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
    valid_labels = np.where(stats[1:, cv2.CC_STAT_AREA] >= min_area)[0] + 1
    return np.isin(labels, valid_labels).astype(np.uint8) * 255


def process_core(img: 'Mat | ndarray[Any, dtype] | UMat'):
    """
    输入参数为opencv图片，输出参数也为opencv图片
    """
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 创建红色和蓝色mask
    mask_red = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    # 合并红色和蓝色
    mask_combined = cv2.bitwise_or(mask_red, mask_blue)

    # 用周围像素填充红色和蓝色区域
    img_cleaned = cv2.inpaint(img, mask_combined, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # 转换为灰度图
    gray = cv2.cvtColor(img_cleaned, cv2.COLOR_BGR2GRAY)
    # 自适应二值化
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 5
    )
    # 通过连通域去除细小噪声
    binary = connect_clean(binary, 50)

    # 形态学去噪
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 开运算去噪
    closed = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    # 闭运算连接文字
    closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)
    # 连通域过滤
    clean_mask = connect_clean(closed, 50)

    # 形态学去噪
    kernel = np.ones((3, 3), np.uint8)
    reconstructed = cv2.morphologyEx(clean_mask, cv2.MORPH_DILATE, kernel, iterations=1)
    final_mask = cv2.bitwise_and(reconstructed, binary)
    # 黑白反转
    final = cv2.bitwise_not(final_mask)

    # 只保留大于阈值的部分
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

            _, buffer = cv2.imencode('.jpg', processed_img)
            result.append(base64.b64encode(buffer).decode('utf-8'))
        return rex.succeed(result)
    except Exception as e:
        return rex.fail(e)


# 单张处理本地文件
def process_local(input_path, output_path):
    img = cv2.imread(input_path)
    output = process_core(img)
    cv2.imwrite(output_path, output)


# 批量处理本地文件
def process_locals(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    # 获取文件夹中所有图片文件
    image_files = glob(os.path.join(input_folder, '*.jpg')) + glob(os.path.join(input_folder, '*.jpeg')) + glob(
        os.path.join(input_folder, '*.png'))
    # 处理每张图片
    for input_path in image_files:
        # 构造输出路径
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_folder, f"processed_{filename}")
        # 处理图片
        process_local(input_path, output_path)
        print(f"已处理: {input_path.replace(os.sep, '/')} -> {output_path.replace(os.sep, '/')}")


# 本地测试用
if __name__ == "__main__":
    input_image = "../asset/process/IMG_0513.jpg"  # 输入图片路径
    output_image = "../asset/process/new2.jpg"  # 输出图片路径
    process_local(input_image, output_image)

    # input_folder = r"../locator/resource/dataset/train/images"  # 输入文件夹路径
    # output_folder = r"../asset/processed"  # 输出文件夹路径
    # process_locals(input_folder, output_folder)
