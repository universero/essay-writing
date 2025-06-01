import base64
from io import BytesIO

import cv2
import numpy as np
from flask import Blueprint, request
from matplotlib import pyplot as plt

from common import rex
from common.consts import MODE
from locator.locator import Locator, MODEL, DEVICE

bp = Blueprint('locator-test', __name__)


def visualize_detection(image, boxes, titles):
    """可视化检测结果"""
    plt.figure(figsize=(12, 8))

    # 绘制原图
    plt.subplot(2, 2, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    plt.axis('off')

    # 绘制带检测框的图像
    img_with_boxes = image.copy()
    for box, title in zip(boxes, titles):
        if box:
            x1, y1, x2, y2 = map(int, box.xyxy)
            cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (255, 0, 0), 8)
            cv2.putText(img_with_boxes, f"{title} {box.conf:.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    plt.subplot(2, 2, 2)
    plt.imshow(cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB))
    plt.title("Detection Results")
    plt.axis('off')

    # 绘制标题区域
    if boxes[0]:
        title_box = boxes[0]
        x1, y1, x2, y2 = map(int, title_box.xyxy)
        title_crop = image[y1:y2, x1:x2]
        plt.subplot(2, 2, 3)
        plt.imshow(cv2.cvtColor(title_crop, cv2.COLOR_BGR2RGB))
        plt.title("Title Region")
        plt.axis('off')

    # 绘制内容区域
    if boxes[1]:
        content_box = boxes[1]
        x1, y1, x2, y2 = map(int, content_box.xyxy)
        content_crop = image[y1:y2, x1:x2]
        plt.subplot(2, 2, 4)
        plt.imshow(cv2.cvtColor(content_crop, cv2.COLOR_BGR2RGB))
        plt.title("Content Region")
        plt.axis('off')

    plt.tight_layout()
    if MODE == "test":
        plt.show()
    # 将图片保存到内存中的二进制流
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg', dpi=100)
    buffer.seek(0)  # 重置指针位置
    plt.close()  # 关闭plt，释放内存

    return base64.b64encode(buffer.getvalue()).decode('utf-8')  # 返回base64编码


def test_locator(image):
    # 初始化定位器
    locator = Locator(weight=MODEL, device=DEVICE)
    # 执行定位
    result = locator.locate(image)

    # 提取检测框
    title_box = result["title"]
    content_box = result["content"]

    print("检测结果:")
    print(f"- Title: {title_box.xyxy if title_box else '未检测到'}")
    print(f"- Content: {content_box.xyxy if content_box else '未检测到'}")

    # 可视化结果
    return visualize_detection(image, [title_box, content_box], ["Title", "Content"])


@bp.post("/locate-test")
def locate():
    imgs = list(cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR) for file in
                request.files.getlist("images"))
    boxs = []
    for img in imgs:
        boxs.append(test_locator(img))
    return rex.succeed(boxs)


if __name__ == "__main__":
    # 替换为您的测试图片路径
    test_image_path = r"F:\xh-polaris\essay-writing\locator\resource\dataset\train\images\IMG_0531.JPG"
    test_locator(test_image_path)
