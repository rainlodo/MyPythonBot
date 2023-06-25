import pkgutil
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya



app = Ariadne(
    config(
        3040461314,  # 账号
        "INITKEYnVrcgUZK",  # 验证钥
        HttpClientConfig("http://localhost:8080"),  # HTTP 配置
        #WebsocketClientConfig("http://localhost:13254"),  # WebSocket 配置
    )
)

saya = create(Saya)

with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        saya.require(f"modules.{module_info.name}")


for module, channel in saya.channels.items():
    print(
        f"module: {module}\n"
        f"name:{channel.meta['name']}\n"
        f"author:{' '.join(channel.meta['author'])}\n"
        f"description:{channel.meta['description']}"
    )

    
app.launch_blocking()