from flask import Blueprint, request

from ocr.bee import bee

bp = Blueprint('orc', __name__)


@bp.post("/ocr/bee")
def ocr():
    # 获取图片的base64数组
    images = request.json.get("images")
    title = [img["image"] for img in images if img["class"] == 0]
    content = [img["image"] for img in images if img["class"] == 1]
    return {"title": bee(title),
            "content": bee(content)}
