# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-29
Desc: 上传文件相关的处理函数（实现文件分片上传）
"""
import json
import logging
import os
import sys
import time

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import database.db_helpers.db_helper as db_helper
from common import address_transfer, key_checker
from const_var import DEBUG_MODE
from WebService.FilesCube import FilesCube_views


def uploadPage(request):
    """
    返回上传文件界面
    :param request:POST
    :return: 上传文件界面
    """
    file_path = request.GET.get('file_path')
    return render(request, 'upload_test.html', {'file_path': file_path})


@csrf_exempt
def check_chunk(request):
    """
    检查上传分片是否重复，如果重复则不提交，否则提交
    :param request: POST
    :return: JsonResponse({'Exist': true or false})
    """
    # post请求
    if request.method == 'POST':
        # 获得上传文件块的大小,如果为0，就告诉他不要上传了
        chunkSize = request.POST.get("chunkSize")
        if chunkSize == '0':
            return JsonResponse({'ifExist': True})
        # 如果文件块大小不为0 ，那么就上传，需要拼接一个临时文件
        file_name = request.POST.get('fileMd5') + request.POST.get('chunk')

        # 如果说这个文件不在已经上传的目录，就可以上传，已经存在了就不需要上传。
        if file_name not in get_deep_data():
            return JsonResponse({'ifExist': False})
        return JsonResponse({'ifExist': True})


def get_deep_data(path='static/upload/'):
    """
    判断一个文件是否在一个目录下
    :param path: 目录的路径
    :return: 所有位于该目录下的目录项名称的数组
    """
    result = []
    data = os.listdir(path)
    for i in data:
        if os.path.isdir(i):
            get_deep_data(i)
            result.append(i)
        else:
            result.append(i)
    return result


def check_access(request):
    """
    检查用户是否在该路径下有上传权限
    :param request: request.POST['file_dir']
    :return: BOOL
    """
    have_access = db_helper.lookup_access_in_the_list(request.POST['file_path'], 'new', request.session['access'])
    if DEBUG_MODE:
        logging.debug('检查用户是否有对应目录的上传权限( %s )', have_access)
    if have_access:
        return JsonResponse({'haveAccess': True})
    else:
        return JsonResponse({'haveAccess': False})


def upload_part(request):
    """
    接受一个新的文件分片
    :param request: POST
    :return: 上传文件界面
    """
    if DEBUG_MODE:
        logging.debug(request.POST)
    task = request.POST['task_id']  # 获取文件的唯一标识符
    chunk = request.POST['chunk']  # 获取该分片在所有分片中的序号
    file_path = request.POST['file_path']
    if not FilesCube_views.validate_identity(request):
        return HttpResponseRedirect('login/')

    elif db_helper.lookup_access_in_the_list(request.POST['file_path'], 'new', request.session['access']):
        _, actual_dir = address_transfer.resolve_path_to_actual_path(file_path)
        filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

        upload_file = request.FILES['file']
        with open(actual_dir + filename, 'wb') as f:
            for i in upload_file.chunks():
                f.write(i)  # 保存分片到本地

    else:
        logging.warning('用户无上传权限，已忽视该请求（用户名：%s, 上传路径： %s）'
                        , request.session['username']
                        , request.POST['file_path'])


def upload(request):
    """
    接受前端发送过来的文件上传请求，向服务器写文件,
    根据request.POST中是否含有chunk参数，来判断传过来的是一个大文件的分片还是一整个文件
    :param request: POST
    request.POST: mode, task_id, file_path, csrfmiddlewaretoken, id, name, type, lastModifiedDate, size
    :return: null
    """
    task = request.POST['task_id']  # 获取文件的唯一标识符
    file_path = request.POST['file_path']
    if not FilesCube_views.validate_identity(request):
        return HttpResponseRedirect('login/')
    elif not db_helper.lookup_access_in_the_list(file_path, 'new', request.session['access']):
        # 用户在该目录下无上传权限，
        # fixme[baixu] 添加返回值，与前端交互
        logging.warning("用户%s希望上传%s, 但他在%s下无上传权限"
                        , request.session['username']
                        , request.POST['name']
                        , file_path)
    else:
        # 进入上传流程
        # fixme[baixu][2020-07-20] 上传路径不存在时如何提醒前端？
        _, actual_dir = address_transfer.resolve_path_to_actual_path(file_path)
        upload_file = request.FILES['file']
        if key_checker.check_if_have_this_key(request.POST, 'chunk'):
            # 前端发送过来的数据是一个大文件的某个分片
            chunk = request.POST['chunk']  # 获取该分片在所有分片中的序号
            filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符
            with open(actual_dir + filename, 'wb') as f:
                for i in upload_file.chunks():
                    f.write(i)  # 保存该分片到本地

        else:
            # 前端发送过来的是一个完整的文件
            filename = '%s%s' % (task, 0)  # 构造文件标识符，上传完毕后会在upload_success中将文件名更正
            with open(actual_dir + filename, 'wb') as f:
                for i in upload_file.chunks():
                    f.write(i)  # 保存该文件
    return HttpResponse(json.dumps({'123': '123'}))


@csrf_exempt
def upload_success(request):
    """
    文件上传成功时调用该函数，将上传过程中服务器上保存的有关该文件的分片整合到一起，形成一个文件
    :param request: POST
    :return: 上传文件界面
    """
    # logging.info('前端发送上传结束消息')
    target_filename = request.GET.get('filename')  # 获取上传文件的文件名
    task = request.GET.get('task_id')  # 获取文件的唯一标识符
    file_path = request.GET.get('file_path')
    # fixme file_path不存在怎么办
    _, actual_dir = address_transfer.resolve_path_to_actual_path(file_path)
    chunk = 0  # 分片序号
    with open(actual_dir + target_filename, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = actual_dir + '%s%d' % (task, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError as msg:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return HttpResponse(status=200)
