import asyncio
import aiofiles
import json
import os

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path):
        # 如果已经初始化过，则不再执行初始化代码
        if hasattr(self, 'initialized') and self.initialized:
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, file_path)

        self.lock = asyncio.Lock()
        self.groups = {}
        self.admin_list = []
        self.black_list = []
        
        # 标记已经初始化
        self.initialized = True

    @classmethod
    async def create(cls, file_path):
        " init the class and return a instance"
        manager = cls(file_path)
        await manager.load_data()
        return manager
    
    async def load_data(self):
        async with self.lock:
            try:
                async with aiofiles.open(self.file_path, 'r') as file:
                    content = await file.read()
                    data = json.loads(content)
                    self.groups = data.get('users', {})
                    self.admin_list = data.get('admin', [])
                    self.black_list = data.get('black_list', [])
            except FileNotFoundError:
                print(f"Data file not found at {self.file_path}. Initializing with default data.")
                self.groups = {}
                self.admin_list = []
                self.black_list = []

    async def save_data(self):
        async with self.lock:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps({'users': self.groups,
                                             'admin': self.admin_list,
                                             'black_list': self.black_list
                                             }))

    async def get_admin_list(self):
        return self.admin_list

    async def add_admin(self, admin_name):
        async with self.lock:
            self.admin_list.append(admin_name)
        await self.save_data()

    async def remove_admin(self, admin_name):
        async with self.lock:
            if admin_name in self.admin_list:
                self.admin_list.remove(admin_name)
        await self.save_data()

    async def get_black_list(self):
        return self.black_list

    async def add_to_black_list(self, user_name):
        async with self.lock:
            self.black_list.append(user_name)
        await self.save_data()

    async def remove_from_black_list(self, user_name):
        async with self.lock:
            if user_name in self.black_list:
                self.black_list.remove(user_name)
        await self.save_data()

    async def get_group_features(self, group_name):
        return self.groups.get(group_name, {})

    async def update_group_feature(self, group_name, feature_name, value):
        async with self.lock:
            if group_name not in self.groups:
                self.groups[group_name] = {}
            self.groups[group_name][feature_name] = value
        await self.save_data()