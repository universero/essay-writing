import torch
from ultralytics import YOLO
import torch.serialization


def compare_models(original_path, trained_path):
    """安全比较两个YOLO模型的权重差异"""

    # 1. 安全加载模型
    def safe_load(model_path):
        required_globals = [
            'ultralytics.nn.tasks.DetectionModel',
            'ultralytics.nn.modules.Conv',
            'torch.nn.Module',
            'torch.Tensor'
        ]
        with torch.serialization.safe_globals(required_globals):
            return YOLO(model_path)

    # 2. 加载模型
    print("正在加载模型...")
    original = safe_load(original_path)
    trained = safe_load(trained_path)

    # 3. 获取模型状态字典
    print("提取模型权重...")
    orig_state = original.model.state_dict()  # 获取原始模型权重
    trained_state = trained.model.state_dict()  # 获取训练后模型权重

    # 4. 比较权重差异
    print("\n开始比较权重差异:")
    diff_count = 0
    for name in orig_state.keys():
        if not torch.equal(orig_state[name], trained_state[name]):
            diff_count += 1
            print(f'[已改变] 层: {name}')

    print(f"\n总结: 共改变了 {diff_count}/{len(orig_state)} 个权重层")


if __name__ == "__main__":
    try:
        compare_models(
            original_path='resource/weights/yolo11n.pt',
            trained_path='resource/weights/best.pt'
        )
    except Exception as e:
        print(f"错误发生: {str(e)}")
        print("\n建议解决方案:")
