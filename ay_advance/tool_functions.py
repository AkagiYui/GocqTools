import os
from datetime import datetime
import psutil


def self_uptime():
    start_time = psutil.Process(os.getpid()).create_time()
    curr_time = datetime.now()
    return curr_time - start_time


def self_cpu_percent():
    pass


def machine_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    curr_time = datetime.now()
    return curr_time - boot_time


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
