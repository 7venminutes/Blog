# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/02
Desc: 用户管理视图层，处理user_management.html发送过来的与用户管理有关的请求
TODO[baixu]: 新建用户和删除用户的业务逻辑在设计上有不妥之处
"""
import json
import logging
import os
import sys

from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.utils.six import BytesIO
from django.views.decorators.csrf import csrf_exempt
import pymysql
import qrcode

if '../../' not in sys.path:
    sys.path.append('../../')

from const_var import FileCube_DbConfig, DEBUG_MODE
from common import address_helper, address_transfer, key_checker
from database.db_helpers import table_access, db_helper
from file_storage.get_file_size import get_file_size
from WebService.FilesCube import operation
from WebService.FilesCube.FilesCube_views import validate_identity


def homepage(request):
    """
    返回hfs系统登陆后的主界面
    :param request: WSGI对象，GET
    :return: 渲染后的index.html
    """
    err_info = []
    if not validate_identity(request):
        return HttpResponseRedirect('/filescube/authentication/')
    else:
        request.session['access_list'] = table_access.get_access_list_by_id(request.session['username'])
    try:
        path = request.session['root_dir']
        if key_checker.check_if_have_this_key(request.POST, 'path'):
            data_dir = path + request.POST['path']
        else:
            data_dir = path
        if request.method == 'POST':
            if 'qr-code' in request.POST:
                url = 'http://' + request.POST['downloadurl']

                if DEBUG_MODE:
                    logging.debug('-----生成二维码-----\nurl: %s', url)

                img = qrcode.make(url)
                buf = BytesIO()
                img.save(buf)
                image_stream = buf.getvalue()
                response = HttpResponse(image_stream, content_type="image/png")
                return response

        return render(request, 'FilesCube/index.html', locals())
    except Exception as error:
        logging.error(error, exc_info=True)
        return render(request, 'FilesCube/index.html', locals())


def get_file_list_under_dir(request):
    """
    展示某目录项下的目录项列表
    :param request: POST
    request.POST = {'file_dir':...}
    request.session['access_list']
    :return: HttpResponse(json.dumps(data_list))
    data_list = {'have_access': BOOL, 'dir_exist': BOOL or None, 'file_list': BOOL or None}
    """
    data_dir = str(request.POST['file_dir'])
    if not data_dir.endswith('/'):
        data_dir += "/"
    have_access = False
    file_list = []
    # 权限校验
    if key_checker.check_if_have_this_key(request.session, 'access_list'):
        access_list = request.session['access_list']
        if db_helper.lookup_access_in_the_list(data_dir, 'read', access_list):
            have_access = True
        else:
            pass

    if have_access:
        _, actual_dir = address_transfer.resolve_path_to_actual_path(data_dir)
        if not os.path.exists(actual_dir):
            data_list = {'have_access': True, 'dir_exist': False, 'file_list': file_list}
        else:
            filename_list = os.listdir(actual_dir)
            for filename in filename_list:
                if os.path.isdir(actual_dir + filename):
                    file_list.append({'file_type': 'dir', 'file_name': filename,
                                      'file_dir': data_dir + filename, 'file_size': '-'})
                else:
                    size = get_file_size(actual_dir + filename)
                    file_list.append({'file_type': 'file', 'file_name': filename,
                                      'file_dir': data_dir + filename, 'file_size': size})
            data_list = {'have_access': True, 'dir_exist': True, 'file_list': file_list}
    else:
        data_list = {'have_access': False, 'dir_exist': None, 'file_list': file_list}

    return HttpResponse(json.dumps(data_list))


def back_to_parent_dir(request):
    """
    切换到文件系统的上级目录，返回上级目录下的目录项列表
    :param request: POST
    request.POST = {'file_dir':...}
    request.session['access_list']
    :return: HttpResponse(json.dumps(data_list))
    data_list = {'have_access':BOOL,'have_parent': BOOL or None,
                'new_current_path': ..., 'file_list': ...}
    """
    current_dir = str(request.POST['file_dir'])
    # TODO[柏旭] 2020-06-28 检查传入路径是否合法
    temp_find_parent_dir_result = address_helper.find_parent_dir(current_dir)
    have_parent = temp_find_parent_dir_result['result']
    if have_parent:
        new_current_path = temp_find_parent_dir_result['details']

        # -------------------------------------------------------------------------------------------------------
        if not new_current_path.endswith('/'):
            new_current_path += "/"
        have_access = False
        file_list = []
        # 权限校验
        if key_checker.check_if_have_this_key(request.session, 'access_list'):
            access_list = request.session['access_list']
            if db_helper.lookup_access_in_the_list(new_current_path, 'read', access_list):
                have_access = True
            else:
                pass

        if have_access:
            _, actual_dir = address_transfer.resolve_path_to_actual_path(new_current_path)
            if os.path.exists(actual_dir):
                filename_list = os.listdir(actual_dir)
                for filename in filename_list:
                    if os.path.isdir(actual_dir + filename):
                        file_list.append({'file_type': 'dir', 'file_name': filename,
                                          'file_dir': new_current_path + filename, 'file_size': '-'})
                    else:
                        size = get_file_size(actual_dir + filename)
                        file_list.append({'file_type': 'file', 'file_name': filename,
                                          'file_dir': new_current_path + filename, 'file_size': size})
        # -------------------------------------------------------------------------------------------------------
    else:
        have_access = True
        new_current_path = current_dir
        file_list = None
    return HttpResponse(json.dumps({'have_access': have_access,
                                    'have_parent': have_parent,
                                    'new_current_path': new_current_path,
                                    'file_list': file_list}))


def remove_file(request):
    """
    删除文件或文件夹
    :param request: POST，
    request.POST={'remove_path':...,'remove_name':...,'remove_file_type':...}
    :return: HttpResponse(json.dumps({'state':...,'remove_file_id':...}))
    state = 'failed' or 'success'
    remove_file_id: 被删除目录项的ID
    """
    if DEBUG_MODE:
        logging.debug("remove_file ——views/index/views.py")
    try:
        remove_path = request.POST['remove_path']
        remove_name = request.POST['remove_name']
        remove_file_type = request.POST['remove_file_type']
        remove_file_id = -1
    except Exception as error:
        logging.error(error, exc_info=True)
        logging.warning("POST中某参数为空 ——views/index/views.py remove_file(request)")
        return {'state': 'failed', 'details': 'session失效'}
    if not db_helper.lookup_access_in_the_list(remove_path, 'remove', request.session['access']):
        logging.info("无删除权限 ——views.py remove_file(request)\n"
                     "用户名：%s, 尝试删除的文件或文件夹： %s"
                     , request.session['username']
                     , remove_path)
        return HttpResponse(json.dumps({'state': 'failed', 'details': '无权限'}))

    if remove_file_type == 'dir':
        remove_dir = remove_path + remove_name + '/'
    else:
        remove_dir = remove_path + remove_name
    if_path_can_be_resolved, actual_remove_path = address_transfer.resolve_path_to_actual_path(remove_dir)
    if not if_path_can_be_resolved or not os.path.exists(actual_remove_path):
        logging.warning("待删除的路径不存在 ——views.py remove_file(request)\n"
                        "\t待删除路径： %s"
                        , remove_path)
        return HttpResponse(json.dumps({'state': 'failed', 'details': '文件不存在'}))
    else:
        operation.remove_file(remove_dir, request.session['username'])
        return HttpResponse(json.dumps({'state': 'success', 'remove_file_id': str(remove_file_id)}))


def rename_or_move(request):
    """
    移动或重命名文件或文件夹
    :param request: POST
    request.POST = {'file_type':...,'curr_path':...,'curr_name':...,'des_path':...,'des_name':...}
    request.session['access']
    :return: HttpResponse(json.dumps({'state':...,'details':...}))
    state = 'failed' or 'success'
    details为移动成功后的文件信息{'file_id':...,'new_parent_id':...}或失败后的报错信息
    """
    if DEBUG_MODE:
        logging.debug("移动或重命名文件")

    file_type = str(request.POST['file_type'])
    curr_path = str(request.POST['curr_path'])
    curr_name = str(request.POST['curr_name'])
    des_path = str(request.POST['des_path'])
    des_name = str(request.POST['des_name'])
    access_in_cur_dir = db_helper.lookup_access_in_the_list(curr_path, 'modify',
                                                            request.session['access'])
    access_in_des_dir = db_helper.lookup_access_in_the_list(des_path, 'modify',
                                                            request.session['access'])
    if access_in_des_dir and access_in_cur_dir:
        message = operation.rename_and_move_file(file_type, curr_path, curr_name, des_path, des_name,
                                                 request.session['username'])
        if message['state'] == 'failed':
            return HttpResponse(json.dumps({'state': 'failed', 'details': message['details']}))
        else:
            conn = pymysql.connect(host=FileCube_DbConfig['host'],
                                   port=FileCube_DbConfig['port'],
                                   user=FileCube_DbConfig['user'],
                                   passwd=FileCube_DbConfig['pwd'],
                                   db=FileCube_DbConfig['db_name'],
                                   charset='utf8')
            cursor = conn.cursor()
            append_slash = ""
            file_id = 0
            new_parent_id = 0
            if file_type == 'dir':
                append_slash = "/"
            cursor.execute("SELECT ID,parent_id FROM file_tree WHERE dir ='" + des_path + des_name + append_slash + "'")
            query_result = cursor.fetchall()
            for row in query_result:
                file_id = row[0]
                new_parent_id = row[1]
            return HttpResponse(json.dumps({'state': 'success', 'details': {'file_id': file_id,
                                                                            'new_parent_id': new_parent_id}}))
    elif not access_in_cur_dir:
        return HttpResponse(json.dumps({'state': 'failed', 'details': '当前路径下无修改权限'}))
    else:
        return HttpResponse(json.dumps({'state': 'failed', 'details': '目标路径下无修改权限'}))


def make_dir(request):
    """
    新建文件夹
    :param request: POST
    request.POST = {'mkdir_path':...,'mkdir_name':...}
    :return: HttpResponse(json.dumps({'state':..., 'details':...}))
    state = 'failed' or 'success'
    details为成功后的文件信息{'file_id':...,'file_name':...,'file_dir':...,'new_parent_id':...}
        或失败后的报错信息
    """
    mkdir_path = str(request.POST['mkdir_path'])
    mkdir_name = str(request.POST['mkdir_name'])

    if DEBUG_MODE:
        logging.debug("开始新建文件夹(路径：%s, 文件名：%s)", mkdir_path, mkdir_name)

    if db_helper.lookup_access_in_the_list(mkdir_path, 'new', request.session['access']):
        conn = pymysql.connect(host=FileCube_DbConfig['host'],
                               port=FileCube_DbConfig['port'],
                               user=FileCube_DbConfig['user'],
                               passwd=FileCube_DbConfig['pwd'],
                               db=FileCube_DbConfig['db_name'],
                               charset='utf8')
        cursor = conn.cursor()
        count = cursor.execute("SELECT * FROM file_tree WHERE dir='" + mkdir_path + mkdir_name + "/'")
        if count > 0:
            conn.close()
            return HttpResponse(json.dumps({'state': 'failed', 'details': '该路径下已存在同名文件夹'}))
        else:
            result = operation.make_dir(mkdir_path, request.session['username'], mkdir_name)
            if result['state'] == 'failed':
                logging.info(result['details'])
                return HttpResponse(json.dumps({'state': 'failed', 'details': result['details']}))
            else:
                logging.info(result['details'])
                file_id = result['ID']
                file_name = result['name']
                file_dir = result['dir']
                file_parent_id = result['parent_id']
                if DEBUG_MODE:
                    logging.debug(json.dumps({'state': 'success',
                                  'file_info': {'file_id': file_id, 'file_name': file_name,
                                                'file_dir': file_dir, 'file_parent_id': file_parent_id}}))
                conn.close()
                return HttpResponse(json.dumps({'state': 'success',
                                                'file_info': {'file_id': file_id, 'file_name': file_name,
                                                              'file_dir': file_dir, 'file_parent_id': file_parent_id}}))
    else:
        return HttpResponse(json.dumps({'state': 'failed', 'details': '权限不足'}))


@csrf_exempt
def display_file_tree(request):
    """
    主页面中文件树所对应的异步查询树中数据的处理代码
    :param request: POST
    :return: HttpResponse(json.dumps(data_list))
    data_list=[{'id':...,'text':..., 'state':...,
                'attributes': {'file_type':..., 'file_name':..., 'file_dir':...}})
    id 为文件在hfs文件系统中的ID
    text 为目录项的名称
    state = 'closed' or 'open'， 文件夹为'closed',文件为'open'
    file_type = 'dir' or 'type'
    file_name 为目录项名称
    file-dir 为目录项在hfs系统中所在的路径
    """
    try:
        request_id = request.POST.get('id', -1)
        if request_id != -1:
            data_list = []
            '''
                        print(request_id)
            data_list = []
            cursor.execute("SELECT ID, type, name, dir from file_tree \
                                        WHERE parent_id='" + str(request_id) + "'")
            listdir = cursor.fetchall()
            for file in listdir:
                file_id = file[0]
                file_name = file[2]
                file_type = file[1]
                file_dir = file[3]
                if file_type == 'dir':
                    data_list.append({'id': file_id, 'text': file_name, 'state': 'closed',
                                      'attributes': {'file_type': 'dir', 'file_name': file_name, 'file_dir': file_dir}})
                else
                    data_list.append({'id': file_id, 'text': file_name, 'state': 'open',
                                      'attributes': {'file_type': 'file', 'file_name': file_name,
                                                     'file_dir': file_dir}})
            '''
        else:
            # 从session中获取当前用户的权限列表access_list
            # 将access_list中的路径信息单独存一个列表path_list
            # 调用db_helper中select_root_node去除path_list中的包含关系
            # data_list为将要返回给前端的数据
            access_list = request.session['access_list']
            path_list = []
            for access in access_list:
                if access['read']:
                    path_list.append(access['path'])
            selected_path_list = db_helper.select_root_node(path_list)
            data_list = []
            for row in selected_path_list:
                file_dir = str(row)
                file_name = address_helper.separate_path(file_dir)[-1]
                data_list.append({'text': file_name, 'state': 'closed',
                                  'attributes': {'file_type': 'dir',
                                                 'file_name': file_name,
                                                 'file_dir': file_dir}})
    finally:
        pass
    if DEBUG_MODE:
        logging.debug(data_list)
    return HttpResponse(json.dumps(data_list))
