from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.broadcast import Broadcast
import graiax.silkcoder as silkcoder
from pathlib import Path
from graia.ariadne.message.element import Voice, Image
from .tools import sub_sentence_exist
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler.timers import crontabify

channel = Channel.current()
channel.name("碧蓝航线 wiki 插件追加")
channel.description("我真的是fw")
channel.author("rainlodo")

bcc = create(Broadcast)

# 碧蓝航线

allow_groups = [601689300, 849686504, 155569660]
# allow_groups = [155569660]
@bcc.receiver(GroupMessage)
async def reward(app: Ariadne, group: Group, message: MessageChain):
    "wiki 插件的补充 追加指令表"
    if message.display == 'wiki':
        if group.id in allow_groups:
            command_list = '追加指令\n#wiki 指挥猫\n#wiki 万油收益\n'
            await app.send_message(group, MessageChain(command_list))

@channel.use(SchedulerSchema(crontabify('30 23 * * 0')))
async def al_notice_week(app: Ariadne):
    "碧蓝航线购买每周物品提醒"
    img = Image(path=Path("data", "imgs", "al_week.jpg"))
    
    for i in allow_groups:
        await app.send_group_message(i, MessageChain("指挥官记得购买每周礼包哦！\n(*˘︶˘*).。.:*♡"))
        await app.send_group_message(i, MessageChain(img))

@channel.use(SchedulerSchema(crontabify('28 21 * * *')))
async def al_notice_day(app: Ariadne):
    "碧蓝航线开发船坞提醒"
    
    img = Image(path=Path("data", "imgs", "graiax.png"))
    for i in allow_groups:
        await app.send_group_message(i, MessageChain("指挥官别忘记白嫖科研图纸哦！\n(*˘︶˘*).。.:*♡"))
        await app.send_group_message(i, MessageChain(img))

@bcc.receiver(GroupMessage)
async def reward(app: Ariadne, group: Group, message: MessageChain):
    "wiki 插件的补充 万油收益"
    if message.display == '#wiki 万油收益':
        if group.id in allow_groups:
            img = Image(path=Path("data", "imgs", "shouyi.png"))
            await app.send_message(group, MessageChain(img))

@bcc.receiver(GroupMessage)
async def commander_cat(app: Ariadne, group: Group, message: MessageChain):
    "wiki 插件的补充 指挥猫"
    if message.display == '#wiki 指挥猫':
        if group.id in allow_groups:
            img = Image(path=Path("data", "imgs", "mao.jpg"))
            await app.send_message(group, MessageChain(img))
