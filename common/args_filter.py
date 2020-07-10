# -*- coding: utf-8 -*-
"""
Arthur: Baixu
Date: 2020/06/03
Desc: 过滤参数
"""


def filter_args(expected_args_list, *args):
    """
    找出expected_args_list与*args中共有的参数，返回筛选之后的参数列表
    :param expected_args_list: 字符串的列表
    :param args: 待筛选的参数列表
    :return: 筛选之后的参数列表
    """
    selected_columns = []  # 字符串列表，存放同时在expected_args_list和*args中存在的参数名
    # 遍历*args,将参数与expected_args_list中的参数比较，若相同则选中该参数
    for arg in args:
        if arg in expected_args_list:
            selected_columns.append(arg)
        else:
            print(str(arg) + " not in expected_args_list")
    print('---------------------')
    return selected_columns
