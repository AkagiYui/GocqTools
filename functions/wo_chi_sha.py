"""
    ①私聊 吃啥|我吃啥 → 该QQ私聊新增的食物
    ②私聊 新增 → 新增自己的食物
    ③群聊 吃啥 → 该群拥有的食物
    ④群聊 我吃啥 → 自己拥有的食物
    ⑤群聊 我吃啥新增 → 增加自己的食物
    ⑥群聊 吃啥删除 → 管理员可删除群内食物
"""
import random
from sqlalchemy import Column, String, distinct
from sqlalchemy.ext.declarative import declarative_base
from ay_advance import GocqConnection, AyStr
from global_variables import get_global

logger = get_global('logger')
db_engine = get_global('db_engine')
db_session = get_global('db_session')
Base = declarative_base()

module_name = '我吃啥'
module_version = '0.0.9'


class WoChiSha(Base):
    __tablename__ = 'wo_chi_sha'
    user_id = Column(String(15), primary_key=True)
    group_id = Column(String(15), primary_key=True)
    food = Column(String(255), primary_key=True)


def init():
    global logger, db_engine, db_session
    logger = get_global('logger')
    db_engine = get_global('db_engine')
    db_session = get_global('db_session')

    Base.metadata.create_all(db_engine)
    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


def food_add(food: str | list[str], user_id: str, group_id: str = ''):
    session = db_session()
    tmp_list = []
    if isinstance(food, str):
        tmp_list.append(food)
    if isinstance(food, list):
        tmp_list = food
    for new_food in tmp_list:
        new_food = WoChiSha(
            user_id=user_id,
            group_id=group_id,
            food=new_food
        )
        session.add(new_food)
    session.commit()
    session.close()


def food_del(food: str | list[str], user_id: str = None, group_id: str = None):
    session = db_session()
    tmp_list = []
    if isinstance(food, str):
        tmp_list.append(food)
    if isinstance(food, list):
        tmp_list = food
    deleted = 0
    for del_food in tmp_list:
        if user_id is None and group_id is None:
            deleted += session.query(WoChiSha).filter(
                WoChiSha.food == del_food
            ).delete()
        elif user_id is None:
            deleted += session.query(WoChiSha).filter(
                WoChiSha.group_id == group_id,
                WoChiSha.food == del_food
            ).delete()
        elif group_id is None:
            deleted += session.query(WoChiSha).filter(
                WoChiSha.user_id == user_id,
                WoChiSha.food == del_food
            ).delete()
        else:
            deleted += session.query(WoChiSha).filter(
                WoChiSha.user_id == user_id,
                WoChiSha.group_id == group_id,
                WoChiSha.food == del_food
            ).delete()
    session.commit()
    session.close()
    return deleted


def food_find(user_id: str = None, group_id: str = None):
    session = db_session()
    if user_id is None and group_id is None:
        foods = session.query(distinct(WoChiSha.food)).all()
    elif user_id is None:
        foods = session.query(WoChiSha.food).filter(
            WoChiSha.group_id == group_id
        ).all()
    elif group_id is None:
        foods = session.query(WoChiSha.food).filter(
            WoChiSha.user_id == user_id
        ).all()
    else:
        foods = session.query(WoChiSha.food).filter(
            WoChiSha.user_id == user_id,
            WoChiSha.group_id == group_id
        ).all()
    session.close()
    return [x[0] for x in foods]


word_self = ['我', '俺', '咱']  # 标记是自己
word_op = ['吃啥', '吃什么', '吃啥好', '吃什么好']  # 找吃的 增加 删除
word_all = ['有啥吃', '都有啥吃', '有什么吃', '都有什么吃', '有啥吃的']  # 所有食物
word_add = ['新增', '增加', '增添', '添加', '来点']  # 增加关键词
word_del = ['删除', '去除', '去掉', '不要']  # 删除关键词

re_no_food_all = '没吃的...'  # 有啥吃 → 没东西吃的答复

re_no_food_one_pre = '...'
re_no_food_one = '都没东西吃'  # 我吃啥 → 没东西吃的答复
re_no_food_one_end = ''

re_not_permit = '！你不能删除食物'

OP_NULL = -1
OP_SEARCH = 0
OP_ADD = 1
OP_DEL = 2
OP_ALL = 3


# 返回 0继续处理 1终止处理
def main(gocq: GocqConnection, msg):
    message: AyStr = AyStr(msg['message'].strip()).replace_all('  ', ' ')  # 消息
    user_id = msg['sender']['user_id']  # 发送者QQ
    group_id = ''  # 发送者群号

    # print(0, group_id, message, user_id)

    # 判断是否是对自己的行为
    op_self = False
    tmp_list: list = message.find(word_self)
    try:
        tmp_index = tmp_list.index(0)
        message = message.removeprefix(word_self[tmp_index]).lstrip()
        op_self = True
    except ValueError:
        pass
    # 私聊则全部行为映射给自己
    if msg['message_type'] == 'private':
        op_self = True
    elif msg['message_type'] == 'group':
        ...
    else:
        return 0

    if not op_self:
        group_id = msg['group_id']  # 发送者群号

    # print(1, group_id, message, user_id, op_self)

    # 是否继续处理
    # tmp_list: list = message.find(word_all)
    # try:
    #     tmp_index = tmp_list.index(0)
    #     message = message.removeprefix(word_all[tmp_index]).lstrip()
    #     op_which = OP_ALL
    # except ValueError:
    #     tmp_list: list = message.find(word_op)
    #     try:
    #         tmp_index = tmp_list.index(0)
    #         message = message.removeprefix(word_self[tmp_index]).lstrip()
    #     except ValueError:
    #         return 0
    if message in word_all:
        op_which = OP_ALL
    else:
        tmp_list: list = AyStr(message).find(word_op)
        try:
            tmp_index = tmp_list.index(0)
            message = message.removeprefix(word_op[tmp_index]).lstrip()
            op_which = OP_SEARCH
        except ValueError:
            # print(11, 'exit')
            return 0

    # print(2, group_id, message, user_id, op_self, op_which)

    # 判断行为
    if op_which != OP_ALL:
        tmp_list: list = AyStr(message).find(word_add)
        try:
            tmp_index = tmp_list.index(0)
            message = message.removeprefix(word_add[tmp_index]).lstrip()
            op_which = OP_ADD
        except ValueError:
            tmp_list: list = AyStr(message).find(word_del)
            try:
                tmp_index = tmp_list.index(0)
                message = message.removeprefix(word_del[tmp_index]).lstrip()
                op_which = OP_DEL
            except ValueError:
                pass

    if op_self:
        foods = food_find(user_id, '')
    else:
        foods = food_find(group_id=group_id)
    # print(3, group_id, message, user_id, op_self, op_which, foods)

    op_need_send = False
    send_msg = ''

    # 有啥吃
    if op_which == OP_ALL:
        if foods:
            send_msg = ''
            for food in foods:
                send_msg += f'{food} '
            send_msg = send_msg[:-1]
        else:
            if op_self:
                send_msg = '你'
            send_msg += re_no_food_all
        op_need_send = True

    # (我)吃啥
    if op_which == OP_SEARCH:
        if foods:
            send_msg = random.choice(foods)
        else:
            send_msg = re_no_food_one_pre
            if op_self:
                send_msg += '你'
            send_msg += re_no_food_one + re_no_food_one_end
        op_need_send = True

    # 新增
    if op_which == OP_ADD:
        new_foods = message.split()
        deleted = False
        for food in new_foods[::-1]:
            if food in foods:
                deleted = True
                if send_msg == '':
                    if op_self:
                        send_msg += '你'
                    send_msg += '已经有 '
                send_msg += f'{food} '
                new_foods.remove(food)
        if deleted:
            send_msg += '了.'
        food_add(new_foods, user_id, group_id)

        send_msg_2 = ''
        for food in new_foods:
            send_msg_2 += f'{food} '
        send_msg_2 = send_msg_2[:-1]

        if send_msg_2:
            if send_msg != '':
                send_msg += '\n'
            send_msg += '新增了 '
            send_msg += send_msg_2
        op_need_send = True

    # 删除
    if op_which == OP_DEL:

        del_food = message.split()

        foods_in_group = food_find(group_id=group_id)
        foods_for_mine = food_find(user_id, group_id)

        if op_self:
            is_admin = True
        else:
            is_admin = msg['sender']['role'] in ['owner', 'admin']

        str_no_permit = ''
        str_dont_have = ''
        str_del_foods = ''

        for food in del_food:
            if food in foods_for_mine:
                str_del_foods += f'{food} '
                food_del(food, user_id, group_id)
            elif not op_self:
                if food in foods_in_group:
                    if is_admin:
                        str_del_foods += f'{food} '
                        food_del(food, group_id)
                    else:
                        str_no_permit += f'{food} '
                else:
                    str_dont_have += f'{food} '
            else:  # if op_self and not in foods_for_mine
                str_dont_have += f'{food} '

        if str_del_foods:
            str_del_foods = str_del_foods[:-1]
            str_del_foods = '删除了 ' + str_del_foods
        if str_dont_have:
            str_dont_have = str_dont_have[:-1]
            str_dont_have = '没有 ' + str_dont_have
        if str_no_permit:
            str_no_permit = str_no_permit[:-1]
            str_no_permit = '没有权限删除 ' + str_no_permit

        if str_del_foods:
            send_msg += str_del_foods + '\n'
        if str_dont_have:
            send_msg += str_dont_have + '\n'
        if str_no_permit:
            send_msg += str_no_permit + '\n'
        if send_msg.endswith('\n'):
            send_msg = send_msg[:-1]

        op_need_send = True

    if op_need_send:
        msg['message'] = send_msg
        gocq.Api.send_message(msg)
        return 1
    return 0
