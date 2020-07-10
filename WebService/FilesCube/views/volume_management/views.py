# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 卷管理模块视图层
"""
import json
import platform
import sys

from django.http import HttpResponse
import pymysql

if '../' not in sys.path:
    sys.path.append('../')

from common import address_helper, address_transfer
from const_var import DB_NAME, DATABASE_HOST, DATABASE_USER, DATABASE_PORT, DATABASE_PWD
from database.db_helpers import table_volume_mapping


# Create your views here.
def display_volume(request):
    """
    返回所有的卷（实际路径和逻辑路径的映射关系）
    :param request: GET
    :return: HttpResponse(json.dumps({'state': 'success', 'details': volume_mapping_list}))
    volume_mapping_list = {'volume_path':...,'actual_path':...,'size':...,'is_localhost':BOOL}
    """
    print(request)
    print('1234')
    volume_mapping_list = table_volume_mapping.get_volume_mapping('volume_path',
                                                                  'actual_path',
                                                                  'size',
                                                                  'is_localhost')['details']
    print(volume_mapping_list)
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
    print(request.POST)
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
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    # 已有的卷映射表中的实际路径不能包含actual_path、不能被actual_path包含、也不能与actual_path相等
    contain = False
    actual_path_list = table_volume_mapping.get_volume_mapping('actual_path',
                                                               'is_localhost')['details']
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
    '''
    
     ------------=========================================================================-----------
     deprecated [baixu] [2020-07-06] 不允许卷嵌套、取消数据库中对文件路径结构的缓存之后，一下操作没有必要了
     ------------=========================================================================-----------
     
    # 已有卷映射表中不能有和path_in_hfs相同的系统路径记录
    contain = False
    path_in_hfs_list = table_volume_mapping.get_volume_mapping('volume_path')
    for item in path_in_hfs_list:
        if item == path_in_hfs:
            contain = True
            break
    if contain:
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed',
                                        'details': 'path_in_hfs值已在卷映射表中存在着对应的实际路径'}))
    # path_in_hfs 不能已存在于hfs系统中，否则将会导致原来存放于path_in_hfs路径下的文件解析出的地址出错
    count = cursor.execute("SELECT * FROM file_tree WHERE dir='" + path_in_hfs + "'")
    if count > 0:
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed',
                                        'details': '卷添加失败，' + path_in_hfs + '已存在，不能挂载在系统中已存在的目录下'}))
    # 检验传入的实际路径是否能合法地在系统中寻址（是否在系统中存在，之后可以将这一部分扩展为若地址合法而不存在则新建目录，放到所有操作的后面，若新建目录失败则进行回滚）：
    if not os.path.exists(actual_path):
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed',
                                        'details': '实际存储位置中没有这个文件夹，请先手动创建'}))
    # 将传来的 path_in_hfs 字符串拆分成目录项的数组
    item_list = address_helper.separate_path(path_in_hfs)
    # 将新建的卷添加到 hfs 整体的目录结构中:
    if len(item_list) > 1:
        curr_dir = str(item_list[0]) + '/'
        cursor.execute("SELECT ID FROM file_tree WHERE dir='" + curr_dir + "';")
        query_result = cursor.fetchone()
        parent_id = query_result[0]
        exist = True  # 在下面目录项遍历的过程中，用于标记是否数据库的文件系统里还能找到目录项了
        for i in range(len(item_list) - 1):
            j = i + 1
            item_list[j] = str(item_list[j])
            curr_dir += (item_list[j] + '/')
            if exist:
                cursor.execute("SELECT ID, name, dir FROM file_tree WHERE parent_id=" + str(parent_id) + ";")
                query_result = cursor.fetchall()
                found = False
                for single_record in query_result:
                    if single_record[1] == item_list[j]:
                        parent_id = single_record[0]
                        found = True
                        break
                if not found:
                    exist = False
                    cursor.execute("INSERT INTO file_tree(name, type, size, dir, parent_id) \
                    VALUES('" + item_list[j] + "','dir','-','" + curr_dir + "','" + str(parent_id) + "');")
                    cursor.execute("SELECT ID FROM file_tree WHERE dir='" + curr_dir + "';")
                    query_result = cursor.fetchone()
                    parent_id = query_result[0]
            # 若不存在就直接插入记录
            else:
                cursor.execute("INSERT INTO file_tree(name, type, size, dir, parent_id) \
                VALUES('" + item_list[j] + "','dir','-','" + curr_dir + "','" + str(parent_id) + "');")
                cursor.execute("SELECT ID FROM file_tree WHERE dir='" + curr_dir + "';")
                query_result = cursor.fetchone()
                parent_id = query_result[0]
    elif len(item_list) == 1:
        # 前面已经检验过hfs的目录结构中不存在和path_in_hfs相同的路径，故此处可以直接添加
        item_list[0] = str(item_list[0])
        curr_dir = item_list[0] + '/'
        cursor.execute("INSERT INTO file_tree(name, type, size, dir) \
                VALUES('" + item_list[0] + "','dir','-','" + curr_dir + "');")
    else:
        conn.close()
        return HttpResponse(json.dumps({'state': 'failed', 'details': '卷添加失败，path_in_hfs为空?'}))
    '''
    # ----------=========================================================================-----------
    # 用于替换上面的新的检验代码：
    # 传入的path_in_hfs不能已存在于系统中
    # 因为方便直接将（系统不能成功解析传入的path_in_hfs）复用，但实际上牺牲了挺多效率，【mark】
    if address_transfer.resolve_path_to_actual_path(path_in_hfs)['state']:
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
    volume_list = table_volume_mapping.get_volume_mapping('volume_path',
                                                          'actual_path',
                                                          'is_localhost')['details']
    for volume in volume_list:
        print(volume)
        if volume['is_localhost'] == is_localhost:
            if path_in_hfs == volume['volume_path'] and actual_path == volume['actual_path']:
                found = True
                break
    if not found:
        return HttpResponse(json.dumps({'state': 'failed', 'details': '找不到待删除的卷'}))

    # 删除本地卷
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM volume_mapping WHERE volume_path='" + path_in_hfs + "'")
        conn.commit()
    except Exception as error_msg:
        print(error_msg)
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
