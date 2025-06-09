from typing import List

import requests

from common.consts import BEE_URL

"""
bee.py bee版本的OCR接口调用
"""

payload = {
    "images": [],
    "leftType": "all"
}

headers = {
    'X-Xh-Env': 'test',
    'Content-Type': 'application/json'
}


def bee(imgs: List[str]) -> str:
    payload['images'] = imgs
    resp = requests.post(BEE_URL, json=payload, headers=headers)
    return resp.json()["content"]
