import time
from datetime import date
from typing import List

import qqbot

from constant import config
from constant.type import OwnerType, FeedbackType
from constant.words import BotReply, BotNotify, BotDefault
from dao.feedback import write_feedback, get_feedback, fix_feedback
from dao.owner import (
    add_owner,
    Owner,
    remove_owner,
    change_owner,
    reset_owner,
    get_owner,
    get_duty_owner,
    get_duty_owners,
    get_owner_by,
)
from dao.sign import get_signed_in_record, sign_in, sign_out, init_sign_record
from flow.reply import (
    reply_text_with_reference,
    reply_text,
    reply_markdown_content,
)
from flow.schedule import start_schedule_processes
from service.qwx_api import send_qwx_message
from util.decorated import Command, Role
from util.string import (
    get_user_list,
    get_feedbacks_markdown_content,
    get_owners_markdown_content,
)


async def _query_today_feedback(message):
    now_date = time.strftime("%Y-%m-%d", time.localtime())
    feedbacks = get_feedback(now_date)

    markdown_content = get_feedbacks_markdown_content(feedbacks)
    qqbot.logger.info("handle_get_feedback, feedback_list: %s" % feedbacks)
    await reply_markdown_content(message.channel_id, message.id, markdown_content)


async def _query_owner_list(message):
    owners = get_owner(date.today())

    markdown_content = get_owners_markdown_content(owners)
    qqbot.logger.info("query_owner_list, owners: %s" % owners)
    await reply_markdown_content(message.channel_id, message.id, markdown_content)


async def _notice_manager(feedback_id, message, notify, owner_on_duty_id, owner_on_duty_name, params):
    # 内部子频道通知
    await reply_markdown_content(
        message_id=message.id,
        markdown_content=notify
        % (
            "<#%s>" % message.channel_id,
            feedback_id,
            message.author.username,
            params,
            "<@%s>" % owner_on_duty_id,
        ),
        channel_id=config["params"]["channelId"],
    )
    # 内部企业微信群通知
    channel_api = qqbot.AsyncChannelAPI(t_token, False)
    channel = await channel_api.get_channel(message.channel_id)
    await send_qwx_message(
        markdown_content=notify
        % (
            "<#%s>" % channel.name,
            feedback_id,
            message.author.username,
            params,
            "<@%s>" % owner_on_duty_name,
        )
    )


async def _handle_feedback(message: qqbot.Message, feedback_type: str, params=None):
    """
    /问题反馈
    """
    if params is None or params == "":
        # 参数不符合就不消费这个事件
        return False
    qqbot.logger.info(
        "handle_feedback name: %s, message_id: %s, feedback_text: %s" % (message.author.username, message.id, params)
    )

    # 查询当天的值班人员
    owner_on_duty = get_duty_owner(date.today(), feedback_type)
    owner_on_duty_id = owner_on_duty["owner_id"]
    owner_on_duty_name = owner_on_duty["owner_name"]
    owner_on_duty_type = owner_on_duty["owner_type"]
    feedback_type = None
    notify = None
    reply = None
    if owner_on_duty_type == OwnerType.TechStaff:
        feedback_type = FeedbackType.BugType
        notify = BotNotify.FEEDBACK_NOTIFY_MD
        reply = BotReply.FEEDBACK_REPLY
    else:
        feedback_type = FeedbackType.StoryType
        notify = BotNotify.FEEDBACK_RECOMMEND_NOTIFY_MD
        reply = BotReply.FEEDBACK_RECOMMEND_REPLY

    if not owner_on_duty_id:
        owner_on_duty_id = config["params"]["userId"]
        owner_on_duty_name = config["params"]["userName"]

    # 记录数据
    feedback_id = write_feedback(
        feedback_user_name=message.author.username,
        feedback_user_id=message.author.id,
        feedback_message_id=message.id,
        feedback_text=params,
        feedback_owner_name=owner_on_duty_name,
        feedback_owner_id=owner_on_duty_id,
        feedback_type=feedback_type,
    )

    # 回复用户
    await reply_text_with_reference(message, content=reply % ("<@%s>" % owner_on_duty_id))

    # 值班群通知
    await _notice_manager(feedback_id, message, notify, owner_on_duty_id, owner_on_duty_name, params)


@Command("/帮助")
async def handle_get_help(message: qqbot.Message, params=None):
    """
    /帮助
    """
    await reply_markdown_content(message.channel_id, message.id, BotDefault.DEFAULT_HELP_MD)
    return True


@Command("/查看值班表")
async def handle_get_duty(message: qqbot.Message, params=None):
    """
    /查看值班表
    """
    await _query_owner_list(message)
    return True


@Command("/问题反馈")
async def handle_feedback_bug(message: qqbot.Message, params=None):
    await _handle_feedback(message, OwnerType.TechStaff, params)
    return True


@Command("/产品建议")
async def handle_feedback_story(message: qqbot.Message, params=None):
    await _handle_feedback(message, OwnerType.ProductStaff, params)
    return True


@Command("/当日反馈")
@Role("值班人员,管理员")
async def handle_get_feedback(message: qqbot.Message, params=None):
    """
    /当日反馈
    """
    await _query_today_feedback(message)
    return True


@Command("/标注解决")
@Role("值班人员,管理员")
async def handle_fix_feedback(message: qqbot.Message, params=None):
    """
    /标注解决
    """
    # 标注后
    result = fix_feedback(params)
    if result is None:
        await reply_text(message, BotReply.FEEDBACK_FIX_ERROR_REPLY % params)
        return True
    else:
        await reply_text(message, BotReply.FEEDBACK_FIX_REPLY % params)

    # 查询数据
    await _query_today_feedback(message)
    return True


@Command("/值班签到")
@Role("值班人员")
async def handle_sign_in(message: qqbot.Message, params=None):
    """
    /值班签到
    """
    qqbot.logger.info("handle_sign_in name: %s, user_id: %s" % (message.author.username, message.author.id))

    sign_record = get_signed_in_record(message.author.id)
    if sign_record is None:
        return True

    # 判断该成员当天是否签到过了
    if sign_record["sign_in_time"] is not None:
        await reply_text(message, content=BotReply.ALREADY_SIGNED_IN % "<@%s>" % message.author.id)
        return True

    # 写数据库
    sign_in(sign_record["id"])
    # 发送回复
    await reply_text(message, content=BotReply.SIGN_IN_REPLY % "<@%s>" % message.author.id)
    return True


@Command("/值班签出")
@Role("值班人员")
async def handle_sign_out(message: qqbot.Message, params=None):
    """
    /值班签出
    """
    qqbot.logger.info("handle_sign_in name: %s, user_id: %s" % (message.author.username, message.author.id))

    sign_record = get_signed_in_record(message.author.id)
    if sign_record is None:
        return True

    # 判断该成员当天是否签到过了
    if sign_record["sign_in_time"] is None:
        await reply_text(message, content=BotReply.DID_NOT_SIGNED_IN % "<@%s>" % message.author.id)
        return True

    # 写数据库
    sign_out(sign_record["id"])
    # 发送回复
    await reply_text(message, content=BotReply.SIGN_OUT_REPLY % "<@%s>" % message.author.id)
    return True


@Command("/值班人员增加")
@Role("管理员")
async def handle_add_owner(message: qqbot.Message, params=None):
    """
    /值班人员添加
    """
    if params is None or params == "":
        # 参数不符合就不消费这个事件
        return False
    # 分割多参数
    owners: List = get_user_list(params)
    # 查询昵称保存
    owner_list = []
    member_api = qqbot.AsyncGuildMemberAPI(t_token, False)
    for owner_id in owners:
        member = await member_api.get_guild_member(message.guild_id, owner_id)
        owner_list.append(Owner(id=owner_id, name=member.nick, owner_type=OwnerType.TechStaff))
    if not add_owner(owner_list):
        return False
    # 从今天值班人员开始重新排
    duty_owners = get_duty_owners(date.today())
    for duty_owner in duty_owners:
        if duty_owner is None:
            owner_on_duty_id = owner_list[0]
        else:
            owner_on_duty_id = duty_owner["owner_id"]

        if not reset_owner(owner_on_duty_id, date.today(), duty_owner["owner_type"]):
            return False
    await _query_owner_list(message)
    return True


@Command("/值班人员移除")
@Role("管理员")
async def handle_remove_owner(message: qqbot.Message, params=None):
    """
    /值班人员移除
    """
    if params is None or params == "":
        # 参数不符合就不消费这个事件
        return False
    # 分割多参数
    owners_id: List = get_user_list(params)

    # 获取今天值班人员
    owners = get_duty_owners(date.today())
    for owner in owners:
        if owners is None:
            owner_on_duty_id = config["params"]["userId"]
        else:
            owner_on_duty_id = owner["owner_id"]
        if owner_on_duty_id in owners_id:
            # 不能删除当前值班人员
            await reply_text(message, BotReply.NO_DELETE_DUTY_REPLY)
            return True
    if not remove_owner(owners_id):
        return False
    # 开始重新排
    for owner in owners:
        if not reset_owner(owner["owner_id"], date.today(), owner["owner_type"]):
            return False
    await _query_owner_list(message)
    return True


@Command("/值班交换")
@Role("管理员")
async def handle_change_owner(message: qqbot.Message, params=None):
    """
    /值班交换
    """
    if params is None or params == "":
        # 参数不符合就不消费这个事件
        return False
    # 分割多参数
    owners: List = get_user_list(params)
    if len(owners) != 2:
        return False
    if not change_owner(owners[0], owners[1]):
        return False
    await _query_owner_list(message)
    return True


@Command("/重新排班")
@Role("管理员")
async def handle_reset_owner(message: qqbot.Message, params=None):
    """
    /重新排班
    签到的时候如果没有发现当天的值班人员需要重新执行这个功能
    """
    if params is None or params == "":
        # 参数不符合就不消费这个事件
        return False
    # 分割多参数
    owners_id: List = get_user_list(params)
    # 修改指定的人员为今天值班人员
    for owner_id in owners_id:
        owner = get_owner_by(owner_id)
        if owner is None:
            return False
        # 重新给值班表指定值班日期
        if not reset_owner(owner_id, date.today(), owner["owner_type"]):
            return False
        init_sign_record(owner["owner_id"], owner["owner_name"])
    await _query_owner_list(message)
    return True


async def _message_handler(event, message: qqbot.Message):
    # 打印返回信息
    qqbot.logger.info(
        "event %s" % event
        + ",receive message %s, guild_id: %s, channel_id: %s" % (message.content, message.guild_id, message.channel_id)
    )

    # 注册指令handler
    handlers = [
        handle_get_help,  # 帮助
        handle_get_duty,  # 查看值班表
        handle_feedback_bug,  # 问题反馈
        handle_feedback_story,  # 需求建议
        handle_get_feedback,  # 获取反馈
        handle_fix_feedback,  # 标注解决
        handle_sign_in,  # 签到
        handle_sign_out,  # 签出
        handle_add_owner,  # 值班人员增加
        handle_remove_owner,  # 值班人员移除
        handle_change_owner,  # 值班人员交换
        handle_reset_owner,  # 重新排班
    ]
    for handler in handlers:
        if await handler(message=message):
            return
    await reply_text(message, BotReply.NO_MATCH_REPLY)


if __name__ == "__main__":
    # 开始定时任务
    start_schedule_processes()

    # async的异步接口的使用示例
    t_token = qqbot.Token(config["token"]["appid"], config["token"]["token"])
    qqbot_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler)
    qqbot.async_listen_events(t_token, False, qqbot_handler)
