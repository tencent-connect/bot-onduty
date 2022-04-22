import datetime
from typing import List

from dao.db import DBConn


class Owner:
    def __init__(self, name: str, id: str, owner_type: str):
        self.name = name
        self.id = id
        self.owner_type = owner_type


def add_owner(owners: List[Owner]):
    """
    :param owners: 值班人员id列表
    """
    with DBConn(log_time=True) as c:
        for owner in owners:
            # 去重插入
            run_sql = "select count(id) from t_owner where owner_id=%s"
            run_params = owner.id
            count = c.get_count(run_sql, run_params)
            if count > 0:
                continue
            run_sql = "insert into t_owner (owner_id,owner_name,owner_type) values (%s,%s,%s)"
            run_params = (owner.id, owner.name, owner.owner_type)
            c.insert(run_sql, params=run_params)
        return True


def remove_owner(owners: List[str]):
    """
    移除值班人员
    :param owners: 值班人员id列表
    """
    with DBConn(log_time=True) as c:
        for owner in owners:
            run_sql = "delete from t_owner where owner_id=%s"
            run_params = owner
            c.delete(run_sql, run_params)
        return True


def change_owner(user_1, user_2):
    """
    交换值班人员
    :param user_1: 值班人员1
    :param user_2: 值班人员2
    """
    with DBConn(log_time=True) as c:
        run_sql = (
            "update t_owner as t1 join t_owner as t2 on "
            "(t1.owner_id = %s and t2.owner_id = %s) "
            "set \
                      t1.owner_name = t2.owner_name, \
                      t2.owner_name = t1.owner_name,\
                      t1.owner_id = t2.owner_id,\
                      t2.owner_id = t1.owner_id,\
                      t1.owner_type = t2.owner_type,\
                      t2.owner_type = t1.owner_type;"
        )
        run_params = (user_1, user_2)
        c.update_by_pk(run_sql, run_params)
        return True


def reset_owner(user, date, type):
    """
    重新排班
    :param date: 从哪天开始排期
    :param user: 值班的人员id
    :param type: 重新设置的类型，有产品和技术两种
    :return:执行是否成功
    """
    with DBConn(log_time=True) as c:
        # 从值班顺序中取出列表按指定人员开始进行重新排序
        owner_list = c.fetch_all("select * from t_owner where owner_type=%s", type)
        owner_result = []
        owner_left = []
        index = 0
        for owner in owner_list:
            if owner["owner_id"] == user:
                owner_left = owner_list[:index]
                owner_result = owner_list[index:]
                break
            index += 1
        owner_result.extend(owner_left)
        if len(owner_result) == 0:
            return False
        # 对重排后的列表更新值班日期
        d = date
        delta = datetime.timedelta(days=1)
        for owner in owner_result:
            run_sql = "update t_owner set on_duty_time=%s where owner_id=%s"
            run_params = (d.strftime("%Y-%m-%d"), owner["owner_id"])
            c.update_by_pk(run_sql, run_params)
            d += delta
        return True


def get_owner(date):
    """
    查看值班表
    :return:值班表列表
    """
    with DBConn(log_time=True) as c:
        run_sql = "select * from t_owner where on_duty_time>=%s order by on_duty_time"
        run_params = date
        return c.fetch_all(run_sql, run_params)


def get_owner_by(owner_id):
    """
    获取指定值班人员
    :param owner_id:值班人员id
    :return:值班人员信息
    """
    with DBConn(log_time=True) as c:
        run_sql = "select * from t_owner where owner_id=%s"
        run_params = owner_id
        return c.fetch_one(run_sql, run_params)


def get_duty_owner(date, type):
    """
    获取某一天的值班人员
    :param date:日期 格式为 2022-04-06
    :param type 值班人员类型
    """
    with DBConn(log_time=True) as c:
        run_sql = "select * from t_owner where on_duty_time=%s and owner_type=%s"
        run_params = (date, type)
        return c.fetch_one(run_sql, run_params)


def get_duty_owners(date):
    """
    获取某一天的值班人员
    :param date:日期 格式为 2022-04-06
    """
    with DBConn(log_time=True) as c:
        run_sql = "select * from t_owner where on_duty_time=%s"
        run_params = date
        return c.fetch_all(run_sql, run_params)
