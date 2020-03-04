# Py-mirai

Thanks for the great work of [Mirai](https://github.com/mamoe/mirai).

This python binding relies on [Mirai Console v0.3.1](https://github.com/mamoe/mirai-console/releases/tag/v0.3.1) with [mirai-api-http-1.0.0](https://github.com/mamoe/mirai-api-http/releases/tag/1.0.0) installed.

## Write a bot from scratch

```python
from pymirai import *

@FriendMessageHandler(restricted_sender=[])
async def friend_msg_handler(event : FriendMessageEvent):
    # 纯文字
    await event.reply_text('hello, world!', quote=True)
    # 组合消息 + 图片
    image_id = await event.bot.uploadImage('sample.gif', 'friend')
    message_chain = [
        miraiPlain('photo\n'),
        miraiImage(image_id),
        miraiPlain('\nend')
    ]
    await event.reply_message(message_chain)
    # 复读
    mc = event.message_chain
    await event.reply_message(mc)

async def main():
    async with Bot(QQNUM, 'auth_key', 'server', 'port') as bot:
        bot : Bot
        bot.addEventHandler(friend_msg_handler)
        await bot.loopEvent()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
```

## Info

This package is merely a non-complete python wrapper for mirai-api-http, use it at your own risk and for learning purposes only.

For a better experience, see [kuriyama](https://pypi.org/project/kuriyama/).