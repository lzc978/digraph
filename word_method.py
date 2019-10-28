"""
获取敏感词       get_sensitive_words
获取重要词       get_important_words
获取近义词       get_synonym_words
获取停用词
获取随机回复      get_random_resp
检测敏感词       sensitive_words_find
检测重要词       important_words_find
同义词替换       synonym_replace
停用词去除
dfa查找          dfa
"""
from snownlp import SnowNLP
from utils import logger, flatten
from contant import comm

trantab = str.maketrans('', '', '?!.？！。')


class Words:
    """
    获取各种词库
    """
    _instance = None
    _first_init = True

    @classmethod
    def __new__(cls, *args, **kwargs):
        """todo 单例模式"""
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, mysql):
        """初始化mysql_client """
        self.mysql = mysql
        self.comm = comm
        if self._first_init: # 默认True 第一次初始化置为False
            self._first_init = False
            self.sensitive_words = None  # 敏感词
            self.important_words = None  # 重要词
            self.synonym_words = None  # 同义词
            self.stop_words = None  # 停用词
            self.random_resp = None  # 随机词
            self.init()

    def init(self):
        """相当于run() 同义词先跑"""
        self.get_synonym_words()  # get_synonym_words 必须在 get_stop_words 之前, 对停用词采用同义词替换
        self.get_stop_words()
        self.get_important_words()
        self.get_sensitive_words()
        self.get_random_resp()
        return True

    def reload(self):
        return self.init()

    def get_sensitive_words(self):
        """从mysql中获取敏感词表
        :param mysql: obj
        :return: dict {subsystem1:[word1,word2,..], subsystem2:[word11,word12...],...}
        """
        self.sensitive_words = {}
        sql = "select sensitivity_word, subsystem_id from way_sensitivity_word where is_deleted = 0 "
        result = self.mysql.fetchall(sql)
        if result[0] == 0:
            for record in result[2]:
                subsystem_id = record["subsystem_id"].lower()  # 防止mysql配置导致大小写问题
                if subsystem_id not in self.sensitive_words:
                    self.sensitive_words[subsystem_id] = []
                self.sensitive_words[subsystem_id].append(record["sensitivity_word"])
            logger.debug("敏感词:{}".format(self.sensitive_words))
        else:
            logger.error("mysql敏感词获取失败：{}".format(result[1]))

    def get_synonym_words(self):
        """从mysql中获取近义词表
        :param mysql: obj
        :return: dict {subsystem1:[([w1,w2,w3],w4), ([w1,w2,w3],w4)...], subsystem2:[...],...}
        词根编辑的时候选择最合适的那个,栗子: [('办理'),'办']　　　我要办理信用卡　-> 我要办信用卡
                            　[('办'),'办理']　　　我要办理信用卡　-> 我要办理理信用卡
        """
        self.synonym_words = {}
        sql = "select synonym_value, synonym_desp, subsystem_id from way_synonym_word where is_deleted = 0 "
        # synonym_value = "中国人民建设银行" synonym_desp = "建设银行|建行|我行"
        result = self.mysql.fetchall(sql)  # 查询集 (error_no:int,error_msg:str,result:tuple)
        if result[0] == 0:  # todo 状态码0
            for record in result[2]:
                subsystem_id = record["subsystem_id"].lower()  # 防止mysql配置导致大小写问题
                if subsystem_id not in self.synonym_words:
                    self.synonym_words[subsystem_id] = []
                # root_word = record["synonym_value"]
                # temp = [x for x in record["synonym_desp"].split("|") if x != root_word]
                # self.synonym_words[subsystem_id].append((temp, root_word))
                # root:词根   t: 排好顺序的同义词列表
                root = record["synonym_value"]  # "中国人民建设银行"
                t = sorted(list(set(_ for _ in record["synonym_desp"].split("|") + [root] if _)), key=len)  # 取最长的词，按字符长短排序
                t2 = [root, t]  # ['中国人民建设银行', ['建行', '我行', '建设银行', '中国人民建设银行']]
                if len(t) < 2:  # 只有一个同义词，重新在来一遍
                    continue
                # self.synonym_words[subsystem_id].append((t[:-1], t[-1]))
                # todo 将包好的同义词数据添加到同义词字典中 key: subsystem_id(子系统id) | value: t2 (t2[0]为词根，t2[1]同义词数据)
                self.synonym_words[subsystem_id].append(t2)

            # for k, v in self.synonym_words.items():
            #     self.synonym_words[k] = sorted(v, key=lambda x: -len(x[1]))  # [(['储蓄卡', '银行卡'], '储蓄卡'),...]
            # logger.debug("同义词:{}".format(self.synonym_words))
            logger.debug("同义词成功载入")
        else:
            logger.error("mysql同义词获取失败：{}".format(result[1]))
        return self.synonym_words

    def get_stop_words(self):
        """获取停用词"""
        self.stop_words = {}
        sql = "select stop_word, subsystem_id from way_stop_word where is_deleted = 0 "
        result = self.mysql.fetchall(sql)
        if result[0] == 0:
            for record in result[2]:
                stop_word = record["stop_word"]
                subsystem_id = record["subsystem_id"].lower()  # 防止mysql配置导致大小写问题
                # 同义词替换
                if self.comm == subsystem_id:
                    tables2 = [self.synonym_words.get(self.comm)]
                else:
                    tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
                # tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
                stop_word = self.synonym_replace(stop_word, tables2)

                if subsystem_id not in self.stop_words:
                    self.stop_words[subsystem_id] = [stop_word]
                else:
                    self.stop_words[subsystem_id].append(stop_word)

            for k, v in self.stop_words.items():
                self.stop_words[k] = sorted(v, key=lambda x: -len(x))
            logger.debug("停用词:{}".format(self.stop_words))
        else:
            logger.error("mysql停用词获取失败：{}".format(result[1]))

    def get_important_words(self):
        """从mysql获取重要词表
        :param mysql: obj
        :return: dict {subsystem1:[word1,word2,..], subsystem2:[word11,word12...],...}
        """
        self.important_words = {}
        sql = "select big_word, subsystem_id from way_big_word where is_deleted = 0 "
        result = self.mysql.fetchall(sql)
        if result[0] == 0:
            for record in result[2]:
                subsystem_id = record["subsystem_id"].lower()  # 防止mysql配置导致大小写问题
                if subsystem_id not in self.important_words:
                    self.important_words[subsystem_id] = []
                # 同义词替换
                big_word = record["big_word"]
                if self.comm == subsystem_id:
                    tables2 = [self.synonym_words.get(self.comm)]
                else:
                    tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
                # tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
                big_word = self.synonym_replace(big_word, tables2)

                self.important_words[subsystem_id].append(big_word)

            for k, v in self.important_words.items():
                self.important_words[k] = sorted(v, key=lambda x: -len(x))
            logger.debug("重要词:{}".format(self.important_words))
        else:
            logger.error("mysql重要词获取失败：{}".format(result[1]))

    def get_random_resp(self):
        """
        :param mysql:
        :return: list [word1,word2,word3...]
        随机词
        """
        self.random_resp = []
        self.random_resp.extend(["呵呵", "然后呢?", "嗯嗯"])  # 枚举

    def words_reload(self):
        """ 通过信号控制 sensitive_words important_words synonym_words random_resp 的更新删除
        :param mysql:
        :return: boolean
        """
        return True

    def synonym_replace(self, question, tables):
        """《同义词》替换
        :param question:
        :param tables: list 同义词列表
        :return: msg
        """
        raw = question
        # 方法1
        # pass_words = []
        # for table in tables:
        #     if not table:
        #         continue
        #     for replace_list, root_word in table:  # ([a, b, c], d)  d类似词根, a, b, c 为别名
        #         for w in replace_list:
        #             if w in question and w != root_word and w not in pass_words:
        #                 question = question.replace(w, root_word)
        #                 pass_words.append(root_word)
        # return question
        # 方法2
        for table in tables:
            if not table:
                continue
            for word_list in table:  # (a,b,c,d) 同义词列表, d最长
                holder = "!"
                root, t = word_list  # root:词根   t: 排好顺序的同义词列表
                for word in sorted(t,reverse=False):  # 优先替换长度长的
                    if root not in question:  # add by ian，12-13
                        question = question.replace(word, holder)
                question = question.replace(holder, root)

        if raw != question:
            logger.debug("同义词　{} -> {}".format(raw, question))
        return question

    def sensitive_words_find(self, question, tables):
        """ 《敏感词》检测 找到一个就返回
        :param question: str
        :param tables: dict
        :return: str
        """
        for table in tables:
            if not table:
                continue
            for word in table:
                if word in question:
                    # 防止曹操被过滤
                    if len(word) == 1:
                        if word == question:
                            return word
                    else:
                        return word

    def important_words_find(self, question, tables):
        """ 检查通用性《重要词》, 子系统自己的通用词 ,返回尽可能多的重要词
        :param question:
        :param tables:
        :return: []
        """
        ret = []
        for table in tables:
            if not table:
                continue
            for word in table:
                if word in question:
                    ret.append(word)
        return ret

    def stop_words_delete(self, question, tables):
        """
        :param question:
        :param tables:
        :return:
        """
        # if len(question) <= 3:  # 太短的语句不做停用词删除处理
        #     return question
        if not question:
            return ''
        question = question.translate(trantab)
        raw = question
        for table in tables:
            if not table:
                continue
            for word in table:
                if word in question:
                    # logger.debug("question={} 去除停用词:{}".format(question, word))
                    question = question.replace(word, "")
        if question != raw:
            logger.debug("去除停用词 {} --> {}".format(raw, question))
        return question or raw

    def rebuild(self, question, subsystem_id, comm=comm):
        if self.comm == subsystem_id:
            tables2 = [self.synonym_words.get(self.comm)]
            tables3 = [self.stop_words.get(comm)]
        else:
            tables3 = [self.stop_words.get(comm), self.stop_words.get(subsystem_id)]
            tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
        # tables3 = [self.stop_words.get(comm), self.stop_words.get(subsystem_id)]
        # 同义词替换
        temp = self.synonym_replace(question, tables2)

        # 去除停用词
        temp = self.stop_words_delete(temp, tables3)

        # 同义词替换
        # tables2 = [self.synonym_words.get(comm), self.synonym_words.get(subsystem_id)]
        temp = self.synonym_replace(temp, tables2)
        # logger.debug("rebuild 结果: {} --> {}".format(question, temp))
        # 英文字符转小写
        temp = temp.lower()
        return temp

    def stop_words_delete2(self, fenci_list, tables):
        """
        :param fenci_list:
        :param tables:
        :return:
        """
        for table in tables:
            if not table:
                continue
            for word in table:
                fenci_list = [_ for _ in fenci_list if _ != word]
        return fenci_list

    def gen_sentences(self, fenci_list, subsystem_id, comm=comm):
        """根据停用词和同义词尽可能多地生成同义句
        :param fenci_list: 句子分词后的 词语列表   ['我', '要', '取钱']
        :param subsystem_id: 子系统
        :param comm: 公共子系统
        :return: 句子列表 [['要 取钱'], ['我 要 取钱'], ['我 想要 取钱']]
        """
        if self.comm == subsystem_id:
            tables2 = [self.synonym_words.get(self.comm)]
            tables3 = [self.stop_words.get(comm)]
        else:
            tables2 = [self.synonym_words.get(self.comm), self.synonym_words.get(subsystem_id)]
            tables3 = [self.stop_words.get(comm), self.stop_words.get(subsystem_id)]
        new_fenci_list = []
        for i, w in enumerate(fenci_list):  # fenci_list -> new_fenci_list 保证顺序同时去重
            if w not in fenci_list[:i]:
                new_fenci_list.append(w)
        qs = set()
        # 导航类提取关键词语作为同义句 -- 适当扩展容易混淆的地点
        sentence = ''.join(new_fenci_list)
        for place in ('迎宾点', '贵宾区', '贵宾点', '理财区'):
            if place in sentence:
                qs.add(place)

        # 导航类提取关键词语 end
        def _gen(ss):
            # ss: list  ['我', '要', '取钱']
            qs.add(' '.join(ss))
            for table in tables2:
                if not table:
                    continue
                for word_list in table:  # (a,b,c,d) 同义词列表, d最长
                    holder = "!"
                    word_list = flatten(word_list)
                    word_list.sort(key=len, reverse=True)
                    s = ss
                    for word in word_list:
                        s = [_ if _ != word else holder for _ in s]
                    for word in word_list[::-1]:
                        qs.add(' '.join([_ if _ != holder else word for _ in s]))

        _gen(new_fenci_list)
        _gen(self.stop_words_delete2(new_fenci_list, tables3))
        return list(qs)


def snow_get_important_words(text):
    if text.isdecimal():
        return []
    s = SnowNLP(text)
    ret = [x[0] for x in s.tags if any([y in x[1] for y in "n"])]
    # n:名词 v:动词 r:代词(你我他啥) p:介词 e:叹词
    logger.debug([x for x in s.tags])
    logger.debug("分词分析重要词:{}".format(ret))
    return ret


try:
    from xpinyin import Pinyin

    _pinyin = Pinyin()


    def get_pinyin_list(text):
        """todo 中文名字转拼音"""
        py = _pinyin.get_pinyin(text)
        return list(_.strip() for _ in py.split("-"))  # todo 分割字符串 格式为 ["zhang", "san"]
except Exception as e:
    logger.warning("请尽量安装xpinyin模块获取更好的拼音转换效果")


    def get_pinyin_list(text):
        """使用SnowNLP分词，情感分词"""
        return SnowNLP(text).pinyin


class Node:
    __slots__ = ["children", "word", "pinyin", "isEnd"]  # todo 使用__slots__，它仅允许动态绑定()里面有的属性,该方法能节约内存消耗

    def __init__(self):
        """
        children：Node-obj, 子节点
        word: list, 子节点上的词列表
        pinyin: list, 子节点上的词拼音,索引和word同步
        isEnd: True 表示 word和pinyin不为空
        """
        self.children = None
        self.word = None
        self.pinyin = None
        self.isEnd = None


class dfa:
    roots = None

    @classmethod
    def init(cls, mysql=None):
        sql = "select proper_noun_word, subsystem_id from way_proper_noun_word where is_deleted = 0 "
        error_code, error_msg, records = mysql.fetchall(sql)  # todo pymysql中返回查询集 (error_no:int,error_msg:str,result:tuple)
        if error_code != 0:  # 0 是请求成功状态码
            logger.error("mysql错误:{}".format(error_msg))
            return
        cls.roots = {}
        for record in records:  # 子系统id元组类型
            subsystem_id = record["subsystem_id"].lower()  # 子系统id
            if subsystem_id not in cls.roots:
                cls.roots[subsystem_id] = Node()  # todo 将实例对象构建构建成一个字典 key: subsystem_id | value: Node()
            cls.add_word(cls.roots[subsystem_id], record["proper_noun_word"])  # proper_noun_word中文字符

    @staticmethod
    def add_word(root, word):
        """添加word和pinyin"""
        node = root  # node就是一个Node()实例对象
        if len(word) < 2:
            return
        # flag = len(word) >= 3  # 大于3个字的词用声母来表示,比如 惠享存 --> h x c
        # flag = True
        pinyin_of_word = ""
        pinyin_list = dfa.get_pinyin_list(word)  # 处理后的拼音列表
        if len(pinyin_list) != len(word):  # 若处理后的拼音列表长度不等于传入的中文字符长度，则抛异常
            logger.warning("该方法不适用中英夹杂的词汇: {}".format(word))
            return

        for i in range(len(word)):
            # temp = dfa.get_pinyin(word[i])[0] if flag else dfa.get_pinyin(word[i])
            temp = pinyin_list[i]
            pinyin_of_word += temp
            temp = temp[0]
            if node.children is None:  # 子节点为空
                node.children = {temp: Node()}  # 则key：z  value: Node()实例对象
            elif temp not in node.children:  # 若 z 不在
                node.children[temp] = Node()
            node = node.children[temp]  # Node()
        if node.word:
            node.word.append(word)  # list, 子节点上的词列表
            node.pinyin.append(pinyin_of_word)  # list, 子节点上的词拼音,索引和word同步
        else:
            node.word = [word]  # node.word为none时，自己构建一个列表
            node.pinyin = [pinyin_of_word]
        node.isEnd = True  # True 表示 word和pinyin不为空

    @classmethod
    def replace(cls, msg, subsystem_id=None, flag=False):
        """ 拼音方式识别msg中的热词并返回替换后的msg, 拼音纠错
        :param flag: =True 需要拼音完全相同才匹配  =False 只要求长度<= 2 的句子进行拼音完全匹配，其余只做声母匹配
        :param subsystem_id: str
        :param msg:
        :return: msg, [hot_words]
        """
        temps = list(cls.find(msg, subsystem_id=subsystem_id, flag=flag))

        if len(temps) == 1:
            word, begin, end = temps[0]
            if word:
                msg = msg[:begin - 1] + word + msg[end:]
            return msg, [word]
        if len(temps) >= 2:
            (word1, b1, e1), (word2, b2, e2) = temps[:2]
            msg = msg[:b1 - 1] + word1 + msg[e1:b2 - 1] + word2 + msg[e2:]
            return msg, [word1, word2]
        return msg, []

    @classmethod
    def find(cls, msg, subsystem_id=None, flag=False):
        """ 从message(句子)中查找热词 优先查找长度较长的词语
        :param flag:
        :param subsystem_id: str
        :param msg: str 完整的句子
        :return: tuple (热词, 热词起始位置, 热词结束位置)
        """
        root = cls.roots.get(subsystem_id.lower())  # 获取Node() 那四个参数
        if not root:
            return
        msg_pinyin_list = dfa.get_pinyin_list(msg)  # 鼻音替换
        logger.info(f"pinyin匹配: { msg } -> { msg_pinyin_list }")
        num = len(msg_pinyin_list)  # 替换后pinyin list的长度
        if len(msg) != num:  # 不是纯中文的句子可能不是一个字符对应一个拼音  3+3 这类计算公式
            return
        i = 0
        while i < num:  # 遍历 解析对象msg
            p = root  # 获取Node() 那四个参数
            j = i
            i = i + 1
            raw_word_pinyin = ""
            raw_word = ""
            while j < num and p.children:  # index在num list中 | 存在子节点
                one_of_msg = msg[j]  # 句子中的一个字
                temp = msg_pinyin_list[j]  # 获取index下鼻音替换后的一个字
                # temp = dfa.get_pinyin(one_of_msg)
                # if temp in p.children or temp[0] in p.children[0]:
                if temp[0] in p.children:  # temp[0] 一般为声母   p.children 为字典，其键值为词声母
                    p = p.children[temp[0]]
                    j = j + 1
                else:
                    break
                raw_word_pinyin += temp
                raw_word += one_of_msg
            # i==j 表示只有一个字, i < j 表示两个字以上
            if i < j and p.word:
                # 上一部 --> 上一步
                if len(raw_word_pinyin) < 3 or flag:  # 对于词长小于3的词语需要拼音完全相等才算满足
                    temp_word = None
                    for index in range(len(p.word)):
                        print(raw_word_pinyin, "   ", p.pinyin[index])
                        if raw_word_pinyin == p.pinyin[index]:
                            temp_word = p.word[index]
                            if temp_word == raw_word:  # 拼音全等且文字全等, 表示完全命中,立即返回
                                temp_word = p.word[index]
                                break
                            else:  # 拼音全等但文字不等 只返回其中（最后）一个(每个满足该条件都返回的话不好处理)
                                temp_word = p.word[index]
                    if temp_word:
                        yield temp_word, i, j
                else:  # 对于词长 >=3 的词语只进行声母比较
                    temp_index = 0
                    distance = 200  # 表示距离无穷大
                    lraw = len(raw_word_pinyin)
                    for index in range(len(p.word)):
                        distance2 = abs(len(p.pinyin[index]) - lraw)
                        # print(distance2, p.word[index], p.pinyin[index])
                        if distance >= distance2:  # 找出拼音字符串长度距离最近的那项并最后返回
                            distance = distance2
                            temp_index = index
                            if p.pinyin[index] == raw_word_pinyin:
                                break
                    if distance != 200:
                        yield p.word[temp_index], i, j

    @classmethod
    def print(cls):
        """用于检测是否成功载入"""
        for k, root in cls.roots.items():
            logger.debug("------------子系统:{}--------------".format(k))
            cls._print(root)

    @staticmethod
    def _print(node, w=""):
        if node.isEnd:
            logger.debug("{:<10} {}  {}".format(w, node.pinyin, node.word))
        if node.children:
            for k, v in node.children.items():
                node = v
                dfa._print(node, w + k)

    # @staticmethod
    # def get_pinyin(text, delimiter=""):
    #     # 鼻音替换，翘舌音替换
    #     return pinyin.get(text, delimiter=delimiter, format="strip").replace("ng", "n"). \
    #         replace("zh", "z").replace("sh", "s").replace("ch", "c")

    @staticmethod
    def get_pinyin_list(text):
        """"""
        s = []
        for x in get_pinyin_list(text):
            # 字符串替换 翘舌音替换等...
            x = x.replace("ng", "n").replace("zh", "z").replace("sh", "s").replace("ch", "c")
            s.append(x)
        return s


if __name__ == "__main__":
    # 汉字 多音字的拼音识别可能失败 比如：单：单（shàn，姓）老师说，单（chán匈奴首领）于只会骑马，不会骑单（dān）车
    # print(dfa.get_pinyin_list("你们还好吧"))
    # print(dfa.get_pinyin_list("上一步"))
    # print(dfa.get_pinyin_list("有什么步骤"))
    # clients = Client()
    # clients.init_all()
    # w = Words(clients.mysql)
    # w2 = Words(clients.mysql)
    # print(id(w))
    # print(id(w2))
    # print(w.reload())
    sub_id = 'a'
    dfa.roots = {}
    root = dfa.roots[sub_id] = Node()
    dfa.add_word(root, '低柜')
    dfa.print()

    msg = '带我去递归区'
    msg_pinyin = get_pinyin_list(msg)

    print(dfa.replace(msg, subsystem_id=sub_id))
    print(list(dfa.find(msg, subsystem_id=sub_id)))
