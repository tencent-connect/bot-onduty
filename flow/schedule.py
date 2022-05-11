import asyncio
import traceback

import qqbot
import schedule
import time
from datetime import date
from multiprocessing import Process

from qqbot.core.exception.error import AuthenticationFailedError

from constant import config
from constant.words import BotNotify
from dao.owner import get_duty_owners, reset_owner
from dao.sign import get_signed_in_record, init_sign_record
from flow.reply import notify_text, reply_markdown_content
from flow.operate import mute_all, end_mute_all
from util.string import get_morning_markdown_content


def start_schedule_processes():
    p = Process(target=schedule_sign_notify)
    p.start()


def schedule_sign_notify():
    """
    每天定时提醒签到
    """

    schedule.every().day.at("08:00").do(post_morning_public_notification)

    schedule.every().day.at("10:00").do(notify_sign_in)
    schedule.every().day.at("10:30").do(notify_sign_in)
    schedule.every().day.at("11:00").do(notify_sign_in)

    schedule.every().day.at("22:30").do(notify_sign_out)
    schedule.every().day.at("23:00").do(notify_sign_out)
    schedule.every().day.at("23:30").do(notify_sign_out)

    schedule.every().day.at("23:59").do(post_evening_public_notification)

    schedule.every().day.at("03:00").do(reset_owner_for_today)

    while True:
        schedule.run_pending()
        time.sleep(1)


def post_morning_public_notification():
    duty_owners = get_duty_owners(date.today())
    qqbot.logger.info("inform_public, today's duty owners are: %s" % duty_owners)

    try:
        loop = asyncio.get_event_loop()
        # 解除禁言
        loop.run_until_complete(
            end_mute_all()
        )
        # 发送消息告知所有人
        markdown_content = get_morning_markdown_content(duty_owners)
        if not markdown_content:
            return
        loop.run_until_complete(
            reply_markdown_content(config["params"]["publicChannelId"], markdown_content)
        )
    except AuthenticationFailedError as e:
        qqbot.logger.error("post_morning_public_notification failed: %s" % e.msgs)
    except Exception as e:
        qqbot.logger.error("notify_sign_in failed: %s" % traceback.format_exc())


def post_evening_public_notification():
    duty_owners = get_duty_owners(date.today())
    qqbot.logger.info("inform_public, everyone is muted after 12 pm: %s" % duty_owners)

    try:
        loop = asyncio.get_event_loop()
        # 解除禁言
        loop.run_until_complete(
            mute_all()
        )
        # 发送消息告知所有人
        loop.run_until_complete(
            reply_markdown_content(config["params"]["publicChannelId"], BotNotify.EVENING_NOTIFY_MD)
        )
    except AuthenticationFailedError as e:
        qqbot.logger.error("post_evening_public_notification failed: %s" % e.msgs)
    except Exception as e:
        qqbot.logger.error("notify_sign_in failed: %s" % traceback.format_exc())


def notify_sign_in():
    try:
        duty_owners = get_duty_owners(date.today())
        if duty_owners is None:
            return

        for duty_owner in duty_owners:
            sign_record = get_signed_in_record(duty_owner["owner_id"])
            qqbot.logger.info("notify_sign_in: sign_record %s" % sign_record)

            if sign_record is None:
                return

            if sign_record["sign_in_time"] is None:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    notify_text(
                        config["params"]["channelId"], content=BotNotify.NOTIFY_SIGN_IN % "<@%s>" % duty_owner["owner_id"]
                    )
                )
    except Exception as e:
        qqbot.logger.error("notify_sign_in failed: %s" % traceback.format_exc())


def notify_sign_out():
    try:
        duty_owners = get_duty_owners(date.today())
        if duty_owners is None:
            return

        for duty_owner in duty_owners:
            sign_record = get_signed_in_record(duty_owner["owner_id"])
            qqbot.logger.info("notify_sign_out: sign_record %s" % sign_record)

            if sign_record is None:
                return

            if sign_record["sign_out_time"] is None:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    notify_text(
                        config["params"]["channelId"], content=BotNotify.NOTIFY_SIGN_OUT % "<@%s>" % duty_owner["owner_id"]
                    )
                )
    except Exception as e:
        qqbot.logger.error("notify_sign_in failed: %s" % traceback.format_exc())


def reset_owner_for_today():
    owners = get_duty_owners(date.today())
    qqbot.logger.info("reset_owner and init_sign_record: owner %s" % owners)

    for owner in owners:
        reset_owner(owner["owner_id"], date.today(), owner["owner_type"])
        init_sign_record(owner["owner_id"], owner["owner_name"])
