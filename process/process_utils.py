import cv2
import numpy as np

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


def color_clean(img):
    # 转换为HSV颜色空间(色相, 亮度, 纯度)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 创建红色和蓝色mask, mask范围内设置为白色, 否则黑色
    mask_red = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    # 合并红色和蓝色
    mask_combined = cv2.bitwise_or(mask_red, mask_blue)

    # 使用TELEA算法进行图像恢复, 去除红色和蓝色区域并用周围像素填充
    # TELEA算法流程:
    #   边界检测：确定掩码区域的边界
    #   优先级计算：基于边界法线和梯度方向计算修复优先级
    #   像素填充：从最高优先级开始，用邻域加权平均填充
    #   传播更新：更新边界和优先级，迭代处理
    return cv2.inpaint(img, mask_combined, inpaintRadius=3, flags=cv2.INPAINT_TELEA)


# 通过连通域去除噪声, 过滤连通区域小于阈值的噪声
def connect_clean(img, min_area):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
    valid_labels = np.where(stats[1:, cv2.CC_STAT_AREA] >= min_area)[0] + 1
    return np.isin(labels, valid_labels).astype(np.uint8) * 255
