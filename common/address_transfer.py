# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/01
Desc: 路径的解析模块，hfs路径与实际路径的转换
"""
import sys
if '../' not in sys.path:
    sys.path.append('../')
from common import address_helper
from database.db_helpers import table_volume_mapping


# 返回卷映射关系表，为方便测试，此处直接返回设置好的字典，实际上线运行时，该函数从数据库中查询
# volume和actual_path均为唯一
def get_volume_relationship():
    """
    从数据库中查询返回卷映射关系表
    :return: [{'volume':...,'actual_path':...,'sys_str':...}]:字典的列表，
    'volume'与'actual_path'均为唯一，'sys_str'为'Linux'或'Windows'
    """
    raw_data = table_volume_mapping.get_volume_mapping('volume_path',
                                                       'actual_path', 'path_type')['details']
    volume_mapping = []
    for row in raw_data:
        volume_mapping.append({'volume': row['volume_path'],
                               'actual_path': row['actual_path'],
                               'sys_str': row['path_type']})
    return volume_mapping


def resolve_path_to_actual_path(path_in_hfs):
    """
    将系统的逻辑路径解析为实际存储路径
    :param path_in_hfs: 文件或文件夹在hfs系统中显示的路径
    :return: {'state':BOOL,'actual_path': 文件或文件夹实际存储的路径 }
    """
    path_in_hfs = str(path_in_hfs)
    volume_mapping = get_volume_relationship()
    selected_volume = {'volume': '', 'actual_path': '', 'sys_str': ''}
    length_of_selected_volume = 0
    for record in volume_mapping:
        # 先判断长度再匹配字符串，长度不够直接剪枝，快
        if len(record['volume']) > length_of_selected_volume:
            if path_in_hfs.find(record['volume']) == 0:
                length_of_selected_volume = len(record['volume'])
                selected_volume['volume'] = record['volume']
                selected_volume['actual_path'] = record['actual_path']
                selected_volume['sys_str'] = record['sys_str']
    # 长度为零就是没匹配到
    actual_path_for_parameter = ''
    state = False
    if length_of_selected_volume == 0:
        actual_path_for_parameter = path_in_hfs
    else:
        state = True
        # path_1st_part is the first part of actual path
        # path_2nd-part is the second part of actual path
        path_1st_part = selected_volume['actual_path']
        path_2nd_part = path_in_hfs[length_of_selected_volume:]
        if selected_volume['sys_str'] == 'Windows':
            path_2nd_part = address_helper.change_slash_to_backslash(path_2nd_part)
        actual_path_for_parameter = path_1st_part + path_2nd_part
    return {'state': state, 'actual_path': actual_path_for_parameter}


def resolve_actual_path_to_path(actual_path):
    """
    将本机上某目录依据卷映射关系表转换为系统的逻辑路径
    函数中的sys_str 为 'Linux' 或 'Windows'
    :param actual_path: 文件或文件夹实际存储的路径
    :return: {'state':...,'path_in_hfs': 文件或文件夹在hfs系统中显示的路径 }
    """
    actual_path = str(actual_path)
    volume_mapping = get_volume_relationship()
    selected_volume = {'volume': '', 'actual_path': '', 'sys_str': ''}
    length_of_actual_path = 0
    for record in volume_mapping:
        if actual_path.find(record['actual_path']) == 0:
            selected_volume['volume'] = record['volume']
            selected_volume['actual_path'] = record['actual_path']
            selected_volume['sys_str'] = record['sys_str']
            length_of_actual_path = len(selected_volume['actual_path'])
            break
    path_in_hfs = ''
    state = False
    # 长度大于零说明成功查询到映射记录
    if length_of_actual_path > 0:
        state = True
        first_part_of_path = selected_volume['volume']
        second_part_of_path = actual_path[length_of_actual_path:]
        if selected_volume['sys_str'] == 'Windows':
            second_part_of_path = address_helper.change_backslash_to_slash(second_part_of_path)
        path_in_hfs = first_part_of_path + second_part_of_path
    else:
        path_in_hfs = actual_path
    return {'state': state, 'path_in_hfs': path_in_hfs}
