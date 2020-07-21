# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-21
Desc: 异步非阻塞调用，装饰器
"""
from threading import Thread


def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper
