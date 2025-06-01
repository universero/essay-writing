import json
import logging
from datetime import datetime
from pathlib import Path
import re

"""
JsonFormatter json格式化器
用于规范化日志的格式
"""


def remove_ansi_escape(text):
    """移除所有 ANSI 转义序列（颜色代码等）"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class JsonFormatter(logging.Formatter):

    def format(self, record):
        log_record = {
            "@timestamp": datetime.now().isoformat() + "Z",
            "caller": f"{Path(record.pathname).name}:{record.lineno}",
            "content": remove_ansi_escape(record.getMessage()),  # 移除颜色代码
            "level": record.levelname
        }
        return json.dumps(log_record, ensure_ascii=False)


def log_init():
    """
    初始化日志配置
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
