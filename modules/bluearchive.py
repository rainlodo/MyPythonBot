import os
import json
import aiofiles
import aiohttp
import asyncio
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, FriendMessage, Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.ariadne.model.relationship import Member
from graia.broadcast import Broadcast
from graia.ariadne.message.element import Image
from pathlib import Path
from .Config_manager import ConfigManager

channel = Channel.current()
channel.name("\nba插件")
channel.description("简单的调用api实现攻略查询")
channel.author("rainlodo\n")

bcc = create(Broadcast)
script_path = Path(__file__).parent
loop = asyncio.get_event_loop()
conf_manager = loop.run_until_complete(ConfigManager.create(r'../data/other/config.json'))

async def load_data():
    try:
        async with aiofiles.open(Path("data", "other", "ba_image_hash.json"), 'r') as file:
            data = await file.read()
            hash_data = {item['name']: item for item in json.loads(data)['data']}
            return hash_data  # Return the loaded data
    except Exception as e:
        print(f"can not load, exception is {e}")
        return {}  # Return an empty dictionary if the file is not found

async def save_data(hash_data):
    try:
        async with aiofiles.open(Path("data", "other", "ba_image_hash.json"), 'w') as file:
            await file.write(json.dumps({'data': list(hash_data.values())}))
    except Exception as e:
        print(f"Error while saving data: {e}")

async def check_hash(hash_val, name, hash_data):
    if name in hash_data:
        if hash_val != hash_data[name]['hash']:
            hash_data[name]['hash'] = hash_val
            # print(hash_val, hash_data[name]['hash'])
            await save_data(hash_data)  # Ensure data is saved after modification
            return False
        return True
    else:
        hash_data[name] = {
            'name': name,
            'hash': hash_val
        }
        # print(hash_val, hash_data[name]['hash'])
        await save_data(hash_data)  # Ensure new data is saved
        return False
    
async def query(key: str, hash_data):
    base_url = 'https://arona.cdn.diyigemt.com/image'
    url = 'https://arona.diyigemt.com/api/v1/image?name='
    url = url + key
    try:
        response_json = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()
                result_data = response_json["data"]
                if len(result_data) == 1:  # 精准查询
                    result_data = result_data[0]
                    name = result_data['name']
                    hash_val = result_data['hash']
                    flag = await check_hash(hash_val, name, hash_data)
                    img_url = base_url + result_data["path"]
                    relative_path = Path("data", "ba", result_data["path"][1:])
                    save_path = (script_path.parent / relative_path).resolve()
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Create parent directory

                    if not flag or not os.path.exists(save_path):  # Only download if hash is different or file doesn't exist
                            async with session.get(img_url) as img_response:
                                if img_response.status == 200:
                                    img_bytes = await img_response.read()
                                    with open(save_path, 'wb') as f:
                                        f.write(img_bytes)
                    return (1, save_path)
                elif len(result_data) > 1:
                    message = ''
                    for i in result_data:
                        message += str(i['name']) + '\n'
                    message = message[:-1]
                    return (2, message)
                return (False, False)
                

    except Exception as e:
        print(e)

loop = asyncio.get_event_loop()
hash_data = loop.run_until_complete(load_data())


@bcc.receiver(GroupMessage)
async def ba_query(app: Ariadne, group: Group, message: MessageChain, source: Source, member: Member):
    "一个简单的查询 ba 攻略的函数"
    if group.id in await conf_manager.get_groups_list():
        sender = member.id
        if message.display[:3] == "#攻略":
            # 获取标签
            text = message.display
            key = text.split()[1]
            # print(key)
            if key != '':
                result = await query(key, hash_data)
                if result[0]:
                    if result[0] == 1:
                        await app.send_message(group, MessageChain(Image(path=str(result[1]))), quote=source)
                    else:
                        await app.send_message(group, MessageChain("请尝试使用以下关键词重试\n" + result[1]), quote=source)
                else:
                    await app.send_message(group, MessageChain("无法查询到你需要的攻略"), quote=source)
