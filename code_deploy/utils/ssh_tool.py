# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/7/29
import paramiko, os
from paramiko.channel import PipeTimeout



def ssh_command(ip:str , port:int, user:str, passwd:str, command:str, timeout=60):
    "远程执行命令"
    # 默认超时时间是60s
    # 需要自己根据需要调整
    ssh = paramiko.SSHClient()
    pkey = None
    if not passwd:
        passwd = None
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if passwd:
            pass
        else:
            #try:
            home_path = os.path.expanduser("~")
            key_path = os.path.join(home_path,".ssh","id_rsa")
            if not os.path.exists(key_path):
                raise Exception("尝试无密码登录，但当前主机不存在%s文件" % key_path)
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
        # ssh 连接 一共重试三次。 每次超时时间为2s
        try:
            _e = None
            for i in range(3):
                try:
                    ssh.connect(ip, port=int(port), username=user,
                                password=passwd, timeout=3, pkey=pkey)
                    break
                except  Exception as e:
                    #print([str(e)])
                    _e = e
                    if 'Authentication failed' in str(e):
                        break
                    #print(_e)
            if _e:
                raise  _e
        except Exception as e:
            if passwd:
                raise Exception("SSH %s:%s 连接失败。%s" % (ip, port, str(e)))
            else:
                raise Exception("SSH %s:%s 免密连接失败。%s " % (ip, port, str(e)))
        tran = ssh.get_transport()
        chan = tran.open_session()
        chan.settimeout(timeout)
        chan.get_pty()
        f = chan.makefile()
        chan.exec_command(command)
        stdout_info = f.read().decode('utf-8').strip()
        return_code = chan.recv_exit_status()
        f.close()
        ssh.close()
        assert  return_code == 0 ,Exception("ssh %s:%s 执行%s 失败，返回值是%s!(命令正常运行返回值一般是0)" %
                                            (ip,port,command, return_code))
    except (PipeTimeout,Exception) as e:
        #print(e,[e,type(e)])
        #traceback.print_exc()
        try:
            f.close()
        except:
            pass
        try:
            ssh.close()
        except:
            pass
        message = str(e) or e.__repr__()
        if message.startswith("timeout"):
            message = 'ssh %s:%s 执行%s 失败，超过最大允许时间 %ss' % (ip, port, command, timeout)
        return False, message
    else:
        return True, stdout_info


# def get_remote_code_ver(ip, port, user, passwd, app_name):
#
#     pass


if __name__ == '__main__':
    import time
    print(time.time())
    res = ssh_command('192.168.220.80', 22, 'root', 'gc895316', 'mkdir -p /data/code/tesbbb && ls -l /data/code/tesbbb', timeout=4)
    print(time.time())
    print(res[1].splitlines())
    print(res[1].split())