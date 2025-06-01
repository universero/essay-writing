import cv2
from remove_colored import remove_colored_marks
from contrast import enhance_contrast
from smoothing import smooth_image
from binarize import binarize_image


def enhance_image(image):
    """
    图像增强主流程：
    1. 清除干扰色（红色批改、绿色/蓝色边框）
    2. 灰度转换
    3. 对比度增强
    4. 图像平滑
    5. 图像二值化
    返回白底黑字的增强图像
    """
    # Step 1: 清理红色、绿色、蓝色标记
    cleaned = remove_colored_marks(image)

    # Step 2: 转换为灰度图
    gray = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)

    # Step 3: 对比度增强（灰度变化法）
    contrast = enhance_contrast(gray)

    # Step 4: 图像平滑（如中值滤波）
    smooth = smooth_image(contrast)

    # Step 5: 二值化
    binary = binarize_image(smooth)

    return binary
