from pymirai import *

@FriendMessageHandler(restricted_sender=[])
async def friend_msg_handler(event : FriendMessageEvent):
    # 纯文字
    await event.reply_text('hello, world!', quote=True)
    # 组合消息+图片
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