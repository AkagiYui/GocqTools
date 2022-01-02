import threading
from time import sleep

from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from global_variables import set_global

Base = declarative_base()


class GocqConnection(Base):
    __tablename__ = 'gocq_connection'
    host = Column(String(50), primary_key=True)
    ws_port = Column(Integer, primary_key=True)
    api_port = Column(Integer, primary_key=True)
    access_token = Column(String(255))
    auto_connect = Column(Boolean, default=False, server_default='0')


class Mysql:
    __engine = None
    __DBSession = None
    __gocq_connection = []

    __go_on = True

    def __keep_db(self, _):
        while self.__go_on:
            session = self.__DBSession()
            result = session.execute('select 1+1')
            session.close()
            result.close()
            if self.__go_on:
                sleep(5)

    __keep_db_thread = None

    def close(self):
        self.__go_on = False
        # self.__keep_db_thread.join()
        self.__engine.dispose()

    def __del__(self):
        if self.__keep_db_thread.is_alive():
            self.__go_on = False

    def __init__(self, host: str, port: int, database: str, username: str, password: str,
                 echo: bool = False, max_connection: int = 10):
        # 连接数据库
        try:
            connection_string = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8' \
                .format(username, password, host, port, database)
        except Exception as e:
            raise e

        self.__engine = create_engine(connection_string,
                                      echo=echo,
                                      pool_size=max_connection,
                                      pool_recycle=3600,
                                      pool_timeout=30,
                                      pool_pre_ping=True,
                                      )
        self.__DBSession = sessionmaker(bind=self.__engine)

        # 创建表结构
        Base.metadata.create_all(self.__engine)

        set_global('db_engine', self.__engine)
        set_global('db_session', self.__DBSession)

        # 防数据库掉线
        self.__keep_db_thread = threading.Thread(
            target=self.__keep_db,
            args=(self,),
            daemon=True,
        )
        self.__keep_db_thread.start()

    def get_gocq_connections(self, use_cache: bool = True):
        if use_cache and len(self.__gocq_connection) > 0:
            return self.__gocq_connection

        session = self.__DBSession()
        users = session.query(GocqConnection).all()
        result = []
        for user in users:
            new_member = {
                'host': user.host.strip(),
                'ws_port': user.ws_port,
                'api_port': user.api_port,
                'auto_connect': user.auto_connect,
                'access_token': user.access_token
            }
            result.append(new_member)
        session.close()
        self.__gocq_connection = result
        return result
