from typing import List

import requests

from common.consts import BEE_URL

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
