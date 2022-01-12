import os
import sys
import time

from bottle import request, redirect, jinja2_template as template, response, static_file

from global_variables import get_global
from web.BottleTools import return_content

config = get_global('config')
app = get_global('app')
jwt = get_global('jwt')
path_self = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path_self)
parent_path = os.path.dirname(path_self)
path_assets = os.path.join(parent_path, 'assets')


def is_login():
    return request.get_cookie('token', secret=config['web.secret']) == get_global('web_username')


@app.route('/', ['GET'])
def api_root():
    # username = request.get_cookie('token', secret=config['web.secret'])
    if is_login():
        return template('index', template_info)
    else:
        redirect('/login')


@app.route('/login', ['POST', 'GET'])
def api_login():
    if is_login():
        redirect('/')
    if request.method == 'POST':
        try:
            username = request.json.get('username')
            password = request.json.get('password')
        except AttributeError:
            return return_content(401)
        if username == get_global('web_username') and password == get_global('web_password'):
            response.set_cookie('token', username, secret=config['web.secret'])
            payload = {
                'username': username,
                'exp': int(time.time()) + 3600 * 24
            }
            template_info['login'] = True
            return return_content(200, jwt.encode(payload))
        else:
            return return_content(401)
    else:
        return template('login', template_info)


@app.route('/logout', ['GET', 'POST'])
def api_logout():
    if is_login():
        template_info['login'] = False
        response.delete_cookie('token')
    redirect('/')
    # return return_content(404)


@app.route('/assets/<filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif|.*\.ico>')
def server_static(filename):
    return static_file(filename, root=path_assets)


@app.error(404)
def error_404(_):
    return return_content(404)


@app.error(405)
def error_405(_):
    return return_content(405)


@app.route('/test', ['GET', 'POST'], auth='t')
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
