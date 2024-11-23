import asyncio
from datetime import datetime
import aiohttp
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model.relationship import Member
from graia.broadcast import Broadcast
from graia.ariadne.message.element import Image
import json
from .Coin_manager import CoinManager
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("命令插件")
channel.description("用于处理用户（管理员）在 qq 中发出的指令")
channel.author("rainlodo")

bcc = create(Broadcast)
loop = asyncio.get_event_loop()
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))
coin_manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))

async def admin_controller(command: str, target_id: int):
    if command == 'remove':
        await conf_manager.remove_admin(target_id)
    elif command == 'add':
        await conf_manager.add_admin(target_id)

async def group_controller(command: str, target_id: int):
    if command == 'remove':
        await conf_manager.del_group(target_id)
    elif command == 'add':
        await conf_manager.add_group(target_id)

async def picture_size_controller(command: str):
    size_list = ['original', 'regular', 'small', 'thumb', 'mini']
    if command in size_list:
        await conf_manager.set_picture_size(command)

async def black_list_controller(command: str, target_id: int):
    if command == 'remove':
        await conf_manager.remove_from_black_list(target_id)
    elif command == 'add':
        await conf_manager.add_to_black_list(target_id)

async def group_feature_controller(command: str, target_id: int, value: int):
    "command is feature_name"
    value = True if value == 1 else False
    if command == 'all' and target_id in await conf_manager.get_groups_list():
        features = await conf_manager.get_feature_list()
        for i in features:
            await conf_manager.update_group_feature(target_id, i, value)
    else:
        await conf_manager.update_group_feature(target_id, command, value)

@bcc.receiver(GroupMessage)
async def command_receiver(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    if member.id in await conf_manager.get_admin_list() and \
        message.display[:4] == '#set':
        sentence = message.display
        sentence = sentence.replace("#set", "")
        command_list = sentence.split()
        command_head = command_list[0]
        command_size = len(command_list)

        if 'picture_size' == command_head:
            await picture_size_controller(command_list[1])

        if 'add_group' == command_head:
            if command_size == 2:
                await group_controller("add", int(command_list[1]))
            elif command_size == 1:
                await group_controller('add', group.id)
        
        if 'del_group' == command_head:
            if command_size == 2:
                await group_controller("remove", int(command_list[1]))
            elif command_size == 1:
                await group_controller('remove', group.id)
        
        if 'add_black' == command_head:
            if command_size == 2:
                await black_list_controller("add", int(command_list[1]))

        if 'del_black' == command_head:
            if command_size == 2:
                await black_list_controller("remove", int(command_list[1]))

        if 'add_admin' == command_head:
            if command_size == 2:
                await admin_controller("add", int(command_list[1]))

        if 'del_admin' == command_head:
            if command_size == 2:
                await admin_controller("remove", int(command_list[1]))

        if 'feature' == command_head:
            "#set feature feature_name value (group_id)"
            if command_size == 3:
                await group_feature_controller(command_list[1], group.id, int(command_list[2]))
            elif command_size == 4:
                await group_feature_controller(command_list[1], command_list[3], int(command_list[2]))
        
        if 'help' == command_head:
            content = '#set add_group/del_group (群号)[添加或删除群]\n'\
            + '#set add_admin/del_admin qq [添加或删除管理员]\n' \
            + '#set feature feature_name value (group_id) [开关群功能]\n'\
            + '#set picture_size [original regular small thumb mini] [修改全局图片尺寸]\n'\
            + '#set add_black/del_black qq [添加或移除黑名单]\n'
            await app.send_message(group, MessageChain(content), quote=source)

## coins ##

async def give_coins(giver_id: int, receiver_id: int, coins: int) -> int:
    "返回 int 用于判断，-1 给予者不存在， 0 给予成功， 1 硬币数异常， 2接收者不存在"
    if giver_id in await coin_manager.get_users():
        if receiver_id in await coin_manager.get_users():
            if coins > 0 and isinstance(coins, int):
                t1 = await coin_manager.get_coins(giver_id)
                if t1 > coins:
                    await coin_manager.change_coins(giver_id, -coins)
                    await coin_manager.change_coins(receiver_id, coins)
                    return 0
            else:
                return 1
        else:
            return 2
    return -1

# @bcc.receiver(GroupMessage)
# async def coin_command_receiver(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
#     "#give receiver_id coins"
#     black_list = await conf_manager.get_black_list()
#     if message.display[:5] == '#give':
#         if member.id not in black_list:
#             sentence = message.display
#             sentence = sentence.replace("#give", "")
#             command_list = sentence.split()
#             command_list[0] = command_list[0][1:]
#             print(command_list)
#             if int(command_list[0]) not in black_list:
#                 flag = await give_coins(member.id, int(command_list[0][1:]))