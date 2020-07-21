# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-21
Desc: web 与 service 之间的中介器，负责向service派发任务，接受service处理完的任务
"""
import time

# 所有web任务均会一直轮询自己有没有完成，轮询请求都会接到mediator这里，mediator会根据上次自己处理请求的时间戳来决定是否无视该请求
# _LAST_TIME_MEDIATOR_ASK_SERVICE为mediator最近一次处理请求的时间戳
_LAST_TIME_MEDIATOR_ASK_SERVICE = 1459994552.51


def set_time_stamp():
    """
    设置时间戳_LAST_TIME_MEDIATOR_ASK_SERVICE
    """
    global _LAST_TIME_MEDIATOR_ASK_SERVICE
    _LAST_TIME_MEDIATOR_ASK_SERVICE = time.time()


def get_time_stamp():
    """
    获取_LAST_TIME_MEDIATOR_ASK_SERVICE的值
    :return: _LAST_TIME_MEDIATOR_ASK_SERVICE: float
    """
    return _LAST_TIME_MEDIATOR_ASK_SERVICE
