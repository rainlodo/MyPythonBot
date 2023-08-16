import asyncio
from datetime import datetime
import aiohttp
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, FriendMessage, Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.ariadne.model.relationship import Member
from graia.broadcast import Broadcast
from graia.ariadne.message.element import Image
from .blhx import allow_groups
import json
from .coin_manager import CoinManager


channel = Channel.current()
channel.name("my_setu")
channel.description("属于自己的简单的涩涩")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))

async def get_sese(tags: list):
    url = 'https://api.lolicon.app/setu/v2'
    headers = {'Content-Type': 'application/json'}
    proxies = 'http://127.0.0.1:7890'
    print(tags)
    await asyncio.sleep(2)
    try:
        data = json.dumps({'tag': tags, 'size': 'regular'})
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, proxy=proxies) as response:
                response_json = await response.json()
                print(response_json)
                img_url = response_json['data'][0]['urls']['regular']
                print(img_url)
                async with session.get(img_url, proxy=proxies) as img_response:
                    img_bytes = await img_response.read()
    except:
        return (False, False if data == [] else True)

    return (img_bytes, True)

@bcc.receiver(GroupMessage)
async def sign_in(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    "use QQ number to sign_in to get coins"
    if group.id in allow_groups:
        sender = member.id
        if message.display == "#签到":
            get_coins = await manager.sign_in(sender, datetime.now())
            current_coins = await manager.get_coins(sender)
            await app.send_message(group, MessageChain("签到成功，本次签到获得{}个硬币，你现在有{}个硬币。".format(get_coins, current_coins)), quote=source)

@bcc.receiver(GroupMessage)
async def setu(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    "一个获取涩图的函数"
    if group.id in allow_groups:
        sender = member.id
        try:
            current_coins = await manager.get_coins(sender)
        except:
            current_coins = 0
        if message.display[:3] == "#来份" and current_coins > 10:
            # 获取标签
            text = message.display
            tags = text.split()[1:] 
            img_bytes, non_data = await get_sese(tags)

            if img_bytes:
                try:
                    event = await app.send_message(group, MessageChain(Image(data_bytes=img_bytes)), quote=source)
                except:
                    await app.send_message(group, MessageChain("发送失败,稍后再试！"), quote=source)
            else:
                if ~non_data:
                    await app.send_message(group, MessageChain("tag 搜索结果为空，请使用其他 tag 继续！"), quote=source)
                else:
                    await app.send_message(group, MessageChain("网络异常,稍后再试！"), quote=source)

            try:
                if event.source.id > 0:
                    await manager.set_coins(sender, current_coins - 10)
                else:
                    await app.send_message(group, MessageChain("涩图被傻呗腾讯吃了，已新增 10 硬币，请重试。"), quote=source)
                    await manager.set_coins(sender, current_coins + 10)
            except:
                print(Exception)

        elif  message.display[:3] == "#来份" and current_coins < 10:
            await app.send_message(group, MessageChain("当前硬币余额为 {}，硬币余额不足 10，请获取更多硬币后重试。\ntips:为什么不试试签到呢？(#签到)".format(current_coins)), quote=source)

@bcc.receiver(FriendMessage)
async def setu(app: Ariadne, message: MessageChain, friend: Friend):
    "一个获取涩图的函数"
    if friend.id == 2591212935:
        if message.display[:3] == "#来份":
            text = message.display
            tags = text.split()[1:] 
            img_bytes = get_sese(tags)
            if img_bytes:
                try:
                    await app.send_friend_message(2591212935,
                                                   MessageChain(Image(data_bytes=img_bytes)))
                except:
                    await app.send_friend_message(2591212935, MessageChain("发送失败,稍后再试！"))
            else:
                await app.send_friend_message(2591212935, MessageChain("网络异常,稍后再试！"))