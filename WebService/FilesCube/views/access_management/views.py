# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-08
Desc: 权限管理模块的视图层
"""
import json
import os
import traceback

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
import pymysql

from common.key_checker import check_if_have_this_key
from common import address_helper, address_transfer
from const_var import DB_NAME, DATABASE_USER, DATABASE_PWD, DATABASE_PORT, DATABASE_HOST
from database.db_helpers import table_access, db_helper, table_user
from WebService.FilesCube.FilesCube_views import validate_identity, who_is_sending_request
from WebService.FilesCube.views.access_management.access_query import get_access_under_path


# Create your views here.
def access_manage(request):
    """
    返回权限管理界面的主界面
    :param request: GET
    :return: render(request, 'access_management.html')
    """
    # 身份验证，已登陆用户才能访问该界面
    if not validate_identity(request):
        return HttpResponseRedirect('/filescube/index/')
    user_list = table_user.get_all_user_info()
    if not check_if_have_this_key(request.session, 'username'):
        raise KeyError('session中缺少username字段')
    access_list = table_access.get_access_list_by_id(request.session['username'])
    admin_access_list = []
    for access_record in access_list:
        if access_record['admin']:
            admin_access_list.append(access_record)
    return render(request, 'FilesCube/access_management.html',
                  {'request': request, 'user_list': user_list, 'admin_access_list': admin_access_list})


def add_access_record(request):
    """
    增加一条权限记录
    :param request: POST
    request.POST = {user_id, path, read, new, download, remove, modify, admin, opt}
    request.session['username']
    :return: {'state':...,'details':...}
    """
    try:
        user_id = str(request.POST['user_id'])
        path = str(request.POST['path'])
        read = request.POST['read'] == 'true'
        new = request.POST['new'] == 'true'
        download = request.POST['download'] == 'true'
        remove = request.POST['remove'] == 'true'
        modify = request.POST['modify'] == 'true'
        admin = request.POST['admin'] == 'true'
        opt = str(request.POST['opt'])
    except KeyError as error_msg:
        print(error_msg)
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'state': 'failed', 'details': 'POST参数错误'}))
    if not validate_identity(request):
        state = 'failed'
        details = '未登录'
    else:
        if not check_if_have_this_key(request.session, 'username'):
            raise KeyError('session 中缺少字段username')
        if not check_if_have_this_key(request.session, 'sys_admin'):
            raise KeyError('session 中缺少字段sys_admin')
        # 查询该用户是否能在该路径下赋予他人权限
        access_list = table_access.get_access_list_by_id(request.session['username'])
        if not db_helper.lookup_access_in_the_list(path, 'admin', access_list) and not request.session['sys_admin']:
            state = 'failed'
            details = '用户无权限在此路径下增加权限'
        elif not table_user.if_user_exists(user_id):
            state = 'failed'
            details = '请检查新增权限记录中的用户名，用户不存在'
        elif not address_transfer.resolve_path_to_actual_path(path)['state']:
            state = 'failed'
            details = '您不能为不存在的路径赋予权限'
        else:
            print(read)
            table_access.modify_some_access(user_id, path, read,
                                            new, download, remove, modify, admin, opt)
            state = 'success'
            details = '成功增加一条权限记录'
    return HttpResponse(json.dumps({'state': state, 'details': details}))


def get_access_list_can_be_managed(request):
    """
    展示该用户在该路径下可管理的权限的列表
    :param request: POST
    request.POST = {'current_dir':...,}
    :return: HttpResponse(json.dumps({'state':...,'details':...}))
    """
    # 身份验证
    if not validate_identity(request):
        state = 'failed'
        details = '已登录用户才能查看权限'
    else:

        # user_info = {'username':...,'is_sys_admin':BOOL,'root_dir':...}
        user_info = who_is_sending_request(request)
        # access_list_owned_by_userself 用户自己的权限列表
        access_list_owned_by_userself = table_access.get_access_list_by_id(user_info['username'])
        # ---------------------------------------------------
        # 根据request.POST['current_dir']筛选access_list中的权限
        if not check_if_have_this_key(request.POST, 'current_dir'):
            raise KeyError("request.POST 中不存在current_dir这一键值对")
        else:
            curr_dir = request.POST['current_dir']
        # 用户在该路径下是否有管理权限?
        if not db_helper.lookup_access_in_the_list(curr_dir, 'admin', access_list_owned_by_userself):
            state = 'failed'
            details = '用户在该路径下没有管理权限'
        else:
            # 用户在该路径下有权限，开始筛选在该路径下可管理的权限列表（权限包含当前路径的、被当前路径包含的）
            state = 'success'
            access_list = table_access.get_access_list_excluding_id(user_info['username'])
            details = []
            for access_record in access_list:
                if access_record['path'].find(curr_dir) == 0:
                    details.append(access_record)
    return HttpResponse(json.dumps({'state': state, 'details': details}))


def get_access_list_owned_by_userself(request):
    """
    获取当前登录用户的权限列表
    :param request: POST
    request.session['username']
    :return: HttpResponse(json.dumps({'state':...,'details':...}))
    """
    # 身份验证
    if not validate_identity(request):
        state = 'failed'
        details = '已登录用户才能查看权限'
    else:
        if not check_if_have_this_key(request.session, 'username'):
            raise KeyError("当前session中没有username这一字段")
        state = 'success'
        details = table_access.get_access_list_by_id(request.session['username'])
    return HttpResponse(json.dumps({'state': state, 'details': details}))


def display_access_under_path(request):
    """
    返回某用户在某路径下的权限
    :param request: POST
    request.POST={'path':...}
    request.session['username']
    :return: HtttpResponse(json.dumps({'state':...,'details':...}))
    """
    if not validate_identity(request):
        state = 'failed'
        details = '已登录用户才能查看权限'
    else:
        if not check_if_have_this_key(request.POST, 'path'):
            state = 'failed'
            details = '查询权限时缺少参数'
        elif not check_if_have_this_key(request.session, 'username'):
            raise KeyError("当前session中没有username这一字段")
        else:
            result = get_access_under_path(request.session['username'], request.POST['path'])
            state = result['state']
            details = result['details']
    return HttpResponse(json.dumps({'state': state, 'details': details}))


def clean_up_redundant_records(request):
    """
    清除权限表中的冗余记录（1.失效记录，path或user已不存在。2，多余记录，删去某记录后对权限判断不会产生影响）
    :param request: WSGI request GET
    :return: HttpResponse(json.dumps({'state':...,'details':...}))
    """
    if not validate_identity(request):
        state = 'failed'
        details = '请登录后进行该操作'
    else:
        get_access_list = table_access.get_access_list()
        if get_access_list['state'] == 'success':
            access_list = get_access_list['details']
        else:
            raise Exception(get_access_list['details'])
        access_records_to_remove = []  # 记录待删除的数据
        for i in range(len(access_list)):
            record = access_list[i]
            if not table_user.if_user_exists(record['ID']):
                # 清理用户ID已不存在的权限记录
                access_records_to_remove.append(record)
            elif not address_transfer.resolve_path_to_actual_path(record['path'])['state']:
                # 清理已经无法解析的权限记录
                access_records_to_remove.append(record)
            elif not os.path.exists(address_transfer.resolve_path_to_actual_path(record['path'])['actual_path']):
                # 清理路径已不存在的权限记录
                access_records_to_remove.append(record)
            else:
                # 清除冗余记录
                for j in range(i + 1, len(access_list)):
                    record_2 = access_list[j]
                    if record_2['ID'] == record['ID'] and\
                            record_2['read'] == record['read'] and \
                            record_2['new'] == record['new'] and \
                            record_2['download'] == record['download'] and \
                            record_2['remove'] == record['remove'] and \
                            record_2['modify'] == record['modify'] and \
                            record_2['admin'] == record['admin']:
                        if address_helper.is_contain_path(record_2['path'], record['path']) \
                                and record['opt'] == 'recursive':
                            access_records_to_remove.append(record_2)
                        elif address_helper.is_contain_path(record['path'], record_2['path']) \
                                and record_2['opt'] == 'recursive':
                            access_records_to_remove.append(record)
        # 待删除的数据记录完毕，存储在access_records_to_remove中，可能会有重复项
        # 开始删除
        conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                               passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
        cursor = conn.cursor()
        for record_to_remove in access_records_to_remove:
            cursor.execute("DELETE FROM Access_for_path WHERE path='"+str(record_to_remove['path'])+"'")
        conn.commit()
        conn.close()
        state = 'success'
        details = '已清除冗余记录'
    return HttpResponse(json.dumps({'state': state, 'details': details}))
