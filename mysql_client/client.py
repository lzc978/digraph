import contextlib
from time import sleep

from utils import wrapper_exception

_instances = {}


def _get_conn_pool(*args, **kwargs):
    """Connection pool factory function, singleton instance factory.
    If you want a single connection pool, call this factory function.

    :param args: positional arguments passed to `MySQLConnectionPool`
    :param kwargs: dict arguments passed to `MySQLConnectionPool`
    :return: instance of class`MySQLConnectionPool`
    """
    from .connection import MySQLConnectionPool
    pool_name = kwargs.setdefault("pool_name", "mysql_pool")

    if pool_name not in _instances:
        _instances[pool_name] = MySQLConnectionPool(*args, **kwargs)
    pool = _instances[pool_name]
    assert isinstance(pool, MySQLConnectionPool)
    return pool


class MysqlClient:
    """
    example1:
        client = MysqlClient(**config)
        sql = "select * from a_table"
        ret = client.fetchone(sql, params=None)
        if ret[0] == 0:
            query_result = ret[2]
        else:
            print("mysql fetchone failed:{}".format(ret[1]))

    example2:
        config["auto_close"] = False
        client = MysqlClient(**config)
        sql = "select * from a_table"
        ret1 = client.fetchone(sql, params=None)
        ret2 = client.fetchall(sql, params=None)
        client.close()
    """
    pools = {}

    def __init__(self,
                 host="localhost",
                 port=3306,
                 user="root",
                 password="",
                 database="way_robot",
                 autocommit=True,
                 pool_name="mysql_pool"):
        self.kwargs = {"host": host,
                       "port": port,
                       "user": user,
                       "password": password,
                       "database": database,
                       "autocommit": autocommit,
                       "pool_name": pool_name}
        self.auto_close = True
        if pool_name not in MysqlClient.pools:
            MysqlClient.pools[pool_name] = _get_conn_pool(**self.kwargs)
        self.pool = MysqlClient.pools[pool_name]

    @contextlib.contextmanager
    def _connect(self):
        """
        :return: result:cursor对象
        """
        conn = self.pool.borrow_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            self.pool.return_connection(conn)

    @wrapper_exception()
    def execute(self, sql, params=None):
        """
        :param sql:str 执行sql语句
        :param params:list sql内参数
        :return: result:int sql语句影响数目，装饰后返回 (error_no:int,error_msg:str,result:int)
        """
        with self._connect() as cursor:
            ret = cursor.execute(sql, params)
        return ret

    @wrapper_exception()
    def fetchone(self, sql, params=None):
        """
        :param sql:str 执行sql语句
        :param params:list sql内参数
        :return: result:dict sql语句返回结果，装饰后返回 (error_no:int,error_msg:str,result:dict)
        """
        with self._connect() as cursor:
            cursor.execute(sql, params)
            ret = cursor.fetchone()
        return ret

    @wrapper_exception()
    def fetchall(self, sql, params=None):
        """
        :param sql:str 执行sql语句
        :param params:list sql内参数
        :return: result:tuple sql语句返回结果,结构：({},{},...)，装饰后返回 (error_no:int,error_msg:str,result:tuple)
        """
        with self._connect() as cursor:
            cursor.execute(sql, params)
            ret = cursor.fetchall()
        return ret

    @property
    def size(self):
        """
        :return: num:int 连接池规模，即池内创建的连接数量
        """
        return self.pool.size
