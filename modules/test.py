import asyncio
import random
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.broadcast import Broadcast
import graiax.silkcoder as silkcoder
from pathlib import Path
from graia.ariadne.message.element import Voice
from .tools import sub_sentence_exist
from graia.ariadne.message.element import Image
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("弱鸡qwq")
channel.description("我真的是fw")
channel.author("rainlodo")

bcc = create(Broadcast)
loop = asyncio.get_event_loop()
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))

@bcc.receiver(GroupMessage)
async def powerless(app: Ariadne, group: Group, message: MessageChain):
    "一个卖弱的函数"
    if group.id in await conf_manager.get_groups_list():
        if sub_sentence_exist(message.display, ['漠神', '漠尘', '漠天帝', '希儿老婆']) :
            path = Path("data", "voices")
            files = [str(f) for f in path.glob('**/*') if f.is_file()]  # 获取指定目录下的所有文件
            
            if len(files) > 0:
                random_file = random.choice(files)  # 随机抽取一个文件
                voice_bytes = await silkcoder.async_encode(random_file)
                # 在此处调用您需要传入文件路径的函数，并将文件路径作为参数传入
            else:
                print('指定目录下没有文件！')
            await app.send_message(group, MessageChain(Voice(data_bytes=voice_bytes)))

@bcc.receiver(GroupMessage)
async def share_lucky(app: Ariadne, group: Group, message: MessageChain):
    if group.id in await conf_manager.get_groups_list():
        if message.display == '狗叫' :
             await app.send_message(group, MessageChain(Image(path=Path("data", "imgs", "goujiao.jpg"))))
