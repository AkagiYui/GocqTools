from ay_advance.AyDict import AyDict
from ay_advance.GocqConnection import GocqConnection
from global_variables import get_global
logger = get_global('Logger')


def router_init():
    global logger
    logger = get_global('Logger')
    logger.debug('路由已加载')


function_list = AyDict({
    'wo_chi_sha': {
        'status': False
    }
})


def event_message(conn: GocqConnection, msg: dict):
    self_id = conn.info['nickname']
    logger.info(f'{self_id} - {msg}')
    if msg['post_type'] == 'message':
        if msg['message_type'] == 'private':
            if msg['message'] == '233':
                conn.Api.send_private_message(msg['sender']['user_id'], '你发了233啊')


def event_connected(connection: GocqConnection):
    nickname = connection.info['nickname']
    user_id = connection.info['user_id']
    logger.info(f'{nickname}({user_id}) - 已连接')
