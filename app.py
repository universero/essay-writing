from flask import Flask
from flask_cors import CORS

from common.log import log_init


def create_app():
    """
    创建并配置 Flask
    """
    # 创建 Flask 应用实例
    the_app = Flask(__name__)
    # 注册蓝图

    # 初始化日志配置
    log_init()
    # 初始化跨域策略配置
    CORS(the_app)

    return the_app


if __name__ == '__main__':
    # 创建并配置 Flask 应用
    app = create_app()
    # 运行 Flask 应用
    app.run("0.0.0.0", port=5000)
