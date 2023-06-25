import asyncio
from datetime import datetime
import time
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
from .coin_manager import CoinManager


channel = Channel.current()
channel.name("some games")
channel.description("属于自己的简单的小游戏")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))