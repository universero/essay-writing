"""
val.py 批量识别图片, 以人为观察效果
200e4b1440sz-s.pt - 大部分title的置信度均低于0.4
100e4b1440sz-s.pt - 大部分title的置信度均低于0.4
200e8b1440sz-n.pt - 少部分title无法识别，存在title和content重合问题
200e4b1440sz-n.pt - title无法识别的情况更少，同样存在title和content重合问题
"""

import time
from pathlib import Path

from ultralytics import YOLO

# 配置参数
WEIGHT = './resource/weights/200e4b1440sz-n.pt'  # 模型路径
INPUT_FOLDER = './resource/dataset/train/images/'  # 输入文件夹路径
OUTPUT_FOLDER = '../asset/locator/val/'  # 输出文件夹路径
DEVICE = "cpu"


def validate_model(weight_path):
    """验证模型和类别是否正确加载"""
    try:
        model = YOLO(weight_path)
        print(f"✅ 模型加载成功，类别: {model.names}")
        return model
    except Exception as e:
        raise RuntimeError(f"模型加载失败: {str(e)}")


def process_single_image(model, image_path, output_dir):
    """处理单张图片并返回结果"""
    # 执行预测
    results = model.predict(
        source=image_path,
        conf=0.4,
        iou=0.45,
        imgsz=640,
        save=True,
        project=output_dir,
        name="",  # 直接保存在output_dir下
        exist_ok=True,
        device=DEVICE,
    )

    # 返回检测结果信息
    detection_info = []
    for result in results:
        boxes_info = []
        for box in result.boxes:
            boxes_info.append({
                'class': model.names[int(box.cls)],
                'confidence': round(box.conf.item(), 2),
                'coordinates': [round(x, 2) for x in box.xyxy.tolist()[0]]
            })
        detection_info.append({
            'image_name': Path(image_path).name,
            'detections': boxes_info
        })
    return detection_info


def run_batch_detection():
    """批量处理输入文件夹中的所有图片"""
    # 验证文件夹存在
    input_path = Path(INPUT_FOLDER)
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件夹不存在: {input_path.absolute()}")

    # 创建输出文件夹
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)

    # 加载模型
    model = validate_model(WEIGHT)

    # 获取所有支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(input_path.glob(ext))

    if not image_paths:
        print("⚠️ 输入文件夹中没有找到支持的图片格式(.jpg/.jpeg/.png/.bmp)")
        return

    print(f"\n🔍 发现 {len(image_paths)} 张待处理图片")

    # 处理所有图片
    all_results = []
    start_time = time.time()

    for i, img_path in enumerate(image_paths, 1):
        try:
            print(f"\n[{i}/{len(image_paths)}] 正在处理: {img_path.name}")
            result = process_single_image(model, img_path, OUTPUT_FOLDER)
            all_results.extend(result)

            # 打印当前图片结果
            print(f"检测到 {len(result[0]['detections'])} 个目标")
            for det in result[0]['detections']:
                print(f" - {det['class']}: 置信度 {det['confidence']:.2f}, 坐标 {det['coordinates']}")

        except Exception as e:
            print(f"❌ 处理 {img_path.name} 时出错: {str(e)}")
            continue

    # 打印汇总信息
    total_time = time.time() - start_time
    avg_time = total_time / len(image_paths) if len(image_paths) > 0 else 0

    print("\n=== 处理完成 ===")
    print(f"📊 共处理 {len(image_paths)} 张图片")
    print(f"⏱️ 总耗时: {total_time:.2f} 秒, 平均每张: {avg_time:.2f} 秒")
    print(f"📁 所有结果已保存至: {output_path.absolute()}")

    # 返回所有结果供进一步处理
    return all_results


if __name__ == "__main__":
    try:
        run_batch_detection()
    except Exception as e:
        print(f"❌ 程序运行失败: {str(e)}")
