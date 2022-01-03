import json
import os
import sys
import threading
import time
from logging import Logger

from .BottleTools import BottleJwt, return_content
from paste import httpserver
from bottle import Bottle, static_file, response, request, TEMPLATE_PATH, jinja2_template as template, TEMPLATES
from ay_advance import AyDict
from global_variables import set_global, get_global

path_self = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path_self)
path_assets = os.path.join(path_self, 'assets')
path_images = os.path.join(path_self, 'images')
path_views = os.path.join(path_self, 'views')
TEMPLATE_PATH.append('./web/views')
jwt: BottleJwt


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
    server = None
    __username = ''
    __password = ''
    __host = ''
    __port = 5050
    __logger: Logger = None
    __thread: threading.Thread = None
    __server = None
    __jwt = None

    def __init__(self, config: AyDict, logger: Logger):
        if config:
            self.__config = config
        self.__username = self.__config['web.username']
        self.__password = self.__config['web.password']
        set_global('web_username', self.__username)
        set_global('web_password', self.__password)
        self.__host = self.__config['web.host']
        self.__port = self.__config['web.port']
        self.__logger = logger
        global jwt
        jwt = BottleJwt(validation, self.__config['web.secret'], algorithm='HS256')

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

    def __start(self):
        self.__server.serve_forever()

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__server.server_close()
        # self.__thread.join()

    def before_request(self):
        self.__logger.debug('web %s', request.path)

    @staticmethod
    def after_request():
        TEMPLATES.clear()


@Web.app.route('/login', ['POST','GET'])
def api_login():
    if request.method == 'POST':
        try:
            username = request.json.get('username')
            password = request.json.get('password')
        except AttributeError:
            return return_content(401)
        if username == get_global('web_username') and password == get_global('web_password'):
            # response.set_cookie('token', username, secret='this is a secret')
            payload = {
                'username': username,
                'exp': int(time.time()) + 3600 * 24
            }
            return return_content(200, jwt.encode(payload))
        else:
            return return_content(401)
    else:
        return template('login', template_info)


@Web.app.route('/logout', ['POST'], auth='t')
def api_logout():
    return return_content(404)


@Web.app.route('/assets/<filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif|.*\.ico>')
def server_static(filename):
    return static_file(filename, root=path_assets)


@Web.app.error(404)
def error_404(_):
    return return_content(404)


@Web.app.error(405)
def error_405(_):
    return return_content(405)


@Web.app.route('/', ['GET'])
def api_root():
    # return return_content(200, 'hello')
    t = template('index', template_info)

    return t


@Web.app.route('/test', ['GET', 'POST'], auth='t')
def api_test(auth):
    payload = {
        'method': request.method,
        'auth': auth
    }
    return return_content(200, payload)


template_info = {
    'title': 'Tools',
    'current': ''
}
