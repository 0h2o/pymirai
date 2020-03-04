import logging
import requests
import asyncio
import aiohttp
from .Network import Network
from .Message import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("asyncio").setLevel(logging.INFO)

class Bot(object):
    def __init__(self, qq : int, auth_key : str, ip : str, port : int):
        self.qq = qq
        self.auth_key = auth_key
        self.ip = ip
        self.port = port
        self.session = ''
        self.event_handler_list = []
        self.event_queue = asyncio.Queue(0)
    
    async def __aenter__(self):

        ret = await Network.post(f"http://{self.ip}:{self.port}/auth", {"authKey" : self.auth_key})
        if self.retValue(ret) == 0:
            logger.info("连接 core 正常")
            self.session = ret['session']
        else:
            logger.critical("错误的 MIRAI API HTTP auth key", exc_info="Wrong HTTP auth key")
       
        ret = await Network.post(f"http://{self.ip}:{self.port}/verify", {
            "sessionKey": self.session,
            "qq": self.qq
        })

        if self.retValue(ret) != 0:
            logger.critical("Verify failed", exc_info="Verify failed")

        return self

    def addEventHandler(self, func):
        self.event_handler_list.append(func)

    async def dispatchEvent(self, events):
        for e in events:
            logger.debug('Dispatching upcoming event....')
            for hd in self.event_handler_list:
                asyncio.create_task(hd(self, e))
        pass

    async def loopEvent(self):
        logger.info('Listening......')
        while True:
            events = await Network.get(f"http://{self.ip}:{self.port}"
            f"/fetchMessage?sessionKey={self.session}&count=10")
            await self.dispatchEvent(events)
            await asyncio.sleep(0.5) # interval

    async def sendGroupMessage(self, target, msg, quote=None):
        data = {
            "sessionKey": self.session,
            "target": target,
            "messageChain": msg,
        }
        if quote is not None:
            data.setdefault('quote', int(quote))

        ret = await Network.post(f"http://{self.ip}:{self.port}/sendGroupMessage", data)

        if self.retValue(ret) != 0 and quote is not None:
            logger.info('Sending failed, fallback using no quote instead.')
            data.__delitem__('quote')
            ret = await Network.post(f"http://{self.ip}:{self.port}/sendGroupMessage", data)

        if self.retValue(ret) == 0: logger.info('Send message ok')
        else: logger.critical('Sending message failed!')
        
        return self.retValue(ret) == 0
        
    async def uploadImage(self, image_path : str, friend_or_group : str):
        assert(friend_or_group in ['friend', 'group'])
        ret = await Network.uploadImage(f"http://{self.ip}:{self.port}/uploadImage", 
        image_path, self.session, friend_or_group)
        if ret != 0:
            logger.info('Upload image ok.')
            return ret
        else:
            logger.critical('Upload image failed!')
    
    async def stupidUploadImage(self, image_path:str, friend_or_group:str):
        # upload both group and friend images and choose from the returned imageId
        # 因为我本地调的时候有时仅上传一者将会发送失败
        tbl = ['group', 'friend']
        assert(friend_or_group in tbl)
        result = {}
        for each in tbl:
            result[each] = await Network.uploadImage(f"http://{self.ip}:{self.port}/uploadImage", 
            image_path, self.session, each)
        return result[friend_or_group]
        

    async def sendFriendMessage(self, target, message_chain, quote=None):
        assert(type(message_chain)==type([]))
        data = {
            "sessionKey": self.session,
            "target": target,
            "messageChain": message_chain
        }
        if quote is not None:
            assert(type(quote)==type(0))
            data.setdefault('quote', quote)

        ret = await Network.post(f"http://{self.ip}:{self.port}/sendFriendMessage", data)

        if self.retValue(ret) != 0 and quote is not None:
            logger.info('Sending failed, fallback using no quote instead.')
            data.__delitem__('quote')
            ret = await Network.post(f"http://{self.ip}:{self.port}/sendFriendMessage", data)

        if self.retValue(ret) == 0: logger.info('Send friend message ok')
        else: logger.critical('Sending friend message failed!')

        return self.retValue(ret) == 0

    def retValue(self, ret):
        try: return ret['code']
        except: return 'error'

    async def releaseSession(self):
        if self.session != '':
            logger.info('Exiting...')
            ret = await Network.post(f"http://{self.ip}:{self.port}/release", {
                "sessionKey": self.session,
                "qq": self.qq
            })
            if self.retValue(ret) == 0: logger.info('Session released.')
            else: logger.critical(f'Session releasing failed, ret value: {self.retValue(ret)}.')


    async def __aexit__(self, *excinfo):
        await self.releaseSession()


class FriendMessageEvent(object):
    def __init__(self, bot : Bot, event):
        assert(event['type']=='FriendMessage')
        self.bot = bot
        self.event = event
        self.sender = event['sender']['id']
        self.message_chain = event['messageChain']
        self.source = self.message_chain[0]['id']
    async def reply_message(self, message_chain, quote = False):
        assert(type(message_chain)==type([]))
        await self.bot.sendFriendMessage(self.sender, message_chain, self.source if quote else None)
    async def reply_text(self, text, quote = False):
        await self.reply_message([miraiPlain(text)], quote)
    async def reply_image(self, image_id, quote = False):
        await self.reply_message([miraiImage(image_id)], quote)
    
class GroupMessageEvent(object):
    def __init__(self, bot : Bot, event):
        assert(event['type']=='GroupMessage')
        self.bot = bot
        self.event = event
        self.sender_id = event['sender']['id'] # 发送者qq
        self.sender_member_name = event['sender']['memberName'] # 发送者群名片
        self.sender_group_id = event['sender']['group']['id'] # 群id
        self.sender_group_name = event['sender']['group']['name'] # 群名
        self.message_chain = event['messageChain']
        self.source = self.message_chain[0]['id'] # 该消息id，用于引用（撤回、回复）
    async def reply_message(self, message_chain, quote = False):
        assert(type(message_chain)==type([]))
        await self.bot.sendGroupMessage(self.sender_group_id, message_chain, self.source if quote else None)
    async def reply_text(self, text, quote = False):
        await self.reply_message([miraiPlain(text)], quote)
    async def reply_image(self, image_id, quote = False):
        await self.reply_message([miraiImage(image_id)], quote)

class GroupMessageHandler(object):
    def __init__(self, restricted_sender=[], restricted_group=[]):
        self.restricted_sender = restricted_sender
        self.restricted_group = restricted_group
    def __call__(self, handler):
        async def wrapped_f(bot, event):
            if event['type'] != 'GroupMessage': return
            if len(self.restricted_sender) > 0:
                if event['sender']['id'] not in self.restricted_sender: return
            if len(self.restricted_group) > 0:
                if event['sender']['group']['id'] not in self.restricted_group: return
            await handler(GroupMessageEvent(bot, event))
        return wrapped_f


class FriendMessageHandler(object):
    def __init__(self, restricted_sender=[]):
        self.restricted_sender = restricted_sender
    def __call__(self, handler):
        async def wrapped_f(bot, event):
            if event['type'] != 'FriendMessage': return
            if len(self.restricted_sender) > 0:
                if event['sender']['id'] not in self.restricted_sender: return
            await handler(FriendMessageEvent(bot, event))
        return wrapped_f

