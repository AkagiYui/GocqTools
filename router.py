from importlib import import_module
from types import ModuleType
from typing import Type
from ay_advance import GocqConnection
from ay_advance.GocqConnection import CqCode
from global_variables import get_global, set_global

logger = get_global('logger')

# 功能列表
# status: 0 未加载模块 1 已加载模块
function_list = [
    {
        'name': 'wo_chi_sha',
        'status': 0,
        'switch': True,
        'module': Type[ModuleType],
    },
    {
        'name': 'server_info',
        'status': 0,
        'switch': True,
        'module': Type[ModuleType],
    },
    {
        'name': 'zhan_bu',
        'status': 0,
        'switch': True,
        'module': Type[ModuleType],
    },
{
        'name': 'pdf_to_png',
        'status': 0,
        'switch': True,
        'module': Type[ModuleType],
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
    # if msg['post_type'] == 'message':
    #     pass
    #
    # elif msg['post_type'] == 'notice':
    #     pass
    if 'message' not in msg.keys():
        msg['message'] = ''
    if msg['message'].strip() == CqCode.at(conn.info['user_id']):
        msg['message'] = '干嘛'
        conn.Api.send_message(msg)
        return
    call_function(conn, msg)


def call_function(conn: GocqConnection, msg: dict):
    functions = function_list
    for function in functions:
        if not function['switch']:
            continue
        module = function['module']
        if module.main(conn, msg) == 0:
            pass
        else:
            break


def event_connected(conn: GocqConnection):
    nickname = conn.info['nickname']
    user_id = conn.info['user_id']
    logger.info(f'{nickname}({user_id}) - 已连接')
    set_global(user_id, nickname)
