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
        self.black_list = [] # 黑名单(QQ)
        self.groups_list = []
        self.picture_size = ''
        self.features = []
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
                    self.groups = data.get('groups', {})
                    self.groups_list = list(map(int, list(self.groups.keys()))) 
                    self.admin_list = data.get('admin', [])
                    self.black_list = data.get('black_list', [])
                    self.features = data.get('features', [])
                    self.picture_size = data.get('picture_size', "small")
            except FileNotFoundError:
                print(f"Data file not found at {self.file_path}. Initializing with default data.")
                self.groups = {}
                self.groups_list = []
                self.admin_list = []
                self.black_list = []
                self.features = []
                self.picture_size = "small"

    async def save_data(self):
        async with self.lock:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps({'groups': self.groups,
                                             'admin': self.admin_list,
                                             'black_list': self.black_list,
                                             'features': self.features,
                                             'picture_size': self.picture_size
                                             }, indent=4)) # indent=4 使文件更加易于阅读和理解
                
    async def get_picture_size(self):
        return self.picture_size         

    async def set_picture_size(self, picture_size: str):
        self.picture_size = picture_size
           
    async def get_groups_list(self):
        return self.groups_list
    
    async def add_group(self, group_id: int):
        if group_id not in self.groups_list:
            self.groups_list.append(group_id)
            for item in self.features:
                await self.update_group_feature(group_id, item, True)

    async def del_group(self, group_id: int):
        async with self.lock:
            if group_id in self.groups_list:
                self.groups_list.remove(group_id)
                self.groups.pop(str(group_id)) # 在 groups 中以 str(group_id) 为 key
                await self.save_data()

    async def get_admin_list(self):
        return self.admin_list

    async def add_admin(self, admin_id: int):
        async with self.lock:
            if admin_id not in self.admin_list:
                self.admin_list.append(admin_id)
        await self.save_data()

    async def remove_admin(self, admin_id: int):
        async with self.lock:
            if admin_id in self.admin_list:
                self.admin_list.remove(admin_id)
        await self.save_data()

    async def get_black_list(self):
        return self.black_list

    async def add_to_black_list(self, user_id):
        async with self.lock:
            if user_id not in self.black_list:
                self.black_list.append(user_id)
        await self.save_data()

    async def remove_from_black_list(self, user_id):
        async with self.lock:
            if user_id in self.black_list:
                self.black_list.remove(user_id)
        await self.save_data()

    async def get_group_features(self, group_id: int):
        return self.groups.get(str(group_id), {})

    async def update_group_feature(self, group_id: int, feature_name: str, value: bool):
        async with self.lock:
            if group_id not in self.groups:
                self.groups[group_id] = {}
            if feature_name not in self.features:
                self.features.append(feature_name)
            self.groups[group_id][feature_name] = value
        await self.save_data()