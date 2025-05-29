import numpy as np
from scipy.signal import convolve2d
import cv2

"""
    空域恢复方法
"""
def inverse_filter(blurred, kernel, epsilon=1e-3):
    """
    空域逆滤波，直接使用反卷积
    """
    kernel_flipped = np.flipud(np.fliplr(kernel))
    restored = convolve2d(blurred, kernel_flipped, mode='same', boundary='symm')
    return np.clip(restored, 0, 255).astype(np.uint8)

def wiener_filter(blurred, kernel, K=0.01):
    """
    空域维纳滤波
    """
    kernel /= np.sum(kernel)
    dummy = np.copy(blurred)
    dft_blur = np.fft.fft2(blurred)
    dft_kernel = np.fft.fft2(kernel, s=blurred.shape)
    dft_kernel_conj = np.conj(dft_kernel)
    dft_kernel_abs2 = np.abs(dft_kernel)**2
    wiener_filter = dft_kernel_conj / (dft_kernel_abs2 + K)
    dft_result = wiener_filter * dft_blur
    result = np.fft.ifft2(dft_result)
    return np.abs(result).astype(np.uint8)
