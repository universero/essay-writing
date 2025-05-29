import cv2
import numpy as np
from scipy.signal import convolve2d

"""
    模拟退化模型在这里的作用：
    作为测试用例 —— 为验证图像恢复算法是否有效
    （感觉不加也行）
    """

def add_motion_blur(image, kernel_size=15):
    """
    添加水平运动模糊（PSF）
    """
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel = kernel / kernel_size
    blurred = cv2.filter2D(image, -1, kernel)
    return blurred, kernel

def add_gaussian_noise(image, mean=0, var=0.001):
    """
    添加高斯噪声
    """
    sigma = var**0.5
    noise = np.random.normal(mean, sigma, image.shape)
    noisy = np.clip(image + noise * 255, 0, 255).astype(np.uint8)
    return noisy
