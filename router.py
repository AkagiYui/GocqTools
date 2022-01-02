from importlib import import_module
from types import ModuleType
from typing import Type
from ay_advance import GocqConnection
from global_variables import get_global

logger = get_global('logger')

# 功能列表
# status: 0 未加载模块 1 已加载模块
function_list = [
    {
        'name': 'wo_chi_sha',
        'status': 0,
        'switch': True,
        'module': Type[ModuleType],
        'prefix': '',
        'suffix': ''
    },
]


def router_init():
    global logger
    logger = get_global('logger')

    # 加载功能模块
    functions = function_list
    for function in functions:
        func_name = function['name']
        module = import_module(f'functions.{func_name}')
        function['module'] = module
        module.init()
        function['status'] = 1
        if function['switch']:
            module.enable()

    logger.debug('路由加载完毕')


def event_message(conn: GocqConnection, msg: dict):
    self_id = conn.info['nickname']
    logger.info(f'{self_id} - {msg}')
    if msg['post_type'] == 'message':
        # 遍历调用模块
        functions = function_list
        for function in functions:
            if not function['switch']:
                continue
            message = msg['message']
            module = function['module']
            if message.find(function['prefix']) == 0 and message.rfind(function['suffix']) == len(message):
                if module.main(conn, msg) == 0:
                    continue
                else:
                    break


def event_connected(connection: GocqConnection):
    nickname = connection.info['nickname']
    user_id = connection.info['user_id']
    logger.info(f'{nickname}({user_id}) - 已连接')
