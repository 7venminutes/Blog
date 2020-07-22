# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-21
Desc: web 与 service 之间的中介器，负责向service派发任务，接受service处理完的任务
"""
import logging
from io import BytesIO

import pymysql
import requests
import time

from PIL import Image

from common import address_transfer
from const_var import Starry_DbConfig
from datetime import datetime, timedelta
from WebService.Starry.database import transform_task
from WebService.Starry.mediator import set_time_stamp, get_time_stamp
from WebService.Starry.proto import enum_class_in_proto
from WebService.Starry.proto.task_common_pb2 import StarryPost
from WebService.Starry.async_call import async_call
from database.db_helpers import table_user
from tools import utils

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
                # TODO baixu【2020-07-21】 询问一下service是否能够接受新任务
                _assign_new_task_to_service()
                set_time_stamp()
                pass
        except Exception as e:
            logging.error(str(e), exc_info=True)
        finally:
            blocked = False


def receive_finished_task_from_ServiceEnd(request):
    """
    接受service端传来的完成任务
    :param request: POST
    :return: XXX
    """
    task_finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # TODO [baixu][2020-07-22] 验证一下service的ip
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    finished_task = StarryPost()
    finished_task.ParseFromString(request.get_data())
    finished_task_id = finished_task.taskID
    count = cursor.execute("SELECT user_id FROM %s WHERE task_id='%s'"
                           " AND task_status!='success'"
                           % (transform_task.TABLE_TRANSFORM_TASK,
                              finished_task_id))
    if count == 0:
        logging.error('No such unfinished task(task_id: %s)',
                      finished_task_id, exc_info=True)
    else:
        user_id = cursor.fetchone()[0]
        # fixme[baixu] 此处假定get_root_dir_by_id()不会返回False的state
        transformed_image_dir = ('%s.starry/%s/transform.%s'
                                 % (table_user.get_root_dir_by_id(user_id)['root_dir'],
                                    finished_task_id,
                                    'png' if finished_task.image.type == 'PNG' else 'jpg'))
        cursor.execute("UPDATE %s SET task_status='success', task_finish_time='%s',"
                       "transformed_image_path='%s' WHERE task_id='%s'"
                       % (transform_task.TABLE_TRANSFORM_TASK,
                          task_finish_time,
                          transformed_image_dir,
                          finished_task_id))
        # 将图片写入对应路径
        try:
            _, actual_path = address_transfer.resolve_path_to_actual_path(transformed_image_dir)
            Image.open(BytesIO(finished_task.image.image)).save(actual_path)
        except OSError as error_msg:
            logging.error('failed to receive finished task from ServiceEnd\n'
                          '\t%s', error_msg, exc_info=True)
            conn.rollback()
    conn.commit()
    conn.close()


def _assign_new_task_to_service():
    """
    该函数仅供handle_FrontEnd_request()调用
    向service派发一条新的任务
    :return: null
    """
    # 1.从transform_task表中拿出一条未完成的任务
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT task_id, original_image_path, image_type, selected_style"
                           " FROM %s WHERE task_status='new'"
                           % transform_task.TABLE_TRANSFORM_TASK)
    if count == 0:
        logging.warning('No `new` task in table transform_task, but handle_FrontEnd_request'
                        ' has been called. Somebody hacked into our interface!')
    # 2.将该任务传递给service
    else:
        no_bug_during_delivering = True
        new_task = cursor.fetchone()
        request_body = StarryPost()

        # 2.1 生成request_body
        request_body.taskId = new_task[0]
        original_image_path = new_task[1]
        try:
            request_body.image.type = enum_class_in_proto.ImageType[new_task[2]].value
            request_body.modelSelect = enum_class_in_proto.ModelOption[new_task[3]].value
        except KeyError as error_msg:
            no_bug_during_delivering = False
            logging.error('Unknown key stored in transform_task:\n\t%s', error_msg, exc_info=True)
        try:
            can_be_transferred, actual_original_image_path \
                = address_transfer.resolve_path_to_actual_path(original_image_path)
            if not can_be_transferred:
                no_bug_during_delivering = False
            else:
                print(actual_original_image_path)
                with open(actual_original_image_path, 'rb') as img:
                    f = img.read()
                    request_body.image.image = f
        except OSError as error_msg:
            no_bug_during_delivering = False
            logging.error(error_msg, exc_info=True)

        # 2.2 request_body序列化并发送
        if no_bug_during_delivering:
            s = requests
            r = s.post("http://127.0.0.1:5000/transfer", request_body.SerializeToString())
            if r.status_code != 200:
                logging.error('Wrong status_code got from server after delivering task\n'
                              'status_code: %s\ttext: %s',
                              r.status_code, r.text)
                no_bug_during_delivering = False
            else:
                cursor.execute("UPDATE %s SET task_status='processing' WHERE task_id='%s'"
                               % (transform_task.TABLE_TRANSFORM_TASK, new_task[0]))

        # 2.3 统一处理一下异常
        if not no_bug_during_delivering:
            cursor.execute("UPDATE %s SET task_status='failed' WHERE task_id='%s'"
                           % (transform_task.TABLE_TRANSFORM_TASK, new_task[0]))
    # 向数据库提交更改，退出
    conn.commit()
    conn.close()


def receive_error_info_from_ServiceEnd(request):
    """
    服务端'任务处理'失败，通过该接口告知web-starry
    :param request: POST(json 格式)
    {'task_id':...,'info':...}
    :return: 状态码为200即成功接收
    """
    # fixme[baixu] 【2020-07-22】验证服务端ip
    task_id = request.POST['task_id']
    info = request.POST['info']
    # 1.把任务表任务状态标记为失败
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    cursor.execute("UPDATE %s SET task_status='failed' WHERE task_id='%s' AND task_status='processing'"
                   % (transform_task.TABLE_TRANSFORM_TASK, task_id))
    conn.commit()
    conn.close()
    # 2.报错
    logging.error('Service failed processing a task:\n'
                  '\ttask_id: %s\n'
                  '\tinfo: %s\n', task_id, info)
