import os
from pathlib import Path

import torch
from ultralytics import YOLO

"""
train.py 定位器的训练过程
"""

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

MODEL = './resource/weights/yolo11n.pt'
DATA = './resource/dataset/data.yaml'


def validate_dataset(data_yaml):
    base = Path(data_yaml).parent.absolute()
    print("base", base)
    for split in ['train', 'val']:
        img_dir = base / split / 'images'
        label_dir = base / split / 'labels'

        if not label_dir.exists():
            raise FileNotFoundError(f"Missing label dir: {label_dir}")

        txt_files = list(label_dir.glob('*.txt'))
        if not txt_files:
            raise ValueError(f"No .txt labels found in {label_dir}")

        print(f"✅ {split}: Found {len(txt_files)} labels")


if __name__ == "__main__":
    print(torch.cuda.is_available())
    print(torch.version.cuda)
    print(torch.cuda.get_device_name(0))
    validate_dataset('resource/dataset/data.yaml')
    model = YOLO(MODEL)
    result = model.train(
        data=DATA,
        epochs=200,
        batch=8,
        imgsz=1440,
        name='essay_test',
        mosaic=0.5,  # 马赛克增强概率
        mixup=0.1,  # 图像混合增强
        device=0,
        augment=False,  # 关闭自动增强
        dropout=0.2,  # 添加dropout防止过拟合
    )
