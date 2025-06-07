import cv2
import numpy as np


def binarize_image(gray_image):
    """
    自适应阈值二值化（白底黑字）。
    """
    # binary = cv2.adaptiveThreshold(
    #     gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY, 15, 10
    # )
    # return binary
    return binarize_text_only(gray_image)


def remove_grid_fft(gray_image):
    # 傅里叶变换
    dft = np.fft.fft2(gray_image)
    dft_shift = np.fft.fftshift(dft)

    # 构造掩膜去除高频（网格线通常在频域表现为高频分量）
    rows, cols = gray_image.shape
    crow, ccol = rows // 2, cols // 2
    mask = np.ones((rows, cols), np.uint8)
    r = 30  # 调整半径大小控制去除网格的强度
    cv2.circle(mask, (ccol, crow), r, 0, -1)

    # 反变换
    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back).astype(np.uint8)

    return img_back


def binarize_text_only(gray_image):
    # 第一步：频域去网格
    fft_cleaned = remove_grid_fft(gray_image)

    # 第二步：形态学优化
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(fft_cleaned, cv2.MORPH_CLOSE, kernel)

    # 第三步：最终二值化
    binary = cv2.adaptiveThreshold(
        morph, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 5
    )
    return cv2.bitwise_not(binary)  # 转换为白底黑字
