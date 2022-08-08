# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/8/13
# 系统初始化脚本
# 1.python版本检查。 并安装依赖
# 2.数据库检查，  表 自动导入。
# 3.成功
import sys,os
import platform
import config
import subprocess
import time





def green_print(*msg):
    for _ in msg:
        print('\033[92m%s \033[0m' % _)
    print('')


def red_print(*msg):
    for _ in msg:
        print('\033[91m%s \033[0m' % _)
    print('')


def yellow_print(*msg):
    for _ in msg:
        print('\033[93m%s \033[0m' % _)
    print('')

def run_cmd(cmd):
    print(cmd)
    _ = os.system(cmd)
    if _ != 0:
        red_print(cmd,"执行报错，返回值是",_)
        raise Exception(cmd + '执行报错！')
    else:
        green_print(cmd,'执行成功')


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    current_dir = os.path.abspath(current_dir)
    python_version = platform.python_version_tuple()
    assert int(python_version[0]) == 3 and int(python_version[1]) >= 6,\
        Exception("python版本必须大于等于3.6")
    run_cmd("cd %s && pip3 install -r %s" % (current_dir, 'requirements.txt'))  # 安装python 依赖
    time.sleep(1)
    import MySQLdb
    host = config.MYSQL_HOST
    port = int(config.MYSQL_PORT)
    db = config.MYSQL_DB
    user = config.MYSQL_USER
    passwd = config.MYSQL_PASSWORD
    try:
        conn = MySQLdb.connect(host=host, port=int(port), db=db, user=user,
                               passwd=passwd, charset='utf8')
        conn.ping()
        with conn.cursor() as cursor:
            cursor.execute("show tables")
            tables = cursor.fetchall()
    except:
        red_print("mysql连接失败")
        raise Exception("mysql %s 测试连接失败")
    if  tables:
        red_print("当前数据库%s内非空，为了安全，禁止执行初始化！" % host)
        raise Exception('当前数据库%s内非空' % host)
    run_cmd("mysql --version")
    run_cmd("mysql -h  %s -P %s -u %s -p'%s' %s< code_deploy.sql" % (host, port, user, passwd, db))
    green_print("表初始化完成。")







