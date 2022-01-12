# irRemote_esp32
microPython irRemote on esp32



用法：

```python
from IRremote import IrReceiver

# 初始化管脚
receiver = IrReceiver(15) # 红外接收模块 HS0038

while True:
    if receiver.decode():
        print(receiver.decodedData)

```

