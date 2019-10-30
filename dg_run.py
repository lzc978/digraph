import logging
import os
import time

from digraph import Digraph, get_obj, save_obj, get_participle
from inotify import main
from utils import logger, single_instance
from mysql_client import MysqlClient
from word_method import Words
# import utils.logger as logger


mysql = MysqlClient(host='192.168.20.29',
                    port=3306,
                    user='way_gkb',
                    password='work@GKB372!',
                    database='way_robot_kb')
w = Words(mysql)


@single_instance
class DGModel(object):

    def __init__(self, sentence_path):
        self.sentence_path = sentence_path
        # self.dg = self._get_obj(file_name) if os.path.isfile(file_name) else self._save_obj(file_name)

    def __get__(self, instance, owner):
        logging.info("hello test")

    def __call__(self, data_path):
        self.dg = self.__get_obj(data_path) if os.path.isfile(data_path) else self.__save_obj(data_path, self.sentence_path)
        self.dg.print(); return self.dg

    @staticmethod
    def __get_obj(data_path):
        begin1 = time.time()
        dg = get_obj(file_name=data_path)
        logger.debug("读取耗时:{}秒".format(time.time() - begin1))
        return dg

    @staticmethod
    def __save_obj(data_path, sentence_path):
        sentences = ["""我 想 去 北京""",
                     """我 想 吃饭 了""",
                     """北京 在 哪里""",
                     """我 想要 办理 汉口 银行 的 信用卡""",
                     """怎么 办理 信用卡""",
                     """信用卡 怎么 办理""",
                     """我 要 取号""",
                     """我 想去 天安门""",]
        # for i in [['我', '要', '取号'], ['我', '要', '吃饭']]:
        with open(sentence_path, 'r', encoding='utf-8') as f:
            for content in f.readlines():
                sentences_list = get_participle(content)
                sentences.extend(w.gen_sentences(sentences_list, subsystem_id='hm256f8c953411e8aea35254004210bf'))
        # sentences = [w.gen_sentences(i, subsystem_id='hm256f8c953411e8aea35254004210bf') for i in [['我', '要', '取号'], ['我', '要', '吃饭']]]
        # sentences.extend(sentences)

        word_list = [item.split() for item in sentences]
        # temp = [set(item) for item in word_list]
        # word_set = reduce(lambda a, b: a | b, temp)  # 保证词语不重复
        # logger.debug(word_set)
        begin1 = time.time()
        # dg = Digraph(word_set)
        # # 构建词序
        # for words in word_list:
        #     l = len(words)
        #     for i in range(l):
        #         if i < l - 1:
        #             dg.addEdge(words[i], words[i + 1])
        dg = Digraph()
        for w_l in word_list:
            dg.build(w_l)
        logger.debug("构建耗时:{}秒".format(time.time() - begin1))
        save_obj(dg, file_name=data_path)
        return dg


if __name__ == '__main__':
    _data_path = "./model/dg.pkl"
    _sentence_path = "./correct/correct.txt"
    logging.basicConfig(level="DEBUG")

    dgl = DGModel(_sentence_path)
    dg = dgl(_data_path) if callable(dgl) else object
    import time
    time.sleep(5)

    from threading import Thread
    Thread(target=main, args=(dgl, )).start()

    # file_name = "./model/dg.pkl"
    # print(os.path.isfile(file_name))
    # if os.path.isfile(file_name):
    #     begin1 = time.time()
    #     dg = get_obj(file_name=file_name)
    #     logger.debug("读取耗时:{}秒".format(time.time() - begin1))
    # else:
    #     sentences = ["""我 想 去 北京""",
    #                  """我 想 吃饭 了""",
    #                  """北京 在 哪里""",
    #                  """我 想要 办理 汉口 银行 的 信用卡""",
    #                  """怎么 办理 信用卡""",
    #                  """信用卡 怎么 办理""",
    #                  """我 要 取号""",
    #                  """我 想去 天安门""",]
    #     # for i in [['我', '要', '取号'], ['我', '要', '吃饭']]:
    #     with open('correct.txt', 'r', encoding='utf-8') as f:
    #         for content in f.readlines():
    #             sentences_list = get_participle(content)
    #             sentences.extend(w.gen_sentences(sentences_list, subsystem_id='hm256f8c953411e8aea35254004210bf'))
    #     # sentences = [w.gen_sentences(i, subsystem_id='hm256f8c953411e8aea35254004210bf') for i in [['我', '要', '取号'], ['我', '要', '吃饭']]]
    #     # sentences.extend(sentences)
    #
    #     word_list = [item.split() for item in sentences]
    #     # temp = [set(item) for item in word_list]
    #     # word_set = reduce(lambda a, b: a | b, temp)  # 保证词语不重复
    #     # logger.debug(word_set)
    #     begin1 = time.time()
    #     # dg = Digraph(word_set)
    #     # # 构建词序
    #     # for words in word_list:
    #     #     l = len(words)
    #     #     for i in range(l):
    #     #         if i < l - 1:
    #     #             dg.addEdge(words[i], words[i + 1])
    #     dg = Digraph()
    #     for w_l in word_list:
    #         dg.build(w_l)
    #     logger.debug("构建耗时:{}秒".format(time.time() - begin1))
    #     save_obj(dg, file_name=file_name)
    # dg.print()

    logger.debug("*" * 10 + "测试" + "*" * 10)

    begin3 = time.time()
    # 我 要 取号
    logger.debug(dg.search("我 线 池法".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    sw = w.get_synonym_words()
    print(sw)

    res = w.gen_sentences(['我', '能', '取号', '吗'], subsystem_id='hm256f8c953411e8aea35254004210bf')

    print(res)
