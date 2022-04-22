import asyncio

import qqbot
import schedule
import time
from datetime import date
from multiprocessing import Process

from constant import config
from constant.words import BotNotify
from dao.owner import get_duty_owners, reset_owner
from dao.sign import get_signed_in_record, init_sign_record
from flow.reply import notify_text


def start_schedule_processes():
    p = Process(target=schedule_sign_notify)
    p.start()


def schedule_sign_notify():
    """
    每天定时提醒签到
    """
    schedule.every().day.at("10:00").do(notify_sign_in)
    schedule.every().day.at("10:30").do(notify_sign_in)
    schedule.every().day.at("11:00").do(notify_sign_in)

    schedule.every().day.at("22:30").do(notify_sign_out)
    schedule.every().day.at("23:00").do(notify_sign_out)
    schedule.every().day.at("23:30").do(notify_sign_out)

    schedule.every().day.at("03:00").do(reset_owner_for_today)

    while True:
        schedule.run_pending()
        time.sleep(1)


def notify_sign_in():
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


def notify_sign_out():
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


def reset_owner_for_today():
    owners = get_duty_owners(date.today())
    qqbot.logger.info("reset_owner_for_today: owner %s" % owners)

    for owner in owners:
        reset_owner(owner["owner_id"], date.today(), owner["owner_type"])
        init_sign_record(owner["owner_id"], owner["owner_name"])
