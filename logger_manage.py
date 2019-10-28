import logging

loggers = []


class LogProxy:
    """日志代理类, 方便更换工具库中使用的日志器"""
    def __init__(self, logger):
        _, __ = self, logger
        _.logger, _.info, _.debug, _.warning, _.error = __, __.info, __.debug, __.warning, __.error


def _get_logger(logger_name):
    """根据名称获取日志器"""
    __ = logging.getLogger(logger_name)
    _ = LogProxy(__)
    loggers.append(_)
    return _


def logger_unify(logger_proxy):
    """将所有的日志器设置为同一个日志器"""
    __ = logger_proxy.logger
    for _ in loggers:
        _.logger, _.info, _.debug, _.warning, _.error = __, __.info, __.debug, __.warning, __.error
