#! /usr/bin/python
# -*- coding: UTF-8 -*-
from timeit import default_timer

import pymysql
import qqbot
from dbutils.pooled_db import PooledDB
from constant import config


class DBConfig:
    def __init__(self, host, db, user, password, port=3306):
        """
        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param passwd:密码
        :param charset:字符编码
        """
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.charset = "utf8"
        self.minCached = 10
        self.maxCached = 20
        self.maxShared = 10
        self.maxConnection = 100

        self.blocking = True
        self.maxUsage = 100
        self.setSession = None
        self.reset = True


# ---- 用连接池来返回数据库连接
class DBPoolConn:
    __pool = None

    def __init__(self, config):
        if not self.__pool:
            self.__class__.__pool = PooledDB(
                creator=pymysql,
                maxconnections=config.maxConnection,
                mincached=config.minCached,
                maxcached=config.maxCached,
                maxshared=config.maxShared,
                blocking=config.blocking,
                maxusage=config.maxUsage,
                setsession=config.setSession,
                charset=config.charset,
                host=config.host,
                port=config.port,
                database=config.db,
                user=config.user,
                password=config.password,
            )

    def get_conn(self):
        return self.__pool.connection()


# 初始化DB配置和链接池
db_config = DBConfig(
    config["database"]["host"],
    config["database"]["db"],
    config["database"]["user"],
    config["database"]["password"],
    config["database"]["port"],
)
g_pool_connection = DBPoolConn(db_config)


# ---- 使用 with 的方式来优化代码, 利用 __enter__ 和 __exit__ 控制with的进入和退出处理
class DBConn(object):
    def __init__(self, commit=True, log_time=True, log_label="总用时"):
        """
        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        # 从连接池获取数据库连接
        conn = g_pool_connection.get_conn()
        conn.ping(reconnect=True)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            qqbot.logger.debug("-- %s: %.6f 秒" % (self._log_label, diff))

    # ========= 一系列封装的方法
    def insert(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.lastrowid

    # 返回 count
    def get_count(self, sql, params=None, count_key="count(id)"):
        self.cursor.execute(sql, params)
        data = self.cursor.fetchone()
        if not data:
            return 0
        return data[count_key]

    def fetch_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_by_pk(self, sql, pk):
        self.cursor.execute(sql, (pk,))
        return self.cursor.fetchall()

    def update_by_pk(self, sql, params=None):
        self.cursor.execute(sql, params)

    def delete(self, sql, params=None):
        self.cursor.execute(sql, params)

    @property
    def cursor(self):
        return self._cursor


if __name__ == "__main__":
    with DBConn(log_time=True) as c:
        print("-- 返回数据量: %d " % c.get_count(sql="select count(id) from t_feedback"))
