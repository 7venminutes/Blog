# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-29
Desc: 下载相关的处理函数（文件分片下载）
"""
import logging
import mimetypes
import os
import re
import stat

from django.http import HttpResponse, FileResponse, HttpResponseNotModified, Http404
# 基于django.views.static.serve实现，支持大文件的断点续传（暂停/继续下载）
from django.utils.http import http_date
from django.views.static import was_modified_since

from common import address_transfer
from database.db_helpers import db_helper, table_access


def download(request, path):
    """
    FileCube文件的下载接口，向前端返回支持文件部分下载的数据流，支持下载暂停、断点续传和多线程并发下载
    path为下载文件在FileCube系统内的表示路径
    request: WSGI请求
    权限控制: 通过request找到对应的session，查找里面记录的用户名，以此来进行权限判断
            若用户未登录，则使用匿名账户的权限记录进行判断
    """
    try:
        username = request.session['username']
    except KeyError:
        username = 'anonymous_user'

    # 对path合法性判断一下
    path = str(path)

    access_list = table_access.get_access_list_by_id(username)
    if not db_helper.lookup_access_in_the_list(path, 'download', access_list):
        return HttpResponse('no download access to resource', status=403)
    else:
        transfer_state, actual_path = address_transfer.resolve_path_to_actual_path
        if transfer_state and not os.path.exists(actual_path):
            raise Http404('"%(path)s" does not exist' % {'path': path})
        elif not transfer_state:
            raise Http404('"%(path)s" can not be resolved properly' % {'path': path})
        elif os.path.isdir(actual_path):
            return HttpResponse('server does not support downloading a folder', status=403)
        else:
            # 一切均正常，开始下载
            return get_file_response(request, actual_path)


def get_file_response(request, path, opt='download'):
    """
    返回下载文件流, 此处path为服务器上文件实际存储的位置
    opt == ‘download’:   下载 content-type = ‘application/octet-stream’
    opt == 'display': 展示文件 content-type = 文件本身的 mimetype
    """
    # 注释原因， 没看懂原代码是否有其他的安全考虑 Baixu 2020-07-08
    # # 防止目录遍历漏洞
    # path = posixpath.normpath(path).lstrip('/')
    # full_path = safe_join(document_root, path)
    full_path = path
    if os.path.isdir(full_path):
        raise Http404('Directory indexes are not allowed here.')
    if not os.path.exists(full_path):
        raise Http404('"%(path)s" does not exist' % {'path': full_path})

    stat_obj = os.stat(full_path)

    # 判断下载过程中文件是否被修改过
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              stat_obj.st_mtime, stat_obj.st_size):
        return HttpResponseNotModified()

    content_type, encoding = mimetypes.guess_type(full_path)
    # 获取文件的content_type
    if opt == 'download':
        content_type = 'application/octet-stream'
    elif opt == 'display':
        content_type = content_type
    else:
        raise ValueError("parameter 'opt' in function get_file_response "
                         "can only be 'download' or 'display'")

    # 计算读取文件的起始位置
    start_bytes = re.search(r'bytes=(\d+)-', request.META.get('HTTP_RANGE', ''), re.S)

    logging.info(request.META.get('HTTP_RANGE', ''))

    start_bytes = int(start_bytes.group(1)) if start_bytes else 0

    # 打开文件并移动下标到起始位置，客户端点击继续下载时，从上次断开的点继续读取
    the_file = open(full_path, 'rb')
    the_file.seek(start_bytes, os.SEEK_SET)

    # status=200表示下载开始，status=206表示下载暂停后继续，为了兼容火狐浏览器而区分两种状态
    # 关于django的response对象，参考：https://www.cnblogs.com/scolia/p/5635546.html
    # 关于response的状态码，参考：https://www.cnblogs.com/DeasonGuan/articles/Hanami.html
    # FileResponse默认block_size = 4096，因此迭代器每次读取4KB数据
    response = FileResponse(the_file, content_type=content_type, status=206 if start_bytes > 0 else 200)
    # 'Accept-Ranges' 设为 'bytes' 告诉客户端服务器支持按字节获取部分文件，以实现断点续传
    response['Accept-Ranges'] = 'bytes'
    # 'Last-Modified'表示文件修改时间，与'HTTP_IF_MODIFIED_SINCE'对应使用，参考：https://www.jianshu.com/p/b4ecca41bbff
    response['Last-Modified'] = http_date(stat_obj.st_mtime)

    # 这里'Content-Length'表示剩余待传输的文件字节长度
    if stat.S_ISREG(stat_obj.st_mode):
        response['Content-Length'] = stat_obj.st_size - start_bytes
    if encoding:
        response['Content-Encoding'] = encoding

    # 'Content-Range'的'/'之前描述响应覆盖的文件字节范围，起始下标为0，'/'之后描述整个文件长度，与'HTTP_RANGE'对应使用
    # 参考：http://liqwei.com/network/protocol/2011/886.shtml
    response['Content-Range'] = 'bytes %s-%s/%s' % (start_bytes, stat_obj.st_size - 1, stat_obj.st_size)

    # 'Cache-Control'控制浏览器缓存行为，此处禁止浏览器缓存，参考：https://blog.csdn.net/cominglately/article/details/77685214
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

    return response
