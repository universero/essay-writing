import cv2
import numpy as np

def enhance_contrast(gray_image):
    """
    使用线性灰度拉伸增强对比度。
    输入：灰度图（uint8）
    输出：增强后的灰度图
    """
    # 获取图像的最小和最大灰度值
    min_val = np.min(gray_image)
    max_val = np.max(gray_image)

    # 防止除以0
    if max_val - min_val < 10:
        return gray_image.copy()

    # 线性拉伸公式
    stretched = (gray_image - min_val) * (255.0 / (max_val - min_val))
    stretched = np.clip(stretched, 0, 255).astype(np.uint8)

    return stretched