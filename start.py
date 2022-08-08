# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/8/13
# 通过 gunicorn 启动项目
#
import sys,os
import platform
import config
import subprocess






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
    assert int(python_version[0]) == 3 and int(python_version[1]) >= 6,Exception("python版本必须大于等于3.6")
    import psutil
    import MySQLdb
    import paramiko
    import django
    RUN_PORT = config.RUN_PORT
    _ = psutil.Process(1)
    for p in _.children(True):
        try:
            cmd_line = " ".join(p.cmdline())
            if 'uwsgi' in p.cmdline()[0]:
                # print(cmd_line)
                if str(RUN_PORT) in cmd_line and 'harakiri' in cmd_line:
                    try:
                        p.kill()
                        p.send_signal(9)
                    except:
                        pass
        except:
            pass
    # run_cmd("ps aux|grep -v  'bash' |grep gunicorn|grep %s | awk '{print $2}' | xargs kill -9" % RUN_PORT)
    os.system("mkdir -p %s" % os.path.join(config.WORK_PATH, 'log'))
    os.system("sysctl -w net.core.somaxconn=32768")
    log_file = os.path.join(config.WORK_PATH, "log","code_deploy.log")
    run_cmd("uwsgi  --protocol http  --socket 0.0.0.0:%s "
            "--listen 1024 --module django_wsgi "
            "--harakiri 10 --processes 4 --master  "
            " --max-requests 1000  --daemonize %s"  % (RUN_PORT, log_file ))
    green_print("cap启动成功  http://0.0.0.0:%s/" % RUN_PORT)
    green_print("提示：管理员初始账号为 admin  123456")
    green_print("日志：%s" % log_file)







