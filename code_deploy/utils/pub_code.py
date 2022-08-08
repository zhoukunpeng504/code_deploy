# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/8/8
import time
import os,sys
_ = os.path.abspath(os.path.join(os.path.dirname(__file__),"..",'..'))
sys.path.append(_)
import config


# 代码发布
def pub_code(work_dir, git_repo_url, version_info, remote_machine_info, app_path,
             cmd_before_deploy:str, cmd_start_app:str, success_after_deploy:str,
             cmd_build_app:str,
             remain_num:int=3, code_tar_gz_path=None,
             qiniu_key= getattr(config,'QINIU_KEY',''),
             qiniu_secret=getattr(config,'QINIU_SECRET',''),
             qiniu_bucket=getattr(config,'QINIU_BUCKET',''),
             qiniu_domain=getattr(config,'QINIU_DOMAIN','')):

    # 代码发布核心逻辑
    print("开始...")
    print("进度5%")
    need_upload_qiniu = False
    upload_qiniu_path = '%s.tar.gz' % version_info
    upload_qiniu_url = f"http://{qiniu_domain}/{upload_qiniu_path}"
    import os, hashlib, time, subprocess, sys
    from qiniu import Auth, put_file, etag, put_data, BucketManager
    import multiprocessing
    sys.stdout.flush()
    from multiprocessing.dummy import Pool as ThreadPool
    import paramiko, os
    from paramiko.channel import PipeTimeout
    # import ssh_tool
    import psutil,datetime
    def md5_(x: bytes):
        return hashlib.md5(x).hexdigest()[:15]
    _ssh_dir = os.path.expanduser("~/.ssh")
    # sshpass 增加可执行权限
    # ssh_pass_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sshpass"))
    # os.system("chmod +x %s" % ssh_pass_path)
    os.system("mkdir -p " + _ssh_dir)
    # ~/.ssh/目录下的   id_rsa 及 id_rsa.pub文件检查
    if os.path.exists(os.path.join(_ssh_dir, "id_rsa"))  and os.path.exists(os.path.join(_ssh_dir, "id_rsa.pub")):
        pass
    else:
        print("~/.ssh/id_rsa 及 ~/.ssh/id_rsa.pub 不完善，尝试重新生成...")
        os.system("rm -rf %s/*" % _ssh_dir)
        os.system("ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa -q")
        if os.path.exists(os.path.join(_ssh_dir, "id_rsa"))  and os.path.exists(os.path.join(_ssh_dir, "id_rsa.pub")):
            print("~/.ssh/id_rsa ~/.ssh/id_rsa.pub已自动生成")
        else:
            raise Exception(("Error! ~/.ssh/id_rsa ~/.ssh/id_rsa.pub 文件缺失，请手动通过ssh-keygen生成"))
    # git clone 不显示yes or no 必须进行的配置。--   ~/.ssh/config文件。
    ssh_config = '''Host *
    StrictHostKeyChecking no'''
    if not os.path.exists(os.path.join(_ssh_dir, "config")):
        with open(os.path.join(_ssh_dir, "config"), "w") as f:
            f.write(ssh_config + '\n')
    else:
        with open(os.path.join(_ssh_dir, "config"), "r") as f:
            content = f.read()
        if ssh_config not in content:
            with open(os.path.join(_ssh_dir, "config"), "w") as f:
                f.write(content + '\n' + ssh_config + '\n')

    os.system("chmod 600 %s" % os.path.join(_ssh_dir, "config"))
    os.system("mkdir -p %s" % work_dir)
    os.system("mkdir -p %s" % os.path.join(work_dir, 'scripts'))
    code_temp_path = os.path.join(work_dir, "code_temp")
    os.system("mkdir -p %s" % code_temp_path)
    os.system("cd %s &&touch __cap_" % os.path.join(work_dir, 'scripts'))
    if not os.path.exists(code_temp_path):
        raise Exception("无法找到路径", code_temp_path)

    def simple_print(content):
        print("[%s]: %s" % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'), content))
        sys.stdout.flush()


    code_dir = os.path.join(code_temp_path, md5_(git_repo_url.encode("utf-8")))
    #os.system("rm -rf " + code_dir)
    os.system("mkdir -p %s" % code_dir)

    def run_cmd(cmd, timeout:int=120):
        simple_print(cmd)
        if not timeout:
            _v = os.system(cmd)
            if _v != 0:
                raise Exception("%s 执行失败，返回值 %s" % (cmd, _v))
            else:
                return _v
        else:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, env=os.environ)
            for i in range(0, timeout*10):
                try:
                    p.wait(timeout=0.1)
                except:
                    pass
                if p.stdout.readable():
                    _ = p.stdout.readlines()
                    # print(_)
                    if _:
                        simple_print("\n".join([i.decode('utf-8', errors='ignore').strip() for i in _ if i]))
                if p.stderr.readable():
                    _ = p.stderr.readlines()
                    if _:
                        simple_print("\n".join([i.decode('utf-8', errors='ignore').strip() for i in _ if i]))
                if p.returncode != None:
                    if p.returncode == 0:
                        return p.returncode
                    else:
                        raise Exception("%s 执行失败，返回值 %s" % (cmd, p.returncode))
            else:
                try:
                    p_obj = psutil.Process(pid=p.pid)
                    for _p  in p_obj.children(recursive=True):
                        try:
                            _p.kill()
                            _p.send_signal(9)
                        except:
                            pass
                    try:
                        p_obj.kill()
                        p_obj.send_signal(9)
                    except:
                        pass
                    try:
                        p.wait(timeout=1)
                    except:
                        pass
                except:
                    pass
                raise Exception("命令%s执行超过允许时间 %s" % (cmd, timeout))

    def get_ssh_conn(args):
        ip, port, user, passwd = args
        start_time = time.time()
        ssh = paramiko.SSHClient()

        pkey = None
        simple_print("开始在SSH连接%s" % (ip))
        if not passwd:
            passwd = None
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if passwd:
                pass
            else:
                # try:
                home_path = os.path.expanduser("~")
                key_path = os.path.join(home_path, ".ssh", "id_rsa")
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
                        ssh.sftp = ssh.open_sftp()
                        ssh.ip = ip
                        ssh.port = port
                        break
                    except  Exception as e:
                        simple_print(e)
                        _e = e
                        pass
                else:
                    raise _e
                simple_print("SSH- %s:%s 连接创建成功，耗时 %.3f" % (ip,port, time.time()-start_time))
                return ssh
            except Exception as e:
                if passwd:
                    raise Exception("SSH %s:%s 连接失败。%s" % (ip, port, str(e)))
                else:
                    raise Exception("SSH %s:%s 免密连接失败。%s " % (ip, port, str(e)))
        except (PipeTimeout, Exception) as e :
            message = str(e) or e.__repr__()
            raise Exception(message)



    def ssh_command(ssh_conn, command: str, timeout:int=60, with_stdout=False):
        "远程执行命令"
        # 默认超时时间是60s
        # 需要自己根据需要调整
        ssh = ssh_conn
        try:
            tran = ssh.get_transport()
            chan = tran.open_session()
            chan.settimeout(timeout)
            chan.get_pty()
            f = chan.makefile()
            chan.exec_command(command)
            stdout_info = f.read().decode('utf-8').strip()
            simple_print(stdout_info)
            return_code = chan.recv_exit_status()
            f.close()
            #ssh.close()
            assert return_code == 0, Exception("在%s:%s上执行%s失败，返回值是%s!(命令正常运行返回值一般是0)" %
                                               (ssh.ip,ssh.port,command, return_code))
        except (PipeTimeout, Exception) as e:
            # print(e,[e,type(e)])
            # traceback.print_exc()
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
                message = '在%s:%s  执行%s失败，超过最大允许时间 %ss' % (ssh.ip,ssh.port, command, timeout)
            raise Exception(message)
        else:
            if with_stdout:
                return stdout_info


    def ssh_commands(ssh_conn, commands: list, timeout:int=60, with_stdout=False):
        "远程执行命令"
        # 默认超时时间是60s
        # 需要自己根据需要调整
        assert len(commands) >= 1
        ssh = ssh_conn
        try:

            for command in commands:
                tran = ssh.get_transport()
                chan = tran.open_session()
                chan.settimeout(timeout)
                chan.get_pty()
                f = chan.makefile()
                simple_print("开始在%s:%s上执行%s" % (ssh.ip,ssh.port, command))
                chan.exec_command(command)
                stdout_info = f.read().decode('utf-8').strip()
                simple_print(stdout_info)
                return_code = chan.recv_exit_status()
                assert return_code == 0, Exception("在%s:%s上执行%s失败，返回值是%s!(命令正常运行返回值一般是0)" %
                                                   (ssh.ip,ssh.port,command, return_code))
                f.close()

        except (PipeTimeout, Exception) as e:
            # print(e,[e,type(e)])
            # traceback.print_exc()
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
                message = '在%s:%s  执行%s失败，超过最大允许时间 %ss' % (ssh.ip,ssh.port, command, timeout)
            raise Exception(message)
        else:
            pass

    if not code_tar_gz_path:
        # 拉取代码
        simple_print("开始从git拉取代码...")
        if not os.path.exists(os.path.join(code_dir, 'code_dir')) or \
                not os.listdir(os.path.join(code_dir, 'code_dir')):
            cmd = "cd %s && rm -rf code_dir && git clone  %s code_dir" % (code_dir, git_repo_url)
        else:
            cmd = 'cd %s/code_dir && git pull ' % code_dir
        p_return_code = run_cmd(cmd, timeout=1800)  # 最大允许时间30分钟
        if p_return_code == 0:
            simple_print("最新代码拉取成功")
        else:
            raise Exception('最新代码拉取失败，Git ErrorCode ', p_return_code)
        simple_print("#进度20%")
        simple_print("开始获取版本 - %s -的代码" % version_info)
        run_cmd("cd %s/code_dir && git reset --hard  %s" % (code_dir, version_info))
        simple_print("代码已获取成功")
        run_cmd("cd %s && rm -rf %s.tar.gz" % (code_dir, version_info))
        run_cmd("cd %s && rm -rf %s && cp -a code_dir %s  && \cp -a %s/* %s " % (code_dir, version_info, version_info,
                                                                                 os.path.join(work_dir, 'scripts'),
                                                                                 version_info))  # 代码拷贝
        simple_print('开始执行cmd_before_deploy')
        for cmd in cmd_before_deploy.splitlines():
            cmd = cmd.strip()
            if cmd:
                run_cmd("cd %s/%s && %s " % (code_dir, version_info, cmd), timeout=30)
        simple_print("cmd_before_deploy执行成功")
        simple_print("开始把代码打包为压缩包")
        run_cmd("cd  %s/%s && rm -rf .git && tar -zcvf  ../%s.tar.gz ./* >/dev/null " % (
        code_dir, version_info, version_info))
        run_cmd("cd %s && rm -rf %s" % (code_dir, version_info))
        simple_print("代码打包成功")
        simple_print("进度35%")
    else:
        simple_print("开始从自定义URL获取代码压缩包")
        code_tar_gz_path = code_tar_gz_path.replace("{version}", version_info)
        run_cmd("wget  %s  -O %s" % (code_tar_gz_path, os.path.join(code_dir,
                                                                              "%s.tar.gz" % version_info)))
        simple_print("从自定义代码源获取代码压缩包成功")
        simple_print("进度35%")

    def send_code(args):
        ssh_conn, source_zip_path, app_path, code_mode = args
        # 向目标机器发布代码
        now_hour_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S-")
        zip_file_name = source_zip_path.split("/")[-1]
        target_code_path = now_hour_str + zip_file_name.split(".")[0]
        dest_zip_path = os.path.join(app_path, zip_file_name)

        # 清理 zip 目录
        cmd = "rm -rf %s && mkdir -p %s " % (dest_zip_path, app_path)
        ssh_command(ssh_conn,cmd, timeout=10)

        # 拷贝代码到目标机器
        #sftp = paramiko.SFTPClient.from_transport(ssh_conn)
        #ssh_conn.get_transport()
        #sftp = ssh_conn.open_sftp()

        if code_mode == 0 :
            # sftp 模式
            ssh_conn.sftp.put(source_zip_path, os.path.join(app_path, zip_file_name))
        else:
            # 七牛云中转模式
            ssh_command(ssh_conn, "wget %s  -O %s " % (upload_qiniu_url,
                                                                os.path.join(app_path, zip_file_name))
                        , timeout=1800)

        print(ssh_conn.sftp.listdir(app_path))
        # _return_v = run_cmd('''%s -p  %s  scp -P %s  %s  %s@%s:%s   ''' % (
        #     ssh_pass_path, (passwd if passwd else "''"), port, source_zip_path, user, host, app_path
        # ))

        # 解压 软链 清理
        cmd = "cd %s && mkdir -p %s && mv %s %s  && " \
              "cd %s && tar -zxvf %s >/dev/null && rm -rf %s  &&  " \
              "cd %s && rm -rf current && ln -s  %s  current" % \
              (app_path, target_code_path, zip_file_name, target_code_path,
               target_code_path, zip_file_name, zip_file_name,
               app_path, target_code_path
               )
        # _return_v = run_cmd('''%s -p %s  ssh -p %s  %s@%s  "%s " ''' % (
        #     ssh_pass_path, (passwd if passwd else "''"), port, user, host , cmd
        # ), timeout=50)
        ssh_command(ssh_conn,cmd, timeout=50)
        # 计算出所有待删除的代码， 并进行删除
        _return_stdout = ssh_command(ssh_conn, "cd %s && ls" % app_path, with_stdout=True)
        _ = [i for i in _return_stdout.split() if i.startswith('20') and '-' in i]
        _.sort()
        dels_codes = _[:-remain_num]
        if dels_codes:
            del_cmd = ("cd %s && " % app_path)  + " && ".join(["rm -rf %s" % i for i in dels_codes])
            # run_cmd('''%s -p %s  ssh -p %s  %s@%s  "%s " ''' % (
            #     ssh_pass_path, (passwd if passwd else "''"), port, user, host, del_cmd
            # ), timeout=30)
            ssh_command(ssh_conn, del_cmd, timeout=30)
        return 0

    for machine in remote_machine_info:
        if machine['code_mode']:
            need_upload_qiniu = True
            break
    if need_upload_qiniu:
        simple_print("因发布地址存在公网地址，上传代码到七牛云...")
        q = Auth(qiniu_key, qiniu_secret)
        bucket = BucketManager(q)
        token = q.upload_token(qiniu_bucket, upload_qiniu_path, 3600)
        ret, info = put_file(token, upload_qiniu_path, os.path.join(code_dir,
                                                                              "%s.tar.gz" % version_info))
    simple_print("开始创建SSH连接")
    SSH_CONN_CACHE = {}
    if remote_machine_info:
        pool = ThreadPool(len(remote_machine_info))
        map_args_list = []
        for machine in remote_machine_info:
            host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
            map_args_list.append([host, port, user, passwd])
        # print(remote_machine_info, map_args_list)
        res_list = pool.map(get_ssh_conn, map_args_list)
        pool.close()
        for i,j in zip(remote_machine_info,res_list):
            if j == None:
                raise Exception('创建到%s:%s的SSH连接失败' % (i["host"],i["port"] ) )
        SSH_CONN_CACHE = {(i["host"],i["port"]): res_list[_index]  for _index, i in enumerate(remote_machine_info)}
    print(SSH_CONN_CACHE)
    simple_print("SSH连接创建完成")
    simple_print("进度40%")
    simple_print("开始向多线程向各服务器下发代码")
    map_args_list = []
    for machine in remote_machine_info:
        host, port, user, passwd, code_mode = machine['host'], machine['port'], machine['user'], machine['passwd'], \
                                            machine['code_mode']
        map_args_list.append([SSH_CONN_CACHE[(host, port)], os.path.join(code_dir, version_info + ".tar.gz"),
                  app_path, code_mode])

    res_list = []
    if map_args_list:
        _pool = ThreadPool(len(map_args_list))
        res_list = _pool.map(send_code, map_args_list)
        _pool.close()

    for _index, res in enumerate(res_list):
        if res != 0:
            raise Exception('发布代码到%s失败' % map_args_list[_index][0].ip)
        else:
            simple_print("发布代码到%s成功" % map_args_list[_index][0].ip)

    simple_print("代码下发成功")
    os.system("rm -rf  %s/*.tar.gz" % code_dir)
    simple_print("进度60%")
    simple_print("开始在各机器多线程执行Build Cmd")
    def _target_fun(args):
        #print(args, len(args))
        host, port, _cmds = args
        ssh_commands(SSH_CONN_CACHE[host,port], _cmds, timeout=60)
        simple_print("%s:%s Build Cmd 执行成功" % (host,port))
    multi_thread_args = []
    for machine in remote_machine_info:
        host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
        _cmds = []
        for cmd in cmd_build_app.splitlines():
            cmd = cmd.strip().replace("{host}",host).replace("{ip}",host)
            if cmd:
                _cmds.append("cd %s/current && %s" % (app_path, cmd ))
        if _cmds:
            multi_thread_args.append((host, port, _cmds))
            # if cmd:
            #     ssh_command(host,port,user,passwd, cmd, timeout=60)

    if multi_thread_args:
        _pool = ThreadPool(len(multi_thread_args))
        _pool.map(_target_fun, multi_thread_args)
        _pool.close()

    simple_print("Build Cmd全部执行成功")
    simple_print("进度70%")

    simple_print('开始各机器多线程执行Start Cmd')
    def _target_fun(args):
        #print(args, len(args))
        host, port,  _cmds = args
        ssh_commands(SSH_CONN_CACHE[host,port], _cmds, timeout=60)
        simple_print("%s:%s Start Cmd 执行成功" % (host, port))
    multi_thread_args = []
    for machine in remote_machine_info:
        host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
        _cmds = []
        for cmd in cmd_start_app.splitlines():
            cmd = cmd.strip().replace("{host}",host).replace("{ip}",host)
            if cmd:
                _cmds.append("cd %s/current && %s" % (app_path, cmd ))
        if _cmds:
            multi_thread_args.append((host, port , _cmds))
        #simple_print("%s Start Cmd命令执行成功" % host)
    if multi_thread_args:
        _pool = ThreadPool(len(multi_thread_args))
        _pool.map(_target_fun, multi_thread_args)
        _pool.close()

    simple_print("Start Cmd全部执行成功")
    simple_print("进度80%")
    simple_print('开始执行Success Cmd')
    for cmd in success_after_deploy.splitlines():
        cmd = cmd.strip()
        if cmd:
            run_cmd(cmd, timeout=60)
    simple_print('Success Cmd执行成功')
    if need_upload_qiniu:
        bucket.delete(qiniu_bucket, upload_qiniu_path)
        print("清理七牛云文件...")
    simple_print("进度100%")



# 代码回滚
def rollback_code(app_path, version_info, remote_machine_info, cmd_start_app:str, success_after_deploy:str, **kwargs):
    # app_name 应用名
    import os, hashlib, time, subprocess, sys
    from qiniu import Auth, put_file, etag, put_data, BucketManager
    import multiprocessing
    sys.stdout.flush()
    from multiprocessing.dummy import Pool as ThreadPool
    import paramiko, os
    from paramiko.channel import PipeTimeout
    # import ssh_tool
    import psutil, datetime
    print("开始...")
    print("进度5%")
    def simple_print(content):
        print("[%s]: %s" % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'), content))
        sys.stdout.flush()

    def run_cmd(cmd, timeout:int=120):
        simple_print(cmd)
        if not timeout:
            _v = os.system(cmd)
            if _v != 0:
                raise Exception("%s 执行失败，返回值 %s" % (cmd, _v))
            else:
                return _v
        else:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, env=os.environ)
            for i in range(0, timeout*10):
                try:
                    p.wait(timeout=0.1)
                except:
                    pass
                if p.stdout.readable():
                    _ = p.stdout.readlines()
                    # print(_)
                    if _:
                        simple_print("\n".join([i.decode('utf-8', errors='ignore').strip() for i in _ if i]))
                if p.stderr.readable():
                    _ = p.stderr.readlines()
                    if _:
                        simple_print("\n".join([i.decode('utf-8', errors='ignore').strip() for i in _ if i]))
                if p.returncode != None:
                    if p.returncode == 0:
                        return p.returncode
                    else:
                        raise Exception("%s 执行失败，返回值 %s" % (cmd, p.returncode))
            else:
                try:
                    p_obj = psutil.Process(pid=p.pid)
                    for _p  in p_obj.children(recursive=True):
                        try:
                            _p.kill()
                            _p.send_signal(9)
                        except:
                            pass
                    try:
                        p_obj.kill()
                        p_obj.send_signal(9)
                    except:
                        pass
                    try:
                        p.wait(timeout=1)
                    except:
                        pass
                except:
                    pass
                raise Exception("命令%s执行超过允许时间 %s" % (cmd, timeout))


    def get_ssh_conn(args):
        ip, port, user, passwd = args
        start_time = time.time()
        ssh = paramiko.SSHClient()

        pkey = None
        simple_print("开始在SSH连接%s:%s" % (ip,port))
        if not passwd:
            passwd = None
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if passwd:
                pass
            else:
                # try:
                home_path = os.path.expanduser("~")
                key_path = os.path.join(home_path, ".ssh", "id_rsa")
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
                        ssh.sftp = ssh.open_sftp()
                        ssh.ip = ip
                        ssh.port = port
                        break
                    except  Exception as e:
                        simple_print(e)
                        _e = e
                        pass
                else:
                    raise _e
                simple_print("SSH- %s:%s 连接创建成功，耗时 %.3f" % (ip, port, time.time()-start_time))
                return ssh
            except Exception as e:
                if passwd:
                    raise Exception("SSH %s:%s 连接失败。%s" % (ip, port, str(e)))
                else:
                    raise Exception("SSH %s:%s 免密连接失败。%s " % (ip, port, str(e)))
        except (PipeTimeout, Exception) as e :
            message = str(e) or e.__repr__()
            raise Exception(message)

    def ssh_command(ssh_conn, command: str, timeout:int=60, with_stdout=False):
        "远程执行命令"
        # 默认超时时间是60s
        # 需要自己根据需要调整
        ssh = ssh_conn
        host = ssh.ip
        port = ssh.port
        try:
            tran = ssh.get_transport()
            chan = tran.open_session()
            chan.settimeout(timeout)
            chan.get_pty()
            f = chan.makefile()
            chan.exec_command(command)
            stdout_info = f.read().decode('utf-8').strip()
            simple_print(stdout_info)
            return_code = chan.recv_exit_status()
            f.close()
            #ssh.close()
            assert return_code == 0, Exception("在%s:%s 上执行%s失败，返回值是%s!(命令正常运行返回值一般是0)" %
                                               (host, port, command, return_code))
        except (PipeTimeout, Exception) as e:
            # print(e,[e,type(e)])
            # traceback.print_exc()
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
                message = '在%s:%s  执行%s失败，超过最大允许时间 %ss' % (ssh.ip,ssh.port, command, timeout)
            raise Exception(message)
        else:
            if with_stdout:
                return stdout_info


    def ssh_commands(ssh_conn, commands: list, timeout:int=60, with_stdout=False):
        "远程执行命令"
        # 默认超时时间是60s
        # 需要自己根据需要调整
        assert len(commands) >= 1
        ssh = ssh_conn
        host = ssh.ip
        port = ssh.port
        try:

            for command in commands:
                tran = ssh.get_transport()
                chan = tran.open_session()
                chan.settimeout(timeout)
                chan.get_pty()
                f = chan.makefile()
                simple_print("开始在%s:%s上执行%s" % (host, port, command))
                chan.exec_command(command)
                stdout_info = f.read().decode('utf-8').strip()
                simple_print(stdout_info)
                return_code = chan.recv_exit_status()
                assert return_code == 0, Exception("在%s:%s上执行%s失败，返回值是%s!(命令正常运行返回值一般是0)" %
                                                   (host,port,command, return_code))
                f.close()

        except (PipeTimeout, Exception) as e:
            # print(e,[e,type(e)])
            # traceback.print_exc()
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
                message = '在%s:%s  执行%s失败，超过最大允许时间 %ss' % (ssh.ip,ssh.port, command, timeout)
            raise Exception(message)
        else:
            pass

    simple_print("开始创建SSH连接")
    SSH_CONN_CACHE = {}
    if remote_machine_info:
        pool = ThreadPool(len(remote_machine_info))
        map_args_list = []
        for machine in remote_machine_info:
            host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
            map_args_list.append([host, port, user, passwd])
        # print(remote_machine_info, map_args_list)
        res_list = pool.map(get_ssh_conn, map_args_list)
        pool.close()
        for i, j in zip(remote_machine_info, res_list):
            if j == None:
                raise Exception('创建到%s的SSH连接失败' % i["host"])
        SSH_CONN_CACHE = {(i["host"],i["port"]): res_list[_index] for _index, i in enumerate(remote_machine_info)}
    print(SSH_CONN_CACHE)
    simple_print("SSH连接创建完成")
    simple_print("进度20%")
    simple_print("校验版本%s是否可以回滚..." % version_info)
    # 版本校验
    for machine in remote_machine_info:
        host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
        ssh_conn = SSH_CONN_CACHE[(host, port)]
        out = ssh_command(ssh_conn,"mkdir -p %s && cd %s && ls" % (app_path, app_path), with_stdout=True).split()
        out = [i for i in out if i!='current']
        if version_info in out:
            pass
        else:
            raise Exception("当前机器%s:%s  版本 %s 校验失败，无此版本代码。" % (host,port,version_info))
    simple_print("版本%s校验成功。" % version_info)
    # 代码回滚
    for machine in remote_machine_info:
        host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
        ssh_conn = SSH_CONN_CACHE[(host, port)]
        ssh_command(ssh_conn,
                          "mkdir -p %s && cd %s && rm -rf current && ln -s  %s  current" %
                          (app_path, app_path, version_info))
    simple_print('代码current软连更改成功。')
    simple_print("进度50%")
    simple_print('开始各机器多线程执行Start Cmd')

    def _target_fun(args):
        # print(args, len(args))
        host, port, _cmds = args
        ssh_commands(SSH_CONN_CACHE[host, port], _cmds, timeout=60)
        simple_print("%s:%s Start Cmd 执行成功" % (host, port))

    multi_thread_args = []
    for machine in remote_machine_info:
        host, port, user, passwd = machine['host'], machine['port'], machine['user'], machine['passwd']
        _cmds = []
        for cmd in cmd_start_app.splitlines():
            cmd = cmd.strip().replace("{host}", host).replace("{ip}", host)
            if cmd:
                _cmds.append("cd %s/current && %s" % (app_path, cmd))
        if _cmds:
            multi_thread_args.append((host, port, _cmds))
        # simple_print("%s Start Cmd命令执行成功" % host)
    if multi_thread_args:
        _pool = ThreadPool(len(multi_thread_args))
        _pool.map(_target_fun, multi_thread_args)
        _pool.close()

    simple_print("Start Cmd全部执行成功")
    simple_print("进度80%")
    simple_print('开始执行Success Cmd')
    for cmd in success_after_deploy.splitlines():
        cmd = cmd.strip()
        if cmd:
            run_cmd(cmd, timeout=60)
    simple_print('Success Cmd执行成功')
    simple_print("回滚完成。")
    simple_print("进度100%")







if __name__ == '__main__':
    # import process_task
    # task_id = process_task.run_task(pub_code,("/data/cap", 'ssh://git@192.168.240.131:722/zhoukunpeng/cap.git'),
    #                                 {"version_info":"1b7b1b7d84",
    #                                  'remote_machine_info':[
    #                                                         {'host':'192.168.240.244',
    #                                                          'port':'22',
    #                                                          'user':'root',
    #                                                          'passwd':'123456'
    #                                                          }
    #                                                         ],
    #
    #                                  'app_path': '/data/code/helloworld',
    #                                  'cmd_before_deploy':'',
    #                                  'cmd_build_app': '',
    #                                  'cmd_start_app':'',
    #                                  'success_after_deploy':"",
    #                                  'remain_num':3
    #                                  })
    #
    #
    # while 1:
    #     log = process_task.get_log(task_id)
    #     print(log)
    #     time.sleep(1)
    rollback_code('/data/code/tesbbb','1b7b1b7d84',[
                                                            {'host':'192.168.240.240',
                                                             'port':'22',
                                                             'user':'root',
                                                             'passwd':'gc895316'
                                                             }
                                                            ],"pwd","ll"
                  )