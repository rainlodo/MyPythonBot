import asyncio
import random
from pathlib import Path
import re
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model.relationship import Member
from graia.broadcast import Broadcast
from .blhx import allow_groups
from .Coin_manager import CoinManager


channel = Channel.current()
channel.name("发病")
channel.description("哼哼哼哼，啊啊啊啊啊啊~")
channel.description("发病语句来自 https://github.com/Ikaros-521/nonebot_plugin_random_stereotypes")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))

with open(Path("data", "other", "FDcentences.txt"), 'r', encoding="utf-8") as f:
  lines = f.readlines()

data = [] 
for line in lines:
  # 使用正则表达式提取双引号里的句子
  try:
    sentence = re.search(r'\s{4}"([^"]*)",', line).group(1) 
    data.append(sentence)
  except:
    pass

@bcc.receiver(GroupMessage)
async def fabing(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    "use QQ number to sign_in to get coins"
    if group.id in allow_groups:
        sender = member.id
        try:
            current_coins = await manager.get_coins(sender)
        except:
            current_coins = 0
        if message.display[:3] == "#发病" and current_coins > 1:
            # 获取发病对象
            text = message.display
            target = text.split()[1:] 
            random_sentence = random.choice(data)
            # 使用正则表达式匹配\\n 并替换为 \n 以便于换行正常工作
            random_sentence = re.sub(r'\\n', '\n', random_sentence)
            random_sentence = random_sentence.replace("{target_name}", target[0])
            await app.send_message(group, MessageChain(str(random_sentence)), quote=source)
