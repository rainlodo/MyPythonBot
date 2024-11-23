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
from .Coin_manager import CoinManager
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("some games")
channel.description("属于自己的简单的小游戏")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
coin_manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))