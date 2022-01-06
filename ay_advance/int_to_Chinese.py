"""
    数字转汉字
    https://blog.csdn.net/PlusChang/article/details/72991191
"""

num = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
kin = ['十', '百', '千', '万', '零']


def del_surplus_0(x):
    if '零' in x:
        a = x.index('零')
        if a == 0:
            x.pop(0)
            del_surplus_0(x)
        else:
            if x[a + 2] in ['十', '百', '千', '万', '零']:
                if x[a + 1] != '万':
                    x.pop(a + 1)
                    del_surplus_0(x)
    return x


def del_surplus_unit(x):
    try:
        a = x.index('零')
        if x[a - 1] in ['十', '百', '千', '零']:
            x.pop(a - 1)
            del_surplus_unit(x[a + 1])
    except Exception:
        pass
    return x


def int_to_Chinese(integer: int) -> str:
    # 数字转汉字列表
    integer = list(str(integer))
    for i in integer:
        integer[(integer.index(i))] = num[int(i)]
    # print(0, integer)

    integer.reverse()
    if len(integer) >= 2:
        integer.insert(1, kin[0])
        if len(integer) >= 4:
            integer.insert(3, kin[1])
            if len(integer) >= 6:
                integer.insert(5, kin[2])
                if len(integer) >= 8:
                    integer.insert(7, kin[3])
                    if len(integer) >= 10:
                        integer.insert(9, kin[0])
                        if len(integer) >= 12:
                            integer.insert(11, kin[1])
    # print(1, integer)

    if len(integer) >= 9:
        if integer[8] == '零':
            integer.pop(8)
    # print(2, integer)

    # 删除多余的0和单位
    integer = del_surplus_0(integer)
    # print(3, integer)

    # 删除多余的单位
    integer = del_surplus_unit(integer)
    # print(4, integer)

    # 删除末尾的零
    while len(integer) > 0 and integer[0] == '零':
        integer.pop(0)

    # 列表转字符串
    # print(50, integer)
    integer.reverse()
    integer = ''.join(integer)
    # print(51, integer)
    if integer == '':
        integer = '零'

    return integer

