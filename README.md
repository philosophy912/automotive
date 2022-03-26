Automotive

> automotive库，提供了车载系统自动化测试的库

## 一、背景

车载娱乐系统中，由于汽车系统的特殊性，各ECU之间的通信并非使用互联网的HTTP协议，而是采用的CAN协议。

然而，传统的测试方法有一些痛点：

1、可以利用CANoe或者其他CAN设备进行总线通信的模拟，但是信号需要挨个查找

2、可以利用CANoe等设备进行面板的制作，但是需要学习CAPL脚本

3、可以利用安卓UI自动化控制安卓设备点击如空调面板等按钮，但是需要CANoe或其他设备来检查发送的总线是否正确。

而automotive库就是为了解决上述的问题而诞生的。

## 二 、安装

> 由于库没有上传PIP，所以需要本地打包安装

```python
git clone https://github.com/philosophy912/automotive.git
python setup.py sdist 
cd dist
pip install automotive-x.x.x.tar.gz -i https://pypi.douban.com/simple/
```

## 三、模块说明

主要模块如下

- CAN Service （CAN模块操作)

>  CAN Service提供了操作CAN盒的能力， 目前支持**PCAN**、**USBCAN**、**CANALYST**、**TSMASTER**、**ZLGUSBCAN**五种设备。CAN Service自带DBC解析的能力，能够根据DBC定义的发送消息（如周期信号、事件信号、周期事件信号)。 支持CAN消息接收及收到的消息的分析。

- Android Service (Android UI自动化)

>  常用的安卓UI自动化测试框架有**Appium**和**uiautomator2**两种，两种框架各有优点，如appium相对来说比较稳定，团队维护，而uiautomator2则有速度快的优点。Android Service在两者之上构建了一个API层，用于快速适配**Appium**和**uiautomator2**。

- Battery Control (电源控制)

> 目前可编程电源仅支持ITECH IT6831和Konstanter两种。前者用于普通的电源变动测试，而后者可以用于模拟点火曲线。

- Others (Images、Camera、Serial、Relay、Player)

> Images类主要提供了图片对比，图片画框、图片剪切的能力
>
> Camera类主要提供了摄像头拍照、录像等能力
>
> Serial类主要提供了串口的输入输出、日志记录等能力
>
> Relay类主要提供了继电器的操作能力（支持USB继电器）
>
> Player类主要提供了播放TTS语音的能力

## 四、硬件设备列表

**PCAN**

![pcan](docs\images\pcan.jpg)

**USBCAN**

![usbcan](docs\images\usbcan.jpg)

**CANALYST**

![canalyst](docs\images\canalyst.jpg)

**TSMASTER**
![tsmaster](docs\images\tsmaster.png)

**ZLGUSBCAN**
![zlg](docs\images\USBCANFD.jpg)

**IT6831**
![it6831](docs\images\itech_it6831.jpg)

**Konstanter**
![konstanter](docs\images\konstanter.jpg)

**USB RELAY**
![usbrelay](docs\images\usbrelay.jpg)

## 五、使用说明

### CAN Service

```python

from automotive import CANService
dbc_file = "test.dbc"
# 初始化CAN Service
# 除messages外，其他参数都有默认参数
# 其中can_box_device支持 PEAKCAN/USBCAN/CANALYST/TSMASTER/ZLGUSBCAN 该参数可以为None，初始化的时候会根据顺序查找对应设备
# channel_index从1开始，即2路的时候最低的一路为1
# baud_rate支持500/125分别对应高速CAN和低速CAN
# can_fd 仅TSMASTER/ZLGUSBCAN支持CANFD
can_service = CANService(messages=dbc_file, can_box_device="tsmaster", baud_rate=500, channel_index=1, can_fd=True)

# 打开设备， 当设备打开的时候，会自动开启接收线程
can_service.open_can()

# can_service中包含了两个对象， messages和name_messages， 这两个对象都是字典类型，表示以ID和NAME的对应的帧。

# 发送CAN消息
# 根据帧ID发送消息（不推荐使用)
can_service.send_can_message_by_id_or_name(0x20)
# 根据帧名字发送消息（不推荐使用)
can_service.send_can_message_by_id_or_name("RSDS_FD1")
# 根据帧ID和信号名和值发送消息（推荐使用)
# 其中msg可以输入帧的ID或者名字 
# signal则表示该帧下的信号名称以及要设定的值（值为物理值)
can_service.send_can_signal_message(msg=0x16F, signal={"BSD_LCA_warningReqleft": 1, "BSD_LCA_warningReqRight": 0x0})

# 接收CAN消息（仅针对接口调用的时候收到的消息）

# 接收CAN总线上最后一帧消息
message = can_service.receive_can_message(0x16F)
# 打印该消息下的信号的物理值
BSD_LCA_warningReqleft_value = message.signals["BSD_LCA_warningReqleft"].physical_value
BSD_LCA_warningReqRight_value = message.signals["BSD_LCA_warningReqRight"].physical_value

# 接收CAN总线上某个信号的值
BSD_LCA_warningReqleft_value = can_service.receive_can_message_signal_value(message_id=0x16F, signal_name="BSD_LCA_warningReqleft")

# 总线分析
# 总线分析是针对接收到的消息进行自动分析，适用场景如： 中控屏幕点击打开空调按钮操作

# 首先需要清空收到的CAN消息然后在进行操作
can_service.clear_stack_data()
# 进行相关的操作如：中控屏幕点击打开空调按钮操作
stack = can_service.get_stack()

# 总线是否丢失
bus_lost = can_service.is_can_bus_lost()

# 检查是否收到被测对象发出来的
# expect_value表示被测对象应该发出来的值
# count表示该值出现的次数
# exact表示是否精确查找  非精确查找仅适用于长按某个按键按照周期方式连续发消息可能存在接收数量有少量差异的情况
result = can_service.check_signal_value(stack=stack, signal_name="IP_FuelLvlLowLmpSts", expect_value=0x1, count=1, exact=True)

# 检查该信号曾经出现的所有值 (该值是物理值)
values = can_service.get_receive_signal_values(stack=stack, signal_name="IP_FuelLvlLowLmpSts")

# 发送默认消息
can_service.send_default_messages(filter_sender="HU")
can_service.send_default_messages(filter_sender=["MMI","ICU"])

# 发送随机消息
# 其中default_message 表示该值不会随机变化，而是固定的。一般用于IGN ON
# cycle_time表示循环次数， 不写则为无限循环
# interval表示每轮信号值改变的间隔时间，默认是0.1秒
can_service.send_random(filter_sender="HU", cycle_time=10000, interval=0.1, default_message={0x16F: {"BSD_LCA_warningReqleft":1}})

# 关闭设备
can_service.close_can()
```

