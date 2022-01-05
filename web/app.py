import json
import os
import sys
import threading
import time
from importlib import import_module
from logging import Logger
from .routes import *

from .BottleTools import BottleJwt, return_content
from paste import httpserver
from bottle import Bottle, static_file, response, request, TEMPLATE_PATH, jinja2_template as template, TEMPLATES, \
    redirect
from ay_advance import AyDict, get_self_ip
from global_variables import set_global, get_global

path_self = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path_self)
path_assets = os.path.join(path_self, 'assets')
path_images = os.path.join(path_self, 'images')
path_views = os.path.join(path_self, 'views')
TEMPLATE_PATH.append('./web/views')
jwt: BottleJwt
config: AyDict = AyDict({})


def validation(auth, value):
    if auth['username'] == get_global('web_username'):
        return True
    return False


class Web:
    __instance: object = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    __config: AyDict = None

    app = Bottle()
    set_global('app', app)
    server = None
    __username = ''
    __password = ''
    __host = ''
    __port = 5050
    __logger: Logger = None
    __thread: threading.Thread = None
    __server = None
    __jwt = None

    def __init__(self, conf: AyDict, logger: Logger):
        if conf:
            self.__config = conf
            global config
            config = conf

        self.__username = self.__config['web.username']
        self.__password = self.__config['web.password']
        set_global('web_username', self.__username)
        set_global('web_password', self.__password)
        self.__host = self.__config['web.host']
        self.__port = self.__config['web.port']
        self.__logger = logger
        global jwt
        jwt = BottleJwt(validation, self.__config['web.secret'], algorithm='HS256')
        set_global('jwt', jwt)

        self.app.add_hook('before_request', self.before_request)
        self.app.add_hook('after_request', self.after_request)
        self.app.install(jwt)
        self.__server = httpserver.serve(self.app,
                                         host=self.__host,
                                         port=self.__port,
                                         start_loop=False
                                         )
        self.__thread = threading.Thread(
            target=self.__start,
            daemon=True
        )
        import_module('web.routes.views')

    def __start(self):
        self.__server.serve_forever()

    def start(self):
        self.__thread.start()
        self.__logger.info('Web url http://%s:%d', get_self_ip(), self.__port)

    def stop(self):
        self.__server.server_close()
        # self.__thread.join()

    def before_request(self):
        self.__logger.debug('%s %s', request.method, request.path)

    @staticmethod
    def after_request():
        TEMPLATES.clear()

