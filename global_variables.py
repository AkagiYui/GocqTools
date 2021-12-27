_global_dict = {}


def set_global(name, value):
    global _global_dict
    _global_dict[name] = value


def get_global(name, def_value=None):
    global _global_dict
    try:
        return _global_dict[name]
    except KeyError:
        return def_value
