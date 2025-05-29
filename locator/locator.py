"""
locator 定位器
基于 YOLO 11, 负责作文主体部分的定位与裁切
"""

import cv2
from ultralytics import YOLO
from pathlib import Path

# 配置参数
WEIGHT = './resource/weights/best.pt'  # 模型路径
INPUT_IMAGE = '../asset/locator_input.jpg'  # 输入图片路径


def validate_model(weight_path):
    """验证模型和类别是否正确加载"""
    try:
        model = YOLO(weight_path)
        print(f"✅ 模型加载成功，类别: {model.names}")
        return model
    except Exception as e:
        raise RuntimeError(f"模型加载失败: {str(e)}")


def run_detection():
    """执行目标检测并输出结果"""
    # 验证文件存在
    input_path = Path(INPUT_IMAGE)
    if not input_path.exists():
        raise FileNotFoundError(f"输入图片不存在: {input_path.absolute()}")

    # 加载并验证模型
    model = validate_model(WEIGHT)

    # 执行预测（添加增强参数）
    results = model.predict(
        source=input_path,
        conf=0.4,  # 调整为更合理的默认阈值
        iou=0.45,  # 显式设置NMS阈值
        imgsz=640,
        save=True,  # 自动保存结果
        project="../asset/",  # 输出目录
        name="locator_output"  # 输出文件夹名
    )

    # 输出检测结果
    print("\n=== 检测结果 ===")
    for i, result in enumerate(results):
        print(f"\n第 {i + 1} 个检测结果:")
        print(f"检测到 {len(result.boxes)} 个目标")

        if result.boxes:
            for box in result.boxes:
                print(f"\n- 类别: {model.names[int(box.cls)]}")
                print(f"- 置信度: {box.conf.item():.2f}")
                print(f"- 坐标 (xyxy格式): {[round(x, 2) for x in box.xyxy.tolist()[0]]}")

        # 可视化结果路径
        output_dir = Path("../asset/locator_output")
        print(f"\n所有输出文件已保存至: {output_dir.absolute()}")


if __name__ == "__main__":
    try:
        run_detection()
    except Exception as e:
        print(f"❌ 检测失败: {str(e)}")
