"""
Author: Baixu
Date: 2020-07-10
Desc: 处理网站中starry风格迁移业务的视图请求
"""
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render

from WebService.Starry.database import transform_task
from WebService.Starry.mediator import mediator


def starry(request, path):
    return render(request, 'Starry/starry.html')


def get_queue_length(request):
    """
    用户提交任务时，前端调用该接口返回正在等待中的任务数，便于用户估计等待时间
    :param request: GET
    :return: HttpResponse(JSON.dumps({'task_num':...))
    """
    task_num = transform_task.get_unfinished_task_num()
    return HttpResponse(json.dumps({'task_num': task_num}))


def get_transformed_image_by_task_id(request):
    """
    前端试图获取某任务所对应的经过风格迁移之后的图像
    :param request: POST
    request.task_id: 任务id
    :return: HttpResponse(json.dumps({'state':'success','failed','new','processing'or'not_found',
                                    'image_dir':'...'})
    """
    task_exist, task_status = transform_task.get_status_of_task(request.POST['task_id'])
    if not task_exist:
        state = 'not_found'
        image_dir = ''
    else:
        if task_status == 'success':
            state = task_status
            # 返回任务对应的图片地址
            # TODO baixu【2020-07-21】 读数据库获得图片地址
            pass
        elif task_status == 'failed' or task_status == 'processing':
            state = task_status
            image_dir = ''
        elif task_status == 'new':
            mediator.handle_FrontEnd_request()  # 该函数为新开一个线程非阻塞调用
            state = task_status
            image_dir = ''
        else:
            logging.error('unknown task_status type: %s', task_status, exc_info=True)
