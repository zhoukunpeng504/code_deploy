# coding:utf8
__author__ = 'Administrator'

from django.db import models
import os, json, random, time, datetime
import sys, os, re
import paramiko
import multiprocessing
import os


class Project(models.Model):
    '项目'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='', unique=True)  # 项目名
    addtime = models.PositiveIntegerField(default=0)  # 创建时间

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = "项目"
        db_table = 'cap_project'


class Server(models.Model):
    "服务器"
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='', unique=True)  # 服务器名
    ip = models.CharField(verbose_name="IP", blank=False, db_index=True, max_length=15)
    user = models.CharField(verbose_name="用户", default='root', max_length=50)
    password = models.CharField(verbose_name="密码", default='123456', max_length=200)
    ssh_port = models.SmallIntegerField(verbose_name="端口", blank=False, default=22)
    addtime = models.PositiveIntegerField(default=0)
    code_mode = models.PositiveIntegerField(default=0)  # 代码传输方式 0 sftp  1 七牛云中转

    class Meta:
        verbose_name = "服务器"
        verbose_name_plural = "服务器"
        db_table = 'cap_server'
        unique_together = [('ip', 'ssh_port')]

    def __unicode__(self):
        return "%s || %s" % (self.ip, self.user)


class RepoServer(models.Model):
    "代码仓库服务器"
    id = models.AutoField(primary_key=True)
    repo_name = models.CharField(max_length=50, default='', unique=True)
    server_url = models.CharField(max_length=100, default='')
    addtime = models.PositiveIntegerField(default=0)
    repo_type = models.PositiveSmallIntegerField(default=0)  # 1 gitlab   2 gitee
    token = models.CharField(max_length=500,default='')

    class Meta:
        db_table  = 'cap_repo_server'
        verbose_name = "代码仓库服务器"
        verbose_name_plural = "代码仓库服务器"


class App(models.Model):
    "应用"
    id = models.AutoField(primary_key=True)
    proj_id = models.PositiveIntegerField(default=1)  # 所属项目
    name = models.CharField(verbose_name="应用名", max_length=30, blank=False, db_index=True, unique=True)
    repo_server_id = models.PositiveIntegerField(default=0)  #  对应的代码服务器的id
    repo_id = models.PositiveIntegerField(default=0)
    repo_git_url = models.CharField(verbose_name="git URL，支持ssh协议",
                                      blank=False, max_length=200)
    branch_name = models.CharField(verbose_name='分支名',max_length=200, default='')
    deploy_to = models.CharField(verbose_name="发布路径", blank=False, max_length=200)  # 发布路径为空代表不发代码。
    old_version_num = models.PositiveSmallIntegerField(verbose_name="保留历史代码版本数", default=4)
    server_ids_1 = models.CharField(verbose_name="环境1服务器", blank=False, null=False,
                                         max_length=500, db_column='formal_server_ids')
    server_ids_2 = models.CharField(verbose_name="环境2服务器", blank=False, null=False,
                                       max_length=500, db_column='test_server_ids')
    server_ids_3 = models.CharField(verbose_name="环境3服务器", blank=False, null=False,
                                    max_length=500, db_column='server_ids_3')
    server_ids_4 = models.CharField(verbose_name="环境4服务器", blank=False, null=False,
                                    max_length=500, db_column='server_ids_4')

    cmd_before_deploy_1 = models.TextField(verbose_name="发布正式开始前执行命令", blank=True, db_column='cmd_before_deploy')

    cmd_build_app_1 = models.TextField(default='', blank=True, db_column='cmd_build_app')
    cmd_start_app_1 = models.TextField(verbose_name="发布后执行命令（如：替换配置，composer update）",
                                       blank=True, db_column='cmd_start_app')

    success_after_deploy_1 = models.TextField(verbose_name="代码发布完成后执行命令", blank=True,
                                              db_column='success_after_deploy')

    cmd_before_deploy_2 = models.TextField(verbose_name="发布正式开始前执行命令", blank=True,
                                              db_column='cmd_before_deploy_test')
    cmd_build_app_2 = models.TextField(default='', blank=True,
                                          db_column='cmd_build_app_test')
    cmd_start_app_2 = models.TextField(verbose_name="发布后执行命令-环境（如：替换配置，composer update）", blank=True,
                                          db_column='cmd_start_app_test')
    success_after_deploy_2 = models.TextField(verbose_name="代码发布完成后执行命令-环境", blank=True,
                                                 db_column='success_after_deploy_test')

    cmd_before_deploy_3 = models.TextField(verbose_name="发布正式开始前执行命令", blank=True,
                                              db_column='cmd_before_deploy_3')
    cmd_build_app_3 = models.TextField(default='', blank=True,
                                          db_column='cmd_build_app_3')
    cmd_start_app_3 = models.TextField(verbose_name="发布后执行命令-环境（如：替换配置，composer update）", blank=True,
                                          db_column='cmd_start_app_3')
    success_after_deploy_3 = models.TextField(verbose_name="代码发布完成后执行命令-环境", blank=True,
                                                 db_column='success_after_deploy_3')

    cmd_before_deploy_4 = models.TextField(verbose_name="发布正式开始前执行命令", blank=True,
                                              db_column='cmd_before_deploy_4')
    cmd_build_app_4 = models.TextField(default='', blank=True,
                                          db_column='cmd_build_app_4')
    cmd_start_app_4 = models.TextField(verbose_name="发布后执行命令-环境（如：替换配置，composer update）", blank=True,
                                          db_column='cmd_start_app_4')
    success_after_deploy_4 = models.TextField(verbose_name="代码发布完成后执行命令-环境", blank=True,
                                                 db_column='success_after_deploy_4')


    addtime = models.PositiveIntegerField(default=0)

    code_tar_gz_path = models.CharField(verbose_name="自定义targz代码URL", blank=False, null=False,
                                       max_length=500)


    def __unicode__(self):
        return "%s-%s" % ("应用", self.name)

    class Meta:
        verbose_name = "应用"
        verbose_name_plural = "应用"
        db_table = 'cap_app'

    @property
    def repo_server(self):
        return RepoServer.objects.get(id=self.repo_server_id)

    @property
    def project(self):
        return Project.objects.get(id=self.proj_id)


class PubLog(models.Model):
    "发布日志"
    id = models.AutoField(primary_key=True)
    ope_user_name = models.CharField(verbose_name="操作人", blank=False, max_length=30, db_index=True)
    target_version = models.CharField(verbose_name="目标版本", blank=False, max_length=100)
    target_version_meta = models.CharField(verbose_name="目标版本附加信息", max_length=100)
    #appname = models.CharField(verbose_name="应用名", blank=False, max_length=50, db_index=True)
    app_id = models.PositiveIntegerField(default=0)
    environ_type = models.PositiveIntegerField(default=0)  # 环境  1 正式环境 2 测试环境


    task_id = models.CharField(max_length=50, default='')
    task_log = models.TextField(verbose_name="操作日志", blank=True)
    progress = models.IntegerField(verbose_name="进度", default=0, db_index=True, )  # 进度 0 开始 100 成功    -100 失败
    status = models.PositiveSmallIntegerField(verbose_name="状态", default=1,
                                              db_index=True)  # 1  开始   2.进行中   3  完成    4  失败
    status_uptime = models.PositiveIntegerField(default=0)     # 状态更新时间
    reason = models.CharField(verbose_name="操作原因", max_length=300)  # 操作原因说明
    operatetime = models.DateTimeField(verbose_name="操作时间", auto_now_add=True, db_index=True)
    pub_type = models.PositiveIntegerField(default=0)   # 0 发布  1 回滚


    class Meta:
        verbose_name = "发布记录"
        verbose_name_plural = "所有发布记录"
        db_table = 'cap_pub_log'


    def get_operate_time(self):
        return self.operatetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_reason(self):
        if len(self.reason) <= 10:
            return self.reason
        else:
            return self.reason[0:10] + "..."


    def can_stoped(self):
        "获取本次发布是否可以强制结束"
        if self.status == 2:
            return True
        else:
            return False

    @property
    def status_cn(self):
        statusconfig = {1: "开始", 2: "进行中", 3: "已完成", 4: "失败"}
        _ = statusconfig[self.status]
        if self.status == 2:
            _ += ("%s%%" % self.progress)
        return _



class UserAppPerm(models.Model):
    # 用户应用权限
    uid = models.AutoField(primary_key=True)
    apps = models.CharField(max_length=300, default='')
    addtime = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'user_app_perm'
        verbose_name = "用户应用权限表"
        verbose_name_plural = "用户应用权限表"


