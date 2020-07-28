"""
Author: Baixu
Date: 2020-07-10
Desc: 处理网站中starry风格迁移业务的视图请求
"""
import json
import logging
import os

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from common.key_checker import check_if_have_this_key
from common.address_transfer import resolve_path_to_actual_path
from tools.utils import make_dir_if_not_exists
from WebService.Starry.database import transform_task
from WebService.Starry.mediator import mediator


def starry(request):
    return render(request, 'Starry/starry.html')


@csrf_exempt
def get_user_info(request):
    """
    获取用户对于starry_web的信息（是否登录，是否开通starry服务，设置的网盘存储路径是多少）
    :param request: GET
    :return: 略
    """
    user_login_state = check_if_have_this_key(request.session, 'username')
    user_id = request.session['username'] if user_login_state else 'anonymous_user'
    # 先不允许用户手动指定图片存储目录，直接给他默认自己的主目录下的.starry文件夹
    user_root_dir = '/%s/.pic/' % user_id
    state, actual_path = resolve_path_to_actual_path(user_root_dir)
    if state:
        path_exist = os.path.exists(actual_path)
        make_dir_if_not_exists(actual_path)
    else:
        path_exist = False
    return HttpResponse(json.dumps({
        'user_login_state': user_login_state,
        'first_to_starry': not path_exist,
        'pics_store_dir': user_root_dir,
    }))


def get_queue_length(request):
    """
    用户提交任务时，前端调用该接口返回正在等待中的任务数，便于用户估计等待时间
    :param request: GET
    :return: HttpResponse(JSON.dumps({'task_num':...))
    """
    task_num = transform_task.get_unfinished_task_num()
    return HttpResponse(json.dumps({'task_num': task_num}))


@csrf_exempt
def receive_a_new_task(request):
    """
    接受前端的请求，将一个新任务插入任务表
    :param request: POST task_id, original_image_dir, selected_style
    :return: json： {'success_established': BOOL}
    """
    if check_if_have_this_key(request.session, 'auth'):
        task_id = str(request.POST['task_id'])
        original_image_dir = str(request.POST['original_image_dir'])
        selected_style = str(request.POST['selected_style'])
        user_id = request.session['username']

        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")

        image_type = original_image_dir[-3:].upper()
        transform_task.add_new_task(
            task_id,
            user_id,
            ip,
            original_image_dir,
            image_type,
            selected_style
        )
        return HttpResponse(json.dumps({'success_established': True}))
    else:
        return HttpResponse(json.dumps({'success_established': False}))


@csrf_exempt
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
            _, image_dir = transform_task.get_transformed_image_path(request.POST['task_id'])
        elif task_status == 'failed' or task_status == 'processing':
            state = task_status
            image_dir = ''
        elif task_status == 'new':
            mediator.handle_FrontEnd_request()  # 该函数为新开一个线程非阻塞调用
            state = task_status
            image_dir = ''
        else:
            state = 'unknown'
            image_dir = ''
            logging.error('unknown task_status type: %s', task_status, exc_info=True)
    return HttpResponse(json.dumps({'state': state, 'image_dir': image_dir}))
