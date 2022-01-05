import os
from datetime import datetime
import platform
import random

import psutil

from ay_advance import GocqConnection
from global_variables import get_global

logger = get_global('logger')

module_name = '服务器信息'
module_version = '0.0.1'


def init():
    global logger
    logger = get_global('logger')
    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


word_prefix = '服务器信息'


# 返回 0继续处理 1终止处理
def main(conn: GocqConnection, msg):
    message = msg['message']
    if message != word_prefix:
        return 0

    self_nickname = conn.info['nickname']
    user_id = conn.info['user_id']
    platform_system = platform.system()
    # platform_version = platform.version()
    platform_version = platform.release()
    platform_memory = psutil.virtual_memory()
    platform_memory_usage = 1 - platform_memory.available / platform_memory.total
    platform_memory_usage *= 100
    platform_memory_usage = round(platform_memory_usage, 4)
    boot_time = datetime.fromtimestamp(psutil.boot_time())

    self_process = psutil.Process(os.getpid())

    start_time = self_process.create_time()
    start_time = datetime.fromtimestamp(start_time)
    curr_time = datetime.now()
    uptime = curr_time - boot_time
    uptime = str(uptime).split('.')[0]
    uptime2 = curr_time - start_time
    uptime2 = str(uptime2).split('.')[0]

    message_sent = conn.info['stat']['message_sent']
    message_received = conn.info['stat']['message_received']

    send_msg = f'登录用户：{self_nickname}({user_id})\n'
    send_msg += f'收发消息数：{message_received}/{message_sent}\n'
    send_msg += f'操作系统：{platform_system} {platform_version}\n'
    send_msg += f'Python版本：{platform.python_version()}\n'
    # send_msg += f'系统CPU使用率：{psutil.cpu_percent()}%\n'
    # send_msg += f'脚本CPU使用率：{self_process.cpu_percent(1)}%\n'
    send_msg += f'系统内存使用率：{platform_memory_usage}%\n'
    send_msg += f'脚本内存使用率：{round(self_process.memory_percent(), 4)}%\n'
    send_msg += f'系统启动时长：{uptime}\n'
    send_msg += f'脚本运行时长：{uptime2}'

    msg['message'] = send_msg
    conn.Api.send_message(msg)
    return 1
