#coding:utf-8
__author__ = 'Administrator'

import datetime
import itertools
import time
import copy
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import  render_to_response,render
from django.core.paginator import Paginator
from django.utils.log  import  mail
from django.template import  Context,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import  csrf_exempt
import json
import config
from .utils import gitrepo, ssh_tool, process_task, pub_code
from django.forms import model_to_dict
import re
from .models import *
from django.db.models import Q
from django.conf import settings
from django.core.paginator import InvalidPage
from multiprocessing.dummy import Pool
from .utils.ssh_tool import *








def json_response(data):
    return HttpResponse(json.dumps(data), content_type="application/javascript")


@login_required
def home(request):
    return HttpResponseRedirect("/pub/")



@login_required
@csrf_exempt
def changepwd(request):
    "更改密码"
    if request.method == 'POST':
        result = {'status': True, 'message': 'success'}
        oldpwd=request.POST.get("oldpwd",'')
        newpwd=request.POST.get('newpwd','')
        confirm_pwd=request.POST.get('confirm_pwd','')
        username=request.user.username
        try:
            if not  request.user.check_password(oldpwd):
                raise Exception("您输入的旧密码错误！请重试")
            if len(newpwd)<6 or len(confirm_pwd)<6 :
                raise Exception("密码长度最少为6")
            if newpwd != confirm_pwd:
                raise Exception("两次输入不一致！请重试！")
        except Exception as e:
            result['status'] = False
            result['message'] = str(e)
        else:
            request.user.set_password(newpwd)
            request.user.save()
        return HttpResponse(json.dumps(result), content_type="application/javascript")

    return render(request,"change_pwd.html", locals())


@login_required
@csrf_exempt
def user_manage(request):
    "用户管理 "
    get_info = request.GET
    post_info = request.POST
    action = get_info.get('action', '')
    apps = list(App.objects.all().order_by("-id"))
    #apps.sort(key=lambda x: x.['name'] + x["name"])
    projects = {i.id:i for i in Project.objects.all()}
    for i in apps:
        i.proj = projects.get(i.proj_id)
    apps.sort(key=lambda x:x.proj.name + x.name )
    all_apps = {app.id:app  for app in apps}
    user_perms_info = {i.uid:[int(kk) for kk in  i.apps.strip().split(",") if int(kk) in all_apps]
                       for  i in UserAppPerm.objects.all()}

    if request.method == 'POST':
        if action == 'get_user_list':
            users = [
                {"id":i.id, "username": i.username, 'addtime': int(i.date_joined.timestamp()),
                      "is_active": i.is_active,"app_perms": user_perms_info.get(i.id, []) }
                            for i in  User.objects.all().order_by("-id")]
            return json_response(users)

        if action == 'add_user':
            result = {'status': True, 'message': 'success'}
            user_name = post_info.get("username", '').strip()
            pwd = post_info.get('pwd', '').strip()
            appids = post_info.getlist("app_ids", []) or []
            appids = ','.join([str(i) for i in appids if int(i) in all_apps])
            confirm_pwd = post_info.get('confirm_pwd', '').strip()
            try:
                assert user_name, Exception('用户名不能为空')
                assert pwd and  confirm_pwd and len(pwd)>=6 and len(confirm_pwd)>=6 \
                    and pwd == confirm_pwd, Exception('密码必须大于等于6位 且 两次输入密码必须一致')
                assert not User.objects.filter(username=user_name).exists(), Exception('用户名和现有用户重复！')
                user = User(username=user_name, is_active=True, is_staff=True, is_superuser=False)
                user.set_password(raw_password=pwd)
                user.save()
                user_perm = UserAppPerm(uid=user.id, apps=appids, addtime=int(time.time()))
                user_perm.save()
            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'disable_user':
            result = {'status': True, 'message': 'success'}
            user_id = post_info.get('user_id', '')
            try:
                id = int(user_id)
                user = User.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '用户已不存在！'
            else:
                if user.username != 'admin':
                    user.is_active = False
                    user.save()
            return json_response(result)


        if action == "enable_user":
            result = {'status': True, 'message': 'success'}
            user_id = post_info.get('user_id', '')
            try:
                id = int(user_id)
                user = User.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '用户已不存在！'
            else:
                user.is_active = True
                user.save()
            return json_response(result)

        if action == 'del_user':
            result = {'status': True, 'message': 'success'}
            user_id = post_info.get('user_id', '')
            try:
                id = int(user_id)
                user = User.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '用户已不存在！'
            else:
                if user.username != 'admin':
                    user.delete()
                UserAppPerm.objects.filter(uid=user.id).delete()
            return json_response(result)

        if action == 'reset_pwd':
            result = {'status': True, 'message': 'success'}
            user_id = post_info.get('user_id', '')
            try:
                id = int(user_id) #
                user = User.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '用户已不存在！'
            else:
                user.set_password('123456')
                user.save()
                result['message'] = '密码已置为123456'
            return json_response(result)

        if action == 'update_perm':
            result = {'status': True, 'message': 'success'}
            user_id = post_info.get('user_id', '')
            appids = post_info.getlist("app_ids", []) or []
            print("dddddd#######", appids)
            appids = ','.join([str(i) for i in appids if int(i) in all_apps])
            print(post_info, all_apps, appids)
            try:
                id = int(user_id) #
                user = User.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '用户已不存在！'
            else:
                try:
                    user_perm = UserAppPerm.objects.get(uid=user.id)
                    user_perm.apps = appids
                    user_perm.save()
                except:
                    user_perm = UserAppPerm(uid=user.id, apps=appids, addtime=int(time.time()))
                    user_perm.save()
                return json_response(result)


    return render(request,"user_manage.html", locals())


@login_required
@csrf_exempt
def reposerver_manage(request):
    "代码仓库管理"
    get_info = request.GET
    post_info = request.POST
    action = get_info.get('action', '')
    if request.method == 'POST':
        if action == 'get_reposerver':
            data = {'status':True, 'message':'success', 'data':None}
            try:
                id = post_info.get('id', '')
                id = int(id)
                repo = RepoServer.objects.get(id=id)
                data['data'] = model_to_dict(repo)
            except:
                data['status'] = False
                data['message'] = '当前GitServer已不存在'
            return json_response(data)

        if action == 'get_reposerver_list':
            servers = [
                {"id": i.id,
                 "repo_name": i.repo_name,
                 'repo_type':i.repo_type,
                 'addtime': i.addtime,
                 'token': i.token,
                 'server_url': i.server_url} for i in RepoServer.objects.all().order_by("-id")
            ]
            return json_response(servers)

        if action == 'add_reposerver':
            result = {'status': True, 'message': 'success'}
            repo_name = post_info.get("repo_name", '').strip()
            repo_type = post_info.get("repo_type", '').strip()
            server_url = post_info.get("server_url", '').strip("/")
            token = post_info.get("token", '').strip()

            try:
                assert repo_name, Exception('名称不能为空')
                assert repo_type in ('1', '2')
                assert server_url, Exception('服务器URL 不能为空')
                assert token ,Exception('Token不能为空')
                assert re.match(r"^https?://[^/]+(:\d{2,6})?$", server_url), Exception('服务器URL 格式不正确！')
                assert not RepoServer.objects.filter(repo_name=repo_name).exists(), Exception('名称和现有的重复！')

                if repo_type == '1':
                    try:
                        gitrepo.GitLab(token, server_url)
                    except Exception as  e:
                        raise Exception("服务器尝试连接失败，请检查URL或者Token.错误信息：%s" % str(e))

                if repo_type == '2':
                    try:
                        gitrepo.Gitee(token, server_url)
                    except Exception as  e:
                        raise Exception("服务器尝试连接失败，请检查URL或者Token.错误信息：%s" % str(e))

                repo_server = RepoServer(repo_name=repo_name, repo_type=int(repo_type),
                                  server_url=server_url,addtime=int(time.time()),
                                  token=token
                                  )
                repo_server.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'update_reposerver':
            result = {'status': True, 'message': 'success'}
            id = post_info.get("id",'').strip()
            repo_name = post_info.get("repo_name", '').strip()
            repo_type = post_info.get("repo_type", '').strip()
            server_url = post_info.get("server_url", '').strip("/")
            token = post_info.get("token", '').strip()
            id = int(id)
            try:
                assert RepoServer.objects.filter(id=id).exists(),Exception('Git服务器已不存在！')
                repo_server = RepoServer.objects.get(id=id)
                assert repo_name, Exception('名称不能为空')
                assert not RepoServer.objects.filter(~Q(id=id), repo_name=repo_name).exists(), Exception('该名称已存在！修改后重试！')
                assert repo_type in ('1', '2')
                assert server_url, Exception('服务器URL 不能为空')
                assert token, Exception('Token不能为空')
                assert re.match(r"^https?://[^/]+(:\d{2,6})?$", server_url), Exception('服务器URL 格式不正确！')

                if repo_type == '1':
                    try:
                        gitrepo.GitLab(token, server_url)
                    except Exception as  e:
                        raise Exception("服务器尝试连接失败，请检查URL或者Token.错误信息：%s" % str(e))

                if repo_type == '2':
                    try:
                        gitrepo.Gitee(token, server_url)
                    except Exception as  e:
                        raise Exception("服务器尝试连接失败，请检查URL或者Token.错误信息：%s" % str(e))


                repo_server.repo_name = repo_name
                repo_server.repo_type = repo_type
                repo_server.server_url = server_url
                repo_server.token = token
                repo_server.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'del_reposerver':
            result = {'status': True, 'message': 'success'}
            repo_id = post_info.get('repo_id', ' ')
            try:
                id = int(repo_id)
                repo_server = RepoServer.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = 'Git服务器已不存在！'
            else:
                if App.objects.filter(repo_server_id=id).count() > 0:
                    result['status'] = False
                    result['message'] = '当前Git服务器仍和应用有关联，禁止删除。'
                else:
                    repo_server.delete()
            return json_response(result)




    return render(request, "reposerver_manage.html", locals())


@login_required
@csrf_exempt
def project_manage(request):
    # 项目管理
    get_info = request.GET
    post_info = request.POST
    try:
        Project.objects.filter(name='默认项目', id__gt=1).update(name='默认项目_')
        _ = Project.objects.get(id=1)
        _.name = '默认项目'
        _.save()
    except Project.DoesNotExist:
        _ = Project(name='默认项目', addtime=int(time.time()))
        _.save()
    App.objects.filter(proj_id=0).update(proj_id=1)

    action = get_info.get('action', '')
    if request.method == 'POST':
        if action == 'get_project':
            data = {'status': True, 'message': 'success', 'data': None}
            try:
                id = post_info.get('id', '')
                id = int(id)
                proj = Project.objects.get(id=id)
                data['data'] = model_to_dict(proj)
            except:
                data['status'] = False
                data['message'] = '当前项目已不存在'
            return json_response(data)

        if action == 'get_project_list':
            _apps = App.objects.all()
            _nums = {}
            for i in _apps:
                _nums.setdefault(i.proj_id,0)
                _nums[i.proj_id] += 1
            projects = [
                dict(model_to_dict(i), app_num=_nums.get(i.id,0)) for i in Project.objects.all().order_by("-id")
            ]
            if "sort" in get_info:
                projects.sort(key=lambda x:x['name'])
            return json_response(projects)

        if action == 'add_project': # 添加项目
            result = {'status': True, 'message': 'success'}
            name = post_info.get("name", '').strip()
            try:
                assert name, Exception('项目名不能为空')
                assert not Project.objects.filter(name=name).exists(), Exception('名称和现有的重复！')
                project = Project(name=name,
                                  addtime=int(time.time()))
                project.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'del_project': # 删除项目
            result = {'status': True, 'message': 'success'}
            id = post_info.get('id', ' ')
            try:
                id = int(id)
                assert id != 1, Exception('默认项目不允许删除')
                assert Project.objects.filter(id=id).exists(), Exception('项目已不存在')
                project = Project.objects.get(id=id)
            except Exception as e:
                result['status'] = False
                result['message'] = str(e)
            else:
                _apps = App.objects.all()
                _nums = {}
                for i in _apps:
                    _nums.setdefault(i.proj_id, 0)
                    _nums[i.proj_id] += 1
                if id in _nums:
                    result['status'] = False
                    result['message'] = '项目仍和%s个应用有关联，禁止删除。' % _nums[id]
                else:
                    project.delete()
            return json_response(result)

        if action == 'update_project':
            result = {'status': True, 'message': 'success'}
            id = post_info.get("id", '').strip()
            name = post_info.get("name", '').strip()
            id = int(id)
            try:
                assert id!=1, Exception('默认项目不允许修改！')
                assert Project.objects.filter(id=id).exists(), Exception('项目已不存在！')
                project = Project.objects.get(id=id)
                assert name, Exception('名称不能为空')
                assert not Project.objects.filter(~Q(id=id), name=name).exists(), Exception('名称和现有的重复！')
                project.name = name
                project.save()
            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

    return render(request, "project_manage.html", locals())



@login_required
@csrf_exempt
def server_manage(request):
    "服务器管理"
    get_info = request.GET
    post_info = request.POST
    action = get_info.get('action', '')
    if request.method == 'POST':
        if action == 'get_server':
            data = {'status': True, 'message': 'success', 'data': None}
            try:
                id = post_info.get('id', '')
                id = int(id)
                repo = Server.objects.get(id=id)
                data['data'] = model_to_dict(repo)
            except:
                data['status'] = False
                data['message'] = '当前Server已不存在'
            return json_response(data)

        if action == 'get_server_list':
            servers = [
                model_to_dict(i) for i in Server.objects.all().order_by("-id")
            ]
            return json_response(servers)

        if action == 'add_server':
            result = {'status': True, 'message': 'success'}
            name = post_info.get("name", '').strip()
            ip = post_info.get("ip", '').strip()
            ssh_port = post_info.get("ssh_port", '').strip("/")
            user = post_info.get("user", '').strip()
            password = post_info.get("password", '').strip()
            code_mode = post_info.get("code_mode", '').strip() or '0'
            code_mode = int(code_mode)
            try:
                assert name, Exception('名称不能为空')
                assert re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip), Exception('ip 格式不正确！')
                try:
                    ssh_port = int(ssh_port)
                except:
                    raise Exception('ssh端口必须是整数')
                assert ssh_port>0, Exception("ssh端口必须大于0")
                assert not Server.objects.filter(name=name).exists(), Exception('名称和现有的重复！')
                assert not Server.objects.filter(ip=ip, ssh_port=ssh_port).exists(), Exception('IP端口和现有的重复！')
                assert user, Exception('登录用户不能为空！')
                server = Server(name=name, ip=ip,
                                     ssh_port=ssh_port,user=user,password=password,
                                          addtime=int(time.time()),
                                code_mode=code_mode
                                         )
                server.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)


        if action == 'update_server':
            result = {'status': True, 'message': 'success'}
            id = post_info.get("id", '').strip()
            name = post_info.get("name", '').strip()
            ip = post_info.get("ip", '').strip()
            ssh_port = post_info.get("ssh_port", '').strip("/")
            user = post_info.get("user", '').strip()
            password = post_info.get("password", '').strip()
            code_mode = post_info.get("code_mode", '').strip() or '0'
            code_mode = int(code_mode)
            id = int(id)
            try:
                assert Server.objects.filter(id=id).exists(), Exception('服务器已不存在！')
                server = Server.objects.get(id=id)
                assert name, Exception('名称不能为空')
                assert re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip), Exception('ip 格式不正确！')
                try:
                    ssh_port = int(ssh_port)
                except:
                    raise Exception('ssh端口必须是整数')
                assert ssh_port > 0, Exception("ssh端口必须大于0")
                assert not Server.objects.filter(~Q(id=id),name=name).exists(), Exception('名称和现有的重复！')
                assert not Server.objects.filter(~Q(id=id),ip=ip,ssh_port=ssh_port).exists(), Exception('IP端口和现有的重复！')
                assert user, Exception('登录用户不能为空！')

                server.name = name
                server.ip = ip
                server.ssh_port = ssh_port
                server.user = user
                server.password = password
                server.code_mode = code_mode
                server.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'del_server':
            result = {'status': True, 'message': 'success'}
            id = post_info.get('id', ' ')
            try:
                id = int(id)
                server = Server.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '服务器已不存在！'
            else:
                app_servers = set()
                for app in App.objects.all():
                    for i in app.server_ids_1.split(","):
                        try:
                            i = int(i)
                            app_servers.add(i)
                        except:
                            pass
                    for i in app.server_ids_2.split(","):
                        try:
                            i = int(i)
                            app_servers.add(i)
                        except:
                            pass
                    for i in app.server_ids_3.split(","):
                        try:
                            i = int(i)
                            app_servers.add(i)
                        except:
                            pass
                    for i in app.server_ids_4.split(","):
                        try:
                            i = int(i)
                            app_servers.add(i)
                        except:
                            pass

                if id in app_servers:
                    result['status'] = False
                    result['message'] = '当前服务器仍和应用有关联，禁止删除。'
                else:
                    server.delete()
            return json_response(result)

    return render(request, "server_manage.html", locals())




@login_required
@csrf_exempt
def get_gitserver_repos(request):
    # 获取 gitserver 当前所有的仓库
    get_info = request.GET
    id = get_info.get('gitserver_id', '')
    id = int(id)
    _data = {"status":True, 'message':'', 'data': None}
    results = []
    try:
        _ = RepoServer.objects.get(id=id)
        if _.repo_type == 1:
            results = gitrepo.GitLab(_.token, _.server_url).get_all_repos()
        elif _.repo_type == 2:
            results = gitrepo.Gitee(_.token, _.server_url).get_all_repos()
        _data['data'] = results
    except Exception as e:
        _data['status'] = False
        _data['message'] = str(e)
    return json_response(_data)



@login_required
@csrf_exempt
def app_manage(request):
    "应用管理"
    get_info = request.GET
    post_info = request.POST
    action = get_info.get('action', '')
    repo_server_info = {i.id:i for i in RepoServer.objects.all()}
    server_info = {i.id:i for i in Server.objects.all()}

    #apps =
    all_apps = {app.id: app for app in App.objects.all().order_by("-id")}
    user_perms_info = {i.uid: [int(kk) for kk in i.apps.strip().split(",") if int(kk) in all_apps]
                       for i in UserAppPerm.objects.all()}

    if request.method == 'POST':
        if action == 'get_app':
            data = {'status': True, 'message': 'success', 'data': None}
            try:
                id = post_info.get('id', '')
                id = int(id)
                repo = App.objects.get(id=id)
                _ = model_to_dict(repo)
                data['data'] = _
                _['repo_server_detail'] = model_to_dict(repo_server_info[_['repo_server_id']])
                _['all_repo_servers'] = {i:model_to_dict(j) for i,j in repo_server_info.items()}
                _['all_servers'] = {i:model_to_dict(j)  for i,j in server_info.items()}
                _['project'] = model_to_dict(repo.project)
            except:
                data['status'] = False
                data['message'] = '当前应用已不存在'
            return json_response(data)

        if action == 'get_app_list':
            servers = []
            projects = {i.id:i for i in  Project.objects.all()}
            if request.user.username == 'admin' or request.user.is_superuser:
                for i in App.objects.all().order_by("-id"):
                    _i = model_to_dict(i)
                    _i["project"] = model_to_dict(projects[i.proj_id])
                    _i['repo_server_detail'] = model_to_dict(repo_server_info[_i['repo_server_id']])
                    servers.append(_i)
            else:
                for i in App.objects.all().order_by("-id"):
                    if i.id in user_perms_info.get(request.user.id, []) or []:
                        _i = model_to_dict(i)
                        _i["project"] = model_to_dict(projects[i.proj_id])
                        _i['repo_server_detail'] = model_to_dict(repo_server_info[_i['repo_server_id']])
                        servers.append(_i)
            if "sort" in get_info:
                if get_info.get('sort') == 'project_name':
                    servers.sort(key=lambda x:x['project']['name'] + x["name"] )
                else:
                    servers.sort(key=lambda x:x['name'])
            return json_response(servers)

        if action == 'add_app':
            result = {'status': True, 'message': 'success'}
            name = post_info.get("name", '').strip()
            repo_server_id = post_info.get('repo_server_id', '').strip()
            repo_url = post_info.get('repo_git_url', '').strip()
            deploy_to = post_info.get('deploy_to', '').strip()
            branch_name = post_info.get("branch_name", 'master').strip()
            old_version_num = post_info.get('old_version_num', '').strip()

            server_ids_1 = post_info.getlist('server_ids_1',[])
            server_ids_2 = post_info.getlist('server_ids_2',[])
            server_ids_3 = post_info.getlist('server_ids_3',[])
            server_ids_4 = post_info.getlist('server_ids_3', [])

            cmd_before_deploy_1 = post_info.get("cmd_before_deploy_1", '')
            cmd_build_app_1 = post_info.get('cmd_build_app_1', '')
            cmd_start_app_1 = post_info.get("cmd_start_app_1", '')
            success_after_deploy_1 = post_info.get("success_after_deploy_1", '')

            cmd_before_deploy_2 = post_info.get("cmd_before_deploy_2", '')
            cmd_build_app_2 = post_info.get('cmd_build_app_2', '')
            cmd_start_app_2 = post_info.get("cmd_start_app_2", '')
            success_after_deploy_2 = post_info.get("success_after_deploy_2", '')

            cmd_before_deploy_3 = post_info.get("cmd_before_deploy_3", '')
            cmd_build_app_3 = post_info.get('cmd_build_app_3', '')
            cmd_start_app_3 = post_info.get("cmd_start_app_3", '')
            success_after_deploy_3 = post_info.get("success_after_deploy_3", '')

            cmd_before_deploy_4 = post_info.get("cmd_before_deploy_4", '')
            cmd_build_app_4 = post_info.get('cmd_build_app_4', '')
            cmd_start_app_4 = post_info.get("cmd_start_app_4", '')
            success_after_deploy_4 = post_info.get("success_after_deploy_4", '')

            code_tar_gz_path = post_info.get('code_tar_gz_path', '').strip()
            # 项目id
            proj_id = post_info.get('proj_id', '') or '1'
            proj_id = int(proj_id)
            projects = {i.id: i for i in Project.objects.all()}
            if proj_id not in projects:
                proj_id = 1
            try:
                assert name, Exception('名称不能为空')
                assert branch_name, Exception('分支不能为空')
                assert not App.objects.filter(name=name).exists(), Exception('名称和现有的重复！')
                assert deploy_to.startswith("/") and ' ' not in deploy_to, Exception('目录必须是绝对路径且不含空格')
                try:
                    old_version_num = int(old_version_num)
                    assert 10>= old_version_num >=2
                except:
                    raise Exception('历史代码版本数量必须大于等于2')
                try:
                    repo_server_id = int(repo_server_id)
                    assert repo_server_id in repo_server_info
                except:
                    raise Exception('请重新选择Git服务器')
                try:
                    assert repo_url
                    repo_url,repo_id = repo_url.split("|")
                    repo_id = int(repo_id)
                except:
                    raise Exception('请选择Git仓库')
                if code_tar_gz_path:
                    try:
                        assert code_tar_gz_path.startswith("http")
                    except:
                        raise Exception('自定义代码源格式错误')
                server_ids_1 = [str(i) for i in server_ids_1 if int(i) in server_info]
                server_ids_2 = [str(i) for i in server_ids_2 if int(i) in server_info]
                server_ids_3 = [str(i) for i in server_ids_3 if int(i) in server_info]
                server_ids_4 = [str(i) for i in server_ids_4 if int(i) in server_info]
                _b = server_ids_1 + server_ids_2 + server_ids_3 + server_ids_4
                _b.sort()
                for _a, _c in itertools.groupby(_b):
                    if len([__c for __c in _c]) >= 2:
                        raise Exception('各环境服务器不能重复')

                app = App(name=name, repo_server_id=repo_server_id, repo_git_url = repo_url,
                          deploy_to = deploy_to, old_version_num=old_version_num,
                          server_ids_1=','.join(server_ids_1),
                          server_ids_2=','.join(server_ids_2),
                          server_ids_3=','.join(server_ids_3),
                          server_ids_4=','.join(server_ids_4),
                          cmd_before_deploy_1 = cmd_before_deploy_1,
                          cmd_start_app_1 = cmd_start_app_1,
                          cmd_build_app_1= cmd_build_app_1,
                          success_after_deploy_1 = success_after_deploy_1,
                          cmd_before_deploy_2=cmd_before_deploy_2,
                          cmd_start_app_2=cmd_start_app_2,
                          cmd_build_app_2=cmd_build_app_2,
                          success_after_deploy_2=success_after_deploy_2,
                          cmd_before_deploy_3=cmd_before_deploy_3,
                          cmd_start_app_3=cmd_start_app_3,
                          cmd_build_app_3=cmd_build_app_3,
                          success_after_deploy_3=success_after_deploy_3,
                          cmd_before_deploy_4=cmd_before_deploy_4,
                          cmd_start_app_4=cmd_start_app_4,
                          cmd_build_app_4=cmd_build_app_4,
                          success_after_deploy_4=success_after_deploy_4,
                          addtime=int(time.time()),
                          code_tar_gz_path = code_tar_gz_path,
                          repo_id=repo_id,
                          branch_name = branch_name, proj_id=proj_id
                                )
                app.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'update_app':
            result = {'status': True, 'message': 'success'}
            id = post_info.get('id', '').strip()
            name = post_info.get("name", '').strip()
            repo_server_id = post_info.get('repo_server_id', '').strip()
            repo_url = post_info.get('repo_git_url', '').strip()

            branch_name = post_info.get("branch_name", 'master').strip()
            deploy_to = post_info.get('deploy_to', '').strip()
            old_version_num = post_info.get('old_version_num', '').strip()

            server_ids_1 = post_info.getlist('server_ids_1', [])
            server_ids_2 = post_info.getlist('server_ids_2', [])
            server_ids_3 = post_info.getlist('server_ids_3', [])
            server_ids_4 = post_info.getlist('server_ids_3', [])

            cmd_before_deploy_1 = post_info.get("cmd_before_deploy_1", '')
            cmd_build_app_1 = post_info.get('cmd_build_app_1', '')
            cmd_start_app_1 = post_info.get("cmd_start_app_1", '')
            success_after_deploy_1 = post_info.get("success_after_deploy_1", '')

            cmd_before_deploy_2 = post_info.get("cmd_before_deploy_2", '')
            cmd_build_app_2 = post_info.get('cmd_build_app_2', '')
            cmd_start_app_2 = post_info.get("cmd_start_app_2", '')
            success_after_deploy_2 = post_info.get("success_after_deploy_2", '')

            cmd_before_deploy_3 = post_info.get("cmd_before_deploy_3", '')
            cmd_build_app_3 = post_info.get('cmd_build_app_3', '')
            cmd_start_app_3 = post_info.get("cmd_start_app_3", '')
            success_after_deploy_3 = post_info.get("success_after_deploy_3", '')

            cmd_before_deploy_4 = post_info.get("cmd_before_deploy_4", '')
            cmd_build_app_4 = post_info.get('cmd_build_app_4', '')
            cmd_start_app_4 = post_info.get("cmd_start_app_4", '')
            success_after_deploy_4 = post_info.get("success_after_deploy_4", '')

            code_tar_gz_path = post_info.get('code_tar_gz_path', '').strip()
            id = int(id)
            id = int(id)
            # 项目id
            proj_id = post_info.get('proj_id', '') or '1'
            proj_id = int(proj_id)
            projects = {i.id: i for i in Project.objects.all()}
            if proj_id not in projects:
                proj_id = 1
            try:
                assert App.objects.filter(id=id).exists(), Exception('应用已不存在！')
                app = App.objects.get(id=id)
                assert name, Exception('名称不能为空')
                assert not App.objects.filter(~Q(id=id), name=name).exists(), Exception('名称和现有的重复！')
                assert deploy_to.startswith("/") and ' ' not in deploy_to, Exception('目录必须是绝对路径且不含空格')
                try:
                    old_version_num = int(old_version_num)
                    assert 10 >= old_version_num >= 2
                except:
                    raise Exception('历史代码版本数量必须大于等于2')
                try:
                    repo_server_id = int(repo_server_id)
                    assert repo_server_id in repo_server_info
                except:
                    raise Exception('请重新选择Git服务器')
                try:
                    assert repo_url
                    repo_url, repo_id = repo_url.split("|")
                    repo_id = int(repo_id)
                except:
                    raise Exception('请选择Git仓库')
                if code_tar_gz_path:
                    try:
                        assert code_tar_gz_path.startswith("http")
                    except:
                        raise Exception('自定义代码源格式错误')
                server_ids_1 = [str(i) for i in server_ids_1 if int(i) in server_info]
                server_ids_2 = [str(i) for i in server_ids_2 if int(i) in server_info]
                server_ids_3 = [str(i) for i in server_ids_3 if int(i) in server_info]
                server_ids_4 = [str(i) for i in server_ids_4 if int(i) in server_info]
                _b = server_ids_1 + server_ids_2 + server_ids_3 + server_ids_4
                _b.sort()
                for _a, _c in itertools.groupby(_b):
                    if len([__c for __c in _c]) >= 2:
                        raise Exception('各环境服务器不能重复')

                app.name = name
                app.repo_server_id = repo_server_id
                app.repo_git_url = repo_url
                app.deploy_to = deploy_to
                app.server_ids_1 = ','.join(server_ids_1)
                app.server_ids_2 = ','.join(server_ids_2)
                app.server_ids_3 = ','.join(server_ids_3)
                app.server_ids_4 = ','.join(server_ids_4)

                app.cmd_before_deploy_1 = cmd_before_deploy_1
                app.cmd_start_app_1 = cmd_start_app_1
                app.success_after_deploy_1 = success_after_deploy_1
                app.cmd_build_app_1 = cmd_build_app_1

                app.cmd_before_deploy_2 = cmd_before_deploy_2
                app.cmd_start_app_2 = cmd_start_app_2
                app.success_after_deploy_2 = success_after_deploy_2
                app.cmd_build_app_2 = cmd_build_app_2

                app.cmd_before_deploy_3 = cmd_before_deploy_3
                app.cmd_start_app_3 = cmd_start_app_3
                app.success_after_deploy_3 = success_after_deploy_3
                app.cmd_build_app_3 = cmd_build_app_3

                app.cmd_before_deploy_4 = cmd_before_deploy_4
                app.cmd_start_app_4 = cmd_start_app_4
                app.success_after_deploy_4 = success_after_deploy_4
                app.cmd_build_app_4 = cmd_build_app_4

                app.code_tar_gz_path = code_tar_gz_path
                app.repo_id = repo_id
                app.branch_name = branch_name
                app.proj_id = proj_id
                app.save()

            except Exception as  e:
                result['status'] = False
                result['message'] = str(e)
            return json_response(result)

        if action == 'del_app':
            result = {'status': True, 'message': 'success'}
            id = post_info.get('id', ' ')
            try:
                id = int(id)
                app = App.objects.get(id=id)
            except:
                result['status'] = False
                result['message'] = '该应用已不存在！'
            else:
                app.delete()
            return json_response(result)

    return render(request, "app_manage.html", locals())



@login_required
def pub(request):
    return render(request, 'pub.html', locals())


@login_required
def pub_log(request):
    return render(request, 'pub_log.html', locals())



@login_required
@csrf_exempt
def get_recent_commit_log(request):
    "获取仓库的的Commit日志"
    post_info = request.POST
    repo_server_id = post_info.get("repo_server_id")
    app_id = post_info.get("app_id", '')
    repo_server_id = int(repo_server_id)
    git_url = post_info.get("git_url", '')
    reposerver_info = {i.id:i for i in  RepoServer.objects.all()}
    app = App.objects.get(id=int(app_id))
    data = {'status':True, 'message': 'success', 'data': []}
    try:
        assert repo_server_id in reposerver_info, Exception("异常， 该Git服务器已被删除！")
        _ = reposerver_info[repo_server_id]
        id = app.repo_id
        versions = []
        if _.repo_type == 1:
            versions = gitrepo.GitLab(_.token, _.server_url).get_recent_versions(id, app.branch_name)
        elif _.repo_type == 2:
            versions = gitrepo.Gitee(_.token, _.server_url).get_recent_versions(id, app.branch_name)
        data['data'] = versions
    except Exception as e :
        data['status'] = False
        data['message'] = str(e)

    return json_response(data)





@login_required
@csrf_exempt
def pub_(request):
    "发布代码"
    post_info = request.POST
    app_id = post_info.get("app_id")
    version = post_info.get('version', '').strip()
    version_meta = post_info.get("version-meta",'').replace("\xa0",'')
    environ_type = post_info.get('environment')
    environ_type = int(environ_type)
    reason = post_info.get('reason','').strip()
    data = {'status': True, "message":'', 'data':None}
    try:
        try:
            app_id = int(app_id)
            assert app_id > 0
        except:
            raise Exception("请选择应用")
        assert App.objects.filter(id=app_id).exists(), Exception('应用不存在！ 请重新选择')
        assert version, Exception('请选择代码版本')
        assert reason, Exception('请填写操作原因')
        app = App.objects.get(id=app_id)
        repo_url = app.repo_git_url
        app_dir = app.deploy_to
        remain_num = app.old_version_num
        if environ_type == 1:
            cmd_before_deploy = app.cmd_before_deploy_1
            cmd_build_app = app.cmd_build_app_1
            cmd_start_app = app.cmd_start_app_1
            success_after_deploy = app.success_after_deploy_1
            machines = [{'host': i.ip,
                              'port': i.ssh_port,
                              'user': i.user,
                              'passwd': i.password,
                              "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                       [int(i) for i in
                                                                                        app.server_ids_1.split(",")
                                                                                        if i])]
        elif environ_type == 2:
            cmd_before_deploy = app.cmd_before_deploy_2
            cmd_build_app = app.cmd_build_app_2
            cmd_start_app = app.cmd_start_app_2
            success_after_deploy = app.success_after_deploy_2
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_2.split(",")
                                                                                   if i])]
        elif environ_type == 3:
            cmd_before_deploy = app.cmd_before_deploy_3
            cmd_build_app = app.cmd_build_app_3
            cmd_start_app = app.cmd_start_app_3
            success_after_deploy = app.success_after_deploy_3
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_3.split(",")
                                                                                   if i])]
        else:
            cmd_before_deploy = app.cmd_before_deploy_4
            cmd_build_app = app.cmd_build_app_4
            cmd_start_app = app.cmd_start_app_4
            success_after_deploy = app.success_after_deploy_4
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_4.split(",")
                                                                                   if i])]


        assert not  PubLog.objects.filter(app_id=app_id, status__in=[1,2], environ_type=environ_type).exists(), \
        Exception('该应用尚有发布任务未完成,暂时不允许提交发布')

        publog = PubLog(ope_user_name=request.user.username,
                        target_version=version,
                        target_version_meta=version_meta,
                        app_id=app_id,
                        environ_type=environ_type,
                        task_id='',
                        status=1,
                        status_uptime=int(time.time()),
                        reason=reason,
                        operatetime=int(time.time()))
        publog.save()
        def sync_fun(task_id, status, log, mysql_host=settings.DATABASES['default']['HOST'],
                     mysql_port = int(settings.DATABASES['default']['PORT']),
                     mysql_db = settings.DATABASES['default']['NAME'],
                     mysql_user = settings.DATABASES['default']['USER'],
                     mysql_passwd= settings.DATABASES['default']['PASSWORD']):
            import MySQLdb, re, time
            conn = MySQLdb.connect(host=mysql_host, port=mysql_port,
                                   user=mysql_user, passwd=mysql_passwd,
                                   db=mysql_db,
                                   charset='utf8mb4')
            cursor = conn.cursor()
            progress = 0
            progress = status
            if abs(progress) != 100:
                _ = re.findall(r"进度(\d{1,3})%", log)
                if _:
                    progress = int(_[-1])
            if 100> progress>0:
                status = 2
            if progress == 100:
                status = 3
            if progress == -100:
                status = 4
            cursor.execute("update  cap_pub_log set progress = %s, status=%s,status_uptime=%s , task_log=%s  where task_id=%s",(
                progress, status,int(time.time()),  log, task_id
            ))
            conn.commit()
            cursor.close()
            conn.close()

        task_args = (settings.WORK_PATH, repo_url)
        task_kwargs = {"version_info": version,
                               'remote_machine_info': machines,
                               'app_path': app_dir,
                               'cmd_before_deploy': cmd_before_deploy,
                               'cmd_build_app': cmd_build_app,
                               'cmd_start_app': cmd_start_app,
                               'success_after_deploy': success_after_deploy,
                               'remain_num': int(remain_num),
                               'code_tar_gz_path': app.code_tar_gz_path.strip() or None,
                               }
        #print(task_args, task_kwargs)
        task_id = process_task.run_task(pub_code.pub_code, task_args,
                              task_kwargs, sync_fun=sync_fun)

        publog.task_id = task_id
        publog.save()
        data['message'] = '发布任务已提交'
        data['data'] = publog.id
    except Exception as e :
        data['status'] = False
        data['message'] = str(e)


    return json_response(data)


@login_required
@csrf_exempt
def rollback_(request):
    post_info = request.POST
    app_id = post_info.get("app_id")
    version = post_info.get('version', '').strip()
    version_meta = post_info.get("version-meta", '').replace("\xa0", '')
    environ_type = post_info.get('environment')
    environ_type = int(environ_type)
    reason = request.user.username + '回滚代码'
    data = {'status': True, "message": '', 'data': None}
    try:
        try:
            app_id = int(app_id)
            assert app_id > 0
        except:
            raise Exception("请选择应用")
        assert App.objects.filter(id=app_id).exists(), Exception('应用不存在！ 请重新选择')
        assert version, Exception('请选择代码版本')
        assert reason, Exception('请填写操作原因')
        app = App.objects.get(id=app_id)
        repo_url = app.repo_git_url
        app_dir = app.deploy_to
        remain_num = app.old_version_num
        if environ_type == 1:
            cmd_before_deploy = app.cmd_before_deploy_1
            cmd_build_app = app.cmd_build_app_1
            cmd_start_app = app.cmd_start_app_1
            success_after_deploy = app.success_after_deploy_1
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_1.split(",")
                                                                                   if i])]
        elif environ_type == 2:
            cmd_before_deploy = app.cmd_before_deploy_2
            cmd_build_app = app.cmd_build_app_2
            cmd_start_app = app.cmd_start_app_2
            success_after_deploy = app.success_after_deploy_2
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_2.split(",")
                                                                                   if i])]
        elif environ_type == 3:
            cmd_before_deploy = app.cmd_before_deploy_3
            cmd_build_app = app.cmd_build_app_3
            cmd_start_app = app.cmd_start_app_3
            success_after_deploy = app.success_after_deploy_3
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_3.split(",")
                                                                                   if i])]
        else:
            cmd_before_deploy = app.cmd_before_deploy_4
            cmd_build_app = app.cmd_build_app_4
            cmd_start_app = app.cmd_start_app_4
            success_after_deploy = app.success_after_deploy_4
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_4.split(",")
                                                                                   if i])]

        assert not PubLog.objects.filter(app_id=app_id, status__in=[1, 2], environ_type=environ_type).exists(), \
            Exception('该应用尚有发布任务未完成,暂时不允许本操作！')

        publog = PubLog(ope_user_name=request.user.username,
                        target_version=version.split("-")[1],
                        target_version_meta=version_meta,
                        app_id=app_id,
                        environ_type=environ_type,
                        task_id='',
                        status=1,
                        status_uptime=int(time.time()),
                        reason=reason,
                        operatetime=int(time.time()),
                        pub_type=1)
        publog.save()

        def sync_fun(task_id, status, log, mysql_host=settings.DATABASES['default']['HOST'],
                     mysql_port=int(settings.DATABASES['default']['PORT']),
                     mysql_db=settings.DATABASES['default']['NAME'],
                     mysql_user=settings.DATABASES['default']['USER'],
                     mysql_passwd=settings.DATABASES['default']['PASSWORD']):
            import MySQLdb, re, time
            conn = MySQLdb.connect(host=mysql_host, port=mysql_port,
                                   user=mysql_user, passwd=mysql_passwd,
                                   db=mysql_db,
                                   charset='utf8mb4')
            cursor = conn.cursor()
            progress = 0
            progress = status
            if abs(progress) != 100:
                _ = re.findall(r"进度(\d{1,3})%", log)
                if _:
                    progress = int(_[-1])
            if 100 > progress > 0:
                status = 2
            if progress == 100:
                status = 3
            if progress == -100:
                status = 4
            cursor.execute(
                "update  cap_pub_log set progress = %s, status=%s,status_uptime=%s , task_log=%s  where task_id=%s", (
                    progress, status, int(time.time()), log, task_id
                ))
            conn.commit()
            cursor.close()
            conn.close()

        task_kwargs = {"version_info": version,
                       'remote_machine_info': machines,
                       'app_path': app_dir,
                       'cmd_start_app': cmd_start_app,
                       'success_after_deploy': success_after_deploy,
                       }
        # print(task_args, task_kwargs)
        task_id = process_task.run_task(pub_code.rollback_code, (),
                                        task_kwargs, sync_fun=sync_fun)

        publog.task_id = task_id
        publog.save()
        data['message'] = '回滚任务已提交'
        data['data'] = publog.id
    except Exception as e:
        data['status'] = False
        data['message'] = str(e)

    return json_response(data)



@login_required
@csrf_exempt
def get_app_current_status(request):
    # 获取某应用当前状态
    post_info = request.POST
    app_id = post_info.get("app_id")
    environ_type = post_info.get('environment')
    environ_type = int(environ_type)
    result = {'status': True, "message": 'success', 'data': None }
    try:
        try:
            app_id = int(app_id)
            assert app_id > 0
        except:
            raise Exception("请选择应用")
        assert App.objects.filter(id=app_id).exists(), Exception('应用不存在！ 请重新选择')
        recent_log = PubLog.objects.filter(app_id=app_id, environ_type=environ_type).order_by("-id")[:300]
        recent_log_dict = {i.target_version: i.target_version_meta for i in recent_log}
        app = App.objects.get(id=app_id)
        app_dir = app.deploy_to
        if environ_type == 1:
            cmd_start_app = app.cmd_start_app_1
            success_after_deploy = app.success_after_deploy_1
            machines = [{'host': i.ip,
                              'port': i.ssh_port,
                              'user': i.user,
                              'passwd': i.password,
                              "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                       [int(i) for i in
                                                                                        app.server_ids_1.split(",")
                                                                                        if i])]
        elif environ_type == 2:
            cmd_start_app = app.cmd_start_app_2
            success_after_deploy = app.success_after_deploy_2
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_2.split(",")
                                                                                   if i])]
        elif environ_type == 3:
            cmd_start_app = app.cmd_start_app_3
            success_after_deploy = app.success_after_deploy_3
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_3.split(",")
                                                                                   if i])]
        else:
            cmd_start_app = app.cmd_start_app_4
            success_after_deploy = app.success_after_deploy_4
            machines = [{'host': i.ip,
                         'port': i.ssh_port,
                         'user': i.user,
                         'passwd': i.password,
                         "code_mode": i.code_mode} for i in Server.objects.filter(id__in=
                                                                                  [int(i) for i in
                                                                                   app.server_ids_4.split(",")
                                                                                   if i])]

        def get_versions(args):
            host, port, user,passwd,app_dir = args
            res = ssh_command(host, port,user, passwd, command='mkdir -p %s && cd %s &&ls -l' % (app_dir, app_dir) ,
                        timeout=3)
            return host, port,res[0], res[1]
        pool = Pool(40)
        ress = pool.map(get_versions,[(i['host'], i['port'], i['user'], i['passwd'], app_dir)  for i in machines])
        pool.close()
        _result = {'versions':[], 'detail':[]}
        result['data'] = _result
        _versions = {}
        for h,p,i,j in ress:
            if i == False:
                _result['detail'].append({"host":h,'port':p,'status':i,"message":j,'data':[],
                                          'current_code_name':'','current_version': '',
                                          'current_version_meta': ''})
            else:
                codes = []
                current_code_name = ''
                current_version = ''
                current_version_meta = ''
                for line in j.splitlines():
                    _ = re.search("\d{14}\-\w{8}",line)
                    if _:
                        _v = _.group()
                        if 'current' in line and _:
                            current_code_name = _v
                            current_version = _v.split("-")[1]
                            current_version_meta = recent_log_dict.get(current_version, '')
                        else:
                            codes.append(_v)
                kk = []
                codes.sort()
                for k in codes:
                    _1,ver = k.split("-")
                    time_stamp = datetime.datetime.strptime(_1[:14],'%Y%m%d%H%M%S').timestamp()
                    if ver in recent_log_dict:
                        kk.append([ver, time_stamp, recent_log_dict[ver], k])
                for k in set(codes):
                    _1, ver = k.split("-")
                    if ver in recent_log_dict:
                        _versions.setdefault((k, ver, recent_log_dict[ver]), 0)
                        _versions[(k, ver, recent_log_dict[ver])] += 1
                _result['detail'].append({"host": h, 'port': p, 'status': i, "message": 'success',
                               'data': kk, 'current_code_name': current_code_name,
                                          'current_version': current_version,
                                          'current_version_meta': current_version_meta})
        items = list(_versions.items())
        items.sort(key=lambda x:x[0][0])
        _result['versions'] = [{'ver':i[1],
                                'code_name': i[0],
                                'ver_meta':i[2]} for i,j in items if j == len(machines) ]

    except Exception as e:
        print(str(e))
        result['status'] = False
        result['message'] = str(e)
    return json_response(result)



@login_required
@csrf_exempt
def kill_pubtask(request):
    # 强制终止发布任务
    post_info = request.POST
    id = post_info.get("id", '')
    id = int(id)
    publog = PubLog.objects.get(id=id)
    result = {"status": True, 'message':'success', 'data':None}
    try:
        task_id = publog.task_id
        if process_task.is_running(task_id):
            process_task.kill(task_id)
        if publog.status in (3, 4):
            raise Exception("当前发布任务已结束，无需强制结束。")
        else:
            publog.status = 4
            publog.status_uptime = int(time.time())
            publog.task_log += "\n[%s] 当前发布任务已被强制结束\n" % datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
            publog.save()
    except Exception as e:
        result['status'] = False
        result['message'] = str(e)

    return json_response(result)



@login_required
@csrf_exempt
def get_publog_detail(request):
    "获取发布的详细信息"
    post_info = request.POST
    id = post_info.get("id", '')
    id = int(id)
    log = PubLog.objects.get(id=id)
    result = model_to_dict(log)
    result['status_cn'] = log.status_cn
    return json_response(result)


@login_required
@csrf_exempt
def get_testenviron_publog(request):
    "获取某版本环境2发布记录"
    post_info = request.POST
    id = post_info.get("app_id", '')
    id = int(id)
    version = post_info.get('version', '')
    try:
        log = PubLog.objects.filter(app_id=id, target_version=version, environ_type=2, status=3)[0]
        result = model_to_dict(log)
        #result['status_cn'] = log.status_cn
        return json_response(result)
    except:
        return json_response(None)


@login_required
@csrf_exempt
def get_recent_publog(request):
    post_info = request.POST
    page = post_info.get("page", '1')
    page = int(page)
    num = post_info.get('num', '20')
    num = int(num)
    apps = {i.id:i for i in App.objects.all()}
    proj_id = post_info.get("proj_id", '')
    app_id = post_info.get("app_id", '')
    info = []
    if app_id:
        info = PubLog.objects.filter(app_id=int(app_id)).order_by("-id")
    if info == [] and proj_id:
        info = PubLog.objects.filter(app_id__in=[i.id for i in
                                                 App.objects.filter(proj_id=int(proj_id))]).order_by("-id")
    if info == []:
        info = PubLog.objects.all().order_by("-id")
    print(num, page)
    paginator = Paginator(info, per_page=num)
    try:
        _info = paginator.page(page)
    except InvalidPage:
        _info = []
    info = []
    for i in _info:
        _dict = model_to_dict(i)
        _dict['addtime'] = time.mktime(i.operatetime.timetuple())
        #time.
        if i.app_id in apps:
            _dict['app_info'] = model_to_dict(apps[i.app_id])
        else:
            _dict['app_info'] = None
        del _dict['task_log']
        _dict['status_cn'] = i.status_cn
        info.append(_dict)
    page_range = list(range(max(1, page - 6), min(paginator.num_pages, page + 6) + 1))
    return json_response({"total_page": paginator.num_pages,
                                    'total_count': paginator.count,
                                    'page': page,
                                    'page_range': page_range,
                                    'data': info
                                    })



@login_required
def advantage_tools(request):
    WORK_PATH = settings.WORK_PATH
    scripts_path = os.path.join(WORK_PATH,'scripts')
    return render(request, 'advantage.html', locals())