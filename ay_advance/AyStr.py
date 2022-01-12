"""
    自定义字符串类
    重写in支持判断列表或元组成员是否出现在字符串里
    重写find()支持查找子串列表或元组
"""


class AyStr(str):
    def __contains__(self, item) -> bool:
        if isinstance(item, list):
            return len([member for member in item if member in self]) > 0
        if isinstance(item, tuple):
            return len([member for member in item if member in self]) > 0
        return super().__contains__(item)

    def find(self, __sub: list | tuple | str, __start=None, __end=None) -> list | tuple | int:
        if isinstance(__sub, list):
            result = []
            for i in __sub:
                result.append(super().find(i, __start, __end))
            return result
        if isinstance(__sub, tuple):
            result = ()
            for i in __sub:
                result += (super().find(i, __start, __end),)
            return result
        return super().find(__sub, __start, __end)

    def startswith(self, __prefix: list | tuple | str, __start=None, __end=None) -> bool:
        if isinstance(__prefix, list or tuple):
            for i in __prefix:
                if super().startswith(i, __start, __end):
                    return True
            return False
        return super().startswith(__prefix, __start, __end)

    def replace_all(self, __old: str, __new: str):
        tmp_str = str(self)
        while tmp_str.find(__old) != -1:
            tmp_str = tmp_str.replace(__old, __new)
        return AyStr(tmp_str)


if __name__ == '__main__':
    pass
    aa = AyStr('咱吃什么')
    word_what_self = ['我', '俺', '咱']
    print(aa.find(word_what_self))
