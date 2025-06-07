import cv2

from processor.enhance import contrast
from processor.enhance.binarize import binarize_image
from processor.enhance.contrast import enhance_contrast
from processor.enhance.remove_colored import remove_colored_marks
from processor.enhance.smoothing import smooth_image


def enhance_image(image):
    """
    图像增强主流程：
    1. 清除干扰色（红色批改、绿色/蓝色边框）
    2. 灰度转换
    3. 对比度增强
    4. 图像平滑
    5. 图像二值化
    返回白底黑字的增强图像
    """

    # Step 1: 清理红色、绿色、蓝色标记
    cleaned = remove_colored_marks(image)
    cv2.imwrite("../../asset/process/clean.JPG", cleaned)
    # Step 2: 转换为灰度图
    gray = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("../../asset/process/gray.JPG", gray)
    # Step 3: 对比度增强（灰度变化法）
    contrast = enhance_contrast(gray)
    cv2.imwrite("../../asset/process/contrast.JPG", contrast)
    # # Step 4: 图像平滑（如中值滤波）
    # smooth = smooth_image(contrast)
    # cv2.imwrite("../../asset/process/smooth.JPG", smooth)
    # Step 5: 二值化
    binary = binarize_image(contrast)
    cv2.imwrite("../../asset/process/binary-15-3.jpg", binary)
    return binary


if __name__ == "__main__":
    # 固定测试图像路径 - 修改为你自己的测试图像路径
    TEST_IMAGE_PATH = "../../asset/process/IMG_0513.JPG"  # 假设当前目录下有一个test.jpg文件

    # 处理并显示测试图像
    print("开始处理测试图像...")
    image = cv2.imread(TEST_IMAGE_PATH, cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"无法读取图像: {TEST_IMAGE_PATH}")

    enhanced = enhance_image(image)
    print("测试完成！")
