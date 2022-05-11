from datetime import datetime, date, timedelta

from constant import config

import qqbot
from qqbot.model.mute import MuteOption

APPID = config["token"]["appid"]
TOKEN = config["token"]["token"]
GUILD_ID = config["params"]["guildId"]


async def mute_all():
    mute_api = qqbot.AsyncMuteAPI(qqbot.Token(APPID, TOKEN), False).with_timeout(5)
    await mute_api.mute_all(GUILD_ID, MuteOption(mute_seconds=str(8 * 3600)))


async def end_mute_all():
    mute_api = qqbot.AsyncMuteAPI(qqbot.Token(APPID, TOKEN), False).with_timeout(5)
    await mute_api.mute_all(GUILD_ID, MuteOption(mute_seconds='0'))
