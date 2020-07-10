# -*- coding: utf-8 -*-
#
# Author: Baixu
# Date: 2020/05/15
# Desc: 用来辅助路径解析的工具
#
"""
TODO[baixu]: L54: check validation of input file name
TODO[baixu]: L61: check validation of input path
"""


def change_backslash_to_slash(backslash_dir):
    """
    将用r'\'分割的路径替换成用'/'分割的路径
    :param backslash_dir: 用r'\'分割的路径字符串
    :return: 用'/'分割的字符串
    """
    return str(backslash_dir).replace('\\', '/')


def change_slash_to_backslash(slash_dir):
    """
    将用'/'分割的路径替换成用r'\'分割的路径
    :param slash_dir: 路径字符串，用'/'进行分割
    :return: 用r'\'分割的字符串
    """
    return str(slash_dir).replace('/', '\\')


def double_backslash(slash_dir):
    r"""
    将路径中所有的 \ 转换成 \\, 以应对 \ 被当作转义字符时的情况
    """
    return str(slash_dir).replace('\\', '\\\\')


def separate_path(path, separator='/'):
    """
    将路径中各个层级拆分出来从前之后存入列表然后返回
    ex： hfs/abcd/hjkl  ->  ['hfs', 'abcd', 'hjkl']
    """
    return [p for p in path.split(separator) if p]


def is_contain_path(path_a, path_b, separator='/'):
    """
    检验路径A是否在路径B之下
    ( 以路径 B 为根节点的文件树中包含路径A )
    """
    path_a = separate_path(str(path_a), separator)
    path_b = separate_path(str(path_b), separator)
    is_contain = True
    if len(path_a) < len(path_b):
        is_contain = False
    else:
        for index_b in range(len(path_b)):
            if path_b[index_b] == path_a[index_b]:
                continue
            is_contain = False
    return is_contain


def find_parent_dir(original_dir):
    """
    寻找original_dir的父节点的路径
    :param original_dir: 传入的路径名称
    :return: {'result': True or False, 'details': 报错详情或 parent_dir
    """
    if not isinstance(original_dir, str):
        raise TypeError('original_dir 应该为字符串类型,----find_parent_dir')
    path_original = separate_path(original_dir, '/')
    if len(path_original) < 2:
        result = False
        details = '路径已经是根目录，没有父节点了'
    else:
        result = True
        details = '/'.join(path_original[:-1]) + '/'
        if original_dir[0] == '/':
            details = '/' + details
    return {'result': result, 'details': details}


def is_file_name_valid(file_name):
    r"""
    TODO[baixu yan]: 检验用户输入的文件名或文件夹名是否合法
    windows 文件名规则：文件名不能包含\ / ? " : * < > |
    linux 文件名规则： 文件名不能包含/
    """
    pass


def is_path_valid(addr):
    """
    TODO[baixu yan]: 检验某路径是否包含违法字符
    """
    pass
