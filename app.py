from flask import Flask
from flask_cors import CORS

from common.log import log_init
from evaluator import evaluator
from locator import locator, locator_test
from ocr import ocr
from processor import process
from render import render


def create_app():
    """
    创建并配置 Flask
    """
    # 创建 Flask 应用实例
    the_app = Flask(__name__)
    # 注册蓝图
    the_app.register_blueprint(evaluator.bp)  # 批改
    the_app.register_blueprint(locator.bp)  # 定位
    the_app.register_blueprint(locator_test.bp)  # 定位测试
    the_app.register_blueprint(ocr.bp)  # ocr
    the_app.register_blueprint(process.bp)  # 图像处理
    the_app.register_blueprint(render.bp)  # 渲染
    # 初始化日志配置
    log_init()
    # 初始化跨域策略配置
    CORS(the_app,supports_credentials=True)

    return the_app


if __name__ == '__main__':
    # 创建并配置 Flask 应用
    app = create_app()
    # 运行 Flask 应用
    app.run("0.0.0.0", port=5000)
