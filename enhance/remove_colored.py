import cv2
import numpy as np


def remove_colored_marks(img):
    """
    清除红色、绿色、蓝色痕迹（教师批改、纸张线框）
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 红色范围（两个区间）
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # 绿色范围
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([90, 255, 255])

    # 蓝色范围（可选）
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])

    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # 合并所有干扰颜色的mask
    full_mask = mask_red | mask_green | mask_blue

    # 将颜色区域“涂白”
    result = img.copy()
    result[full_mask > 0] = [255, 255, 255]
    return result
