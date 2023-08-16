import asyncio
import aiofiles
import json
import random
from datetime import datetime
import os

class CoinManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CoinManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path, coin_range=(10, 50)):
        # 如果已经初始化过，则不再执行初始化代码
        if hasattr(self, 'initialized') and self.initialized:
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, file_path)

        self.coin_range = coin_range
        self.lock = asyncio.Lock()
        self.users = {}
        
        # 标记已经初始化
        self.initialized = True

    @classmethod
    async def create(cls, file_path, coin_range=(10, 50)):
        " init the class and return a instance"
        manager = cls(file_path, coin_range)
        await manager.load_data()
        return manager
    
    async def load_data(self):
        try:
            async with aiofiles.open(self.file_path, 'r') as file:
                data = await file.read()
                self.users = {str(user['qq']): user for user in json.loads(data)['users']}
        except FileNotFoundError:
            self.users = {}

    async def save_data(self):
        async with self.lock:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)  # Create parent directory
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps({'users': list(self.users.values())}, indent=4))

    async def sign_in(self, qq, current_time) -> int:
        " request QQ number and current time, if the QQ not in data, will make a record and set a initiation coins"
        qq = str(qq)
        current_time_str = current_time.strftime('%Y-%m-%d')
        get_coins = random.randint(*self.coin_range)

        async with self.lock:
            if qq in self.users:
                last_sign_in = datetime.strptime(self.users[qq]['last_sign_in'], '%Y-%m-%d')
                if current_time.date() > last_sign_in.date():
                    self.users[qq]['last_sign_in'] = current_time_str
                    self.users[qq]['coins'] += get_coins
                else:
                    return 0
            else:
                self.users[qq] = {
                    'qq': qq,
                    'coins': get_coins,
                    'last_sign_in': current_time_str
                }
        await self.save_data()
        return get_coins

    async def get_coins(self, qq) -> int:
        " request a QQ number, return the number's coins"
        qq = str(qq)
        async with self.lock:
            return self.users.get(qq, {}).get('coins', 0)

    async def set_coins(self, qq, coins):
        " request a QQ number and a count of coins, it will change the coins data of the QQ number"
        qq = str(qq)
        async with self.lock:
            if qq in self.users:
                self.users[qq]['coins'] = coins
            else:
                current_time_str = datetime.now().strftime('%Y-%m-%d')
                self.users[qq] = {
                    'qq': qq,
                    'coins': coins,
                    'last_sign_in': current_time_str
                }
        await self.save_data()
