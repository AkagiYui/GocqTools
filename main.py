import getopt
import json
import logging
from time import sleep

import colorlog
import sys
import signal

from dotenv import dotenv_values
from ay_advance.AyDict import AyDict
from database.connection import Mysql
from router import *
from global_variables import set_global

config_path = './config.json'
mode_debug = False

MAIN_NAME = 'GocqTools'
MAIN_VERSION = 3
MAIN_VERSION_TEXT = '0.0.3'


def print_help_text():
    print('Usage: python ./main.py [options]')
    print('Options:')
    print('-h --help : 输出本信息')
    print('-c --config : 指定配置文件(默认:./config.json)')
    print('-d --debug : 输出调试信息')


time_to_exit = False


def signal_handler(sign, frame):
    if sign == signal.SIGINT or sign == signal.SIGTERM:
        global time_to_exit
        time_to_exit = True


def main_exit():

    for conn in connections:
        conn['main'].stop_connection()
    database.close()
    sleep(0.1)
    logger.info('程序退出，欢迎下次使用')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 读取启动参数
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'dhc:', ['debug', 'help', 'config='])
    except getopt.GetoptError:
        print('参数错误')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help_text()
            sys.exit(0)
        if opt in ('-c', '--config'):
            config_path = arg
        if opt in ('-d', '--debug'):
            mode_debug = True

    # 加载配置文件
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            config = AyDict(config)
    except FileNotFoundError:
        print('配置文件不存在')
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        print('配置文件解析错误')
        sys.exit(1)

    # 初始化日志
    log_level = config['log.level']
    if log_level == 'debug':
        log_level = logging.DEBUG
    elif log_level == 'warning':
        log_level = logging.WARNING
    elif log_level == 'error':
        log_level = logging.ERROR
    elif log_level == 'critical':
        log_level = logging.CRITICAL
    elif mode_debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = logging.getLogger(MAIN_NAME)
    logger.setLevel(log_level)

    log_colors_config = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    console_handler = logging.StreamHandler()
    console_handler.setLevel(-1000)
    console_handler.setFormatter(colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors=log_colors_config
    ))
    if not logger.handlers:
        logger.addHandler(console_handler)

    set_global('Logger', logger)
    logger.info('%s v%s', MAIN_NAME, MAIN_VERSION_TEXT)
    logger.debug('version: %d', MAIN_VERSION)

    # 读取环境变量
    env = dotenv_values('./.env')
    for key, value in env.items():
        new_key = key.lower().replace('_', '.')
        new_value = int(env[key]) if env[key].isdigit() else env[key]
        config[new_key] = new_value

    # 连接数据库
    try:
        database = Mysql(
            host=config['db.host'],
            port=config['db.port'],
            database=config['db.database'],
            username=config['db.username'],
            password=config['db.password'],
            echo=False
        )
    except Exception as e:
        logger.error('数据库连接失败: %s', e)
        sys.exit(1)
    logger.debug('数据库连接成功')
    # set_global('db', database)

    # 启动路由
    router_init()

    connections = database.get_gocq_connections()
    for connection in connections:
        # if not connection['auto_connect']:
        #     continue
        connection['main'] = GocqConnection(
            host=connection['host'],
            ws_port=connection['ws_port'],
            api_port=connection['api_port'],
            access_token=connection['access_token'],
            daemon=True,
            auto_connect=connection['auto_connect'],
            on_message=event_message,
            on_connected=event_connected,
        )
        # connection['connection'].start_connection(False)

    while True:
        if time_to_exit:
            main_exit()
        sleep(0.5)
