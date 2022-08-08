#coding:utf-8


# Uncomment the next two lines to enable the admin:
import time

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.admin import views
from code_deploy import  settings
from django.views import  static
admin.autodiscover()
import  os
from django.contrib import admin
from django.urls import path,re_path
from . import settings
from django.views.static import serve as static_serve
from . import views
from . import settings
from . import models


urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', static_serve,
            {'document_root': settings.STATICFILES_DIRS[0]}),  # django static

    # path('admin/', admin.site.urls),  # django admin
    path('admin/', admin.site.urls),
    #path('logout/', )
    path('', views.home),
    path('pub/', views.pub),
    path('pub_log/', views.pub_log),
    path('changepwd/', views.changepwd),
    path('user_manage/', views.user_manage),     # 用户管理
    path('reposerver_manage/', views.reposerver_manage),     # 代码仓库管理
    path('server_manage/', views.server_manage), # 服务器管理
    path('app_manage/', views.app_manage),       # 应用管理
    path('project_manage/', views.project_manage), # 项目管理

    path('get_gitserver_repos/', views.get_gitserver_repos),    # 获取git服务器的所有仓库
    path('get_recent_commit_log', views.get_recent_commit_log), # 获取git服务器的某仓库的提交日志


    path('pub_code/', views.pub_),               # 发布代码
    path("rollback_code/", views.rollback_),     # 回滚代码

    path('get_publog_detail', views.get_publog_detail), # 获取发布日志的详细信息
    path('get_testenviron_publog', views.get_testenviron_publog),
    path("get_app_current_status", views.get_app_current_status), # 获取应用在某环境当前的状态
    path('get_recent_publog', views.get_recent_publog), # 获取最近的发布日志
    path('kill_pubtask', views.kill_pubtask),  # 强制结束发布任务


    path('advantage_tools/', views.advantage_tools),

]


# 创建默认项目
try:
    models.Project.objects.filter(name='默认项目',id__gt=1).update(name='默认项目_')
    _ = models.Project.objects.get(id=1)
    _.name = '默认项目'
    _.save()
except models.Project.DoesNotExist:
    _ = models.Project(name='默认项目', addtime=int(time.time()))
    _.save()
models.App.objects.filter(proj_id=0).update(proj_id=1)
