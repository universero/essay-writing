from flask import Blueprint, request

from ocr.post import *
from ocr.bee import bee

"""
ocr.py 定义ocr相关接口
"""

bp = Blueprint('orc', __name__)


@bp.post("/ocr/bee")
def ocr():
    # 获取图片的base64数组
    images = request.json.get("images")
    titles = [img["image"] for img in images if img["class"] == 0]
    contents = [img["image"] for img in images if img["class"] == 1]
    title = convert_punctuation_to_chinese(bee(titles))
    content = convert_punctuation_to_chinese(bee(contents))
    print(title)
    print(content)
    return {"title": title,
            "content": content}
