"""
consts.py 常量定义
"""

# 是否为测试环境
MODE = "test"

# BETA 版批改接口
BETA_URL = "https://api.xhpolaris.com/essay/evaluate"
MICRO_URL = "http://52.131.210.24/api/score"
BEE_URL = "https://api.xhpolaris.com/essay/sts/ocr/bee/base64"
# 测试环境的请求头
TEST_HEADER = {
    'X-Xh-Env': 'test',
    'Content-Type': 'application/json'
}

ZH_NO = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
