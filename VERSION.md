## 版本更新说明

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




    






