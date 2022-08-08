# coding:utf-8
__author__ = "zhou"
# create by zhou on 2020/8/28
#import pickle as cloudpickle
import cloudpickle
import os
import random
import string
import json
import base64
import datetime
import psutil
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),"..",".."))
import config



MAX_TASK_RUNTIME = 3600 *2  # task运行时间超过2个小时的。将会被清理。
TASK_WORK_DIR = os.path.join(config.WORK_PATH, 'task')
os.system("mkdir -p %s" % TASK_WORK_DIR)


_current_dir = os.path.abspath(os.path.dirname(__file__))
_my_path = os.path.join(_current_dir, 'process_task.py')
if sys.executable.endswith('python') or sys.executable.endswith('python3') or \
        sys.executable.split("/")[-1].startswith("python"):
    _py_path = sys.executable
elif sys.executable.endswith('uwsgi') or sys.executable.endswith('uwsgi3'):
    if sys.version_info.major == 2:
        _py_path = os.path.join(os.path.dirname(sys.executable), 'python2')
        if not  os.path.exists(_py_path):
            _py_path = 'python2'
    else:
        _py_path = os.path.join(os.path.dirname(sys.executable), 'python3')
        if not os.path.exists(_py_path):
            _py_path = 'python3'
else:
    _py_path = 'python%s' % sys.version_info.major



def run_task(fun, args=(), kwargs={}, sync_fun=None):
    '''
    fun   要运行的函数
    args  函数的参数
    kwargs 函数的参数
    sync_fun  函数的运行状态。 接受两个参数 sync_fun(taskid, status, log)  status为 1 运行中  100 运行成功   -100 运行失败 。log为运行过程中的输出
    '''
    fun = cloudpickle.dumps(fun, protocol=4)
    #print([fun])
    cloudpickle.loads(fun)
    fun_b64 = base64.b64encode(fun).decode()
    today = datetime.datetime.now()
    def _gen(length: int = 8):
        "生成随机字符串"
        _ = random.sample(string.ascii_letters[:26] + "0123456789", length)
        return "".join(_)
    task_id =  today.strftime("%Y%m%d") +  _gen(10) + "CAP"
    if not sync_fun:
        sync_fun_b64 = None
    else:
        sync_fun_b64 = base64.b64encode(cloudpickle.dumps(sync_fun, protocol=4)).decode()
    data = {"fun_b64":fun_b64, 'args': args, 'kwargs': kwargs, 'sync_fun_b64': sync_fun_b64}
    # print(data)
    data_json = json.dumps(data)
    os.system("mkdir -p " + os.path.join(TASK_WORK_DIR,"process_task"))
    os.system("mkdir -p " + os.path.join(TASK_WORK_DIR,"process_task_log"))
    os.system("mkdir -p " + os.path.join(TASK_WORK_DIR,"process_task_result"))

    # # 对于过老的log删除掉
    # for i in  os.listdir('/tmp/process_task_log'):
    #     if i.endswith(".log"):
    #         _real_path = os.path.join('/tmp/process_task_log', i)
    #         try:
    #             modify_time = os.path.getmtime(_real_path)
    #             if time.time() - modify_time >= 86400*2:
    #                 os.system("rm -rf %s" % _real_path)
    #         except:
    #             pass
    #
    # # 对于过老的result删除掉
    # for i in  os.listdir('/tmp/process_task_result'):
    #     if i.endswith(".log"):
    #         _real_path = os.path.join('/tmp/process_task_result', i)
    #         try:
    #             modify_time = os.path.getmtime(_real_path)
    #             if time.time() - modify_time >= 86400*2:
    #                 os.system("rm -rf %s" % _real_path)
    #         except:
    #             pass


    with open(os.path.join(TASK_WORK_DIR,"process_task", task_id), "w") as f:
        f.write(data_json)

    os.system("%s %s/process_task.py %s >> %s 2>&1" %
              (_py_path, _current_dir, task_id, os.path.join(TASK_WORK_DIR,"process_task_log","%s.log" % task_id)))
    return task_id


def is_running(task_id):
    _p = psutil.Process(pid=1)
    for i in _p.children(recursive=True):
        try:
            cmdline = i.cmdline()
            if task_id == cmdline[-1]:
                return True
        except:
            pass
    return False


def kill(task_id):
    _p = psutil.Process(pid=1)
    for i in _p.children(recursive=True):
        try:
            cmdline = i.cmdline()
            if task_id == cmdline[-1]:
                try:
                    if i.is_running():
                        i.kill()
                        i.send_signal(9)
                except:
                    pass
        except:
            pass
    return True


def get_result(task_id):
    if is_running(task_id):
        raise Exception('task is running!')
    else:
        task_result_path =  os.path.join(TASK_WORK_DIR, 'process_task_result', task_id)
        if os.path.exists(task_result_path):
            with open(task_result_path, "r") as f:
                return json.loads(f.read())
        else:
            return None


def get_log(task_id):
    task_log_path = os.path.join(TASK_WORK_DIR, 'process_task_log', task_id + ".log")
    print(task_log_path)
    if os.path.exists(task_log_path):
        with open(task_log_path, "r") as f:
            return f.read()
    else:
        return None


if __name__ == '__main__':
    # 当前目录加入到sys.path中
    sys.path.append(os.path.dirname(__file__))
    import daemon, time
    import threading
    import traceback
    import pickle
    import sys
    #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    #print(_py_path)
    # 尝试杀死运行时间过长的task
    try:
        _p = psutil.Process(pid=1)
        for i in _p.children(recursive=True):
            try:
                cmdline = i.cmdline()
                cmdline_str = ' '.join(cmdline)
                if cmdline[-1].endswith("CAP") and "python" in cmdline_str and 'process_task.py' in cmdline_str:
                    if time.time() - i.create_time() > MAX_TASK_RUNTIME:
                        i.kill()
                        i.send_signal(9)
            except:
                pass
    except:
        pass

    task_id = sys.argv[-1]
    task_id_path = os.path.join(TASK_WORK_DIR,"process_task", task_id)
    with open(task_id_path, "r") as f:
        data_json = f.read()
    os.system("rm -rf %s" % task_id_path)
    task_log_path = os.path.join(TASK_WORK_DIR, 'process_task_log', task_id + ".log")
    data = json.loads(data_json)
    fun = base64.b64decode(data['fun_b64'].encode())
    try:
        fun = pickle.loads(fun)
    except:
        traceback.print_exc()
    args = data['args']
    kwargs = data['kwargs']
    daemon.daemon_start()

    task_status = 1
    # stdout刷新线程
    def flush():
        while 1:
            time.sleep(0.03)
            sys.stdout.flush()
            sys.stderr.flush()
    flush_thread = threading.Thread(target=flush)
    flush_thread.setDaemon(True)
    flush_thread.start()
    # 日志同步线程
    if data['sync_fun_b64']:
        sync_fun = cloudpickle.loads(base64.b64decode(data['sync_fun_b64'].encode()))

        def status_sync():
            _ = 0
            while True:
                if _:
                    time.sleep(0.7)
                try:
                    with open(task_log_path, "r") as f:
                        logcontent = f.read()
                    sync_fun(task_id, task_status, logcontent)
                except Exception as e:
                    #traceback.print_exc()
                    pass
                _ += 1

        thread = threading.Thread(target=status_sync)
        thread.setDaemon(True)
        thread.start()
    else:
        sync_fun = None
    try:
        result = fun(*args, **kwargs)
        task_status = 100
        try:
            result_json = json.dumps(result)
            os.system("mkdir -p %s" % os.path.join(TASK_WORK_DIR,"process_task_result"))
            with open(os.path.join(TASK_WORK_DIR,"process_task_result", task_id), "w") as f:
                f.write(result_json)
        except:
            pass
    except Exception as e:
        traceback.print_exc()
        task_status = -100
    time.sleep(3)