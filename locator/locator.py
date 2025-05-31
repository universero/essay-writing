"""
locator 用于作文主体部分和标题的定位
基于 YOLO 11, 负责作文主体部分的定位与裁切
"""
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from ultralytics import YOLO

MODEL = './resource/weights/200e4b1440sz-n.pt'
IMGSZ = 640


class Locator:
    def __init__(self, weight, device):
        """初始化定位器"""
        try:
            self.model = YOLO(weight)
            self.model.to(device)
            self.class_names = self.model.names  # 获取类别名称映射
            print(f"✅ 定位器初始化成功 | 类别: {self.class_names} | 设备: {device}")
        except Exception as e:
            raise RuntimeError(f"定位器初始化失败: {str(e)}")

    def locate(self, image):
        """输入图片, 输出title和content的定位box"""
        # 参数验证
        if not isinstance(image, np.ndarray) or image.ndim != 3:
            raise ValueError("输入必须是3通道的numpy数组(BGR格式)")

        # 执行预测
        results = self.model.predict(
            source=image,
            conf=0.4,
            iou=0.45,
            imgsz=IMGSZ,
            verbose=False  # 关闭冗余输出
        )

        # 解析结果
        detections = []
        for result in results:
            for box in result.boxes:
                xyxy = box.xyxy.cpu().numpy()[0]  # 转换为numpy数组后取第一个元素
                detections.append(Box(
                    c=int(box.cls),
                    x1=float(xyxy[0]),
                    y1=float(xyxy[1]),
                    x2=float(xyxy[2]),
                    y2=float(xyxy[3]),
                    conf=float(box.conf)
                ))

        # 按类别分组并选择置信度最高的
        output = {"title": None, "content": None}
        for box in sorted(detections, key=lambda x: -x.conf):
            if box.c == 0 and output["title"] is None:  # title
                output["title"] = box
            elif box.c == 1 and output["content"] is None:  # content
                output["content"] = box

        # 确保content的上沿低于title的下沿
        if output["title"] and output["content"]:
            output["content"].adjust_based_on_title(output["title"])

        return output


@dataclass
class Box:
    """表示检测框的坐标和类别"""
    c: int  # 类别 (0:title, 1:content)
    x1: float  # 左上角x
    y1: float  # 左上角y
    x2: float  # 右下角x
    y2: float  # 右下角y
    conf: float = 0.0  # 置信度

    @property
    def xyxy(self) -> Tuple[float, float, float, float]:
        """返回(x1, y1, x2, y2)格式坐标"""
        return self.x1, self.y1, self.x2, self.y2

    def adjust_based_on_title(self, title_box: 'Box') -> None:
        """根据title框位置调整当前content框的上沿"""
        if self.y1 < title_box.y2:  # 如果content上沿高于title下沿
            self.y1 = title_box.y2 - 1  # 调整为title下沿-1
            # 确保调整后仍然是有效框
            if self.y1 >= self.y2:
                self.y2 = self.y1 + 10  # 最小高度保护
