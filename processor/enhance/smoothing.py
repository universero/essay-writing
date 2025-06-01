import cv2


def smooth_image(image):
    """
    这里用的是PPT里的讲述的加权平均滤波中的双边滤波（Bilateral Filter）
    使用双边滤波平滑图像，去噪保边缘。
    """
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
