# 单张处理本地文件
import os
from glob import glob

import cv2

from process.processor import process_core


def process_local(input_path, output_path):
    img = cv2.imread(input_path)
    output = process_core(img)
    cv2.imwrite(output_path, output)


# 批量处理本地文件
def process_locals(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    # 获取文件夹中所有图片文件
    image_files = glob(os.path.join(input_folder, '*.jpg')) + glob(os.path.join(input_folder, '*.jpeg')) + glob(
        os.path.join(input_folder, '*.png'))
    # 处理每张图片
    for input_path in image_files:
        # 构造输出路径
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_folder, f"processed_{filename}")
        # 处理图片
        process_local(input_path, output_path)
        print(f"已处理: {input_path.replace(os.sep, '/')} -> {output_path.replace(os.sep, '/')}")


# 本地测试用
if __name__ == "__main__":
    input_image = "../asset/process/0377ac35a913fe307f9e9118398c587.jpg"  # 输入图片路径
    output_image = "../asset/process/new.jpg"  # 输出图片路径
    process_local(input_image, output_image)

    # input_folder = r"../locate/resource/dataset/train/images"  # 输入文件夹路径
    # output_folder = r"../asset/processed"  # 输出文件夹路径
    # process_locals(input_folder, output_folder)
