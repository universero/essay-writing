import os
import cv2
from enhance import enhance_image


def process_folder(input_folder, output_folder):
    """
    批处理图像增强：处理文件夹中所有图像并输出。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(input_folder, filename)
            image = cv2.imread(path)
            enhanced = enhance_image(image)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, enhanced)
            print(f"Processed: {filename}")


if __name__ == "__main__":
    input_dir = "cut_images"
    output_dir = "enhanced_images"
    process_folder(input_dir, output_dir)
