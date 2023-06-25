import yaml
import threading
from typing import Union
from pathlib import Path
from datetime import datetime, time, timedelta


def read_yaml_return_value(path:Union[str, Path], key:Union[str, list]):
    " 返回指定的 yml 文件中指定键 key 的値 "
    result = []
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
        if key in data:
            temp = data[key]
            result.append(temp)
    result = tuple(result) # 以元组的形式返回 result
    return result 

def sub_sentence_exist(sentence:str, sub_key:list):
    " 查看 sub_key 中的词是否存在于 sentence 中 "
    for item in sub_key:
        if item in sentence:
            return True
        
    return False

class refresh_item_everyday:
    " 一个能够在每天刷新 data 的 class, 默认 0 点刷新 "
    def __init__(self, data: Union[int, list], refresh_time = (0,0)) -> None:
        " 初始化 "
        self.data = data
        self.initial_data = data # 保存初始值
        self.refresh_time = time(refresh_time[0], refresh_time[1])
        self.start_refresh_timer()

    def start_refresh_timer(self):
        " 定时器 "
        current_time = datetime.now().time() # 获取当前时间, 不包含日期
        time_until_refresh = self.calculate_time_until_refresh(current_time) # 计算下次刷新时间
        refresh_timer = threading.Timer(time_until_refresh.total_seconds(), self.refresh_data) # 创建新线程等待下次刷新时间归零
        self.refresh_data()

    def refresh_data(self):
        " 刷新数据 "
        self.data = self.initial_data # 刷新数据
        self.start_refresh_timer() # 重新同步定时器
    
    def calculate_time_until_refresh(self, current_time:time):
        " 计算下次刷新时间 "
        next_refresh = datetime.combine(datetime.now().date(), self.refresh_time)
        if current_time > self.refresh_time: # 当前时间大于指定的刷新时间，则刷新时间加一天
            next_refresh += timedelta(days=1) 
        time_until_refresh = next_refresh - datetime.now()
        return time_until_refresh
    

