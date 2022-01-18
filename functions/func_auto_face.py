import hashlib
import re
from datetime import datetime
from typing import Iterator

import requests

from ay_advance import chinese_to_int, AyStr
from ay_advance.GocqConnection import CqCode
import random
from sqlalchemy import Column, Integer, String, DateTime, or_, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from ay_advance import GocqConnection
from global_variables import get_global

logger = get_global('logger')
db_engine = get_global('db_engine')
db_session = get_global('db_session')
Base = declarative_base()

module_name = '自动表情'
module_version = '0.0.1'


class TableKey(Base):
    __tablename__ = 'auto_face_key'
    key = Column(String(15), primary_key=True)
    group_id = Column(String(15), primary_key=True)
    face_id = Column(String(32))
    user_id = Column(String(15))


class TableFace(Base):
    __tablename__ = 'auto_face_data'
    face_id = Column(String(32), primary_key=True)
    data = Column(LargeBinary)


def init():
    global logger, db_engine, db_session
    logger = get_global('logger')
    db_engine = get_global('db_engine')
    db_session = get_global('db_session')
    Base.metadata.create_all(db_engine)

    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


def get_face(face_id: str):
    session = db_session()
    found = session.query(TableFace.data).filter(TableFace.face_id == face_id).first()
    session.close()
    if found is not None:
        return found[0]
    return None


def del_face(face_id: str):
    session = db_session()
    deleted = session.query(TableFace).filter(TableFace.face_id == face_id).delete()
    session.commit()
    session.close()
    return deleted


def add_face(face_id: str, data: bytes):
    new_face = TableFace(face_id=face_id, data=data)
    session = db_session()
    session.add(new_face)
    session.commit()
    session.close()


def get_id(key: str, group_id: str):
    session = db_session()
    found = session.query(TableKey.face_id).filter(TableKey.key == key, TableKey.group_id == group_id).first()
    session.close()
    if found is not None:
        return found[0]
    return None


def add_key(key: str, group_id: str, face_id: str, user_id: str):
    session = db_session()
    new_key = TableKey(key=key, group_id=group_id, face_id=face_id, user_id=user_id)
    session.add(new_key)
    session.commit()
    session.close()


def del_key(key: str, group_id: str):
    session = db_session()
    deleted = session.query(TableKey).filter(TableKey.key == key, TableKey.group_id == group_id).delete()
    session.commit()
    session.close()
    return deleted


word_add = ['新增', '增加', '增添', '添加', '来点', '修改']  # 增加关键词
word_del = ['删除', '去除', '去掉', '不要']  # 删除关键词
word_face = ['表情']
regex_text = r'\[CQ:image,file=[^\]]+,url=([^\]]+)\]'


# 返回 0继续处理 1终止处理
def main(conn: GocqConnection, msg):
    if msg['post_type'] != 'message':
        return 0
    if msg['message_type'] != 'group':
        return 0
    try:
        group_id = msg['group_id']
    except KeyError:
        return 0

    message: str = msg['message'].strip()
    sender = msg['sender']['user_id']
    send_msg = ''

    # 增加表情
    tmp_list: list = AyStr(message).find(word_add)
    try:
        tmp_index = tmp_list.index(0)
        message = message.removeprefix(word_add[tmp_index]).lstrip()
        tmp_list: list = AyStr(message).find(word_face)
        try:
            tmp_index = tmp_list.index(0)
            message = message.removeprefix(word_face[tmp_index]).lstrip()
            message = AyStr(message).replace_all('\n', '')
            tmp_list: Iterator = re.finditer(regex_text, message)
            start_index = 0
            for each in tmp_list:
                keyword = message[start_index:each.span()[0]].strip()
                if keyword == '':
                    continue
                if get_id(keyword, group_id) is not None:
                    continue
                url = each.group(1)
                start_index = each.span()[1]
                image_data: bytes = requests.get(url).content
                image_md5: str = hashlib.md5(image_data).hexdigest()
                if get_face(image_md5) is None:
                    add_face(image_md5, image_data)
                del image_data
                add_key(keyword, group_id, image_md5, sender)
                send_msg += f'已为「{keyword}」添加表情\n'
            send_msg = send_msg.rstrip()
        except ValueError:
            return 0
    except ValueError:
        pass

    if send_msg != '':
        msg['message'] = send_msg
        conn.Api.send_message(msg)
        return 1

    # 匹配表情
    face_id = get_id(key=message, group_id=group_id)
    if face_id:
        face_data = get_face(face_id=face_id)
        if face_data:
            send_msg = CqCode.image(face_data)
        else:
            logger.debug(f'找不到表情 {face_id}')
            return 0
    else:
        return 0

    if send_msg != '':
        msg['message'] = send_msg
        conn.Api.send_message(msg)
        return 1
    else:
        return 0
