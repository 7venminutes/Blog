# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-21
Desc: 转换任务表（进行中的和已完成的）
"""
import logging
import pymysql

from const_var import Starry_DbConfig

TABLE_TRANSFORM_TASK = 'transform_task_table'

logging.basicConfig(level=logging.NOTSET)


def create_table_transform_task():
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    # date_string = time.strftime("%Y%m%d")
    # count = cursor.execute("SHOW TABLES LIKE '%s'" % ('transform_task_' + date_string))
    count = cursor.execute("SHOW TABLES LIKE '%s'" % TABLE_TRANSFORM_TASK)
    if count == 0:
        cursor.execute('''
            CREATE TABLE %s
            (
                task_id VARCHAR(128) NOT NULL,
                task_status ENUM('new', 'processing', 'success', 'failed') NOT NULL,
                user_id VARCHAR(20) NOT NULL,
                ipv4_ip VARCHAR(15),
                request_start_time DATETIME NOT NULL,
                task_finish_time DATETIME,
                original_image_path VARCHAR(128) NOT NULL,
                transformed_image_path VARCHAR(128),
                image_type ENUM('png', 'jpg') NOT NULL,
                selected_style VARCHAR(20) NOT NULL,
                
                PRIMARY KEY (task_id)
            );
        ''' % TABLE_TRANSFORM_TASK)
        conn.commit()
        logging.info('%s created successfully' % TABLE_TRANSFORM_TASK)
    else:
        logging.info('%s already existed in %s, skipped'
                     % (TABLE_TRANSFORM_TASK,
                        Starry_DbConfig['db_name']))
    conn.close()


def get_unfinished_task_num():
    """
    获得当前所有处于'new'状态和'processing'状态的任务的总数
    :return: count
    """
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT task_id FROM %s WHERE task_status='new' OR task_status='processing'"
                           % TABLE_TRANSFORM_TASK)
    conn.close()
    return count


def get_status_of_task(task_id):
    """
    获取某任务的状态（task_status）
    :param task_id: 任务id
    :return: task_exist, task_status
    task_exist: BOOL 该任务id是否在表中存在
    task_status: 'new', 'processing', 'success', 'failed' or 'not_found'
    """
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT task_status FROM %s WHERE task_id='%s'"
                           % (TABLE_TRANSFORM_TASK, str(task_id)))
    if count == 0:
        task_exist = False
        task_status = 'not_found'
    else:
        task_exist = True
        task_status = cursor.fetchone()[0]
    conn.close()
    return task_exist, task_status


def get_transformed_image_path(task_id):
    """
    获取某个task_id所对应的transformed_image_path, 该task_id的task_status应为'success'
    :param task_id: 任务id
    :return: success, image_path
    success = True or False  # image_path是否获得成功
    image_path  # 转换后的图片路径
    """
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT transformed_image_path FROM %s WHERE task_id='%s' AND task_status='success'"
                           % (TABLE_TRANSFORM_TASK, str(task_id)))
    if count == 0:
        success = False
        image_path = ''
    else:
        success = True
        # fixme[baixu] 2020-07-21 如果transformed_image_path为NULL的话，此处取出来的是什么？
        image_path = cursor.fetchone()[0]
    conn.close()
    return success, image_path
