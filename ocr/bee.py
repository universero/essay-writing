import requests
import json

from flask import Blueprint, request

bp = Blueprint('orc', __name__)

payload = json.dumps({
    "images": [
        "https://cos.ap-shanghai.myqcloud.com/cs-homework-1305192562/18871454419_12C06961F3424A8ErB7707XC.jpg"
    ],
    "leftType": "all"
})
headers = {
    'X-Xh-Env': 'test',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)


@bp.post("/ocr/bee")
def ocr_bee():
    # 获取图片的base64数组
    images = request.json.get("images")
