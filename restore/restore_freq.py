import numpy as np
import cv2

"""
    频域逆滤波方法
    """

def freq_inverse_filter(blurred, kernel, eps=1e-3):
    """
    频域逆滤波：H(u,v)^-1 * G(u,v)
    """
    G = np.fft.fft2(blurred)
    H = np.fft.fft2(kernel, s=blurred.shape)
    H[np.abs(H) < eps] = eps  # 避免除0
    F_hat = G / H
    f_hat = np.fft.ifft2(F_hat)
    restored = np.abs(f_hat)
    return np.clip(restored, 0, 255).astype(np.uint8)
