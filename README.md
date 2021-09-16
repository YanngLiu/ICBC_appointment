# ICBC_appointment


## 功能
自动刷新ICBC预约系统，找到合适的时间。


## 安装
**请预先安装python2.7 版本**


## 用法

### 笔试刷新

1.1 修改期望刷新的月份

在文件 knowledge_test.py 修改expectMonth.

1.2 Change probe frequency 

在文件 knowledge_test.py 修改 value of time.sleep(), unit is seconds

1.3 Change wanted test positions list
Change file locations.json

2. 打开命令行直接运行：

`python knowledge_test.py locations.json`

不间断刷新知道有可用的预约时间，电脑会发出声音。

### 路考刷新

Change value of examDate, lastName and licenseNumber to your own in method fetch_road_test
同上修改expectMonth后，运行:

`python road_test.py {driverLastName} {licenceNumber} {keyword}`

说明
- driverLastName, 登陆使用的Last Name
- licenceNumber, 驾照号码
- keyword 登陆密码

