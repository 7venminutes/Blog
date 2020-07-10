# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/02
Desc: 用户管理视图层，处理user_management.html发送过来的与用户管理有关的请求
TODO[baixu]: 新建用户和删除用户的业务逻辑在设计上有不妥之处
"""
import json
import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

if '../' not in sys.path:
    sys.path.append('../')

from database.db_helpers import table_user, table_access
from common.address_transfer import resolve_path_to_actual_path
from WebService.FilesCube.FilesCube_views import validate_identity, who_is_sending_request


def user_manage(request):
    """
    返回管理界面，管理界面里面不仅仅只有用户管理、还有卷管理的入口
    :param request: GET
    :return: render(request, 'user_management.html', locals())
    """
    # 身份验证，系统管理员才能进入该页面
    if not validate_identity(request):
        return HttpResponseRedirect('/filescube/index/')
    user = who_is_sending_request(request)
    if not user['is_sys_admin']:
        return HttpResponseRedirect('/filescube/index/')
    else:
        return render(request, 'FilesCube/user_management.html', locals())


def get_user_list(request):
    """
    返回用户表中所有用户的相关数据
    :return: json数据，{'state':...,'details':...}
        'details'中为user_list或详细的错误信息
        'state'为success或failed
    """
    # 身份验证，系统管理员才能获取全部用户列表
    if not validate_identity(request):
        return HttpResponseRedirect('/filescube/index/')
    user = who_is_sending_request(request)
    if not user['is_sys_admin']:
        return HttpResponseRedirect('/filescube/index/')
    user_list = table_user.get_user_info('ID', 'sys_admin', 'root_dir')
    return HttpResponse(json.dumps({'state': 'success', 'details': user_list}))


def new_user(request):
    """
    新增用户
    :param request: POST
    request.POST: {'id':...,'password':...,'root_dir':...,'size':...}
    :return: json数据, {'state':...,'details':...}
    """
    user_id = str(request.POST['id'])
    password = str(request.POST['password'])
    root_dir = str(request.POST['root_dir'])
    size = str(request.POST['size'])
    # 检验用户名是否冲突
    curr_user_list = table_user.get_all_user_info()
    user_exist = False
    for user in curr_user_list:
        if user_id == user['user_ID']:
            user_exist = True
            break
    if user_exist:
        message_to_return = {'state': 'failed', 'details': '用户名已存在'}
    else:
        # root_dir是否存在？
        print(root_dir)
        root_dir_exist = resolve_path_to_actual_path(root_dir)['state']
        if not root_dir_exist:
            message_to_return = {'state': 'failed', 'details': '传入的用户根目录无法解析'}
        else:
            table_user.add_user(user_id, password, root_dir)
            message_to_return = {'state': 'success', 'details': '新用户添加成功'}
    return HttpResponse(json.dumps(message_to_return))


def remove_user(request):
    """
    删除用户，仅将用户表中数据删除
    :param request: POST
    request.POST:{'user_name':...}
    :return: json数据 {'state':...,'details':...}
    """
    user_name = str(request.POST['user_name'])
    message_to_return = table_user.remove_user(user_name)
    message_to_return_2 = table_access.remove_access_by_id(user_name)
    if message_to_return_2['state'] == 'failed':
        message_to_return = {'state': 'failed',
                             'details': '用户删除成功，关联权限删除失败，可去权限管理处清理冗余权限'}
    return HttpResponse(json.dumps(message_to_return))


def modify_root_dir_of_user(request):
    """
    修改用户主目录
    :param request: POST
    request.POST:{'user_id':...,'original_dir':...,'new_dir':...}
    :return: json数据 {'state':...,'details':...}
    """
    print('hhhh')
    user_id = str(request.POST['user_id'])
    original_dir = str(request.POST['original_dir'])
    new_dir = str(request.POST['new_dir'])
    # TODO[baixu]: 修改用户主目录
    return HttpResponse(json.dumps({'state': 'failed', 'details': '没写完呢，改什么主目录'}))
