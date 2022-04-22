import re
from datetime import date
from typing import List
from constant.type import FeedbackType
from constant.words import BotDefault

FEEDBACK_STATUS_DEFAULT = 0
FEEDBACK_STATUS_FIX = 1


def filter_emoji(des_str, result_str=""):
    # 过滤表情
    res = re.compile("[\U00010000-\U0010ffff\\uD800-\\uDBFF\\uDC00-\\uDFFF]")
    return res.sub(result_str, des_str)


def get_emoji(status: int):
    if status == FEEDBACK_STATUS_DEFAULT:
        return "❓"
    elif status == FEEDBACK_STATUS_FIX:
        return "✅"


def get_duty_emoji(duty_time=None):
    if duty_time == date.today().strftime("%Y-%m-%d"):
        return "✅" + BotDefault.DEFAULT_DUTY
    else:
        return ""


def get_user_list(params: str) -> List[str]:
    user_list = params.replace("<@", "").replace(">", "").replace(" ", "").replace("\xa0", "").split("!")
    user_list.remove("")
    return user_list


def get_feedbacks_markdown_content(feedback_list) -> str:
    markdown_content = "今日反馈列表\n------\n"

    if len(feedback_list) == 0:
        markdown_content += "暂无反馈"

    for feedback in feedback_list:
        if feedback is not None:
            markdown_content += get_feedback_item_markdown(feedback)
    return markdown_content


def get_feedback_item_markdown(feedback) -> str:
    status_emoji = "️☑️" if (feedback["feedback_status"] == 1) else "⬜️"
    status_text = "已解决" if (feedback["feedback_status"] == 1) else "未解决"
    status_type = "问题反馈" if (feedback["feedback_type"] == FeedbackType.BugType) else "产品反馈"

    str_build = "\n\n\u200B%s %s**%s**: %s" + "\n\n> 反馈人: %s" + "\n> 解决状态: %s"
    return str_build % (
        status_emoji,
        status_type,
        str(feedback["id"]),
        feedback["feedback_text"],
        feedback["feedback_user_name"],
        status_text,
    )


def get_owners_markdown_content(owners) -> str:
    markdown_content = "值班表排期「最近7天」\n------\n"
    i = 0
    j = 0
    while i < 7:
        owner1 = owners[j]
        j = j + 1
        if j < len(owners) and owner1["on_duty_time"] == owners[j]["on_duty_time"]:
            owner2 = owners[j]
            j = j + 1
            markdown_content += "%s\t%s\n\n>「%s」\t%s\n「%s」\t%s\n\n" % (
                owner1["on_duty_time"],
                get_duty_emoji(owner1["on_duty_time"]),
                owner1["owner_type"],
                owner1["owner_name"],
                owner2["owner_type"],
                owner2["owner_name"],
            )
        elif owner1 is not None:
            markdown_content += "%s\n\n> 「%s」\t%s%s\n\n" % (
                owner1["on_duty_time"],
                owner1["owner_type"],
                owner1["owner_name"],
                get_duty_emoji(owner1["on_duty_time"]),
            )
        i = i + 1

    return markdown_content
