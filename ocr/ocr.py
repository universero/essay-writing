from flask import Blueprint, request

from common import util
from ocr.bee import bee

bp = Blueprint('orc', __name__)


@bp.post("/ocr/bee")
def ocr():
    # 获取图片的base64数组
    images = request.json.get("images")
    titles = [img["image"] for img in images if img["class"] == 0]
    contents = [img["image"] for img in images if img["class"] == 1]
    title = util.convert_punctuation_to_chinese(bee(titles))
    content = util.convert_punctuation_to_chinese(bee(contents))
    print(title)
    print(content)
    return {"title": title,
            "content": content}
