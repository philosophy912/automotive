## 版本更新说明
**V5.4.0**
- 更新了同星的dll文件

- adb增加了只执行命令不用返回值的参数

- logger增加了写入文件等级，用于区分控制台和运行环境的区别

- 增加了dbc parser和serial port以及utils中编码错误忽略问题

- 修复了gui框架多线程输出的问题

**V5.3.9**

- 更新了类型提示从List或者Tuple更新到了Sequence

- 修改了adb模块中的执行部分，统一调用Utils下面的代码


**V5.3.8**

- xmind8_writer_sample中， __create_test_case_node新增参数result_flag，默认False，excel转xmind时，默认不加测试结果

- standard_excel_reader_sample中，——parse_test_case中修改测试结果所在列，因为之>前多加了一列修改记录，所以测试结果目前在N列

- 增加了xmind转换成仪表测试用例生成器的代码

- 修复了konstanter中参数类型提示错误

- 修复了excelutils中根据列名获取单元格的问题

- 增加了dbc转换成excel的文档（完成主要部分，缺节点部分)

- 去掉了图片对比中的多重对比，改用单一方式即airtest对比错误

- 修复了图片对比中的位置错误

- 面板功能中添加读取Excel文件时，自动检测msg_id ，不用手动填写（兼容之前的写法）

- 修改读取excel模板文件的方法：通过增加参数temple file的地址，默认为None，调用时自己查找文件。传了参数后，就按照传入的地址找文件。

- 修改excel-utils中获取最大行的方法，解决删掉的行也会算入最大行计算中

- 修改adb，拆分adb时，解决命令中“***adb***"时，会破坏命令

- 修复有符号的signal负数的总线值计算错误

**V5.3.7**

- can service中增加了计算指定signal出现在stack中的次数

- 修复了xmind转excel的小缺陷

- 优化了message中只适用于usbcan的部分到device中

- 增加了adb中的截屏并拉取到本地的功能

- 新增了基于串口的USB继电器代码

- 增加了excel utils中以字典方式获取excel sheet的功能

- 新增了performance中统计高通平台单个app内存和cpu占用率

- 修改了面板控制
  
  - 设置默认宽度以及自动换行功能
  - 修改默认读取excel表格中的第一张表格
  - 修复检查信号值读取不成功的缺陷

- 所有的枚举对象都增加了from_value方法

- android service中涉及到枚举对象的都可以支持字符串输入

- excel utils增加了枚举对象的字符串输入

- image类修改图像对比枚举类为ImageCompareTypeEnum

- 删除了doc相关的说明，只留下了DEVELOP.md文件

**V5.3.6**

- 修复了xmind转excel是否自动化的bug

**V5.3.5**

- xmind转excel增加了ID号的检查

**V5.3.4**

- 修复了CAN面板中sleep小数的错误
- 重构了CAN面板读取Excel的方式，通过ExcelUtils来读取
- 添加了ExcelUtils类，用于Excel的读写
- SerialPort修改了pop方法直接返回值，去掉了变量接收参数
- 修复standard_excel_reader_sample.py  前置条件，以\n拆分的时候，把\r\n的也给拆了，导致转成xmind的时候，前提条件中有一条如果有两行，第二行内容会丢失
- 容错了DBCParser中解析PSA项目错误的情况（PSA项目DBC本身就是错误的)

**V5.3.3**

- CANService初始化的时候，可以通过字符串方式初始化而不需要用枚举
- 修复了DBCParser中当BA没有SG的时候的错误

**V5.3.2**

- 增加了SerialPort和CompareProperty的导出
- 开放了allure-pytest和pytest的安装
- 面板增加了信号丢失的判断
- 修复了tsmaster标准CAN的时候多线程收不到消息的问题

**V5.3.1**

- 修复了测试用例生成器不生成excel的问题
- 公共面板增加了事件按钮，调整了线程池的分布，解决了卡顿问题

**V5.3.0**

- 修复了生成器中的TC带换行的情况导致的错误
- 融合了面板生成器类调用，使得调用更简单。
- 增加了面板生成器中多Tab用于分类
- 增加了公共面板

**V5.2.0**

- 新增面板生成器

**V5.1.0**

- 在解析DBC的时候过滤了CAN ID大于0x7FF的数据
- 重构了测试用例生成器
- 增加了GUI生成器从Excel文件中读取的方法

**V5.0.0**

- 适配了同星的CAN盒
- 修改了类型提示
- 修复了android service的问题
- 完成了测试用例生成器（简版）
- 调整了代码结构

**V4.2.8** 

- 修改了testcase生成器，兼容长安标准
- 修改了message，在传入非物理值的时候做严格校验

**V4.2.7**

- 实现了之前没有实现的uiautomator2的drag方法

**V4.2.6**

- 增加了座舱QNX删除单个文件、多个文件
- camera_test中增加了摄像头选择的参数
- 修改了performance中的调用方法， 计算座舱的性能需要hogs输出

**V4.2.5**

- 修改了android service， 使得可以根据属性值判断是否点击

**V4.2.4**

- 修改了android service中
- 打包增加了*.lib的库
- 修改了Images中的获取文件的numpy值的方式

**V4.2.3**

- 修改下载文件夹时，文件夹中包含文件夹无法下载的情况，调用download_file_tree方法
- 修改cluster_hmi，一些slay的内容
- 修改了message中is_standard_can不存在的时候默认为标准can
- 修正了CANService中 __is_message_in_node关于filter的类型判断错误
- 修改了api中的BaseActions中，拆分出来了BasePowerActions方便on off（适配UsbRelay)
- 增加了camera拍照名字的后缀名
- 修改默认对比方式为感知哈希算法
- 修复了Camera的错误
- 更改了sync命令的顺序
- adb.py增加删除文件的方法
- 增加了IT6831和konstanter获取电流电压的方法get_current_voltage
- 增加了RelayAction的on off方法

**V4.2.2**

- 重构了actions的代码
- 重构了actions的api，在抽象类上面都增加了Base
- 修改了Utils的get_json_object中的log等级

**V4.2.1**

- 修复了Hyupervisor截图的路径依赖错误
- 修复了Image的汉明距对比ONE的错误
- 修复了Serial_Port如果传入bytes数据的时候命令错误

**V4.2.0**

- 修改了image的图片汉明距对比的代码，读取视频的时候不用写入文件，只需要从内存里面读取每一帧
- 修改了类型提示，符合python规则
- 更新了relay_actions的channel_on传递参数的问题
- 优化了konstanter_actions关闭close的调用问题
- 优化了摄像头打开的分辨率，默认1920*1080
- image中图片对比（汉明距）增加了阈值部分，传入阈值后会返回对比的结果
- 解决了xmind转换器中excel的writer和reader之间数据缺失的问题
- 修改了hypervisor截图中默认地址，可以通过传递参数的方式实现
- 修改了ADB截图的时候放到本地路径可能失败的问题
- 修复了CanService中发送默认信号变成随机信号的问题

**V4.1.7**-

- 解决了xmind转换器中excel的writer和reader之间数据缺失的问题
- 修改了hypervisor截图中默认地址，可以通过传递参数的方式实现
- 修改了ADB截图的时候放到本地路径可能失败的问题

**V4.1.6**

- 更新了relay_actions的channel_on传递参数的问题
- 优化了konstanter_actions关闭close的调用问题
- 优化了摄像头打开的分辨率，默认1920*1080
- image中图片对比（汉明距）增加了阈值部分，传入阈值后会返回对比的结果

**V4.1.5**

- 修改了image的图片汉明距对比的代码，读取视频的时候不用写入文件，只需要从内存里面读取每一帧
- 修改了类型提示，符合python规则

**V4.1.1**

- 完成了xmind转换成excel的工作

**V4.0.8**

- 解决了konstanter收不到SEQ消息的时候进行一个超时判断
- 完成了xmind解析成excel的工作

**V4.0.7**

- 事件信号发送从主线程中移除到了子线程中，加快了消息发送的速度
- 优化了随机信号发送的代码

**V4.0.6**

- camera_test增加了摄像头序号的选择

**V4.0.5**

- CanService的线程增加到了300个

**V4.0.4**

- 修复了默认信号诊断信号发出来的错误
- 增加了CAN设备没有连接的错误

**V4.0.3**

- 增加了发送默认信号的容错问题，避免CAN盒消息发不出去导致的阻塞

**V4.0.2**

- 增加了Camera中的camera_test方法提示需要打开摄像头
- 更改了CanService的log等级

**V4.0.1**

- 增加了CanService过滤多个节点的方法

**V4.0.0**

- 调整了api的结构到common下面
- 增加了application包与core进行分开
- 调整了setup依赖的包，避免安装的时候时间过长，需要用到该包的时候在代码中进行pip安装（需要提前配置好pip）
- 增加了发送默认值的时候恢复初始的message

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

**V2.3**

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

**V2.2**

- CANService中增加了设备获取的接口 -> 通过调用self.can_box_device获取当前设备的类型

- 修复了adb工具的错误

- 增加了Linux的performance的测试

**V2.1**

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

**V2.0**

- 完善了周期事件信号的发送
- 优化了CAN消息的解析（***不兼容之前的版本***)
- 取消了stack的大小
- 移除了无用的device_can_bus模块

**V1.1.1**

- 修复了it6831电源操作在get_all_status的时候检测了电源是否处于打开状态的问题
- 修复了konstanter无法断开串口连接的问题
- 修复了更新opencv之后，camera无法打开的问题,修改了camera_test的窗口名
- 修复了继电器on/off反接需要调整接口的问题，增加了reverse用于翻转操作

**V1.1.0**

- 修复了CAN消息stop之后无法resume的问题
- 修改了konstanter的start函数返回值为None，并添加自动判断
- 联动修复了onoff的actions实现类

**V1.0.9**

- 修复了CAN消息关闭的时候没有结束线程的问题
- 修复了CAN解析消息的错误
- 增加了自动安装的脚本install.bat

**V1.0.8**

- 修复了串口无法disconnect的问题
- 修复了CAN消息发送default默认值不成功的问题

**V1.0.7**

- 修复了CAN消息发送和接收错误  
  当CAN消息发送的时候，如果发送的值低于1位的长度就会出错  
  当CAN消息接收消息的时候，解析会出现的错误
- 增加了CAN盒未连接的时候发送消息会报错的提示
- 根据airtest增加了image的对比方式find_best_result/find_best_result_by_position, 应用于存在背景图片的图像对比
- 增加了Battery相关的连接和断开接口，同时调整了onoff中对应的修改

**V1.0.6**

- 修复了CAN 消息解析错误的问题
- 修复了PCAN接收消息的错误
- 修改了resume_transmit接口，当不传入msgid的时候恢复所有已发送的消息
- 由于DBC解析可能存在某些问题，修改了message接口中的报文快速发送的次数/报文发送的快速周期/报文延时时间的默认值都为0
- 增加了部分message的logger
- 修复了CAN Service中当为8byte发送数据的时候产生的错误
- 移出了代码生成所需要的image_compare以及screenshot等文件，改由代码直接生成
- 增加了串口的disconnect方法

**V1.0.5**

- 修改了CAN层的log打印等级
- 增加了adb tap的方式点击屏幕坐标

**V1.0.4**

- 修复了CAN工具计算值的错误, 涉及src/automotive/can/interfaces/message以及src/automotive/can/interfaces/tools文件
- 增加了单元测试

**V1.0.3**

- 增加了新的CAN分析仪的dll文件
- 修复了ADB截屏的错误  
  针对高通820需要先执行adb remount操作，否则会导致截屏不成功

**V1.0.2**

- 修复了CANBOX的发送错误
- 修复了CAN Message计算的错误
- 统一了CANDevice的接口
- 增加了CAN 随机发送消息的接口

**V1.0.1**

- base_image_compare.py
  
  初始化的时候调整了传入对象可以为实例化后的BaseScreenShot对象（即可以是他的实现后得子类)，也可以是模块名. 方便在没有模块的情况下引用该对象。

- image_compare.py
  
  根据base_image_compare的修改调整了初始化传入的对象

- utils.py
  
  修改了**get_folder_path**方法， 添加了current_path，方便在不同位置查找文件夹，修正了之前在模块中引用的路径错误。
