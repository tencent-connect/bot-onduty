import qqbot
from qqbot.model.mute import MuteOption

from constant import config

APPID = config["token"]["appid"]
TOKEN = config["token"]["token"]
GUILD_ID = config["params"]["guildId"]


async def mute_all():
    mute_api = qqbot.AsyncMuteAPI(qqbot.Token(APPID, TOKEN), False, timeout=5)
    await mute_api.mute_all(GUILD_ID, MuteOption(mute_seconds=str(8 * 3600)))


async def end_mute_all():
    mute_api = qqbot.AsyncMuteAPI(qqbot.Token(APPID, TOKEN), False, timeout=5)
    await mute_api.mute_all(GUILD_ID, MuteOption(mute_seconds='0'))
