Automotive

> automotive库，提供了车载系统自动化测试的库

# 背景

车载娱乐系统中，由于汽车系统的特殊性，各ECU之间的通信并非使用互联网的HTTP协议，而是采用的CAN协议。

然而，传统的测试方法有一些痛点：

1、可以利用CANoe或者其他CAN设备进行总线通信的模拟，但是信号需要挨个查找

2、可以利用CANoe等设备进行面板的制作，但是需要学习CAPL脚本

3、可以利用安卓UI自动化控制安卓设备点击如空调面板等按钮，但是需要CANoe或其他设备来检查发送的总线是否正确。

而automotive库就是为了解决上述的问题而诞生的。

# 安装

## 依赖安装

由于使用到了ctypes调用dll文件，所以需要安装以下内容

1. 下载Visual Studio Community

   [Visual Studio Community](https://visualstudio.microsoft.com/zh-hans/vs/community)

2.  选择安装以下组件

   - 使用C++的桌面开发
   - 使用C++的移动开发
   - 通用Windows平台开发
   - 使用C++的游戏开发
   - 使用C++进行Linux和嵌入式开发

![安装步骤1](/docs/images/vs1.jpg)
![安装步骤2](/docs/images/vs2.jpg)

## Aumotive库安装

> 由于库没有上传PIP，所以需要本地打包安装

```python
git clone https://github.com/philosophy912/automotive.git
python setup.py sdist 
cd dist
pip install automotive-x.x.x.tar.gz -i https://pypi.douban.com/simple/
```

# 模块说明

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

# 硬件设备列表

## **PCAN**

![pcan](/docs/images/pcan.jpg)

## **USBCAN**

![usbcan](/docs/images/usbcan.jpg)

## **CANALYST**

![canalyst](/docs/images/canalyst.jpg)

## **TSMASTER**

![tsmaster](/docs/images/tsmaster.png)

## **ZLGUSBCAN**

![zlg](/docs/images/USBCANFD.jpg)

## **IT6831**

![it6831](/docs/images/itech_it6831.jpg)

## **Konstanter**

![konstanter](/docs/images/konstanter.jpg)

## **USB RELAY**

![usbrelay](/docs/images/usbrelay.jpg)

# 使用说明

## 核心模块

### CAN Service

- 初始化

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
```

- 打开设备

```python
# 打开设备， 当设备打开的时候，会自动开启接收线程
can_service.open_can()
# can_service中包含了两个对象， messages和name_messages， 这两个对象都是字典类型，表示以ID和NAME的对应的帧。
```

- 发送CAN信号

```python
# 根据帧ID发送消息（不推荐使用)
can_service.send_can_message_by_id_or_name(0x20)
# 根据帧名字发送消息（不推荐使用)
can_service.send_can_message_by_id_or_name("RSDS_FD1")
# 根据帧ID和信号名和值发送消息（推荐使用)
# 其中msg可以输入帧的ID或者名字 
# signal则表示该帧下的信号名称以及要设定的值（值为物理值)
can_service.send_can_signal_message(msg=0x16F, signal={"BSD_LCA_warningReqleft": 1, "BSD_LCA_warningReqRight": 0x0})
```

- 接收CAN信号

```python
# 仅针对接口调用的时候收到的消息

# 接收CAN总线上最后一帧消息
message = can_service.receive_can_message(0x16F)
# 打印该消息下的信号的物理值
BSD_LCA_warningReqleft_value = message.signals["BSD_LCA_warningReqleft"].physical_value
BSD_LCA_warningReqRight_value = message.signals["BSD_LCA_warningReqRight"].physical_value

# 接收CAN总线上某个信号的值
BSD_LCA_warningReqleft_value = can_service.receive_can_message_signal_value(message_id=0x16F, signal_name="BSD_LCA_warningReqleft")
```

- 总线分析

```python
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
```

- 其他方法

```python
# 发送默认消息
can_service.send_default_messages(filter_sender="HU")
can_service.send_default_messages(filter_sender=["MMI","ICU"])

# 发送随机消息
# 其中default_message 表示该值不会随机变化，而是固定的。一般用于IGN ON
# cycle_time表示循环次数， 不写则为无限循环
# interval表示每轮信号值改变的间隔时间，默认是0.1秒
can_service.send_random(filter_sender="HU", cycle_time=10000, interval=0.1, default_message={0x16F: {"BSD_LCA_warningReqleft":1}})
```

- 关闭设备

```python
# 关闭设备
can_service.close_can()
```

### Android Service

- 初始化

```python
from automotive import AndroidService
# 初始化安卓service
# 目前仅支持uiautomator2和appium， 如果需要用Appium得打开AppiumDesktop
android_service = AndroidService("uiautomator2")
```

- 连接设备

```python
# 连接设备
# uiautomator方式
android_service.connect(device_id="1234567")

# appium方式
capability = {
    "platformName": "android",
    "platformVersion": "6.0.1",
    "appPackage": "com.miui.home",
    "appActivity": "com.miui.home/.launcher.Launcher"
} 
android_service.connect(device_id="1234567", capability=capability)
```

- 打开/关闭App

```python
# 打开app (不常用)
android_service.open_app(package="com.android.settings", activity="com.android.settings/.MainSettings")

# 关闭app (不常用)
android_service.close_app(package="com.android.settings")
```

- 截图操作

```python
# 截图到本地
android_service.screen_shot(r"d:\screen.jpg")
```

- 获取元素

```python
# 单一元素定位
element = android_service.get_element(locator={"resourceid": "android:id/title"})
# 多重定位
element = android_service.get_element(locator={"resourceid": "android:id/title", "classname": "android.widget.TextView"})
# 默认超时时间3秒
element = android_service.get_element(locator={"resourceid": "android:id/title"}, timeout=3)
# 根据text定位
element = android_service.get_element(locator="双卡和移动网络")
```

- 获取元素列表

```python
# 通过resourceid获取元素集合
elements = android_service.get_element(locator={"resource-id": "android:id/title"})
# 通过类名获取元素集合
elements = android_service.get_element(locator={"classname": "android.widget.TextView"})

# 不支持通过text名字方式获取
# elements = android_service.get_element(locator="蓝牙")
```

- 获取元素的子元素

```python
# 父元素的定位方式
parent_locator = {"classname": "android.widget.ListView", "resource-id": "android:id/list"}
# 子元素的定位方式
locator = {"text": "我的设备"}
# 获取父元素下面的子元素
element = android_service.get_child_element(parent=parent_locator, locator=locator)
```

- 获取元素的子元素列表

```python
# 父元素的定位方式
parent_locator = {"classname": "android.widget.ListView", "resource-id": "android:id/list"}
# 子元素的定位方式
locator = {"classname": "android.widget.LinearLayout"}
# 获取父元素下面的子元素
elements = android_service.get_child_element(parent=parent_locator, locator=locator)
# 获取父元素
parent = android_service.get_element(locator=parent_locator)
# 获取父元素下面的子元素(此处可以传入定位的方式也可以传入元素)
elements = android_service.get_child_element(parent=parent, locator=locator)
```

- 获取元素的属性

```python
locator = {"text": "我的设备"}
# 获取元素
element = android_service.get_element(locator=locator)
# 获取属性
attributes = android_service.get_element_attribute(locator=element)
# 元素属性是 CHECKABLE、CHECKED、CLICKABLE、ENABLED、FOCUSABLE、FOCUSED、SCROLLABLE、LONG_CLICKABLE、DISPLAYED、SELECTED
is_checkable = attributes[ElementAttributeEnum.CHECKABLE]
# 直接获取相关的属性
is_checkable = android_service.is_checkable(locator=locator)
is_checkable = android_service.is_checkable(locator=element)
```

- 滑动查找元素

  该方法主要用于在滑动框中查找某一个指定列的元素

```python
# 父元素的定位方式，该元素为可滑动的区域 如ListView
parent_locator = {"classname": "android.widget.ListView", "resource-id": "android:id/list"}
# 拥有相同属性的每一行内容， 如新闻中的没一个新闻标题。 该元素一定会有多个
locator = {"classname": "android.widget.LinearLayout"}
# 是否完全匹配text内容
exact_match=False
# 滑动持续的时间，单位为秒， 默认为None
duration=None
# direct，滑动方向, 默认为向上滑动，即手指往上滑动
direct = SwipeDirectorEnum.UP
# 滑动的次数， 默认为None， 即表示滑动到头
swipe_time = None
# 滑动范围(0-1),表示在滑动框内移动的位置，默认0.8，即距离底部10%位置到距离顶部10%的位置
swipe_percent=0.8
# 每次滑动之间的间隔， 默认1秒
wait_time=1
# 滑动之后等待元素出现的最长时间
timeout = 3
# 滑动查找某个控件
element = android_service.scroll_get_element(element=parent_locator, locator=locator, text="个人热点", exact_match=exact_match, duration=duration, direct=direct, swipe_time=swipe_time, swipe_percent=swipe_percent, wait_time=wait_time, timeout=timeout)

# 滑动查找并点击某个控件
android_service.scroll_get_element_and_click(element=parent_locator, locator=locator, text="个人热点", exact_match=exact_match, duration=duration, direct=direct, swipe_time=swipe_time, swipe_percent=swipe_percent, wait_time=wait_time, timeout=timeout)

# 向下滑动查找控件
element = android_service.scroll_down_get_element(element=parent_locator, locator=locator, text="个人热点", exact_match=exact_match, duration=duration, swipe_time=swipe_time, swipe_percent=swipe_percent, wait_time=wait_time, timeout=timeout)
```

- 获取元素的位置

```python
# 子元素的定位方式
locator = {"text": "我的设备"}
# 获取元素的位置
x, y, width, height = android_service.get_location(locator=locator)
```

- 当元素处于某个属性状态的时候点击元素

```python
# 子元素的定位方式
locator = {"text": "我的设备"}
```

- 单击/长按/双击

```python
# 子元素的定位方式
locator = {"text": "我的设备"}
# 单击
android_service.click(locator=locator)
# 双击(两次点击之间的间隔默认为0.1秒)
android_service.double_click(locator=locator, duration=0.1)
# 长按(长按按键3秒)
android_service.press(locator=locator, duration=3)
```

- 拖拽

```python
# 从A点拖拽到B点
x1, y1, x2, y2 = 100, 400, 200, 600
# 拖动时间
duration = 1
# 从（100， 400）拖拽到 (200, 600)， 拖拽持续时间1秒
android_service.drag(start_x=x1, start_y=y1, end_x=x2, end_y=y2, duration=duration)
# A元素拖拽到B元素的位置
android_service.drag_element_to(locator1={"text": "音乐"}, locator2={"text": "蓝牙"}, duration=duration)
# A元素拖拽到(x, y)位置
android_service.drag_to(locator1={"text": "音乐"}, x=x1, y=y2, duration=duration)
```

- 滑动操作

```python
# 从某个元素的位置滑动到另外一个元素的位置
from_element = {"text": "壁纸"}
to_element = {"text": "WLAN"}
# 滑动持续时间
duration = 1
android_service.swipe_element(from_element=from_element, to_element=to_element, duration=duration)

# 滑动操作

# 父元素的定位方式，该元素为可滑动的区域 如ListView
swipe_element = {"classname": "android.widget.ListView", "resource-id": "android:id/list"}
# 拥有相同属性的每一行内容， 如新闻中的没一个新闻标题。 该元素一定会有多个
# 本参数方便是否滑动到底的判断
locator = {"classname": "android.widget.LinearLayout"}
# 滑动持续的时间，单位为秒， 默认为None
duration=None
# direct，滑动方向, 默认为向上滑动，即手指往上滑动
direct = SwipeDirectorEnum.UP
# 滑动的次数， 默认为None， 即表示滑动到头
swipe_time = None
# 滑动范围(0-1),表示在滑动框内移动的位置，默认0.8，即距离底部10%位置到距离顶部10%的位置
swipe_percent=0.8
# 每次滑动之间的间隔， 默认1秒
wait_time=1
# 滑动之后等待元素出现的最长时间
timeout = 3
android_service.swipe(swipe_element=swipe_element, locator=locator, duration=duration, direct=direct, swipe_time=swipe_time, wait_time=wait_time, timeout=timeout, swipe_percent=swipe_percent)

# 简化版操作
android_service.swipe_right(swipe_element=swipe_element, locator=locator, duration=duration, swipe_time=swipe_time, wait_time=wait_time, timeout=timeout, swipe_percent=swipe_percent)

# 仅滑动，不做任何查询操作
android_service.swipe_in_element(element=swipe_element, swipe_time=100, duration=2, percent=swipe_percent, director=director)

# 简化版操作
android_service.swipe_down_in_element(element=swipe_element, swipe_time=100, duration=2, percent=swipe_percent)
```

- 输入框

```python
# 获取元素的文本
text_value = android_service.get_text(locator={"resourceid": "android:id/title"})
# 对话框输入文本
android_service.input_text(locator={"resourceid": "android:id/title"}, text="测试文字")
# 清空输入框文本
android_service.clear_text(locator={"resourceid": "android:id/title"})
```

- 判断元素是否存在

```python
# 元素是否存在
is_element_exist = android_service.exist(locator={"resourceid": "android:id/title"})
```

- 获取节点内容

```python
xml_content = android_service.get_xml_struct()
```

- 断开连接

```python
# 断开连接
android_service.disconnect()
```

### Utils

#### Images

- 初始化

```python
from automotive import Images
images = Images()
```

- 常用方法

```python
# 图片对比
file1 = "image1.jpg"
file2 = "image2.jpg"
# compare_type 图片对比类型，支持hamming/pixel/vague三种方式对比
# hamming表示汉明距对比， 适用于摄像头拍照的模糊对比 (拍照对比推荐此方法)
# pixel像素对比，适用于截图对比，每个像素进行对比
# vague利用的是airtest提供的图像对比算法进行快速对比 (截图对比推荐此方法)

# 汉明距对比 threshold表示相似度，越靠近0表示图片越相似，默认值为10
result = images.compare(compare_type="hamming", image1=file1, image2=file2, threshold=10)

# 像素对比
# 图片对比位置
position = 0, 0, 1920, 1080   # 起点x， 起点y， 终点x， 终点y
# 是否转置位置参数从(起点x， 起点y， 宽，高)变成(起点x， 起点y， 终点x， 终点y)
is_convert = False
gray = False # 表示彩色图片对比，若灰度对比，不建议用本方法，会涉及到灰度二值化处理，在本方法中使用的是默认值240
result = images.compare(compare_type="hamming", image1=file1, image2=file2, position1=position, position2=position, gray=gray, is_convert=False)

# 模糊对比
# 当对比的区域相同的时候，position2可以为None，表示position2==position1
result = images.compare(compare_type="vague", image1=file1, image2=file2, position1=position, position2=position, gray=gray, is_convert=is_convert)

# 设置某区域为某个颜色， 该方法用于屏蔽某个区域，对比其他区域, 返回的是一个numpy数组
numpy_array = images.set_area_to_white(image=file1, position=position, rgb=(0, 0, 0), gray=gray)

# png图片转成JPG图片 (不推荐使用)
images.convert_png_to_jpg(origin=file1, target=file2)

# 坐标转换方法 把高宽方式转换成起始点方式
start_x, start_y, end_x, end_y = images.convert_position(start_x=0, start_y=0, width=1920, height=1080)

# 截取某个区域，  返回的是一个numpy数组
images.cut_image_array(image=file1, position=position, is_convert=is_convert)
# 截取某个区域并保存到文件
images.cut_image(image=file1, target_image=file2, position=position, is_convert=is_convert)

# 汉明距对比 （不推荐使用，推荐使用compare方法）
result = images.compare_by_hamming_distance(img1=file1, img2=file2, threshold=10)

# 像素对比 （不推荐使用，推荐使用compare方法）
threshold = 240   二值化的阈值， 范围[0, 255]
result = images.compare_by_matrix(img1=file1, img2=file2, gray=True, threshold=threshold)

# 像素对比  对比区域之外的部分
same_percent,  different_percent= images.compare_by_matrix_exclude(image1=file1, image1=file2, position=position, gray=gray, threshold=threshold, rgb=(0, 0, 0), is_convert=is_convert)
# 像素对比， 对比相同部分
same_percent,  different_percent= images.compare_by_matrix_in_same_area(image1=file1, image1=file2, position1=position, position2=position, gray=gray, threshold=threshold, is_convert=is_convert)


# 对图片画框
# position 表示一个或者多个区域 color表示框的颜色， 返回的是一个numpy数组
numpy_array = images.rectangle_image_matrix(image=file1, position=[position1, position2], color=(0, 0, 0), is_convert=is_convert)
# 画框并存到文件中
# 若存在target_image则表示写到另外一个文件中，否则写入本文件中
images.rectangle_image(image=file1,  position=[position1, position2], color=(0, 0, 0), is_convert=is_convert, target_image=file2)


# 模糊对比(airtest) 不推荐使用
# 此处的threshold表示相似度
result = images.find_best_result(small_image=file1, big_image=file2, threshold=0.7, rgb=True)

```

#### Utils

- 常用方法

```python
from automotive import Utils
from datetime import datetime

# 获取时间戳 默认时间戳格式是2018-07-27_14-18-59
current_time = Utils.get_time_as_string()
# 自定义时间格式  (该方法是类静态方法，可以直接类调用，不用实例化)
current_time = Utils.get_time_as_string(fmt='%Y%m%d%H%M%S')
# 获取当前第几周
current_week = Utils().get_week(date_time="2018-07-27", fmt="%Y-%m-%d")
# 转换时间为字符串
date_time = datetime.now()
current_date_time = Utils.convert_datetime_string(date_time=date_time, fmt="Y%m%d_%H%M%S")
# 转换字符串为时间
current_date_time = Utils.convert_string_datetime(date_time="2018-07-27", fmt="%Y-%m-%d")

# 随机数获取
# 随机小数
random_value = Utils.random_decimal(0, 10)
# 随机整数
random_value = Utils.random_int(0, 10)

# 获取中文的拼音
pinyin_value = Utils.get_pin_yin(text="中文")

# 带分段休息的sleep  text仅仅影响logger打印内容
Utils.sleep(sleep_time=70, text=None)

# 随机休息  
Utils().random_sleep(start:40, end:90) # 在40秒到90秒之间选择随机数进行休眠

# 压缩文件到文件夹
Utils.zip(zip_folder=r"d:\test", zip_file_name=r"d:\a.zip")

# 获取json数据
contents = Utils.get_json_obj(file="test.json")

# 获取yml数据
contents = Utils.read_yml_full(file="test.yml")  # 推荐
contents = Utils.read_yml_safe(file="test.yml")
contents = Utils.read_yml_un_safe(file="test.yml")

# 过滤文件 
files = Utils.filter_images(folder=r"c:\test", image_name="test_")  # 把test_开头的文件都找出来，仅针对当前文件夹根下的文件

# 执行命令
# 执行命令并回显结果
contents = Utils.exec_command_with_output(command="dir"， workspace=r"c:\windows")
# 相似方法还有 exec_command_must_success/exec_commands_must_success/exec_commands/exec_command

# 删除文件/文件夹
Utils().delete_file(file_name=file1)
Utils().delete_folder(folder_name=r"d:\test1")


# 文件/文件夹是否存在
file_exist = Utils.check_file_exist(file=file1)
folder_exist = Utils.check_folder_exist(folder=r"d:\test1")

```

#### Player

```python
from automotive import Player

player = Player()
# 播放TTS
player.text_to_tts(text="小爱同学")
player.text_to_voice(text="天猫精灵")
# 播放歌曲
file = "test.mp3"
player.play_audio(filename=file)
```

#### Camera

- 摄像头

```python
from automotive import Camera
# 初始化
camera = Camera()
# 打开摄像头 (仅支持打开一个摄像头，不支持打开多个摄像头)
# 默认camera的序号是0，对于笔记本来说如果用内置摄像头就是0， 如果用外置摄像头就是1
camera_id = 0
camera.open_camera(camera_id=camera_id)

# 直接GUI方式呈现摄像头， 默认2分钟
wait = 2
camera.camera_test(camera_id=camera_id, wait=wait)

# 拍照
file = "test.jpg"
# gray = True表示拍摄黑白照片
camera.take_picture(path=file, gray=False)
#################特别注意，摄像头拍摄第一张图片的时候会有偏色，建议拍三张相同图片#################

# 录像 录像采用多线程方式，不会阻塞主线程 录像仅支持AVI格式
# 总录制时间，单位为秒，但实际录制时间可能与期望录制时间有差别，为None表示一直录制，直到调用stop_record方法才会停止录像
total_time=None
camera.record_video(name="test.avi", total_time=total_time)
# 停止录像
camera.stop_record()
# 录像过程中截图
camera.get_picture_from_record(path=file, gray=False)

# 关闭摄像头
camera.close_camera()
```

- 麦克风

```python
from automotive import MicroPhone
micro_phone = MicroPhone()
# 录音只支持wav格式  采用多线程方式录音
record_time=30 # 录音持续时间30秒
micro_phone.record_audio(filename=r"d:\test.wav", record_time=record_time)
```

#### Excel Utils

- 常用方法

```python
from automotive import ExcelUtils
file = "template.xlsx"
# 初始化  支持openpyxl和xlwings
excel_utils = ExcelUtils("openpyxl")
# 创建workbook
workbook = excel_utils.create_workbook()
# 创建sheet
sheet = excel_utils.create_sheet(workbook=workbook, sheet_name="sheet1")
# 打开excel文件
workbook = excel_utils.open_workbook(file=file)
# 获取所有sheets
sheets = excel_utils.get_sheets(workbook=workbook)
# 获取指定的sheet
sheet = excel_utils.get_sheet(workbook=workbook, sheet_name="sheet1")
# 复制sheet， 返回target_shee(sheet对象)
sheet = excel_utils.copy_sheet(workbook=workbook, origin_sheet="sheet1", target_sheet="sheet2")
# 删除sheet
excel_utils.delete_sheet(workbook=workbook)

# 读取sheet中所有内容
start_row = 1 # 开始读取的行数， 目前不支持合并单元格的读取，可能会存在一些问题
contents = excel_utils.get_sheet_contents(sheet=sheet, start_row=1)

# 写入内容到sheet中
contents = [["A","B","C"],[1, 2, 3]]
border = True # 是否需要加边框
excel_utils.set_sheet_contents(sheet=sheet, contents=contents, start_row=start_row, border=border)

# 获取总共的行数
rows = excel_utils.get_max_rows(sheet=sheet)

# 获取总共的列数（非标准表格可能不准)
columns = excel_utils.get_max_columns(sheet=sheet)

# 读取单元格内容
row_index = 1 # 第几行内容， 从1开始
column_index = "A" # 从第几列开始读取，可以输入A或者数字1
cell_value = excel_utils.get_cell_value(sheet=sheet, row_index=row_index, column_index=column_index)

# 写入内容到单元格
cell_value = "2"
excel_utils.set_cell_value(sheet=sheet, row_index=row_index, column_index=column_index, value=cell_value, border=border)

# 保存workbook到文件
excel_utils.save_workbook(file=file, workbook=workbook)

# 关闭workbook
excel_utils.close_workbook(workbook=workbook)
```

## 应用模块

### logger

logger模块是集成了loguru模块，并在此基础上进行了二次封装产生的， 使用方法如下：

1. 在运行脚本目录下建立config.yml文件，建立如下内容

   ```yaml
   # level关键字表示log等级，默认等级为info
   level: info
   # log_folder关键字表示log存放文件的路径
   log_folder: d:\test
   ```

   

2. 对于logger来说，脚本在运行的时候依次从脚本所在文件夹向查找***config.yml***文件直到磁盘的根目录为止

   1.  查询不到**config.yml**文件   log会默认为**info**且只在控制台输出，并且不会记录日志到文件中
   2.  查询到**config.yml**文件
      1. 当**level**配置的不是 **trace**/**debug**/**info**/**warning**/**error** 的时候， 则log等级为**info**
      2. 当没有配置**log_folder**的时候，或者**log_folder**配置的是**None**的时候， 此时不记录日志到文件中
      3. 当配置的**log_folder**路径不正确
         1. 路径不存在的时候，会在当前路径下建立**logs**文件夹，把日志写到该文件夹中
         2. 路径存在但是文件的时候，会截取文件所在的文件夹，把日志写到该文件夹中
      4. 当配置的**log_folder**的路径正确， 则会把日志写到该文件夹中
      5. 每个文件最大的数量是**20M**。

3.  logger使用方法

   ```python
   from automotive import logger
   logger.info("info message")
   logger.error("info message")
   logger.warning("info message")
   logger.debug("info message")
   logger.trace("info message")
   ```

### Actions

Actions主要是在基础代码上统一了大部分接口，方便开发者直接调用。

#### CameraActions (不推荐使用该接口，推荐使用Camera类)

```python
from automotive import CameraActions

template_folder = r"d:\test"  # 拍照存放的路径，可不传。不传则会在当前路径下面创建以时间戳命名的文件夹
actions = CameraActions()

# 特别提示， 没一个actions下面都会有一个属性，可以通过该属性调用实际的接口， 如CameraActions就是camera
# actions.camera

# 打开摄像头 
actions.open() # 仅支持打开默认摄像头
# 打开其他摄像头， 参考Camera类的用法
actions.camera.open_camera(camer_id=1)

# 拍照 该方法拍照图片存在template_folder中
actions.take_picture("test")

# 拍摄基准照片
actions.take_template_image("template")

# 关闭摄像头
actions.close()
```

#### CanActions  (不推荐使用该接口，推荐使用CANService类)

```python
from automotive import CanActions

messages = "test.dbc"
# 相关参数参考CANService
actions = CanActions(messages = messages, can_fd=False,  can_box_device=None)
# 打开CAN盒
actions.open()

node_name = []
# 发送默认消息
actions.send_default_messages(node_name=node_name)
# 发送随机信号
actions.send_random_messages(cycle_time=1000)

# 发送消息
actions.send_message(msg=0x152, signal={"BSD_LCA_warningReqleft": 1, "BSD_LCA_warningReqRight": 0x0})

# 接收消息
signal_value = actions.receive_message(msg=0x152, signal_name="BSD_LCA_warningReqleft")

# 接收消息列表
stack = actions.get_messages()

# 检查收到的消息
result = actions.check_message(stack=stack, message_id=0x152, signal_name="BSD_LCA_warningReqleft", expect_value=0x1, count=1, exact=True)

# 清除接收消息列表
actions.clear_messages()

# 关闭CAN盒
actions.close()
```



#### IT6831Actions (推荐使用)

```python
from automotive import It6831Actions, Curve
# IT6831 端口号及波特率，默认波特率9600
port = "com9" 
baud_rate = 9600
actions = It6831Actions()

# 打开电源, 设置的默认电压为12V， 注意，此时电源不一定处于ON状态
actions.open()

# 电源通电
actions.on()

# 设置电源电压
actions.set_voltage(voltage=12)
# 设置电源最大电流值
actions.set_current(current=10)

# 同时设置电源电压和电流, 默认电流值是10A
actions.set_voltage_current(voltage=12, current=10)

# 调节电压
start = 9 # 起始电压
end= 16 # 结束电压
step = 0.1 # 每次调节的电压值
interval = 0.5 # 电压调节后保持的时间
current = 10 # 电流最大值
actions.change_voltage(start=start, end=end, step=step, interval=interval, current=current)

# 获取当前的电流电压值
voltage, current = actions.get_current_voltage()

# 电源断电
actions.off()

# 关闭电源,
actions.close()
```

#### KonstanterActions (推荐使用)

```python
from automotive import KonstanterActions
# IT6831 端口号及波特率，默认波特率19200
port = "com9" 
baud_rate = 19200
actions = KonstanterActions()

# 打开电源, 注意，此时电源不一定处于ON状态
actions.open()

# 电源通电
actions.on()

# 设置电源电压
actions.set_voltage(voltage=12)
# 设置电源最大电流值
actions.set_current(current=10)

# 同时设置电源电压和电流, 默认电流值是10A
actions.set_voltage_current(voltage=12, current=10)

# 调节电压
start = 9 # 起始电压
end= 16 # 结束电压
step = 0.1 # 每次调节的电压值
interval = 0.5 # 电压调节后保持的时间
current = 10 # 电流最大值
actions.change_voltage(start=start, end=end, step=step, interval=interval, current=current)

# 获取当前的电流电压值
voltage, current = actions.get_current_voltage()

# 模拟电压变化
curve = Curve()
# 从示波器抓取的波形csv图自动读取成点火曲线值
csv_file = "curve_20220331.csv"
# 使用的列序号
use_cols = [0, 1]
# 即电压降幅超过0.5表示开始点火了
threshold = 0.5 
curve_list = curve.get_voltage_by_csv(csv_file=csv_file, use_cols=use_cols, threshold=threshold)
interval=0.01 # 表示10毫秒 (目前Konstanter支持最短电压变化时间10毫秒)
actions.adjust_voltage_by_curve(curve=curve_list， current=current, interval=interval)

# 电源断电
actions.off()

# 关闭电源,
actions.close()
```

#### RelayActions (推荐使用)

```python
from automotive import RelayActions

actions = RelayActions()
# 打开继电器
actions.open()

# 继电器接通
channel = 1 # 表示继电器的第一个通道， 通道数从1开始， 如果该值为None表示闭合所有的通道
interval = 1 # 表示闭合操作后等待的时间
reverse = False # 由于继电器有常开和常闭两种情况，如果此时接的是常闭，则闭合操作会变成接通操作。
actions.channel_on(channel=channel, interval=interval, reverse=reverse)

# 继电器断开
actions.channel_off(channel=channel, interval=interval, reverse=reverse)

# 快速开通闭合继电器
duration = 5 # 整个快速操作期间持续时间
interval = 1 # 表示操作后等待的时间
channel = 1 # 表示继电器的第一个通道， 通道数从1开始，
stop_status = True # 表示最终停留的状态
actions.fast_on_off(duration=duration, interval=interval, channel=channel, stop_status=stop_status)

# 继电器开启所有通道
actions.on(reverse=reverse)
# 继电器关闭所有通道
actions.off(reverse=reverse)

# 关闭继电器
actions.close()
```

#### SerialActions

```python
from automotive import SerialActions
port = "com9"  # 端口号
baud_rate = 115200 # 波特率
actions = SerialActions(port=port, baud_rate=baud_rate)
# 连接串口
actions.open()

# 串口写入数据
command = "ls -l"
actions.write(command=content)

# 读取串口数据
contents = actions.read() # 读取成字符串
contents = actions.read_lines() #读取数据并分成多行

# 清空串口缓存数据
actions.clear_buffer()

# 判断文件是否存在 (适用于连接到了嵌入式操作系统中)
check_times = 3 # 重复检查次数
interval= 1 # 两次检查之间的间隔时间
timeout = 10 # 10秒超时退出
file_exist = actions.file_exist(file="/bin/bash/test.sh", check_times=check_times, interval=interval, timeout=timeout)

# 串口登陆系统 ()
double_check = False # 登陆成功后是否二次校验
login_locator = "login" # 登陆提示符
actions.login(username="root", password="root", double_check=double_check, double_check=double_check, login_locator=login_locator)

# 拷贝文件
remote_folder = "/home/user/test"
target_folder = "/home/user/target"
system_type = SystemTypeEnum.LINUX # LINUX系统
timeout = 300 # 最长拷贝时间
actions.copy_file(remote_folder=remote_folder, target_folder=target_folder, system_type=system_type, timeout=timeout)

# 检查串口中是否存在某些特殊字符
contents = "Startup ...." # 此处一般是系统启动打印的字符
result = actions.check_text(contents=contents)

# 断开串口
actions.close()
```

### Panel

使用介绍

[面板生成器使用文档](/docs/面板生成器使用文档.pdf)

示例代码

```python
from automotive import Gui
# 必填项目
excel_file = "template.xlsx"
dbc_file = "test.dbc"
# 非必填项
can_box_device = "tsmaster" # 参考CAN Service  
baud_rate = 500 # 低速CAN 125 高速CAN 500
data_rate = 2000 # 仲裁率2000 CANFD时候有效
channel_index = 1 # 第一个CAN通道
filter_nodes = [] # 需要过滤的节点，涉及默认发送的节点
can_fd = True  # 是否CANFD， 支持的设备参考CAN Service  
max_workers = 500  # 最大的线程数

Gui(excel_file=excel_file, dbc=dbc_file, can_box_device=can_box_device,
        baud_rate=baud_rate, data_rate=data_rate, channel_index=channel_index,
        filter_nodes=filter_nodes, can_fd=can_fd, max_workers=max_workers)   
```

### testcase

使用介绍

[测试用例（Xmind）编写规范](/docs/测试用例（Xmind）编写规范.pdf)



# 实际应用示例

## 汽车空调屏

```python
```



## 上下电测试

```python
```

