# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-21
Desc: web 与 service 之间的中介器，负责向service派发任务，接受service处理完的任务
"""
import logging
import time

from WebService.Starry.mediator import set_time_stamp, get_time_stamp
from WebService.Starry.async_call import async_call

blocked = False  # handle_frontend_request()的锁，同一时间只能由一个该函数在运行
min_time_interval = 1  # handle_fronted_request()处理不同请求的最短时间间隔


@async_call
def handle_FrontEnd_request():
    """
    前端轮询任务是否完成，每一次请求最终都会触发该函数，该函数根据距上次自己询问service相隔的时间
    来决定是否要向service推送一条新的任务
    """
    global blocked
    if not blocked:
        blocked = True
        try:
            if time.time() - get_time_stamp() < min_time_interval:
                # 若时间间隔小于min_time_interval，则忽视该请求(节省查询数据库的消耗，帮助service模块限流）
                pass
            else:
                # TODO baixu【2020-07-21】 给service安排任务
                # 从transform_task表中拿出一条未完成的任务
                # 将该任务传递给service
                # 最后更新time_stamp
                set_time_stamp()
                pass
        except Exception as e:
            logging.error(str(e), exc_info=True)
        finally:
            blocked = False


# TODO [baixu][2020-07-21] 接受service传来的任务
def receive_finished_task_from_ServiceEnd(request):
    """
    接受service端传来的完成任务
    :param request: POST
    :return: XXX
    """
    pass
