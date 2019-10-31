import configparser

from utils import logger


class ReadConfigFile(object):

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.cfg_parser = None
        self.cfg = {}

    def read_ini(self):
        self.cfg_parser = configparser.ConfigParser()
        try:
            self.cfg_parser.read(self.ini_path, encoding="utf8")
            self._digraph()
            self._inotify()
            self._tcpsocket()
            self._mysql()
        except configparser.Error as e:
            self.cfg_parser = None
            logger.error('errcode:10004, 读取配置文件失败，error:{err}'.format(err=e))
            return False

    def _digraph(self):
        cfg_digraph = {}
        section_name = 'Digraph'
        cfg_digraph['_data_path'] = self.cfg_parser.get(section_name, '_data_path')
        cfg_digraph['_sentence_path'] = self.cfg_parser.get(section_name, '_sentence_path')

        self.cfg['digraph'] = cfg_digraph

    def _inotify(self):
        cfg_inotify = {}
        section_name = 'Inotify'
        cfg_inotify['WATCH_PATH'] = self.cfg_parser.get(section_name, 'WATCH_PATH')
        cfg_inotify['PICKLE_NAME'] = self.cfg_parser.get(section_name, 'PICKLE_NAME')
        cfg_inotify['FILE_NAME'] = self.cfg_parser.get(section_name, 'FILE_NAME')

        self.cfg['inotify'] = cfg_inotify

    def _tcpsocket(self):
        cfg_tcpsocket = {}
        section_name = 'TCPSocket'
        cfg_tcpsocket['host'] = self.cfg_parser.get(section_name, 'host')
        cfg_tcpsocket['port'] = self.cfg_parser.get(section_name, 'port')

        self.cfg['tcpsocket'] = cfg_tcpsocket

    def _mysql(self):
        cfg_mysql = {}
        section_name = 'Mysql'
        cfg_mysql['host'] = self.cfg_parser.get(section_name, 'host')
        cfg_mysql['port'] = self.cfg_parser.get(section_name, 'port')
        cfg_mysql['user'] = self.cfg_parser.get(section_name, 'user')
        cfg_mysql['password'] = self.cfg_parser.get(section_name, 'password')
        cfg_mysql['database'] = self.cfg_parser.get(section_name, 'database')

        self.cfg['mysql'] = cfg_mysql
