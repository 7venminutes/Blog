# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-05
Desc: 检查是否某字典类型内是否含有某些键值
"""


def check_if_have_these_keys(dict_to_check, key_list):
    """
    检查字典dict_to_check中是否含有key_list中的键值
    :param dict_to_check: 待检查的字典
    :param key_list: 待判断的键值列表
    :return: BOOL
    """
    have_keys = True
    for key in key_list:
        try:
            dict_to_check[key]
        except KeyError:
            have_keys = False
            break
        except TypeError:
            raise TypeError('dict_to_check should be a dict')
    return have_keys


def check_if_have_this_key(dict_to_check, key):
    """
    检查字典dict_to_check中是否含有key
    :param dict_to_check: 待检查的字典
    :param key: 待判断的键值
    :return: BOOL
    """
    have_key = True
    try:
        dict_to_check[key]
    except KeyError:
        have_key = False
    except TypeError:
        raise TypeError('dict_to_check should be a dict')
    print(have_key)
    print('-----------------------common.py check if have this key')
    return have_key
