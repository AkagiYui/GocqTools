import os
import random

import requests

from ay_advance import GocqConnection, get_file_format
from ay_advance.GocqConnection import CqCode
from global_variables import get_global

logger = get_global('logger')

module_name = 'PDF自动转PNG'
module_version = '0.0.1'


def init():
    global logger
    logger = get_global('logger')
    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


# 返回 0继续处理 1终止处理
def main(conn: GocqConnection, msg):
    limit_pages = 5
    limit_size = 100
    zoom_times = 5

    if msg['post_type'] != 'notice':
        return 0
    if msg['notice_type'] != 'group_upload':
        return 0
    file_size = msg['file']['size']
    file_size = file_size / 1024 / 1024  # 单位MB
    if file_size > limit_size:
        return 0
    file_name: str = msg['file']['name']
    if file_name.split('.')[-1] != 'pdf':
        return 0
    file_url = msg['file']['url']
    file_content: bytes = requests.get(file_url).content
    file_type = get_file_format(file_content)
    if file_type != 'pdf':
        send_msg = f'文件类型：{file_type}，取消处理'
    else:
        import fitz
        temp_name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba9876543210', 16))
        temp_name = './temp/' + temp_name
        with open(temp_name, 'wb') as f:
            f.write(file_content)
        with fitz.open(temp_name) as pdf:
            page_count = pdf.page_count
            send_msg = f'{file_name}(共{page_count}页) 预览\n'
            logger.debug(f'{file_name}(共{page_count}页)')
            if page_count > limit_pages:
                page_count = limit_pages
            for i in range(page_count):
                mtx = fitz.Matrix(zoom_times, zoom_times)
                image = pdf[i].get_pixmap(matrix=mtx, alpha=False).tobytes()
                send_msg += CqCode.image(image)
        os.remove(temp_name)
    msg['message'] = send_msg
    conn.Api.send_message(msg)
    return 1
