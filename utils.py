"""
ChatterBot utility functions
"""
import sys
import traceback
import functools
from threading import Lock as ThreadLock
from os.path import dirname, abspath, join

root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from threading import local
import logging.config
from contant import *
from logger_manage import _get_logger

# logging.config.fileConfig(join(root_dir, "config/logger.ini"))
logger = _get_logger(log_name_main)
timer_log = _get_logger(log_name_timer)
keep_alive_log = _get_logger(log_name_keep_alive)
socketio_log = _get_logger(log_name_socketio)
LOCAL = local()  # 线程变量, 必须在线程里设置变量，并在线程中取出 LOCAL.abc = "abc";print(LOCAL.abc)


def get_logger():
    """该函数只能在局部作用域调用!
    优先使用线程设置的日志器"""
    return LOCAL.logger if hasattr(LOCAL, 'logger') else logger


def flatten(nested_list):
    """嵌套list 摊平: [1, [2, 3]] -> [1, 2, 3]"""
    queue = [nested_list]
    ret = []
    while queue:
        for item in queue.pop():
            if isinstance(item, list):
                queue.append(item)
            else:
                ret.append(item)
    return ret

def wrapper_exception(exception=Exception):
    """ 装饰器，给被装饰函数提供异常捕捉行为
    :param exception: obj or tuple 定义异常类型，默认Exception
    :return: (int:错误码, str：异常信息, val:操作结果)
    """

    def utils_exception(func):
        def work(*args, **kwargs):
            err_code = 0
            err_msg = '操作已执行'
            val = None
            try:
                val = func(*args, **kwargs)
            except exception as e:
                logger.error(traceback.format_exc())
                err_code = 1
                err_msg = e
                val = None
            finally:
                return err_code, err_msg, val

        return work

    return utils_exception


def single_instance(cls):
    """
    通过装饰器的实现任何类的单例模式，并且通过线程锁，实现了单例模式的线程安全
    """
    __instance = dict()
    __instance_lock = ThreadLock()

    @functools.wraps(cls)
    def _single_instance(*args, **kwargs):
        if cls not in __instance:
            with __instance_lock:
                if cls not in __instance:
                    __instance[cls] = cls(*args, **kwargs)
        return __instance[cls]

    return _single_instance
