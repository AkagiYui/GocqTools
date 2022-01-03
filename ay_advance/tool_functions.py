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
