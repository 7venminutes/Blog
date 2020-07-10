# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 视图层，一些工具。比如根据传入的参数生成二维码，把图像返回给前端。
"""
import json

from django.http import HttpResponse
from django.utils.six import BytesIO
import os
import qrcode

from common import address_helper, address_transfer
from database.db_helpers import db_helper
import WebService.FilesCube.FilesCube_views as hfs_sys_basic_funcs


def generate_qr_code(request, data):
    """
    根据传来的参数data来生成二维码
    :param request: WSGI请求 GET
    :param data: 附带的参数，用来生成二维码
    :return: HttpResponse(image_stream, content_type="image/png")
    """
    img = qrcode.make(data)

    buf = BytesIO()
    img.save(buf)
    image_stream = buf.getvalue()

    response = HttpResponse(image_stream, content_type="image/png")
    return response


def preview_file_content(request):
    """
    根据传来的文件路径，返回文件的内容供前端预览文件
    :param request: POST
    request.POST['file_dir']
    request.session['access_list']
    :return:HttpResponse(json.dumps(data))
    data = {'result': 'failed' or 'success', 'details': ’文件内容‘ or '报错信息‘}
    """
    hfs_sys_basic_funcs.validate_identity(request)
    file_dir = str(request.POST['file_dir'])
    # fixme [baixu] 2020-06-28 对file_dir的合法性进行验证处理
    have_access = db_helper.lookup_access_in_the_list(file_dir, 'read', request.session['access_list'])
    if not have_access:
        result = 'failed'
        details = '权限不足、无法查看文件内容'
    else:
        temp_path_transfer_result = address_transfer.resolve_path_to_actual_path(file_dir)
        if not temp_path_transfer_result['state']:
            result = 'failed'
            details = '传入的路径无法解析'
        elif not os.path.exists(temp_path_transfer_result['actual_path']):
            result = 'failed'
            details = '所指定文件不存在'
        else:
            filename = temp_path_transfer_result['actual_path']
            try:
                fp = open(filename, 'r', encoding='utf-8')
                details = fp.read()
                fp.close()
                result = 'success'
            except IOError:
                result = 'failed'
                details = "文件打开失败，%s文件不存在" % filename
            except Exception as e:
                result = 'failed'
                details = '文件不支持预览、或其他未知错误'
                print(e)
    return HttpResponse(json.dumps({'result': result, 'details': details}))


def save_txt_file(request):
    """
    更新txt文件内容
    :param request: POST
    request.POST['file_dir'], request.POST['file_content']
    request.session
    :return: HttpResponse(json.dumps({'state': 'failed' or 'success', 'details'))
    """
    hfs_sys_basic_funcs.validate_identity(request)
    file_dir = str(request.POST['file_dir'])
    # fixme [baixu] 2020-06-28 对file_dir的合法性进行验证处理
    have_access = db_helper.lookup_access_in_the_list(file_dir, 'modify', request.session['access_list'])
    if not have_access:
        state = 'failed'
        details = '权限不足、无法修改文件内容'
    else:
        temp_path_transfer_result = address_transfer.resolve_path_to_actual_path(file_dir)
        if not temp_path_transfer_result['state']:
            state = 'failed'
            details = '传入的路径无法解析'
        elif not os.path.exists(temp_path_transfer_result['actual_path']):
            state = 'failed'
            details = '所指定文件不存在'
        else:
            try:
                file = open(temp_path_transfer_result['actual_path'], 'w', encoding='utf-8')
                file.write(request.POST['file_content'])
                print(file_dir)
                print('--------------')
                print(request.POST['file_content'])
                file.close()
                state = 'success'
                details = '文件保存成功'
            except Exception as error_msg:
                print(error_msg)
                state = 'failed'
                details = '未知错误，请联系管理员查看日志排查'
    return HttpResponse(json.dumps({'state': state, 'details': details}))

