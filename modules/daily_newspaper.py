import asyncio
import aiohttp
from creart import create
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import Group, GroupMessage
from graia.broadcast import Broadcast
from graia.ariadne.message.element import Image
from .Config_manager import ConfigManager
from graia.ariadne.model.relationship import Member
from graia.ariadne.message.parser.base import DetectPrefix

channel = Channel.current()
channel.name("Repeater")
channel.description("复读机")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))

async def get_img():
    url = 'http://api.2xb.cn/zaob'
    try:
        response_json = {} # 用于存储 api 返回的数据
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()
                img_url = response_json['imageUrl']
                async with session.get(img_url) as img_response:
                    img_bytes = await img_response.read()
    except:
        return (False, False if response_json == {} else response_json)

    return (img_bytes, response_json)

@bcc.receiver(GroupMessage, decorators=[DetectPrefix('#日报')])
async def daily_newspaper(app: Ariadne,  message: MessageChain, group: Group, sender: Member):
    "复读机"
    if group.id in await conf_manager.get_groups_list() and sender.id not in await conf_manager.get_black_list():
        feature = await conf_manager.get_group_features(group.id)
        if feature.get('daily_newspaper', True):
            img_bytes, response_json = await get_img()
            if img_bytes:
                await app.send_message(group, MessageChain(Image(data_bytes=img_bytes)))
            else:
                await app.send_message(group, MessageChain("获取失败，请重试！"))


