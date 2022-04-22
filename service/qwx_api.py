import json

import aiohttp

from constant import config


async def send_qwx_message(markdown_content):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=config["webhook"]["qwx"],
            timeout=5,
            json={
                "msgtype": "markdown",
                "markdown": {"content": markdown_content},
            },
        ) as resp:
            content = await resp.text()
            content_json_obj = json.loads(content)
            return content_json_obj
