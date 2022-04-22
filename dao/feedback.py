from dao.db import DBConn
from util.string import filter_emoji


def write_feedback(
    feedback_user_name: str,
    feedback_user_id: str,
    feedback_message_id: str,
    feedback_owner_name: str,
    feedback_owner_id: str,
    feedback_text: str,
    feedback_type: str,
):
    """
    写反馈
    :param feedback_user_name: 反馈用户昵称
    :param feedback_user_id: 反馈用户id
    :param feedback_message_id: 消息id
    :param feedback_owner_name: 反馈责任人名称
    :param feedback_owner_id: 反馈责任人id
    :param feedback_text: 反馈内容
    :param feedback_type: 反馈类型 取值有 缺陷 需求
    """
    with DBConn(log_time=True) as c:
        feedback_text = filter_emoji(feedback_text)
        run_sql = (
            "insert into t_feedback (feedback_user_name,feedback_user_id,feedback_message_id,"
            "feedback_text,feedback_owner_name,feedback_owner_id,feedback_type) values (%s,%s,%s,%s,%s,%s,%s)"
        )
        run_params = (
            feedback_user_name,
            feedback_user_id,
            feedback_message_id,
            feedback_text,
            feedback_owner_name,
            feedback_owner_id,
            feedback_type,
        )
        return c.insert(sql=run_sql, params=run_params)


def get_feedback(date):
    """
    获取某天的反馈数据
    :param date: 日期 如：22-04-01
    :return:
    """
    with DBConn(log_time=True) as c:
        run_sql = "select * from t_feedback where create_time like '%%%s%%'" % date
        feedbacks = c.fetch_all(sql=run_sql)
        if feedbacks == ():
            return []
        return feedbacks


def fix_feedback(feedback_id):
    """
    标记解决某个反馈
    :param feedback_id: 反馈的id
    """
    with DBConn(log_time=True) as c:
        run_sql = "select count(id) from t_feedback where id=%s"
        run_params = feedback_id
        count = c.get_count(sql=run_sql, params=run_params)
    if count == 0:
        return None

    with DBConn(log_time=True) as c:
        run_sql = "update t_feedback set feedback_status=1 where id=%s"
        run_params = feedback_id
        return c.fetch_all(sql=run_sql, params=run_params)
