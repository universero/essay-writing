import cv2


def binarize_image(gray_image):
    """
    自适应阈值二值化（白底黑字）。
    """
    binary = cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 10
    )
    return binary
