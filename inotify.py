#!/usr/bin/env python3

# Linux的tail/tailf命令使用了内核提供的inotify功能，Python也能使用inotify实现比tail/tailf更强的监控文件功能。

"""
事件标志	                事件含义
IN_ACCESS	            被监控项目或者被监控目录中的文件被访问，比如一个文件被读取
IN_MODIFY	            被监控项目或者被监控目录中的文件被修改
IN_ATTRIB	            被监控项目或者被监控目录中的文件的元数据被修改
IN_CLOSE_WRITE	        一个打开切等待写入的文件或者目录被关闭
IN_CLOSE_NOWRITE	    一个以只读方式打开的文件或者目录被关闭
IN_OPEN	                文件或者目录被打开
IN_MOVED_FROM	        被监控项目或者目录中的文件被移除监控区域
IN_MOVED_TO	            文件或目录被移入监控区域
IN_CREATE	            在所监控的目录中创建子目录或文件
IN_DELETE	            在所监控的目录中删除目录或文件
IN_CLOSE*	            文件被关闭,等同于IN_CLOSE_WRITE*
IN_MOVE	                文件被移动,等同于IN_CLOSE_NOWRITE
"""

__author__ = 'BraveHeart'
__version__ = 0.1

import os, sys
import pyinotify
import logging
import datetime

from digraph import save_obj

logging.basicConfig(level="DEBUG", filename='/home/braveheart/Digraph_demo/log/monitor.log')
logging.info("Starting monitor...")


class MyEventHandler(pyinotify.ProcessEvent):  # 定制化事件处理类，注意继承

    _dg_flag = int(os.path.exists('/home/braveheart/Digraph_demo/model/dg.pkl'))  # type: int

    def __init__(self, path, pickle_name, file_name, dg_obj):
        self._correct_path = path + file_name
        self._digraph_path = path + pickle_name
        self.dg_obj = dg_obj
        super(MyEventHandler, self).__init__()

    def process_IN_OPEN(self, event):  # 必须为process_事件名称，event表示事件对象
        print('OPEN',event.pathname)  # event.pathname 表示触发事件的文件路径
        logging.info("IN_OPEN event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_CLOSE_NOWRITE(self, event):
        print('CLOSE_NOWRITE',event.pathname)
        logging.info("IN_CLOSE_NOWRITE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_MODIFY(self, event):
        print('modify', event.pathname)
        logging.info("IN_MODIFY event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))
        if event.pathname == self._correct_path and os.path.isfile(self._correct_path):
            print(self._dg_flag)
            if self._digraph_path.endswith('pkl') and self._dg_flag == 1:
                if not os.path.exists(self._digraph_path + '.bak'): return self.process_IN_DELETE(event)
                try: os.remove(self._digraph_path + '.bak')
                except OSError as err: logging.info(f"IN_MODIFY event : 删除文件失败: {err}"); self.process_IN_DELETE(event)
            else: self.dg_obj(self._digraph_path)  # dg_run
        else: ...

    def process_IN_ACCESS(self, event):
        print('access', event.pathname)
        logging.info("IN_ACCESS event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_ATTRIB(self, event):
        print('ATTRIB', event.pathname)
        logging.info("IN_ATTRIB event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_DELETE(self, event):
        print('DELETE', event.pathname)
        logging.info("IN_DELETE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))
        if event.pathname == self._digraph_path + '.bak' or \
                all([os.path.exists(self._digraph_path), not os.path.exists(self._digraph_path + '.bak')]):
            try: os.renames(self._digraph_path, self._digraph_path + '.bak'); self._dg_flag = 0
            except OSError as err: logging.info(f"IN_DELETE event : 文件重命名失败: {err}")
            finally: self.dg_obj(self._digraph_path); self._dg_flag = 1
        else: logging.info(f"IN_DELETE event : pkl模型文件不存在&bak备份文件")

    def process_IN_CREATE(self, event):
        print('CREATE', event.pathname)
        logging.info("IN_CREATE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))
        if event.pathname == self._digraph_path: self._dg_flag = 1
        else: ...


def main(dg_obj, cfg):
    WATCH_PATH = cfg['inotify']['WATCH_PATH']
    PICKLE_NAME = cfg['inotify']['PICKLE_NAME']
    FILE_NAME = cfg['inotify']['FILE_NAME']
    if not WATCH_PATH:
        print("The WATCH_PATH setting MUST be set.")
        sys.exit()
    else:
        if os.path.exists(WATCH_PATH):
            print('Found watch path: path=%s.' % (WATCH_PATH))
        else:
            print('The watch path NOT exists, watching stop now: path=%s.' % (WATCH_PATH))
            sys.exit()

    multi_event = pyinotify.IN_OPEN | pyinotify.IN_CLOSE_NOWRITE | pyinotify.IN_MODIFY | pyinotify.IN_ATTRIB  # 监控多个事件
    dg_multi_event = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_ACCESS
    wm = pyinotify.WatchManager()  # 创建WatchManager对象

    handler = MyEventHandler(WATCH_PATH, PICKLE_NAME, FILE_NAME, dg_obj)  # 实例化我们定制化后的事件处理类
    notifier = pyinotify.Notifier(wm, handler)  # 在notifier实例化时传入,notifier会自动执行

    wm.add_watch(WATCH_PATH + '/correct', multi_event, rec=True)  # 添加监控的目录，及事件
    wm.add_watch(WATCH_PATH + '/model', dg_multi_event, rec=True)  # 添加监控的目录，及事件
    notifier.loop()


if __name__ == '__main__':
    # main()
    pass