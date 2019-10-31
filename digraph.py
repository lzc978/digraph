"""
声母：b p m f d t n l g k h j q x zh ch sh r z c s y w
单韵母:a o e i u ü
复韵母：ai ei ui ao ou iu ie ue er
特殊韵母:(er)
前鼻韵母：an en in un ün
后鼻韵母：ang eng ing ong
整体认读音节：zhi chi shi ri zi ci si yi wu yu yu yue yin yun yuan
"""
import os
import time
from snownlp import SnowNLP

from word_method import dfa
from utils import logger

holder = "_"


class Digraph:
    def __init__(self, word_list=None, pinyins=None, pys=None, freqs=None):
        """每个词通过数组索引标识
        :param word_list:
        :param pinyins:
        :param pys:
        :param freqs:

        self.E int: 边的数目
        self.V int: 顶点的数目
        self.adj list: [[1,2],[4,5],[7,8]...] 储存顶点的邻近点的索引
        self.words list: 词语/顶点列表
        self.pinyins list: 词语的完全拼音列表，有做翘舌音，鼻音处理
        self.pys     list: 词语的拼音的声母列表
        self.freqs   list: 储存词语词频的列表
        self._rg    obj: Digraph 反向图对象
        """
        self.E = 0  # 边的数目
        if word_list:
            """初始化反向图"""
            self.words = word_list  # 分词后的词语/顶点列表
            self.V = len(self.words)  # 词数/顶点的数目
            self.adj = [[] for _ in range(self.V)] # 存储顶点的临近点的索引 todo 可以是多个临近点
            self.pinyins = pinyins
            self.pys = pys
            self.freqs = freqs
            self._rg = None  # 反向图对象
        else:
            """初始化一个空的有向图"""
            self.words = []
            self.V = 0
            self.adj = []
            self.pys = []
            self.pinyins = []
            self.freqs = []
            self._rg = None

    def build(self, word_list):
        """
        :param word_list: 句子分词后得到的列表 eg: ["今天", "天气", "真好"]
        :return:
        """
        pre = None
        for index, word in enumerate(word_list):  # 索引和值 (0，"今天")
            logger.debug(word)
            self.addVetex(word)  # 当一个词不存在时, 将该词作为顶点并添加到顶点列表, pinyins, pys, freqs, V顶点计数加一  |  若存在就词频加一
            if index > 0:
                self.addEdge(pre, word)  # 添加一条边
            pre = word  # 则pre变成了前一个值, word是下一个值 eg: 0: "今天" , 1: "天气"
        logger.debug("+" * 100)

    def addEdge(self, first_word, second_word):
        """添加一条边：first_word to second_word"""
        v, w = self.vetex_exist(first_word), self.vetex_exist(second_word)  # 分别返回索引 or -1
        if v == -1 or w == -1:  # 有一个顶点不存在
            return False
        if w in self.adj[v]:  # 已建立连接  todo 若second_word的索引 在 v索引下对应的邻近点索引列表中, 则返回False
            return False
        self.adj[v].append(w)  # TODO 若不存在, 则添加到v索引下对应的邻近点索引列表中
        self.E += 1  # 添加后, 边的数目也自增一
        return True

    def addVetex(self, word):
        """将一个词作为一个顶点并添加"""
        index = self.vetex_exist(word)  # 分词对应的索引
        if index != -1:  # 查到他的索引了
            # 该顶点已存在，频率加一
            self.freqs[index] += 1  # 该分词词频自增一
            return True
        pinyin_list = dfa.get_pinyin_list(word)  # 处理一下鼻音
        self.adj.append([])  #
        self.words.append(word)
        self.pinyins.append("".join(pinyin_list))
        self.pys.append("".join(x[0] for x in pinyin_list))
        self.freqs.append(1)
        self.V += 1  # 不存在, 则顶点数目自增一
        return True

    def vetex_exist(self, word):
        """
        :param word:
        :return: -1表不存在，>=0 的整数标识该词语已录入并且该数字为其索引
        """
        try:
            return self.words.index(word)  # 分词对应的索引
        except ValueError as e:
            pass
        return -1

    def pingyin_exist(self, word_pinyin):
        """ 传入的词语的完整拼音是否是图中的一个顶点
        :param word_pinyin:
        :return:
        """
        try:
            return self.pinyins.index(word_pinyin)
        except ValueError as e:
            pass
        return -1

    def py_exist(self, word_py):
        """ 传入的词语的声母组合是否是图中的一个顶点
        :param word_py:
        :return:
        """
        try:
            return self.pys.index(word_py)
        except ValueError as e:
            pass
        # logger.error("该图中不存在这个词{},请先调用addVetex将该词语插入：{}".format(word, e))
        return -1

    # def adj_vetex(self, word):
    #     index = self.vetex_exist(word)
    #     if index == -1:
    #         return []
    #     return self.adj[index]

    def reverse(self):
        """获得反向图，更该邻接表即可"""
        R = Digraph(word_list=self.words, pinyins=self.pinyins, pys=self.pys, freqs=self.freqs)
        # R = Digraph(self.words, self.pinyins)
        for v in range(self.V):  # 遍历顶点索引
            for w in self.adj[v]:  # 遍历每个顶点的邻近点的索引
                """
                todo 反过来添加一条边
                即: 用顶点索引去匹配是否存在于该顶点的邻近点索引的 邻近点列表中
                """
                R.addEdge(self.words[w], self.words[v])
        return R

    @property
    def rg(self):
        """反向图 reverse-graph"""
        if not self._rg:
            self._rg = self.reverse()  # 反向图
        return self._rg

    def del_rg(self):
        del self._rg

    def print(self):
        s = "\n"
        for index, w in enumerate(self.adj):
            s += "{:<4}freq={:<4} {:20}".format(index, self.freqs[index], self.words[index] + "({})".format(
                self.pinyins[index])) + \
                 "".join(
                     [str(index) + self.words[index] + "({})".format(self.pinyins[index]) + " " for index in w]) + "\n"
        logger.debug(s)
        return s

    def search(self, word_list):
        """ 参考 word_list 获得有向图中的句子
        :param word_list: 分词后的词列表 ["我", "想", "去", "北京"]
        :return: None or str
        """
        logger.debug(word_list)
        l = len(word_list)  # 4
        answer = [holder] * l  # ['_', '_', '_', '_']  答案
        scores = [0] * l  # [0, 0, 0, 0]  得分
        indice = [None] * l  # [None, None, None, None]
        pys = [None] * l  # [None, None, None, None]  todo 词语的拼音声母列表
        flag = False  # boolean(bool布尔值) 是否需要纠错的标记
        if l <= 3:  # 分词后的列表长度小于等于3
            times = 1
        else:
            times = 2  # 一次查找中允许的纠错次数  词长3--> 1次
        first = None  # int  纠错需要的前位词在 图的列表中的 索引
        middle = None  # int  纠错需要的中位词在 句子中的 索引
        adj_list = None  # list
        for i, w in enumerate(word_list):  # index, 值
            snow_pinyin = SnowNLP(w).pinyin  # 转拼音
            # w_pinyin = dfa.get_pinyin(w, delimiter="|")
            # w_py = "".join(x[0] for x in w_pinyin.split("|"))
            w_pinyin = "".join(snow_pinyin)  # 字符串拼接 ["bei", "jing"]-->"beijing"
            w_py = "".join(x[0] for x in snow_pinyin)  # 字符串拼接 声母拼接 |  "bj"
            pys[i] = w_py  # 声母列表中 修改对应的索引下的声母
            # 1 词查询
            index = self.vetex_exist(w)  # 查询该词的索引
            if index == -1:  # 没找到该词索引, 采用完整拼音查询
                # 2 完整拼音查询
                index = self.pingyin_exist(w_pinyin)  # 完整拼音对应索引
                if index == -1:  # 完整拼音索引没找到, 采用声母查询
                    # 3 声母查询
                    index = self.py_exist(w_py)  # 声母查询对应索引
                    if index == -1:  # 声母查询索引没找到, 得分为0分
                        temp_score = 0
                    else:
                        temp_score = 0.8  # 声母查到了, 给0.8
                else:
                    temp_score = 0.9  # 完整拼音找到了, 给0.9
            else:
                temp_score = 1  # 词/顶点 找到, 给1

            if index != -1:
                # if flag and times > 0 and i > 1:  # 表示需要反向纠错 i>1 表示第三个词开始才能进行纠错
                if i > 1:  # 表示需要反向纠错 i>1 表示第三个词开始才能进行纠错
                    # if answer[i - 2] != holder:
                    if answer[i - 2] != holder:
                        times -= 1  # 纠错次数自减一
                        logger.debug(
                            "first.adj:{}-{}   rg.adj:{}-{}".format(first, self.adj[first], index, self.rg.adj[index]))
                        # 有向图的前一位词索引的邻近点索引集合 和 反向图的当前词索引的邻近点索引集合 取 交集 dict
                        result = set(self.adj[first]) & set(self.rg.adj[index])
                        logger.debug("集合取交集 result:{}".format(result))
                        if not result:  # 若没有交集
                            if times < 1: # 纠错次数小于1
                                pass
                                # return None
                            else:  # 反向纠错失败
                                pass
                        else:
                            # 根据词频来筛选
                            max_freq = 0  # 最大词频
                            temp_i = None
                            for _index in result:  # 遍历dict
                                if max_freq < self.freqs[_index]:  # 若最大词频小于该交集词的词频
                                    max_freq = self.freqs[_index]  # 则更新最大词频
                                    temp_i = _index  # 该词频索引放入答案
                            answer[middle] = self.words[temp_i]  # 将该词放入答案列表中的中位词索引位置
                            indice[middle] = temp_i  # 该词索引 给中位词索引对应的值
                        flag = False  # 纠错完毕一次

                # 不纠错，直接缓存需要的数据再继续
                if adj_list and index not in adj_list:
                    # 找出来的索引不 是 上一个词的 下一位

                    adj_list = None  # 邻近点列表None
                    flag = True  # 标记为需要纠错
                    middle = i  # 将该词索引 作为中位词索引
                else:
                    answer[i] = self.words[index]  # 将该词作为答案, 索引保持一致
                    scores[i] += temp_score  # 对应索引的值 累加 (分值累加)
                    indice[i] = index  # 索引赋值 的值设置
                    first = index  # 该分词索引 赋值给 前位词索引
                    adj_list = self.adj[index]  # 将该索引对应的邻近点 赋值给 邻近点列表
            else:
                """该词语无法找到, 设置需要纠错的词语"""
                flag = True
                middle = i
                adj_list = None

        logger.debug("分词查找结果:{}".format(answer))
        logger.debug("分词打分结果:{}".format(scores))
        modified_words = [0, [], []]  # 修改矫正的词 list
        not_found_words = [0, []]  # 没找到的词 list
        for index, w in enumerate(answer):
            if scores[index] == 0:
                if w == holder:
                    not_found_words[0] += 1
                    not_found_words[1].append(index)
                else:
                    modified_words[0] += 1
                    modified_words[1].append(index)
                    modified_words[2].append(w)
        logger.debug("查询过程矫正词{}, 未找到的词{}".format(modified_words, not_found_words))

        if all(holder == item for item in answer):
            # 失败
            return None
        if l == 1:
            # 补词
            s = answer[0]
            temp_index = indice[0]
            n = 3
            while True:
                n -= 1
                max_freq = 0
                if not self.adj[temp_index]:
                    break
                for _index in self.adj[temp_index]:
                    if max_freq < self.freqs[_index]:
                        max_freq = self.freqs[_index]
                        temp_index = _index
                s += self.words[temp_index]
                if not n:
                    break
            return s
        else:
            # s = None
            if answer[0] == holder:  # 补充第一个词
                max_freq = 0
                temp_index = None
                next_index = indice[1]
                if next_index is not None:
                    for index in self.rg.adj[next_index]:
                        if any(item in self.pys[index] for item in pys[0]):  # 词频不靠谱  声母更相似优先
                            temp_index = index
                            break
                        if self.freqs[index] > max_freq:
                            max_freq = self.freqs[index]
                            temp_index = index

                    if temp_index:
                        # s = self.words[temp_index] + answer[1]
                        answer[0] = self.words[temp_index]
            if answer[-1] == holder:  # 补充最后一个词
                max_freq = 0
                temp_index = None
                pre_index = indice[-2]
                if pre_index is not None:
                    for index in self.adj[pre_index]:
                        if any(item in self.pys[index] for item in pys[0]):
                            temp_index = index
                            break
                        if self.freqs[index] > max_freq:
                            max_freq = self.freqs[index]
                            temp_index = index

                    if temp_index:
                        # s = answer[0] + self.words[temp_index]
                        answer[-1] = self.words[temp_index]

        return "".join([str(x) for x in answer if x != holder])

    def search2(self, word_list):
        begin = time.time()
        logger.debug("查询语句={}".format(word_list))
        l = len(word_list)
        if l < 1:
            return None
        indices = [-1 for _ in range(l)]
        scores = [0 for _ in range(l)]
        for i, w in enumerate(word_list):
            snow_pinyin = dfa.get_pinyin_list(w)
            # w_py = "".join(x[0] for x in w_pinyin.split("|"))
            w_pinyin = "".join(snow_pinyin)
            w_py = "".join(x[0] for x in snow_pinyin)
            # pys[i] = w_py
            # 1 词查询
            index = self.vetex_exist(w)
            if index == -1:
                # 2 完整拼音查询
                index = self.pingyin_exist(w_pinyin)
                if index == -1:
                    # 3 声母查询
                    index = self.py_exist(w_py)
                    if index == -1:
                        temp_score = 0
                    else:
                        temp_score = 0.8
                else:
                    temp_score = 0.9
            else:
                temp_score = 1
            if index != -1:
                indices[i] = index
                scores[i] = temp_score
                if l == 1:
                    return self.words[index]
            else:
                if l == 1:
                    return None
        for i, index in enumerate(indices):
            if i == 0:
                # 第一个词空缺
                behind = indices[i + 1]
                if scores[i + 1] > scores[i] and behind != -1:
                    temp = self.rg.adj[behind]
                    if temp:
                        temp_index = -1
                        temp_freq = 0
                        for x in temp:
                            if self.freqs[x] > temp_freq:
                                temp_freq = self.freqs[x]
                                temp_index = i
                        indices[i] = temp_index
            elif i == l - 1:
                # 最后一个词空缺
                front = indices[i - 1]
                if scores[i - 1] > scores[i] and front != -1:
                    temp = self.adj[front]
                    if temp:
                        temp_index = -1
                        temp_freq = 0
                        for x in temp:
                            if self.freqs[x] > temp_freq:
                                temp_freq = self.freqs[x]
                                temp_index = i
                        indices[i] = temp_index
            else:
                # 中间词语
                front = indices[i - 1]
                behind = indices[i + 1]
                if front != -1 and behind != -1:
                    temp = set(self.adj[front]) & set(self.rg.adj[behind])
                    logger.debug("front={}  behind={} 交集={}".format(front, behind, temp))
                    if temp:
                        temp_index = -1
                        temp_freq = 0
                        for x in temp:
                            if self.freqs[x] > temp_freq:
                                temp_freq = self.freqs[x]
                                temp_index = i
                        indices[i] = temp_index
                        scores[i] = 1
        answer = [self.words[index] if index != -1 else holder for index in indices]
        logger.debug("最终结果={}".format(answer))
        logger.debug("最终得分={}".format(scores))
        s = ""
        for word in answer:
            if word != holder:
                s += word
        logger.debug("纠错耗时:{}".format(time.time() - begin))
        return s or None


def save_obj(obj, file_name="dg.pickle"):
    """ 对象系列化
    :param obj:
    :param file_name:
    :return:
    """
    import pickle
    logger.debug("保存对象")
    with open(file_name, "wb") as f:
        pickle.dump(obj, f)


def get_obj(file_name="dg.pickle"):
    """ 对象反系列化, 并获得对象
    :param file_name:
    :return:
    """
    import pickle
    logger.debug("载入对象")
    with open(file_name, "rb") as f:
        obj = pickle.load(f)
    return obj


def get_participle(word):
    s = SnowNLP(word)
    return s.words


def get_dg(es, sub_system_id=None):
    sub_system_id = "8771a68be48911e792d400505687a0a9"
    index = "chat_" + sub_system_id
    file_name = "{}.from_es.dg.pickle".format(index)
    if not os.path.isfile(file_name):
        dg = Digraph()
        body = {"query": {"match_all": {}}, "size": 10000}
        for item in es.search(index=index, body=body, _source_include=["question"])["hits"]["hits"]:
            q = item["_source"]["question"]
            question = ""
            for x in q:
                if x.isalpha():
                    question += x
            if question:
                word_list = get_participle(question)
                dg.build(word_list)
        save_obj(dg, file_name=file_name)
    else:
        dg = get_obj(file_name=file_name)
    return dg


def get_dg2(mysql, sub_system_id=None):
    sub_system_id = "8771a68be48911e792d400505687a0a9"
    index = "chat_" + sub_system_id
    file_name = "{}.from_mysql.dg.pickle".format(index)
    if not os.path.isfile(file_name):
        dg = Digraph()
        sql = "select question from way_gkb_question_answer where is_deleted=0 and qa_status=1"
        ret = mysql.fetchall(sql)
        if ret[0] != 0 and ret[2]:
            for item in ret[2]:
                for q in item["question"].split("|"):
                    question = ""
                    for x in q:
                        if x.isalpha():
                            question += x
                    if question:
                        word_list = get_participle(question)
                        dg.build(word_list)
        save_obj(dg, file_name=file_name)
    else:
        dg = get_obj(file_name=file_name)
    return dg


def printf(dg, data):
    logger.debug("*" * 10 + "测试" + "*" * 10)
    begin3 = time.time()
    # 我 要 取号
    corr_res = dg.search(get_participle(data))
    logger.debug(corr_res)
    logger.debug("查询耗时{}秒\n".format(time.time() - begin3))
    return corr_res


if __name__ == "__main__":
    """前向查询后向查询"""
    import logging

    logging.basicConfig(level="DEBUG")
    file_name = "dg.pickle"
    if os.path.isfile(file_name):
        dg = get_obj(file_name=file_name)
    else:
        sentences = ["""我 想 去 北京""",
                     """我 想 吃饭 了""",
                     """北京 在 哪里""",
                     """我 想要 办理 汉口 银行 的 信用卡""",
                     """怎么 办理 信用卡""",
                     """信用卡 怎么 办理""",
                     """我 要 取号""",
                     """我 想去 天安门"""]
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
        save_obj(dg, file_name=file_name)
    dg.print()

    logger.debug("*" * 10 + "测试" + "*" * 10)

    begin2 = time.time()
    logger.debug(dg.search("我 想 去 北京".split()))
    logger.debug("查询1 耗时{}秒\n".format(time.time() - begin2))

    begin3 = time.time()
    logger.debug(dg.search("我 要 去 北京".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    logger.debug(dg.search("挖 要 去 深圳".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("我 想要 哈哈 汉口 啦啦 的 信用卡".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("新用卡".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("深圳".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("我 要".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("我".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("信用卡 该 怎么 办理".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 想要 办理 汉口 银行 的 信用卡
    logger.debug(dg.search("北京 银行 的 信用卡 该 怎么 办理".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 要 取号
    logger.debug(dg.search("我 要 取好".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 要 取he
    logger.debug(dg.search("我 要 去号".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

    begin3 = time.time()
    # 我 要 取he
    logger.debug(dg.search("我 想去 田安门".split()))
    logger.debug("查询2耗时{}秒\n".format(time.time() - begin3))

