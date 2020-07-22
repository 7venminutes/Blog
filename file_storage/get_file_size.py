# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-17
Desc: 根据文件存储的实际位置获取文件大小
"""
import os


def get_file_size(file_dir):
    """
    根据传入的文件实际存储的位置，计算并返回文件的大小
    :param file_dir: 文件或文件夹的实际存储位置
    :return: 若file_dir为文件夹则返回‘-’，若为文件则返回以'B'、'KB'或'MB'结尾的字符串
    """
    if not os.path.exists(file_dir):
        return '文件失效, 计算大小时已被其他程序删除'
    elif os.path.isdir(file_dir):
        return '-'
    else:
        size = os.path.getsize(file_dir) / 1024 / 1024
        if size >= 1:
            return str(round(size, 2)) + 'MB'
        else:
            size *= 1024
            if size >= 1:
                return str(round(size, 2)) + 'KB'
            else:
                return str(round(size * 1024, 2)) + 'B'
