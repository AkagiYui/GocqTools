from logging import Logger
from ay_advance import AyDict, GocqConnection
from database.connection import Mysql
from router import router_init, event_message, event_connected
from web.app import Web


class GocqTools:
    __instance: object = None

    __config: AyDict = None
    __logger: Logger = None
    __database: Mysql = None
    __web: Web = None
    __ready: bool = False
    __start: bool = False
    __ws_connections: list = []

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return '警告：这是个单例'

    def __init__(self, config: dict = None,
                 logger: Logger = None,
                 ):
        self.set_config(config)
        self.__logger = logger

    def set_config(self, config: dict = None):
        if config is None:
            config = {}
        self.__config = AyDict(config)

    def init(self):
        self.__web = Web(self.__config, self.__logger)
        self.__ready = True

    def exit(self):
        self.__ready = False

    # 阻塞等待
    def start(self):
        if not self.__ready:
            self.__logger.error('未初始化')
            return False
        if self.__start:
            self.__logger.error('已启动')
            return False
        self.__start = True
        self.__start_database()
        self.__start_web()

        router_init()
        self.__start_websocket()

    def stop(self):
        self.__stop_web()
        self.__stop_websocket()
        self.__stop_database()

    def __start_database(self):
        database = None
        try:
            database = Mysql(
                host=self.__config['db.host'],
                port=self.__config['db.port'],
                database=self.__config['db.database'],
                username=self.__config['db.username'],
                password=self.__config['db.password'],
                echo=False
            )
        except Exception as e:
            self.__logger.error('数据库连接失败: %s', e)

        self.__database = database
        self.__logger.debug('数据库连接成功')

    def __start_web(self):
        try:
            self.__web.start()
        except Exception as e:
            self.__logger.error(f'web启动失败: {e}')
        finally:
            self.__logger.debug('web启动成功')

    def __start_websocket(self):
        connections = self.__database.get_gocq_connections()
        for conn in connections:
            conn['main'] = GocqConnection(
                host=conn['host'],
                ws_port=conn['ws_port'],
                api_port=conn['api_port'],
                access_token=conn['access_token'],
                daemon=True,
                auto_connect=conn['auto_connect'],
                on_message=event_message,
                on_connected=event_connected,
                auto_reconnect=True,
            )
            # connection['connection'].start_connection(False)

    def __stop_database(self):
        self.__database.close()

    def __stop_web(self):
        self.__web.stop()

    def __stop_websocket(self):
        for conn in self.__ws_connections:
            conn['main'].stop_connection()
