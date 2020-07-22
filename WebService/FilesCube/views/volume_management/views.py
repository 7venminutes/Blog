# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 卷管理模块视图层
"""
import json
import logging
import platform
import sys

from django.http import HttpResponse
import pymysql

if '../' not in sys.path:
    sys.path.append('../')

from common import address_helper, address_transfer
from const_var import FileCube_DbConfig, DEBUG_MODE
from database.db_helpers import table_volume_mapping


# Create your views here.
def display_volume(request):
    """
    返回所有的卷（实际路径和逻辑路径的映射关系）
    :param request: GET
    :return: HttpResponse(json.dumps({'state': 'success', 'details': volume_mapping_list}))
    volume_mapping_list = {'volume_path':...,'actual_path':...,'size':...,'is_localhost':BOOL}
    """
    if DEBUG_MODE:
        logging.debug(request)

    _, volume_mapping_list = table_volume_mapping.get_volume_mapping('volume_path',
                                                                     'actual_path',
                                                                     'size',
                                                                     'is_localhost')
    return HttpResponse(json.dumps({'state': 'success', 'details': volume_mapping_list}))


# 接收参数： POST提交, actual_path, path_in_hfs
def create_normal_volume(request):
    """
    创建新的本地卷
    :param request: POST
    request.POST['actual_path']
    request.POST['path_in_hfs']
    :return: HttpResponse(json.dumps({'state': ...,'details': ...}
    state = 'failed' or 'success'
    details为详细的描述信息
    """
    if DEBUG_MODE:
        logging.debug(request.POST)

    # 为服务器本机上某个目录创建卷，加入到hfs系统中
    actual_path = str(request.POST['actual_path'])
    path_in_hfs = str(request.POST['path_in_hfs'])
    if not path_in_hfs.endswith('/'):
        path_in_hfs += '/'
    # sys_str为 Windows 或 Linux
    sys_str = platform.system()
    if sys_str == 'Windows':
        if not actual_path.endswith('\\'):
            actual_path += '\\'
    elif sys_str == 'Linux':
        if not actual_path.endswith('/'):
            actual_path += '/'
    size = '500G'
    is_localhost = True
    conn = pymysql.connect(host=FileCube_DbConfig['host'],
                           port=FileCube_DbConfig['port'],
                           user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'],
                           db=FileCube_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    # 已有的卷映射表中的实际路径不能包含actual_path、不能被actual_path包含、也不能与actual_path相等
    contain = False
    _, actual_path_list = table_volume_mapping.get_volume_mapping('actual_path',
                                                                  'is_localhost')
    for item in actual_path_list:
        if item['is_localhost'] and sys_str == 'Windows':
            if address_helper.is_contain_path(item['actual_path'], actual_path, '\\') or \
                    address_helper.is_contain_path(actual_path, item['actual_path'], '\\'):
                contain = True
                break
        elif item['is_localhost'] and sys_str == 'Linux':
            if address_helper.is_contain_path(item['actual_path'], actual_path) or \
                    address_helper.is_contain_path(actual_path, item['actual_path']):
                contain = True
                break
    if contain:
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed',
                                        'details': '已有的卷映射表中的实际路径不能包含actual_path、'
                                                   '不能被actual_path包含、也不能与actual_path相等'}))
    # ----------=========================================================================-----------
    # 用于替换上面的新的检验代码：
    # 传入的path_in_hfs不能已存在于系统中
    # 因为方便直接将（系统不能成功解析传入的path_in_hfs）复用，但实际上牺牲了挺多效率，【mark】
    transfer_state, _ = address_transfer.resolve_path_to_actual_path(path_in_hfs)
    if transfer_state:
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed',
                                        'details': '卷的挂载点已存在'}))
    # 最后进行新建卷的操作
    cursor.execute("INSERT INTO volume_mapping"
                   "            (volume_path, size, actual_path, path_type, is_localhost) "
                   "VALUES('" + path_in_hfs + "', '" + size + "', '" +
                   address_helper.double_backslash(actual_path)
                   + "','" + sys_str + "', " + str(is_localhost) + ");")
    conn.commit()
    conn.close()
    return HttpResponse(json.dumps({'state': 'success', 'details': '卷添加成功，选择文件同步可同步卷的目录结构'}))


def remove_normal_volume(request):
    """
    移除本地卷、但不删除卷内存储的文件
    :param request: POST
    request.POST = {'actual_path':...,'path_in_hfs':...,'is_localhost':...,'host_address":...}
        actual_path: 卷的实际路径
        path_in_hfs: 卷在hfs系统内的挂载点
        is_localhost: 'true' or 'false', 目前前端只会传入true
        host_address: 主机地址，仅当is_localhost=='false'时传入此项
    :return: HttpResponse(json.dumps({'state': ..., 'details': ...}))
        state = 'failed' or 'success'
        details为详细的状态描述信息
    """
    actual_path = str(request.POST['actual_path'])
    path_in_hfs = str(request.POST['path_in_hfs'])
    if not path_in_hfs.endswith('/'):
        path_in_hfs += '/'
    is_localhost = False  # BOOL类型
    if request.POST['is_localhost'] == 'true':
        is_localhost = True
    # 检查传入参数

    # 1.检查卷是否在映射表中
    found = False
    _, volume_list = table_volume_mapping.get_volume_mapping('volume_path',
                                                             'actual_path',
                                                             'is_localhost')
    for volume in volume_list:
        if volume['is_localhost'] == is_localhost:
            if path_in_hfs == volume['volume_path'] and actual_path == volume['actual_path']:
                found = True
                break
    if not found:
        return HttpResponse(json.dumps({'state': 'failed', 'details': '找不到待删除的卷'}))

    # 删除本地卷
    conn = pymysql.connect(host=FileCube_DbConfig['host'],
                           port=FileCube_DbConfig['port'],
                           user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'],
                           db=FileCube_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM volume_mapping WHERE volume_path='" + path_in_hfs + "'")
        conn.commit()
    except Exception as error_msg:
        logging.error(error_msg, exc_info=True)
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed', 'details': '数据库错误、删除失败'}))

    conn.close()
    return HttpResponse(json.dumps({'state': 'success', 'details': '删除成功'}))


"""
def modify_volume(request):
    \"""
    修改某个卷在hfs系统内的挂载点
    :param request: POST
        request.POST = {'volume_path':...,'new_volume_path':...}
    :return: HttpResponse(json.dumps({'state': ..., 'details': ...}))
        state = 'failed' or 'success'
        details为详细的状态描述信息
    \"""
    # 重新指定卷在hfs系统内的挂载点
    # 重新指定卷的大小(涉及到对实际存储空间的判断，暂且不写)
    volume_path = request.POST['volume_path']
    new_volume_path = request.POST['new_volume_path']
    do_something = 4
"""
