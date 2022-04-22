from typing import List

import qqbot
from qqbot.model.message import (
    MessageReference,
    MessageSendRequest,
    MessageEmbed,
    MessageEmbedField,
)

from constant import config
from constant.words import BotDefault

APPID = config["token"]["appid"]
TOKEN = config["token"]["token"]


async def reply_text(message: qqbot.Message, content: str, channel_id=None):
    # 发送回复消息
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False).with_timeout(5)
    if channel_id is None:
        message_channel_id = message.channel_id
    else:
        message_channel_id = channel_id
    await message_api.post_message(
        message_channel_id,
        MessageSendRequest(
            content=content,
            msg_id=message.id,
        ),
    )


async def notify_text(channel_id: str, content: str):
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False).with_timeout(5)
    await message_api.post_message(channel_id, MessageSendRequest(content=content))


async def reply_text_list(reply_message: qqbot.Message, content_list: List, title):
    # 发送回复消息
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False)
    # 构造消息
    total_content = ""
    if len(content_list) == 0:
        total_content = BotDefault.DEFAULT_GET_FEEDBACK
    else:
        total_content = total_content.join([content + "\n" for content in content_list])

    # 通过api发送回复消息
    await message_api.post_message(
        reply_message.channel_id,
        qqbot.MessageSendRequest(content=title + "\n" + total_content, msg_id=reply_message.id),
    )


async def reply_markdown_content(channel_id: str, message_id: str, markdown_content: str):
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False)

    markdown = qqbot.model.message.MessageMarkdown()
    markdown.content = markdown_content

    # 发送 markdown 消息
    await message_api.post_message(
        channel_id,
        qqbot.MessageSendRequest(markdown=markdown, msg_id=message_id),
    )


async def reply_text_with_reference(message: qqbot.Message, content: str):
    # 发送回复消息
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False)
    reference = MessageReference()
    reference.message_id = message.id
    await message_api.post_message(
        message.channel_id,
        MessageSendRequest(
            content=content,
            msg_id=message.id,
            message_reference=reference,
        ),
    )


async def reply_embed(reply_message: qqbot.Message, content_list: List, title, prompt):
    # 发送回复消息
    message_api = qqbot.AsyncMessageAPI(qqbot.Token(APPID, TOKEN), False)
    # 构造消息发送请求数据对象
    embed = MessageEmbed()
    embed.title = title
    embed.prompt = prompt
    # 构造内嵌消息fields
    if len(content_list) == 0:
        embed.fields = [MessageEmbedField(name=BotDefault.DEFAULT_GET_FEEDBACK)]
    else:
        embed.fields = [MessageEmbedField(name=content) for content in content_list]

    # 通过api发送回复消息
    await message_api.post_message(
        reply_message.channel_id,
        qqbot.MessageSendRequest(embed=embed, msg_id=reply_message.id),
    )
