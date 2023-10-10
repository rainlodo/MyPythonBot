import asyncio
from creart import create
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import Group, GroupMessage
from graia.broadcast import Broadcast
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("Repeater")
channel.description("复读机")
channel.author("rainlodo")

bcc = create(Broadcast)

group_repeat = {}

# 初始化 CoinManager
loop = asyncio.get_event_loop()
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))

@bcc.receiver(GroupMessage)
async def repeater(app: Ariadne,  message: MessageChain, group: Group):
    "复读机"
    if group.id in await conf_manager.get_groups_list():
        global group_repeat
        feature = await conf_manager.get_group_features(group.id)
        if feature.get('repeater', True):
            if group.id not in group_repeat:
                group_repeat[group.id] = {"msg_hash": hash(str(message)), "count": 1}
            elif hash(str(message)) == group_repeat[group.id]["msg_hash"]:
                group_repeat[group.id]["count"] += 1
                if group_repeat[group.id]["count"] == 3:
                    try:
                        await app.send_message(group, message)
                    except:
                        pass
            else:
                group_repeat[group.id] = {"msg_hash": hash(str(message)), "count": 1}

