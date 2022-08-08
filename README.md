# cap代码发布系统

## 常规安装（以centos7为例）
1. 基本环境准备
```bash
yum install git gcc mysql-devel  python3 python3-devel  python3-pip net-tools mysql
pip3 install pip --upgrade 
```
2. 拉取代码
```bash
git clone ssh://git@192.168.240.131:722/zhoukunpeng/cap.git
```
3. 修改配置文件
```bash
vim config.py
# 运行目录
WORK_PATH = '/data/cap'
# 运行端口
RUN_PORT = 8081

# MYSQL相关配置
MYSQL_HOST = '192.168.240.240'
MYSQL_PORT = 3306
MYSQL_DB = 'cap_test'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
```
4. 初始化数据库
```bash
python3 init.py
```
5.  运行
```bash
python3 start.py
```

## Docker 安装
1. 下载镜像并导入
```bash
链接:https://pan.baidu.com/s/1IZFNei3IrC86-LWiIqWVKA  密码:xunn
```
2. 运行镜像到/bin/bash环境（以host模式运行）
```bash
docker run -it --network=host  cap:v1 /bin/bash
```


3. 修改配置 && 初始化 &&运行 
```bash
#修改配置
vim ~/cap/config.py
#初始化数据库：
cd cap   
python3 init.py
#运行
python3 start.py
```