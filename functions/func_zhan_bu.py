from datetime import datetime

from ay_advance import GocqConnection, chinese_to_int
from ay_advance.GocqConnection import CqCode
from global_variables import get_global
import random
from sqlalchemy import Column, Integer, String, distinct, DateTime, or_
from sqlalchemy.ext.declarative import declarative_base
from ay_advance import GocqConnection
from global_variables import get_global

logger = get_global('logger')
db_engine = get_global('db_engine')
db_session = get_global('db_session')
Base = declarative_base()

module_name = '占卜'
module_version = '0.0.3'


class TableZhanBu(Base):
    __tablename__ = 'zhan_bu'
    id = Column(Integer, primary_key=True)
    number = Column(String(255))
    fortune = Column(String(255))
    text_1 = Column(String(255))
    text_2 = Column(String(255))
    text_3 = Column(String(255))
    text_4 = Column(String(255))
    explain_1 = Column(String(255))
    explain_2 = Column(String(255))
    explain_3 = Column(String(255))
    explain_4 = Column(String(255))
    saying = Column(String(255))


class TableZhanBuRecord(Base):
    __tablename__ = 'zhan_bu_record'
    id = Column(Integer)
    user_id = Column(String(15), primary_key=True)
    last_time = Column(DateTime)


def init():
    global logger, db_engine, db_session
    logger = get_global('logger')
    db_engine = get_global('db_engine')
    db_session = get_global('db_session')
    Base.metadata.create_all(db_engine)

    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


def get_new_omikuji(user_id: str) -> int:
    result_id = random.randint(1, 100)
    session = db_session()
    found = session.query(TableZhanBuRecord).filter(TableZhanBuRecord.user_id == user_id).first()
    if found:
        found.last_time = datetime.now()
        found.id = result_id
    else:
        found = TableZhanBuRecord(user_id=user_id, last_time=datetime.now(), id=result_id)
    session.add(found)
    session.commit()
    session.close()
    return result_id


def get_today_omikuji(user_id: str):
    session = db_session()
    found: TableZhanBuRecord = session.query(TableZhanBuRecord).filter(TableZhanBuRecord.user_id == user_id).first()
    session.close()
    if found:
        diff = (datetime.now().date() - found.last_time.date()).days
        if diff != 0:
            return None
        else:
            return found.id
    return None


def get_omikuji(user_id: str) -> int:
    session = db_session()
    found: TableZhanBuRecord = session.query(TableZhanBuRecord).filter(TableZhanBuRecord.user_id == user_id).first()
    session.close()
    if found:
        diff = (datetime.now().date() - found.last_time.date()).days
        if diff != 0:
            result_id = get_new_omikuji(user_id)
        else:
            result_id = found.id
    else:
        result_id = get_new_omikuji(user_id)
    return result_id


def get_explain(omikuji_id, only_number: bool = False):
    session = db_session()
    found: TableZhanBu = session.query(TableZhanBu)\
        .filter(or_(TableZhanBu.id == omikuji_id,
                    TableZhanBu.number == omikuji_id,))\
        .first()
    if not found:
        found: TableZhanBu = session.query(TableZhanBu) \
            .filter(TableZhanBu.id == chinese_to_int(omikuji_id)).first()
    session.close()
    if not found:
        return None
    if only_number:
        return found.number
    result = f'【第{found.number}签{found.fortune}】\n\n'
    result += f'{found.text_1}\n{found.explain_1}\n\n'
    result += f'{found.text_2}\n{found.explain_2}\n\n'
    result += f'{found.text_3}\n{found.explain_3}\n\n'
    result += f'{found.text_4}\n{found.explain_4}\n\n'
    saying = found.saying.replace('。', '。\n')
    saying = saying[:-1]
    result += f'{saying}'
    if '凶' in found.fortune:
        result += f'\n\n{notice_1}'
    return result


word_for = '求签'
word_explain = '解签'
word_hand = '挂签'
notice_1 = '注：你抽中了凶签。\n相传抽中凶签后，将签就近挂在神社内的树枝上，便可以破除厄运、逢凶化吉。\n回复「挂签」将签挂起。'


# 返回 0继续处理 1终止处理
def main(conn: GocqConnection, msg):
    message: str = msg['message']
    sender = msg['sender']['user_id']
    if message.strip() == word_for:
        omikuji_id = get_omikuji(sender)
        send_msg = CqCode.image_local(f'./functions/zhan_bu/{omikuji_id}.jpg')
        msg['message'] = f'你抽到了第{get_explain(omikuji_id, True)}签。' + send_msg
        conn.Api.send_message(msg)
        return 1
    elif message.strip() == word_hand:
        today = get_today_omikuji(sender)
        if not today:
            send_msg = '你今天还没有求签。'
        else:
            send_msg = '你已将签挂起。'
        msg['message'] = send_msg
        conn.Api.send_message(msg)
        return 1
    elif message.strip() == word_explain:
        today = get_today_omikuji(sender)
        if not today:
            send_msg = '你今天还没有求签。'
        else:
            send_msg = get_explain(today)
            if not send_msg:
                return 0
        msg['message'] = send_msg
        conn.Api.send_message(msg)
        return 1
    elif message.find(word_explain) != -1:
        # omikuji_id = message.split(' ')[1]
        omikuji_id = message[2:]
        send_msg = get_explain(omikuji_id)
        if not send_msg:
            return 0
        msg['message'] = send_msg
        conn.Api.send_message(msg)
        return 1
    return 0
