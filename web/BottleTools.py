import json

from bottle import request, HTTPError, response
import inspect
from functools import wraps
import jwt

error_msg = {
    200: '',
    401: 'unauthorized',
    403: 'forbidden',
    404: 'not found',
    405: 'method not allowed',
    500: 'internal server error',
}


def return_content(code: int = 200, data=None, msg: str = ''):
    if msg:
        message = msg
    else:
        try:
            message = error_msg[code]
        except KeyError:
            message = 'unknown error'
    result = {
        'code': code,
        'msg': message,
        'data': data
    }
    if code != 200:
        response.status = code
        response.set_header('Content-Type', 'application/json')
        result = json.dumps(result)
    return result


class BottleJwt:
    name = 'BottleJwt'  # 插件名
    api = 2  # api版本
    keyword = 'auth'  # 插件参数

    jwt_encode = {}
    jwt_prefix = 'Bearer'.lower()

    def __init__(self, validation, key, algorithm='HS256', headers=None):
        self.jwt_encode = {
            'key': key,
            'algorithm': algorithm,
            'headers': headers
        }
        self.jwt_decode = {
            'key': key,
            'algorithms': [algorithm],
        }

        self.validation = validation

    # 获取jwt
    def encode(self, data):
        return jwt.encode(data, **self.jwt_encode)

    # 解密jwt
    def decode(self, data):
        try:
            r = jwt.decode(data, **self.jwt_decode)
            return r
        except jwt.InvalidTokenError:
            return None

    def get_token(self):
        try:
            token = request.query.get('access_token', None)
            if token:
                return token
            _type, token = request.headers['Authorization'].split(' ')
            if _type.lower() != self.jwt_prefix:
                return None
            return token
        except:
            return None

    def get_auth(self):
        token = self.get_token()
        if not token:
            return False, return_content(403, None, 'No token')
        decoded = self.decode(token)
        if decoded is None:
            return False, return_content(403, None, 'Bad token')
        # decoded['token'] = token
        return True, decoded

    def apply(self, callback, route):
        auth_value = route.config.get(self.keyword, None)
        if not auth_value:
            # 没有配置，则不验证
            return callback

        @wraps(callback)
        def wrapper(*args, **kwargs):
            ok, auth = self.get_auth()
            if not ok:
                return auth
            if self.validation(auth, auth_value):
                sig = inspect.getfullargspec(callback)
                if self.keyword in sig.args:
                    kwargs[self.keyword] = auth
                return callback(*args, **kwargs)
            else:
                return return_content(401)

        return wrapper
