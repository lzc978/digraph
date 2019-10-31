#!/usr/bin/env python
# async socket 编解码读取写入并传输

__author__ = 'BraveHeart'
__version__ = 0.1

import pickle

from digraph import printf
from utils import logger


class Handler(object):

    def __init__(self, request):
        self.requests = request

    def _send(self, data):
        self.requests.sendall(pickle.dumps(data))

    def _receive(self):
        try: data = self.requests.recv(1024); return pickle.loads(data)
        except EOFError as err: logger.error(f"客户端断开链接：{err}"); return False

    def __call__(self, dg):
        content = \
            """{}请输入选项{}\n0. exit | 1. print | 2. input\n{}""".format('*' * 10, '*' * 10, '*' * 29)
        self._send(content)
        _flag = 1
        while _flag:
            data = self._receive()
            if not data:
                break
            logger.info(f"接收到需要纠错的句子：{data}\n\t有向图类型{type(dg)}")
            if all(map(lambda c: '\u4e00' <= c <= '\u9fa5', data)):
                corr_res = printf(dg, data)
            else: logger.error(f"请输入中文：{data}"); corr_res = f"请输入中文：{data}"
            self._send(corr_res)

    def connect(self):
        pass

    def send_message(self):
        pass


if __name__ == '__main__':
    # Handler()
    ...