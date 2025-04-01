import json
import logging
from datetime import datetime
from pathlib import Path

"""
JsonFormatter json格式化器
用于规范化日志的格式
"""


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "@timestamp": datetime.now().isoformat() + "Z",
            "caller": f"{Path(record.pathname).name}:{record.lineno}",  # 只记录文件名和行号
            "content": record.getMessage(),
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
