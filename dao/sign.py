from dao.db import DBConn
from datetime import datetime
import time


def init_sign_record(
    owner_id: str,
    owner_name: str,
):
    """
    初始化当天的值班数据
    :param owner_id: 值班人id
    :param owner_name: 值班人用户昵称
    """
    with DBConn(log_time=True) as c:
        run_sql = "insert into t_sign (owner_id,owner_name) " "values (%s,%s)"
        run_params = (
            owner_id,
            owner_name,
        )
        c.insert(sql=run_sql, params=run_params)


def sign_in(record_id: int):
    """
    值班签到
    :param record_id: 签到记录的id
    """
    with DBConn(log_time=True) as c:
        run_sql = "update t_sign set sign_in_time=%s where id=%s"
        run_params = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id)
        c.update_by_pk(sql=run_sql, params=run_params)


def sign_out(record_id: int):
    """
    值班签出
    :param record_id: 签到记录的id
    """
    with DBConn(log_time=True) as c:
        run_sql = "update t_sign set sign_out_time=%s where id=%s"
        run_params = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id)
        c.update_by_pk(sql=run_sql, params=run_params)


def get_signed_in_record(owner_id: str):
    """
    检查今天是否已经签到了
    :param owner_id: 值班人id
    """
    with DBConn(log_time=True) as c:
        req_sql = "select * from t_sign where date like '%%%s%%'" % time.strftime("%Y-%m-%d", time.localtime())
        records = c.fetch_all(sql=req_sql)

    for record in records:
        if record["owner_id"] == owner_id:
            return record
    return None
