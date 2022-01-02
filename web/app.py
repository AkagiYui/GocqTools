import threading
from logging import Logger
from paste import httpserver
from bottle import Bottle
from ay_advance import AyDict, HiddenPrints


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

    def __init__(self, config: AyDict, logger: Logger):
        if config:
            self.__config = config
        self.__username = self.__config['web.username']
        self.__password = self.__config['web.password']
        self.__host = self.__config['web.host']
        self.__port = self.__config['web.port']
        self.__logger = logger

        self.app.add_hook('before_request', self.before_route)
        # self.__thread = threading.Thread(
        #     target=bottle_run,
        #     kwargs={
        #         'app': self.app,
        #         'server': 'paste',
        #         'host': self.__host,
        #         'port': self.__port,
        #         'quiet': True,
        #     }
        # )
        # self.__thread = threading.Thread(
        #     target=httpserver.serve,
        #     args=(self.app, self.__host, self.__port),
        #     daemon=True
        # )
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
        with HiddenPrints(False):
            self.__server.serve_forever()
            # self.app.run(
            #            # server='paste',
            #            host=self.__host,
            #            port=self.__port,
            #            quiet=True
            #            )

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__server.server_close()
        # self.__thread.join()

    def before_route(self):
        self.__logger.debug('before_route')


@Web.app.error(404)
def error_404(_):
    return '404'


@Web.app.route('/', method=['GET'])
def index():
    return {'a': 'Hello World!测试'}
