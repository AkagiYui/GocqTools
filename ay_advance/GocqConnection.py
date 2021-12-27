import json
import requests as http
import websocket
import threading


class GocqConnection:
    __host = ''
    __access_token = ''
    __header = {
        'Authorization': 'Bearer '
    }
    __auto_connect = False

    __api_port = 0
    __api_url = ''
    Api = None

    __ws_port = 0
    __ws_url = ''
    __ws_connection = None
    __ws_connected = False
    __ws_thread_in_daemon = False
    __ws_thread = None
    __ws_event_message = None
    __ws_event_connected = None

    # QQ信息
    info = {
        'user_id': 0,
        'nick_name': '',
    }

    # 根据配置生成url和header
    def __make_url(self):
        # self.__api_url = 'http://{}:{}'.format(self.__host, self.__api_port)
        self.Api = GocqApi(self.__host, self.__api_port, self.__access_token)
        self.__ws_url = 'ws://{}:{}'.format(self.__host, self.__ws_port)
        if not self.__access_token == '':
            self.__header['Authorization'] = 'Bearer ' + self.__access_token

    # 启动ws连接
    def __ws_connect(self):
        self.__ws_connection = websocket.WebSocketApp(
            url=self.__ws_url,
            header=self.__header,
            on_message=self._event_message,
            on_error=self._event_error,
            on_close=self._event_close,
            on_open=self._event_open
        )

        self.__ws_thread = threading.Thread(
            target=self.__ws_connection.run_forever,
            daemon=self.__ws_thread_in_daemon,
            args=()
        )
        self.__ws_thread.start()

    # 关闭ws连接
    def __ws_close(self):
        if self.__ws_thread.is_alive():
            self.__ws_connection.close()

    # 以下是ws事件方法
    def _event_open(self, _):
        self.__ws_connected = True

    def _event_message(self, _, message):
        message = json.loads(message)

        if message['post_type'] == 'meta_event':
            if message['meta_event_type'] == 'lifecycle':
                # 连接成功
                # self.info['self_id'] = message['self_id']
                self.info = self.Api.get_login_info()
                if self.__ws_event_connected:
                    self.__ws_event_connected(self)
                return
            elif message['meta_event_type'] == 'heartbeat':
                # 心跳
                return

        # 其他消息
        if not self.__ws_event_message:
            return
        result_dict = {
            # 'self_id': message['self_id'],
            'post_type': message['post_type'],
            'time': message['time'],
        }

        if message['post_type'] == 'message':
            result_dict['message_type'] = message['message_type']
            result_dict['message'] = message['message']
            result_dict['message_id'] = message['message_id']

            result_dict['sender'] = {}
            result_dict['sender']['user_id'] = message['sender']['user_id']
            result_dict['sender']['nickname'] = message['sender']['nickname']

            # 群消息
            if message['message_type'] == 'group':
                result_dict['sender']['card'] = message['sender']['card']
                result_dict['sender']['title'] = message['sender']['title']
            elif message['message_type'] == 'private':
                pass

            self.__ws_event_message(self, result_dict)
            return

    def _event_error(self, ws, error):
        pass

    def _event_close(self, _):
        self.__ws_connected = False

    def __init__(self,
                 host: str,
                 ws_port: int,
                 api_port: int,
                 access_token: str,
                 auto_connect: bool = False,
                 on_message: callable = None,
                 on_connected: callable = None
                 ):
        self.__host = host
        self.__ws_port = ws_port
        self.__api_port = api_port
        self.__access_token = access_token
        self.__make_url()

        self.__ws_event_message = on_message
        self.__ws_event_connected = on_connected

        self.__auto_connect = auto_connect
        if self.__auto_connect:
            self.start_connection()

    # 以下是公共方法
    # 启动ws连接
    def start_connection(self, in_daemon: bool = False):
        self.__ws_thread_in_daemon = in_daemon
        self.__ws_connect()

    # 关闭ws连接
    def stop_connection(self):
        self.__ws_close()


# noinspection HttpUrlsUsage
class GocqApi:
    __host = ''
    __port = 0
    __header = {
        'Authorization': 'Bearer '
    }
    __base_url = ''

    def __init__(self, host, port, access_token):
        self.__host = host
        self.__port = port
        self.__header['Authorization'] = 'Bearer ' + access_token
        self.__base_url = 'http://{}:{}'.format(self.__host, self.__port)

    def __go_api(self, api: str, method: int = 1, data: dict = None):
        if method == 0:
            result = http.get(self.__base_url + api, headers=self.__header, data=data)
        else:
            result = http.post(self.__base_url + api, headers=self.__header, data=data)
        return result.json()

    def send_private_message(self, send_to: str, message: str, auto_escape: bool = False):
        if send_to is None or message is None:
            return
        url = '/send_private_msg'
        data = {
            'user_id': send_to,
            'message': message,
            'auto_escape': auto_escape
        }
        result = self.__go_api(url, method=1, data=data)
        return result

    def get_login_info(self):
        url = '/get_login_info'
        result = self.__go_api(url)
        return result['data']


class CqCode:
    @staticmethod
    def face(face_id: int):
        return '[CQ:face,id={}]'.format(face_id)

    @staticmethod
    def record(url: str):
        return '[CQ:record,file={}]'.format(url)
