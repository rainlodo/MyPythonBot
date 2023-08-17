import asyncio
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.broadcast import Broadcast
from pathlib import Path
from .blhx import allow_groups
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
async def share_lucky(app: Ariadne, group: Group, message: MessageChain):
    if group.id in await conf_manager.get_groups_list():
        if message.display == '狗叫' :
             await app.send_message(group, MessageChain(Image(path=Path("data", "imgs", "goujiao.jpg"))))