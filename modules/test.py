import random
from creart import create
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.broadcast import Broadcast
import graiax.silkcoder as silkcoder
from pathlib import Path
from graia.ariadne.message.element import Voice
from .tools import sub_sentence_exist
from .blhx import allow_groups


channel = Channel.current()
channel.name("弱鸡qwq")
channel.description("我真的是fw")
channel.author("rainlodo")

bcc = create(Broadcast)

@bcc.receiver(GroupMessage)
async def powerless(app: Ariadne, group: Group, message: MessageChain):
    "一个卖弱的函数"
    if group.id in allow_groups:
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

@bcc.receiver(FriendMessage)
async def send_ai_list(app: Ariadne, friend: Friend, message: MessageChain):
    "ai 指令回复"
    if friend.id == 2591212935:
        if message.display == "#ai列表":
            await app.send_friend_message(2591212935, MessageChain(" bing \n gpt-api \n bing-p \n bing-b \n slack \n sage \n claude \n nutria, 'capybara': 'Sage', 'a2': 'Claude-instant', 'beaver': 'GPT-4', 'a2_2': 'Claude+', 'chinchilla': 'ChatGPT', 'hutia': 'NeevaAI', 'nutria': 'Dragonfly', 'a2_100k': 'Claude-instant-100k'"))
