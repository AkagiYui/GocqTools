import random

from sqlalchemy import Column, Integer, String, distinct
from sqlalchemy.ext.declarative import declarative_base

from ay_advance.GocqConnection import GocqConnection
from global_variables import get_global

logger = get_global('Logger')
db_engine = get_global('db_engine')
db_session = get_global('db_session')
Base = declarative_base()

module_name = '我吃啥'
module_version = '0.0.1'


class WoChiSha(Base):
    __tablename__ = 'wo_chi_sha'
    user_id = Column(String(15), primary_key=True)
    food = Column(String(255), primary_key=True)


def init():
    global logger, db_engine, db_session
    logger = get_global('Logger')
    db_engine = get_global('db_engine')
    db_session = get_global('db_session')

    Base.metadata.create_all(db_engine)
    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


word_prefix = '我吃啥'
word_add = ['新增']
word_del = ['删除']
word_what = '有啥吃'
word_what_all = '都有啥吃'


def food_add(user_id: int, food: str):
    new_food = WoChiSha(
        user_id=user_id,
        food=food
    )
    session = db_session()
    session.add(new_food)
    session.commit()
    session.close()


def food_del(user_id: int, food: str):
    session = db_session()
    session.query(WoChiSha).filter(WoChiSha.user_id == user_id, WoChiSha.food == food).delete()
    session.commit()
    session.close()


def food_find(user_id: int = None):
    session = db_session()
    if user_id is None:
        foods = session.query(distinct(WoChiSha.food)).all()
    else:
        foods = session.query(WoChiSha.food).filter(WoChiSha.user_id == user_id).all()
    session.close()

    food_list = []
    for food in foods:
        food_list.append(food[0])
    foods = food_list
    return foods


# 返回 0继续处理 1终止处理
def main(gocq: GocqConnection, msg):
    message = msg['message']
    sender = msg['sender']['user_id']

    if message == word_what:
        send_msg = ''
        foods = food_find(sender)
        if len(foods) != 0:
            for food in foods:
                send_msg += f'{food} '
            send_msg = send_msg[:-1]
        else:
            send_msg = '你没吃的...'
        msg['message'] = send_msg
        gocq.Api.send_message(msg)
        return 0

    if message == word_what_all:
        send_msg = ''
        foods = food_find()
        for food in foods:
            send_msg += f'{food} '
        msg['message'] = send_msg
        gocq.Api.send_message(msg)
        return 0

    if message.find(word_prefix) != 0:
        return 0

    message = message[3:]
    foods = food_find(sender)

    send_msg = ''
    # 查询
    if message == '':
        logger.debug(f'求食者：{sender}')

        if len(foods) == 0:
            send_msg = '...你都没东西吃'
        else:
            send_msg = random.choice(foods)
    else:
        if message[0] == ' ':
            message = message[1:]
        else:
            return 0
        # 新增
        for word in word_add:
            if message.find(f'{word} ') == 0:
                food = message[len(word) + 1:].strip()
                if food in foods:
                    send_msg = f'...你已经有{food}了'
                    break
                else:
                    food_add(sender, food)
                    send_msg = f'已{word} {food}'
                    break
        # 删除
        for word in word_del:
            if message.find(f'{word} ') == 0:
                food = message[len(word) + 1:].strip()
                if food not in foods:
                    send_msg = f'...你本来就没有{food}'
                    break
                else:
                    food_del(sender, food)
                    send_msg = f'已{word} {food}'
                    break
    msg['message'] = send_msg
    gocq.Api.send_message(msg)
    return 0
