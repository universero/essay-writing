import cv2
import numpy as np

def remove_red_marks(image):
    """
    去除图像中的红色区域（如批改痕迹），用周围颜色修复填补。
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    inpainted = cv2.inpaint(image, red_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return inpainted
