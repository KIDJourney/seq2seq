import re
import os
import json

import requests
from bs4 import BeautifulSoup
from multiprocessing import Lock, Process

from logger import logger
from utils import add_signal_handler, init_script

CHINESE_RE = re.compile("[\u4e00-\u9fff]+")
POETRY_RE = re.compile(r'[\u4e00-\u9fff]+，[\u4e00-\u9fff]+')
CRAWLER_CONFIG_PATH = "./config/crawler_check_point.json"
URL_TEMPLATE = "http://so.gushiwen.org/mingju/ju_%s.aspx"


def url_generator():
    check_point = 0
    if os.path.exists(CRAWLER_CONFIG_PATH):
        with open(CRAWLER_CONFIG_PATH) as f:
            try:
                check_point_data = json.loads(f.read())
                check_point = check_point_data.get('check_point', check_point)
            except Exception:
                logger.warning('get checkpoint failed, start from beginning')

    for i in range(check_point, 6000):
        url = URL_TEMPLATE % i
        if i % 10 == 0:
            with open(CRAWLER_CONFIG_PATH, 'w') as f:
                f.write(json.dumps({
                    'check_point': i
                }))
        yield url, i


def get_poetry(url, index):
    ret = {}
    try:
        content = requests.get(url, timeout=1).text
    except Exception:
        logger.exception('get http data failed url=%s', url)
        return ret

    soup = BeautifulSoup(content, "html.parser")
    divs = soup.find_all('div', {'class': 'contson'})
    if divs:
        poetry_text = divs[0].text.strip()
    else:
        logger.warning("can't get poetry content from url=%s", url)
        return ret

    poetry_parts = POETRY_RE.findall(poetry_text)

    data = []
    for poetry_sen in poetry_parts:
        pair = CHINESE_RE.findall(poetry_sen)
        if len(pair) == 2 and len(pair[0]) == len(pair[1]) and (pair[0] != pair[1]):
            data.append(pair)

    ret[index] = data
    return ret


def save_poetry_pair(poetry_pairs):
    saved_data = []
    if os.path.exists('train_data.json'):
        with open("train_data.json") as f:
            saved_data = json.loads(f.read())

    saved_data.update(poetry_pairs)
    with open("./data/train_data.json", 'w') as f:
        f.write(json.dumps(poetry_pairs))


def signal_handler(poetry_dict):
    def wrapper(signal, frame):
        save_poetry_pair(poetry_pair)

    return wrapper


if __name__ == "__main__":
    poetry_pair = {}

    add_signal_handler(signal_handler(poetry_pair))
    init_script()

    for url, index in url_generator():
        print(url, index)
        poetry_pair.update(get_poetry(url, index))

    save_poetry_pair(poetry_pair)
