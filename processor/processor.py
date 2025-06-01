from flask import request
from flask.sansio.blueprints import Blueprint

from common import rex

bp = Blueprint("processor", __name__)


@bp.post("/process")
def process():
    # 前端上传的图片列表, 对列表中每一个元素执行read方法就能拿到二进制文件
    imgs = request.files.getlist("images")
    # TODO 完成处理逻辑, 如果返回的是图片列表最好是把图片全编码成base64, 然后返回的result是一个字符串数组
    result = []
    return rex.succeed(result)
