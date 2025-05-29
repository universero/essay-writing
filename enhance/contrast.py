import cv2
import numpy as np

def enhance_contrast(gray_image):
    """
    这里我选择使用灰度变化法（线性拉伸）而不是方图调整法（直方图均衡）：
    因为作文纸通常光照相对稳定；
        直方图均衡容易增强红色批改痕迹或纸张底纹；灰度变化法更稳定，突出墨迹但不强化红痕或纸纹；
        线性拉伸简单有效、利于后续图像清理与二值化。
    使用线性灰度拉伸进行对比度增强。
    将原始灰度范围线性映射到 [0, 255]。
    """
    min_gray = np.min(gray_image)
    max_gray = np.max(gray_image)

    # 避免除以 0 的异常
    if max_gray - min_gray == 0:
        return gray_image.copy()

    # 线性变换公式：output = (input - min) * 255 / (max - min)
    stretched = ((gray_image - min_gray) * 255 / (max_gray - min_gray)).astype(np.uint8)
    return stretched
