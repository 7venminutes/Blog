# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: hfs主界面的视图层
"""

# TODO[baixu] request.session中['access']与['access_list']存的是一个东西，查看这方面的代码逻辑，将其合并

import platform
import sys
import traceback

from django.http import HttpResponseRedirect
from django.shortcuts import render

if '../' not in sys.path:
    sys.path.append('../')

from database.db_helpers import table_access, table_user

sys_str = platform.system()


def index(request):
    """
    url重定向
    :param request: 不重要
    :return: HttpResponseRedirect('/filescube/index/')
    """
    return HttpResponseRedirect('/filescube/index/', request)


def validate_identity(request):
    """
    根据request.session['auth']判断用户是否登录
    :param request: GET or POST
    :return: BOOL
    """
    is_auth = True
    try:
        if not request.session['auth']:
            request.session.flush()
            is_auth = False
    except KeyError:
        request.session.flush()
        is_auth = False
    return is_auth


def who_is_sending_request(request):
    """
    返回发送该request的用户的基本信息，若发送请求的为匿名用户，则抛出异常
    故使用该函数之前先调用identity_validation，确认用户有身份之后再调用该函数
    :param request: GET or POST
    :return: {'username':...,'is_sys_admin':BOOL,'root_dir':...}
    """
    try:
        username = request.session['username']
        is_sys_admin = request.session['sys_admin']
        root_dir = request.session['root_dir']
    except KeyError as error:
        raise Exception("键值异常，request.session中没有该键值")
    return {'username': username, 'is_sys_admin': is_sys_admin, 'root_dir': root_dir}


def authentication(request):
    """
    登陆界面所对应的验证用户名密码的函数，验证无误后相关信息存入session，跳转到hfs主界面
    :param request: POST
    request.POST={'username':...,'passwd':...}
    :return: 渲染后的登陆界面，或将请求重定向至主页面的路由进行处理
    """
    err_info = []
    try:
        if request.method == 'POST':
            # print request.POST['username'] + request.POST['passwd']
            auth_info = table_user.validation_for_login(request.POST['username'], request.POST['passwd'])
            print(auth_info)
            if auth_info['result']:
                print(1)
                request.session['auth'] = True
                request.session['sys_admin'] = auth_info['sys_admin']
                request.session['username'] = request.POST['username']
                request.session['root_dir'] = auth_info['root_dir']
                request.session['access'] = table_access.get_access_list_by_id(request.POST['username'])
                return HttpResponseRedirect('/filescube/index/')
            else:
                print(2)
                err_info = "用户名密码错误！"
                request.session['auth'] = False
                return render(request, 'FilesCube/login.html', {'err_info': err_info})
        else:
            return render(request, 'FilesCube/login.html', locals())
    except Exception as error_msg:
        request.session.clear()
        print(traceback.format_exc())
        err_info.append(str(error_msg))
        return render(request, 'FilesCube/login.html', locals())


def login(request):
    """
    返回登陆界面
    :param request: GET
    :return: 渲染后的登陆界面login.html
    """
    try:
        return render(request, 'FilesCube/login.html', locals())
    except Exception as error_msg:
        print(error_msg)
        print(traceback.format_exc())
        return render(request, 'FilesCube/login.html', locals())


def logout(request):
    """
    退出登录，清除session
    :param request: GET
    :return: 登录界面
    """
    try:
        request.session.flush()
    except Exception as error_msg:
        print(str(error_msg))
    return HttpResponseRedirect('/filescube/authentication/')
