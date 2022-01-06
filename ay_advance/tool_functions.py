# 获取自身运行时长
def self_uptime():
    import os
    from datetime import datetime
    import psutil
    start_time = psutil.Process(os.getpid()).create_time()
    curr_time = datetime.now()
    return curr_time - start_time


# 获取开机时长
def machine_uptime():
    from datetime import datetime
    import psutil
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    curr_time = datetime.now()
    return curr_time - boot_time


# 获取自身ip
# https://www.zhihu.com/question/49036683/answer/1243217025
def get_self_ip():
    s = None
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        if s:
            s.close()
