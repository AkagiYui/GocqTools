from gevent import monkey
monkey.patch_all()

import psutil
import getopt
import json
import logging
from time import sleep
import colorlog
import sys
import signal
from dotenv import dotenv_values
from ay_advance import AyDict
from GocqTools import GocqTools
from router import *
from global_variables import set_global

config_path = './config.json'
mode_debug = False
time_to_exit = False

MAIN_NAME = 'GocqTools'
MAIN_VERSION = 12
MAIN_VERSION_TEXT = '0.3.2'


def print_help_text():
    print('Usage: python ./main.py [options]')
    print('Options:')
    print('-h --help : 输出本信息')
    print('-c --config : 指定配置文件(默认:./config.json)')
    print('-d --debug : 输出调试信息')
    print('-v --version : 输出版本信息')


def signal_handler(sign, _):
    if sign == signal.SIGINT or sign == signal.SIGTERM:
        global time_to_exit
        time_to_exit = True


def main_exit(go_cq_tools: GocqTools):
    go_cq_tools.stop()
    go_cq_tools.exit()
    sleep(0.1)
    logger.info('程序退出，欢迎下次使用')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 读取启动参数
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vdhc:', ['version', 'debug', 'help', 'config='])
    except getopt.GetoptError:
        print('参数错误')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-v', '--version'):
            print(MAIN_NAME + ' ' + MAIN_VERSION_TEXT)
            sys.exit(0)
        if opt in ('-h', '--help'):
            print_help_text()
            sys.exit(0)
        if opt in ('-c', '--config'):
            config_path = arg
        if opt in ('-d', '--debug'):
            mode_debug = True
            set_global('debug', True)
        else:
            set_global('debug', False)

    # 加载配置文件
    try:
        with open(config_path, 'r') as f:
            conf = json.load(f)
            conf = AyDict(conf)
            set_global('config', conf)
    except FileNotFoundError:
        print('配置文件不存在')
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        print('配置文件解析错误')
        sys.exit(1)

    conf['debug'] = mode_debug

    # 初始化日志
    log_level = conf['log.level']
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

    logger = logging.getLogger('werkzeug')
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

    set_global('console_handler', console_handler)
    set_global('logger', logger)
    logger.info('%s v%s', MAIN_NAME, MAIN_VERSION_TEXT)
    logger.debug('version: %d', MAIN_VERSION)

    # 读取环境变量
    env = dotenv_values('./.env')
    for key, value in env.items():
        new_key = key.lower().replace('_', '.')
        new_value = int(env[key]) if env[key].isdigit() else env[key]
        conf[new_key] = new_value

    psutil.cpu_percent()
    # 启动主程序
    main = GocqTools(conf(), logger)
    set_global('main', main)
    main.init()
    main.start()

    while True:
        if time_to_exit:
            main_exit(main)
        sleep(0.5)
