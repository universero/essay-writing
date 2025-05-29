import cv2
from remove_red import remove_red_marks
from contrast import enhance_contrast
from smoothing import smooth_image
from binarize import binarize_image

def enhance_image(image):
    """
    图像增强主流程：清除红色、增强对比度、平滑、二值化、形态学处理。
    返回增强后的二值图像（白底黑字）。
    """
    cleaned = remove_red_marks(image)
    gray = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    contrast = enhance_contrast(gray)
    smooth = smooth_image(contrast)
    binary = binarize_image(smooth)
    morph = apply_morphology(binary)
    return morph
