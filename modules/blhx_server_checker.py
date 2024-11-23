import asyncio
from datetime import datetime
import io
import time
import aiohttp
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model.relationship import Member
from graia.broadcast import Broadcast
import json
from .Coin_manager import CoinManager
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("blhx_server_checker")
channel.description("碧蓝航线服务器状态检查")
channel.author("rainlodo")

bcc = create(Broadcast)

# 初始化 CoinManager
loop = asyncio.get_event_loop()
coin_manager = loop.run_until_complete(CoinManager.create(r'../data/other/qq_coin.json', coin_range=(10, 100)))
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))

# 全局变量，储存上一次查询数据的时间戳
last_query_time = 0

async def check_server_status():
    global last_query_time
    api = "http://sc.shiratama.cn/server/get_all_state"
    # 检查查询间隔是否大于 15s ，大于则通过 post 方法直接获取 json 数据，小于则返回 -1
    current_time = time.time()
    if (current_time - last_query_time) > 15:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api) as resp:
                    data = await resp.json()

                    # 替换数字为指定字符串
                    for key, value in data.items():
                        if value == 3:
                            data[key] = "爆满"
                        elif value == 1:
                            data[key] = "维护"
                        else:
                            data[key] = "正常"
                    # data = data[24:]

                    # 将字典的值拼接为字符串
                    result_str = ''
                    max_items_per_line = 3

                    for i, (k, v) in enumerate(data.items(), 1):
                        if i >= 25:
                            result_str += f"{k}: {v}, \t "
                            if i % max_items_per_line == 0:
                                result_str += "\n"

                    last_query_time = current_time
                    return result_str
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None  # 或者适当的错误处理
    else:
        return -1

# 接受指令并回复
@bcc.receiver(GroupMessage)
async def sign_in(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    if message.display == "#wiki 服务器状态":
        if group.id in await conf_manager.get_groups_list():
            data = await check_server_status()
            if data == -1:
                await app.send_message(group, MessageChain("查询过于频繁，请稍后再试"), quote=source)
            elif data is None:
                await app.send_message(group, MessageChain("查询失败，请稍后再试"), quote=source)
            else:
                await app.send_message(group,MessageChain(str(data)))