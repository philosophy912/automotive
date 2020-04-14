#### V1.0.1

- base_image_compare.py

  初始化的时候调整了传入对象可以为实例化后的BaseScreenShot对象（即可以是他的实现后得子类)，也可以是模块名. 方便在没有模块的情况下引用该对象。

- image_compare.py

  根据base_image_compare的修改调整了初始化传入的对象

- utils.py

  修改了**get_folder_path**方法， 添加了current_path，方便在不同位置查找文件夹，修正了之前在模块中引用的路径错误。

#### V1.0.2

- 修复了CANBOX的发送错误
- 修复了CAN Message计算的错误
- 统一了CANDevice的接口
- 增加了CAN 随机发送消息的接口

#### V1.0.3
- 增加了新的CAN分析仪的dll文件
- 修复了ADB截屏的错误  
    针对高通820需要先执行adb remount操作，否则会导致截屏不成功
    
#### V1.0.4
- 修复了CAN工具计算值的错误, 涉及src/automotive/can/interfaces/message以及src/automotive/can/interfaces/tools文件
- 增加了单元测试


