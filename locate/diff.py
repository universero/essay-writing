import json
import time
from collections import defaultdict
from pathlib import Path

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO

"""
diff.py 比较不同模型不同输入尺寸的效果
"""

# 配置参数
MODELS = [
    "./resource/weights/200e4b1440sz-s.pt",
    "./resource/weights/200e4b1440sz-n.pt",
    "./resource/weights/100e4b1440sz-s.pt",
    "./resource/weights/200e8b1440sz-n.pt",
]
IMAGE_SIZES = [640, 800, 1440]  # 需要测试的输入尺寸
IMAGE_DIR = "./resource/dataset/train/images/"
LABEL_DIR = "./resource/dataset/train/labels/"
OUTPUT_DIR = "../asset/locator/diff/"
METRICS_FILE = "../asset/locator/diff/model_metrics.json"


def yolo_to_xyxy(yolo_box, img_width, img_height):
    """
    将YOLO归一化坐标转换为像素坐标
    Args:
        yolo_box: [x_center, y_center, width, height] (归一化值)
        img_width: 图像实际宽度
        img_height: 图像实际高度
    Returns:
        [x1, y1, x2, y2] 像素坐标
    """
    x_center, y_center, w, h = yolo_box
    x_center *= img_width
    y_center *= img_height
    w *= img_width
    h *= img_height

    x1 = max(0, x_center - w / 2)
    y1 = max(0, y_center - h / 2)
    x2 = min(img_width - 1, x_center + w / 2)
    y2 = min(img_height - 1, y_center + h / 2)

    return [x1, y1, x2, y2]


def get_image_size(img_path):
    """获取图像实际尺寸"""
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"无法读取图像: {img_path}")
    return img.shape[1], img.shape[0]  # (width, heigh


def load_ground_truth():
    """加载手动标注的真实标签"""
    gt = {}
    for label_file in Path(LABEL_DIR).glob("*.txt"):
        img_file = Path(IMAGE_DIR) / f"{label_file.stem}.jpg"
        if not img_file.exists():
            continue

        img_width, img_height = get_image_size(img_file)

        with open(label_file, 'r') as f:
            lines = [line.strip().split() for line in f.readlines()]

        gt[label_file.stem] = [
            {
                'class': int(parts[0]),
                'xyxy': yolo_to_xyxy(list(map(float, parts[1:5])), img_width, img_height),
                'conf': 1.0
            }
            for parts in lines if len(parts) >= 5
        ]

    return gt


def calculate_iou(pred, gt):
    """计算两个框的IoU"""
    # 计算交集坐标
    x1 = max(pred[0], gt[0])
    y1 = max(pred[1], gt[1])
    x2 = min(pred[2], gt[2])
    y2 = min(pred[3], gt[3])
    # 计算交集面积
    inter_area = abs(x2 - x1) * abs(y2 - y1)
    # 计算并集面积
    box1_area = (pred[2] - pred[0]) * (pred[3] - pred[1])
    box2_area = (gt[2] - gt[0]) * (gt[3] - gt[1])
    iou = inter_area / (box1_area + box2_area - inter_area)
    return iou


class AdvancedEvaluator:
    def __init__(self):
        self.gt_data = load_ground_truth()
        self.metrics = defaultdict(dict)

    def evaluate_model(self, model_path, imgsz):
        """评估单个模型在特定尺寸下的表现"""
        model = YOLO(model_path)
        model_name = f"{Path(model_path).stem}_{imgsz}"
        print(f"\n🔍 正在评估: {model_name}")

        stats = {
            'total_images': 0,
            'correct_detections': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'avg_iou': 0,
            'avg_conf': 0,
            'inference_time': 0
        }

        for img_path in Path(LABEL_DIR).glob("*.txt"):
            # 获取对应图片路径
            img_file = Path(IMAGE_DIR) / f"{img_path.stem}.jpg"
            if not img_file.exists():
                continue

            # 预测并计时
            start_time = time.time()
            results = model.predict(
                source=str(img_file),
                conf=0.4,
                iou=0.5,
                imgsz=imgsz,
                verbose=False
            )
            stats['inference_time'] += time.time() - start_time

            # 处理预测结果
            gt_boxes = self.gt_data.get(img_path.stem, [])
            pred_boxes = []
            for r in results:
                for box in r.boxes:
                    pred_boxes.append({
                        'class': int(box.cls),
                        'xyxy': box.xyxy.tolist()[0],
                        'conf': float(box.conf)
                    })

            # 更新统计指标
            stats['total_images'] += 1
            matched = set()

            for gt in gt_boxes:
                best_iou = 0
                best_idx = -1

                for i, pred in enumerate(pred_boxes):
                    if pred['class'] == gt['class']:
                        iou = calculate_iou(pred['xyxy'], gt['xyxy'])
                        if iou > best_iou and i not in matched:
                            best_iou = iou
                            best_idx = i

                if best_iou > 0.7:
                    stats['correct_detections'] += 1
                    stats['avg_iou'] += best_iou
                    stats['avg_conf'] += pred_boxes[best_idx]['conf']
                    matched.add(best_idx)
                else:
                    stats['false_negatives'] += 1

            stats['false_positives'] += len(pred_boxes) - len(matched)

        # 计算平均值
        if stats['correct_detections'] > 0:
            stats['avg_iou'] /= stats['correct_detections']
            stats['avg_conf'] /= stats['correct_detections']
        if stats['total_images'] > 0:
            stats['inference_time'] /= stats['total_images']

        # 计算综合评分
        recall = stats['correct_detections'] / (stats['correct_detections'] + stats['false_negatives'] + 1e-6)
        precision = stats['correct_detections'] / (stats['correct_detections'] + stats['false_positives'] + 1e-6)
        stats['score'] = 0.4 * recall + 0.3 * precision + 0.2 * stats['avg_iou'] + 0.1 * (
                1 - stats['inference_time'] / 0.5)

        self.metrics[model_name] = stats
        return stats

    def run_evaluation(self):
        """执行全量评估"""
        for model_path in MODELS:
            for imgsz in IMAGE_SIZES:
                self.evaluate_model(model_path, imgsz)

        # 保存结果
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.metrics, f, indent=2)

        # 可视化结果
        self.visualize_results()

        return self.metrics

    def visualize_results(self):
        """自适应可视化报告（自动调整画布尺寸）"""
        # 动态计算画布尺寸
        n_models = len(self.metrics)
        fig_width = max(18, n_models * 2)  # 基础宽度 + 每模型2英寸
        fig_height = max(15, fig_width * 0.8)

        # 创建画布和子图布局
        fig = plt.figure(figsize=(fig_width, fig_height), constrained_layout=True)
        gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1], height_ratios=[1, 1])
        ax1 = fig.add_subplot(gs[0, 0])  # 质量指标
        ax2 = fig.add_subplot(gs[0, 1])  # 推理速度
        ax3 = fig.add_subplot(gs[1, 0])  # 雷达图
        ax4 = fig.add_subplot(gs[1, 1])  # 尺寸影响

        plt.suptitle(f'多模型评估报告（共{n_models}种配置）', fontsize=16, y=1.05)

        # --- 数据准备 ---
        model_names = []
        recalls, precisions, ious, speeds, scores = [], [], [], [], []

        for name, stats in self.metrics.items():
            model_names.append(name)
            recalls.append(stats['recall'] if 'recall' in stats else
                           stats['correct_detections'] / (
                                   stats['correct_detections'] + stats['false_negatives'] + 1e-6))
            precisions.append(stats['precision'] if 'precision' in stats else
                              stats['correct_detections'] / (
                                      stats['correct_detections'] + stats['false_positives'] + 1e-6))
            ious.append(stats['avg_iou'])
            speeds.append(1 / (stats['inference_time'] + 1e-6))
            scores.append(stats['score'])

        # --- 图1: 质量指标对比（横向柱状图）---
        y = np.arange(len(model_names))
        width = 0.25
        ax1.barh(y - width, recalls, width, label='召回率', color='#4C72B0')
        ax1.barh(y, precisions, width, label='精确率', color='#55A868')
        ax1.barh(y + width, ious, width, label='平均IoU', color='#C44E52')

        ax1.set_yticks(y, model_names, fontsize=9)
        ax1.set_title('(a) 检测质量指标对比', pad=10)
        ax1.legend(loc='lower right', bbox_to_anchor=(1, 0))
        ax1.grid(axis='x', linestyle='--', alpha=0.7)
        ax1.set_xlim(0, 1.1)

        # --- 图2: 推理速度（横向条形图）---
        colors = plt.cm.viridis(np.linspace(0, 1, len(IMAGE_SIZES)))
        imgsz_to_color = {sz: colors[i] for i, sz in enumerate(IMAGE_SIZES)}

        bar_colors = [imgsz_to_color[int(name.split('_')[-1])] for name in model_names]
        bars = ax2.barh(model_names, speeds, color=bar_colors)

        # 添加速度数值标签
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 5, bar.get_y() + bar.get_height() / 2,
                     f'{width:.1f}', ha='left', va='center', fontsize=8)

        ax2.set_title('(b) 推理速度 (FPS)', pad=10)
        ax2.grid(axis='x', linestyle='--', alpha=0.7)

        # 添加图例说明尺寸颜色
        legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color, label=f'{sz}px')
                           for sz, color in imgsz_to_color.items()]
        ax2.legend(handles=legend_elements, title='输入尺寸', loc='lower right')

        # --- 图3: 雷达图（缩小标签字体）---
        categories = ['召回率', '精确率', 'IoU', '速度', '综合']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        for name, stats in self.metrics.items():
            values = [
                stats['correct_detections'] / (stats['correct_detections'] + stats['false_negatives'] + 1e-6),
                stats['correct_detections'] / (stats['correct_detections'] + stats['false_positives'] + 1e-6),
                stats['avg_iou'],
                min(1, 1 / (stats['inference_time'] + 1e-6)),
                stats['score']
            ]
            values += values[:1]
            ax3.plot(angles, values, 'o-', linewidth=1, markersize=3,
                     label=name.split('_')[0])  # 只显示模型基础名称

        ax3.set_xticks(angles[:-1], categories, fontsize=8)
        ax3.set_title('(c) 雷达图综合对比', pad=10)
        ax3.legend(bbox_to_anchor=(1.1, 1), fontsize=8)
        ax3.grid(True)

        # --- 图4: 尺寸影响（分组柱状图）---
        model_bases = sorted(set([name.split('_')[0] for name in model_names]))
        x = np.arange(len(model_bases))
        width = 0.25

        for i, imgsz in enumerate(IMAGE_SIZES):
            scores = []
            for model in model_bases:
                key = f"{model}_{imgsz}"
                scores.append(self.metrics[key]['score'] if key in self.metrics else 0)

            ax4.bar(x + i * width, scores, width, label=f'{imgsz}px',
                    color=imgsz_to_color[imgsz])

        ax4.set_xticks(x + width, model_bases, rotation=45, ha='right')
        ax4.set_title('(d) 不同尺寸下的评分对比', pad=10)
        ax4.legend(title='输入尺寸')
        ax4.grid(axis='y', linestyle='--', alpha=0.7)

        # 自适应调整并保存
        plt.tight_layout()
        plt.savefig(
            f"{OUTPUT_DIR}/comparison.png",
            dpi=300,
            bbox_inches='tight',
            facecolor='white'
        )
        print(f"📊 自适应可视化报告已保存至: {OUTPUT_DIR}/comparison.png")


if __name__ == "__main__":
    # 切换字体
    try:
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    except Exception as e:
        print(e)

    evaluator = AdvancedEvaluator()
    metrics = evaluator.run_evaluation()

    # 打印最佳配置
    best_config = max(metrics.items(), key=lambda x: x[1]['score'])
    print(f"\n🏆 最佳配置: {best_config[0]}")
    print(f"   - 综合评分: {best_config[1]['score']:.3f}")
    print(
        f"   - 召回率: {best_config[1]['correct_detections'] / (best_config[1]['correct_detections'] + best_config[1]['false_negatives']):.2%}")
    print(
        f"   - 精确率: {best_config[1]['correct_detections'] / (best_config[1]['correct_detections'] + best_config[1]['false_positives']):.2%}")
    print(f"   - 平均IoU: {best_config[1]['avg_iou']:.3f}")
    print(f"   - 推理时间: {best_config[1]['inference_time']:.3f}s/张")
