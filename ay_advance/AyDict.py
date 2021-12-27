class AyDict:
    __dict = {}

    def __init__(self, ori_dict):
        self.__dict = ori_dict

    def __call__(self):
        return self.__dict

    def __eq__(self, other):
        return self.__dict == other.__dict

    def __contains__(self, ori_key: str):
        ori_key = ori_key.split('.')
        now_dict = self.__dict
        for key in ori_key:
            if key in now_dict:
                now_dict = now_dict[key]
            else:
                return False
        return True

    def __getitem__(self, ori_key: str):
        ori_key = ori_key.split('.')
        now_dict = self.__dict
        for key in ori_key:
            if key in now_dict:
                now_dict = now_dict[key]
            else:
                return None
        return now_dict

    def __setitem__(self, ori_key: str, ori_value):
        ori_key = ori_key.split('.')
        now_dict = self.__dict
        for key in ori_key[:-1]:
            if key not in now_dict:
                now_dict[key] = {}
            now_dict = now_dict[key]
        now_dict[ori_key[-1]] = ori_value
        return ori_value

