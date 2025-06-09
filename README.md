# Essay-Eval作文批改系统

## 概述

本项目是综合运用各种数字图像处理技术, 并结合现有的作文批改能力实现的作文批改系统
用户上传作文图片, 经过定位, 处理, 识别, 批改, 渲染等流程后可以得到画面精美, 内容详实的批改结果

## 架构

![项目架构](asset/structure.png)

## 核心模块

项目总共四个核心模块, 依次为Locator定位器, Processor 预处理器, OCR 识别器, Render 渲染器

### Locator 定位器

Locator 模块基于 YOLO 11 实现作文标题与主体的定位与切分, 以弥补OCR模块不具备分类能力的缺陷

- 模块构成
  ```
  ├── resource/                  # 静态资源
  │   ├── dataset/               # 数据集
  │   │   ├── train/             # 训练集
  │   │   ├── val/               # 测试集
  │   │   └── data.yaml          # 数据集配置
  │   └── weights/               # 模型权重集合
  ├── train.py                   # 训练代码（默认使用device-0，需Nvidia显卡与CUDA驱动）
  ├── locator.py                 # 推理代码（默认使用device-0，需Nvidia显卡与CUDA驱动）
  ├── locator_test.py            # 推理测试代码（返回切割图与原图等可视化对比）
  ├── val.py                     # 批量测试代码（批量推理测试效率）
  └── diff.py                    # 模型性能对比（批量对比不同模型在不同输入尺寸下的效果）
  ```

- 模型能力对比 [模型评分](asset/locator/diff/model_metrics.json) ![模型相关对比](asset/locator/diff/comparison.png)
- 定位结果展示 ![定位结果](asset/locate_show.png)

### Processor 预处理器

Processor 模块通过hsv掩码, 连通域分析, 开闭运算, 二值化等数字图像处理技术对图像进行一系列操作，从而去除涂改, 教师批改等多余信息,
以弥补OCR模块无法排除非作文信息干扰的缺陷

- 模块构成
  ```
  ├── restore/                   # 图像恢复工具, 暂时没有实际使用
  ├── local_tests.py             # 本地测试工具, 用于测试处理效果
  ├── process_utils.py           # 自定义处理工具(包括颜色去除, 连通域分析等)
  └── processor.py               # 预处理器核心部分, 组织各处理流程以及定义相关接口
  ```
- 处理效果样例
    - 处理前![处理前](asset/process_origin.jpg "原始图像")
    - 处理后(实际使用时, 侧边栏中多余字符与噪声在locate阶段会被去除)
      ![处理后](asset/process_show.jpg "处理后图像")

### OCR

OCR 模块通过调用Essay-Stateless中台的OCR接口实现文字识别, 并通过后处理增强OCR的抗干扰能力

[Essay-Stateless:OCR模块](https://github.com/xh-polaris/essay-stateless/tree/main/src/main/java/com/xhpolaris/essay_stateless/ocr)
是Java实现的中台服务, 可以集成多供应商的OCR能力, 并且能够根据供应商特性实现如印刷字体去除等增强功能

- 模块构成
  ```
  ├── bee.py                   # BeeOCR客户端, 调用OCR中台服务
  ├── post.py                  # OCR后处理工具, 用于对OCR结果进一步校正(核心是中英字符处理)
  └── ocr.py                   # OCR核心部分, 组织处理流程并定义相关接口
  ```

### Evaluate

Evaluate 模块通过调用批改服务的接口实现作文批改功能, 并通过建造者模式构造渲染模块需要的对象组织形式

- 模块构成
  ```
  ├── evaluator.py             # Evalutate核心部分, 组织批改流程并定义相关接口
  ├── micro_evalu.py           # 定义micro版本批改算法的对象结构
  └── micro_builder.py         # micro版本建造者, 构建render所需对象
  ```

### Render

Render模块负责作文批改结果的渲染, 核心组成如下:

- 作文框线生成
- 段评绘制
- 好词好句/错词病句标注
- 侧边栏点评
- 全文总评

```
├── resource/                  # 静态资源（如字体文件等）
├── components.py              # 渲染图内容组件定义
├── config.py                  # 渲染图各部分尺寸定义
├── draw_utils.py              # 自定义绘图工具（包括波浪线、多行文字等）
└── render.py                  # 渲染核心类（负责各组件的组织与绘制）
```

渲染结果样例
![渲染结果](asset/render_show.png)

## 部署方式

前端位于端口5173, 后端位于端口5000, 需预先避免端口占用

### 后端

- 依赖安装
    - 开发使用的python版本为3.12.9, 所依赖的库均在requirements.txt中指出
    - plus: 训练和推理都用到了Nvidia的GPU, 需要安装gpu版本的torch
- 启动
    - 开发环境: 直接用python运行app.py即可
    - 正式环境: 建议使用Gunicorn部署

### 前端

- 依赖安装
    - 使用npm作为包管理器, npm install即可
- 启动
    - npm run dev即可以开发模式部署, 用于测试
    - 若需要构建, 则使用npm run build