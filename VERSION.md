## 版本更新说明

 **V3.0**

- 容错了诺博项目的测试截图(clusterHMI)
- 增加了python解析DBC的库
- 增加了message的CANFD的解析

**V2.9**

- 修改uiautomator2_client的warning变为debug
- 删掉了cluster_hmi中的删除图片的操作以提高执行效率
- 增加了screenshot中hypervisor的qnx部分的sync动作

**V2.8**

- 增加了CANService中的send_messages和send_default_messages方法
- 增加了telnet和ssh连接不成功跑异常的功能
- 根据PEP8的部分规范修改了代码注释

**V2.7**

- 修复了utils中filter_images过滤文件错误的问题
- 新增了serial_utils工具，简化了serialport操作，并增加了登陆操作以及检查文件是否存在，拷贝文件等等
- 增加了FTP下载文件时候的文件检查
- 新增了ssh以及telnet中检查文件是否存在以及拷贝文件的检查
- 删除了原始的电子邮件的模块更改为email_utils模块
- 增加了部分类的说明文件
- 修改了qnx_device操作从原来的SerialPort更改为SerialUtils，并修改了copy_images_to_usb操作的逻辑

**V2.6**

- 修复了message中motorola算法的错误
- 修复了图片对比image_compare中当不填写positions的时候仍然返回正确结果的缺陷
- 更新了cluster_HMI中需要slay进程的列表
- 修复了当config.yml中找不到level时候抛出异常的问题，改为当找不到的时候就设置为info级别
- 新增了email_utils工具，只完成了发送部分，未完成接收部分
- 修复了ftputil中下载软件不成功的问题，增加了等待时间
- 修复了Utils中函数filter_images的错误
- 修复了imagecompare当目标文件为空的时候返回True的错误

**V2.5**

 - 增加了FTP工具类FtpUtils
 - 增加了Telnet工具类TelnetUtils
 - 增加了诺创项目使用的clusterHmi类
 - 修复了空调屏截屏和仪表屏截屏的错误，并统一了截屏的接口
 - 修复了AndroidService调用的错误
 - 修复了Camera的中录制视频的错误
 - 增加了SerialPort中关于日志保存到文件的方法


**V2.4**

- 修复了Camera中重复录像导致不成功的问题（修改为线程池的方式实现）
- CanService中增加了检查signal的方法check_signal_value
- TracePlayback中修复了回放的错误（待验证）
- 开放了Action的操作，如CameraAction、It6831Action等方便操作

##### V2.3

- 增加默认的logger， 参考配置说明

```python
"""
使用方法：

    1、 from automotive import logger
    
    2、 在运行代码目录及父目录到根目录的任意目录放置config.yml文件，其中yml中包含level和log_folder用于定义log等级及log存放文件路径
    
    3、 如果找不到配置文件，默认使用info级别输出log，并且不保存log内容到文件
"""
```

- 调整了代码结构（若上层代码非使用全路径方式，不影响上层代码使用) 

- 新增了hypervisor和qnx两个模块，主要实现功能

  - 相应的QNX系统中的截图（Hypervisor是通过ADB htalk方式截图, qnx则通过串口截图)
  
  - 相应的QNX系统的点击操作（仅空调屏)
  
- 修复了文档错误

- 废弃了AppiumPythonClient模块（但仍然可以使用）

- 新增了AndroidService，用于统一uiautomator2(python)以及appium的接口，便于切换


##### V2.2

- CANService中增加了设备获取的接口 -> 通过调用self.can_box_device获取当前设备的类型

- 修复了adb工具的错误

- 增加了Linux的performance的测试 

##### V2.1

- 增加了电源自动化测试的模板代码

- 优化了CAN消息的CAN Bus接口，提取了重复代码

- 增加了trace发送的代码

  ```python
  from automotive import TraceService, TraceType
  file = r"d:\a.asc"
  service = TraceService()
  service.open_can()
  service.send_trace(file, TraceType.PCAN)
  service.close_can()
  ```


##### V2.0

- 完善了周期事件信号的发送
- 优化了CAN消息的解析（***不兼容之前的版本***)
- 取消了stack的大小
- 移除了无用的device_can_bus模块

##### V1.1.1

- 修复了it6831电源操作在get_all_status的时候检测了电源是否处于打开状态的问题
- 修复了konstanter无法断开串口连接的问题
- 修复了更新opencv之后，camera无法打开的问题,修改了camera_test的窗口名
- 修复了继电器on/off反接需要调整接口的问题，增加了reverse用于翻转操作

##### V1.1.0
- 修复了CAN消息stop之后无法resume的问题
- 修改了konstanter的start函数返回值为None，并添加自动判断
- 联动修复了onoff的actions实现类

##### V1.0.9

- 修复了CAN消息关闭的时候没有结束线程的问题
- 修复了CAN解析消息的错误
- 增加了自动安装的脚本install.bat

##### V1.0.8

- 修复了串口无法disconnect的问题
- 修复了CAN消息发送default默认值不成功的问题

##### V1.0.7
- 修复了CAN消息发送和接收错误  
当CAN消息发送的时候，如果发送的值低于1位的长度就会出错  
当CAN消息接收消息的时候，解析会出现的错误
- 增加了CAN盒未连接的时候发送消息会报错的提示
- 根据airtest增加了image的对比方式find_best_result/find_best_result_by_position, 应用于存在背景图片的图像对比
- 增加了Battery相关的连接和断开接口，同时调整了onoff中对应的修改


##### V1.0.6
- 修复了CAN 消息解析错误的问题
- 修复了PCAN接收消息的错误
- 修改了resume_transmit接口，当不传入msgid的时候恢复所有已发送的消息
- 由于DBC解析可能存在某些问题，修改了message接口中的报文快速发送的次数/报文发送的快速周期/报文延时时间的默认值都为0
- 增加了部分message的logger
- 修复了CAN Service中当为8byte发送数据的时候产生的错误
- 移出了代码生成所需要的image_compare以及screenshot等文件，改由代码直接生成
- 增加了串口的disconnect方法

#### V1.0.5
- 修改了CAN层的log打印等级
- 增加了adb tap的方式点击屏幕坐标

#### V1.0.4
- 修复了CAN工具计算值的错误, 涉及src/automotive/can/interfaces/message以及src/automotive/can/interfaces/tools文件
- 增加了单元测试

#### V1.0.3
- 增加了新的CAN分析仪的dll文件
- 修复了ADB截屏的错误  
    针对高通820需要先执行adb remount操作，否则会导致截屏不成功

#### V1.0.2

- 修复了CANBOX的发送错误
- 修复了CAN Message计算的错误
- 统一了CANDevice的接口
- 增加了CAN 随机发送消息的接口

#### V1.0.1

- base_image_compare.py

  初始化的时候调整了传入对象可以为实例化后的BaseScreenShot对象（即可以是他的实现后得子类)，也可以是模块名. 方便在没有模块的情况下引用该对象。

- image_compare.py

  根据base_image_compare的修改调整了初始化传入的对象

- utils.py

  修改了**get_folder_path**方法， 添加了current_path，方便在不同位置查找文件夹，修正了之前在模块中引用的路径错误。




​    






